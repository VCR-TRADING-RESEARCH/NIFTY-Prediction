#!/usr/bin/env python3
"""Private-credential backend for on-demand Dhan -> ExtraTrees predictions.

This service is deployed to a Hugging Face Docker Space by GitHub Actions.
Secrets are runtime environment variables and are never returned to the browser.
"""
from __future__ import annotations

import os
import re
import time
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyotp
import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

HERE = Path(__file__).resolve().parent
ROOT = HERE if (HERE / "research_core.py").exists() else HERE.parent
SCRIPTS = ROOT / "scripts"
import sys
sys.path.insert(0, str(ROOT if (ROOT / "research_core.py").exists() else SCRIPTS))
from research_core import (  # noqa: E402
    FEATURE_COLUMNS, IST, _calculate_features, _day_minutes, _first_anchor,
    _make_model, _prob_up, apply_official_daily_closes, construct_weekly_table,
    daily_aggregates,
)

AUTH_URL = "https://auth.dhan.co/app/generateAccessToken"
INTRADAY_URL = "https://api.dhan.co/v2/charts/intraday"
MASTER_URL = "https://images.dhan.co/api-data/api-scrip-master.csv"
OFFICIAL_CLOSES = ROOT / "data" / "reconciliation" / "nifty50_official_daily.csv"
EXPIRY_CALENDAR = ROOT / "data" / "reconciliation" / "expiry_verification.csv"
CACHE_DIR = Path(os.getenv("DHAN_CACHE_DIR", "/data/nifty-dhan-cache"))
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "https://vcr-trading-research.github.io")
MIN_TRAINING_ROWS = 104
MAX_REQUESTS_PER_HOUR = 6
MAX_CONCURRENT_JOBS = 1

