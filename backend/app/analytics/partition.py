from __future__ import annotations

import pandas as pd


def partition_value(open_: float, high: float, low: float, close: float) -> float | None:
    """
    Partition Value = abs(Close - Open) / (High - Low) * 100

    When High == Low the range is undefined; return 0.0 and callers should
    record a data note rather than divide by zero.
    """
    if any(v is None or pd.isna(v) for v in (open_, high, low, close)):
        return None
    rng = float(high) - float(low)
    if rng == 0:
        return 0.0
    return abs(float(close) - float(open_)) / rng * 100.0


def partition_series(df: pd.DataFrame) -> pd.Series:
    values = []
    for _, row in df.iterrows():
        values.append(partition_value(row["Open"], row["High"], row["Low"], row["Close"]))
    return pd.Series(values, index=df.index, name="partition_value")
