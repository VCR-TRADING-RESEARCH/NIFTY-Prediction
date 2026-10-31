from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.constituent_weekly.dhan_equity_preflight import analyse_bars, membership_symbol_sets, resolve_ids


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


def test_analyse_bars_accepts_1514_close_as_1515_expiry_proxy():
    body = {
        "open": [100.0, 101.0, 102.0],
        "high": [101.0, 102.0, 103.0],
        "low": [99.0, 100.0, 101.0],
        "close": [100.5, 101.5, 102.5],
        "volume": [1000, 1200, 900],
        "timestamp": [
            epoch_ist("2026-10-30T10:00:00"),
            epoch_ist("2026-10-30T15:14:00"),
            epoch_ist("2026-10-30T15:29:00"),
        ],
    }
    result = analyse_bars(body, "RELIANCE", "2026-10-30")
    assert result["status"] == "PASS"
    assert result["bar_count"] == 3
    assert result["anchor_window_bars"] == 1
    assert result["expiry_proxy_bar_count"] == 1
    assert result["expiry_proxy_bar_time_ist"] == "2026-10-30T15:14:00+05:30"
    assert result["expiry_proxy_cutoff_ist"] == "15:15:00"
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
    assert result["expiry_proxy_bar_count"] == 0
    assert result["expiry_proxy_bar_time_ist"] is None
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
    from types import SimpleNamespace

    monkeypatch.setenv("DHAN_CLIENT_ID", "client")
    monkeypatch.setenv("DHAN_PIN", "123456")
    monkeypatch.setenv("DHAN_TOTP_SECRET", "fake-secret")
    monkeypatch.setenv("DHAN_ACCESS_TOKEN", "fallback-token-value")
    monkeypatch.setattr(probe.pyotp, "TOTP", lambda secret: SimpleNamespace(now=lambda: "654321"))

    captured = {}

    class Response:
        ok = True
        status_code = 200

        @staticmethod
        def json():
            return {"accessToken": "fresh-token-value-that-is-long-enough"}

    def fake_post(url, *, params, timeout):
        captured.update(url=url, params=params, timeout=timeout)
        return Response()

    monkeypatch.setattr(probe.requests, "post", fake_post)
    token, client_id, method, status, diagnostics = probe.acquire_access_token()
    assert token == "fresh-token-value-that-is-long-enough"
    assert client_id == "client"
    assert method == "totp_refresh"
    assert status == "SUCCESS"
    assert captured["url"] == probe.AUTH_URL
    assert captured["params"] == {"dhanClientId": "client", "pin": "123456", "totp": "654321"}
    assert diagnostics["response_keys"] == ["accessToken"]
    assert diagnostics["access_token_field_type"] == "str"
    assert "accessToken" not in str(diagnostics["token_container"])


def test_access_token_helper_uses_fallback_only_after_refresh_failure(monkeypatch):
    import scripts.constituent_weekly.dhan_equity_preflight as probe
    from types import SimpleNamespace

    monkeypatch.setenv("DHAN_CLIENT_ID", "client")
    monkeypatch.setenv("DHAN_PIN", "123456")
    monkeypatch.setenv("DHAN_TOTP_SECRET", "fake-secret")
    monkeypatch.setenv("DHAN_ACCESS_TOKEN", "fallback-token-value")
    monkeypatch.setattr(probe.pyotp, "TOTP", lambda secret: SimpleNamespace(now=lambda: "654321"))

    class Response:
        ok = True
        status_code = 200

        @staticmethod
        def json():
            return {"status": "error", "message": "provider message must not be copied"}

    monkeypatch.setattr(probe.requests, "post", lambda *args, **kwargs: Response())
    token, client_id, method, status, diagnostics = probe.acquire_access_token()
    assert token == "fallback-token-value"
    assert client_id == "client"
    assert method == "provided_token_fallback"
    assert status == "FAILED_FALLBACK_USED"
    assert diagnostics["response_keys"] == ["message", "status"]
    assert "provider message must not be copied" not in str(diagnostics)


def test_access_token_helper_rejects_invalid_fallback_line_breaks(monkeypatch):
    import pytest
    import scripts.constituent_weekly.dhan_equity_preflight as probe
    from types import SimpleNamespace

    monkeypatch.setenv("DHAN_CLIENT_ID", "client")
    monkeypatch.setenv("DHAN_PIN", "123456")
    monkeypatch.setenv("DHAN_TOTP_SECRET", "fake-secret")
    monkeypatch.setenv("DHAN_ACCESS_TOKEN", "token-value\nBAD_ENV=1")
    monkeypatch.setattr(probe.pyotp, "TOTP", lambda secret: SimpleNamespace(now=lambda: "654321"))

    class Response:
        ok = True
        status_code = 200

        @staticmethod
        def json():
            return {"message": "no access token"}

    monkeypatch.setattr(probe.requests, "post", lambda *args, **kwargs: Response())
    with pytest.raises(probe.PublicPredictionError):
        probe.acquire_access_token()


