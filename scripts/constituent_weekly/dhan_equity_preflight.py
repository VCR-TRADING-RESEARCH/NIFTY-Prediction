from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import pyotp
import requests

from live_api.app import MASTER_URL, PublicPredictionError
OUTPUT = ROOT / "research" / "constituent_weekly" / "C1_DHAN_PREFLIGHT.json"
AUTH_URL = "https://auth.dhan.co/app/generateAccessToken"
PROFILE_URL = "https://api.dhan.co/v2/profile"
INTRADAY_URL = "https://api.dhan.co/v2/charts/intraday"
DAILY_URL = "https://api.dhan.co/v2/charts/historical"
PROBE_SYMBOLS = ("RELIANCE", "TCS", "INFY", "HDFCBANK", "WIPRO")
PROBE_DATES = ("2022-10-31", "2026-10-30")
# Current scrip-master probes do not prove history for removed/delisted security IDs.
IST = "Asia/Kolkata"


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

def resolve_ids(master: pd.DataFrame) -> dict[str, str]:
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
    for symbol in PROBE_SYMBOLS:
        matches = rows[rows[symbol_col].astype(str).str.upper().eq(symbol)]
        ids = sorted(set(matches[id_col].dropna().astype(str).str.strip()) - {""})
        if len(ids) == 1:
            found[symbol] = ids[0]
    return found


def analyse_bars(body: dict, symbol: str, day: str) -> dict:
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
    passed = not anchors.empty and not expiry.empty and ohlc_ok
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
        headers = {"access-token": token, "client-id": client_id, "Accept": "application/json", "Content-Type": "application/json"}

        profile = requests.get(PROFILE_URL, headers=headers, timeout=25)
        if not profile.ok and auth_method == "totp_refresh":
            fallback_token = os.getenv("DHAN_ACCESS_TOKEN", "").strip()
            if fallback_token and "\n" not in fallback_token and "\r" not in fallback_token:
                headers["access-token"] = fallback_token
                retry = requests.get(PROFILE_URL, headers=headers, timeout=25)
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
            print(result["status"])
            return 0
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
        ids = resolve_ids(master)
        result["resolved_probe_symbols"] = sorted(ids)
        result["missing_probe_symbols"] = sorted(set(PROBE_SYMBOLS) - set(ids))

        if "RELIANCE" in ids:
            daily = requests.post(
                DAILY_URL,
                headers=headers,
                json={
                    "securityId": ids["RELIANCE"],
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

        for symbol, security_id in ids.items():
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
        result["status"] = "PASS_ACTIVE_EQUITIES" if passed == expected else "PARTIAL_OR_BLOCKED"
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
    print(f"Data API plan active: {result.get('data_plan_active')}")
    print(f"Current symbols resolved: {len(result.get('resolved_probe_symbols', []))}; unresolved: {len(result.get('missing_probe_symbols', []))}")
    print(f"Daily history probe: {result.get('daily_history_probe', {}).get('status', 'NOT_RUN')}; bars={result.get('daily_history_probe', {}).get('bar_count', 0)}")
    print(f"Intraday windows passing: {result.get('intraday_probe_passed', 0)}/{result.get('intraday_probe_expected', 0)}")
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
