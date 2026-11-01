from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from live_api.app import MASTER_URL
from scripts.constituent_weekly.dhan_equity_preflight import (
    DAILY_URL,
    IST,
    MEMBERSHIP_CSV,
    acquire_access_token,
    apply_historical_security_aliases,
    request_profile,
    resolve_ids,
)

INDEX_DAILY_CSV = ROOT / "data" / "reconciliation" / "nifty50_official_daily.csv"
OUTPUT = ROOT / "research" / "constituent_weekly" / "C1_DAILY_COVERAGE.json"
START_DATE = "2018-04-01"
REQUEST_DELAY_SECONDS = 0.25
REQUEST_TIMEOUT_SECONDS = 60
METHODOLOGY_VERSION = "bup01-c1-daily-feature-coverage-v1"


class FatalAccessError(RuntimeError):
    pass


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def build_expected_member_sessions(
    membership: pd.DataFrame,
    session_dates: list[str],
    start_date: str = START_DATE,
) -> dict[str, list[str]]:
    required = {"symbol", "valid_from", "valid_to", "member_type", "market_data_required"}
    missing = required - set(membership.columns)
    if missing:
        raise ValueError("Membership ledger lacks required date or tradability fields.")
    symbols = membership["symbol"].astype("string").str.strip()
    starts = pd.to_datetime(membership["valid_from"], errors="coerce")
    ends = pd.to_datetime(membership["valid_to"], errors="coerce")
    member_type = membership["member_type"].astype(str).str.strip().str.casefold()
    tradable = membership["market_data_required"].astype(str).str.strip().str.upper().isin(("TRUE", "1", "YES"))
    start_cutoff = pd.Timestamp(start_date)
    result: dict[str, list[str]] = {}
    for symbol in sorted(set(symbols.dropna().astype(str))):
        mask = (
            symbols.eq(symbol)
            & member_type.eq("equity_security")
            & tradable
            & starts.notna()
            & starts.le(pd.Timestamp(max(session_dates)))
            & (ends.isna() | ends.gt(start_cutoff))
        )
        intervals = [
            (starts.loc[i], ends.loc[i])
            for i in membership.index[mask]
        ]
        expected = []
        for day in session_dates:
            stamp = pd.Timestamp(day)
            if stamp < start_cutoff:
                continue
            if any(stamp >= left and (pd.isna(right) or stamp < right) for left, right in intervals):
                expected.append(day)
        if expected:
            result[symbol] = expected
    return result


def parse_daily_payload(body: Any) -> tuple[pd.DataFrame | None, str | None]:
    if not isinstance(body, dict):
        return None, "INVALID_JSON_SHAPE"
    if str(body.get("status", "")).casefold() == "failure":
        return None, "PROVIDER_FAILURE"
    payload = body.get("data") if isinstance(body.get("data"), dict) else body
    names = ("timestamp", "open", "high", "low", "close", "volume")
    arrays = {key: payload.get(key) for key in names}
    if any(not isinstance(value, list) for value in arrays.values()):
        return None, "MISSING_DAILY_ARRAY"
    lengths = {len(value) for value in arrays.values()}
    if len(lengths) != 1:
        return None, "DAILY_ARRAY_LENGTH_MISMATCH"
    if not lengths or next(iter(lengths)) == 0:
        return pd.DataFrame(columns=["session_date", "open", "high", "low", "close", "volume"]), "NO_DAILY_BARS"
    frame = pd.DataFrame({
        "timestamp": pd.to_datetime(arrays["timestamp"], unit="s", utc=True, errors="coerce"),
        "open": pd.to_numeric(arrays["open"], errors="coerce"),
        "high": pd.to_numeric(arrays["high"], errors="coerce"),
        "low": pd.to_numeric(arrays["low"], errors="coerce"),
        "close": pd.to_numeric(arrays["close"], errors="coerce"),
        "volume": pd.to_numeric(arrays["volume"], errors="coerce"),
    })
    frame = frame.dropna(subset=["timestamp"]).copy()
    frame["session_date"] = (
        frame["timestamp"].dt.tz_convert(IST).dt.strftime("%Y-%m-%d")
    )
    return frame, None


