from __future__ import annotations

import pandas as pd


def max_drawdown(equity: pd.Series) -> dict:
    if equity.empty:
        raise ValueError("Equity series is empty")
    running_max = equity.cummax()
    drawdown = equity - running_max
    dd_pct = (equity / running_max - 1.0).replace([float("inf"), -float("inf")], 0)
    trough_idx = drawdown.idxmin()
    peak_idx = equity.loc[:trough_idx].idxmax()
    return {
        "max_drawdown": float(drawdown.min()),
        "max_drawdown_pct": float(dd_pct.min() * 100) if pd.notna(dd_pct.min()) else 0.0,
        "peak_date": pd.Timestamp(peak_idx).strftime("%Y-%m-%d"),
        "trough_date": pd.Timestamp(trough_idx).strftime("%Y-%m-%d"),
        "series": [
            {
                "date": pd.Timestamp(idx).strftime("%Y-%m-%d"),
                "drawdown": float(drawdown.loc[idx]),
                "drawdown_pct": float(dd_pct.loc[idx] * 100) if pd.notna(dd_pct.loc[idx]) else 0.0,
            }
            for idx in equity.index
        ],
    }


def analyze_trades(
    trades: pd.DataFrame,
    initial_capital: float,
    dataset_label: str,
    source: str,
) -> dict:
    frame = trades.copy()
    frame["date"] = pd.to_datetime(frame["date"])
    frame = frame.sort_values("date")
    frame["cumulative_pnl"] = frame["pnl"].cumsum()
    frame["equity"] = initial_capital + frame["cumulative_pnl"]

    wins = frame[frame["pnl"] > 0]
    losses = frame[frame["pnl"] < 0]
    flats = frame[frame["pnl"] == 0]
    total_pnl = float(frame["pnl"].sum())
    n = int(len(frame))

    monthly = (
        frame.set_index("date")
        .resample("ME")["pnl"]
        .sum()
        .rename("pnl")
        .to_frame()
    )
    monthly["year"] = monthly.index.year
    monthly["month"] = monthly.index.month

    yearly = frame.set_index("date").resample("YE")["pnl"].sum()

    equity = frame.set_index("date")["equity"]
    # resample daily for a continuous-looking curve without inventing P&L
    equity_daily = equity.resample("D").ffill()
    dd = max_drawdown(equity)

    by_strategy = []
    if "strategy" in frame.columns:
        grouped = frame.groupby("strategy")["pnl"].agg(["sum", "count", "mean"])
        for name, row in grouped.iterrows():
            by_strategy.append(
                {
                    "strategy": str(name),
                    "total_pnl": float(row["sum"]),
                    "trades": int(row["count"]),
                    "average_trade": float(row["mean"]),
                }
            )

    return {
        "dataset_label": dataset_label,
        "source": source,
        "initial_capital": initial_capital,
        "ending_equity": float(frame["equity"].iloc[-1]),
        "total_pnl": total_pnl,
        "return_on_capital_pct": float(total_pnl / initial_capital * 100) if initial_capital else None,
        "trade_count": n,
        "average_trade": float(frame["pnl"].mean()) if n else 0.0,
        "win_count": int(len(wins)),
        "loss_count": int(len(losses)),
        "flat_count": int(len(flats)),
        "win_rate_pct": float(len(wins) / n * 100) if n else 0.0,
        "average_win": float(wins["pnl"].mean()) if len(wins) else 0.0,
        "average_loss": float(losses["pnl"].mean()) if len(losses) else 0.0,
        "gross_profit": float(wins["pnl"].sum()) if len(wins) else 0.0,
        "gross_loss": float(losses["pnl"].sum()) if len(losses) else 0.0,
        "profit_factor": (
            float(wins["pnl"].sum() / abs(losses["pnl"].sum()))
            if len(losses) and losses["pnl"].sum() != 0
            else None
        ),
        "max_drawdown": dd["max_drawdown"],
        "max_drawdown_pct": dd["max_drawdown_pct"],
        "drawdown_peak": dd["peak_date"],
        "drawdown_trough": dd["trough_date"],
        "first_trade": frame["date"].iloc[0].strftime("%Y-%m-%d"),
        "last_trade": frame["date"].iloc[-1].strftime("%Y-%m-%d"),
        "equity_curve": [
            {"date": r.date.strftime("%Y-%m-%d"), "equity": float(r.equity), "cumulative_pnl": float(r.cumulative_pnl)}
            for r in frame.itertuples()
        ],
        "drawdown_curve": dd["series"],
        "monthly_pnl": [
            {
                "period": idx.strftime("%Y-%m"),
                "pnl": float(row["pnl"]),
            }
            for idx, row in monthly.iterrows()
        ],
        "yearly_pnl": [
            {"year": int(idx.year), "pnl": float(val)} for idx, val in yearly.items()
        ],
        "pnl_distribution": _histogram(frame["pnl"]),
        "by_strategy": by_strategy,
        "note": "Metrics are computed from the supplied trade list. They are research analytics, not a live track record.",
    }


