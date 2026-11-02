from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import requests

from live_api.app import MASTER_URL, find_nifty50_security
from scripts.constituent_weekly.dhan_equity_preflight import (
    INTRADAY_URL,
    IST,
    MEMBERSHIP_CSV,
    acquire_access_token,
    apply_historical_security_aliases,
    request_profile,
    resolve_ids,
)

EXPIRY_CSV = ROOT / "data" / "reconciliation" / "expiry_verification.csv"
INDEX_DAILY_CSV = ROOT / "data" / "reconciliation" / "nifty50_official_daily.csv"
OUTPUT = ROOT / "research" / "constituent_weekly" / "C1_CONTINUOUS_COVERAGE.json"
CHUNK_DAYS = 90
REQUEST_DELAY_SECONDS = 0.5
REQUEST_TIMEOUT_SECONDS = 120
MIN_VALID_MEMBERS = 47
MIN_MEMBER_FRACTION = 0.94
MIN_INDEX_TARGET_FRACTION = 0.98
MIN_CONFIRMATORY_HISTORY = 104
METHODOLOGY_VERSION = "bup01-c1-dhan-target-coverage-v1"
KNOWN_CORPORATE_ACTION_DATES = {"HDFC": "2023-07-01", "TATAMOTORS": "2025-10-14"}
SPECIAL_EVENING_ONLY_SESSIONS = {
    "2021-11-04",
    "2022-10-24",
    "2024-11-01",
    "2025-10-21",
}
LOCAL_TZ = ZoneInfo(IST)


class FatalAccessError(RuntimeError):
    pass


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def parse_date(value: str) -> date:
    return date.fromisoformat(str(value)[:10])


def active_members_for_date(membership: pd.DataFrame, as_of: str) -> list[str]:
    """Return only active, tradable equity constituents; valid_to is exclusive."""
    required = {"symbol", "valid_from", "valid_to", "member_type", "market_data_required"}
    missing = required - set(membership.columns)
    if missing:
        raise ValueError("Membership ledger is missing required columns.")
    cutoff = pd.Timestamp(as_of)
    symbols = membership["symbol"].astype("string").str.strip()
    starts = pd.to_datetime(membership["valid_from"], errors="coerce")
    ends = pd.to_datetime(membership["valid_to"], errors="coerce")
    mask = (
        membership["member_type"].astype(str).str.strip().str.casefold().eq("equity_security")
        & membership["market_data_required"].astype(str).str.strip().str.upper().isin(("TRUE", "1", "YES"))
        & symbols.notna()
        & symbols.ne("")
        & starts.notna()
        & starts.le(cutoff)
        & (ends.isna() | ends.gt(cutoff))
    )
    return sorted(set(symbols[mask].astype(str)))


def verified_expiry_dates(expiry_frame: pd.DataFrame) -> list[str]:
    required = {"verified_expiry_trade_date", "status", "contract_expiry_present"}
    missing = required - set(expiry_frame.columns)
    if missing:
        raise ValueError("Expiry verification file is missing required columns.")
    present = expiry_frame["contract_expiry_present"].astype(str).str.strip().str.casefold().isin(
        ("true", "1", "yes")
    )
    verified_statuses = {"verified_nifty_weekly_expiry", "verified_shifted_nifty_weekly_expiry"}
    valid = expiry_frame["status"].astype(str).str.strip().isin(verified_statuses) & present
    values = pd.to_datetime(expiry_frame.loc[valid, "verified_expiry_trade_date"], errors="coerce")
    return sorted({stamp.date().isoformat() for stamp in values.dropna()})