def summarise_daily_coverage(body: Any, expected_dates: list[str]) -> dict[str, Any]:
    frame, parse_error = parse_daily_payload(body)
    if frame is None:
        return {
            "status": parse_error or "INVALID_RESPONSE",
            "expected_session_count": len(expected_dates),
            "available_session_count": 0,
            "valid_ohlc_session_count": 0,
            "valid_volume_session_count": 0,
            "coverage_fraction": 0.0,
            "missing_session_sample": expected_dates[:20],
        }
    if frame.empty:
        return {
            "status": parse_error or "NO_DAILY_BARS",
            "expected_session_count": len(expected_dates),
            "available_session_count": 0,
            "valid_ohlc_session_count": 0,
            "valid_volume_session_count": 0,
            "coverage_fraction": 0.0,
            "missing_session_sample": expected_dates[:20],
        }

    frame["ohlc_valid"] = False
    numeric = frame[["open", "high", "low", "close"]].to_numpy(dtype=float)
    finite = np.isfinite(numeric).all(axis=1)
    positive = (numeric > 0).all(axis=1)
    low = frame["low"].to_numpy(dtype=float)
    high = frame["high"].to_numpy(dtype=float)
    open_ = frame["open"].to_numpy(dtype=float)
    close = frame["close"].to_numpy(dtype=float)
    invariant = (
        (low <= np.minimum(open_, close))
        & (high >= np.maximum(open_, close))
        & (high >= low)
    )
    frame["ohlc_valid"] = finite & positive & invariant
    volume = frame["volume"].to_numpy(dtype=float)
    frame["volume_valid"] = np.isfinite(volume) & (volume >= 0)
    counts = frame.groupby("session_date", dropna=True).size()
    unique_dates = set(counts.index)
    duplicate_dates = sorted(d for d, count in counts.items() if count != 1)

    valid_ohlc_dates = set(
        frame.loc[frame["ohlc_valid"], "session_date"]
    )
    valid_volume_dates = set(
        frame.loc[frame["ohlc_valid"] & frame["volume_valid"], "session_date"]
    )
    duplicates = set(duplicate_dates)
    expected = set(expected_dates)
    valid_ohlc_expected = (valid_ohlc_dates & expected) - duplicates
    valid_volume_expected = (valid_volume_dates & expected) - duplicates
    missing = sorted(expected - valid_ohlc_expected)

    return {
        "status": "PASS_RESPONSE",
        "expected_session_count": len(expected_dates),
        "available_session_count": len(unique_dates & expected),
        "valid_ohlc_session_count": len(valid_ohlc_expected),
        "valid_volume_session_count": len(valid_volume_expected),
        "ohlc_coverage_fraction": round(len(valid_ohlc_expected) / len(expected), 6) if expected else 0.0,
        "volume_coverage_fraction": round(len(valid_volume_expected) / len(expected), 6) if expected else 0.0,
        "duplicate_session_count": len(duplicates & expected),
        "invalid_ohlc_row_count": int((~frame["ohlc_valid"]).sum()),
        "invalid_volume_row_count": int((~frame["volume_valid"]).sum()),
        "first_daily_bar_date": min(unique_dates) if unique_dates else None,
        "last_daily_bar_date": max(unique_dates) if unique_dates else None,
        "missing_session_sample": missing[:20],
        "missing_session_count": len(missing),
    }


