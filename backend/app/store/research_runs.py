from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from app.config import RUNS_PATH

_lock = Lock()


def _empty() -> dict:
    return {"next_seq": 1, "year": datetime.now(timezone.utc).year, "runs": []}


def _load(path: Path) -> dict:
    if not path.exists():
        return _empty()
    with path.open() as handle:
        return json.load(handle)


def _save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w") as handle:
        json.dump(payload, handle, indent=2)
    tmp.replace(path)


def list_runs() -> list[dict]:
    with _lock:
        data = _load(RUNS_PATH)
    return list(reversed(data.get("runs", [])))


def get_run(run_id: str) -> dict | None:
    with _lock:
        data = _load(RUNS_PATH)
    for run in data.get("runs", []):
        if run.get("run_id") == run_id:
            return run
    return None


def create_run(
    analysis_type: str,
    instrument: str | None,
    universe: str | None,
    parameters: dict,
    data_period: dict,
    data_source: str,
    result_summary: dict,
    details: dict | None = None,
) -> dict:
    now = datetime.now(timezone.utc)
    with _lock:
        data = _load(RUNS_PATH)
        year = now.year
        if data.get("year") != year:
            data["year"] = year
            data["next_seq"] = 1
        seq = int(data.get("next_seq", 1))
        run_id = f"RUN-{year}-{seq:03d}"
        record = {
            "run_id": run_id,
            "timestamp": now.isoformat(),
            "instrument": instrument,
            "universe": universe,
            "analysis_type": analysis_type,
            "parameters": parameters,
            "data_period": data_period,
            "data_source": data_source,
            "result_summary": result_summary,
            "details": details or {},
        }
        data.setdefault("runs", []).append(record)
        data["next_seq"] = seq + 1
        _save(RUNS_PATH, data)
    return record