app = FastAPI(title="NIFTY Live ExtraTrees Prediction API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_JOBS)
jobs: dict[str, dict[str, Any]] = {}
jobs_lock = threading.Lock()
cache_lock = threading.Lock()
request_times: dict[str, list[float]] = {}
security_master_cache: tuple[float, pd.DataFrame] | None = None


class PredictRequest(BaseModel):
    as_of_date: str = Field(min_length=8, max_length=10)


class PublicPredictionError(Exception):
    """An expected validation/data failure safe to display to the user."""


def parse_as_of_date(value: str) -> date:
    value = str(value or "").strip()
    formats = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y")
    for fmt in formats:
        try:
            result = datetime.strptime(value, fmt).date()
            if result > pd.Timestamp.now(tz=IST).date():
                raise PublicPredictionError("The as-of date cannot be in the future.")
            if result < date(2019, 2, 1):
                raise PublicPredictionError("The research dataset begins in February 2019.")
            return result
        except ValueError:
            continue
    raise PublicPredictionError("Enter a valid date as YYYY-MM-DD or DD/MM/YYYY, for example 2024-05-10.")


def refresh_dhan_token() -> tuple[str, str]:
    client_id = os.getenv("DHAN_CLIENT_ID", "").strip()
    pin = os.getenv("DHAN_PIN", "").strip()
    totp_secret = os.getenv("DHAN_TOTP_SECRET", "").strip()
    if not all((client_id, pin, totp_secret)):
        raise PublicPredictionError(
            "Dhan live credentials are not configured on the inference service. Check its deployment secrets."
        )
    try:
        otp = pyotp.TOTP(totp_secret).now()
        response = requests.post(
            AUTH_URL,
            params={"dhanClientId": client_id, "pin": pin, "totp": otp},
            timeout=25,
        )
    except requests.RequestException:
        raise PublicPredictionError("Could not reach Dhan's token-refresh service. Please retry.") from None
    if not response.ok:
        raise PublicPredictionError(
            f"Dhan token refresh failed (HTTP {response.status_code}). Check the configured credentials and Dhan authentication."
        )
    try:
        body = response.json()
    except ValueError:
        raise PublicPredictionError("Dhan token service returned an unreadable response.") from None
    token = body.get("accessToken") or body.get("access_token")
    if not isinstance(token, str) or len(token) < 20:
        raise PublicPredictionError("Dhan token service did not return a usable access token.")
    return token, client_id


def find_nifty50_security(master: pd.DataFrame) -> str:
    lookup = {str(column).strip().upper(): column for column in master.columns}
    id_col = next((lookup[k] for k in (
        "SEM_SMST_SECURITY_ID", "SECURITYID", "SECURITY_ID", "SMST_SECURITY_ID"
    ) if k in lookup), None)
    if id_col is None:
        raise PublicPredictionError("Dhan's scrip master has no recognized security-ID field.")
    seg_col = next((lookup[k] for k in ("SEM_SEGMENT", "SEGMENT") if k in lookup), None)
    exchange_col = next((lookup[k] for k in ("SEM_EXM_EXCH_ID", "EXCHANGE") if k in lookup), None)
    text_cols = [lookup[k] for k in lookup if any(
        word in k for word in ("SYMBOL", "INSTRUMENT", "CUSTOM", "NAME")
    )]
    if not text_cols:
        raise PublicPredictionError("Dhan's scrip master has no recognized name/symbol fields.")
    mask = pd.Series(False, index=master.index)
    for column in text_cols:
        mask |= master[column].astype(str).str.upper().str.fullmatch(
            r"\s*NIFTY\s*50(?:\s+INDEX)?\s*", na=False
        )
    if seg_col:
        mask &= master[seg_col].astype(str).str.upper().str.strip().isin(["I", "IDX_I", "IDX"])
    if exchange_col:
        mask &= master[exchange_col].astype(str).str.upper().str.strip().eq("NSE")
    ids = sorted(set(master.loc[mask, id_col].dropna().astype(str).str.strip()) - {""})
    if len(ids) != 1:
        raise PublicPredictionError(
            "Dhan's scrip master did not identify exactly one NSE NIFTY 50 index. Refusing to guess a security ID."
        )
    return ids[0]


def get_security_id() -> str:
    global security_master_cache
    now = time.time()
    with cache_lock:
        if security_master_cache and now - security_master_cache[0] < 86400:
            return find_nifty50_security(security_master_cache[1])
    try:
        response = requests.get(MASTER_URL, timeout=40)
        response.raise_for_status()
        master = pd.read_csv(pd.io.common.BytesIO(response.content), low_memory=False)
    except Exception:
        raise PublicPredictionError("Could not load Dhan's current scrip master to verify the NIFTY 50 security ID.") from None
    with cache_lock:
        security_master_cache = (now, master)
    return find_nifty50_security(master)


def _dhan_chunk(
    security_id: str, token: str, client_id: str, start: date, end: date, refresh_recent: bool
) -> pd.DataFrame:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{security_id}_{start.isoformat()}_{end.isoformat()}.csv"
    today = pd.Timestamp.now(tz=IST).date()
    # Completed old sessions are immutable enough to cache. Re-fetch the current
    # date and the immediately preceding date to capture provider corrections.
    if cache_file.exists() and end < today - timedelta(days=1) and not refresh_recent:
        try:
            cached = pd.read_csv(cache_file)
            if not cached.empty:
                cached["timestamp"] = pd.to_datetime(cached["timestamp"], errors="coerce")
                if getattr(cached["timestamp"].dt, "tz", None) is None:
                    cached["timestamp"] = cached["timestamp"].dt.tz_localize(IST)
                return cached.dropna(subset=["timestamp"])
        except Exception:
            pass

    headers = {
        "access-token": token,
        "client-id": client_id,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    request_body = {
        "securityId": security_id,
        "exchangeSegment": "IDX_I",
        "instrument": "INDEX",
        "interval": "1",
        "oi": False,
        "fromDate": start.isoformat() + " 09:15:00",
        "toDate": end.isoformat() + " 15:30:00",
    }
    try:
        response = requests.post(INTRADAY_URL, headers=headers, json=request_body, timeout=75)
    except requests.RequestException:
        raise PublicPredictionError(f"Dhan intraday request failed for {start} to {end}. Please retry.") from None
    if not response.ok:
        code = response.status_code
        if code in (401, 403):
            detail = "Dhan rejected the refreshed token or this account's historical-data access."
        elif code == 429:
            detail = "Dhan rate-limited the historical-data request. Wait briefly and retry."
        else:
            detail = f"Dhan historical-data API returned HTTP {code}."
        raise PublicPredictionError(f"{detail} Requested date window: {start} to {end}.")
    try:
        body = response.json()
    except ValueError:
        raise PublicPredictionError("Dhan returned an unreadable historical-data response.") from None
    if str(body.get("status", "")).casefold() == "failure":
        raise PublicPredictionError(f"Dhan rejected the intraday data request for {start} to {end}. Check data API permissions.")
    if isinstance(body.get("data"), dict):
        body = body["data"]
    opens = body.get("open", [])
    highs = body.get("high", [])
    lows = body.get("low", [])
    closes = body.get("close", [])
    epochs = body.get("timestamp") or body.get("start_Time") or body.get("startTime") or []
    count = min(len(opens), len(highs), len(lows), len(closes), len(epochs))
    if not count:
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "source_file"])
    stamps = pd.to_datetime(epochs[:count], unit="s", utc=True).tz_convert(IST)
    frame = pd.DataFrame({
        "timestamp": stamps,
        "open": pd.to_numeric(opens[:count], errors="coerce"),
        "high": pd.to_numeric(highs[:count], errors="coerce"),
        "low": pd.to_numeric(lows[:count], errors="coerce"),
        "close": pd.to_numeric(closes[:count], errors="coerce"),
        "source_file": "DhanHQ_v2_intraday",
    })
    if not frame.empty:
        temp = cache_file.with_suffix(".tmp")
        frame.assign(timestamp=frame["timestamp"].astype(str)).to_csv(temp, index=False)
        temp.replace(cache_file)
    return frame


