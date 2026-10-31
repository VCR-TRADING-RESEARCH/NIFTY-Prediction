from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import pyotp
import requests
import time

from live_api.app import MASTER_URL, PublicPredictionError
OUTPUT = ROOT / "research" / "constituent_weekly" / "C1_DHAN_PREFLIGHT.json"
MEMBERSHIP_CSV = ROOT / "data" / "constituent_weekly" / "nifty50_membership_intervals.csv"
AUTH_URL = "https://auth.dhan.co/app/generateAccessToken"
PROFILE_URL = "https://api.dhan.co/v2/profile"
INTRADAY_URL = "https://api.dhan.co/v2/charts/intraday"
DAILY_URL = "https://api.dhan.co/v2/charts/historical"
PROBE_SYMBOLS = ("RELIANCE", "TCS", "INFY", "HDFCBANK", "WIPRO")
PROBE_DATES = ("2022-10-31", "2026-10-29")
# Current scrip-master probes do not prove history for removed/delisted security IDs.
IST = "Asia/Kolkata"


# The current scrip master is checked against both the active universe and historical membership aliases.
# Live full-universe checks run only on push/dispatch events, never on pull-request credentials.
# Emit aggregate counts so the protected live run can be independently audited from CI logs.
# The workflow commits the sanitized JSON and STATUS block after each live attempt.
def membership_symbol_sets(as_of_date: str) -> tuple[list[str], list[str]]:
    """Return active tradable symbols and all historical tradable aliases from the licensed ledger."""
    frame = pd.read_csv(MEMBERSHIP_CSV, low_memory=False)
    required = {"symbol", "valid_from", "valid_to", "member_type", "market_data_required"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError("Membership ledger missing required columns: " + ",".join(sorted(missing)))
    symbols = frame["symbol"].astype("string").str.strip()
    starts = pd.to_datetime(frame["valid_from"], errors="coerce")
    ends = pd.to_datetime(frame["valid_to"], errors="coerce")
    cutoff = pd.Timestamp(as_of_date)
    tradable = (
        frame["member_type"].astype(str).str.strip().str.casefold().eq("equity_security")
        & frame["market_data_required"].astype(str).str.strip().str.upper().isin(("TRUE", "1", "YES"))
        & symbols.notna()
        & symbols.ne("")
        & starts.notna()
    )
    historical = sorted(set(symbols[tradable].astype(str)))
    active_mask = tradable & starts.le(cutoff) & (ends.isna() | ends.gt(cutoff))
    active = sorted(set(symbols[active_mask].astype(str)))
    return active, historical


LAST_SUCCESS_OUTPUT = ROOT / "research" / "constituent_weekly" / "C1_DHAN_LAST_SUCCESS.json"


def write_result(data: dict) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2) + "\n"
    OUTPUT.write_text(payload, encoding="utf-8")
    # Preserve the last valid success separately so a transient auth failure cannot erase it.
    if data.get("status") == "PASS_ACTIVE_EQUITIES":
        LAST_SUCCESS_OUTPUT.write_text(payload, encoding="utf-8")




def auth_response_diagnostics(body: object) -> dict:
    """Return response-shape metadata only; never retain provider field values."""
    if not isinstance(body, dict):
        return {"body_type": type(body).__name__, "response_keys": []}

    keys = sorted(str(key) for key in body.keys())
    data = body.get("data")
    data_keys = sorted(str(key) for key in data.keys()) if isinstance(data, dict) else []
    # Classify known auth failure families without retaining provider text.
    message = " ".join(str(body.get(k, "")) for k in ("message", "error", "errorDescription")).casefold()
    category = "UNCLASSIFIED_PROVIDER_RESPONSE"
    if any(term in message for term in ("totp", "one-time password", "otp")):
        category = "TOTP_REJECTED_OR_INVALID"
    elif any(term in message for term in ("pin", "password")):
        category = "PIN_REJECTED_OR_INVALID"
    elif any(term in message for term in ("client id", "clientid", "account id")):
        category = "CLIENT_ID_REJECTED_OR_INVALID"
    elif any(term in message for term in ("expired", "validity")):
        category = "CREDENTIAL_OR_TOKEN_EXPIRED"
    elif any(term in message for term in ("unauthor", "not allowed", "permission")):
        category = "AUTHORIZATION_OR_PERMISSION_FAILURE"
    containers = [("top_level", body)]
    if isinstance(data, dict):
        containers.append(("data", data))

    candidate = None
    candidate_container = None
    candidate_type = "missing"
    candidate_length = 0
    for container_name, container in containers:
        for field in ("accessToken", "access_token"):
            if field in container:
                value = container[field]
                candidate_type = type(value).__name__
                candidate_length = len(value) if isinstance(value, str) else 0
                if isinstance(value, str) and len(value) >= 20:
                    candidate = value
                    candidate_container = container_name
                    break
        if candidate:
            break

    return {
        "body_type": "dict",
        "response_keys": keys,
        "data_keys": data_keys,
        "provider_error_category": category,
        "access_token_field_type": candidate_type,
        "access_token_length": candidate_length,
        "token_container": candidate_container,
    }