def test_auth_response_diagnostics_never_return_response_values():
    import scripts.constituent_weekly.dhan_equity_preflight as probe

    response = {
        "status": "failed",
        "message": "secret provider message",
        "data": {"accessToken": "x" * 40},
    }
    result = probe.auth_response_diagnostics(response)
    assert result["response_keys"] == ["data", "message", "status"]
    assert result["data_keys"] == ["accessToken"]
    assert result["access_token_field_type"] == "str"
    assert result["access_token_length"] == 40
    assert "secret provider message" not in str(result)
    assert "x" * 40 not in str(result)



def test_analyse_bars_never_uses_a_candle_after_the_1515_cutoff():
    body = {
        "open": [100.0, 100.5, 101.0],
        "high": [100.5, 101.0, 101.5],
        "low": [99.5, 100.0, 100.5],
        "close": [100.2, 100.8, 101.2],
        "volume": [500, 600, 700],
        "timestamp": [
            epoch_ist("2026-10-30T15:13:00"),
            epoch_ist("2026-10-30T15:14:00"),
            epoch_ist("2026-10-30T15:15:00"),
        ],
    }
    result = analyse_bars(body, "RELIANCE", "2026-10-30", require_anchor=False)
    assert result["status"] == "PASS"
    assert result["expiry_proxy_bar_time_ist"] == "2026-10-30T15:14:00+05:30"


def test_request_intraday_probe_reports_only_sanitised_bar_quality(monkeypatch):
    import scripts.constituent_weekly.dhan_equity_preflight as probe

    captured = {}

    class Response:
        ok = True
        status_code = 200

        @staticmethod
        def json():
            return {
                "open": [100.0, 101.0],
                "high": [101.0, 102.0],
                "low": [99.0, 100.0],
                "close": [100.5, 101.5],
                "volume": [100, 200],
                "timestamp": [
                    epoch_ist("2026-10-29T10:00:00"),
                    epoch_ist("2026-10-29T15:14:00"),
                ],
            }

    def fake_post(url, *, headers, json, timeout):
        captured.update(url=url, headers=headers, body=json, timeout=timeout)
        return Response()

    monkeypatch.setattr(probe.requests, "post", fake_post)
    result = probe.request_intraday_probe({"access-token": "secret"}, "RELIANCE", "12345", "2026-10-29")

    assert result["status"] == "PASS"
    assert result["anchor_window_bars"] == 1
    assert result["expiry_proxy_bar_time_ist"] == "2026-10-29T15:14:00+05:30"
    assert "securityId" in captured["body"]
    assert "close" not in result
    assert "prices" not in result
    assert "secret" not in str(result)


def test_analyse_intraday_range_validates_anchor_and_expiry_for_all_sessions():
    import numpy as np
    from scripts.constituent_weekly.dhan_equity_preflight import analyse_intraday_range

    body = {
        "open": [100.0, 100.5, 101.0, 101.5],
        "high": [101.0, 101.5, 102.0, 102.5],
        "low": [99.0, 99.5, 100.0, 100.5],
        "close": [100.5, 101.0, 101.5, 102.0],
        "volume": [100, 110, 120, 130],
        "timestamp": [
            epoch_ist("2022-10-03T10:00:00"),
            epoch_ist("2022-10-03T15:14:00"),
            epoch_ist("2022-10-04T10:03:00"),
            epoch_ist("2022-10-04T15:13:00"),
            # Special evening-only Muhurat session: should not count as a missing regular-session bar.
            epoch_ist("2022-10-24T18:15:00"),
            epoch_ist("2022-10-24T19:14:00"),
        ],
    }
    body["open"].extend([103.0, 103.5])
    body["high"].extend([103.5, 104.0])
    body["low"].extend([102.5, 103.0])
    body["close"].extend([103.2, 103.7])
    body["volume"].extend([140, 150])
    result = analyse_intraday_range(body, "RELIANCE", "2022-10-03", "2022-10-24")
    assert result["status"] == "PASS"
    assert result["bar_count"] == 6
    assert result["response_calendar_date_count"] == 3
    assert result["session_count"] == 2
    assert result["non_standard_session_dates"] == ["2022-10-24"]
    assert result["anchor_sessions_present"] == 2
    assert result["expiry_proxy_sessions_present"] == 2
    assert result["contains_raw_price_values"] is False
    assert "close" not in result


