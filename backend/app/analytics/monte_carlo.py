from __future__ import annotations

import numpy as np
import pandas as pd

from app.analytics.pnl import max_drawdown


def monte_carlo_from_trades(
    trades: pd.DataFrame,
    initial_capital: float,
    n_simulations: int = 500,
    seed: int | None = 42,
) -> dict:
    if n_simulations < 10 or n_simulations > 5000:
        raise ValueError("n_simulations must be between 10 and 5000")
    pnl = trades["pnl"].to_numpy(dtype=float)
    if len(pnl) < 5:
        raise ValueError("Monte Carlo requires at least 5 trades")

    rng = np.random.default_rng(seed)
    terminal = []
    max_dds = []
    paths_sample = []

    for i in range(n_simulations):
        shuffled = rng.permutation(pnl)
        equity = initial_capital + np.cumsum(shuffled)
        terminal.append(float(equity[-1]))
        series = pd.Series(equity)
        dd = float((series - series.cummax()).min())
        max_dds.append(dd)
        if i < 25:
            paths_sample.append([float(x) for x in equity])

    terminal_arr = np.array(terminal)
    dd_arr = np.array(max_dds)
    return {
        "n_simulations": n_simulations,
        "seed": seed,
        "method": "Trade-sequence permutation (order shuffled; trade P&L values preserved).",
        "initial_capital": initial_capital,
        "terminal_equity": {
            "mean": float(terminal_arr.mean()),
            "median": float(np.median(terminal_arr)),
            "p05": float(np.percentile(terminal_arr, 5)),
            "p25": float(np.percentile(terminal_arr, 25)),
            "p75": float(np.percentile(terminal_arr, 75)),
            "p95": float(np.percentile(terminal_arr, 95)),
            "min": float(terminal_arr.min()),
            "max": float(terminal_arr.max()),
        },
        "max_drawdown": {
            "mean": float(dd_arr.mean()),
            "median": float(np.median(dd_arr)),
            "p05": float(np.percentile(dd_arr, 5)),
            "p95": float(np.percentile(dd_arr, 95)),
            "worst": float(dd_arr.min()),
        },
        "histogram": _hist(terminal_arr),
        "sample_paths": paths_sample,
        "disclaimer": (
            "Permutation Monte Carlo probes path-order uncertainty given the observed trade P&L list. "
            "It does not prove future performance and assumes trades are exchangeable."
        ),
    }


def internship_monte_carlo_placeholder(payload: dict) -> dict:
    info = payload.get("monte_carlo") or {}
    return {
        "available": False,
        "performed_during_internship": bool(info.get("performed_during_internship")),
        "message": info.get(
            "message",
            "Monte Carlo analysis was performed during the internship; "
            "raw simulation output is not included in this portfolio reconstruction.",
        ),
        "how_to_run": (
            "Upload a trade-level CSV (date, pnl) to run a genuine permutation Monte Carlo "
            "simulation in this application."
        ),
    }


def _hist(arr: np.ndarray, bins: int = 16) -> list[dict]:
    counts, edges = np.histogram(arr, bins=bins)
    out = []
    for i, count in enumerate(counts):
        out.append({"bin_from": float(edges[i]), "bin_to": float(edges[i + 1]), "count": int(count)})
    return out