def acquire_access_token() -> tuple[str, str, str, str, dict]:
    """Prefer a fresh TOTP token; retry once after the current 30-second TOTP window."""
    client_id = os.getenv("DHAN_CLIENT_ID", "").strip()
    pin = os.getenv("DHAN_PIN", "").strip()
    totp_secret = os.getenv("DHAN_TOTP_SECRET", "").strip()
    fallback_token = os.getenv("DHAN_ACCESS_TOKEN", "").strip()
    refresh_error = "TOTP credentials are not fully configured."
    diagnostics: dict = {"status": "NOT_ATTEMPTED"}

    if client_id and pin and totp_secret:
        for attempt in range(2):
            try:
                otp = pyotp.TOTP(totp_secret).now()
                response = requests.post(
                    AUTH_URL,
                    params={"dhanClientId": client_id, "pin": pin, "totp": otp},
                    timeout=30,
                )
                body = response.json()
                diagnostics = auth_response_diagnostics(body)
                diagnostics["http_status"] = int(response.status_code)
                diagnostics["refresh_attempts"] = attempt + 1
                candidate = None
                if isinstance(body, dict):
                    candidate = body.get("accessToken") or body.get("access_token")
                    if not (isinstance(candidate, str) and len(candidate) >= 20):
                        nested = body.get("data")
                        if isinstance(nested, dict):
                            candidate = nested.get("accessToken") or nested.get("access_token")
                if response.ok and isinstance(candidate, str) and len(candidate) >= 20 and "\n" not in candidate and "\r" not in candidate:
                    return candidate, client_id, "totp_refresh", "SUCCESS", diagnostics
                if response.ok:
                    refresh_error = "Token service returned HTTP success but no usable access token; response values withheld."
                else:
                    refresh_error = f"Token service returned HTTP {response.status_code}; response values withheld."
            except (requests.RequestException, ValueError) as exc:
                refresh_error = f"Token refresh request/JSON failed ({type(exc).__name__}); response values withheld."
            except Exception as exc:
                refresh_error = f"Token refresh failed ({type(exc).__name__}); response values withheld."

            if attempt == 0:
                time.sleep(31)

    if fallback_token and client_id and "\n" not in fallback_token and "\r" not in fallback_token:
        diagnostics["fallback_available"] = True
        return fallback_token, client_id, "provided_token_fallback", "FAILED_FALLBACK_USED", diagnostics

    diagnostics["fallback_available"] = bool(fallback_token)
    raise PublicPredictionError(refresh_error)

def resolve_ids(master: pd.DataFrame, symbols: tuple[str, ...] | list[str] = PROBE_SYMBOLS) -> dict[str, str]:
    columns = {str(c).strip().upper(): c for c in master.columns}
    id_col = next((columns[k] for k in ("SEM_SMST_SECURITY_ID", "SECURITYID", "SECURITY_ID") if k in columns), None)
    symbol_col = next((columns[k] for k in ("SEM_TRADING_SYMBOL", "TRADING_SYMBOL", "SYMBOL") if k in columns), None)
    exchange_col = next((columns[k] for k in ("SEM_EXM_EXCH_ID", "EXCHANGE") if k in columns), None)
    segment_col = next((columns[k] for k in ("SEM_SEGMENT", "SEGMENT") if k in columns), None)
    series_col = next((columns[k] for k in ("SEM_SERIES", "SERIES") if k in columns), None)
    instrument_col = next((columns[k] for k in ("SEM_INSTRUMENT_NAME", "INSTRUMENT", "INSTRUMENT_NAME") if k in columns), None)
    if id_col is None or symbol_col is None:
        raise ValueError("Scrip master missing security-ID or trading-symbol columns.")

    rows = master.copy()
    if exchange_col:
        rows = rows[rows[exchange_col].astype(str).str.upper().eq("NSE")]
    if segment_col:
        rows = rows[rows[segment_col].astype(str).str.upper().isin(("E", "EQ", "NSE_EQ", "EQUITY"))]
    if series_col:
        eq_rows = rows[rows[series_col].astype(str).str.upper().eq("EQ")]
        if not eq_rows.empty:
            rows = eq_rows
    if instrument_col:
        eq_rows = rows[rows[instrument_col].astype(str).str.upper().str.contains("EQUITY", na=False)]
        if not eq_rows.empty:
            rows = eq_rows

    found: dict[str, str] = {}
    for symbol in symbols:
        matches = rows[rows[symbol_col].astype(str).str.upper().eq(symbol)]
        ids = sorted(set(matches[id_col].dropna().astype(str).str.strip()) - {""})
        if len(ids) == 1:
            found[symbol] = ids[0]
    return found


