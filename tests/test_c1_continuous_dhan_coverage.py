from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

from scripts.constituent_weekly.audit_c1_continuous_dhan_coverage import (
    active_members_for_date,
    build_expiry_cycles,
    evaluate_cycle_coverage,
    inspect_target_dates,
    is_stock_coverage_acceptable,
    make_chunks,
    verified_expiry_dates,
)


def epoch_ist(value: str) -> int:
    return int(datetime.fromisoformat(value).replace(tzinfo=ZoneInfo("Asia/Kolkata")).timestamp())


def test_expiry_parser_accepts_verified_shifted_contracts_only_when_present():
    frame = pd.DataFrame({
        "verified_expiry_trade_date": ["2021-11-03", "2025-10-14", "2025-10-20", "2025-10-28", "2025-11-04"],
        "status": ["verified_shifted_nifty_weekly_expiry", "verified_nifty_weekly_expiry", "verified_shifted_nifty_weekly_expiry", "candidate", "verified_nifty_weekly_expiry"],
        "contract_expiry_present": [True, True, True, True, False],
    })
    assert verified_expiry_dates(frame) == ["2021-11-03", "2025-10-14", "2025-10-20"]


def test_shifted_holiday_expiry_splits_adjacent_weekly_cycles():
    membership = pd.DataFrame({
        "symbol": ["AAA", "BBB"], "valid_from": ["2020-01-01", "2020-01-01"],
        "valid_to": ["", ""], "member_type": ["equity_security", "equity_security"],
        "market_data_required": ["TRUE", "TRUE"],
    })
    cycles = build_expiry_cycles(
        ["2025-10-14", "2025-10-20", "2025-10-28"],
        ["2025-10-14", "2025-10-15", "2025-10-16", "2025-10-17", "2025-10-20", "2025-10-21", "2025-10-23", "2025-10-24", "2025-10-27", "2025-10-28"],
        membership, "2025-10-01", "2025-10-28", {"2025-10-21"},
    )
    assert [(c["anchor_date"], c["expiry_date"]) for c in cycles] == [
        ("2025-10-15", "2025-10-20"), ("2025-10-23", "2025-10-28"),
    ]


def test_membership_uses_point_in_time_tradable_equity_only():
    frame = pd.DataFrame({
        "symbol": ["AAA", "BBB", "DUMMY", "OLD"],
        "valid_from": ["2020-01-01"] * 4,
        "valid_to": ["", "", "", "2021-01-01"],
        "member_type": ["equity_security"] * 4,
        "market_data_required": ["TRUE", "TRUE", "FALSE", "TRUE"],
    })
    assert active_members_for_date(frame, "2022-01-01") == ["AAA", "BBB"]


def test_cycle_uses_first_regular_session_after_previous_verified_expiry():
    membership = pd.DataFrame({
        "symbol": ["AAA", "BBB"],
        "valid_from": ["2020-01-01", "2020-01-01"],
        "valid_to": ["", ""],
        "member_type": ["equity_security", "equity_security"],
        "market_data_required": ["TRUE", "TRUE"],
    })
    cycles = build_expiry_cycles(
        ["2021-11-03", "2021-11-11", "2021-11-18"],
        ["2021-11-04", "2021-11-05", "2021-11-12", "2021-11-15"],
        membership,
        "2021-11-01",
        "2021-11-18",
        {"2021-11-04"},
    )
    assert len(cycles) == 2
    assert cycles[0]["previous_expiry"] == "2021-11-03"
    assert cycles[0]["anchor_date"] == "2021-11-05"
    assert cycles[0]["expiry_date"] == "2021-11-11"
    assert cycles[0]["members"] == ["AAA", "BBB"]


def test_dhan_chunks_are_non_overlapping_and_max_90_days():
    chunks = make_chunks("2021-11-01", "2022-04-29", 90)
    assert chunks == [
        {"from": "2021-11-01", "to": "2022-01-29"},
        {"from": "2022-01-30", "to": "2022-04-29"},
    ]
    for chunk in chunks:
        start = datetime.fromisoformat(chunk["from"])
        end = datetime.fromisoformat(chunk["to"])
        assert (end - start).days + 1 <= 90


