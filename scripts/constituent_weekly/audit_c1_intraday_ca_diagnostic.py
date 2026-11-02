from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from live_api.app import MASTER_URL
from scripts.constituent_weekly.audit_c1_daily_history import (
    parse_daily_payload,
    request_daily_history,
)
from scripts.constituent_weekly.dhan_equity_preflight import (
    INTRADAY_URL,
    acquire_access_token,
    request_profile,
    resolve_ids,
)

OUT_JSON = ROOT / "research/constituent_weekly/C1_DHAN_INTRADAY_CA_DIAGNOSTIC.json"
OUT_MD = ROOT / "research/constituent_weekly/C1_DHAN_INTRADAY_CA_DIAGNOSTIC.md"
IST = ZoneInfo("Asia/Kolkata")
TIMEOUT_SECONDS = 90

# Each event has already been adjudicated from issuer/exchange evidence.
# The ratios are price-scale factors expected for the first ex-date session.
EVENTS = (
    {
        "symbol": "RELIANCE",
        "pre_date": "2024-10-25",
        "ex_date": "2024-10-28",
        "expected_price_factor": 0.5,
        "action": "1:1 bonus",
    },
    {
        "symbol": "BAJAJFINSV",
        "pre_date": "2022-09-12",
        "ex_date": "2022-09-13",
        "expected_price_factor": 0.1,
        "action": "5:1 split plus 1:1 bonus",
    },
)


def classify_intraday_scale(post_pre_ratio: float, expected_factor: float) -> str:
    """Classify whether an intraday series retains the ex-date price-scale jump."""
    if not np.isfinite(post_pre_ratio) or post_pre_ratio <= 0:
        return "INVALID_RATIO"
    if not np.isfinite(expected_factor) or not 0 < expected_factor < 0.8:
        return "INVALID_EXPECTED_FACTOR"
    raw_low, raw_high = expected_factor * 0.75, expected_factor * 1.25
    if raw_low <= post_pre_ratio <= raw_high:
        return "RAW_SCALE_UNADJUSTED_INTRADAY"
    if 0.80 <= post_pre_ratio <= 1.25:
        return "ADJUSTED_SCALE_INTRADAY"
    return "AMBIGUOUS_GAP_OR_SCALE"


def parse_intraday_payload(body: object) -> tuple[pd.DataFrame | None, str | None]:
    if not isinstance(body, dict):
        return None, "INVALID_RESPONSE_SHAPE"
    if str(body.get("status", "")).casefold() == "failure":
        return None, "PROVIDER_FAILURE"
    payload = body.get("data") if isinstance(body.get("data"), dict) else body
    timestamps = payload.get("timestamp")
    if timestamps is None:
        timestamps = payload.get("start_Time")
    if timestamps is None:
        timestamps = payload.get("startTime")
    fields = {
        "timestamp": timestamps,
        "open": payload.get("open"),
        "high": payload.get("high"),
        "low": payload.get("low"),
        "close": payload.get("close"),
    }
    if any(not isinstance(v, list) for v in fields.values()):
        return None, "MISSING_REQUIRED_ARRAY"
    lengths = {len(v) for v in fields.values()}
    if len(lengths) != 1:
        return None, "ARRAY_LENGTH_MISMATCH"
    if not lengths or next(iter(lengths)) == 0:
        return pd.DataFrame(columns=["timestamp", "session_date", "clock", "open", "high", "low", "close"]), "NO_BARS"

    frame = pd.DataFrame({
        "timestamp": pd.to_datetime(fields["timestamp"], unit="s", utc=True, errors="coerce"),
        **{k: pd.to_numeric(fields[k], errors="coerce") for k in ("open", "high", "low", "close")},
    })
    frame = frame.dropna(subset=["timestamp"]).copy()
    frame["timestamp"] = frame["timestamp"].dt.tz_convert(IST)
    frame["session_date"] = frame["timestamp"].dt.strftime("%Y-%m-%d")
    frame["clock"] = frame["timestamp"].dt.strftime("%H:%M")
    frame = frame.sort_values("timestamp")
    if frame.empty:
        return None, "NO_VALID_TIMESTAMPS"
    values = frame[["open", "high", "low", "close"]].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values <= 0).any():
        return None, "INVALID_OHLC_VALUES"
    low = frame["low"].to_numpy(dtype=float)
    high = frame["high"].to_numpy(dtype=float)
    open_ = frame["open"].to_numpy(dtype=float)
    close = frame["close"].to_numpy(dtype=float)
    if (low > np.minimum(open_, close)).any() or (high < np.maximum(open_, close)).any() or (high < low).any():
        return None, "INVALID_OHLC_RELATION"
    return frame, None


