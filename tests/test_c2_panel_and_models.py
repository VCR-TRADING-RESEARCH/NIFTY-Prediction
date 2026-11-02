from __future__ import annotations

import json

import numpy as np
import pandas as pd

from scripts.constituent_weekly.audit_c1_continuous_dhan_coverage import build_expiry_cycles, verified_expiry_dates
from scripts.constituent_weekly.run_c2_panel_and_models import (
    arrays_from_body,
    equal_cycle_weights,
    event_flags,
    index_features,
    metrics,
    parse_target_bars,
    stock_features,
    summarize_cycle_coverage,
    write_json_report,
    request_profile_with_fallback,
)


def _epoch(value: str) -> int:
    return int(pd.Timestamp(value, tz="Asia/Kolkata").timestamp())


def test_target_parser_uses_first_anchor_and_latest_expiry_proxy_only():
    day = "2026-10-01"
    clocks = ["10:00", "10:01", "15:13", "15:14", "15:25"]
    timestamps = [_epoch(f"{day} {clock}") for clock in clocks]
    body = {
        "timestamp": timestamps,
        "open": [100, 101, 102, 103, 104],
        "high": [101, 102, 104, 105, 999],
        "low": [99, 100, 101, 102, 103],
        "close": [100.5, 101.5, 103, 104, 999],
        "volume": [10, 11, 12, 13, 14],
    }
    result = parse_target_bars(body, {day}, {day}, require_volume=True)[day]
    assert result["anchor_ok"] is True
    assert result["expiry_ok"] is True
    assert result["anchor_open"] == 100.0
    assert result["expiry_close"] == 104.0
    assert result["expiry_time"].startswith(f"{day}T15:14:00")


def test_target_parser_rejects_invalid_ohlc_and_missing_stock_volume():
    day = "2026-10-01"
    invalid = {
        "timestamp": [_epoch(f"{day} 10:00"), _epoch(f"{day} 15:14")],
        "open": [100, 100], "high": [99, 101], "low": [98, 99],
        "close": [100, 100], "volume": [1, 1],
    }
    result = parse_target_bars(invalid, {day}, {day}, require_volume=True)[day]
    assert result["anchor_ok"] is False
    assert result["expiry_ok"] is True

    missing_volume = {k: v for k, v in invalid.items() if k != "volume"}
    assert arrays_from_body(missing_volume, require_volume=True) is None


def test_stock_features_are_asof_safe_and_ignore_future_rows():
    dates = pd.bdate_range("2026-06-01", periods=90)
    close = 100 * np.cumprod(1 + np.linspace(-0.002, 0.003, len(dates)))
    frame = pd.DataFrame({
        "session_date": dates.strftime("%Y-%m-%d"),
        "open": close * 0.999, "high": close * 1.01, "low": close * 0.99,
        "close": close, "volume": np.arange(len(dates)) + 1000,
    })
    asof = dates[75].strftime("%Y-%m-%d")
    original = stock_features(frame, asof)
    changed = frame.copy()
    changed.loc[changed["session_date"] >= asof, ["open", "high", "low", "close", "volume"]] = 1e9
    future_changed = stock_features(changed, asof)
    assert original is not None and future_changed is not None
    assert original == future_changed


def test_event_crossing_flag_is_date_bounded():
    events = pd.DataFrame([{
        "event_date": "2025-10-14",
        "affected_symbols": "TATAMOTORS;DUMMYTATAM;TMPV",
    }])
    assert event_flags("TATAMOTORS", "2025-10-08", "2025-10-14", events) == (1, 1)
    assert event_flags("TATAMOTORS", "2025-10-14", "2025-10-21", events) == (1, 0)
    assert event_flags("RELIANCE", "2025-10-08", "2025-10-14", events) == (0, 0)


def test_training_sample_weights_equalise_expiry_cycles():
    cycle_ids = pd.Series([1, 1, 2, 2, 2, 2])
    weights = equal_cycle_weights(cycle_ids)
    assert np.isclose(weights[:2].sum(), weights[2:].sum())
    assert np.isclose(weights.mean(), 1.0)


def test_model_metric_calculation_is_well_formed():
    result = metrics(np.array([0, 0, 1, 1]), np.array([0.2, 0.4, 0.6, 0.8]))
    assert result["n"] == 4
    assert result["accuracy"] == 1.0
    assert result["balanced_accuracy"] == 1.0
    assert result["brier"] <= 0.1
    assert result["roc_auc"] == 1.0