def test_stock_coverage_requires_47_and_at_least_94_percent():
    assert is_stock_coverage_acceptable(47, 50)
    assert not is_stock_coverage_acceptable(46, 50)
    assert not is_stock_coverage_acceptable(47, 51)
    assert is_stock_coverage_acceptable(48, 51)
    assert not is_stock_coverage_acceptable(0, 0)


def test_target_windows_select_1514_as_expiry_proxy_not_1515():
    body = {
        "open": [100.0, 101.0, 102.0],
        "high": [101.0, 102.0, 103.0],
        "low": [99.0, 100.0, 101.0],
        "close": [100.5, 101.5, 102.5],
        "volume": [1000, 1200, 900],
        "timestamp": [
            epoch_ist("2026-10-27T10:00:00"),
            epoch_ist("2026-10-27T15:14:00"),
            epoch_ist("2026-10-27T15:15:00"),
        ],
    }
    result = inspect_target_dates(body, ["2026-10-27"], require_volume=True)
    day = result["dates"]["2026-10-27"]
    assert result["status"] == "PASS_RESPONSE"
    assert day["anchor_ok"] is True
    assert day["expiry_ok"] is True
    assert day["anchor_time_ist"] == "10:00"
    assert day["expiry_time_ist"] == "15:14"


def test_index_target_does_not_require_traded_volume():
    body = {
        "open": [100.0, 101.0],
        "high": [101.0, 102.0],
        "low": [99.0, 100.0],
        "close": [100.5, 101.5],
        "timestamp": [
            epoch_ist("2026-10-27T10:00:00"),
            epoch_ist("2026-10-27T15:14:00"),
        ],
    }
    result = inspect_target_dates(body, ["2026-10-27"], require_volume=False)
    assert result["dates"]["2026-10-27"]["anchor_ok"] is True
    assert result["dates"]["2026-10-27"]["expiry_ok"] is True


def test_duplicate_target_candles_fail_the_ohlc_quality_gate():
    body = {
        "open": [100.0, 100.0, 101.0],
        "high": [101.0, 101.0, 102.0],
        "low": [99.0, 99.0, 100.0],
        "close": [100.5, 100.5, 101.5],
        "volume": [1000, 1000, 1200],
        "timestamp": [
            epoch_ist("2026-10-27T10:00:00"),
            epoch_ist("2026-10-27T10:00:00"),
            epoch_ist("2026-10-27T15:14:00"),
        ],
    }
    result = inspect_target_dates(body, ["2026-10-27"], require_volume=True)
    day = result["dates"]["2026-10-27"]
    assert day["anchor_ok"] is False
    assert day["expiry_ok"] is True
    assert day["duplicate_anchor_timestamps"] == 1


def test_confirmatory_history_counts_only_prior_accepted_cycles():
    good = {
        "index_target_ok": True,
        "stock_coverage_ok": True,
        "cycle_accepted_for_coverage": True,
    }
    invalid = {
        "index_target_ok": False,
        "stock_coverage_ok": True,
        "cycle_accepted_for_coverage": False,
    }
    exactly_104 = evaluate_cycle_coverage([good.copy() for _ in range(104)])
    assert exactly_104["confirmatory_cycles_after_104_prior_cycles"] == 0
    assert exactly_104["target_coverage_gate"] == "FAIL"

    cycles_105 = evaluate_cycle_coverage([good.copy() for _ in range(105)])
    assert cycles_105["confirmatory_cycles_after_104_prior_cycles"] == 1
    assert cycles_105["target_coverage_gate"] == "PASS"

    with_one_missing_index = evaluate_cycle_coverage(
        [good.copy() for _ in range(105)] + [invalid.copy()]
    )
    assert with_one_missing_index["index_target_valid_fraction"] >= 0.98
    assert with_one_missing_index["target_coverage_gate"] == "PASS"

    with_two_missing_index = evaluate_cycle_coverage(
        [good.copy() for _ in range(103)] + [invalid.copy(), invalid.copy()]
    )
    assert with_two_missing_index["target_coverage_gate"] == "FAIL"


