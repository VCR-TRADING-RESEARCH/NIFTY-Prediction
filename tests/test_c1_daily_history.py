from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

from scripts.constituent_weekly.audit_c1_daily_history import (
    build_expected_member_sessions,
    parse_daily_payload,
    summarise_daily_coverage,
    summarise_daily_universe,
    daily_audit_status,
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


def test_duplicate_daily_session_is_not_double_counted():
    body = {
        "open": [100.0, 100.0, 101.0],
        "high": [102.0, 102.0, 103.0],
        "low": [99.0, 99.0, 100.0],
        "close": [101.0, 101.0, 102.0],
        "volume": [1000, 1100, 1200],
        "timestamp": [
            epoch_ist("2026-10-27T00:00:00"),
            epoch_ist("2026-10-27T00:00:00"),
            epoch_ist("2026-10-28T00:00:00"),
        ],
    }
    result = summarise_daily_coverage(body, ["2026-10-27", "2026-10-28"])
    assert result["valid_ohlc_session_count"] == 1
    assert result["duplicate_session_count"] == 1
    assert result["missing_session_count"] == 1


def test_unparseable_historical_security_is_counted_as_zero_coverage():
    symbols = ["HDFC", "TATAMOTORS"]
    expected = {
        "HDFC": [f"2023-01-{day:02d}" for day in range(1, 11)],
        "TATAMOTORS": [f"2023-01-{day:02d}" for day in range(1, 11)],
    }
    results = {
        "HDFC": {
            "status": "MISSING_DAILY_ARRAY",
            "valid_ohlc_session_count": 0,
            "valid_volume_session_count": 0,
        },
        "TATAMOTORS": {
            "status": "PASS_RESPONSE",
            "valid_ohlc_session_count": 9,
            "valid_volume_session_count": 9,
        },
    }
    summary = summarise_daily_universe(symbols, expected, results)
    assert summary["point_in_time_symbols_expected"] == 2
    assert summary["symbols_with_parseable_daily_responses"] == 1
    assert summary["symbols_with_unparseable_daily_responses"] == 1
    assert summary["symbols_with_any_ohlc_gap"] == 2
    assert summary["symbols_with_any_ohlcv_gap"] == 2
    assert summary["minimum_symbol_ohlc_coverage_fraction"] == 0.0
    assert summary["median_symbol_ohlc_coverage_fraction"] == 0.45
    assert summary["weighted_ohlc_session_coverage_fraction"] == 0.45


def test_unresolved_security_id_is_also_zero_coverage():
    expected = {"OLDCO": ["2023-01-02", "2023-01-03"]}
    summary = summarise_daily_universe(
        ["OLDCO"], expected, {}, unresolved_symbols=["OLDCO"]
    )
    assert summary["symbols_with_unparseable_daily_responses"] == 1
    assert summary["symbols_with_unresolved_security_id"] == 1
    assert summary["weighted_ohlc_session_coverage_fraction"] == 0.0


def test_daily_audit_status_uses_the_aggregate_summary():
    complete = {
        "expected_member_sessions": 100,
        "valid_member_sessions_ohlc": 100,
        "valid_member_sessions_ohlcv": 100,
    }
    with_gap = {
        "expected_member_sessions": 100,
        "valid_member_sessions_ohlc": 99,
        "valid_member_sessions_ohlcv": 99,
    }
    assert daily_audit_status(complete, 0) == "COMPLETE"
    assert daily_audit_status(with_gap, 0) == "COMPLETED_WITH_GAPS"
    assert daily_audit_status(complete, 1) == "COMPLETED_WITH_GAPS"
