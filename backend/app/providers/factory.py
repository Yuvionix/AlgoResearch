from __future__ import annotations

from app.providers.base import MarketDataProvider
from app.providers.csv_provider import CSVProvider
from app.providers.local import LocalDatasetProvider
from app.providers.yahoo import YahooFinanceProvider


def get_provider(name: str | None, csv_provider: CSVProvider | None = None) -> MarketDataProvider:
    key = (name or "yahoo").strip().lower()
    if key in {"yahoo", "yfinance", "yahoo_finance"}:
        return YahooFinanceProvider()
    if key in {"local", "local_dataset", "fallback"}:
        return LocalDatasetProvider()
    if key in {"csv", "csv_upload"}:
        if csv_provider is None:
            raise ValueError("CSV provider requested but no file was supplied.")
        return csv_provider
    raise ValueError(f"Unknown data provider: {name}")


def fetch_with_fallback(
    symbol: str,
    preferred: str = "yahoo",
    start: str | None = None,
    end: str | None = None,
    period: str | None = "1y",
    csv_provider: CSVProvider | None = None,
) -> tuple:
    """Returns (frame, source_name, used_fallback: bool, warning: str | None)."""
    preferred_key = (preferred or "yahoo").strip().lower()
    if preferred_key in {"csv", "csv_upload"}:
        provider = get_provider("csv", csv_provider)
        frame = provider.fetch_ohlc(symbol, start=start, end=end, period=period)
        return frame, provider.name, False, None

    if preferred_key in {"local", "local_dataset", "fallback"}:
        provider = LocalDatasetProvider()
        frame = provider.fetch_ohlc(symbol, start=start, end=end, period=period)
        return frame, provider.name, False, None

    yahoo = YahooFinanceProvider()
    try:
        frame = yahoo.fetch_ohlc(symbol, start=start, end=end, period=period)
        return frame, yahoo.name, False, None
    except Exception as exc:  # noqa: BLE001
        local = LocalDatasetProvider()
        try:
            frame = local.fetch_ohlc(symbol, start=start, end=end, period=period)
        except Exception as local_exc:  # noqa: BLE001
            raise RuntimeError(
                f"Yahoo Finance failed ({exc}) and no local dataset was available ({local_exc})."
            ) from local_exc
        warning = (
            f"Yahoo Finance request failed ({exc}). "
            "Analysis is using the local fallback dataset — this is historical research data, not a live feed."
        )
        return frame, local.name, True, warning
