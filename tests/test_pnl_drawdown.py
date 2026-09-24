from __future__ import annotations

import pandas as pd
import pytest

from app.analytics.pnl import analyze_trades, max_drawdown


def test_pnl_and_win_rate():
    trades = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-02", "2024-01-03", "2024-02-01"]),
            "pnl": [100.0, -40.0, 20.0],
            "strategy": ["A", "A", "B"],
        }
    )
    result = analyze_trades(trades, initial_capital=1000, dataset_label="t", source="test")
    assert result["total_pnl"] == pytest.approx(80.0)
    assert result["trade_count"] == 3
    assert result["win_count"] == 2
    assert result["win_rate_pct"] == pytest.approx(200 / 3)
    assert result["ending_equity"] == pytest.approx(1080.0)
    assert result["average_trade"] == pytest.approx(80 / 3)


def test_max_drawdown():
    equity = pd.Series(
        [100, 120, 90, 95],
        index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]),
    )
    dd = max_drawdown(equity)
    assert dd["max_drawdown"] == pytest.approx(-30.0)
    assert dd["peak_date"] == "2024-01-02"
    assert dd["trough_date"] == "2024-01-03"
