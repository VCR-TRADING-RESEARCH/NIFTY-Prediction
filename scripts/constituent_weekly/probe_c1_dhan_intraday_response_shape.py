from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from live_api.app import MASTER_URL, find_nifty50_security
from scripts.constituent_weekly.audit_c1_continuous_dhan_coverage import inspect_target_dates
from scripts.constituent_weekly.dhan_equity_preflight import (
    DAILY_URL,
    INTRADAY_URL,
    acquire_access_token,
    resolve_ids,
)

OUTPUT = ROOT / "research" / "constituent_weekly" / "C1_DHAN_INTRADAY_RESPONSE_DIAGNOSTIC.json"
TIMEOUT_SECONDS = 90
DELAY_SECONDS = 0.25

CASES = [
    {
        "name": "stock_pre_failure_window",
        "kind": "stock",
        "symbol": "RELIANCE",
        "from": "2022-11-07",
        "to": "2023-02-04",
        "target_date": "2023-02-02",
    },
    {
        "name": "stock_partial_boundary_window",
        "kind": "stock",
        "symbol": "RELIANCE",
        "from": "2023-02-05",
        "to": "2023-05-05",
        "target_date": "2023-05-04",
    },
    {
        "name": "stock_post_boundary_full_window",
        "kind": "stock",
        "symbol": "RELIANCE",
        "from": "2023-05-06",
        "to": "2023-08-03",
        "target_date": "2023-05-11",
    },
    {
        "name": "stock_post_boundary_short_window",
        "kind": "stock",
        "symbol": "RELIANCE",
        "from": "2023-05-06",
        "to": "2023-06-04",
        "target_date": "2023-05-11",
    },
    {
        "name": "index_post_boundary_full_window",
        "kind": "index",
        "symbol": "NIFTY 50",
        "from": "2023-05-06",
        "to": "2023-08-03",
        "target_date": "2023-05-11",
    },
    {
        "name": "index_failing_window_date_2024",
        "kind": "index",
        "symbol": "NIFTY 50",
        "from": "2024-01-31",
        "to": "2024-04-29",
        "target_date": "2024-02-01",
    },
    {
        "name": "index_exact_first_c1_failed_window",
        "kind": "index",
        "symbol": "NIFTY 50",
        "from": "2022-05-07",
        "to": "2022-08-04",
        "target_date": "2022-05-12",
    },
    {
        "name": "stock_exact_first_c1_failed_window",
        "kind": "stock",
        "symbol": "RELIANCE",
        "from": "2022-05-07",
        "to": "2022-08-04",
        "target_date": "2022-05-12",
    },
    {
        "name": "stock_adani_exact_first_c1_failed_window",
        "kind": "stock",
        "symbol": "ADANIENT",
        "from": "2022-05-07",
        "to": "2022-08-04",
        "target_date": "2022-05-12",
    },
    {
        "name": "index_exact_c1_failed_window_2023",
        "kind": "index",
        "symbol": "NIFTY 50",
        "from": "2023-05-02",
        "to": "2023-07-30",
        "target_date": "2023-05-04",
    },
    {
        "name": "stock_exact_c1_failed_window_2023",
        "kind": "stock",
        "symbol": "RELIANCE",
        "from": "2023-05-02",
        "to": "2023-07-30",
        "target_date": "2023-05-04",
    },
    {
        "name": "index_exact_c1_failed_window_2024",
        "kind": "index",
        "symbol": "NIFTY 50",
        "from": "2024-01-27",
        "to": "2024-04-25",
        "target_date": "2024-02-01",
    },
    {
        "name": "stock_exact_c1_failed_window_2024",
        "kind": "stock",
        "symbol": "RELIANCE",
        "from": "2024-01-27",
        "to": "2024-04-25",
        "target_date": "2024-02-01",
    },
    {
        "name": "legacy_hdfc_daily_history_full",
        "kind": "daily_stock",
        "symbol": "HDFC",
        "from": "2018-04-01",
        "to": "2023-07-13",
    },
    {
        "name": "legacy_hdfc_daily_history_recent",
        "kind": "daily_stock",
        "symbol": "HDFC",
        "from": "2022-10-01",
        "to": "2023-07-13",
    },
    {
        "name": "legacy_hdfc_daily_history_single_date",
        "kind": "daily_stock",
        "symbol": "HDFC",
        "from": "2023-06-30",
        "to": "2023-07-01",
    },
    {
        "name": "active_hdfcbank_daily_control",
        "kind": "daily_stock",
        "symbol": "HDFCBANK",
        "from": "2022-10-01",
        "to": "2023-07-13",
    },
]


