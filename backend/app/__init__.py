from __future__ import annotations

from flask import Flask, jsonify
from flask_cors import CORS

from app.config import CORS_ORIGINS, MAX_CONTENT_LENGTH, SECRET_KEY, UPLOAD_DIR
from app.routes.auth import bp as auth_bp
from app.routes.backtest import bp as backtest_bp
from app.routes.dashboard import bp as dashboard_bp
from app.routes.data_quality import bp as quality_bp
from app.routes.health import bp as health_bp
from app.routes.market import bp as market_bp
from app.routes.research import bp as research_bp
from app.routes.scanner import bp as scanner_bp
from app.routes.workspace import bp as workspace_bp


def create_app() -> Flask:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
    CORS(app, origins=CORS_ORIGINS, supports_credentials=False)

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(market_bp, url_prefix="/api")
    app.register_blueprint(scanner_bp, url_prefix="/api")
    app.register_blueprint(backtest_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(quality_bp, url_prefix="/api")
    app.register_blueprint(research_bp, url_prefix="/api")
    app.register_blueprint(workspace_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")

    @app.errorhandler(400)
    def bad_request(err):
        return jsonify({"error": "bad_request", "message": str(err)}), 400

    @app.errorhandler(404)
    def not_found(err):
        return jsonify({"error": "not_found", "message": "Resource not found"}), 404

    @app.errorhandler(413)
    def too_large(_err):
        return jsonify(
            {
                "error": "payload_too_large",
                "message": "Upload exceeds the configured size limit.",
            }
        ), 413

    @app.errorhandler(500)
    def server_error(err):
        return jsonify({"error": "server_error", "message": str(err)}), 500

    return app
