from __future__ import annotations

import pandas as pd
import pytest

from app.providers.csv_provider import CSVProvider, parse_trades_csv
from app.providers.local import LocalDatasetProvider
from app.providers.normalize import normalize_ohlc
from app import create_app


def test_parse_ohlc_csv_bytes():
    raw = b"Date,Open,High,Low,Close,Volume\n2026-01-02,10,12,9,11,100\n2026-01-05,11,13,10,12,110\n"
    provider = CSVProvider.from_bytes(raw)
    frame = provider.fetch_ohlc("X")
    assert list(frame.columns[:4]) == ["Open", "High", "Low", "Close"]
    assert len(frame) == 2


def test_parse_trades_csv():
    raw = b"date,pnl,strategy\n2024-01-02,100,A\n2024-01-03,-40,B\n"
    frame = parse_trades_csv(raw)
    assert len(frame) == 2
    assert frame["pnl"].sum() == 60


def test_parse_trades_rejects_missing_pnl():
    with pytest.raises(ValueError):
        parse_trades_csv(b"date,qty\n2024-01-02,1\n")


def test_local_provider_rejects_path_traversal(tmp_path):
    dataset_dir = tmp_path / "fallback_ohlc"
    dataset_dir.mkdir()
    (tmp_path / "outside.csv").write_text(
        "Date,Open,High,Low,Close\n2026-01-02,10,12,9,11\n"
    )

    provider = LocalDatasetProvider(dataset_dir)

    with pytest.raises(FileNotFoundError):
        provider.fetch_ohlc("../outside")


def test_local_provider_rejects_symlink_escape(tmp_path):
    dataset_dir = tmp_path / "fallback_ohlc"
    dataset_dir.mkdir()
    outside = tmp_path / "outside.csv"
    outside.write_text("Date,Open,High,Low,Close\n2026-01-02,10,12,9,11\n")
    (dataset_dir / "LINK.csv").symlink_to(outside)

    provider = LocalDatasetProvider(dataset_dir)

    with pytest.raises(FileNotFoundError):
        provider.fetch_ohlc("LINK")


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        ("/api/market/classify", {"lookback": "not-a-number"}),
        ("/api/market/classify", {"instrument": "../../etc/passwd"}),
        ("/api/scanner/run", {"lookback_days": 999999}),
    ],
)
def test_invalid_api_parameters_return_bad_request(path, payload):
    client = create_app().test_client()
    response = client.post(path, json=payload)
    assert response.status_code == 400
    assert response.get_json()["error"] in {"classification_failed", "scan_failed"}