def request_daily_history(
    security_id: str,
    token: str,
    client_id: str,
    from_date: str,
    to_date_exclusive: str,
) -> tuple[Any, int]:
    headers = {
        "access-token": token,
        "client-id": client_id,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "securityId": str(security_id),
        "exchangeSegment": "NSE_EQ",
        "instrument": "EQUITY",
        "expiryCode": 0,
        "oi": False,
        "fromDate": from_date,
        "toDate": to_date_exclusive,
    }
    for attempt in range(2):
        try:
            response = requests.post(
                DAILY_URL,
                headers=headers,
                json=payload,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.RequestException as exc:
            return {"status": "NETWORK_ERROR", "error_type": type(exc).__name__}, attempt + 1
        if response.status_code in (401, 403):
            raise FatalAccessError(f"Dhan daily-history authorization failed with HTTP {response.status_code}.")
        if response.status_code == 429 and attempt == 0:
            wait_header = response.headers.get("Retry-After", "2")
            try:
                wait = min(max(float(wait_header), 1.0), 10.0)
            except ValueError:
                wait = 2.0
            time.sleep(wait)
            continue
        if not response.ok:
            return {"status": f"HTTP_{response.status_code}"}, attempt + 1
        try:
            return response.json(), attempt + 1
        except ValueError:
            return {"status": "INVALID_JSON"}, attempt + 1
    return {"status": "HTTP_429"}, 2


def write_report(report: dict[str, Any]) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    report["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    tmp = OUTPUT.with_suffix(".tmp")
    tmp.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(OUTPUT)


def main() -> int:
    started = time.monotonic()
    membership = pd.read_csv(MEMBERSHIP_CSV, low_memory=False)
    calendar = pd.read_csv(INDEX_DAILY_CSV, low_memory=False)
    if "session_date" not in calendar.columns:
        raise ValueError("Official NIFTY daily-session reference lacks session_date.")
    session_dates = sorted({
        pd.Timestamp(value).strftime("%Y-%m-%d")
        for value in calendar["session_date"].dropna().astype(str)
        if pd.Timestamp(value) >= pd.Timestamp(START_DATE)
    })
    if not session_dates:
        raise ValueError("No official trading-session dates found in feature window.")
    window_end = session_dates[-1]
    expected_by_symbol = build_expected_member_sessions(membership, session_dates)
    symbols = sorted(expected_by_symbol)

    master_response = requests.get(MASTER_URL, timeout=45)
    master_response.raise_for_status()
    master_bytes = master_response.content
    master = pd.read_csv(pd.io.common.BytesIO(master_bytes), low_memory=False)
    master_sha = sha256_bytes(master_bytes)
    resolved = resolve_ids(master, symbols)
    alias_ids = resolve_ids(master, ["TMPV"])
    resolved = apply_historical_security_aliases(symbols, resolved, alias_ids)
    unresolved = sorted(set(symbols) - set(resolved))

    expected_total = sum(len(expected_by_symbol[symbol]) for symbol in symbols)
    manifest = {
        "membership_sha256": file_sha256(MEMBERSHIP_CSV),
        "official_daily_session_sha256": file_sha256(INDEX_DAILY_CSV),
        "dhan_scrip_master_sha256": master_sha,
        "daily_endpoint": DAILY_URL,
        "official_session_count": len(session_dates),
        "expected_member_session_count": expected_total,
        "window_start": START_DATE,
        "window_end": window_end,
    }
    report = {
        "schema_version": 1,
        "methodology_version": METHODOLOGY_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "IN_PROGRESS",
        "coverage_interpretation": "Descriptive daily OHLCV coverage only; the plan does not register a separate numeric daily-coverage acceptance threshold.",
        "input_manifest": manifest,
        "requests_this_run": 0,
        "cache_reused_symbols": 0,
        "symbol_results": {},
        "unresolved_symbols": unresolved,
        "summary": {},
        "fatal_error": None,
    }
    if OUTPUT.exists():
        try:
            old = json.loads(OUTPUT.read_text(encoding="utf-8"))
            if old.get("methodology_version") == METHODOLOGY_VERSION and old.get("input_manifest") == manifest:
                report["symbol_results"] = old.get("symbol_results", {})
                report["cache_reused_symbols"] = len(report["symbol_results"])
        except (OSError, ValueError, TypeError):
            pass

    pending = [symbol for symbol in symbols if symbol in resolved and
               report["symbol_results"].get(symbol, {}).get("status") != "PASS_RESPONSE"]
    write_report(report)
    try:
        if pending:
            token, client_id, auth_method, refresh_status, _diag = acquire_access_token()
            profile = request_profile(token)
            if not profile.ok:
                raise FatalAccessError(f"Dhan profile authorization failed with HTTP {profile.status_code}.")
            body = profile.json()
            if str(body.get("dataPlan", "")).strip().casefold() != "active":
                raise FatalAccessError("Dhan Data API plan is not active.")
            report["auth_method"] = auth_method
            report["token_refresh_status"] = refresh_status
        else:
            token = client_id = ""
            report["auth_method"] = "SANITIZED_QA_CACHE"
            report["token_refresh_status"] = "NOT_NEEDED"

        for number, symbol in enumerate(pending, 1):
            response, attempts = request_daily_history(
                resolved[symbol],
                token,
                client_id,
                START_DATE,
                (date.fromisoformat(window_end) + timedelta(days=1)).isoformat(),
            )
            report["requests_this_run"] += attempts
            time.sleep(REQUEST_DELAY_SECONDS)
            report["symbol_results"][symbol] = summarise_daily_coverage(
                response, expected_by_symbol[symbol]
            )
            report["last_symbol_completed"] = symbol
            report["symbols_completed_this_run"] = number
            report["symbols_total"] = len(pending)
            write_report(report)
            print(
                f"C1_DAILY_SYMBOL {number}/{len(pending)} {symbol} "
                f"coverage={report['symbol_results'][symbol].get('ohlc_coverage_fraction', 0):.3f} "
                f"requests={report['requests_this_run']}"
            )

        results = report["symbol_results"]
        valid_symbols = [s for s in symbols if results.get(s, {}).get("status") == "PASS_RESPONSE"]
        total_expected = sum(len(expected_by_symbol[s]) for s in symbols)
        total_valid = sum(results.get(s, {}).get("valid_ohlc_session_count", 0) for s in symbols)
        total_volume = sum(results.get(s, {}).get("valid_volume_session_count", 0) for s in symbols)
        per_symbol_ohlc = [
            results[symbol].get("ohlc_coverage_fraction", 0.0)
            for symbol in symbols
            if symbol in results and results[symbol].get("status") == "PASS_RESPONSE"
        ]
        per_symbol_ohlcv = [
            results[symbol].get("volume_coverage_fraction", 0.0)
            for symbol in symbols
            if symbol in results and results[symbol].get("status") == "PASS_RESPONSE"
        ]
        report["summary"] = {
            "window_start": START_DATE,
            "window_end": window_end,
            "official_trading_session_count": len(session_dates),
            "point_in_time_symbols_expected": len(symbols),
            "expected_member_sessions": total_expected,
            "symbols_with_parseable_daily_responses": len(valid_symbols),
            "expected_member_sessions": total_expected,
            "valid_member_sessions_ohlc": total_valid,
            "valid_member_sessions_ohlcv": total_volume,
            "weighted_ohlc_session_coverage_fraction": round(total_valid / total_expected, 6) if total_expected else 0.0,
            "weighted_ohlcv_session_coverage_fraction": round(total_volume / total_expected, 6) if total_expected else 0.0,
            "symbols_with_unresolved_security_id": len(unresolved),
            "symbols_with_any_ohlc_gap": sum(value < 1.0 for value in per_symbol_ohlc),
            "symbols_with_any_ohlcv_gap": sum(value < 1.0 for value in per_symbol_ohlcv),
            "minimum_symbol_ohlc_coverage_fraction": min(per_symbol_ohlc, default=0.0),
            "median_symbol_ohlc_coverage_fraction": float(np.median(per_symbol_ohlc)) if per_symbol_ohlc else 0.0,
            "minimum_symbol_ohlcv_coverage_fraction": min(per_symbol_ohlcv, default=0.0),
            "median_symbol_ohlcv_coverage_fraction": float(np.median(per_symbol_ohlcv)) if per_symbol_ohlcv else 0.0,
            "daily_feature_coverage_disposition": "DESCRIPTIVE_REVIEW_REQUIRED",
        }
        report["status"] = "COMPLETED_WITH_GAPS" if unresolved or total_valid < total_expected or total_volume < total_expected else "COMPLETE"
        report["elapsed_seconds"] = round(time.monotonic() - started, 2)
        write_report(report)
        print("C1_DAILY_COVERAGE_STATUS", report["status"])
        return 0
    except FatalAccessError as exc:
        report["status"] = "BLOCKED_AUTH_OR_ENTITLEMENT"
        report["fatal_error"] = str(exc)[:180]
        write_report(report)
        print("C1_DAILY_COVERAGE_BLOCKED", str(exc)[:180])
        return 1
    except Exception as exc:
        report["status"] = "PARTIAL_OR_BLOCKED_RUNTIME_ERROR"
        report["fatal_error"] = type(exc).__name__
        write_report(report)
        print("C1_DAILY_COVERAGE_RUNTIME_ERROR", type(exc).__name__)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
