from flask import Blueprint, current_app, jsonify, request

from app.services.workspace_service import dashboard_summary, execute_workspace
from app.validation.requests import bounded_int, required_symbol

bp = Blueprint("workspace", __name__)


@bp.post("/workspace/execute")
def execute():
    payload = request.get_json(silent=True) or {}
    try:
        result = execute_workspace(
            instrument=required_symbol(payload.get("instrument")),
            analysis_date=payload.get("analysis_date"),
            lookback=bounded_int(payload.get("lookback"), 5, 3, 250, "lookback"),
            source=payload.get("source") or "yahoo",
            include_scan=bool(payload.get("include_scan", True)),
            include_backtest=bool(payload.get("include_backtest", True)),
            backtest_dataset=payload.get("backtest_dataset") or "internship",
            scan_lookback_days=bounded_int(payload.get("scan_lookback_days"), 15, 1, 365, "scan_lookback_days"),
        )
        return jsonify(result)
    except Exception as exc:  # noqa: BLE001
        current_app.logger.exception("Workspace execution failed", exc_info=exc)
        return jsonify({"error": "workspace_failed", "message": "Unable to execute the workspace workflow."}), 400
