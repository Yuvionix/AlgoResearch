from flask import Blueprint, jsonify

from app.config import MAX_UPLOAD_MB

bp = Blueprint("health", __name__)


@bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "algoresearch-api"})


@bp.get("/meta")
def meta():
    return jsonify(
        {
            "name": "AlgoResearch",
            "subtitle": "Algorithmic Trading Research & Analytics Platform",
            "positioning": "From market analysis to strategy evaluation — one reproducible research workflow.",
            "not": [
                "live trading platform",
                "broker",
                "autonomous trading bot",
                "investment-advisory system",
            ],
            "is": "research + screening + analytics + backtest evaluation platform",
            "max_upload_mb": MAX_UPLOAD_MB,
        }
    )