def analyse_bars(body: dict, symbol: str, day: str, *, require_anchor: bool = True, require_expiry: bool = True) -> dict:
    arrays = {k: body.get(k, []) for k in ("open", "high", "low", "close", "volume", "timestamp")}
    lengths = {k: len(v) for k, v in arrays.items()}
    n = lengths["timestamp"]
    if n == 0 or any(length != n for length in lengths.values()):
        return {"symbol": symbol, "date": day, "status": "EMPTY_OR_MISMATCHED_ARRAYS", "array_lengths": lengths}

    frame = pd.DataFrame(arrays)
    frame["time_ist"] = pd.to_datetime(frame["timestamp"], unit="s", utc=True, errors="coerce").dt.tz_convert(IST)
    frame = frame.dropna(subset=["time_ist"]).sort_values("time_ist")
    if frame.empty:
        return {"symbol": symbol, "date": day, "status": "NO_VALID_TIMESTAMPS"}

    ts = frame["time_ist"]
    anchors = frame[(ts.dt.strftime("%Y-%m-%d") == day) & (ts.dt.strftime("%H:%M") >= "10:00") & (ts.dt.strftime("%H:%M") <= "10:03")]
    expiry_candidates = frame[
        (ts.dt.strftime("%Y-%m-%d") == day)
        & (ts.dt.strftime("%H:%M") >= "15:00")
        & (ts.dt.strftime("%H:%M") <= "15:14")
    ]
    expiry_proxy = expiry_candidates.tail(1)
    ohlc_ok = bool(
        ((frame["low"] <= frame[["open", "close"]].min(axis=1)) &
         (frame["high"] >= frame[["open", "close"]].max(axis=1)) &
         (frame[["open", "high", "low", "close"]] > 0).all(axis=1) &
         (frame["volume"] >= 0)).all()
    )
    passed = (not require_anchor or not anchors.empty) and (not require_expiry or not expiry_proxy.empty) and ohlc_ok
    return {
        "symbol": symbol,
        "date": day,
        "status": "PASS" if passed else "REQUIRED_BAR_OR_OHLC_CHECK_FAILED",
        "bar_count": int(len(frame)),
        "anchor_window_bars": int(len(anchors)),
        "expiry_proxy_bar_count": int(len(expiry_proxy)),
        "expiry_proxy_bar_time_ist": expiry_proxy["time_ist"].iloc[-1].isoformat() if not expiry_proxy.empty else None,
        "expiry_proxy_cutoff_ist": "15:15:00",
        "expiry_proxy_price_field": "close",
        "expiry_proxy_method": "Close of the most recent available 1-minute candle timestamped 15:00–15:14 IST; later bars are excluded.",
        "first_bar_ist": ts.iloc[0].isoformat(),
        "last_bar_ist": ts.iloc[-1].isoformat(),
        "ohlc_volume_invariants_pass": ohlc_ok,
    }




def request_intraday_probe(headers: dict, symbol: str, security_id: str, day: str) -> dict:
    """Fetch one compact Dhan one-minute window and return only sanitised QA metadata."""
    response = requests.post(
        INTRADAY_URL,
        headers=headers,
        json={
            "securityId": security_id,
            "exchangeSegment": "NSE_EQ",
            "instrument": "EQUITY",
            "interval": "1",
            "oi": False,
            "fromDate": f"{day} 09:15:00",
            "toDate": f"{day} 15:30:00",
        },
        timeout=60,
    )
    if not response.ok:
        return {"symbol": symbol, "date": day, "status": f"HTTP_{response.status_code}"}
    return analyse_bars(response.json(), symbol, day)


