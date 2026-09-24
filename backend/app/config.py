"""Application configuration. Secrets never belong in source control."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent
DATA_DIR = ROOT_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
RUNS_PATH = DATA_DIR / "research_runs.json"
FALLBACK_DIR = DATA_DIR / "fallback_ohlc"
UNIVERSE_PATH = DATA_DIR / "nifty_universe.json"
INTERNSHIP_RESULTS_PATH = DATA_DIR / "internship_backtest_summary.json"
SAMPLE_BACKTEST_PATH = DATA_DIR / "sample_research_backtest.json"
SAMPLE_TRADES_PATH = DATA_DIR / "sample_trades.csv"


def _int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]

PORT = _int("PORT", 5001)
HOST = os.getenv("HOST", "127.0.0.1")
MAX_UPLOAD_MB = _int("MAX_UPLOAD_MB", 5)
MAX_CONTENT_LENGTH = MAX_UPLOAD_MB * 1024 * 1024
YFINANCE_TIMEOUT = _int("YFINANCE_TIMEOUT", 20)
OFFLINE = os.getenv("ALGORESEARCH_OFFLINE", "").lower() in {"1", "true", "yes"}
DEBUG = os.getenv("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
ALLOWED_EXTENSIONS = {".csv"}
ALLOWED_CSV_MIME = {
    "text/csv",
    "application/csv",
    "application/vnd.ms-excel",
    "text/plain",
    "application/octet-stream",
}
MAX_CSV_ROWS = 50_000
