from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.providers.normalize import normalize_ohlc
from app.validation.ohlc import validate_ohlc

ROOT = Path(__file__).resolve().parents[1]


def test_valid_series_scores_high():
    idx = pd.bdate_range("2025-01-01", periods=40)
    df = pd.DataFrame(
        {
            "Open": 100,
            "High": 102,
            "Low": 99,
            "Close": 101,
            "Volume": 1000,
        },
        index=idx,
    )
    report = validate_ohlc(df)
    assert report["passed"]
    assert report["score"] >= 80


def test_invalid_fixture_flags_errors():
    path = ROOT / "data" / "invalid_ohlc.csv"
    raw = pd.read_csv(path)
    df = normalize_ohlc(raw, source="test")
    report = validate_ohlc(df)
    codes = {i["code"] for i in report["issues"]}
    assert "high_lt_low" in codes or "close_outside_range" in codes
    assert "impossible_prices" in codes
    assert report["score"] < 80
    assert not report["passed"]


def test_missing_values_detected():
    idx = pd.bdate_range("2025-01-01", periods=10)
    df = pd.DataFrame(
        {"Open": [1, None] + [1] * 8, "High": 2, "Low": 0.5, "Close": 1.5, "Volume": 1},
        index=idx,
    )
    report = validate_ohlc(df)
    assert any(i["code"] == "missing_values" for i in report["issues"])
