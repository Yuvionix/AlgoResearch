from __future__ import annotations

from app.analytics.pnl import documented_internship_metrics
from app.services.backtest_service import load_internship_results


def test_internship_figures_are_documented_not_invented():
    payload = load_internship_results()
    metrics = documented_internship_metrics(payload)
    assert metrics["generated_by_this_application"] is False
    assert metrics["initial_capital"] == 200000
    years = {row["year"]: row for row in metrics["yearly_pnl"]}
    assert years[2024]["pnl"] == 46419
    assert years[2024]["max_drawdown"] == 3557
    assert years[2025]["pnl"] == 195621
    assert years[2025]["max_drawdown"] == 5765
    assert metrics["total_pnl"] == 46419 + 195621
