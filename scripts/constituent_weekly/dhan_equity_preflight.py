from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

from live_api.app import MASTER_URL, PublicPredictionError, refresh_dhan_token

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "research" / "constituent_weekly" / "C1_DHAN_PREFLIGHT.json"
PROFILE_URL = "https://api.dhan.co/v2/profile"
INTRADAY_URL = "https://api.dhan.co/v2/charts/intraday"
DAILY_URL = "https://api.dhan.co/v2/charts/historical"
PROBE_SYMBOLS = ("RELIANCE", "TCS", "INFY", "HDFCBANK", "WIPRO")
PROBE_DATES = ("2022-10-31", "2026-10-30")
IST = "Asia/Kolkata"


def write_result(data: dict) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


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
        token, client_id = refresh_dhan_token()
        headers = {"access-token": token, "client-id": client_id, "Accept": "application/json", "Content-Type": "application/json"}

        profile = requests.get(PROFILE_URL, headers=headers, timeout=25)
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
    print(f"Intraday windows passing: {result.get('intraday_probe_passed', 0)}/{result.get('intraday_probe_expected', 0)}")
    print("No raw bars, prices, security IDs, tokens, PINs or TOTP values were saved or logged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