def test_partial_target_date_response_is_not_marked_cache_complete():
    body = {
        "open": [100.0],
        "high": [101.0],
        "low": [99.0],
        "close": [100.5],
        "volume": [1000],
        "timestamp": [epoch_ist("2026-10-27T15:14:00")],
    }
    result = inspect_target_dates(body, ["2026-10-27"], require_volume=True)
    assert result["status"] == "PARTIAL_TARGET_DATES"
    assert result["dates"]["2026-10-27"]["anchor_ok"] is False
    assert result["dates"]["2026-10-27"]["expiry_ok"] is True


def test_known_action_crossing_cycle_has_audit_dates():
    from scripts.constituent_weekly.audit_c1_continuous_dhan_coverage import KNOWN_CORPORATE_ACTION_DATES
    assert KNOWN_CORPORATE_ACTION_DATES == {
        "HDFC": "2023-07-01",
        "TATAMOTORS": "2025-10-14",
    }


def test_request_intraday_window_retries_malformed_success_shape(monkeypatch):
    import scripts.constituent_weekly.audit_c1_continuous_dhan_coverage as audit

    calls = {"count": 0}

    class Response:
        status_code = 200
        ok = True
        headers = {}

        def __init__(self, body):
            self.body = body

        def json(self):
            return self.body

    good = {
        "open": [100.0, 101.0],
        "high": [101.0, 102.0],
        "low": [99.0, 100.0],
        "close": [100.5, 101.5],
        "volume": [1000, 1100],
        "timestamp": [epoch_ist("2023-05-11T10:00:00"), epoch_ist("2023-05-11T15:14:00")],
    }

    def fake_post(*args, **kwargs):
        calls["count"] += 1
        return Response({"status": "failure"} if calls["count"] == 1 else good)

    monkeypatch.setattr(audit.requests, "post", fake_post)
    monkeypatch.setattr(audit.time, "sleep", lambda *_: None)
    body, attempts = audit.request_intraday_window(
        "123", "NSE_EQ", "EQUITY", "token", "client",
        "2023-05-06", "2023-08-03",
    )
    assert attempts == 2
    assert calls["count"] == 2
    assert body == good


def test_request_intraday_window_returns_sanitizable_schema_after_three_malformed_shapes(monkeypatch):
    import scripts.constituent_weekly.audit_c1_continuous_dhan_coverage as audit

    class Response:
        status_code = 200
        ok = True
        headers = {}

        def json(self):
            return {"status": "failure", "remarks": "private provider text"}

    monkeypatch.setattr(audit.requests, "post", lambda *_args, **_kwargs: Response())
    monkeypatch.setattr(audit.time, "sleep", lambda *_: None)
    body, attempts = audit.request_intraday_window(
        "123", "NSE_EQ", "EQUITY", "token", "client",
        "2023-05-06", "2023-08-03",
    )
    inspected = audit.inspect_target_dates(body, ["2023-05-11"], require_volume=True)
    assert attempts == 3
    assert inspected["status"] == "INVALID_RESPONSE"
    assert inspected["response_schema"]["response_top_level_keys"] == ["remarks", "status"]
    assert "private provider text" not in str(inspected)



def test_provider_error_fields_are_whitelisted_and_message_text_is_not_retained():
    import scripts.constituent_weekly.audit_c1_continuous_dhan_coverage as audit

    body = {
        "errorCode": "DH-905",
        "errorType": "Input_Exception",
        "errorMessage": "private provider text with account-specific detail",
    }
    fields = audit.sanitized_provider_error_fields(body)
    assert fields == {
        "provider_error_code": "DH-905",
        "provider_error_type": "Input_Exception",
        "provider_message_category": "DHAN_INPUT_EXCEPTION_DH905",
    }
    assert "private provider text" not in str(fields)
    assert "account-specific detail" not in str(fields)


