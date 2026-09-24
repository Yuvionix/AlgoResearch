from flask import Blueprint, current_app, jsonify, request

from app.services.market_service import run_classification
from app.validation.uploads import UploadError, validate_csv_file
from app.providers.csv_provider import CSVProvider
from app.providers.factory import fetch_with_fallback
from app.analytics.classification import classify_market
from app.validation.ohlc import validate_ohlc
from app.providers.normalize import ohlc_records
from app.store.research_runs import create_run
from app.validation.requests import bounded_int, required_symbol

bp = Blueprint("market", __name__)


@bp.post("/market/classify")
def classify():
    payload = request.get_json(silent=True) or {}
    try:
        instrument = required_symbol(payload.get("instrument"))
        analysis_date = payload.get("analysis_date")
        lookback = bounded_int(payload.get("lookback"), 5, 3, 250, "lookback")
        source = payload.get("source") or "yahoo"
        period = payload.get("period") or "6mo"
        result = run_classification(
            instrument=instrument,
            analysis_date=analysis_date,
            lookback=lookback,
            source=source,
            period=period,
        )
    except Exception as exc:  # noqa: BLE001
        current_app.logger.exception("Market classification failed", exc_info=exc)
        return jsonify({"error": "classification_failed", "message": "Unable to complete market classification."}), 400
    return jsonify(result)


@bp.post("/market/classify-csv")
def classify_csv():
    try:
        content = validate_csv_file(request.files.get("file"))
        instrument = required_symbol(request.form.get("instrument"), default="CSV")
        analysis_date = request.form.get("analysis_date") or None
        lookback = bounded_int(request.form.get("lookback"), 5, 3, 250, "lookback")
        provider = CSVProvider.from_bytes(content)
        frame = provider.fetch_ohlc(instrument)
        quality = validate_ohlc(frame)
        result = classify_market(
            frame,
            instrument=instrument,
            analysis_date=analysis_date,
            lookback=lookback,
            source="csv_upload",
        )
        run = create_run(
            analysis_type="market_direction",
            instrument=instrument,
            universe=None,
            parameters={"lookback": lookback, "source": "csv_upload"},
            data_period={"start": quality.get("start"), "end": result.get("last_session")},
            data_source="csv_upload",
            result_summary={"classification": result["classification"]},
        )
        return jsonify(
            {
                "result": result,
                "data_quality": quality,
                "ohlc": ohlc_records(frame.tail(90)),
                "research_run": run,
                "is_realtime": False,
            }
        )
    except UploadError as exc:
        return jsonify({"error": "upload_rejected", "message": str(exc)}), 400
    except Exception as exc:  # noqa: BLE001
        current_app.logger.exception("CSV market classification failed", exc_info=exc)
        return jsonify({"error": "classification_failed", "message": "Unable to classify the uploaded data."}), 400