def fetch_dhan_bars(as_of: date, token: str, client_id: str, security_id: str) -> pd.DataFrame:
    now_date = pd.Timestamp.now(tz=IST).date()
    # Dhan documents a five-year intraday history window and 90-day maximum
    # date span per request. Never ask the provider for more than that window.
    provider_floor = now_date - pd.DateOffset(years=5) + pd.Timedelta(days=1)
    user_floor = pd.Timestamp(as_of) - pd.DateOffset(years=5)
    start = max(pd.Timestamp(provider_floor).date(), pd.Timestamp(user_floor).date(), date(2019, 2, 1))
    if start >= as_of:
        raise PublicPredictionError(
            "This date is outside the usable Dhan intraday lookback window. Choose a more recent as-of date."
        )
    frames: list[pd.DataFrame] = []
    cursor = start
    while cursor <= as_of:
        end = min(cursor + timedelta(days=89), as_of)
        # Chunk cache keys are deterministic for repeated requests; refreshing the
        # token is unconditional even if eligible historical chunks are cached.
        frame = _dhan_chunk(security_id, token, client_id, cursor, end, refresh_recent=False)
        if not frame.empty:
            frames.append(frame)
        cursor = end + timedelta(days=1)
    if not frames:
        raise PublicPredictionError("Dhan returned no NIFTY 50 minute bars through the selected date.")
    minutes = pd.concat(frames, ignore_index=True)
    minutes["timestamp"] = pd.to_datetime(minutes["timestamp"], errors="coerce")
    if getattr(minutes["timestamp"].dt, "tz", None) is None:
        minutes["timestamp"] = minutes["timestamp"].dt.tz_localize(IST)
    else:
        minutes["timestamp"] = minutes["timestamp"].dt.tz_convert(IST)
    minutes = minutes.dropna(subset=["timestamp"]).sort_values("timestamp")
    minutes = minutes.drop_duplicates(subset=["timestamp"], keep="last")
    valid = (
        minutes[["open", "high", "low", "close"]].notna().all(axis=1)
        & (minutes[["open", "high", "low", "close"]] > 0).all(axis=1)
        & (minutes["low"] <= minutes[["open", "close"]].min(axis=1))
        & (minutes["high"] >= minutes[["open", "close"]].max(axis=1))
        & (minutes["high"] >= minutes["low"])
    )
    minutes = minutes.loc[valid].copy()
    minutes["session_date"] = minutes["timestamp"].dt.date
    minutes["clock_time"] = minutes["timestamp"].dt.time
    minutes = minutes[
        (minutes["timestamp"].dt.dayofweek < 5)
        & (minutes["clock_time"] >= datetime.strptime("09:15", "%H:%M").time())
        & (minutes["clock_time"] <= datetime.strptime("15:29", "%H:%M").time())
    ].reset_index(drop=True)
    if not len(minutes):
        raise PublicPredictionError("No valid in-session Dhan NIFTY 50 minute bars remain after OHLC checks.")
    return minutes