def test_index_features_accept_official_nifty_daily_column_names():
    dates = pd.bdate_range("2025-01-01", periods=90)
    close = 20000 + np.arange(len(dates)) * 4.0
    frame = pd.DataFrame({
        "session_date": dates.strftime("%Y-%m-%d"),
        "official_open": close - 5, "official_high": close + 20,
        "official_low": close - 30, "official_close": close,
    })
    result = index_features(frame, dates[75].strftime("%Y-%m-%d"))
    assert result is not None
    assert set(result) == {
        "idx_ret_1d", "idx_ret_5d", "idx_ret_10d", "idx_ret_20d", "idx_ret_60d",
        "idx_vol_10d", "idx_vol_20d", "idx_vol_60d", "idx_range_10d", "idx_range_20d",
    }
    assert np.isfinite(list(result.values())).all()


def test_write_json_report_emits_one_valid_json_document(tmp_path):
    path = tmp_path / "nested" / "failure.json"
    payload = {"status": "FAILED", "fatal_error_message": "synthetic diagnostic"}
    write_json_report(path, payload)
    text = path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\\n")
    assert json.loads(text) == payload


def test_cycle_coverage_summary_applies_both_member_thresholds():
    index_panel = pd.DataFrame({"cycle_idx": [1, 2, 3]})
    eligible_counts = pd.Series({1: 48, 2: 47, 3: 46})
    member_count = {1: 50, 2: 50, 3: 50}
    result = summarize_cycle_coverage(index_panel, eligible_counts, member_count)
    assert result["cycles_with_valid_index_targets"] == 3
    assert result["cycles_passing_47_94_rule"] == 2
    assert result["eligible_stock_count_histogram"] == {"46": 1, "47": 1, "48": 1}

def test_c2_calendar_accepts_verified_shifted_weekly_contract_expiries():
    frame = pd.DataFrame({
        "verified_expiry_trade_date": ["2021-11-03", "2025-10-20", "2025-10-28", "2025-11-04"],
        "status": [
            "verified_shifted_nifty_weekly_expiry",
            "verified_shifted_nifty_weekly_expiry",
            "candidate",
            "verified_nifty_weekly_expiry",
        ],
        "contract_expiry_present": [True, True, True, False],
    })
    assert verified_expiry_dates(frame) == ["2021-11-03", "2025-10-20"]


def test_c2_calendar_creates_separate_weekly_cycles_around_shifted_expiry():
    membership = pd.DataFrame({
        "symbol": ["AAA", "BBB"],
        "valid_from": ["2020-01-01", "2020-01-01"],
        "valid_to": ["", ""],
        "member_type": ["equity_security", "equity_security"],
        "market_data_required": ["TRUE", "TRUE"],
    })
    cycles = build_expiry_cycles(
        ["2025-10-14", "2025-10-20", "2025-10-28"],
        [
            "2025-10-14", "2025-10-15", "2025-10-16", "2025-10-17",
            "2025-10-20", "2025-10-21", "2025-10-23", "2025-10-24",
            "2025-10-27", "2025-10-28",
        ],
        membership,
        "2025-10-01",
        "2025-10-28",
        {"2025-10-21"},
    )
    assert [(c["anchor_date"], c["expiry_date"]) for c in cycles] == [
        ("2025-10-15", "2025-10-20"),
        ("2025-10-23", "2025-10-28"),
    ]

def test_dhan_profile_fallback_uses_provided_token_only_after_fresh_token_http_failure():
    class Response:
        def __init__(self, ok, status_code):
            self.ok = ok
            self.status_code = status_code

    supplied = []
    def fake_profile(token):
        supplied.append(token)
        return Response(token == "known-good-fallback", 200 if token == "known-good-fallback" else 401)

    token, profile, method, fallback = request_profile_with_fallback(
        "fresh-totp-token", "totp_refresh", "known-good-fallback", fake_profile
    )
    assert supplied == ["fresh-totp-token", "known-good-fallback"]
    assert token == "known-good-fallback"
    assert profile.ok is True
    assert method == "provided_token_fallback"
    assert fallback == "PASS"


def test_dhan_profile_fallback_is_not_used_for_non_totp_auth():
    class Response:
        ok = False
        status_code = 401

    supplied = []
    def fake_profile(token):
        supplied.append(token)
        return Response()

    token, profile, method, fallback = request_profile_with_fallback(
        "supplied-token", "provided_token_fallback", "another-token", fake_profile
    )
    assert supplied == ["supplied-token"]
    assert token == "supplied-token"
    assert profile.status_code == 401
    assert method == "provided_token_fallback"
    assert fallback == "NOT_NEEDED"
