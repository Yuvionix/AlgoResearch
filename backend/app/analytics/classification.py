from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from app.analytics.partition import partition_series, partition_value


CLASSIFICATIONS = ("Bullish", "Bearish", "Sideways")


def classify_market(
    df: pd.DataFrame,
    instrument: str,
    analysis_date: str | None = None,
    lookback: int = 5,
    source: str = "unknown",
) -> dict:
    if lookback < 3:
        raise ValueError("lookback must be at least 3 sessions")
    if df.empty:
        raise ValueError("Cannot classify an empty OHLC series")

    frame = df.copy().sort_index()
    if analysis_date:
        cutoff = pd.Timestamp(analysis_date)
        frame = frame[frame.index <= cutoff]
        if frame.empty:
            raise ValueError(f"No OHLC rows on or before {analysis_date}")

    window = frame.tail(lookback)
    if len(window) < 3:
        raise ValueError("Insufficient sessions after filtering for classification")

    window = window.copy()
    window["partition_value"] = partition_series(window)
    window["body_up"] = window["Close"] > window["Open"]
    window["body_down"] = window["Close"] < window["Open"]
    window["close_up"] = window["Close"].diff() > 0

    last = window.iloc[-1]
    first = window.iloc[0]
    last_date = pd.Timestamp(window.index[-1]).strftime("%Y-%m-%d")

    up_days = int(window["body_up"].sum())
    down_days = int(window["body_down"].sum())
    doji_days = int((~window["body_up"] & ~window["body_down"]).sum())
    higher_closes = int(window["close_up"].fillna(False).sum())
    lower_closes = int((window["Close"].diff() < 0).sum())
    higher_highs = int((window["High"].diff() > 0).fillna(False).sum())
    lower_lows = int((window["Low"].diff() < 0).fillna(False).sum())
    net_move = float(last["Close"] - first["Close"])
    net_move_pct = float(net_move / first["Close"] * 100) if first["Close"] else 0.0
    avg_partition = float(window["partition_value"].dropna().mean()) if window["partition_value"].notna().any() else 0.0
    last_partition = partition_value(last["Open"], last["High"], last["Low"], last["Close"])
    zero_range_bars = int(((window["High"] - window["Low"]) == 0).sum())

    bullish_points = []
    bearish_points = []
    sideways_points = []

    if up_days > down_days:
        bullish_points.append(f"{up_days}/{lookback} sessions closed above the open")
    elif down_days > up_days:
        bearish_points.append(f"{down_days}/{lookback} sessions closed below the open")
    else:
        sideways_points.append("Up-close and down-close session counts are balanced")

    if net_move > 0:
        bullish_points.append(f"Close advanced {net_move_pct:.2f}% over the lookback window")
    elif net_move < 0:
        bearish_points.append(f"Close declined {abs(net_move_pct):.2f}% over the lookback window")
    else:
        sideways_points.append("Net close change over the lookback window is approximately zero")

    if higher_closes > lower_closes:
        bullish_points.append(f"More higher closes ({higher_closes}) than lower closes ({lower_closes})")
    elif lower_closes > higher_closes:
        bearish_points.append(f"More lower closes ({lower_closes}) than higher closes ({higher_closes})")
    else:
        sideways_points.append("Higher-close and lower-close counts are balanced")

    last_body_up = bool(last["Close"] > last["Open"])
    last_body_down = bool(last["Close"] < last["Open"])
    if last_partition is not None and last_partition >= 55 and last_body_up:
        bullish_points.append(
            f"Last session partition value {last_partition:.1f} indicates a relatively large bullish body"
        )
    elif last_partition is not None and last_partition >= 55 and last_body_down:
        bearish_points.append(
            f"Last session partition value {last_partition:.1f} indicates a relatively large bearish body"
        )
    elif last_partition is not None and last_partition <= 30:
        sideways_points.append(
            f"Last session partition value {last_partition:.1f} indicates a small body relative to the range"
        )

    if higher_highs > lower_lows:
        bullish_points.append("Highs expanded more often than lows contracted")
    elif lower_lows > higher_highs:
        bearish_points.append("Lows contracted more often than highs expanded")

    bull_score = len(bullish_points)
    bear_score = len(bearish_points)

    if bull_score >= 3 and bull_score > bear_score:
        classification = "Bullish"
    elif bear_score >= 3 and bear_score > bull_score:
        classification = "Bearish"
    else:
        classification = "Sideways"

    rationale = {
        "Bullish": bullish_points,
        "Bearish": bearish_points,
        "Sideways": sideways_points,
    }

    why = [
        f"Classification is rule-based on the last {len(window)} completed sessions ending {last_date}.",
        f"Supporting observations ({classification}):",
        *rationale[classification],
    ]
    if classification != "Sideways":
        conflicting = rationale["Sideways"] + (
            bearish_points if classification == "Bullish" else bullish_points
        )
        if conflicting:
            why.append("Conflicting or neutralizing observations:")
            why.extend(conflicting)

    why.append(
        "This is a descriptive classification of recently observed OHLC structure. "
        "It is not a forecast, not a machine-learning model, and not a trading recommendation."
    )

    observations = []
    for idx, row in window.iterrows():
        observations.append(
            {
                "date": pd.Timestamp(idx).strftime("%Y-%m-%d"),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "partition_value": None if pd.isna(row["partition_value"]) else round(float(row["partition_value"]), 2),
                "session_bias": (
                    "up" if row["Close"] > row["Open"] else "down" if row["Close"] < row["Open"] else "unchanged"
                ),
            }
        )

    return {
        "instrument": instrument,
        "classification": classification,
        "analysis_date_requested": analysis_date,
        "last_session": last_date,
        "lookback_sessions": len(window),
        "data_source": source,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "last_close": float(last["Close"]),
            "last_open": float(last["Open"]),
            "last_high": float(last["High"]),
            "last_low": float(last["Low"]),
            "last_partition_value": None if last_partition is None else round(float(last_partition), 2),
            "average_partition_value": round(avg_partition, 2),
            "up_sessions": up_days,
            "down_sessions": down_days,
            "unchanged_body_sessions": doji_days,
            "higher_closes": higher_closes,
            "lower_closes": lower_closes,
            "higher_highs": higher_highs,
            "lower_lows": lower_lows,
            "net_close_change": round(net_move, 4),
            "net_close_change_pct": round(net_move_pct, 4),
            "zero_range_bars": zero_range_bars,
            "bullish_rule_hits": bull_score,
            "bearish_rule_hits": bear_score,
        },
        "observations": observations,
        "why": why,
        "disclaimer": (
            "Rule-based market-structure description for research only. "
            "Not investment advice and not a prediction of future returns."
        ),
    }
