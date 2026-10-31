from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.constituent_weekly.dhan_equity_preflight import analyse_bars, resolve_ids


def epoch_ist(value: str) -> int:
    return int(datetime.fromisoformat(value).replace(tzinfo=ZoneInfo("Asia/Kolkata")).timestamp())


def test_resolve_ids_selects_nse_equity_eq_series_only():
    master = pd.DataFrame({
        "SEM_SMST_SECURITY_ID": ["101", "102", "103", "104"],
        "SEM_TRADING_SYMBOL": ["RELIANCE", "RELIANCE", "TCS", "INFY"],
        "SEM_EXM_EXCH_ID": ["NSE", "NSE", "NSE", "BSE"],
        "SEM_SEGMENT": ["E", "E", "E", "E"],
        "SEM_SERIES": ["EQ", "BE", "EQ", "EQ"],
        "SEM_INSTRUMENT_NAME": ["EQUITY", "EQUITY", "EQUITY", "EQUITY"],
    })
    assert resolve_ids(master) == {"RELIANCE": "101", "TCS": "103"}


def test_analyse_bars_checks_10am_anchor_and_expiry_close_windows():
    body = {
        "open": [100.0, 101.0],
        "high": [101.0, 102.0],
        "low": [99.0, 100.0],
        "close": [100.5, 101.5],
        "volume": [1000, 1200],
        "timestamp": [
            epoch_ist("2026-10-30T10:00:00"),
            epoch_ist("2026-10-30T15:29:00"),
        ],
    }
    result = analyse_bars(body, "RELIANCE", "2026-10-30")
    assert result["status"] == "PASS"
    assert result["bar_count"] == 2
    assert result["anchor_window_bars"] == 1
    assert result["expiry_close_window_bars"] == 1
    assert result["ohlc_volume_invariants_pass"] is True


def test_analyse_bars_fails_closed_on_bad_ohlc_or_missing_expiry_bar():
    body = {
        "open": [100.0],
        "high": [99.0],
        "low": [98.0],
        "close": [100.5],
        "volume": [100],
        "timestamp": [epoch_ist("2026-10-30T10:00:00")],
    }
    result = analyse_bars(body, "RELIANCE", "2026-10-30")
    assert result["status"] == "REQUIRED_BAR_OR_OHLC_CHECK_FAILED"
    assert result["anchor_window_bars"] == 1
    assert result["expiry_close_window_bars"] == 0
    assert result["ohlc_volume_invariants_pass"] is False


def test_analyse_bars_rejects_mismatched_response_arrays():
    body = {
        "open": [100.0],
        "high": [101.0],
        "low": [99.0],
        "close": [100.5],
        "volume": [],
        "timestamp": [epoch_ist("2026-10-30T10:00:00")],
    }
    result = analyse_bars(body, "RELIANCE", "2026-10-30")
    assert result["status"] == "EMPTY_OR_MISMATCHED_ARRAYS"


def test_access_token_helper_prefers_fresh_totp_token(monkeypatch):
    import scripts.constituent_weekly.dhan_equity_preflight as probe
    monkeypatch.setenv("DHAN_CLIENT_ID", "client")
    monkeypatch.setenv("DHAN_ACCESS_TOKEN", "fallback-token-value")
    monkeypatch.setattr(probe, "refresh_dhan_token", lambda: ("fresh-token-value", "client"))
    assert probe.acquire_access_token() == (
        "fresh-token-value", "client", "totp_refresh", "SUCCESS"
    )


def test_access_token_helper_uses_fallback_only_after_refresh_failure(monkeypatch):
    import scripts.constituent_weekly.dhan_equity_preflight as probe
    from live_api.app import PublicPredictionError
    monkeypatch.setenv("DHAN_CLIENT_ID", "client")
    monkeypatch.setenv("DHAN_ACCESS_TOKEN", "fallback-token-value")

    def fail_refresh():
        raise PublicPredictionError("sanitized refresh failure")

    monkeypatch.setattr(probe, "refresh_dhan_token", fail_refresh)
    assert probe.acquire_access_token() == (
        "fallback-token-value", "client", "provided_token_fallback",
        "FAILED_FALLBACK_USED"
    )


def test_access_token_helper_rejects_invalid_fallback_line_breaks(monkeypatch):
    import pytest
    import scripts.constituent_weekly.dhan_equity_preflight as probe
    from live_api.app import PublicPredictionError
    monkeypatch.setenv("DHAN_CLIENT_ID", "client")
    monkeypatch.setenv("DHAN_ACCESS_TOKEN", "token-value\\nBAD_ENV=1")

    def fail_refresh():
        raise PublicPredictionError("refresh failed")

    monkeypatch.setattr(probe, "refresh_dhan_token", fail_refresh)
    with pytest.raises(PublicPredictionError):
        probe.acquire_access_token()