def analyse_intraday_range(body: dict, symbol: str, start_date: str, end_date: str) -> dict:
    """Return sanitized regular-session coverage and OHLCV quality metrics.

    Muhurat dates are explicit non-standard sessions: the regular-day expiry proxy
    must not be inferred from any stale or mis-timestamped daytime rows on those dates.
    Extended/post-market bars are excluded from regular-session OHLCV invariants.
    """
    keys = ("open", "high", "low", "close", "volume", "timestamp")
    arrays = {key: body.get(key, []) for key in keys}
    lengths = {key: len(value) for key, value in arrays.items()}
    n = lengths["timestamp"]
    if n == 0 or any(length != n for length in lengths.values()):
        return {
            "symbol": symbol, "from_date": start_date, "to_date": end_date,
            "status": "EMPTY_OR_MISMATCHED_ARRAYS", "array_lengths": lengths,
        }

    frame = pd.DataFrame(arrays)
    frame["time_ist"] = pd.to_datetime(
        frame["timestamp"], unit="s", utc=True, errors="coerce"
    ).dt.tz_convert(IST)
    frame = frame.dropna(subset=["time_ist"]).sort_values("time_ist")
    if frame.empty:
        return {"symbol": symbol, "from_date": start_date, "to_date": end_date, "status": "NO_VALID_TIMESTAMPS"}

    ts = frame["time_ist"]
    day = ts.dt.strftime("%Y-%m-%d")
    clock = ts.dt.strftime("%H:%M")
    dates = sorted(day.unique().tolist())

    # NSE circulars confirm evening-only Muhurat sessions on these dates.
    # Exclude entire date from normal 10:00/15:15 expiry-proxy validation.
    special_session_dates = {"2021-11-04", "2022-10-24"}
    special_dates_in_response = sorted(set(dates).intersection(special_session_dates))
    regular_mask = clock.between("09:15", "15:30") & ~day.isin(special_session_dates)
    regular_frame = frame.loc[regular_mask].copy()
    regular_day = day.loc[regular_mask]
    regular_clock = clock.loc[regular_mask]
    regular_dates = sorted(regular_day.unique().tolist())
    non_standard_dates = sorted(set(dates) - set(regular_dates))

    anchor_dates = set(regular_day.loc[regular_clock.between("10:00", "10:03")].unique())
    expiry_dates = set(regular_day.loc[regular_clock.between("15:00", "15:14")].unique())
    missing_anchor_dates = sorted(set(regular_dates) - anchor_dates)
    missing_expiry_dates = sorted(set(regular_dates) - expiry_dates)
    duplicated = int(regular_frame["time_ist"].duplicated().sum())

    numeric = regular_frame[["open", "high", "low", "close", "volume"]].apply(
        pd.to_numeric, errors="coerce"
    )
    if numeric.empty:
        finite_rows = pd.Series(dtype=bool, index=numeric.index)
        ohlc_rows = pd.Series(dtype=bool, index=numeric.index)
        volume_rows = pd.Series(dtype=bool, index=numeric.index)
    else:
        numeric_values = numeric.to_numpy(dtype=float)
        finite_rows = numeric.notna().all(axis=1) & np.isfinite(numeric_values).all(axis=1)
        low = numeric["low"]
        high = numeric["high"]
        ohlc_rows = (
            (low <= numeric[["open", "close"]].min(axis=1)) &
            (high >= numeric[["open", "close"]].max(axis=1)) &
            (numeric[["open", "high", "low", "close"]] > 0).all(axis=1)
        )
        volume_rows = numeric["volume"] >= 0

    invalid_numeric_rows = int((~finite_rows).sum())
    invalid_ohlc_rows = int((finite_rows & ~ohlc_rows).sum())
    invalid_volume_rows = int((finite_rows & ~volume_rows).sum())
    ohlc_ok = bool(
        len(regular_frame) > 0 and finite_rows.all() and ohlc_rows.all() and volume_rows.all()
    )
    passed = bool(
        ohlc_ok and duplicated == 0 and len(regular_dates) > 0 and
        not missing_anchor_dates and not missing_expiry_dates
    )
    return {
        "symbol": symbol,
        "from_date": start_date,
        "to_date": end_date,
        "status": "PASS" if passed else "RANGE_COVERAGE_OR_OHLC_FAILED",
        "bar_count": int(len(frame)),
        "regular_bar_count": int(len(regular_frame)),
        "outside_regular_hours_bar_count": int(len(frame) - len(regular_frame)),
        "response_calendar_date_count": int(len(dates)),
        "session_count": int(len(regular_dates)),
        "special_session_dates_excluded": special_dates_in_response,
        "non_standard_session_dates": non_standard_dates,
        "anchor_sessions_present": int(len(anchor_dates)),
        "expiry_proxy_sessions_present": int(len(expiry_dates)),
        "missing_anchor_sessions": len(missing_anchor_dates),
        "missing_expiry_proxy_sessions": len(missing_expiry_dates),
        "missing_anchor_dates": missing_anchor_dates,
        "missing_expiry_proxy_dates": missing_expiry_dates,
        "duplicate_timestamps": duplicated,
        "invalid_numeric_rows": invalid_numeric_rows,
        "invalid_ohlc_rows": invalid_ohlc_rows,
        "invalid_volume_rows": invalid_volume_rows,
        "ohlc_volume_invariants_pass": ohlc_ok,
        "first_timestamp_ist": ts.iloc[0].isoformat(),
        "last_timestamp_ist": ts.iloc[-1].isoformat(),
        "first_regular_timestamp_ist": regular_frame["time_ist"].iloc[0].isoformat() if len(regular_frame) else None,
        "last_regular_timestamp_ist": regular_frame["time_ist"].iloc[-1].isoformat() if len(regular_frame) else None,
        "contains_raw_price_values": False,
    }


