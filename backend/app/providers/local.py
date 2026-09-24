from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.config import FALLBACK_DIR, UNIVERSE_PATH
from app.providers.base import MarketDataProvider
from app.providers.normalize import normalize_ohlc


class LocalDatasetProvider(MarketDataProvider):
    name = "local_dataset"

    def __init__(self, directory: Path | None = None) -> None:
        self.directory = directory or FALLBACK_DIR

    def available(self) -> bool:
        return self.directory.exists()

    def list_symbols(self) -> list[str]:
        if not self.directory.exists():
            return []
        return sorted(p.stem.replace("-", ".") for p in self.directory.glob("*.csv"))

    def fetch_ohlc(
        self,
        symbol: str,
        start: str | None = None,
        end: str | None = None,
        period: str | None = "1y",
    ) -> pd.DataFrame:
        path = self._resolve(symbol)
        if path is None:
            raise FileNotFoundError(
                f"No local dataset for {symbol}. Place a CSV in {self.directory}."
            )
        raw = pd.read_csv(path)
        frame = normalize_ohlc(raw, source=self.name)
        if start:
            frame = frame[frame.index >= pd.Timestamp(start)]
        if end:
            frame = frame[frame.index <= pd.Timestamp(end)]
        if frame.empty:
            raise ValueError(f"Local dataset for {symbol} has no rows in the requested window.")
        return frame

    def _resolve(self, symbol: str) -> Path | None:
        directory = self.directory.resolve()
        candidates = [
            self.directory / f"{symbol}.csv",
            self.directory / f"{symbol.replace('.', '-')}.csv",
            self.directory / f"{symbol.replace('.NS', '')}.csv",
        ]
        for path in candidates:
            try:
                resolved = path.resolve()
                resolved.relative_to(directory)
            except ValueError:
                continue
            if resolved.is_file():
                return resolved
        return None


def load_universe() -> list[dict]:
    import json

    if not UNIVERSE_PATH.exists():
        return []
    with UNIVERSE_PATH.open() as handle:
        payload = json.load(handle)
    return payload.get("constituents", [])