def inspect_event_scale(frame: pd.DataFrame, event: dict) -> dict:
    pre = frame.loc[
        frame["session_date"].eq(event["pre_date"])
        & frame["clock"].between("15:10", "15:14", inclusive="both")
    ]
    post = frame.loc[
        frame["session_date"].eq(event["ex_date"])
        & frame["clock"].between("09:15", "09:19", inclusive="both")
    ]
    if pre.empty or post.empty:
        return {
            "status": "INSUFFICIENT_PRE_POST_BARS",
            "pre_window_bars": int(len(pre)),
            "post_window_bars": int(len(post)),
        }
    pre_level = float(pre["close"].median())
    post_level = float(post["close"].median())
    if not np.isfinite(pre_level) or not np.isfinite(post_level) or pre_level <= 0 or post_level <= 0:
        return {"status": "INVALID_PRICE_LEVEL"}
    ratio = post_level / pre_level
    classification = classify_intraday_scale(ratio, float(event["expected_price_factor"]))
    return {
        "status": classification,
        "pre_window_bars": int(len(pre)),
        "post_window_bars": int(len(post)),
        "post_pre_median_close_ratio": round(float(ratio), 6),
        "expected_raw_price_factor": float(event["expected_price_factor"]),
        "classification_note": (
            "RAW_SCALE means pre-ex bars remain on the cum-event price scale relative to first ex-date bars; "
            "ADJUSTED_SCALE means the two sessions are approximately continuous on a common price scale. "
            "The overnight market move is not removed, so borderline cases remain ambiguous."
        ),
    }



def classify_intraday_vs_daily_scale(
    pre_ratios: dict[str, float],
    ex_ratios: dict[str, float],
    expected_factor: float,
) -> str:
    """Compare same-session intraday OHLC aggregates with Dhan's adjusted daily OHLC."""
    fields = ("open", "high", "low", "close")
    if not 0 < expected_factor < 0.8:
        return "INVALID_EXPECTED_FACTOR"
    if any(
        field not in pre_ratios or field not in ex_ratios
        or not np.isfinite(pre_ratios[field]) or not np.isfinite(ex_ratios[field])
        or pre_ratios[field] <= 0 or ex_ratios[field] <= 0
        for field in fields
    ):
        return "INVALID_ENDPOINT_RATIO"
    adjusted = all(
        0.80 <= pre_ratios[field] <= 1.20
        and 0.80 <= ex_ratios[field] <= 1.20
        for field in fields
    )
    if adjusted:
        return "INTRADAY_MATCHES_DHAN_DAILY_ADJUSTED_SCALE"
    raw_pre_factor = 1.0 / expected_factor
    raw = all(
        raw_pre_factor * 0.80 <= pre_ratios[field] <= raw_pre_factor * 1.20
        and 0.80 <= ex_ratios[field] <= 1.20
        for field in fields
    )
    if raw:
        return "INTRADAY_RAW_SCALE_VS_DAILY_ADJUSTED"
    return "AMBIGUOUS_INTRADAY_DAILY_SCALE"


def compare_intraday_with_daily(
    intraday: pd.DataFrame,
    daily: pd.DataFrame,
    event: dict,
) -> dict:
    per_date = {}
    for day in (event["pre_date"], event["ex_date"]):
        intraday_day = intraday.loc[intraday["session_date"].eq(day)].sort_values("timestamp")
        daily_day = daily.loc[daily["session_date"].astype(str).eq(day)]
        if intraday_day.empty or len(daily_day) != 1:
            return {
                "status": "INSUFFICIENT_DAILY_INTRADAY_SESSION_MATCH",
                "pre_intraday_bars": int(len(intraday.loc[intraday["session_date"].eq(event["pre_date"])])),
                "ex_intraday_bars": int(len(intraday.loc[intraday["session_date"].eq(event["ex_date"])])),
                "daily_session_rows": int(len(daily_day)),
            }
        first, last = intraday_day.iloc[0], intraday_day.iloc[-1]
        intraday_ohlc = {
            "open": float(first["open"]),
            "high": float(intraday_day["high"].max()),
            "low": float(intraday_day["low"].min()),
            "close": float(last["close"]),
        }
        daily_row = daily_day.iloc[0]
        daily_ohlc = {field: float(daily_row[field]) for field in ("open", "high", "low", "close")}
        if any(not np.isfinite(v) or v <= 0 for v in (*intraday_ohlc.values(), *daily_ohlc.values())):
            return {"status": "INVALID_DAILY_INTRADAY_OHLC"}
        per_date[day] = {
            field: round(intraday_ohlc[field] / daily_ohlc[field], 6)
            for field in ("open", "high", "low", "close")
        }
    classification = classify_intraday_vs_daily_scale(
        per_date[event["pre_date"]], per_date[event["ex_date"]], float(event["expected_price_factor"])
    )
    return {
        "status": classification,
        "pre_intraday_to_daily_adjusted_ohlc_ratios": per_date[event["pre_date"]],
        "ex_intraday_to_daily_adjusted_ohlc_ratios": per_date[event["ex_date"]],
        "comparison_method": "same-session intraday OHLC aggregation / Dhan adjusted daily historical OHLC",
        "note": "This avoids the overnight return in a pre-close to ex-open ratio. Dhan daily OHLC is the adjusted-scale comparator; same-session scale matching is evidence for the sampled symbol/event only.",
    }

