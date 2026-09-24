from __future__ import annotations

import pandas as pd
import pytest

from app.analytics.indicators import ema


def test_ema_constant_series():
    series = pd.Series([10.0] * 30)
    result = ema(series, 10)
    assert result.iloc[:8].isna().all()
    assert result.iloc[-1] == pytest.approx(10.0)


def test_ema_reacts_to_step_up():
    values = [100.0] * 20 + [120.0] * 20
    series = pd.Series(values)
    fast = ema(series, 5)
    slow = ema(series, 20)
    assert fast.iloc[-1] > slow.iloc[-1]
    assert fast.iloc[-1] < 120.0
    assert slow.iloc[-1] > 100.0
