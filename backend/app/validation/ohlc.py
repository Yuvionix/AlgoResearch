from __future__ import annotations

import pandas as pd


def validate_ohlc(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        return {
            "score": 0,
            "row_count": 0,
            "issues": [{"severity": "error", "code": "empty", "message": "No OHLC rows to validate."}],
            "passed": False,
        }

    issues = []
    n = len(df)
    missing = df[["Open", "High", "Low", "Close"]].isna().sum()
    for col, count in missing.items():
        if count:
            issues.append(
                {
                    "severity": "error" if count > n * 0.05 else "warning",
                    "code": "missing_values",
                    "message": f"{int(count)} missing values in {col}.",
                    "count": int(count),
                }
            )

    dupes = int(df.index.duplicated().sum())
    if dupes:
        issues.append(
            {
                "severity": "error",
                "code": "duplicate_dates",
                "message": f"{dupes} duplicate session dates.",
                "count": dupes,
            }
        )

    high_lt_low = int((df["High"] < df["Low"]).sum())
    if high_lt_low:
        issues.append(
            {
                "severity": "error",
                "code": "high_lt_low",
                "message": f"{high_lt_low} rows where High < Low.",
                "count": high_lt_low,
            }
        )

    close_outside = int(
        ((df["Close"] > df["High"]) | (df["Close"] < df["Low"])).sum()
    )
    open_outside = int(((df["Open"] > df["High"]) | (df["Open"] < df["Low"])).sum())
    if close_outside:
        issues.append(
            {
                "severity": "error",
                "code": "close_outside_range",
                "message": f"{close_outside} rows where Close is outside High/Low.",
                "count": close_outside,
            }
        )
    if open_outside:
        issues.append(
            {
                "severity": "warning",
                "code": "open_outside_range",
                "message": f"{open_outside} rows where Open is outside High/Low.",
                "count": open_outside,
            }
        )

    non_positive = int((df[["Open", "High", "Low", "Close"]] <= 0).any(axis=1).sum())
    if non_positive:
        issues.append(
            {
                "severity": "error",
                "code": "impossible_prices",
                "message": f"{non_positive} rows with non-positive prices.",
                "count": non_positive,
            }
        )

    zero_range = int((df["High"] == df["Low"]).sum())
    if zero_range:
        issues.append(
            {
                "severity": "warning",
                "code": "zero_range",
                "message": (
                    f"{zero_range} bars have High == Low. Partition value is defined as 0 for those bars."
                ),
                "count": zero_range,
            }
        )

    if n >= 2:
        dates = pd.DatetimeIndex(df.index).normalize()
        biz = pd.bdate_range(dates.min(), dates.max())
        missing_sessions = int(len(set(biz.date) - set(dates.date)) )
        # weekends already excluded via bdate_range; remaining gaps may be holidays
        if missing_sessions > n * 0.25:
            issues.append(
                {
                    "severity": "warning",
                    "code": "missing_periods",
                    "message": (
                        f"{missing_sessions} business days between first and last session have no bar. "
                        "Some gaps are expected (holidays); a large share may indicate incomplete data."
                    ),
                    "count": missing_sessions,
                }
            )
        elif missing_sessions:
            issues.append(
                {
                    "severity": "info",
                    "code": "calendar_gaps",
                    "message": f"{missing_sessions} business-day gaps (holidays or missing sessions).",
                    "count": missing_sessions,
                }
            )

    error_count = sum(1 for i in issues if i["severity"] == "error")
    warning_count = sum(1 for i in issues if i["severity"] == "warning")
    score = max(0, 100 - error_count * 25 - warning_count * 8)
    if n < 30:
        score = min(score, 70)
        issues.append(
            {
                "severity": "warning",
                "code": "short_history",
                "message": f"Only {n} sessions available; EMA 50 and longer studies are less reliable.",
            }
        )
        score = max(0, score - 5)

    return {
        "score": int(score),
        "row_count": n,
        "start": pd.Timestamp(df.index.min()).strftime("%Y-%m-%d"),
        "end": pd.Timestamp(df.index.max()).strftime("%Y-%m-%d"),
        "error_count": error_count,
        "warning_count": warning_count,
        "issues": issues,
        "passed": error_count == 0,
    }