def build_expiry_cycles(
    expiry_dates: list[str],
    session_dates: list[str],
    membership: pd.DataFrame,
    start_date: str,
    end_date: str,
    special_sessions: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Pair each expiry with the first regular session after the preceding expiry."""
    specials = special_sessions or set()
    sessions = sorted(d for d in set(session_dates) if d not in specials)
    expiry = sorted(set(expiry_dates))
    cycles: list[dict[str, Any]] = []
    for index in range(1, len(expiry)):
        previous_expiry = expiry[index - 1]
        expiry_date = expiry[index]
        if expiry_date < start_date or expiry_date > end_date:
            continue
        anchors = [session for session in sessions if session > previous_expiry]
        if not anchors:
            continue
        anchor_date = anchors[0]
        if anchor_date < start_date or anchor_date >= expiry_date:
            continue
        members = active_members_for_date(membership, anchor_date)
        cycles.append({
            "previous_expiry": previous_expiry,
            "anchor_date": anchor_date,
            "expiry_date": expiry_date,
            "members": members,
        })
    return cycles


def is_stock_coverage_acceptable(valid_count: int, member_count: int) -> bool:
    fraction = valid_count / member_count if member_count > 0 else 0.0
    return valid_count >= MIN_VALID_MEMBERS and fraction >= MIN_MEMBER_FRACTION


def evaluate_cycle_coverage(cycle_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate the registered thresholds using only previously accepted expiry cycles."""
    total = len(cycle_results)
    index_valid = sum(bool(item.get("index_target_ok")) for item in cycle_results)
    stock_covered = sum(bool(item.get("stock_coverage_ok")) for item in cycle_results)
    accepted = sum(bool(item.get("cycle_accepted_for_coverage")) for item in cycle_results)
    index_fraction = index_valid / total if total else 0.0
    accepted_before = 0
    confirmatory_after_104 = 0
    for item in cycle_results:
        if item.get("cycle_accepted_for_coverage"):
            if accepted_before >= MIN_CONFIRMATORY_HISTORY:
                confirmatory_after_104 += 1
            accepted_before += 1
    passed = bool(
        total >= MIN_CONFIRMATORY_HISTORY + 1
        and index_fraction >= MIN_INDEX_TARGET_FRACTION
        and accepted >= MIN_CONFIRMATORY_HISTORY + 1
        and confirmatory_after_104 > 0
    )
    return {
        "scheduled_cycles": total,
        "index_target_valid_cycles": index_valid,
        "index_target_valid_fraction": round(index_fraction, 6),
        "cycles_meeting_47_and_94_percent_stock_gate": stock_covered,
        "cycles_accepted_for_coverage": accepted,
        "confirmatory_cycles_after_104_prior_cycles": confirmatory_after_104,
        "target_coverage_gate": "PASS" if passed else "FAIL",
    }


def make_chunks(start_date: str, end_date: str, days: int = CHUNK_DAYS) -> list[dict[str, str]]:
    """Create non-overlapping, inclusive date chunks, never longer than 90 days."""
    if days < 1 or days > 90:
        raise ValueError("Dhan intraday windows must be from 1 to 90 calendar days.")
    start = parse_date(start_date)
    stop = parse_date(end_date)
    chunks = []
    cursor = start
    while cursor <= stop:
        chunk_end = min(cursor + timedelta(days=days - 1), stop)
        chunks.append({"from": cursor.isoformat(), "to": chunk_end.isoformat()})
        cursor = chunk_end + timedelta(days=1)
    return chunks


def chunk_key(chunk: dict[str, str]) -> str:
    return f"{chunk['from']}|{chunk['to']}"


def _payload_arrays(body: Any) -> tuple[dict[str, Any] | None, str | None]:
    if not isinstance(body, dict):
        return None, "INVALID_JSON_SHAPE"
    if str(body.get("status", "")).casefold() == "failure":
        return None, "PROVIDER_FAILURE"
    payload = body.get("data") if isinstance(body.get("data"), dict) else body
    timestamps = payload.get("timestamp")
    if timestamps is None:
        timestamps = payload.get("start_Time")
    if timestamps is None:
        timestamps = payload.get("startTime")
    arrays = {
        "timestamp": timestamps,
        "open": payload.get("open"),
        "high": payload.get("high"),
        "low": payload.get("low"),
        "close": payload.get("close"),
        "volume": payload.get("volume"),
    }
    required = ("timestamp", "open", "high", "low", "close")
    if any(not isinstance(arrays[key], list) for key in required):
        return None, "MISSING_REQUIRED_ARRAY"
    lengths = [len(arrays[key]) for key in required]
    if len(set(lengths)) != 1:
        return None, "ARRAY_LENGTH_MISMATCH"
    if lengths[0] == 0:
        return arrays, "NO_BARS"
    if arrays["volume"] is not None and not isinstance(arrays["volume"], list):
        arrays["volume"] = None
    if isinstance(arrays["volume"], list) and len(arrays["volume"]) != lengths[0]:
        return None, "VOLUME_LENGTH_MISMATCH"
    return arrays, None


def _ohlc_rows_valid(frame: pd.DataFrame, require_volume: bool) -> bool:
    if frame.empty:
        return False
    cols = ["open", "high", "low", "close"]
    values = frame[cols].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values <= 0).any():
        return False
    low = frame["low"].to_numpy(dtype=float)
    high = frame["high"].to_numpy(dtype=float)
    open_ = frame["open"].to_numpy(dtype=float)
    close = frame["close"].to_numpy(dtype=float)
    if (low > np.minimum(open_, close)).any() or (high < np.maximum(open_, close)).any():
        return False
    if (high < low).any():
        return False
    if require_volume:
        if "volume" not in frame or frame["volume"].isna().any():
            return False
        volume = frame["volume"].to_numpy(dtype=float)
        if not np.isfinite(volume).all() or (volume < 0).any():
            return False
    return True