def classify_provider_text(value: Any) -> str:
    """Classify an error message without retaining the provider text."""
    if not isinstance(value, str) or not value.strip():
        return "NO_PROVIDER_MESSAGE"
    text = value.casefold()
    patterns = [
        ("RATE_LIMIT", ("rate limit", "too many request", "throttl", "429")),
        ("ENTITLEMENT_OR_PLAN", ("plan", "subscription", "entitlement", "not allowed", "permission")),
        ("AUTHENTICATION", ("unauthor", "invalid token", "expired token", "access denied")),
        ("INVALID_INSTRUMENT", ("invalid security", "invalid instrument", "security id", "not found")),
        ("DATE_RANGE_OR_HISTORY", ("date range", "historical data", "past data", "from date", "to date", "invalid date")),
        ("INVALID_PARAMETERS", ("invalid parameter", "incorrect parameter", "bad request", "validation error")),
        ("INACTIVE_OR_DELISTED_SECURITY", ("inactive instrument", "delisted", "merged", "not active", "instrument inactive")),
        ("NO_DATA", ("no data", "no record", "not available", "empty")),
    ]
    for category, matches in patterns:
        if any(match in text for match in matches):
            return category
    return "UNCLASSIFIED_PROVIDER_MESSAGE"


def response_shape(
    response: requests.Response,
    target_date: str | None = None,
    require_volume: bool = True,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "http_status": int(response.status_code),
        "http_ok": bool(response.ok),
        "content_type": response.headers.get("Content-Type", "").split(";")[0][:80],
        "content_length_bytes": len(response.content),
    }
    try:
        body = response.json()
    except ValueError:
        result["json_status"] = "INVALID_JSON"
        result["body_prefix_class"] = (
            "HTML" if response.text.lstrip().startswith("<") else "NON_JSON_TEXT"
        )
        return result

    if not isinstance(body, dict):
        result["json_status"] = "NON_OBJECT_JSON"
        result["body_type"] = type(body).__name__
        return result

    result["json_status"] = "OBJECT"
    result["top_level_keys"] = sorted(str(k) for k in body.keys())[:60]
    if "status" in body:
        result["provider_status_type"] = type(body["status"]).__name__
        if isinstance(body["status"], (str, int, float, bool)):
            result["provider_status_value"] = str(body["status"])[:40]

    remarks = body.get("remarks")
    nested_error = remarks if isinstance(remarks, dict) else {}
    message_fields = [
        nested_error.get("error_message"),
        nested_error.get("message"),
        body.get("message"),
        body.get("errorMessage"),
        body.get("error"),
        remarks if isinstance(remarks, str) else None,
    ]
    message_text = next((x for x in message_fields if isinstance(x, str) and x), None)
    error_code = body.get("errorCode") or nested_error.get("error_code") or nested_error.get("errorCode")
    error_type = body.get("errorType") or nested_error.get("error_type") or nested_error.get("errorType")
    result["remarks_type"] = type(remarks).__name__ if remarks is not None else "MISSING"
    result["provider_message_category"] = classify_provider_text(message_text)
    if error_code is not None:
        result["provider_error_code"] = str(error_code)[:40]
    if error_type is not None:
        result["provider_error_type"] = str(error_type)[:60]
    code = str(error_code or "").strip().upper()
    if code == "DH-905":
        result["provider_message_category"] = "DHAN_INPUT_EXCEPTION_DH905"
    elif code == "DH-907":
        result["provider_message_category"] = "DHAN_DATA_ERROR_DH907"

    payload = body.get("data") if isinstance(body.get("data"), dict) else body
    result["data_field_type"] = type(body["data"]).__name__ if "data" in body else "TOP_LEVEL_ARRAYS"
    result["payload_container"] = "data_object" if payload is not body else "top_level"
    result["payload_keys"] = sorted(str(k) for k in payload.keys())[:60]
    for key in ("open", "high", "low", "close", "volume", "timestamp", "start_Time", "startTime"):
        value = payload.get(key)
        result[f"{key}_type"] = type(value).__name__ if value is not None else "MISSING"
        if isinstance(value, list):
            result[f"{key}_length"] = len(value)
    for key in ("errorCode", "errorType"):
        if key in body:
            value = body.get(key)
            result[f"{key}_type"] = type(value).__name__
            if isinstance(value, (str, int, float, bool)):
                result[f"{key}_value"] = str(value)[:60]
    if target_date:
        parsed = inspect_target_dates(body, [target_date], require_volume=require_volume)
        date_result = parsed.get("dates", {}).get(target_date, {})
        result["parser_response_status"] = parsed.get("status")
        result["target_date_checked"] = target_date
        result["target_date_status"] = date_result.get("status")
        result["target_anchor_ok"] = date_result.get("anchor_ok")
        result["target_expiry_ok"] = date_result.get("expiry_ok")
        result["target_anchor_time_ist"] = date_result.get("anchor_time_ist")
        result["target_expiry_time_ist"] = date_result.get("expiry_time_ist")
    return result


