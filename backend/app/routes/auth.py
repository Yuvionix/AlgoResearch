from __future__ import annotations

from functools import wraps
from hmac import compare_digest

from flask import Blueprint, jsonify, request, session

from app.config import AUTH_ENABLED, AUTH_PASSWORD, AUTH_USERNAME, SECRET_KEY

bp = Blueprint("auth", __name__)


def auth_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if AUTH_ENABLED and not session.get("authenticated"):
            return jsonify({"error": "authentication_required", "message": "Please sign in."}), 401
        return view(*args, **kwargs)

    return wrapped


@bp.post("/auth/login")
def login():
    if AUTH_ENABLED and (SECRET_KEY == "change-me-in-production" or not AUTH_PASSWORD):
        return jsonify({"error": "auth_misconfigured", "message": "Authentication is not configured securely."}), 503
    payload = request.get_json(silent=True) or {}
    username = str(payload.get("username") or "")
    password = str(payload.get("password") or "")
    if not AUTH_ENABLED or (compare_digest(username, AUTH_USERNAME) and compare_digest(password, AUTH_PASSWORD)):
        session["authenticated"] = True
        return jsonify({"authenticated": True, "username": AUTH_USERNAME})
    return jsonify({"error": "invalid_credentials", "message": "Invalid username or password."}), 401


@bp.post("/auth/logout")
def logout():
    session.clear()
    return jsonify({"authenticated": False})


@bp.get("/auth/me")
def me():
    return jsonify({"authenticated": bool(session.get("authenticated")) or not AUTH_ENABLED})