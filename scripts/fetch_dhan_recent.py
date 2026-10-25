#!/usr/bin/env python3
"""Optionally cross-check recent public NIFTY 50 minute bars with Dhan historical data."""
from __future__ import annotations

import os
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "dhan" / "NIFTY50_DHAN_recent.csv"
MASTER_URL = "https://images.dhan.co/api-data/api-scrip-master.csv"
INTRADAY_URL = "https://api.dhan.co/v2/charts/intraday"
IST = "Asia/Kolkata"


def find_nifty50_security(master: pd.DataFrame) -> str:
    lookup = {str(column).strip().upper(): column for column in master.columns}
    required_id_candidates = ["SEM_SMST_SECURITY_ID", "SECURITYID", "SECURITY_ID", "SMST_SECURITY_ID"]
    id_col = next((lookup[k] for k in required_id_candidates if k in lookup), None)
    if id_col is None:
        raise ValueError("Security master does not expose a recognized security ID field.")
    seg_col = next((lookup[k] for k in ("SEM_SEGMENT", "SEGMENT") if k in lookup), None)
    exchange_col = next((lookup[k] for k in ("SEM_EXM_EXCH_ID", "EXCHANGE") if k in lookup), None)
    text_cols = [lookup[k] for k in lookup if any(w in k for w in ("SYMBOL", "INSTRUMENT", "CUSTOM", "NAME"))]
    if not text_cols:
        raise ValueError("Security master has no recognized symbol/name fields.")
    mask = pd.Series(False, index=master.index)
    for column in text_cols:
        mask = mask | master[column].astype(str).str.upper().str.fullmatch(r"\s*NIFTY\s*50(?:\s+INDEX)?\s*", na=False)
    if seg_col:
        segment = master[seg_col].astype(str).str.upper().str.strip()
        mask &= segment.isin(["I", "IDX_I", "IDX"])
    if exchange_col:
        exchange = master[exchange_col].astype(str).str.upper().str.strip()
        mask &= exchange.eq("NSE")
    ids = sorted(set(master.loc[mask, id_col].dropna().astype(str).str.strip()) - {""})
    if len(ids) != 1:
        raise ValueError("Security-master match for NSE NIFTY 50 INDEX was not unique; refusing unchecked hard-coded IDs.")
    return ids[0]


def main() -> int:
    token = os.getenv("DHAN_JOB_ACCESS_TOKEN", "").strip()
    client_id = os.getenv("DHAN_CLIENT_ID", "").strip()
    if not token or not client_id:
        print("DHAN_DATA_SKIPPED: No short-lived Dhan token available; public archive remains the core dataset.")
        return 0
    try:
        master_response = requests.get(MASTER_URL, timeout=60)
        master_response.raise_for_status()
        master_path = ROOT / "data" / "raw" / "dhan" / "security_master.csv"
        master_path.parent.mkdir(parents=True, exist_ok=True)
        master_path.write_bytes(master_response.content)
        master = pd.read_csv(master_path, low_memory=False)
        security_id = find_nifty50_security(master)

        lookback_days = max(5, min(int(os.getenv("DHAN_CROSSCHECK_LOOKBACK_DAYS", "120")), 365))
        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=lookback_days)
        token_headers = {
            "access-token": token,
            "client-id": client_id,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        chunks = []
        cursor = start_date
        while cursor <= end_date:
            chunk_end = min(cursor + timedelta(days=89), end_date)
            request_body = {
                "securityId": security_id,
                "exchangeSegment": "IDX_I",
                "instrument": "INDEX",
                "interval": "1",
                "oi": False,
                "fromDate": cursor.isoformat() + " 09:15:00",
                "toDate": chunk_end.isoformat() + " 15:30:00",
            }
            response = requests.post(INTRADAY_URL, headers=token_headers, json=request_body, timeout=90)
            if not response.ok:
                print("DHAN_DATA_ERROR: Intraday endpoint returned HTTP", response.status_code, file=sys.stderr)
                return 2
            result = response.json()
            opens = result.get("open", [])
            highs = result.get("high", [])
            lows = result.get("low", [])
            closes = result.get("close", [])
            epochs = result.get("timestamp") or result.get("start_Time") or result.get("startTime") or []
            count = min(len(opens), len(highs), len(lows), len(closes), len(epochs))
            if count:
                stamps = pd.to_datetime(epochs[:count], unit="s", utc=True).tz_convert(IST)
                chunks.append(pd.DataFrame({
                    "Timestamp": stamps.astype(str),
                    "Open": opens[:count],
                    "High": highs[:count],
                    "Low": lows[:count],
                    "Close": closes[:count],
                }))
            cursor = chunk_end + timedelta(days=1)

        OUT.parent.mkdir(parents=True, exist_ok=True)
        if chunks:
            all_bars = pd.concat(chunks, ignore_index=True).drop_duplicates("Timestamp", keep="last").sort_values("Timestamp")
            all_bars.to_csv(OUT, index=False)
            print("DHAN_DATA_OK: Recent NIFTY 50 bars retrieved for independent comparison; raw vendor bars kept out of Git.")
            print("DHAN_DATA_BAR_COUNT:", len(all_bars), "coverage:", all_bars["Timestamp"].min(), "to", all_bars["Timestamp"].max())
        else:
            print("DHAN_DATA_WARNING: Dhan returned no intraday bars for the requested window.", file=sys.stderr)
            return 2
        return 0
    except Exception as exc:
        print("DHAN_DATA_ERROR:", type(exc).__name__, "Recent Dhan data cross-check failed; sensitive response details withheld.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