def inspect_target_dates(
    body: Any,
    target_dates: list[str],
    require_volume: bool,
) -> dict[str, Any]:
    """Keep only OHLC quality flags and the selected observation times, never values."""
    arrays, shape_error = _payload_arrays(body)
    results: dict[str, Any] = {}
    if arrays is None or shape_error in ("INVALID_JSON_SHAPE", "MISSING_REQUIRED_ARRAY", "ARRAY_LENGTH_MISMATCH", "VOLUME_LENGTH_MISMATCH"):
        for target_date in target_dates:
            results[target_date] = {
                "anchor_ok": False,
                "expiry_ok": False,
                "status": shape_error or "INVALID_RESPONSE",
            }
        schema = {}
        if isinstance(body, dict):
            payload = body.get("data") if isinstance(body.get("data"), dict) else body
            schema = {
                "response_top_level_keys": sorted(str(key) for key in body.keys())[:40],
                "response_data_type": type(body.get("data")).__name__ if "data" in body else "TOP_LEVEL_ARRAYS",
                "response_payload_keys": sorted(str(key) for key in payload.keys())[:40] if isinstance(payload, dict) else [],
                "response_array_types": {
                    key: type(payload.get(key)).__name__ if key in payload else "MISSING"
                    for key in ("timestamp", "open", "high", "low", "close", "volume")
                } if isinstance(payload, dict) else {},
                "provider_status_value": str(body.get("status"))[:32] if isinstance(body.get("status"), (str, int, float, bool)) else None,
            }
        return {"status": "INVALID_RESPONSE", "bar_count": 0, "dates": results, "response_schema": schema}

    count = len(arrays["timestamp"])
    if count == 0:
        for target_date in target_dates:
            results[target_date] = {
                "anchor_ok": False,
                "expiry_ok": False,
                "status": shape_error or "NO_BARS",
            }
        return {"status": "NO_BARS", "bar_count": 0, "dates": results}

    frame = pd.DataFrame({
        "timestamp": pd.to_datetime(arrays["timestamp"], unit="s", utc=True, errors="coerce"),
        "open": pd.to_numeric(arrays["open"], errors="coerce"),
        "high": pd.to_numeric(arrays["high"], errors="coerce"),
        "low": pd.to_numeric(arrays["low"], errors="coerce"),
        "close": pd.to_numeric(arrays["close"], errors="coerce"),
    })
    if isinstance(arrays["volume"], list):
        frame["volume"] = pd.to_numeric(arrays["volume"], errors="coerce")
    frame["timestamp"] = frame["timestamp"].dt.tz_convert(LOCAL_TZ)
    frame = frame.dropna(subset=["timestamp"]).sort_values("timestamp")
    frame["session_date"] = frame["timestamp"].dt.strftime("%Y-%m-%d")
    frame["clock"] = frame["timestamp"].dt.strftime("%H:%M")

    for target_date in target_dates:
        day = frame[frame["session_date"].eq(target_date)]
        anchor_rows = day[day["clock"].between("10:00", "10:03", inclusive="both")]
        expiry_rows = day[day["clock"].between("15:00", "15:14", inclusive="both")]
        anchor_dupes = int(anchor_rows["timestamp"].duplicated().sum())
        expiry_dupes = int(expiry_rows["timestamp"].duplicated().sum())
        anchor_ok = bool(len(anchor_rows) > 0 and anchor_dupes == 0 and _ohlc_rows_valid(anchor_rows, require_volume))
        expiry_ok = bool(len(expiry_rows) > 0 and expiry_dupes == 0 and _ohlc_rows_valid(expiry_rows, require_volume))
        results[target_date] = {
            "anchor_ok": anchor_ok,
            "expiry_ok": expiry_ok,
            "anchor_time_ist": anchor_rows["clock"].iloc[0] if len(anchor_rows) else None,
            "expiry_time_ist": expiry_rows["clock"].iloc[-1] if len(expiry_rows) else None,
            "anchor_bars": int(len(anchor_rows)),
            "expiry_bars": int(len(expiry_rows)),
            "duplicate_anchor_timestamps": anchor_dupes,
            "duplicate_expiry_timestamps": expiry_dupes,
            "status": "PASS" if anchor_ok and expiry_ok else "TARGET_WINDOW_GAP_OR_INVALID_OHLC",
        }
    all_pass = bool(results) and all(item["anchor_ok"] and item["expiry_ok"] for item in results.values())
    return {
        "status": "PASS_RESPONSE" if all_pass else "PARTIAL_TARGET_DATES",
        "bar_count": int(count),
        "dates": results,
    }


