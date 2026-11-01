from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from live_api.app import MASTER_URL, PublicPredictionError
from scripts.constituent_weekly.dhan_equity_preflight import (
    IST, INTRADAY_URL, PROFILE_URL, acquire_access_token, resolve_ids,
)

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "research" / "constituent_weekly" / "C1_SHREECEM_EDGE_DIAGNOSTIC.json"
START_DATE = "2021-11-01"
END_DATE = "2022-01-29"
SYMBOL = "SHREECEM"
SPECIAL_SESSION_DATES = {"2021-11-04", "2022-10-24"}


def negative_volume_diagnostics(body: dict, start_date: str, end_date: str) -> dict:
    """Return timestamps/counts for negative finite volumes; never return market values."""
    keys = ("open", "high", "low", "close", "volume", "timestamp")
    arrays = {key: body.get(key, []) for key in keys}
    lengths = {key: len(value) for key, value in arrays.items()}
    count = lengths["timestamp"]
    if count == 0 or any(length != count for length in lengths.values()):
        return {"status": "EMPTY_OR_MISMATCHED_ARRAYS", "array_lengths": lengths}

    frame = pd.DataFrame(arrays)
    frame["time_ist"] = pd.to_datetime(
        frame["timestamp"], unit="s", utc=True, errors="coerce"
    ).dt.tz_convert(IST)
    frame = frame.dropna(subset=["time_ist"]).sort_values("time_ist")
    day = frame["time_ist"].dt.strftime("%Y-%m-%d")
    clock = frame["time_ist"].dt.strftime("%H:%M")
    regular = clock.between("09:15", "15:30") & ~day.isin(SPECIAL_SESSION_DATES)
    regular_frame = frame.loc[regular].copy()
    volume = pd.to_numeric(regular_frame["volume"], errors="coerce")
    finite = volume.notna() & np.isfinite(volume.to_numpy(dtype=float))
    negative = finite & volume.lt(0)
    timestamps = regular_frame.loc[negative, "time_ist"].dt.isoformat().tolist()
    in_range = (
        regular_frame["time_ist"].dt.strftime("%Y-%m-%d").between(start_date, end_date)
    )
    negative &= in_range
    timestamps = regular_frame.loc[negative, "time_ist"].dt.isoformat().tolist()
    return {
        "status": "NEGATIVE_VOLUME_ROWS_FOUND" if timestamps else "NO_NEGATIVE_VOLUME",
        "regular_session_rows": int(len(regular_frame)),
        "finite_volume_rows": int(finite.sum()),
        "negative_volume_row_count": int(negative.sum()),
        "negative_volume_timestamps_ist": timestamps[:20],
        "special_session_dates_excluded": sorted(set(day[day.isin(SPECIAL_SESSION_DATES)])),
        "contains_raw_price_or_volume_values": False,
    }


def write_result(result: dict) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    result = {
        "track": "BUP-01",
        "symbol": SYMBOL,
        "date_range": {"from": START_DATE, "to": END_DATE},
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "credentials_or_tokens_recorded": False,
        "raw_market_bars_saved": False,
    }
    try:
        token, client_id, auth_method, refresh_status, auth_diagnostics = acquire_access_token()
        result.update({
            "auth_method": auth_method,
            "token_refresh_status": refresh_status,
            "token_refresh_diagnostics": auth_diagnostics,
        })
        profile = requests.get(
            PROFILE_URL,
            headers={"access-token": token, "Accept": "application/json"},
            timeout=25,
        )
        result["profile_http_status"] = int(profile.status_code)
        if not profile.ok:
            result["status"] = "BLOCKED_PROFILE_AUTH"
            write_result(result)
            return 0
        profile_body = profile.json()
        result["data_plan_active"] = str(profile_body.get("dataPlan", "")).strip().casefold() == "active"
        if not result["data_plan_active"]:
            result["status"] = "BLOCKED_DATA_PLAN"
            write_result(result)
            return 0

        master_response = requests.get(MASTER_URL, timeout=45)
        master_response.raise_for_status()
        master = pd.read_csv(pd.io.common.BytesIO(master_response.content), low_memory=False)
        ids = resolve_ids(master, [SYMBOL])
        result["security_id_resolved"] = SYMBOL in ids
        if SYMBOL not in ids:
            result["status"] = "BLOCKED_SECURITY_ID_NOT_RESOLVED"
            write_result(result)
            return 0

        response = requests.post(
            INTRADAY_URL,
            headers={
                "access-token": token,
                "client-id": client_id,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json={
                "securityId": ids[SYMBOL],
                "exchangeSegment": "NSE_EQ",
                "instrument": "EQUITY",
                "interval": "1",
                "oi": False,
                "fromDate": f"{START_DATE} 09:15:00",
                "toDate": f"{END_DATE} 15:15:00",
            },
            timeout=120,
        )
        result["intraday_http_status"] = int(response.status_code)
        if not response.ok:
            result["status"] = "BLOCKED_INTRADAY_HTTP"
            write_result(result)
            return 0

        qa = negative_volume_diagnostics(response.json(), START_DATE, END_DATE)
        result["volume_diagnostic"] = qa
        result["status"] = qa.get("status", "DIAGNOSTIC_FAILED")
    except PublicPredictionError as exc:
        result["status"] = "BLOCKED_DHAN_AUTH"
        result["sanitised_error"] = str(exc)[:160]
    except requests.RequestException as exc:
        result["status"] = "BLOCKED_PROVIDER_OR_NETWORK"
        result["sanitised_error_type"] = type(exc).__name__
    except Exception as exc:
        result["status"] = "BLOCKED_DIAGNOSTIC_ERROR"
        result["sanitised_error_type"] = type(exc).__name__

    result["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_result(result)
    print(json.dumps({k: v for k, v in result.items() if k != "token_refresh_diagnostics"}, sort_keys=True))
    print("No raw bars, prices, volumes, security IDs or credentials were saved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
