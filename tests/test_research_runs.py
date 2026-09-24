from __future__ import annotations

from pathlib import Path

from app.store import research_runs


def test_create_and_fetch_run(tmp_path, monkeypatch):
    path = tmp_path / "runs.sqlite3"
    monkeypatch.setattr(research_runs, "RUNS_DB_PATH", path)
    run = research_runs.create_run(
        analysis_type="golden_crossover",
        instrument="NIFTY",
        universe="NIFTY 50",
        parameters={"lookback_days": 15},
        data_period={"start": "2026-01-01", "end": "2026-09-20"},
        data_source="local_dataset",
        result_summary={"candidates": 12},
    )
    assert run["run_id"].startswith("RUN-")
    fetched = research_runs.get_run(run["run_id"])
    assert fetched["result_summary"]["candidates"] == 12
    assert fetched["parameters"]["lookback_days"] == 15
    listed = research_runs.list_runs()
    assert listed[0]["run_id"] == run["run_id"]
