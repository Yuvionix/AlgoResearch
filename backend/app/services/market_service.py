from __future__ import annotations

from datetime import datetime, timezone

from app.analytics.classification import classify_market
from app.providers.factory import fetch_with_fallback
from app.providers.normalize import ohlc_records
from app.store.research_runs import create_run
from app.validation.ohlc import validate_ohlc


def run_classification(
    instrument: str,
    analysis_date: str | None = None,
    lookback: int = 5,
    source: str = "yahoo",
    period: str = "6mo",
    persist_run: bool = True,
) -> dict:
    frame, source_name, used_fallback, warning = fetch_with_fallback(
        instrument, preferred=source, period=period
    )
    quality = validate_ohlc(frame)
    result = classify_market(
        frame,
        instrument=instrument,
        analysis_date=analysis_date,
        lookback=lookback,
        source=source_name,
    )
    payload = {
        "result": result,
        "data_quality": quality,
        "used_fallback": used_fallback,
        "warning": warning,
        "ohlc": ohlc_records(frame.tail(90)),
        "is_realtime": False,
        "data_note": "Historical market data. This platform does not provide a real-time feed.",
    }
    if persist_run:
        payload["research_run"] = create_run(
            analysis_type="market_direction",
            instrument=instrument,
            universe=None,
            parameters={"lookback": lookback, "analysis_date": analysis_date, "period": period},
            data_period={
                "start": quality.get("start"),
                "end": result.get("last_session"),
            },
            data_source=source_name,
            result_summary={
                "classification": result["classification"],
                "last_partition_value": result["metrics"]["last_partition_value"],
            },
            details={"why": result["why"]},
        )
    payload["generated_at"] = datetime.now(timezone.utc).isoformat()
    return payload
