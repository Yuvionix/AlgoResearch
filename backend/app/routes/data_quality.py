from flask import Blueprint, jsonify, request

from app.providers.csv_provider import CSVProvider
from app.providers.factory import fetch_with_fallback
from app.validation.ohlc import validate_ohlc
from app.validation.uploads import UploadError, validate_csv_file

bp = Blueprint("quality", __name__)


@bp.post("/data-quality/validate")
def validate():
    payload = request.get_json(silent=True) or {}
    symbol = (payload.get("symbol") or "NIFTY").strip()
    source = payload.get("source") or "yahoo"
    try:
        frame, source_name, used_fallback, warning = fetch_with_fallback(
            symbol, preferred=source, period=payload.get("period") or "1y"
        )
        report = validate_ohlc(frame)
        report.update(
            {
                "symbol": symbol,
                "data_source": source_name,
                "used_fallback": used_fallback,
                "warning": warning,
                "is_realtime": False,
            }
        )
        return jsonify(report)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": "validation_failed", "message": str(exc)}), 400


@bp.post("/data-quality/validate-csv")
def validate_csv():
    try:
        content = validate_csv_file(request.files.get("file"))
        provider = CSVProvider.from_bytes(content)
        frame = provider.fetch_ohlc("CSV")
        report = validate_ohlc(frame)
        report.update({"data_source": "csv_upload", "is_realtime": False})
        return jsonify(report)
    except UploadError as exc:
        return jsonify({"error": "upload_rejected", "message": str(exc)}), 400
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": "validation_failed", "message": str(exc)}), 400
