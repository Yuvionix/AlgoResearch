from flask import Blueprint, jsonify, request

from app.services.workspace_service import dashboard_summary, execute_workspace

bp = Blueprint("workspace", __name__)


@bp.post("/workspace/execute")
def execute():
    payload = request.get_json(silent=True) or {}
    try:
        result = execute_workspace(
            instrument=(payload.get("instrument") or "NIFTY").strip(),
            analysis_date=payload.get("analysis_date"),
            lookback=int(payload.get("lookback") or 5),
            source=payload.get("source") or "yahoo",
            include_scan=bool(payload.get("include_scan", True)),
            include_backtest=bool(payload.get("include_backtest", True)),
            backtest_dataset=payload.get("backtest_dataset") or "internship",
            scan_lookback_days=int(payload.get("scan_lookback_days") or 15),
        )
        return jsonify(result)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": "workspace_failed", "message": str(exc)}), 400
