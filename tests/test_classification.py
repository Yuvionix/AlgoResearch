from __future__ import annotations

import pandas as pd

from app.analytics.classification import classify_market


def _frame(rows):
    idx = pd.bdate_range("2026-01-05", periods=len(rows))
    return pd.DataFrame(rows, index=idx)


def test_classifies_bullish_structure():
    rows = []
    price = 100
    for _ in range(6):
        o = price
        c = price + 3
        rows.append({"Open": o, "High": c + 0.5, "Low": o - 0.2, "Close": c, "Volume": 1})
        price = c
    result = classify_market(_frame(rows), "TEST", lookback=5, source="test")
    assert result["classification"] == "Bullish"
    assert result["metrics"]["up_sessions"] == 5
    assert any("rule-based" in line.lower() or "Classification is rule-based" in line for line in result["why"])


def test_classifies_bearish_structure():
    rows = []
    price = 100
    for _ in range(6):
        o = price
        c = price - 3
        rows.append({"Open": o, "High": o + 0.2, "Low": c - 0.5, "Close": c, "Volume": 1})
        price = c
    result = classify_market(_frame(rows), "TEST", lookback=5, source="test")
    assert result["classification"] == "Bearish"


def test_classifies_sideways():
    rows = [
        {"Open": 100, "High": 101, "Low": 99, "Close": 100.2, "Volume": 1},
        {"Open": 100.2, "High": 101, "Low": 99, "Close": 99.8, "Volume": 1},
        {"Open": 99.8, "High": 101, "Low": 99, "Close": 100.1, "Volume": 1},
        {"Open": 100.1, "High": 101, "Low": 99, "Close": 99.9, "Volume": 1},
        {"Open": 99.9, "High": 100.5, "Low": 99.5, "Close": 100.0, "Volume": 1},
    ]
    result = classify_market(_frame(rows), "TEST", lookback=5, source="test")
    assert result["classification"] == "Sideways"
