from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

from scripts.constituent_weekly.audit_c1_daily_history import (
    build_expected_member_sessions,
    parse_daily_payload,
    summarise_daily_coverage,
)


def epoch_ist(value: str) -> int:
    return int(datetime.fromisoformat(value).replace(tzinfo=ZoneInfo("Asia/Kolkata")).timestamp())


def test_expected_member_sessions_obey_half_open_intervals_and_dummy_exclusion():
    membership = pd.DataFrame({
        "symbol": ["AAA", "AAA", "DUMMY"],
        "valid_from": ["2021-11-01", "2021-11-04", "2021-11-01"],
        "valid_to": ["2021-11-04", "", ""],
        "member_type": ["equity_security", "equity_security", "zero_price_dummy"],
        "market_data_required": ["TRUE", "TRUE", "FALSE"],
    })
    expected = build_expected_member_sessions(
        membership,
        ["2021-11-01", "2021-11-02", "2021-11-03", "2021-11-04", "2021-11-05"],
        "2021-11-01",
    )
    assert expected == {"AAA": ["2021-11-01", "2021-11-02", "2021-11-03", "2021-11-04", "2021-11-05"]}


def test_parse_daily_payload_converts_daily_timestamps_to_ist_dates():
    body = {
        "open": [100.0],
        "high": [102.0],
        "low": [99.0],
        "close": [101.0],
        "volume": [1000],
        "timestamp": [epoch_ist("2026-10-27T00:00:00")],
    }
    frame, error = parse_daily_payload(body)
    assert error is None
    assert frame["session_date"].tolist() == ["2026-10-27"]


def test_daily_payload_rejects_mismatched_arrays():
    body = {
        "open": [100.0, 101.0],
        "high": [102.0],
        "low": [99.0, 100.0],
        "close": [101.0, 100.5],
        "volume": [1000, 1200],
        "timestamp": [epoch_ist("2026-10-27T00:00:00")] * 2,
    }
    frame, error = parse_daily_payload(body)
    assert frame is None
    assert error == "DAILY_ARRAY_LENGTH_MISMATCH"


def test_daily_ohlc_and_volume_coverage_are_reported_separately():
    body = {
        "open": [100.0, 101.0],
        "high": [102.0, 99.0],
        "low": [99.0, 100.0],
        "close": [101.0, 100.5],
        "volume": [1000, -1],
        "timestamp": [
            epoch_ist("2026-10-27T00:00:00"),
            epoch_ist("2026-10-28T00:00:00"),
        ],
    }
    result = summarise_daily_coverage(body, ["2026-10-27", "2026-10-28"])
    assert result["valid_ohlc_session_count"] == 1
    assert result["valid_volume_session_count"] == 1
    assert result["ohlc_coverage_fraction"] == 0.5
    assert result["volume_coverage_fraction"] == 0.5


def test_no_daily_bars_is_reported_as_missing_not_fabricated():
    body = {"open": [], "high": [], "low": [], "close": [], "volume": [], "timestamp": []}
    result = summarise_daily_coverage(body, ["2026-10-27"])
    assert result["status"] == "NO_DAILY_BARS"
    assert result["valid_ohlc_session_count"] == 0
    assert result["missing_session_sample"] == ["2026-10-27"]
