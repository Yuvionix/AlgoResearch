from __future__ import annotations

import json

import pandas as pd

from app.analytics.monte_carlo import internship_monte_carlo_placeholder, monte_carlo_from_trades
from app.analytics.pnl import analyze_trades, compare_backtests, documented_internship_metrics
from app.config import INTERNSHIP_RESULTS_PATH, SAMPLE_BACKTEST_PATH, SAMPLE_TRADES_PATH
from app.providers.csv_provider import parse_trades_csv
from app.store.research_runs import create_run


def load_internship_results() -> dict:
    with INTERNSHIP_RESULTS_PATH.open() as handle:
        return json.load(handle)


def internship_view() -> dict:
    payload = load_internship_results()
    metrics = documented_internship_metrics(payload)
    metrics["monte_carlo"] = internship_monte_carlo_placeholder(payload)
    return metrics


def sample_dataset_view() -> dict:
    with SAMPLE_BACKTEST_PATH.open() as handle:
        meta = json.load(handle)
    trades = pd.read_csv(SAMPLE_TRADES_PATH)
    trades["date"] = pd.to_datetime(trades["date"])
    analysis = analyze_trades(
        trades,
        initial_capital=float(meta["initial_capital"]),
        dataset_label=meta["label"],
        source=meta["source"],
    )
    analysis["synthetic"] = True
    analysis["caveat"] = meta.get("caveat")
    return analysis


def analyze_uploaded_trades(
    content: bytes,
    initial_capital: float,
    dataset_label: str = "Uploaded trade list",
    persist_run: bool = True,
) -> dict:
    trades = parse_trades_csv(content)
    analysis = analyze_trades(
        trades,
        initial_capital=initial_capital,
        dataset_label=dataset_label,
        source="csv_upload",
    )
    if persist_run:
        analysis["research_run"] = create_run(
            analysis_type="backtest_analytics",
            instrument=None,
            universe=None,
            parameters={"initial_capital": initial_capital, "label": dataset_label},
            data_period={"start": analysis["first_trade"], "end": analysis["last_trade"]},
            data_source="csv_upload",
            result_summary={
                "total_pnl": analysis["total_pnl"],
                "max_drawdown": analysis["max_drawdown"],
                "trade_count": analysis["trade_count"],
            },
        )
    return analysis


def run_monte_carlo(content: bytes, initial_capital: float, n_simulations: int = 500) -> dict:
    trades = parse_trades_csv(content)
    return monte_carlo_from_trades(trades, initial_capital=initial_capital, n_simulations=n_simulations)


def compare_named(datasets: list[str]) -> dict:
    loaded = []
    for name in datasets:
        key = name.strip().lower()
        if key in {"internship", "internship_backtest"}:
            item = internship_view()
            item["max_drawdown"] = min(p["max_drawdown"] for p in item["max_drawdown_by_year"])
            item["trade_count"] = None
            item["average_trade"] = None
            item["win_rate_pct"] = None
            loaded.append(item)
        elif key in {"sample", "sample_research"}:
            loaded.append(sample_dataset_view())
        else:
            raise ValueError(f"Unknown dataset '{name}'. Use internship or sample, or upload CSV.")
    return compare_backtests(loaded)