def test_analyse_intraday_range_fails_when_a_session_has_no_expiry_proxy():
    from scripts.constituent_weekly.dhan_equity_preflight import analyse_intraday_range

    body = {
        "open": [100.0, 100.5, 101.0],
        "high": [101.0, 101.5, 102.0],
        "low": [99.0, 99.5, 100.0],
        "close": [100.5, 101.0, 101.5],
        "volume": [100, 110, 120],
        "timestamp": [
            epoch_ist("2022-10-03T10:00:00"),
            epoch_ist("2022-10-03T15:14:00"),
            epoch_ist("2022-10-04T10:00:00"),
        ],
    }
    result = analyse_intraday_range(body, "RELIANCE", "2022-10-03", "2022-10-04")
    assert result["status"] == "RANGE_COVERAGE_OR_OHLC_FAILED"
    assert result["missing_expiry_proxy_sessions"] == 1



def test_request_intraday_range_sends_a_90_day_window_and_returns_no_prices(monkeypatch):
    import scripts.constituent_weekly.dhan_equity_preflight as probe

    captured = {}

    class Response:
        ok = True
        status_code = 200

        @staticmethod
        def json():
            return {
                "open": [100.0, 100.5],
                "high": [101.0, 101.5],
                "low": [99.0, 99.5],
                "close": [100.5, 101.0],
                "volume": [100, 120],
                "timestamp": [epoch_ist("2022-10-03T10:00:00"), epoch_ist("2022-10-03T15:14:00")],
            }

    def fake_post(url, *, headers, json, timeout):
        captured.update(url=url, headers=headers, body=json, timeout=timeout)
        return Response()

    monkeypatch.setattr(probe.requests, "post", fake_post)
    result = probe.request_intraday_range(
        {"access-token": "secret"}, "RELIANCE", "1333", "2022-10-03", "2022-12-30"
    )
    assert result["status"] == "PASS"
    assert captured["body"]["fromDate"] == "2022-10-03 09:15:00"
    assert captured["body"]["toDate"] == "2022-12-30 15:15:00"
    assert "close" not in result
    assert "secret" not in str(result)


def test_profile_request_uses_documented_access_token_header_only(monkeypatch):
    import scripts.constituent_weekly.dhan_equity_preflight as probe

    captured = {}

    class Response:
        status_code = 200
        ok = True

    def fake_get(url, *, headers, timeout):
        captured.update(url=url, headers=headers, timeout=timeout)
        return Response()

    monkeypatch.setattr(probe.requests, "get", fake_get)
    response = probe.request_profile("fake-jwt-token")

    assert response.status_code == 200
    assert captured["url"] == probe.PROFILE_URL
    assert captured["headers"] == {
        "access-token": "fake-jwt-token",
        "Accept": "application/json",
    }
    assert "client-id" not in captured["headers"]



def test_auth_diagnostics_classify_totp_failure_without_retaining_message():
    from scripts.constituent_weekly.dhan_equity_preflight import auth_response_diagnostics

    result = auth_response_diagnostics({
        "status": "error",
        "message": "Invalid TOTP code; do not persist this text",
    })
    assert result["provider_error_category"] == "TOTP_REJECTED_OR_INVALID"
    assert "Invalid TOTP" not in str(result)
    assert "do not persist this text" not in str(result)


def test_membership_symbol_sets_respects_effective_dates_and_dummy_exclusion():
    current, historical = membership_symbol_sets("2026-10-31")
    assert len(current) == 50
    assert "BSE" in current
    assert "WIPRO" not in current
    assert "DUMMYTATAM" not in current
    assert "WIPRO" in historical
    assert "TATAMOTORS" in historical
    assert "TMPV" in historical


def test_resolve_ids_accepts_full_membership_symbol_list():
    master = pd.DataFrame({
        "SEM_SMST_SECURITY_ID": ["101", "102", "103"],
        "SEM_TRADING_SYMBOL": ["RELIANCE", "BSE", "WIPRO"],
        "SEM_EXM_EXCH_ID": ["NSE", "NSE", "NSE"],
        "SEM_SEGMENT": ["E", "E", "E"],
        "SEM_SERIES": ["EQ", "EQ", "EQ"],
        "SEM_INSTRUMENT_NAME": ["EQUITY", "EQUITY", "EQUITY"],
    })
    assert resolve_ids(master, ["RELIANCE", "BSE", "WIPRO"]) == {
        "RELIANCE": "101", "BSE": "102", "WIPRO": "103"
    }
