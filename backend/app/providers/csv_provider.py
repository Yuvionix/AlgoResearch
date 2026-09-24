from __future__ import annotations

from io import BytesIO, StringIO

import pandas as pd

from app.providers.base import MarketDataProvider
from app.providers.normalize import normalize_ohlc


class CSVProvider(MarketDataProvider):
    name = "csv_upload"

    def __init__(self, frame: pd.DataFrame | None = None) -> None:
        self._frame = frame

    def available(self) -> bool:
        return self._frame is not None and not self._frame.empty

    def fetch_ohlc(
        self,
        symbol: str,
        start: str | None = None,
        end: str | None = None,
        period: str | None = "1y",
    ) -> pd.DataFrame:
        if self._frame is None:
            raise ValueError("No CSV data loaded.")
        frame = self._frame
        if start:
            frame = frame[frame.index >= pd.Timestamp(start)]
        if end:
            frame = frame[frame.index <= pd.Timestamp(end)]
        return frame

    @classmethod
    def from_bytes(cls, content: bytes, source: str = "csv_upload") -> "CSVProvider":
        text = content.decode("utf-8-sig")
        raw = pd.read_csv(StringIO(text))
        frame = normalize_ohlc(raw, source=source)
        return cls(frame)

    @classmethod
    def from_path(cls, path, source: str = "csv_file") -> "CSVProvider":
        raw = pd.read_csv(path)
        frame = normalize_ohlc(raw, source=source)
        return cls(frame)


def parse_trades_csv(content: bytes) -> pd.DataFrame:
    text = content.decode("utf-8-sig")
    raw = pd.read_csv(StringIO(text))
    if raw.empty:
        raise ValueError("Trade CSV is empty.")
    columns = {c.strip().lower(): c for c in raw.columns}
    date_col = _pick(columns, ("date", "trade_date", "timestamp", "datetime"))
    pnl_col = _pick(columns, ("pnl", "p&l", "profit", "pl", "pnl_inr", "net_pnl"))
    if date_col is None or pnl_col is None:
        raise ValueError(
            "Trade CSV must include a date column and a PnL column "
            "(accepted names: date/trade_date, pnl/net_pnl/profit)."
        )
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(raw[date_col], errors="coerce"),
            "pnl": pd.to_numeric(raw[pnl_col], errors="coerce"),
        }
    )
    if "strategy" in columns:
        frame["strategy"] = raw[columns["strategy"]].astype(str)
    else:
        frame["strategy"] = "unspecified"
    frame = frame.dropna(subset=["date", "pnl"]).sort_values("date")
    if frame.empty:
        raise ValueError("Trade CSV produced no valid date/PnL rows.")
    return frame.reset_index(drop=True)


def _pick(columns: dict, names: tuple[str, ...]):
    for name in names:
        if name in columns:
            return columns[name]
    return None
