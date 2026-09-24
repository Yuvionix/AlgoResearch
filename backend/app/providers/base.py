from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class MarketDataProvider(ABC):
    """Switchable market-data source. Analytics engines depend on this, not Yahoo."""

    name: str

    @abstractmethod
    def fetch_ohlc(
        self,
        symbol: str,
        start: str | None = None,
        end: str | None = None,
        period: str | None = "1y",
    ) -> pd.DataFrame:
        """Return a DataFrame indexed by date with Open, High, Low, Close, Volume."""

    @abstractmethod
    def available(self) -> bool:
        return True