def _binary_train_table(cycles: pd.DataFrame) -> pd.DataFrame:
    data = cycles.copy()
    data["expiry_date"] = pd.to_datetime(data["expiry_date"], errors="coerce").dt.normalize()
    data["anchor_date"] = pd.to_datetime(data["anchor_date"], errors="coerce").dt.normalize()
    data["target"] = data["label"].map({"DOWN": 0, "UP": 1, "FLAT": np.nan})
    data = data.loc[data["target"].notna()].copy()
    data["target"] = data["target"].astype(int)
    complete = data[FEATURE_COLUMNS].notna().sum(axis=1) >= len(FEATURE_COLUMNS) - 2
    return data.loc[complete].sort_values("expiry_date").reset_index(drop=True)


def _first_official_session_after(previous_expiry: pd.Timestamp, official_path: Path = OFFICIAL_CLOSES) -> pd.Timestamp:
    """Return the first official NSE trading session after an expiry date."""
    try:
        official_sessions = pd.read_csv(official_path, usecols=["session_date"])
        session_dates = pd.to_datetime(official_sessions["session_date"], errors="coerce")
        session_dates = session_dates.dropna().dt.normalize().drop_duplicates().sort_values()
    except Exception:
        raise PublicPredictionError("Could not read the official NSE session calendar. Refusing to infer the next session from minute-data gaps.") from None
    candidates = session_dates.loc[session_dates > pd.Timestamp(previous_expiry).normalize()]
    if candidates.empty:
        raise PublicPredictionError("The official NSE session calendar has no session after the preceding verified expiry.")
    return pd.Timestamp(candidates.iloc[0]).normalize()


