from __future__ import annotations

import pandas as pd

from app.analytics.indicators import add_emas


def detect_crossovers(df: pd.DataFrame, fast: int = 20, slow: int = 50) -> pd.DataFrame:
    frame = add_emas(df, fast=fast, slow=slow)
    prev_fast = frame["EMA20"].shift(1)
    prev_slow = frame["EMA50"].shift(1)
    golden = (prev_fast <= prev_slow) & (frame["EMA20"] > frame["EMA50"])
    death = (prev_fast >= prev_slow) & (frame["EMA20"] < frame["EMA50"])
    return frame.assign(golden_cross=golden.fillna(False), death_cross=death.fillna(False))


def latest_crossover(df: pd.DataFrame, kind: str = "golden") -> dict | None:
    col = "golden_cross" if kind == "golden" else "death_cross"
    hits = df[df[col]]
    if hits.empty:
        return None
    idx = hits.index[-1]
    row = hits.iloc[-1]
    return {
        "date": pd.Timestamp(idx).strftime("%Y-%m-%d"),
        "ema20": float(row["EMA20"]),
        "ema50": float(row["EMA50"]),
        "close": float(row["Close"]),
        "kind": kind,
    }


def recent_golden_cross(df: pd.DataFrame, within_days: int = 15) -> dict | None:
    last = latest_crossover(df, "golden")
    if last is None:
        return None
    last_ts = pd.Timestamp(last["date"])
    end_ts = pd.Timestamp(df.index[-1])
    if (end_ts - last_ts).days > within_days:
        return None
    last["sessions_ago"] = int((df.index > last_ts).sum())
    last["calendar_days_ago"] = int((end_ts - last_ts).days)
    return last


def structure_validation(df: pd.DataFrame) -> dict:
    """
    Structural checks used as research filters, not entry instructions.
    - Close stacked above EMA20 and EMA50
    - Recent swing low is not making a new extreme versus the prior window
    """
    last = df.iloc[-1]
    stacked = bool(
        pd.notna(last.get("EMA20"))
        and pd.notna(last.get("EMA50"))
        and last["Close"] > last["EMA20"] > last["EMA50"]
    )
    tail = df.tail(20)
    recent = tail.tail(5)["Low"].min()
    prior = tail.head(15)["Low"].min() if len(tail) >= 10 else tail["Low"].min()
    higher_low = bool(recent >= prior)
    notes = []
    if stacked:
        notes.append("Last close is above EMA 20, and EMA 20 is above EMA 50 (stacked alignment).")
    else:
        notes.append("Price/EMA stack is not aligned (close above EMA 20 above EMA 50 is required).")
    if higher_low:
        notes.append("The most recent 5-session low is not below the prior-window low.")
    else:
        notes.append("Recent lows undercut the prior window — structure filter not passed.")
    passed = stacked and higher_low
    return {
        "passed": passed,
        "stacked_emas": stacked,
        "higher_or_equal_low": higher_low,
        "notes": notes,
        "status": "Passed structure checks" if passed else "Did not pass structure checks",
    }


def fundamental_filter(fundamentals: dict | None) -> dict:
    """
    Conservative filter applied only when reliable fields exist.
    Missing data is reported — it is not treated as a pass.
    """
    if not fundamentals or not fundamentals.get("available"):
        return {
            "applied": False,
            "passed": False,
            "status": "Fundamental data unavailable",
            "notes": [
                "No reliable fundamental snapshot was available for this symbol. "
                "The scanner does not treat missing data as a pass."
            ],
            "fields": {},
        }

    fields = fundamentals.get("fields") or {}
    notes = []
    failures = []
    pe = fields.get("trailing_pe")
    pb = fields.get("price_to_book")
    margins = fields.get("profit_margins")

    if pe is None:
        notes.append("Trailing P/E unavailable.")
        failures.append("missing_pe")
    elif pe <= 0 or pe > 80:
        failures.append("pe_outlier")
        notes.append(f"Trailing P/E {pe:.1f} is outside the research band (0, 80].")
    else:
        notes.append(f"Trailing P/E {pe:.1f} is inside the research band (0, 80].")

    if pb is not None and pb < 0:
        failures.append("negative_pb")
        notes.append("Price-to-book is negative.")
    elif pb is not None:
        notes.append(f"Price-to-book {pb:.2f} recorded.")

    if margins is not None and margins < 0:
        failures.append("negative_margins")
        notes.append("Reported profit margins are negative.")
    elif margins is not None:
        notes.append(f"Profit margins {margins:.2%} recorded.")

    passed = len(failures) == 0 and pe is not None
    return {
        "applied": True,
        "passed": passed,
        "status": "Passed fundamental filter" if passed else "Did not pass fundamental filter",
        "notes": notes,
        "fields": fields,
        "failures": failures,
    }


def research_status(technical_ok: bool, structure_ok: bool, fundamental: dict) -> dict:
    if technical_ok and structure_ok and fundamental.get("passed"):
        label = "Passed Screening Criteria"
        detail = "Technical candidate with structure and fundamental filters passed."
    elif technical_ok and structure_ok:
        label = "Technical Candidate"
        detail = (
            "Golden-crossover and structure checks passed. "
            "Fundamental filter did not pass or data was unavailable."
        )
    elif technical_ok:
        label = "Research Signal"
        detail = "A recent EMA 20/50 golden crossover was detected; structure and/or fundamental filters remain open."
    else:
        label = "Not a current candidate"
        detail = "No recent golden crossover within the configured window."
    return {"label": label, "detail": detail}