def post_probe(
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any],
    case: dict[str, Any],
) -> dict[str, Any]:
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT_SECONDS)
        shape = response_shape(
            response,
            case.get("target_date"),
            require_volume=case.get("kind") != "index",
        )
    except requests.RequestException as exc:
        shape = {
            "http_status": None,
            "http_ok": False,
            "network_error_type": type(exc).__name__,
        }
    return {
        "case": case["name"],
        "instrument_kind": case["kind"],
        "symbol": case["symbol"],
        "from_date": case["from"],
        "to_date": case["to"],
        **shape,
    }


def main() -> int:
    started = time.monotonic()
    stage = "token_acquisition"
    report: dict[str, Any] = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "IN_PROGRESS",
        "credentials_or_tokens_recorded": False,
        "security_ids_recorded": False,
        "market_values_recorded": False,
        "cases": [],
    }
    try:
        token, client_id, auth_method, refresh_status, diagnostics = acquire_access_token()
        stage = "profile_entitlement"
        profile = requests.get(
            "https://api.dhan.co/v2/profile",
            headers={"access-token": token, "Accept": "application/json"},
            timeout=30,
        )
        report["profile_http_status"] = int(profile.status_code)
        if not profile.ok:
            raise RuntimeError(f"Dhan profile request failed with HTTP {profile.status_code}.")
        profile_body = profile.json()
        report["data_plan_active"] = str(profile_body.get("dataPlan", "")).strip().casefold() == "active"
        if not report["data_plan_active"]:
            raise RuntimeError("Dhan Data API plan is not active.")

        stage = "scrip_master_download"
        master_response = requests.get(MASTER_URL, timeout=45)
        report["scrip_master_http_status"] = int(master_response.status_code)
        master_response.raise_for_status()
        master = pd.read_csv(pd.io.common.BytesIO(master_response.content), low_memory=False)
        burst_symbols = ["ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK", "BAJAJ-AUTO", "BAJAJFINSV", "BAJFINANCE", "BEL", "BHARTIARTL", "BPCL", "BRITANNIA", "CIPLA", "COALINDIA", "DIVISLAB", "DRREDDY"]
        stock_ids = resolve_ids(master, ["RELIANCE", "HDFCBANK", *burst_symbols])
        index_id = find_nifty50_security(master)
        report["reliance_symbol_resolved"] = "RELIANCE" in stock_ids
        report["nifty50_index_resolved"] = bool(index_id)
        report["hdfcbank_symbol_resolved"] = "HDFCBANK" in stock_ids
        report["burst_symbol_resolution_count"] = len(set(burst_symbols) & set(stock_ids))
        if "RELIANCE" not in stock_ids:
            raise RuntimeError("RELIANCE security lookup missing from current scrip master.")
        if "HDFCBANK" not in stock_ids:
            raise RuntimeError("HDFCBANK control security lookup missing from current scrip master.")
        if not index_id:
            raise RuntimeError("NIFTY 50 index security lookup missing from current scrip master.")

        headers = {
            "access-token": token,
            "client-id": client_id,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        report["auth_method"] = auth_method
        report["token_refresh_status"] = refresh_status
        report["token_refresh_diagnostic_keys"] = sorted(diagnostics.keys()) if isinstance(diagnostics, dict) else []
        burst_cases = [
            {
                "name": f"stock_post_boundary_burst_{index:02d}",
                "kind": "stock",
                "symbol": symbol,
                "from": "2023-05-06",
                "to": "2023-08-03",
                "target_date": "2023-05-11",
            }
            for index, symbol in enumerate(burst_symbols, start=1)
        ]
        all_cases = CASES + burst_cases

        for case in all_cases:
            stage = f"market_data_request:{case['name']}"
            if case["kind"] == "daily_stock":
                url = DAILY_URL
                security_id = "1330" if case["symbol"] == "HDFC" else stock_ids[case["symbol"]]
                payload = {
                    "securityId": security_id,
                    "exchangeSegment": "NSE_EQ",
                    "instrument": "EQUITY",
                    "expiryCode": 0,
                    "oi": False,
                    "fromDate": case["from"],
                    "toDate": case["to"],
                }
            else:
                url = INTRADAY_URL
                security_id = index_id if case["kind"] == "index" else stock_ids[case["symbol"]]
                payload = {
                    "securityId": str(security_id),
                    "exchangeSegment": "IDX_I" if case["kind"] == "index" else "NSE_EQ",
                    "instrument": "INDEX" if case["kind"] == "index" else "EQUITY",
                    "interval": "1",
                    "oi": False,
                    "fromDate": f"{case['from']} 09:15:00",
                    "toDate": f"{case['to']} 15:15:00",
                }
            report["cases"].append(post_probe(url, headers, payload, case))
            result = report["cases"][-1]
            print(
                "C1_DHAN_RESPONSE_CASE",
                case["name"],
                result.get("http_status"),
                result.get("data_field_type"),
                result.get("provider_message_category"),
            )
            time.sleep(DELAY_SECONDS)

        report["status"] = "COMPLETED"
        report["elapsed_seconds"] = round(time.monotonic() - started, 2)
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return 0
    except Exception as exc:
        report["status"] = "BLOCKED_OR_FAILED"
        report["fatal_error_type"] = type(exc).__name__
        report["fatal_error_stage"] = stage
        message = str(exc).casefold()
        if "data api plan is not active" in message:
            report["fatal_error_category"] = "DATA_PLAN_NOT_ACTIVE"
        elif "profile request failed with http" in message:
            report["fatal_error_category"] = "PROFILE_HTTP_ERROR"
        elif "security lookup missing" in message:
            report["fatal_error_category"] = "SCRIP_MASTER_ID_LOOKUP_FAILED"
        elif "http" in message and "master" in stage:
            report["fatal_error_category"] = "SCRIP_MASTER_HTTP_ERROR"
        else:
            report["fatal_error_category"] = type(exc).__name__.upper()
        report["elapsed_seconds"] = round(time.monotonic() - started, 2)
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("C1_DHAN_RESPONSE_DIAGNOSTIC_FAILED", type(exc).__name__)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
