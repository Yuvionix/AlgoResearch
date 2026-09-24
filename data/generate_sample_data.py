"""Generate labelled synthetic OHLC, index, and sample trade files."""

from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FALLBACK = ROOT / "data" / "fallback_ohlc"
DATA = ROOT / "data"


def business_days(start: date, n: int) -> list[date]:
    days = []
    cur = start
    while len(days) < n:
        if cur.weekday() < 5:
            days.append(cur)
        cur += timedelta(days=1)
    return days


def bars_from_close(closes: np.ndarray, dates: list[date], seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for i, close in enumerate(closes):
        prev = closes[i - 1] if i else close
        open_ = float(prev * (1 + rng.normal(0, 0.002)))
        high = float(max(open_, close) * (1 + abs(rng.normal(0.002, 0.003))))
        low = float(min(open_, close) * (1 - abs(rng.normal(0.002, 0.003))))
        if high < low:
            high, low = low, high
        close_f = float(close)
        close_f = min(max(close_f, low), high)
        open_ = min(max(open_, low), high)
        vol = int(rng.integers(200_000, 2_000_000))
        rows.append(
            {
                "Date": dates[i].isoformat(),
                "Open": round(open_, 2),
                "High": round(high, 2),
                "Low": round(low, 2),
                "Close": round(close_f, 2),
                "Volume": vol,
            }
        )
    return pd.DataFrame(rows)


def path_with_golden_cross(n: int, start_price: float, seed: int) -> np.ndarray:
    """Down-drift then recover so EMA20 crosses above EMA50 near the end."""
    rng = np.random.default_rng(seed)
    px = [start_price]
    for i in range(1, n):
        if i < n - 40:
            drift = -0.0012
        else:
            drift = 0.0045
        px.append(px[-1] * (1 + drift + rng.normal(0, 0.008)))
    return np.array(px)


def path_chop(n: int, start_price: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    px = [start_price]
    for _ in range(1, n):
        px.append(px[-1] * (1 + rng.normal(0, 0.006)))
    return np.array(px)


def path_down(n: int, start_price: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    px = [start_price]
    for _ in range(1, n):
        px.append(px[-1] * (1 - 0.001 + rng.normal(0, 0.007)))
    return np.array(px)


def path_up(n: int, start_price: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    px = [start_price]
    for _ in range(1, n):
        px.append(px[-1] * (1 + 0.0012 + rng.normal(0, 0.006)))
    return np.array(px)


def main() -> None:
    FALLBACK.mkdir(parents=True, exist_ok=True)
    n = 180
    dates = business_days(date(2025, 10, 1), n)

    specs = {
        "NIFTY": (path_up, 22500, 1),
        "RELIANCE": (path_with_golden_cross, 1400, 11),
        "TCS": (path_with_golden_cross, 3600, 12),
        "HDFCBANK": (path_chop, 1650, 13),
        "ICICIBANK": (path_with_golden_cross, 1100, 14),
        "INFY": (path_down, 1550, 15),
        "ITC": (path_chop, 450, 16),
        "SBIN": (path_with_golden_cross, 780, 17),
        "TATAMOTORS": (path_down, 950, 18),
        "WIPRO": (path_chop, 480, 19),
        "MARUTI": (path_up, 12500, 20),
        "SUNPHARMA": (path_with_golden_cross, 1700, 21),
    }
    for symbol, (fn, start, seed) in specs.items():
        closes = fn(n, start, seed)
        frame = bars_from_close(closes, dates, seed + 99)
        frame.to_csv(FALLBACK / f"{symbol}.csv", index=False)

    # invalid fixture for tests
    bad = FALLBACK / "_invalid_fixture.csv"
    with bad.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
        writer.writerow(["2026-01-02", 100, 90, 95, 101, 1000])  # high < low, close outside
        writer.writerow(["2026-01-02", 100, 110, 90, 105, 1000])  # duplicate date
        writer.writerow(["2026-01-03", -1, 10, 2, 5, 1000])  # impossible
        writer.writerow(["2026-01-06", 10, 10, 10, 10, 1000])  # zero range

    # synthetic trades spanning 2024-2025 — labelled sample only
    rng = np.random.default_rng(7)
    trade_dates = business_days(date(2024, 2, 1), 48)
    strategies = ["NIFTY_expiry_sample", "SENSEX_expiry_sample"]
    rows = []
    for i, d in enumerate(trade_dates):
        pnl = float(rng.normal(1800, 4200))
        if i in {10, 22, 35}:
            pnl = float(-abs(rng.normal(5500, 800)))
        rows.append(
            {
                "date": d.isoformat(),
                "strategy": strategies[i % 2],
                "pnl": round(pnl, 2),
            }
        )
    pd.DataFrame(rows).to_csv(DATA / "sample_trades.csv", index=False)
    print(f"Wrote {len(specs)} OHLC files and sample_trades.csv")


if __name__ == "__main__":
    main()