def fetch_event(token: str, client_id: str, security_id: str, event: dict) -> dict:
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
        "interval": "1",
        "oi": False,
        "fromDate": f'{event["pre_date"]} 09:15:00',
        "toDate": f'{event["ex_date"]} 15:15:00',
    }
    response = requests.post(INTRADAY_URL, headers=headers, json=payload, timeout=TIMEOUT_SECONDS)
    if response.status_code in (401, 403):
        raise RuntimeError(f"Dhan intraday authorization failed: HTTP {response.status_code}")
    if not response.ok:
        return {"status": f"DHAN_HTTP_{response.status_code}"}
    body = response.json()
    frame, error = parse_intraday_payload(body)
    if frame is None:
        return {"status": error or "INVALID_INTRADAY_DATA"}
    daily_body, daily_attempts = request_daily_history(
        security_id, token, client_id, event["pre_date"],
        (pd.Timestamp(event["ex_date"]) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    )
    daily_frame, daily_error = parse_daily_payload(daily_body)
    if daily_frame is None or daily_frame.empty:
        return {
            "status": "DAILY_ADJUSTED_COMPARATOR_UNAVAILABLE",
            "daily_parse_error": daily_error,
            "daily_request_attempts": int(daily_attempts),
            "bar_count": int(len(frame)),
        }
    intraday_daily = compare_intraday_with_daily(frame, daily_frame, event)
    overnight_diagnostic = inspect_event_scale(frame, event)
    return {
        **intraday_daily,
        "bar_count": int(len(frame)),
        "daily_request_attempts": int(daily_attempts),
        "overnight_close_ratio_diagnostic": overnight_diagnostic.get("post_pre_median_close_ratio"),
        "overnight_diagnostic_status": overnight_diagnostic.get("status"),
    }


def run() -> dict:
    result = {
        "status": "BLOCKED",
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "data_source": "DhanHQ v2 intraday historical API",
        "raw_bars_published": False,
        "credentials_or_tokens_recorded": False,
        "events": [],
    }
    shared_token = os.environ.get("DHAN_EPHEMERAL_ACCESS_TOKEN", "").strip()
    client_id = os.environ.get("DHAN_CLIENT_ID", "").strip()
    if shared_token:
        token = shared_token
        auth_method = "reused_validated_prior_step_token"
        refresh_status = "REUSED_WITHIN_SAME_ACTIONS_JOB"
        auth_diagnostics = {"token_value_recorded": False, "source": "prior_profile_and_data_plan_validated_step"}
    else:
        token, client_id, auth_method, refresh_status, auth_diagnostics = acquire_access_token()
    result["auth_method"] = auth_method
    result["token_refresh_status"] = refresh_status
    result["token_refresh_diagnostics"] = auth_diagnostics
    if not token or not client_id:
        result["status"] = "BLOCKED_TOKEN_OR_CLIENT_ID_MISSING"
        return result
    # When reused, the preceding protected step already validated this token against profile and data-plan APIs.
    if not shared_token:
        profile = request_profile(token)
        if not profile.ok:
            result["status"] = f"BLOCKED_PROFILE_HTTP_{profile.status_code}"
            return result
    master_response = requests.get(MASTER_URL, timeout=45)
    master_response.raise_for_status()
    master = pd.read_csv(BytesIO(master_response.content), low_memory=False)
    ids = resolve_ids(master, [e["symbol"] for e in EVENTS])
    for event in EVENTS:
        row = {"symbol": event["symbol"], "action": event["action"], "pre_date": event["pre_date"], "ex_date": event["ex_date"]}
        security_id = ids.get(event["symbol"])
        if not security_id:
            row["diagnostic"] = {"status": "SECURITY_ID_NOT_RESOLVED"}
        else:
            row["diagnostic"] = fetch_event(token, client_id, security_id, event)
        result["events"].append(row)

    statuses = [e.get("diagnostic", {}).get("status") for e in result["events"]]
    accepted_statuses = ("INTRADAY_MATCHES_DHAN_DAILY_ADJUSTED_SCALE", "INTRADAY_RAW_SCALE_VS_DAILY_ADJUSTED")
    if len(statuses) == len(EVENTS) and all(s in accepted_statuses for s in statuses):
        result["status"] = "COMPLETED_INTRADAY_SCALE_DIAGNOSTIC"
    else:
        result["status"] = "PARTIAL_OR_BLOCKED"
    result["summary"] = {
        "events_tested": len(result["events"]),
        "raw_scale_unadjusted": sum(s == "INTRADAY_RAW_SCALE_VS_DAILY_ADJUSTED" for s in statuses),
        "matches_daily_adjusted_scale": sum(s == "INTRADAY_MATCHES_DHAN_DAILY_ADJUSTED_SCALE" for s in statuses),
        "ambiguous_or_unavailable": sum(s not in accepted_statuses for s in statuses),
    }
    return result


def write_report(result: dict) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Dhan Intraday Corporate-Action Scale Diagnostic",
        "",
        f'**Updated:** {result.get("updated_at_utc")}',
        f'**Status:** {result.get("status")}',
        "",
        "Primary test: aggregate the full Dhan intraday session OHLC for the last cum-event day and ex-date, then compare each same-session OHLC field with Dhan daily adjusted historical OHLC for that exact date. This removes the overnight return from the scale comparison.",
        "A pre-event intraday/daily ratio near 1 indicates a common adjusted scale. A pre-event ratio near the reciprocal of the documented event factor (2x for a 1:1 bonus; 10x for the combined 5:1 split + 1:1 bonus) indicates intraday bars remain unadjusted while daily OHLC is adjusted. Ex-date ratios should remain near 1 in either case.",
        "",
        "| Symbol | Action | Ex-date | Pre intraday/daily OHLC ratios | Ex-date intraday/daily OHLC ratios | Diagnostic |",
        "|---|---|---|---:|---:|---|",
    ]
    for row in result.get("events", []):
        d = row.get("diagnostic", {})
        lines.append(
            f'| {row.get("symbol")} | {row.get("action")} | {row.get("ex_date")} | '
            f'{d.get("pre_intraday_to_daily_adjusted_ohlc_ratios", "—")} | '
            f'{d.get("ex_intraday_to_daily_adjusted_ohlc_ratios", "—")} | {d.get("status", "—")} |'
        )
    lines += [
        "",
        "## Scope and limitations",
        "",
        "- Only two issuer/exchange-adjudicated events are tested: one bonus and one combined split/bonus.",
        "- The same-session comparison removes the overnight gap, but remains a diagnostic on only two known events rather than a complete intraday adjustment audit.",
        "- No raw OHLC values, security IDs, access tokens or credentials are published.",
        "- A result does not establish adjustment behavior for all instruments, other event classes or all historical dates.",
        "- The daily endpoint is the adjusted-scale comparator for this test; source-specific intraday adjustment still requires broader independent event coverage.",
        "- If intraday bars are unadjusted, affected weekly stock-return windows must be adjusted using independently verified event factors or excluded before confirmatory fitting.",
        "- Dhan's published support statement explicitly covers **daily** historical OHLCV adjustment for bonuses/splits; its intraday API documentation specifies minute bars and a five-year window but does not state an equivalent corporate-action adjustment guarantee.",
        "",
        "## Official Dhan documentation",
        "",
        "- Daily historical adjustment statement: https://dhan.co/support/platforms/dhanhq-api/is-the-historical-data-from-dhan-s-data-api-adjusted-for-corporate-actions-like-bonuses-and-splits/",
        "- Intraday historical data documentation: https://dhanhq.co/docs/v2/historical-data/",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    try:
        result = run()
    except Exception as exc:
        result = {
            "status": "BLOCKED_RUNTIME_ERROR",
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            "raw_bars_published": False,
            "credentials_or_tokens_recorded": False,
            "error_type": type(exc).__name__,
            "events": [],
        }
    write_report(result)
    print("C1_DHAN_INTRADAY_CA_STATUS", result["status"])
    for row in result.get("events", []):
        d = row.get("diagnostic", {})
        print("C1_DHAN_INTRADAY_EVENT", row.get("symbol"), row.get("ex_date"), d.get("status"), d.get("post_pre_median_close_ratio"))
    # Diagnostic status is retained in the report; ambiguous observations do not abort report publication.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