def request_intraday_window(
    security_id: str,
    segment: str,
    instrument: str,
    token: str,
    client_id: str,
    start: str,
    end: str,
) -> tuple[dict[str, Any], int]:
    headers = {
        "access-token": token,
        "client-id": client_id,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "securityId": str(security_id),
        "exchangeSegment": segment,
        "instrument": instrument,
        "interval": "1",
        "oi": False,
        "fromDate": f"{start} 09:15:00",
        "toDate": f"{end} 15:15:00",
    }
    attempts = 0
    last_body: dict[str, Any] = {"status": "NO_RESPONSE", "bar_count": 0, "dates": {}}
    for attempt in range(3):
        attempts += 1
        try:
            response = requests.post(INTRADAY_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)
        except requests.RequestException as exc:
            last_body = {"status": "NETWORK_ERROR", "error_type": type(exc).__name__, "bar_count": 0, "dates": {}}
            if attempt < 2:
                time.sleep(1.0)
                continue
            return last_body, attempts
        if response.status_code in (401, 403):
            raise FatalAccessError(f"Dhan historical-data authorization failed with HTTP {response.status_code}.")
        if response.status_code == 429:
            last_body = {"status": "HTTP_429", "bar_count": 0, "dates": {}}
            if attempt < 2:
                retry_header = response.headers.get("Retry-After", "2")
                try:
                    wait = min(max(float(retry_header), 1.0), 10.0)
                except ValueError:
                    wait = 2.0
                time.sleep(wait)
                continue
            return last_body, attempts
        if not response.ok:
            return {"status": f"HTTP_{response.status_code}", "bar_count": 0, "dates": {}}, attempts
        try:
            body = response.json()
        except ValueError:
            last_body = {"status": "INVALID_JSON", "bar_count": 0, "dates": {}}
            if attempt < 2:
                time.sleep(1.0)
                continue
            return last_body, attempts

        arrays, shape_error = _payload_arrays(body)
        retryable_shape_errors = {
            "INVALID_JSON_SHAPE",
            "MISSING_REQUIRED_ARRAY",
            "ARRAY_LENGTH_MISMATCH",
            "VOLUME_LENGTH_MISMATCH",
            "PROVIDER_FAILURE",
        }
        if arrays is None and shape_error in retryable_shape_errors and attempt < 2:
            last_body = body if isinstance(body, dict) else {"status": "INVALID_JSON_SHAPE"}
            time.sleep(1.0)
            continue
        return body, attempts

    return last_body, attempts


