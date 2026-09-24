from flask import Blueprint, current_app, jsonify, request

from app.services.backtest_service import (
    analyze_uploaded_trades,
    compare_named,
    internship_view,
    run_monte_carlo,
    sample_dataset_view,
)
from app.validation.uploads import UploadError, validate_csv_file
from app.validation.requests import bounded_int, positive_float
from app.routes.auth import auth_required

bp = Blueprint("backtest", __name__)


@bp.get("/backtest/internship")
def internship():
    return jsonify(internship_view())


@bp.get("/backtest/sample")
def sample():
    return jsonify(sample_dataset_view())


@bp.post("/backtest/analyze-csv")
@auth_required
def analyze_csv():
    try:
        content = validate_csv_file(request.files.get("file"))
        capital = positive_float(request.form.get("initial_capital"), 200000, "initial_capital")
        label = request.form.get("label") or "Uploaded trade list"
        return jsonify(analyze_uploaded_trades(content, initial_capital=capital, dataset_label=label))
    except UploadError as exc:
        return jsonify({"error": "upload_rejected", "message": str(exc)}), 400
    except Exception as exc:  # noqa: BLE001
        current_app.logger.exception("Backtest analysis failed", exc_info=exc)
        return jsonify({"error": "analyze_failed", "message": "Unable to analyze the uploaded trades."}), 400


@bp.post("/backtest/monte-carlo")
@auth_required
def monte_carlo():
    try:
        content = validate_csv_file(request.files.get("file"))
        capital = positive_float(request.form.get("initial_capital"), 200000, "initial_capital")
        n = bounded_int(request.form.get("n_simulations"), 500, 10, 5000, "n_simulations")
        return jsonify(run_monte_carlo(content, initial_capital=capital, n_simulations=n))
    except UploadError as exc:
        return jsonify({"error": "upload_rejected", "message": str(exc)}), 400
    except Exception as exc:  # noqa: BLE001
        current_app.logger.exception("Monte Carlo analysis failed", exc_info=exc)
        return jsonify({"error": "monte_carlo_failed", "message": "Unable to run the Monte Carlo analysis."}), 400


@bp.post("/backtest/compare")
@auth_required
def compare():
    payload = request.get_json(silent=True) or {}
    datasets = payload.get("datasets") or ["internship", "sample"]
    try:
        return jsonify(compare_named(datasets))
    except Exception as exc:  # noqa: BLE001
        current_app.logger.exception("Backtest comparison failed", exc_info=exc)
        return jsonify({"error": "compare_failed", "message": "Unable to compare the selected datasets."}), 400