def _do_prediction(as_of: date) -> dict[str, Any]:
    token, client_id = refresh_dhan_token()
    security_id = get_security_id()
    minutes = fetch_dhan_bars(as_of, token, client_id, security_id)
    if not OFFICIAL_CLOSES.is_file():
        raise PublicPredictionError("Official NSE daily-close reference data is missing on the inference service.")
    if not EXPIRY_CALENDAR.is_file():
        raise PublicPredictionError("The verified expiry calendar is missing on the inference service.")

    daily = daily_aggregates(minutes)
    daily, official_quality = apply_official_daily_closes(daily, OFFICIAL_CLOSES)
    cycles, calendar, construction_report = construct_weekly_table(minutes, daily, EXPIRY_CALENDAR)
    as_of_ts = pd.Timestamp(as_of).normalize()

    # The chosen date must be the first session after the preceding verified expiry.
    events = calendar.copy()
    events["resolved_expiry"] = pd.to_datetime(events["resolved_expiry"], errors="coerce").dt.normalize()
    events["nominal_expiry"] = pd.to_datetime(events["nominal_expiry"], errors="coerce").dt.normalize()
    verified = events.loc[
        events.get("calendar_verified", pd.Series(False, index=events.index)).astype(bool)
        & events["resolved_expiry"].notna()
    ].sort_values("resolved_expiry").drop_duplicates("resolved_expiry")
    prior_events = verified.loc[verified["resolved_expiry"] < as_of_ts]
    if prior_events.empty:
        raise PublicPredictionError("No verified prior expiry is available for this as-of date.")
    prior_event = prior_events.iloc[-1]
    previous_expiry = pd.Timestamp(prior_event["resolved_expiry"]).normalize()
    # Use the official session calendar; Dhan minute-bar coverage is validated separately.
    expected_next_session = _first_official_session_after(previous_expiry)
    if expected_next_session != as_of_ts:
        raise PublicPredictionError(
            "This date is not the first NSE trading session after the previous verified NIFTY weekly expiry. "
            f"The preceding verified expiry is {previous_expiry.date()}; the official NSE calendar next session is {expected_next_session.date()}."
        )

    anchor_day = _day_minutes(minutes, as_of_ts)
    anchor_bar = _first_anchor(anchor_day)
    if anchor_bar is None:
        raise PublicPredictionError(
            "Dhan has no valid 10:00–10:03 IST NIFTY 50 minute bar for the selected date."
        )
    target_events = verified.loc[verified["resolved_expiry"] > previous_expiry].sort_values("resolved_expiry")
    if target_events.empty:
        raise PublicPredictionError("No subsequent verified expiry is listed in the repository calendar.")
    target_event = target_events.iloc[0]
    target_expiry = pd.Timestamp(target_event["resolved_expiry"]).normalize()
    if target_expiry <= as_of_ts:
        raise PublicPredictionError("The next verified expiry is not later than the selected anchor date.")

    cycles["expiry_normalized"] = pd.to_datetime(cycles["expiry_date"], errors="coerce").dt.normalize()
    previous_cycle_rows = cycles.loc[cycles["expiry_normalized"].eq(previous_expiry)]
    if previous_cycle_rows.empty:
        raise PublicPredictionError(
            "The preceding expiry has no complete Dhan-backed training label. The selected date cannot be evaluated safely."
        )
    previous_cycle = previous_cycle_rows.sort_values("expiry_normalized").iloc[-1]
    train = _binary_train_table(cycles)
    train = train.loc[
        train["expiry_date"].le(previous_expiry)
        & train["expiry_date"].lt(as_of_ts)
    ].copy()
    if len(train) < MIN_TRAINING_ROWS:
        raise PublicPredictionError(
            f"Only {len(train)} eligible completed weekly labels are available from the Dhan history; "
            f"at least {MIN_TRAINING_ROWS} are required. Choose a later as-of date."
        )
    if train["expiry_date"].max() >= as_of_ts:
        raise PublicPredictionError("Leakage check failed: a training expiry label reaches the selected anchor date.")
    anchor_price = float(anchor_bar["open"])
    if not np.isfinite(anchor_price) or anchor_price <= 0:
        raise PublicPredictionError("Dhan's selected 10:00 anchor price is missing or invalid.")
    anchor_row = pd.Series({
        "anchor_price": anchor_price,
        "anchor_timestamp": anchor_bar["timestamp"],
    })
    features = _calculate_features(
        daily=daily,
        minutes=minutes,
        anchor_date=as_of_ts,
        anchor_row=anchor_row,
        previous_cycle_return=float(previous_cycle["return_pct"]),
        previous_cycle_label=str(previous_cycle["label"]),
        previous_expiry=previous_expiry,
    )
    test_x = pd.DataFrame([{column: features.get(column, np.nan) for column in FEATURE_COLUMNS}])
    observed_features = int(test_x[FEATURE_COLUMNS].notna().sum(axis=1).iloc[0])
    if observed_features < len(FEATURE_COLUMNS) - 2:
        raise PublicPredictionError(
            f"Only {observed_features} of {len(FEATURE_COLUMNS)} required model features are available at this cutoff."
        )
    if train["target"].nunique() < 2:
        raise PublicPredictionError("The available training labels contain only one direction class; cannot fit ExtraTrees.")
    model = _make_model("extra_trees")
    model.fit(train[FEATURE_COLUMNS], train["target"].astype(int).to_numpy())
    p_up = float(_prob_up(model, test_x[FEATURE_COLUMNS]))
    if not np.isfinite(p_up) or not 0 <= p_up <= 1:
        raise PublicPredictionError("The ExtraTrees model produced an invalid score.")
    trained_through = pd.Timestamp(train["expiry_date"].max()).date().isoformat()
    return {
        "as_of_date": as_of.isoformat(),
        "as_of_time_ist": pd.Timestamp(anchor_bar["timestamp"]).strftime("%H:%M"),
        "target_expiry_date": target_expiry.date().isoformat(),
        "direction": "UP" if p_up >= 0.5 else "DOWN",
        "p_up": p_up,
        "training_rows": int(len(train)),
        "trained_through_expiry_date": trained_through,
        "prediction_kind": "LIVE_DHAN_POINT_IN_TIME",
        "data_source": "DhanHQ v2 one-minute NIFTY 50 index bars; official NSE daily closes for completed training labels",
        "security_id": security_id,
        "bars_used": int(len(minutes)),
        "data_from": pd.Timestamp(minutes["timestamp"].min()).isoformat(),
        "data_through": pd.Timestamp(minutes["timestamp"].max()).isoformat(),
        "anchor_price": anchor_price,
        "anchor_source": "DhanHQ v2 intraday minute bar; independent anchor reconciliation not passed",
        "data_quality": {
            "status": "BLOCKED",
            "detail": "Fresh Dhan inference completed, but independent 10:00 anchor validation and executable-cost validation remain incomplete.",
            "official_close_sessions_matched": official_quality.get("official_sessions_matched"),
            "training_rows_leakage_check": "PASS",
            "features_available": observed_features,
            "features_total": len(FEATURE_COLUMNS),
            "target_calendar_status": str(target_event.get("calendar_status", "verified_expiry_calendar")),
        },
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "note": "ExtraTrees was fit again for this request. This is a spot-direction classification, not a calibrated probability, options P&L or trading instruction.",
    }


