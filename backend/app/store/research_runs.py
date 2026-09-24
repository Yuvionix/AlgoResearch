from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from app.config import RUNS_DB_PATH

_lock = Lock()


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS research_runs (
            run_id TEXT PRIMARY KEY,
            year INTEGER NOT NULL,
            sequence INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            instrument TEXT,
            universe TEXT,
            analysis_type TEXT NOT NULL,
            parameters TEXT NOT NULL,
            data_period TEXT NOT NULL,
            data_source TEXT NOT NULL,
            result_summary TEXT NOT NULL,
            details TEXT NOT NULL
        )
        """
    )
    connection.commit()
    return connection


def _decode(row: sqlite3.Row) -> dict:
    return {
        "run_id": row["run_id"],
        "timestamp": row["timestamp"],
        "instrument": row["instrument"],
        "universe": row["universe"],
        "analysis_type": row["analysis_type"],
        "parameters": json.loads(row["parameters"]),
        "data_period": json.loads(row["data_period"]),
        "data_source": row["data_source"],
        "result_summary": json.loads(row["result_summary"]),
        "details": json.loads(row["details"]),
    }


def list_runs() -> list[dict]:
    with _lock, _connect(RUNS_DB_PATH) as connection:
        rows = connection.execute("SELECT * FROM research_runs ORDER BY timestamp DESC").fetchall()
    return [_decode(row) for row in rows]


def get_run(run_id: str) -> dict | None:
    with _lock, _connect(RUNS_DB_PATH) as connection:
        row = connection.execute("SELECT * FROM research_runs WHERE run_id = ?", (run_id,)).fetchone()
    return _decode(row) if row else None


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
    year = now.year
    with _lock, _connect(RUNS_DB_PATH) as connection:
        row = connection.execute(
            "SELECT COALESCE(MAX(sequence), 0) AS sequence FROM research_runs WHERE year = ?", (year,)
        ).fetchone()
        sequence = int(row["sequence"]) + 1
        run_id = f"RUN-{year}-{sequence:03d}"
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
        connection.execute(
            """
            INSERT INTO research_runs
            (run_id, year, sequence, timestamp, instrument, universe, analysis_type,
             parameters, data_period, data_source, result_summary, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                year,
                sequence,
                record["timestamp"],
                instrument,
                universe,
                analysis_type,
                json.dumps(parameters),
                json.dumps(data_period),
                data_source,
                json.dumps(result_summary),
                json.dumps(details or {}),
            ),
        )
        connection.commit()
    return record
