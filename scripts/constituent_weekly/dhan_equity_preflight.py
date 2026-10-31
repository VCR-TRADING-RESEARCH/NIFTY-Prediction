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

import pandas as pd
import pyotp
import requests

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


def write_result(data: dict) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")




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
    """Prefer fresh TOTP generation; use the configured token only after safe validation."""
    client_id = os.getenv("DHAN_CLIENT_ID", "").strip()
    pin = os.getenv("DHAN_PIN", "").strip()
    totp_secret = os.getenv("DHAN_TOTP_SECRET", "").strip()
    fallback_token = os.getenv("DHAN_ACCESS_TOKEN", "").strip()
    refresh_error = "TOTP credentials are not fully configured."
    diagnostics: dict = {"status": "NOT_ATTEMPTED"}

    if client_id and pin and totp_secret:
        try:
            otp = pyotp.TOTP(totp_secret).now()
            response = requests.post(
                AUTH_URL,
                params={"dhanClientId": client_id, "pin": pin, "totp": otp},
                timeout=30,
            )
            diagnostics = auth_response_diagnostics(response.json())
            diagnostics["http_status"] = int(response.status_code)
            if response.ok:
                body = response.json()
                candidate = body.get("accessToken") or body.get("access_token") if isinstance(body, dict) else None
                if isinstance(body, dict) and not (isinstance(candidate, str) and len(candidate) >= 20):
                    nested = body.get("data")
                    if isinstance(nested, dict):
                        candidate = nested.get("accessToken") or nested.get("access_token")
                if isinstance(candidate, str) and len(candidate) >= 20 and "\n" not in candidate and "\r" not in candidate:
                    return candidate, client_id, "totp_refresh", "SUCCESS", diagnostics
                refresh_error = "Token service returned HTTP success but no usable access token; response values withheld."
            else:
                refresh_error = f"Token service returned HTTP {response.status_code}; response values withheld."
        except (requests.RequestException, ValueError) as exc:
            refresh_error = f"Token refresh request/JSON failed ({type(exc).__name__}); response values withheld."
        except Exception as exc:
            refresh_error = f"Token refresh failed ({type(exc).__name__}); response values withheld."

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
    expiry = frame[(ts.dt.strftime("%Y-%m-%d") == day) & (ts.dt.strftime("%H:%M") >= "15:25") & (ts.dt.strftime("%H:%M") <= "15:29")]
    ohlc_ok = bool(
        ((frame["low"] <= frame[["open", "close"]].min(axis=1)) &
         (frame["high"] >= frame[["open", "close"]].max(axis=1)) &
         (frame[["open", "high", "low", "close"]] > 0).all(axis=1) &
         (frame["volume"] >= 0)).all()
    )
    passed = (not require_anchor or not anchors.empty) and (not require_expiry or not expiry.empty) and ohlc_ok
    return {
        "symbol": symbol,
        "date": day,
        "status": "PASS" if passed else "REQUIRED_BAR_OR_OHLC_CHECK_FAILED",
        "bar_count": int(len(frame)),
        "anchor_window_bars": int(len(anchors)),
        "expiry_close_window_bars": int(len(expiry)),
        "first_bar_ist": ts.iloc[0].isoformat(),
        "last_bar_ist": ts.iloc[-1].isoformat(),
        "ohlc_volume_invariants_pass": ohlc_ok,
    }



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
        "targeted_expiry_close_probe": [],
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

                # Dhan's large day response may be truncated; probe only the final 10-minute window separately.
                if day == "2026-10-29":
                    close_response = requests.post(
                        INTRADAY_URL,
                        headers=headers,
                        json={
                            "securityId": security_id,
                            "exchangeSegment": "NSE_EQ",
                            "instrument": "EQUITY",
                            "interval": "1",
                            "oi": False,
                            "fromDate": f"{day} 15:20:00",
                            "toDate": f"{day} 15:30:00",
                        },
                        timeout=60,
                    )
                    if not close_response.ok:
                        result["targeted_expiry_close_probe"].append({
                            "symbol": symbol, "date": day, "status": f"HTTP_{close_response.status_code}"
                        })
                    else:
                        close_body = close_response.json()
                        close_result = analyse_bars(
                            close_body, symbol, day, require_anchor=False, require_expiry=True
                        )
                        close_result["probe_type"] = "targeted_expiry_close"
                        result["targeted_expiry_close_probe"].append(close_result)

        expected = len(PROBE_SYMBOLS) * len(PROBE_DATES)
        passed = sum(x.get("status") == "PASS" for x in result["intraday_probe"])
        result["intraday_probe_passed"] = passed
        result["intraday_probe_expected"] = expected
        targeted_passed = sum(x.get("status") == "PASS" for x in result["targeted_expiry_close_probe"])
        result["targeted_expiry_close_passed"] = targeted_passed
        result["targeted_expiry_close_expected"] = len(result["targeted_expiry_close_probe"])
        result["status"] = "PASS_ACTIVE_EQUITIES" if passed == expected and targeted_passed == len(PROBE_SYMBOLS) else "PARTIAL_OR_BLOCKED"
        result["note"] = "This tests only five current master symbols on two dates; it does not establish history for delisted/inactive securities or index membership/weights."
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
    print(f"Current symbols resolved: {len(result.get('resolved_probe_symbols', []))}; unresolved: {len(result.get('missing_probe_symbols', []))}")
    print(f"Daily history probe: {result.get('daily_history_probe', {}).get('status', 'NOT_RUN')}; bars={result.get('daily_history_probe', {}).get('bar_count', 0)}")
    print(f"Intraday windows passing: {result.get('intraday_probe_passed', 0)}/{result.get('intraday_probe_expected', 0)}")
    print(f"Targeted 2026 expiry-close windows passing: {result.get('targeted_expiry_close_passed', 0)}/{result.get('targeted_expiry_close_expected', 0)}")
    for probe in result.get("targeted_expiry_close_probe", []):
        print("TARGETED_CLOSE", probe.get("symbol"), probe.get("date"), probe.get("status"),
              "bars=", probe.get("bar_count", 0),
              "expiry_close=", probe.get("expiry_close_window_bars", 0),
              "ohlc_ok=", probe.get("ohlc_volume_invariants_pass"))
    for probe in result.get("intraday_probe", []):
        print("PROBE", probe.get("symbol"), probe.get("date"), probe.get("status"),
              "bars=", probe.get("bar_count", 0),
              "anchor=", probe.get("anchor_window_bars", 0),
              "expiry_close=", probe.get("expiry_close_window_bars", 0),
              "ohlc_ok=", probe.get("ohlc_volume_invariants_pass"))
    print("No raw bars, prices, security IDs, tokens, PINs or TOTP values were saved or logged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
