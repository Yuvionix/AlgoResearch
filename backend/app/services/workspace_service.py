from __future__ import annotations

from app.services.backtest_service import internship_view, sample_dataset_view
from app.services.market_service import run_classification
from app.services.scanner_service import scan_universe
from app.store.research_runs import create_run, get_run, list_runs


def execute_workspace(
    instrument: str,
    analysis_date: str | None,
    lookback: int,
    source: str,
    include_scan: bool,
    include_backtest: bool,
    backtest_dataset: str,
    scan_lookback_days: int,
) -> dict:
    market = run_classification(
        instrument=instrument,
        analysis_date=analysis_date,
        lookback=lookback,
        source=source,
        persist_run=False,
    )
    scan = None
    if include_scan:
        scan = scan_universe(
            lookback_days=scan_lookback_days,
            source=source,
            persist_run=False,
            max_symbols=None,
        )
    backtest = None
    if include_backtest:
        if backtest_dataset == "sample":
            backtest = sample_dataset_view()
        else:
            backtest = internship_view()

    candidate_n = 0
    if scan:
        counts = scan["summary"]["candidate_counts"]
        candidate_n = sum(
            counts.get(k, 0)
            for k in ("Passed Screening Criteria", "Technical Candidate", "Research Signal")
        )

    run = create_run(
        analysis_type="workspace",
        instrument=instrument,
        universe="NIFTY 50" if include_scan else None,
        parameters={
            "lookback": lookback,
            "analysis_date": analysis_date,
            "include_scan": include_scan,
            "include_backtest": include_backtest,
            "backtest_dataset": backtest_dataset if include_backtest else None,
            "scan_lookback_days": scan_lookback_days,
        },
        data_period={
            "start": market["data_quality"].get("start"),
            "end": market["result"].get("last_session"),
        },
        data_source=market["result"]["data_source"],
        result_summary={
            "classification": market["result"]["classification"],
            "candidates": candidate_n,
            "backtest_dataset": backtest_dataset if include_backtest else None,
        },
        details={
            "market": market["result"],
            "scan_summary": scan["summary"] if scan else None,
            "backtest_summary": {
                "dataset_label": backtest.get("dataset_label") if backtest else None,
                "total_pnl": backtest.get("total_pnl") if backtest else None,
            }
            if backtest
            else None,
        },
    )
    return {
        "research_run": run,
        "market": market,
        "scan": scan,
        "backtest": backtest,
    }


def export_run_markdown(run_id: str) -> str:
    run = get_run(run_id)
    if run is None:
        raise KeyError(run_id)
    lines = [
        f"# Research summary {run['run_id']}",
        "",
        f"- Timestamp: {run['timestamp']}",
        f"- Analysis: {run['analysis_type']}",
        f"- Instrument: {run.get('instrument')}",
        f"- Universe: {run.get('universe')}",
        f"- Data source: {run.get('data_source')}",
        f"- Period: {run.get('data_period')}",
        f"- Parameters: {run.get('parameters')}",
        f"- Result summary: {run.get('result_summary')}",
        "",
        "This export records what was run so the analysis can be reproduced. "
        "It is not a trading recommendation.",
        "",
    ]
    return "\n".join(lines)


def dashboard_summary() -> dict:
    runs = list_runs()
    latest_market = next((r for r in runs if r["analysis_type"] in {"market_direction", "workspace"}), None)
    latest_scan = next((r for r in runs if r["analysis_type"] in {"golden_crossover", "workspace"}), None)
    return {
        "research_run_count": len(runs),
        "latest_runs": runs[:8],
        "latest_market": latest_market,
        "latest_scan": latest_scan,
        "internship_backtest": internship_view(),
        "problem_statement": (
            "It reduces fragmentation and repetitive manual work in systematic trading research "
            "by providing a unified workflow for market analysis, technical screening, "
            "strategy evaluation, and risk analytics."
        ),
    }
