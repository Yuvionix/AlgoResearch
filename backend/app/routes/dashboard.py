from flask import Blueprint, jsonify

from app.services.workspace_service import dashboard_summary

bp = Blueprint("dashboard", __name__)


@bp.get("/dashboard")
def dashboard():
    return jsonify(dashboard_summary())
