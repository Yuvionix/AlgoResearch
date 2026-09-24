from flask import Blueprint, current_app, jsonify, request

from app.providers.local import load_universe
from app.services.scanner_service import scan_universe, symbol_detail
from app.validation.requests import bounded_int, required_symbol

bp = Blueprint("scanner", __name__)


@bp.get("/scanner/universe")
def universe():
    return jsonify({"universe": "NIFTY 50", "constituents": load_universe()})


@bp.post("/scanner/run")
def run():
    payload = request.get_json(silent=True) or {}
    try:
        lookback_days = bounded_int(payload.get("lookback_days"), 15, 1, 365, "lookback_days")
        source = payload.get("source") or "yahoo"
        result = scan_universe(
            lookback_days=lookback_days,
            source=source,
            max_symbols=bounded_int(payload.get("max_symbols"), 50, 1, 50, "max_symbols")
            if payload.get("max_symbols") not in (None, "")
            else None,
        )
    except Exception as exc:  # noqa: BLE001
        current_app.logger.exception("Universe scan failed", exc_info=exc)
        return jsonify({"error": "scan_failed", "message": "Unable to complete the scan."}), 400
    return jsonify(result)


@bp.get("/scanner/symbol/<path:symbol>")
def detail(symbol: str):
    source = request.args.get("source") or "yahoo"
    try:
        return jsonify(symbol_detail(required_symbol(symbol), source=source))
    except Exception as exc:  # noqa: BLE001
        current_app.logger.exception("Symbol analysis failed", exc_info=exc)
        return jsonify({"error": "symbol_failed", "message": "Unable to load symbol analysis."}), 400