def test_provider_error_fields_support_nested_remarks_shape():
    import scripts.constituent_weekly.audit_c1_continuous_dhan_coverage as audit

    fields = audit.sanitized_provider_error_fields({
        "status": "failure",
        "remarks": {
            "error_code": "805",
            "error_type": "Data_Error",
            "error_message": "too many requests; private text",
        },
    })
    assert fields == {
        "provider_error_code": "805",
        "provider_error_type": "Data_Error",
        "provider_message_category": "DHAN_DATA_TOO_MANY_REQUESTS_805",
    }
    assert "private text" not in str(fields)


def test_http_400_dh905_is_recorded_without_retry_or_message_text(monkeypatch):
    import scripts.constituent_weekly.audit_c1_continuous_dhan_coverage as audit

    class Response:
        status_code = 400
        ok = False
        headers = {}

        def json(self):
            return {
                "errorCode": "DH-905",
                "errorType": "Input_Exception",
                "errorMessage": "private provider message",
            }

    calls = {"count": 0}
    def fake_post(*_args, **_kwargs):
        calls["count"] += 1
        return Response()

    monkeypatch.setattr(audit.requests, "post", fake_post)
    monkeypatch.setattr(audit.time, "sleep", lambda *_: None)
    body, attempts = audit.request_intraday_window(
        "123", "IDX_I", "INDEX", "token", "client", "2023-05-06", "2023-08-03"
    )
    assert attempts == calls["count"] == 1
    assert body["status"] == "HTTP_400"
    assert body["provider_error_code"] == "DH-905"
    assert body["provider_message_category"] == "DHAN_INPUT_EXCEPTION_DH905"
    assert "private provider message" not in str(body)


def test_http_400_dh904_uses_bounded_backoff_then_recovers(monkeypatch):
    import scripts.constituent_weekly.audit_c1_continuous_dhan_coverage as audit

    class Response:
        ok = True
        headers = {}

        def __init__(self, status_code, body):
            self.status_code = status_code
            self.body = body
            self.ok = status_code == 200

        def json(self):
            return self.body

    success = {
        "open": [100.0, 101.0],
        "high": [101.0, 102.0],
        "low": [99.0, 100.0],
        "close": [100.5, 101.5],
        "timestamp": [epoch_ist("2023-05-11T10:00:00"), epoch_ist("2023-05-11T15:14:00")],
    }
    responses = [
        Response(400, {
            "errorCode": "DH-904",
            "errorType": "Data_Error",
            "errorMessage": "too many requests; private detail",
        }),
        Response(200, success),
    ]
    calls = {"count": 0}
    waits = []

    def fake_post(*_args, **_kwargs):
        response = responses[calls["count"]]
        calls["count"] += 1
        return response

    monkeypatch.setattr(audit.requests, "post", fake_post)
    monkeypatch.setattr(audit.time, "sleep", lambda seconds: waits.append(seconds))
    body, attempts = audit.request_intraday_window(
        "123", "IDX_I", "INDEX", "token", "client", "2023-05-06", "2023-08-03"
    )
    assert attempts == calls["count"] == 2
    assert waits == [2.0]
    assert body == success


def test_inspect_target_dates_exposes_only_sanitized_provider_error_metadata():
    body = {
        "errorCode": "DH-905",
        "errorType": "Input_Exception",
        "errorMessage": "do not publish this provider detail",
    }
    inspected = inspect_target_dates(body, ["2023-05-11"], require_volume=False)
    schema = inspected["response_schema"]
    assert schema["provider_error_code"] == "DH-905"
    assert schema["provider_error_type"] == "Input_Exception"
    assert schema["provider_message_category"] == "DHAN_INPUT_EXCEPTION_DH905"
    assert "do not publish this provider detail" not in str(inspected)
