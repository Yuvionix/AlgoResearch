from flask import Blueprint, jsonify, Response

from app.services.workspace_service import export_run_markdown
from app.store.research_runs import get_run, list_runs

bp = Blueprint("research", __name__)


@bp.get("/research-runs")
def runs():
    return jsonify({"runs": list_runs()})


@bp.get("/research-runs/<run_id>")
def run_detail(run_id: str):
    run = get_run(run_id)
    if run is None:
        return jsonify({"error": "not_found", "message": run_id}), 404
    return jsonify(run)


@bp.get("/research-runs/<run_id>/export")
def export_run(run_id: str):
    try:
        text = export_run_markdown(run_id)
    except KeyError:
        return jsonify({"error": "not_found", "message": run_id}), 404
    return Response(
        text,
        mimetype="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={run_id}.md"},
    )