def request_intraday_range(headers: dict, symbol: str, security_id: str, start_date: str, end_date: str) -> dict:
    """Fetch one <=90-day Dhan minute window and retain only sanitised QA metadata."""
    response = requests.post(
        INTRADAY_URL,
        headers=headers,
        json={
            "securityId": security_id,
            "exchangeSegment": "NSE_EQ",
            "instrument": "EQUITY",
            "interval": "1",
            "oi": False,
            "fromDate": f"{start_date} 09:15:00",
            "toDate": f"{end_date} 15:15:00",
        },
        timeout=120,
    )
    if not response.ok:
        return {
            "symbol": symbol, "from_date": start_date, "to_date": end_date,
            "status": f"HTTP_{response.status_code}",
        }
    return analyse_intraday_range(response.json(), symbol, start_date, end_date)


def apply_historical_security_aliases(symbols: list[str], resolved: dict, alias_ids: dict) -> dict:
    """Add explicit dated legacy-security mappings without stitching price series."""
    result = dict(resolved)
    if "HDFC" in symbols and "HDFC" not in result:
        result["HDFC"] = "1330"  # Dhan legacy HDFC Ltd security ID; previously sampled 2022/2023.
    if "TATAMOTORS" in symbols and "TATAMOTORS" not in result:
        tmpv_id = alias_ids.get("TMPV")
        if tmpv_id:
            result["TATAMOTORS"] = str(tmpv_id)  # same continuing listing before 2025-10-24 rename/demerger.
    return result


def request_profile(token: str):
    """Check token validity using the documented profile header only."""
    return requests.get(
        PROFILE_URL,
        headers={"access-token": token, "Accept": "application/json"},
        timeout=25,
    )


def log_auth_diagnostics(result: dict) -> None:
    """Emit only status codes, response key names and token metadata; never values."""
    diagnostics = result.get("token_refresh_diagnostics")
    if diagnostics:
        print("TOKEN_RESPONSE_SHAPE", json.dumps(diagnostics, sort_keys=True))



