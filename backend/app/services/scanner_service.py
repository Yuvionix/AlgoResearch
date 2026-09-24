from __future__ import annotations

from app.analytics.crossover import (
    detect_crossovers,
    fundamental_filter,
    recent_golden_cross,
    research_status,
    structure_validation,
)
from app.providers.factory import fetch_with_fallback
from app.providers.local import load_universe
from app.providers.normalize import ohlc_records
from app.providers.yahoo import YahooFinanceProvider
from app.store.research_runs import create_run
from app.validation.ohlc import validate_ohlc


def scan_universe(
    lookback_days: int = 15,
    source: str = "yahoo",
    persist_run: bool = True,
    max_symbols: int | None = None,
) -> dict:
    universe = load_universe()
    if max_symbols:
        universe = universe[:max_symbols]
    candidates = []
    skipped = []
    used_fallback_any = False

    for item in universe:
        symbol = item["symbol"]
        try:
            frame, source_name, used_fallback, warning = fetch_with_fallback(
                symbol, preferred=source, period="1y"
            )
        except Exception as exc:  # noqa: BLE001
            skipped.append({"symbol": symbol, "reason": str(exc)})
            continue
        used_fallback_any = used_fallback_any or used_fallback
        quality = validate_ohlc(frame)
        if not quality["passed"] and quality["score"] < 40:
            skipped.append({"symbol": symbol, "reason": "data quality too low", "quality": quality})
            continue
        tagged = detect_crossovers(frame)
        last = tagged.iloc[-1]
        cross = recent_golden_cross(tagged, within_days=lookback_days)
        technical_ok = cross is not None
        structure = structure_validation(tagged) if technical_ok else {
            "passed": False,
            "status": "Not evaluated — no recent golden crossover",
            "notes": ["Structure checks run only after a recent EMA 20/50 golden crossover."],
        }
        fundamentals = {"available": False}
        if source_name == "yahoo_finance" and technical_ok:
            try:
                fundamentals = YahooFinanceProvider().fundamentals(symbol)
            except Exception as exc:  # noqa: BLE001
                fundamentals = {"available": False, "reason": str(exc)}
        fund = fundamental_filter(fundamentals)
        status = research_status(technical_ok, structure.get("passed", False), fund)
        candidates.append(
            {
                "symbol": symbol,
                "name": item.get("name"),
                "sector": item.get("sector"),
                "price": None if last["Close"] != last["Close"] else float(last["Close"]),
                "ema20": None if last.get("EMA20") != last.get("EMA20") else float(last["EMA20"]) if last.get("EMA20") == last.get("EMA20") else None,
                "ema50": float(last["EMA50"]) if last.get("EMA50") == last.get("EMA50") else None,
                "crossover": cross,
                "technical_status": (
                    "Recent golden crossover" if technical_ok else "No recent golden crossover"
                ),
                "structure": structure,
                "fundamental": fund,
                "research_status": status,
                "data_source": source_name,
                "warning": warning,
                "data_quality_score": quality["score"],
                "is_realtime": False,
            }
        )

    # sort: screening pass first
    rank = {
        "Passed Screening Criteria": 0,
        "Technical Candidate": 1,
        "Research Signal": 2,
        "Not a current candidate": 3,
    }
    candidates.sort(key=lambda row: (rank.get(row["research_status"]["label"], 9), row["symbol"]))

    summary = {
        "universe": "NIFTY 50",
        "scanned": len(universe),
        "returned": len(candidates),
        "skipped": skipped,
        "lookback_days": lookback_days,
        "preferred_source": source,
        "used_fallback": used_fallback_any,
        "candidate_counts": _counts(candidates),
        "note": (
            "Results are research candidates from a rule-based EMA 20/50 screen. "
            "They are not buy instructions, profit claims, or investment advice."
        ),
    }
    payload = {"summary": summary, "candidates": candidates}
    if persist_run:
        payload["research_run"] = create_run(
            analysis_type="golden_crossover",
            instrument="NIFTY",
            universe="NIFTY 50",
            parameters={"lookback_days": lookback_days, "ema_fast": 20, "ema_slow": 50},
            data_period={"start": None, "end": None},
            data_source=source if not used_fallback_any else "mixed_or_fallback",
            result_summary={
                "candidates_passed_or_technical": summary["candidate_counts"].get(
                    "Technical Candidate", 0
                )
                + summary["candidate_counts"].get("Passed Screening Criteria", 0)
                + summary["candidate_counts"].get("Research Signal", 0),
                "scanned": len(universe),
            },
        )
    return payload


def symbol_detail(symbol: str, source: str = "yahoo") -> dict:
    frame, source_name, used_fallback, warning = fetch_with_fallback(
        symbol, preferred=source, period="1y"
    )
    tagged = detect_crossovers(frame)
    quality = validate_ohlc(frame)
    cross = recent_golden_cross(tagged, within_days=30)
    last_golden = None
    hits = tagged[tagged["golden_cross"]]
    if not hits.empty:
        last_golden = {
            "date": hits.index[-1].strftime("%Y-%m-%d"),
            "close": float(hits.iloc[-1]["Close"]),
        }
    structure = structure_validation(tagged)
    last = tagged.iloc[-1]
    why = []
    if cross:
        why.append(
            f"EMA 20 crossed above EMA 50 on {cross['date']} "
            f"({cross['calendar_days_ago']} calendar days before the last session)."
        )
    elif last_golden:
        why.append(
            f"A golden crossover exists on {last_golden['date']} but it is outside the recent-window filter."
        )
    else:
        why.append("No EMA 20/50 golden crossover in the loaded history.")
    why.extend(structure.get("notes", []))
    why.append(
        "Screening identifies research candidates only. It does not output a buy instruction."
    )
    return {
        "symbol": symbol,
        "data_source": source_name,
        "used_fallback": used_fallback,
        "warning": warning,
        "is_realtime": False,
        "data_quality": quality,
        "last_close": float(last["Close"]),
        "ema20": float(last["EMA20"]) if last.get("EMA20") == last.get("EMA20") else None,
        "ema50": float(last["EMA50"]) if last.get("EMA50") == last.get("EMA50") else None,
        "recent_crossover": cross,
        "last_golden_in_history": last_golden,
        "structure": structure,
        "why": why,
        "series": ohlc_records(tagged.tail(180)),
        "markers": [
            {"date": idx.strftime("%Y-%m-%d"), "kind": "golden"}
            for idx in tagged.index[tagged["golden_cross"]]
        ][-8:],
    }


def _counts(rows: list[dict]) -> dict:
    out: dict[str, int] = {}
    for row in rows:
        label = row["research_status"]["label"]
        out[label] = out.get(label, 0) + 1
    return out
