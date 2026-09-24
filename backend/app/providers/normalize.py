from __future__ import annotations

import pandas as pd

REQUIRED_OHLC = ("Open", "High", "Low", "Close")


def normalize_ohlc(df: pd.DataFrame, source: str) -> pd.DataFrame:
    if df is None or df.empty:
        raise ValueError("No OHLC rows returned.")

    frame = df.copy()
    frame.columns = [str(c).strip().title() for c in frame.columns]

    rename = {
        "Adj Close": "Adj_Close",
        "Adj_Close": "Adj_Close",
        "Date": "Date",
    }
    frame = frame.rename(columns=rename)

    if "Date" in frame.columns:
        frame = frame.assign(Date=pd.to_datetime(frame["Date"], utc=False, errors="coerce"))
        frame = frame.dropna(subset=["Date"])
        frame = frame.set_index("Date")
    else:
        frame.index = pd.to_datetime(frame.index, utc=False, errors="coerce")
        frame = frame[~frame.index.isna()]

    frame.index = pd.DatetimeIndex(frame.index).tz_localize(None)
    frame.index.name = "Date"
    frame = frame.copy()

    for col in REQUIRED_OHLC:
        if col not in frame.columns:
            raise ValueError(f"Missing required column: {col}")
        frame = frame.assign(**{col: pd.to_numeric(frame[col], errors="coerce")})

    if "Volume" in frame.columns:
        frame = frame.assign(Volume=pd.to_numeric(frame["Volume"], errors="coerce"))
    else:
        frame["Volume"] = pd.NA

    frame = frame.sort_index()
    frame = frame[~frame.index.duplicated(keep="last")]
    frame.attrs["source"] = source
    return frame


def ohlc_records(df: pd.DataFrame, limit: int | None = None) -> list[dict]:
    frame = df.tail(limit) if limit else df
    rows = []
    for idx, row in frame.iterrows():
        item = {
            "date": pd.Timestamp(idx).strftime("%Y-%m-%d"),
            "open": _num(row.get("Open")),
            "high": _num(row.get("High")),
            "low": _num(row.get("Low")),
            "close": _num(row.get("Close")),
            "volume": _num(row.get("Volume")),
        }
        if "EMA20" in frame.columns:
            item["ema20"] = _num(row.get("EMA20"))
        if "EMA50" in frame.columns:
            item["ema50"] = _num(row.get("EMA50"))
        rows.append(item)
    return rows


def _num(value):
    if value is None or pd.isna(value):
        return None
    return float(value)
