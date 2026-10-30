#!/usr/bin/env python3
"""Collect Dhan rolling expired NIFTY options data for reproducible research.

The endpoint returns ATM-relative strikes, not a static contract chain. Every row
retains expiry_code and relative_strike; an independently verified expiry calendar
must map those codes to actual expiry dates before contract-level simulation.
Raw data stays in the Actions cache and is never committed to Git.
"""
from __future__ import annotations
import json, os, sys, time, hashlib
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import pandas as pd
import requests

URL = "https://api.dhan.co/v2/charts/rollingoption"
OUT = Path(os.getenv("DHAN_OPTIONS_CACHE", ".cache/dhan-options"))
FIELDS = ["open", "high", "low", "close", "iv", "volume", "strike", "oi", "spot"]
OFFSETS = range(-10, 11)
EXPIRY_CODES = (0, 1)
OPTION_TYPES = ("CALL", "PUT")
IST = "Asia/Kolkata"

def chunks(start: date, end_exclusive: date):
    cur = start
    while cur < end_exclusive:
        nxt = min(cur + timedelta(days=30), end_exclusive)
        yield cur, nxt
        cur = nxt

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

def request_one(session, headers, payload, retries=6):
    for attempt in range(retries):
        try:
            r = session.post(URL, headers=headers, json=payload, timeout=90)
            if r.status_code == 429 or r.status_code >= 500:
                if attempt + 1 == retries:
                    r.raise_for_status()
                time.sleep(min(60, 2 ** attempt))
                continue
            r.raise_for_status()
            body = r.json()
            if str(body.get("status", "")).lower() == "failure":
                raise RuntimeError("Dhan returned a failure status (details withheld)")
            return body
        except (requests.Timeout, requests.ConnectionError):
            if attempt + 1 == retries:
                raise
            time.sleep(min(60, 2 ** attempt))
    raise RuntimeError("Dhan request retry limit reached")

def extract_rows(body, option_type, expiry_code, relative_strike):
    data = body.get("data") or {}
    side = "ce" if option_type == "CALL" else "pe"
    block = data.get(side)
    if not block:
        return pd.DataFrame()
    ts = block.get("timestamp") or []
    n = len(ts)
    if not n:
        return pd.DataFrame()
    cols = {}
    for field in FIELDS:
        vals = block.get(field)
        if vals is None:
            cols[field] = [None] * n
        elif len(vals) != n:
            raise ValueError(f"Dhan response array length mismatch for {field}")
        else:
            cols[field] = vals
    df = pd.DataFrame(cols)
    df["timestamp"] = pd.to_datetime(ts, unit="s", utc=True).tz_convert(IST)
    df["option_type"] = option_type
    df["expiry_code"] = expiry_code
    df["relative_strike"] = relative_strike
    return df

def main():
    token = os.getenv("DHAN_JOB_ACCESS_TOKEN", "").strip()
    client_id = os.getenv("DHAN_CLIENT_ID", "").strip()
    if not token or not client_id:
        raise SystemExit("DHAN_AUTH_REQUIRED: Dhan token/client ID missing; no public-data fallback is implied.")
    end_text = os.getenv("DHAN_TO_DATE", "").strip() or date.today().isoformat()\n    end = date.fromisoformat(end_text)
    default_start = end.replace(year=end.year - 5)
    start_text = os.getenv("DHAN_FROM_DATE", "").strip() or default_start.isoformat()\n    start = date.fromisoformat(start_text)
    if (end-start).days > 5*365+5:
        raise SystemExit("Requested range exceeds Dhan's documented rolling five-year window.")
    OUT.mkdir(parents=True, exist_ok=True)
    headers = {"access-token": token, "client-id": client_id,
               "Content-Type": "application/json", "Accept": "application/json"}
    manifest = {"dataset":"DhanHQ rolling expired options", "underlying":"NIFTY",
                "interval":"1 minute", "from_date":start.isoformat(),
                "to_date_exclusive":end.isoformat(), "expiry_codes":list(EXPIRY_CODES),
                "relative_strikes":list(OFFSETS), "option_types":list(OPTION_TYPES),
                "fields":FIELDS, "files":[], "failed_requests":0,
                "generated_utc":datetime.now(timezone.utc).isoformat(),
                "important":"expiry_code is rolling (0 near/current, 1 next); map to actual expiry by timestamp using official calendar."}
    session = requests.Session()
    calls = 0
    for lo, hi in chunks(start, end):
        target = OUT / f"nifty_{lo:%Y%m%d}_{(hi-timedelta(days=1)):%Y%m%d}.parquet"
        if target.exists() and target.stat().st_size > 0:
            manifest["files"].append({"file":target.name,"cached":True,"bytes":target.stat().st_size,
                                      "sha256":sha256(target)})
            continue
        frames = []
        for expiry_code in EXPIRY_CODES:
            for offset in OFFSETS:
                strike = "ATM" if offset == 0 else f"ATM{offset:+d}"
                for opt in OPTION_TYPES:
                    payload = {"exchangeSegment":"NSE_FNO","interval":"1","securityId":"13",
                               "instrument":"OPTIDX","expiryFlag":"WEEK",
                               "expiryCode":expiry_code,"strike":strike,
                               "drvOptionType":opt,"requiredData":FIELDS,
                               "fromDate":lo.isoformat(),"toDate":hi.isoformat()}
                    body = request_one(session, headers, payload)
                    frame = extract_rows(body, opt, expiry_code, offset)
                    if not frame.empty:
                        frames.append(frame)
                    calls += 1
                    if calls % 100 == 0:
                        print(f"DHAN_PROGRESS requests={calls} chunk={lo}:{hi} rows={sum(len(x) for x in frames)}")
                    time.sleep(float(os.getenv("DHAN_REQUEST_PAUSE", "0.25")))
        if frames:
            df = pd.concat(frames, ignore_index=True)
            df = df.drop_duplicates(["timestamp","expiry_code","relative_strike","option_type"], keep="last")
            df = df.sort_values(["timestamp","expiry_code","option_type","relative_strike"])
            df.to_parquet(target, index=False, compression="zstd")
            manifest["files"].append({"file":target.name,"cached":False,"rows":len(df),
                                      "bytes":target.stat().st_size,"sha256":sha256(target),
                                      "min_timestamp":str(df.timestamp.min()),
                                      "max_timestamp":str(df.timestamp.max()),
                                      "null_ohlc_rows":int(df[["open","high","low","close"]].isna().any(axis=1).sum()),
                                      "null_iv_rows":int(df.iv.isna().sum()),
                                      "null_spot_rows":int(df.spot.isna().sum())})
        else:
            manifest["files"].append({"file":target.name,"rows":0,"empty":True})
    manifest["request_count_this_run"] = calls
    manifest["total_rows"] = sum(x.get("rows",0) for x in manifest["files"])
    manifest["gate"] = "PASS_RAW_COLLECTION" if manifest["total_rows"] > 0 else "FAIL_NO_ROWS"
    (OUT / "manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))
    if manifest["gate"] != "PASS_RAW_COLLECTION":
        raise SystemExit("No option rows collected.")
if __name__ == "__main__":
    main()
