from __future__ import annotations

import pandas as pd

from app.analytics.crossover import detect_crossovers, recent_golden_cross
from app.analytics.indicators import ema


def _ohlc_from_closes(closes):
    rows = []
    for i, c in enumerate(closes):
        rows.append(
            {
                "Open": c,
                "High": c + 1,
                "Low": c - 1,
                "Close": c,
                "Volume": 1000,
            }
        )
    idx = pd.bdate_range("2025-01-01", periods=len(closes))
    return pd.DataFrame(rows, index=idx)


def test_golden_crossover_detected():
    down = [100 - i * 0.4 for i in range(60)]
    up = [down[-1] + i * 1.2 for i in range(1, 40)]
    df = detect_crossovers(_ohlc_from_closes(down + up))
    assert df["golden_cross"].any()
    last = recent_golden_cross(df, within_days=90)
    assert last is not None
    assert last["kind"] == "golden"
    assert last["ema20"] > last["ema50"]


def test_no_crossover_on_flat_series():
    df = detect_crossovers(_ohlc_from_closes([50.0] * 80))
    assert not df["golden_cross"].any()
    assert recent_golden_cross(df, within_days=10) is None
