from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from scripts.constituent_weekly.audit_c1_daily_history import (
    build_expected_member_sessions,
    parse_daily_payload,
    summarise_daily_coverage,
    summarise_daily_universe,
    daily_audit_status,
    parse_daily_index_sessions,
    encrypt_tejhq_cache_bytes,
    decrypt_tejhq_cache_bytes,
    inspect_tejhq_member_rows,
    compare_dhan_and_tejhq_daily,
    merge_daily_fallback_coverage,
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


def test_dhan_daily_index_calendar_parser_does_not_require_volume():
    body = {
        "open": [100.0, 101.0],
        "high": [102.0, 103.0],
        "low": [99.0, 100.0],
        "close": [101.0, 102.0],
        "timestamp": [
            epoch_ist("2018-04-02T00:00:00"),
            epoch_ist("2018-04-03T00:00:00"),
        ],
    }
    result = parse_daily_index_sessions(body)
    assert result["status"] == "PASS"
    assert result["valid_session_dates"] == ["2018-04-02", "2018-04-03"]
    assert result["valid_session_count"] == 2


def test_dhan_daily_index_calendar_parser_rejects_invalid_ohlc_and_duplicates():
    body = {
        "open": [100.0, 100.0, 101.0],
        "high": [102.0, 102.0, 99.0],
        "low": [99.0, 99.0, 100.0],
        "close": [101.0, 101.0, 100.5],
        "timestamp": [
            epoch_ist("2018-04-02T00:00:00"),
            epoch_ist("2018-04-02T00:00:00"),
            epoch_ist("2018-04-03T00:00:00"),
        ],
    }
    result = parse_daily_index_sessions(body)
    assert result["valid_session_dates"] == []
    assert result["duplicate_session_count"] == 1
    assert result["invalid_ohlc_row_count"] == 1


def test_encrypted_tejhq_cache_roundtrip_and_wrong_key_fails_authentication():
    from cryptography.exceptions import InvalidTag

    payload = b"non-publishable raw partition bytes"
    aad = b"tejhq/indian-markets@pinned:nse/year=2018/nse_2018.parquet"
    encrypted = encrypt_tejhq_cache_bytes(payload, "secret-token-a", aad)
    assert encrypted != payload
    assert decrypt_tejhq_cache_bytes(encrypted, "secret-token-a", aad) == payload
    try:
        decrypt_tejhq_cache_bytes(encrypted, "secret-token-b", aad)
    except InvalidTag:
        pass
    else:
        raise AssertionError("Wrong HF token must not decrypt the personal-use cache.")


def test_tejhq_bhavcopy_rows_filter_eq_series_validate_isin_and_ohlcv():
    frame = pd.DataFrame([
        {
            "date": "2025-10-21", "session_date": "2025-10-21",
            "symbol": "TATAMOTORS", "series": "EQ", "isin": "INE155A01022",
            "open": 650.0, "high": 660.0, "low": 640.0, "close": 655.0, "volume": 1000,
        },
        {
            "date": "2025-10-21", "session_date": "2025-10-21",
            "symbol": "TATAMOTORS", "series": "BE", "isin": "INE155A01022",
            "open": 650.0, "high": 660.0, "low": 640.0, "close": 655.0, "volume": 1000,
        },
        {
            "date": "2025-10-21", "session_date": "2025-10-21",
            "symbol": "TMPV", "series": "EQ", "isin": "INE155A01022",
            "open": 650.0, "high": 660.0, "low": 640.0, "close": 655.0, "volume": 1000,
        },
    ])
    qa, rows = inspect_tejhq_member_rows(frame, "TATAMOTORS", ["2025-10-21"])
    assert qa["source_rows_found"] == 1
    assert qa["unique_isin_count"] == 1
    assert qa["duplicate_session_count"] == 0
    assert qa["valid_session_dates"] == ["2025-10-21"]


def test_tejhq_fallback_fills_only_a_dhan_missing_session_without_double_count():
    expected = ["2025-10-20", "2025-10-21", "2025-10-22"]
    dhan = {
        "status": "PASS_RESPONSE",
        "dhan_status": "PASS_RESPONSE",
        "dhan_valid_ohlc_session_count": 2,
        "dhan_valid_volume_session_count": 2,
        "valid_ohlc_session_count": 2,
        "valid_volume_session_count": 2,
        "missing_session_count": 1,
        "missing_session_sample": ["2025-10-21"],
    }
    result = merge_daily_fallback_coverage(
        dhan,
        expected,
        ["2025-10-20", "2025-10-21", "2025-10-22"],
        "PASS",
        source_crosscheck=None,
        require_crosscheck=False,
    )
    assert result["valid_ohlc_session_count"] == 3
    assert result["valid_volume_session_count"] == 3
    assert result["fallback_valid_session_count"] == 1
    assert result["status"] == "PASS_WITH_TEJHQ_FALLBACK"


def test_tejhq_fallback_does_not_infer_truncated_dhan_missing_date_sample():
    expected = [f"2025-10-{day:02d}" for day in range(1, 26)]
    dhan = {
        "status": "PASS_RESPONSE",
        "dhan_status": "PASS_RESPONSE",
        "dhan_valid_ohlc_session_count": 20,
        "dhan_valid_volume_session_count": 20,
        "valid_ohlc_session_count": 20,
        "valid_volume_session_count": 20,
        "missing_session_count": 5,
        "missing_session_sample": ["2025-10-21"],
    }
    result = merge_daily_fallback_coverage(
        dhan,
        expected,
        expected,
        "PASS",
    )
    assert result["valid_ohlc_session_count"] == 20
    assert result["fallback_valid_session_count"] == 0
    assert result["status"] == "PASS_RESPONSE"


def test_tejhq_tata_crosscheck_requires_every_selected_session_to_match():
    sample = ["2025-10-20", "2025-10-22", "2025-10-23"]
    body = {
        "open": [650.0, 652.0, 654.0],
        "high": [660.0, 662.0, 664.0],
        "low": [640.0, 642.0, 644.0],
        "close": [655.0, 657.0, 659.0],
        "volume": [1000, 1100, 1200],
        "timestamp": [epoch_ist(f"{day}T00:00:00") for day in sample],
    }
    rows = pd.DataFrame({
        "session_date": sample,
        "open": [650.0, 652.0, 654.0],
        "high": [660.0, 662.0, 664.0],
        "low": [640.0, 642.0, 644.0],
        "close": [655.0, 657.0, 659.0],
        "volume": [1000, 1100, 1200],
    })
    passed = compare_dhan_and_tejhq_daily(body, rows, sample)
    assert passed["status"] == "PASS"
    rows.loc[2, "volume"] = 1201
    failed = compare_dhan_and_tejhq_daily(body, rows, sample)
    assert failed["status"] == "FAIL_OR_INCOMPLETE"
    assert failed["dates_mismatched"] == 1


def test_hdfc_last_tradable_session_is_separate_from_hdfcbank():
    membership = pd.DataFrame({
        "symbol": ["HDFC", "HDFC"],
        "valid_from": ["2018-04-01", "2018-04-01"],
        "valid_to": ["2023-07-01", ""],
        "member_type": ["equity_security", "equity_security"],
        "market_data_required": ["TRUE", "TRUE"],
    }).iloc[:1]
    expected = build_expected_member_sessions(
        membership,
        ["2023-06-30", "2023-07-03", "2023-07-04"],
        "2023-06-30",
    )
    assert expected["HDFC"] == ["2023-06-30"]


def test_registered_hdfc_membership_interval_ends_on_last_separate_trading_session():
    root = Path(__file__).resolve().parents[1]
    membership = pd.read_csv(root / "data" / "constituent_weekly" / "nifty50_membership_intervals.csv")
    row = membership.loc[membership["symbol"].eq("HDFC")].iloc[0]
    assert str(row["valid_to"])[:10] == "2023-07-01"


def test_tejhq_fallback_requires_explicit_personal_use_only_flag():
    from scripts.constituent_weekly.audit_c1_daily_history import personal_use_fallback_authorized

    assert personal_use_fallback_authorized("1") is True
    assert personal_use_fallback_authorized(" 1 ") is True
    assert personal_use_fallback_authorized(None) is False
    assert personal_use_fallback_authorized("") is False
    assert personal_use_fallback_authorized("0") is False

def test_tejhq_fallback_reports_only_residual_hdfc_missing_dates():
    expected = [f"2018-04-{day:02d}" for day in range(2, 9)]
    available = [day for day in expected if day not in {"2018-04-04", "2018-04-08"}]
    dhan = {
        "status": "KNOWN_DHAN_DH905",
        "dhan_status": "KNOWN_DHAN_DH905",
        "dhan_valid_ohlc_session_count": 0,
        "dhan_valid_volume_session_count": 0,
        "missing_session_count": len(expected),
        "missing_session_sample": expected[:20],
    }
    result = merge_daily_fallback_coverage(dhan, expected, available, "PASS")
    assert result["valid_ohlc_session_count"] == len(available)
    assert result["missing_session_count"] == 2
    assert result["missing_session_sample"] == ["2018-04-04", "2018-04-08"]
    assert result["missing_session_sample_complete"] is True


def test_tejhq_fallback_keeps_truncated_dhan_missing_sample_unresolved():
    expected = [f"2025-10-{day:02d}" for day in range(1, 26)]
    dhan = {
        "status": "PASS_RESPONSE",
        "dhan_status": "PASS_RESPONSE",
        "dhan_valid_ohlc_session_count": 20,
        "dhan_valid_volume_session_count": 20,
        "valid_ohlc_session_count": 20,
        "valid_volume_session_count": 20,
        "missing_session_count": 5,
        "missing_session_sample": ["2025-10-21"],
    }
    result = merge_daily_fallback_coverage(dhan, expected, expected, "PASS")
    assert result["fallback_valid_session_count"] == 0
    assert result["missing_session_sample"] == ["2025-10-21"]
    assert result["missing_session_sample_complete"] is False


def test_tata_crosscheck_exposes_missing_comparison_date_without_prices():
    sample = ["2025-10-20", "2025-10-22", "2025-10-23"]
    dhan = {
        "open": [650.0, 652.0, 654.0],
        "high": [660.0, 662.0, 664.0],
        "low": [640.0, 642.0, 644.0],
        "close": [655.0, 657.0, 659.0],
        "volume": [1000, 1100, 1200],
        "timestamp": [epoch_ist(f"{day}T00:00:00") for day in sample],
    }
    tejhq = pd.DataFrame({
        "session_date": sample[:2],
        "open": [650.0, 652.0],
        "high": [660.0, 662.0],
        "low": [640.0, 642.0],
        "close": [655.0, 657.0],
        "volume": [1000, 1100],
    })
    result = compare_dhan_and_tejhq_daily(dhan, tejhq, sample)
    assert result["status"] == "FAIL_OR_INCOMPLETE"
    assert result["dates_checked"] == 2
    assert result["dates_matched"] == 2
    assert result["comparison_dates_missing_from_dhan"] == []
    assert result["comparison_dates_missing_from_tejhq"] == ["2025-10-23"]
    assert "open" not in result and "close" not in result

def test_tejhq_cache_directory_expands_home_path(tmp_path):
    from scripts.constituent_weekly.audit_c1_daily_history import resolve_tejhq_encrypted_cache_dir

    home_path = resolve_tejhq_encrypted_cache_dir("~/.cache/bup01-test-cache")
    assert home_path == (Path.home() / ".cache" / "bup01-test-cache").resolve()
    explicit_path = resolve_tejhq_encrypted_cache_dir(str(tmp_path / "encrypted"))
    assert explicit_path == (tmp_path / "encrypted").resolve()