def main() -> int:
    result = {
        "track": "BUP-01",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "BLOCKED",
        "credentials_or_tokens_recorded": False,
        "raw_market_bars_saved": False,
        "daily_history_probe": {},
        "intraday_probe": [],
    }
    try:
        token, client_id, auth_method, refresh_status, auth_diagnostics = acquire_access_token()
        result["auth_method"] = auth_method
        result["token_refresh_status"] = refresh_status
        result["token_refresh_diagnostics"] = auth_diagnostics
        profile = request_profile(token)
        if not profile.ok and auth_method == "totp_refresh":
            fallback_token = os.getenv("DHAN_ACCESS_TOKEN", "").strip()
            if fallback_token and "\n" not in fallback_token and "\r" not in fallback_token:
                retry = request_profile(fallback_token)
                if retry.ok:
                    profile = retry
                    result["auth_method"] = "provided_token_fallback"
                    result["token_refresh_status"] = "FRESH_TOKEN_PROFILE_FAILED_FALLBACK_USED"
                    result["fallback_profile_retry"] = "PASS"
                else:
                    result["fallback_profile_retry"] = f"HTTP_{retry.status_code}"
        if not profile.ok:
            result["status"] = f"BLOCKED_PROFILE_HTTP_{profile.status_code}"
            write_result(result)
            log_auth_diagnostics(result)
            print(result["status"])
            return 0
        headers = {"access-token": token, "client-id": client_id, "Accept": "application/json", "Content-Type": "application/json"}
        profile_body = profile.json()
        data_plan = str(profile_body.get("dataPlan", "")).strip().casefold()
        result["data_plan_active"] = data_plan == "active"
        if data_plan != "active":
            result["status"] = "BLOCKED_DATA_PLAN_NOT_ACTIVE"
            write_result(result)
            print(result["status"])
            return 0

        master_response = requests.get(MASTER_URL, timeout=45)
        master_response.raise_for_status()
        master = pd.read_csv(pd.io.common.BytesIO(master_response.content), low_memory=False)
        as_of_date = datetime.now(ZoneInfo(IST)).date().isoformat()
        current_symbols, historical_symbols = membership_symbol_sets(as_of_date)
        current_ids = resolve_ids(master, current_symbols)
        historical_ids = resolve_ids(master, historical_symbols)
        probe_ids = resolve_ids(master, PROBE_SYMBOLS)
        result["membership_as_of_date_ist"] = as_of_date
        result["current_universe_symbol_count"] = len(current_symbols)
        result["current_universe_resolved_count"] = len(current_ids)
        result["current_universe_missing_symbols"] = sorted(set(current_symbols) - set(current_ids))
        result["historical_membership_symbol_count"] = len(historical_symbols)
        result["historical_membership_symbols_found_in_current_master_count"] = len(historical_ids)
        result["historical_membership_symbols_missing_from_current_master"] = sorted(set(historical_symbols) - set(historical_ids))
        result["security_master_scope_note"] = "Current scrip-master lookup only; does not prove historical security-ID validity for inactive/delisted instruments."
        result["resolved_probe_symbols"] = sorted(probe_ids)
        result["missing_probe_symbols"] = sorted(set(PROBE_SYMBOLS) - set(probe_ids))

        # Full 50-stock cross-section check on a fixed recent historical session.
        full_universe_date = "2026-10-29"
        full_universe_symbols, _ = membership_symbol_sets(full_universe_date)
        full_universe_ids = resolve_ids(master, full_universe_symbols)
        full_universe_results = []
        for symbol in full_universe_symbols:
            security_id = full_universe_ids.get(symbol)
            if not security_id:
                full_universe_results.append({
                    "symbol": symbol, "date": full_universe_date, "status": "MISSING_SECURITY_ID"
                })
                continue
            full_universe_results.append(
                request_intraday_probe(headers, symbol, security_id, full_universe_date)
            )
        full_passed = sum(item.get("status") == "PASS" for item in full_universe_results)
        result["full_universe_probe_date"] = full_universe_date
        result["full_universe_probe_expected"] = len(full_universe_symbols)
        result["full_universe_probe_resolved"] = len(full_universe_ids)
        result["full_universe_probe_passed"] = full_passed
        result["full_universe_probe"] = full_universe_results

        # A <90-day range request tests the actual historical batch size/shape before any bulk backfill.
        range_probe_dates = ("2022-10-03", "2022-12-30")
        range_probe_symbols = ("RELIANCE", "TCS", "INFY")
        range_results = []
        for symbol in range_probe_symbols:
            security_id = probe_ids.get(symbol) or historical_ids.get(symbol)
            if not security_id:
                range_results.append({
                    "symbol": symbol, "from_date": range_probe_dates[0],
                    "to_date": range_probe_dates[1], "status": "MISSING_SECURITY_ID",
                })
                continue
            range_results.append(
                request_intraday_range(
                    headers, symbol, security_id, range_probe_dates[0], range_probe_dates[1]
                )
            )
        result["ninety_day_range_probe"] = range_results
        result["ninety_day_range_probe_expected"] = len(range_probe_symbols)
        result["ninety_day_range_probe_passed"] = sum(item.get("status") == "PASS" for item in range_results)

        # Full point-in-time 50-name basket over one recent <=90-day range.
        full_range_dates = ("2026-06-29", "2026-09-26")
        full_range_symbols, _ = membership_symbol_sets(full_range_dates[0])
        full_range_ids = resolve_ids(master, full_range_symbols)
        full_range_results = []
        for symbol in full_range_symbols:
            security_id = full_range_ids.get(symbol)
            if not security_id:
                full_range_results.append({
                    "symbol": symbol, "from_date": full_range_dates[0],
                    "to_date": full_range_dates[1], "status": "MISSING_SECURITY_ID",
                })
                continue
            full_range_results.append(
                request_intraday_range(
                    headers, symbol, security_id, full_range_dates[0], full_range_dates[1]
                )
            )
            # Stay comfortably below the published per-second API request limit.
            time.sleep(0.25)
        result["full_universe_90d_range_date"] = {
            "from": full_range_dates[0], "to": full_range_dates[1]
        }
        result["full_universe_90d_range_expected"] = len(full_range_symbols)
        result["full_universe_90d_range_resolved"] = len(full_range_ids)
        result["full_universe_90d_range_passed"] = sum(
            item.get("status") == "PASS" for item in full_range_results
        )
        result["full_universe_90d_range_probe"] = full_range_results

        # Historical point-in-time universe and legacy security identities: 2022 Q4.
        historical_range_dates = ("2022-10-03", "2022-12-30")
        historical_symbols, _ = membership_symbol_sets(historical_range_dates[0])
        historical_resolved = resolve_ids(master, historical_symbols)
        alias_ids = resolve_ids(master, ["TMPV"])
        historical_ids = apply_historical_security_aliases(historical_symbols, historical_resolved, alias_ids)
        historical_results = []
        for symbol in historical_symbols:
            security_id = historical_ids.get(symbol)
            if not security_id:
                historical_results.append({
                    "symbol": symbol, "from_date": historical_range_dates[0],
                    "to_date": historical_range_dates[1], "status": "MISSING_SECURITY_ID",
                })
                continue
            historical_results.append(
                request_intraday_range(
                    headers, symbol, security_id,
                    historical_range_dates[0], historical_range_dates[1]
                )
            )
            time.sleep(0.25)
        result["historical_universe_90d_range_date"] = {
            "from": historical_range_dates[0], "to": historical_range_dates[1]
        }
        result["historical_universe_90d_range_expected"] = len(historical_symbols)
        result["historical_universe_90d_range_resolved"] = len(historical_ids)
        result["historical_universe_90d_range_passed"] = sum(
            item.get("status") == "PASS" for item in historical_results
        )
        result["historical_universe_90d_range_probe"] = historical_results

        # Test the oldest edge of the documented five-year intraday history window.
        edge_range_dates = ("2021-11-01", "2022-01-29")
        edge_symbols, _ = membership_symbol_sets(edge_range_dates[0])
        edge_resolved = resolve_ids(master, edge_symbols)
        edge_alias_ids = resolve_ids(master, ["TMPV"])
        edge_ids = apply_historical_security_aliases(edge_symbols, edge_resolved, edge_alias_ids)
        edge_results = []
        for symbol in edge_symbols:
            security_id = edge_ids.get(symbol)
            if not security_id:
                edge_results.append({
                    "symbol": symbol, "from_date": edge_range_dates[0],
                    "to_date": edge_range_dates[1], "status": "MISSING_SECURITY_ID",
                })
                continue
            edge_results.append(
                request_intraday_range(
                    headers, symbol, security_id, edge_range_dates[0], edge_range_dates[1]
                )
            )
            time.sleep(0.25)
        result["five_year_edge_90d_date"] = {
            "from": edge_range_dates[0], "to": edge_range_dates[1]
        }
        result["five_year_edge_90d_expected"] = len(edge_symbols)
        result["five_year_edge_90d_resolved"] = len(edge_ids)
        result["five_year_edge_90d_passed"] = sum(item.get("status") == "PASS" for item in edge_results)
        result["five_year_edge_90d_probe"] = edge_results

        if "RELIANCE" in probe_ids:
            daily = requests.post(
                DAILY_URL,
                headers=headers,
                json={
                    "securityId": probe_ids["RELIANCE"],
                    "exchangeSegment": "NSE_EQ",
                    "instrument": "EQUITY",
                    "expiryCode": 0,
                    "oi": False,
                    "fromDate": "2018-01-01",
                    "toDate": "2018-02-01",
                },
                timeout=60,
            )
            if daily.ok:
                body = daily.json()
                count = min(len(body.get(k, [])) for k in ("open", "high", "low", "close", "volume", "timestamp"))
                result["daily_history_probe"] = {
                    "status": "PASS" if count > 0 else "NO_DAILY_BARS",
                    "bar_count": count,
                    "date_range_requested": ["2018-01-01", "2018-02-01"],
                    "old_daily_history_available": count > 0,
                }
            else:
                result["daily_history_probe"] = {"status": f"HTTP_{daily.status_code}", "bar_count": 0}

        legacy_probe_ids = {"HDFC": "1330"}
        result["legacy_identity_probe"] = []
        for legacy_symbol, legacy_security_id in legacy_probe_ids.items():
            for day in ("2022-10-31", "2023-06-30"):
                legacy_response = requests.post(
                    INTRADAY_URL,
                    headers=headers,
                    json={
                        "securityId": legacy_security_id,
                        "exchangeSegment": "NSE_EQ",
                        "instrument": "EQUITY",
                        "interval": "1",
                        "oi": False,
                        "fromDate": f"{day} 09:15:00",
                        "toDate": f"{day} 15:15:00",
                    },
                    timeout=60,
                )
                if not legacy_response.ok:
                    result["legacy_identity_probe"].append({
                        "symbol": legacy_symbol, "date": day, "status": f"HTTP_{legacy_response.status_code}"
                    })
                    continue
                legacy_result = analyse_bars(legacy_response.json(), legacy_symbol, day)
                legacy_result["probe_type"] = "documented_legacy_security_id"
                result["legacy_identity_probe"].append(legacy_result)

        for symbol, security_id in probe_ids.items():
            for day in PROBE_DATES:
                response = requests.post(
                    INTRADAY_URL,
                    headers=headers,
                    json={
                        "securityId": security_id,
                        "exchangeSegment": "NSE_EQ",
                        "instrument": "EQUITY",
                        "interval": "1",
                        "oi": False,
                        "fromDate": f"{day} 09:15:00",
                        "toDate": f"{day} 15:30:00",
                    },
                    timeout=60,
                )
                if not response.ok:
                    result["intraday_probe"].append({"symbol": symbol, "date": day, "status": f"HTTP_{response.status_code}"})
                    continue
                body = response.json()
                result["intraday_probe"].append(analyse_bars(body, symbol, day))

        expected = len(PROBE_SYMBOLS) * len(PROBE_DATES)
        passed = sum(x.get("status") == "PASS" for x in result["intraday_probe"])
        result["intraday_probe_passed"] = passed
        result["intraday_probe_expected"] = expected
        result["expiry_proxy_cutoff_ist"] = "15:15:00"
        result["expiry_proxy_definition"] = "Use the close of the latest available 1-minute candle timestamped between 15:00 and 15:14 IST; ignore later candles."
        full_expected = result.get("full_universe_probe_expected", 0)
        full_passed = result.get("full_universe_probe_passed", 0)
        full_complete = full_expected > 0 and full_passed == full_expected
        range_expected = result.get("ninety_day_range_probe_expected", 0)
        range_passed = result.get("ninety_day_range_probe_passed", 0)
        range_complete = range_expected > 0 and range_passed == range_expected
        full_range_expected = result.get("full_universe_90d_range_expected", 0)
        full_range_passed = result.get("full_universe_90d_range_passed", 0)
        full_range_complete = full_range_expected == 50 and full_range_passed == 50 and result.get("full_universe_90d_range_resolved", 0) == 50
        historical_range_expected = result.get("historical_universe_90d_range_expected", 0)
        historical_range_passed = result.get("historical_universe_90d_range_passed", 0)
        historical_range_complete = historical_range_expected == 50 and historical_range_passed == 50 and result.get("historical_universe_90d_range_resolved", 0) == 50
        edge_expected = result.get("five_year_edge_90d_expected", 0)
        edge_passed = result.get("five_year_edge_90d_passed", 0)
        edge_complete = edge_expected == 50 and edge_passed == 50 and result.get("five_year_edge_90d_resolved", 0) == 50
        result["status"] = "PASS_ACTIVE_EQUITIES" if passed == expected and full_complete and range_complete and full_range_complete and historical_range_complete and edge_complete else "PARTIAL_OR_BLOCKED"
        result["note"] = "Five-symbol/two-date data probe only. The final available candle by the 15:15 IST cutoff is accepted as the expiry proxy; this does not establish full-universe coverage, inactive-security history or official index weights."
    except PublicPredictionError as exc:
        result["status"] = "BLOCKED_DHAN_AUTH"
        result["sanitised_error"] = str(exc)[:200]
    except requests.RequestException as exc:
        result["status"] = "BLOCKED_PROVIDER_OR_NETWORK"
        result["sanitised_error_type"] = type(exc).__name__
    except Exception as exc:
        result["status"] = "BLOCKED_PREFLIGHT_ERROR"
        result["sanitised_error_type"] = type(exc).__name__

    result["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_result(result)
    print(f"Dhan equity preflight status: {result['status']}")
    if result.get("token_refresh_diagnostics"):
        print("TOKEN_RESPONSE_SHAPE", json.dumps(result["token_refresh_diagnostics"], sort_keys=True))
    print(f"Data API plan active: {result.get('data_plan_active')}")
    # Print full-universe counts so live workflow logs are independently auditable.
    print(f"Current NIFTY 50 security-master resolution: {result.get('current_universe_resolved_count', 0)}/{result.get('current_universe_symbol_count', 0)}")
    print(f"Historical membership aliases found in current scrip master: {result.get('historical_membership_symbols_found_in_current_master_count', 0)}/{result.get('historical_membership_symbol_count', 0)}")
    print(f"Five-symbol price probe IDs resolved: {len(result.get('resolved_probe_symbols', []))}; unresolved: {len(result.get('missing_probe_symbols', []))}")
    print(f"Daily history probe: {result.get('daily_history_probe', {}).get('status', 'NOT_RUN')}; bars={result.get('daily_history_probe', {}).get('bar_count', 0)}")
    print(f"Intraday windows passing: {result.get('intraday_probe_passed', 0)}/{result.get('intraday_probe_expected', 0)}")
    print(f"Expiry-proxy cutoff: {result.get('expiry_proxy_cutoff_ist', 'NOT_SET')}")
    print(f"Full point-in-time NIFTY 50 probe: {result.get('full_universe_probe_passed', 0)}/{result.get('full_universe_probe_expected', 0)} passed; resolved={result.get('full_universe_probe_resolved', 0)}; date={result.get('full_universe_probe_date', 'NOT_RUN')}")
    print(f"90-day range probe: {result.get('ninety_day_range_probe_passed', 0)}/{result.get('ninety_day_range_probe_expected', 0)} passed")
    print(f"Full-universe 90-day range probe: {result.get('full_universe_90d_range_passed', 0)}/{result.get('full_universe_90d_range_expected', 0)} passed; resolved={result.get('full_universe_90d_range_resolved', 0)}")
    print(f"Historical point-in-time 2022 90-day range probe: {result.get('historical_universe_90d_range_passed', 0)}/{result.get('historical_universe_90d_range_expected', 0)} passed; resolved={result.get('historical_universe_90d_range_resolved', 0)}")
    print(f"Five-year edge 2021 90-day range probe: {result.get('five_year_edge_90d_passed', 0)}/{result.get('five_year_edge_90d_expected', 0)} passed; resolved={result.get('five_year_edge_90d_resolved', 0)}")
    for probe in result.get("intraday_probe", []):
        print("PROBE", probe.get("symbol"), probe.get("date"), probe.get("status"),
              "bars=", probe.get("bar_count", 0),
              "anchor=", probe.get("anchor_window_bars", 0),
              "expiry_proxy_time=", probe.get("expiry_proxy_bar_time_ist"),
              "ohlc_ok=", probe.get("ohlc_volume_invariants_pass"))
    print("No raw bars, prices, security IDs, tokens, PINs or TOTP values were saved or logged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Trigger a persisted live Dhan run after correcting the diagnostics commit step.
