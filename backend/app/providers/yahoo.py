from __future__ import annotations

import pandas as pd

from app.config import OFFLINE, YFINANCE_TIMEOUT
from app.providers.base import MarketDataProvider
from app.providers.normalize import normalize_ohlc

YAHOO_ALIASES = {
    "NIFTY": "^NSEI",
    "NIFTY50": "^NSEI",
    "NSEI": "^NSEI",
    "^NSEI": "^NSEI",
    "SENSEX": "^BSESN",
    "BSESN": "^BSESN",
    "^BSESN": "^BSESN",
}


def to_yahoo_symbol(symbol: str) -> str:
    key = symbol.strip().upper()
    if key in YAHOO_ALIASES:
        return YAHOO_ALIASES[key]
    if key.endswith(".NS") or key.endswith(".BO") or key.startswith("^"):
        return key
    return f"{key}.NS"


class YahooFinanceProvider(MarketDataProvider):
    name = "yahoo_finance"

    def available(self) -> bool:
        return not OFFLINE

    def fetch_ohlc(
        self,
        symbol: str,
        start: str | None = None,
        end: str | None = None,
        period: str | None = "1y",
    ) -> pd.DataFrame:
        if OFFLINE:
            raise RuntimeError("Yahoo Finance disabled (ALGORESEARCH_OFFLINE=1).")

        import yfinance as yf

        ticker = to_yahoo_symbol(symbol)
        kwargs = {"auto_adjust": False, "progress": False, "threads": False}
        try:
            if start or end:
                raw = yf.download(ticker, start=start, end=end, timeout=YFINANCE_TIMEOUT, **kwargs)
            else:
                raw = yf.download(
                    ticker, period=period or "1y", timeout=YFINANCE_TIMEOUT, **kwargs
                )
        except TypeError:
            # older yfinance without timeout
            if start or end:
                raw = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
            else:
                raw = yf.download(ticker, period=period or "1y", progress=False, auto_adjust=False)

        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = [col[0] if isinstance(col, tuple) else col for col in raw.columns]

        if raw is None or raw.empty:
            raise ValueError(f"Yahoo Finance returned no rows for {ticker}.")
        return normalize_ohlc(raw, source=self.name)

    def fundamentals(self, symbol: str) -> dict:
        if OFFLINE:
            return {"available": False, "reason": "offline_mode"}
        import yfinance as yf

        ticker = to_yahoo_symbol(symbol)
        try:
            info = yf.Ticker(ticker).info or {}
        except Exception as exc:  # noqa: BLE001 — provider boundary
            return {"available": False, "reason": str(exc)}

        fields = {
            "long_name": info.get("longName") or info.get("shortName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "trailing_pe": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "price_to_book": info.get("priceToBook"),
            "market_cap": info.get("marketCap"),
            "dividend_yield": info.get("dividendYield"),
            "profit_margins": info.get("profitMargins"),
        }
        present = {k: v for k, v in fields.items() if v not in (None, "")}
        return {
            "available": bool(present),
            "yahoo_symbol": ticker,
            "fields": present,
        }