def _empty_report(input_manifest: dict[str, Any], settings: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "methodology_version": METHODOLOGY_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "IN_PROGRESS",
        "target_coverage_status": "NOT_EVALUATED",
        "identity_status": "NOT_EVALUATED",
        "input_manifest": input_manifest,
        "settings": settings,
        "auth_method": None,
        "token_refresh_status": None,
        "data_plan_active": None,
        "requests_this_run": 0,
        "cache_reused_index_chunks": 0,
        "cache_reused_stock_chunks": 0,
        "index_chunks": {},
        "stock_chunks": {},
        "cycle_results": [],
        "summary": {},
        "unresolved_security_symbols": [],
        "fatal_error": None,
    }


def write_report(report: dict[str, Any]) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    report["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    tmp = OUTPUT.with_suffix(".tmp")
    tmp.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(OUTPUT)


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    membership = pd.read_csv(MEMBERSHIP_CSV, low_memory=False)
    expiry = pd.read_csv(EXPIRY_CSV, low_memory=False)
    daily = pd.read_csv(INDEX_DAILY_CSV, low_memory=False)
    if "session_date" not in daily.columns:
        raise ValueError("Official NIFTY daily reference lacks session_date.")
    return membership, expiry, daily


def main() -> int:
    started = time.monotonic()
    today = datetime.now(LOCAL_TZ).date()
    provider_floor = (pd.Timestamp(today) - pd.DateOffset(years=5) + pd.Timedelta(days=1)).date()
    configured_floor = date(2021, 11, 1)
    window_start = max(provider_floor, configured_floor)
    membership, expiry_frame, daily_frame = load_inputs()
    daily_sessions = sorted({
        parse_date(value).isoformat()
        for value in daily_frame["session_date"].dropna().astype(str)
    })
    expiries = verified_expiry_dates(expiry_frame)
    max_session = max(daily_sessions)
    eligible_expiries = [value for value in expiries if window_start.isoformat() <= value <= max_session]
    if len(eligible_expiries) < MIN_CONFIRMATORY_HISTORY + 1:
        raise ValueError("Verified expiry calendar does not contain enough eligible history.")
    window_end = eligible_expiries[-1]
    cycles = build_expiry_cycles(
        expiries,
        daily_sessions,
        membership,
        window_start.isoformat(),
        window_end,
        SPECIAL_EVENING_ONLY_SESSIONS,
    )
    if len(cycles) < MIN_CONFIRMATORY_HISTORY:
        raise ValueError("Could not build at least 104 point-in-time expiry cycles.")

    # Download the Dhan scrip master once, but never store its security IDs in the audit output.
    master_response = requests.get(MASTER_URL, timeout=45)
    master_response.raise_for_status()
    master_bytes = master_response.content
    master = pd.read_csv(pd.io.common.BytesIO(master_bytes), low_memory=False)
    master_sha = sha256_bytes(master_bytes)
    index_security_id = find_nifty50_security(master)
    all_symbols = sorted({symbol for cycle in cycles for symbol in cycle["members"]})
    resolved = resolve_ids(master, all_symbols)
    alias_ids = resolve_ids(master, ["TMPV"])
    resolved = apply_historical_security_aliases(all_symbols, resolved, alias_ids)
    unresolved_symbols = sorted(set(all_symbols) - set(resolved))

    start_date = min(cycle["anchor_date"] for cycle in cycles)
    end_date = max(cycle["expiry_date"] for cycle in cycles)
    chunks = make_chunks(start_date, end_date, CHUNK_DAYS)
    chunk_for_date: dict[str, str] = {}
    for chunk in chunks:
        key = chunk_key(chunk)
        for stamp in pd.date_range(chunk["from"], chunk["to"], freq="D").strftime("%Y-%m-%d"):
            chunk_for_date[stamp] = key

    index_dates = sorted({
        stamp
        for cycle in cycles
        for stamp in (cycle["anchor_date"], cycle["expiry_date"])
    })
    stock_dates: dict[str, set[str]] = {}
    for cycle in cycles:
        for symbol in cycle["members"]:
            stock_dates.setdefault(symbol, set()).update((cycle["anchor_date"], cycle["expiry_date"]))

    index_dates_by_chunk: dict[str, list[str]] = {chunk_key(c): [] for c in chunks}
    stock_targets_by_chunk: dict[str, dict[str, list[str]]] = {chunk_key(c): {} for c in chunks}
    for stamp in index_dates:
        key = chunk_for_date[stamp]
        index_dates_by_chunk[key].append(stamp)
    for symbol, dates in stock_dates.items():
        for stamp in dates:
            key = chunk_for_date[stamp]
            stock_targets_by_chunk[key].setdefault(symbol, []).append(stamp)

    input_manifest = {
        "membership_sha256": file_sha256(MEMBERSHIP_CSV),
        "expiry_calendar_sha256": file_sha256(EXPIRY_CSV),
        "official_daily_session_sha256": file_sha256(INDEX_DAILY_CSV),
        "dhan_scrip_master_sha256": master_sha,
        "window_start": window_start.isoformat(),
        "window_end": window_end,
    }
    settings = {
        "chunk_days_inclusive": CHUNK_DAYS,
        "request_delay_seconds": REQUEST_DELAY_SECONDS,
        "target_anchor_window_ist": ["10:00", "10:03"],
        "target_expiry_proxy_window_ist": ["15:00", "15:14"],
        "minimum_valid_members": MIN_VALID_MEMBERS,
        "minimum_member_fraction": MIN_MEMBER_FRACTION,
        "minimum_valid_index_target_fraction": MIN_INDEX_TARGET_FRACTION,
        "minimum_confirmatory_history_cycles": MIN_CONFIRMATORY_HISTORY,
        "special_evening_only_sessions_excluded_from_anchor": sorted(SPECIAL_EVENING_ONLY_SESSIONS),
    }

    # Reuse prior completed 90-day summaries only when every source/configuration hash matches.
    report = _empty_report(input_manifest, settings)
    if OUTPUT.exists():
        try:
            previous = json.loads(OUTPUT.read_text(encoding="utf-8"))
            if (
                previous.get("schema_version") == 1
                and previous.get("methodology_version") == METHODOLOGY_VERSION
                and previous.get("input_manifest") == input_manifest
                and previous.get("settings") == settings
            ):
                report["index_chunks"] = previous.get("index_chunks", {})
                report["stock_chunks"] = previous.get("stock_chunks", {})
                report["cache_reused_index_chunks"] = len(report["index_chunks"])
                report["cache_reused_stock_chunks"] = len(report["stock_chunks"])
        except (OSError, ValueError, TypeError):
            pass
    report["scheduled_cycles"] = len(cycles)
    report["cycle_window"] = {"first_anchor": start_date, "last_expiry": end_date}
    report["expiry_calendar_verified_count"] = len(expiries)
    report["all_symbols_in_point_in_time_window"] = len(all_symbols)
    report["unresolved_security_symbols"] = unresolved_symbols
    report["index_security_id_resolved"] = bool(index_security_id)
    write_report(report)

    # If every requested window is already covered by matching sanitized QA cache
    # entries, do not create another 24-hour Dhan token merely to re-read the cache.
    pending_index = any(
        index_dates_by_chunk[key]
        and report["index_chunks"].get(key, {}).get("status") != "PASS_RESPONSE"
        for key in index_dates_by_chunk
    )
    pending_stocks = any(
        dates
        and symbol in resolved
        and report["stock_chunks"].get(f"{symbol}|{key}", {}).get("status") != "PASS_RESPONSE"
        for key, symbol_targets in stock_targets_by_chunk.items()
        for symbol, dates in symbol_targets.items()
    )
    need_network = pending_index or pending_stocks
    token = ""
    client_id = ""
    try:
        if need_network:
            token, client_id, auth_method, refresh_status, _auth_diagnostics = acquire_access_token()
            report["auth_method"] = auth_method
            report["token_refresh_status"] = refresh_status
            profile = request_profile(token)
            report["profile_http_status"] = int(profile.status_code)
            if not profile.ok:
                raise FatalAccessError(f"Dhan profile authorization failed with HTTP {profile.status_code}.")
            profile_body = profile.json()
            plan = str(profile_body.get("dataPlan", "")).strip().casefold()
            report["data_plan_active"] = plan == "active"
            if plan != "active":
                raise FatalAccessError("Dhan Data API plan is not active.")
        else:
            report["auth_method"] = "SANITIZED_QA_CACHE"
            report["token_refresh_status"] = "NOT_NEEDED"
            report["data_plan_active"] = "NOT_RECHECKED"
    except Exception as exc:
        report["status"] = "BLOCKED_AUTH_OR_ENTITLEMENT"
        report["fatal_error"] = str(exc)[:220] if isinstance(exc, FatalAccessError) else type(exc).__name__
        write_report(report)
        print("C1_CONTINUOUS_COVERAGE_BLOCKED_AUTH")
        return 1

    try:
        for number, chunk in enumerate(chunks, start=1):
            key = chunk_key(chunk)
            target_index_dates = sorted(set(index_dates_by_chunk[key]))
            if target_index_dates:
                cached = report["index_chunks"].get(key)
                if not cached or cached.get("status") != "PASS_RESPONSE":
                    body, attempts = request_intraday_window(
                        index_security_id, "IDX_I", "INDEX", token, client_id, chunk["from"], chunk["to"]
                    )
                    report["requests_this_run"] += attempts
                    time.sleep(REQUEST_DELAY_SECONDS)
                    report["index_chunks"][key] = inspect_target_dates(
                        body, target_index_dates, require_volume=False
                    )
                if report["index_chunks"][key].get("status") not in ("PASS_RESPONSE", "NO_BARS"):
                    report["index_chunks"][key]["target_dates_requested"] = target_index_dates

            for symbol, dates in sorted(stock_targets_by_chunk[key].items()):
                stock_key = f"{symbol}|{key}"
                cached = report["stock_chunks"].get(stock_key)
                if cached and cached.get("status") == "PASS_RESPONSE":
                    continue
                security_id = resolved.get(symbol)
                if not security_id:
                    report["stock_chunks"][stock_key] = {
                        "status": "MISSING_SECURITY_ID",
                        "bar_count": 0,
                        "dates": {},
                    }
                    continue
                body, attempts = request_intraday_window(
                    security_id, "NSE_EQ", "EQUITY", token, client_id, chunk["from"], chunk["to"]
                )
                report["requests_this_run"] += attempts
                time.sleep(REQUEST_DELAY_SECONDS)
                report["stock_chunks"][stock_key] = inspect_target_dates(body, sorted(set(dates)), require_volume=True)
            report["last_completed_chunk"] = key
            report["chunks_completed_this_run"] = number
            report["chunks_total"] = len(chunks)
            write_report(report)
            index_status = report["index_chunks"].get(key, {}).get("status", "NOT_REQUESTED")
            stocks_in_chunk = len(stock_targets_by_chunk[key])
            print(
                f"C1_COVERAGE_CHUNK {number}/{len(chunks)} {key} "
                f"index={index_status} stocks={stocks_in_chunk} "
                f"requests_this_run={report['requests_this_run']}"
            )

        cycle_results = []
        for cycle in cycles:
            anchor_date = cycle["anchor_date"]
            expiry_date = cycle["expiry_date"]
            index_anchor = report["index_chunks"].get(chunk_for_date[anchor_date], {}).get("dates", {}).get(anchor_date, {})
            index_expiry = report["index_chunks"].get(chunk_for_date[expiry_date], {}).get("dates", {}).get(expiry_date, {})
            index_ok = bool(index_anchor.get("anchor_ok") and index_expiry.get("expiry_ok"))
            members = cycle["members"]
            id_to_symbols: dict[str, list[str]] = {}
            for symbol in members:
                if symbol in resolved:
                    id_to_symbols.setdefault(resolved[symbol], []).append(symbol)
            collisions = {name for names in id_to_symbols.values() if len(names) > 1 for name in names}
            valid_members = []
            missing_members = []
            corporate_action_excluded = []
            for symbol in members:
                action_date = KNOWN_CORPORATE_ACTION_DATES.get(symbol)
                if action_date and anchor_date < action_date <= expiry_date:
                    corporate_action_excluded.append(symbol)
                    continue
                if symbol in collisions:
                    missing_members.append(symbol)
                    continue
                if symbol not in resolved:
                    missing_members.append(symbol)
                    continue
                anchor_data = report["stock_chunks"].get(
                    f"{symbol}|{chunk_for_date[anchor_date]}", {}
                ).get("dates", {}).get(anchor_date, {})
                expiry_data = report["stock_chunks"].get(
                    f"{symbol}|{chunk_for_date[expiry_date]}", {}
                ).get("dates", {}).get(expiry_date, {})
                if anchor_data.get("anchor_ok") and expiry_data.get("expiry_ok"):
                    valid_members.append(symbol)
                else:
                    missing_members.append(symbol)
            member_count = len(members)
            fraction = len(valid_members) / member_count if member_count else 0.0
            stock_ok = is_stock_coverage_acceptable(len(valid_members), member_count)
            cycle_results.append({
                "previous_expiry": cycle["previous_expiry"],
                "anchor_date": anchor_date,
                "expiry_date": expiry_date,
                "member_count": member_count,
                "valid_member_count": len(valid_members),
                "member_coverage_fraction": round(fraction, 6),
                "valid_members": valid_members,
                "missing_members": missing_members,
                "known_corporate_action_excluded_symbols": corporate_action_excluded,
                "index_anchor_ok": bool(index_anchor.get("anchor_ok")),
                "index_expiry_proxy_ok": bool(index_expiry.get("expiry_ok")),
                "index_target_ok": index_ok,
                "stock_coverage_ok": stock_ok,
                "cycle_accepted_for_coverage": bool(index_ok and stock_ok),
            })
        coverage_summary = evaluate_cycle_coverage(cycle_results)
        target_gate = coverage_summary["target_coverage_gate"] == "PASS"
        report["cycle_results"] = cycle_results
        report["summary"] = {
            **coverage_summary,
            "minimum_member_coverage_fraction": round(
                min((item["member_coverage_fraction"] for item in cycle_results), default=0.0), 6
            ),
            "median_valid_member_count": float(np.median([item["valid_member_count"] for item in cycle_results])) if cycle_results else 0.0,
            "total_dhan_requests_this_run": report["requests_this_run"],
            "total_index_chunks_cached": len(report["index_chunks"]),
            "total_stock_symbol_chunks_cached": len(report["stock_chunks"]),
        }
        report["target_coverage_status"] = "PASS" if target_gate else "FAIL"
        report["identity_status"] = (
            "UNRESOLVED_SECURITY_SYMBOLS"
            if unresolved_symbols
            else "SYMBOL_MAPPING_RESOLVED_KNOWN_AND_UNIVERSAL_CORPORATE_ACTION_REVIEW_PENDING"
        )
        report["status"] = (
            "DATA_COVERAGE_PASS_IDENTITY_ACTION_REVIEW_PENDING"
            if target_gate
            else "PARTIAL_OR_BLOCKED_TARGET_COVERAGE"
        )
        report["fatal_error"] = None
        report["elapsed_seconds"] = round(time.monotonic() - started, 2)
        write_report(report)
        print("C1_CONTINUOUS_TARGET_COVERAGE", report["target_coverage_status"])
        print(
            f"INDEX_TARGETS {coverage_summary['index_target_valid_cycles']}/{len(cycle_results)} "
            f"STOCK_ACCEPTED_CYCLES {coverage_summary['cycles_accepted_for_coverage']}/{len(cycle_results)} "
            f"CONFIRMATORY_AFTER_104 {coverage_summary['confirmatory_cycles_after_104_prior_cycles']}"
        )
        print(f"UNRESOLVED_ACTIVE_SYMBOLS {len(unresolved_symbols)}")
        return 0 if target_gate else 2
    except FatalAccessError as exc:
        report["status"] = "BLOCKED_AUTH_OR_ENTITLEMENT"
        report["fatal_error"] = str(exc)[:220]
        report["elapsed_seconds"] = round(time.monotonic() - started, 2)
        write_report(report)
        print("C1_CONTINUOUS_COVERAGE_BLOCKED", str(exc)[:220])
        return 1
    except Exception as exc:
        report["status"] = "PARTIAL_OR_BLOCKED_RUNTIME_ERROR"
        report["fatal_error"] = type(exc).__name__
        report["elapsed_seconds"] = round(time.monotonic() - started, 2)
        write_report(report)
        print("C1_CONTINUOUS_COVERAGE_RUNTIME_ERROR", type(exc).__name__)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
