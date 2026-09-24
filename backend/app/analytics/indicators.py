from __future__ import annotations

import math

import numpy as np
import pandas as pd


def ema(series: pd.Series, span: int) -> pd.Series:
    if span < 1:
        raise ValueError("EMA span must be >= 1")
    return series.astype(float).ewm(span=span, adjust=False, min_periods=span).mean()


def sma(series: pd.Series, window: int) -> pd.Series:
    return series.astype(float).rolling(window=window, min_periods=window).mean()


def add_emas(df: pd.DataFrame, fast: int = 20, slow: int = 50) -> pd.DataFrame:
    frame = df.copy()
    return frame.assign(EMA20=ema(frame["Close"], fast), EMA50=ema(frame["Close"], slow))
