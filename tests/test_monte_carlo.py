from __future__ import annotations

import pandas as pd

from app.analytics.monte_carlo import monte_carlo_from_trades


def test_monte_carlo_preserves_trade_sum():
    trades = pd.DataFrame(
        {
            "date": pd.bdate_range("2024-01-02", periods=12),
            "pnl": [100, -50, 80, -20, 30, 40, -10, 15, 25, -5, 60, -15],
        }
    )
    result = monte_carlo_from_trades(trades, initial_capital=1000, n_simulations=50, seed=1)
    expected_terminal = 1000 + trades["pnl"].sum()
    # permutation preserves the sum, so every terminal equity matches
    assert result["terminal_equity"]["mean"] == expected_terminal
    assert result["n_simulations"] == 50