def _run_job(job_id: str, as_of: date) -> None:
    with jobs_lock:
        jobs[job_id]["status"] = "running"
        jobs[job_id]["started_at_utc"] = datetime.now(timezone.utc).isoformat()
    try:
        result = _do_prediction(as_of)
        with jobs_lock:
            jobs[job_id]["status"] = "succeeded"
            jobs[job_id]["result"] = result
            jobs[job_id]["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    except PublicPredictionError as exc:
        with jobs_lock:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = str(exc)
            jobs[job_id]["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    except Exception as exc:
        # Do not log a traceback with request URLs, token values or provider payloads.
        with jobs_lock:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = (
                "Live inference encountered an internal data/model error (" + type(exc).__name__ +
                "). Sensitive details were withheld; check service deployment logs."
            )
            jobs[job_id]["finished_at_utc"] = datetime.now(timezone.utc).isoformat()


def _client_key(request: Request) -> str:
    # Prefer proxy headers normally overwritten by the edge. Avoid trusting a
    # caller-supplied leftmost X-Forwarded-For value for quota enforcement.
    value = request.headers.get("cf-connecting-ip") or request.headers.get("x-real-ip")
    if not value and request.client is not None:
        value = request.client.host
    return (value or "unknown").strip()[:80] or "unknown"


@app.get("/health")
def health() -> dict[str, Any]:
    missing = [key for key in ("DHAN_CLIENT_ID", "DHAN_PIN", "DHAN_TOTP_SECRET") if not os.getenv(key)]
    return {
        "status": "ready" if not missing else "missing_configuration",
        "provider": "DhanHQ v2",
        "missing_configuration": missing,
        "model": "scikit-learn ExtraTreesClassifier",
        "secrets_exposed": False,
    }


@app.post("/predict")
def create_prediction(request_body: PredictRequest, request: Request) -> dict[str, str]:
    try:
        as_of = parse_as_of_date(request_body.as_of_date)
    except PublicPredictionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    if request.headers.get("origin", "") != ALLOWED_ORIGIN:
        raise HTTPException(status_code=403, detail="This prediction endpoint only accepts requests from the NIFTY Prediction page.")
    client = _client_key(request)
    now = time.time()
    with jobs_lock:
        recent = [stamp for stamp in request_times.get(client, []) if now - stamp < 3600]
        if len(recent) >= MAX_REQUESTS_PER_HOUR:
            raise HTTPException(status_code=429, detail="Too many prediction requests. Please wait before retrying.")
        request_times[client] = recent + [now]
        active = sum(job["status"] in ("queued", "running") for job in jobs.values())
        if active >= MAX_CONCURRENT_JOBS:
            raise HTTPException(status_code=429, detail="A live Dhan prediction is already running. Retry in a moment.")
        if len(jobs) > 200:
            for old_id in list(jobs)[:100]:
                if jobs[old_id]["status"] not in ("queued", "running"):
                    jobs.pop(old_id, None)
        job_id = uuid.uuid4().hex
        jobs[job_id] = {
            "status": "queued",
            "as_of_date": as_of.isoformat(),
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        }
    executor.submit(_run_job, job_id, as_of)
    return {"job_id": job_id, "status": "queued", "as_of_date": as_of.isoformat()}


@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Prediction request expired or was not found. Submit it again.")
        return {"job_id": job_id, **job}
