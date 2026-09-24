from flask import Blueprint, jsonify, request

from app.providers.local import load_universe
from app.services.scanner_service import scan_universe, symbol_detail

bp = Blueprint("scanner", __name__)


@bp.get("/scanner/universe")
def universe():
    return jsonify({"universe": "NIFTY 50", "constituents": load_universe()})


@bp.post("/scanner/run")
def run():
    payload = request.get_json(silent=True) or {}
    lookback_days = int(payload.get("lookback_days") or 15)
    source = payload.get("source") or "yahoo"
    max_symbols = payload.get("max_symbols")
    try:
        result = scan_universe(
            lookback_days=lookback_days,
            source=source,
            max_symbols=int(max_symbols) if max_symbols else None,
        )
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": "scan_failed", "message": str(exc)}), 400
    return jsonify(result)


@bp.get("/scanner/symbol/<path:symbol>")
def detail(symbol: str):
    source = request.args.get("source") or "yahoo"
    try:
        return jsonify(symbol_detail(symbol, source=source))
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": "symbol_failed", "message": str(exc)}), 400