def _histogram(series: pd.Series, bins: int = 12) -> list[dict]:
    counts, edges = pd.cut(series, bins=bins, retbins=True)
    grouped = series.groupby(counts, observed=False).size()
    out = []
    for interval, count in grouped.items():
        out.append(
            {
                "bin_from": float(interval.left),
                "bin_to": float(interval.right),
                "count": int(count),
            }
        )
    return out


def documented_internship_metrics(payload: dict) -> dict:
    """Present documented internship figures without inventing trades."""
    capital = float(payload["initial_capital"])
    periods = payload.get("periods", [])
    total_profit = float(sum(p["profit"] for p in periods))
    yearly = [{"year": int(p["year"]), "pnl": float(p["profit"]), "max_drawdown": float(p["max_drawdown"])} for p in periods]
    # Equity path from yearly profits only — not a daily reconstruction
    equity_points = [{"date": "start", "year": None, "equity": capital, "cumulative_pnl": 0.0}]
    running = 0.0
    for p in periods:
        running += float(p["profit"])
        equity_points.append(
            {
                "date": f"{p['year']}-12-31",
                "year": int(p["year"]),
                "equity": capital + running,
                "cumulative_pnl": running,
            }
        )
    return {
        "dataset_label": payload.get("label", "Internship Backtest Results"),
        "source": payload.get("source"),
        "generated_by_this_application": False,
        "initial_capital": capital,
        "currency": payload.get("currency", "INR"),
        "transaction_costs_included": payload.get("transaction_costs_included", True),
        "total_pnl": total_profit,
        "ending_equity": capital + total_profit,
        "return_on_capital_pct": total_profit / capital * 100,
        "yearly_pnl": yearly,
        "equity_curve_yearly": equity_points,
        "max_drawdown_by_year": yearly,
        "notes": payload.get("notes"),
        "portfolio_description": payload.get("portfolio_description"),
        "monte_carlo": payload.get("monte_carlo"),
        "limitation": (
            "Raw trade-level data from the internship is not included. "
            "Yearly P&L and drawdown figures are documented historical results, "
            "not regenerated by this engine."
        ),
    }


def compare_backtests(analyses: list[dict]) -> dict:
    rows = []
    for item in analyses:
        rows.append(
            {
                "dataset_label": item.get("dataset_label"),
                "source": item.get("source"),
                "total_pnl": item.get("total_pnl"),
                "max_drawdown": item.get("max_drawdown"),
                "trade_count": item.get("trade_count"),
                "average_trade": item.get("average_trade"),
                "win_rate_pct": item.get("win_rate_pct"),
                "return_on_capital_pct": item.get("return_on_capital_pct"),
                "profit_factor": item.get("profit_factor"),
                "monthly_pnl": item.get("monthly_pnl"),
            }
        )
    return {
        "comparisons": rows,
        "note": (
            "Metrics are presented for the researcher to interpret. "
            "This platform does not rank a 'best' strategy."
        ),
    }
