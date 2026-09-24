from flask import Blueprint, jsonify, request

from app.services.backtest_service import (
    analyze_uploaded_trades,
    compare_named,
    internship_view,
    run_monte_carlo,
    sample_dataset_view,
)
from app.validation.uploads import UploadError, validate_csv_file

bp = Blueprint("backtest", __name__)


@bp.get("/backtest/internship")
def internship():
    return jsonify(internship_view())


@bp.get("/backtest/sample")
def sample():
    return jsonify(sample_dataset_view())


@bp.post("/backtest/analyze-csv")
def analyze_csv():
    try:
        content = validate_csv_file(request.files.get("file"))
        capital = float(request.form.get("initial_capital") or 200000)
        label = request.form.get("label") or "Uploaded trade list"
        return jsonify(analyze_uploaded_trades(content, initial_capital=capital, dataset_label=label))
    except UploadError as exc:
        return jsonify({"error": "upload_rejected", "message": str(exc)}), 400
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": "analyze_failed", "message": str(exc)}), 400


@bp.post("/backtest/monte-carlo")
def monte_carlo():
    try:
        content = validate_csv_file(request.files.get("file"))
        capital = float(request.form.get("initial_capital") or 200000)
        n = int(request.form.get("n_simulations") or 500)
        return jsonify(run_monte_carlo(content, initial_capital=capital, n_simulations=n))
    except UploadError as exc:
        return jsonify({"error": "upload_rejected", "message": str(exc)}), 400
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": "monte_carlo_failed", "message": str(exc)}), 400


@bp.post("/backtest/compare")
def compare():
    payload = request.get_json(silent=True) or {}
    datasets = payload.get("datasets") or ["internship", "sample"]
    try:
        return jsonify(compare_named(datasets))
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": "compare_failed", "message": str(exc)}), 400
