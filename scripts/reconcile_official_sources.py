#!/usr/bin/env python3
"""Fetch official NIFTY 50 daily OHLC and verify candidate weekly expiries.

The script uses NSE Indices' public historical OHLC endpoint and the NSE F&O
daily bhavcopy archive. It never marks a candidate verified merely because a
weekday rule or a price bar exists: the expiry must appear in the official
F&O contract data. Network/source failures are written to a sanitized JSON
report and leave the acceptance gate blocked.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
import time
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "reconciliation"
CACHE = ROOT / "data" / "cache" / "official"
NIFTY_URL = "https://www.niftyindices.com/Backpage.aspx/getHistoricaldatatabletoString"
NIFTY_REFERER = "https://www.niftyindices.com/reports/historical-data"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"
FIRST_WEEKLY = date(2019, 2, 14)
TUESDAY_REGIME = date(2025, 9, 1)


def parse_niftyindices_response(payload: dict[str, Any]) -> pd.DataFrame:
    """Parse official NiftyIndices ASP.NET JSON response into canonical OHLC."""
    raw = payload.get("d")
    if isinstance(raw, str):
        rows = json.loads(raw)
    elif isinstance(raw, list):
        rows = raw
    else:
        raise ValueError("NiftyIndices response has no valid 'd' array")
    if not rows:
        raise ValueError("NiftyIndices returned no rows")
    frame = pd.DataFrame(rows)
    date_col = next((c for c in ("HistoricalDate", "Date", "DATE") if c in frame), None)
    close_col = next((c for c in ("CLOSE", "Close", "Closing Index Value") if c in frame), None)
    if date_col is None or close_col is None:
        raise ValueError("Unexpected NiftyIndices columns: " + ",".join(map(str, frame.columns)))
    frame["session_date"] = pd.to_datetime(frame[date_col], errors="coerce", dayfirst=True).dt.date
    for col in ("OPEN", "HIGH", "LOW", close_col):
        if col in frame:
            frame[col] = pd.to_numeric(frame[col].astype(str).str.replace(",", "", regex=False), errors="coerce")
    frame["official_close"] = pd.to_numeric(frame[close_col].astype(str).str.replace(",", "", regex=False), errors="coerce")
    frame = frame.dropna(subset=["session_date", "official_close"])
    frame = frame[["session_date", "official_close"]].drop_duplicates("session_date").sort_values("session_date")
    if frame.empty:
        raise ValueError("No valid official NIFTY 50 OHLC rows after parsing")
    return frame.reset_index(drop=True)


def fetch_official_daily(start: date, end: date, force: bool = False) -> pd.DataFrame:
    """Fetch official NIFTY 50 price-return index closes in <= 360-day chunks."""
    CACHE.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({
        "User-Agent": UA,
        "Referer": NIFTY_REFERER,
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json; charset=UTF-8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    })
    frames: list[pd.DataFrame] = []
    chunk_start = start
    while chunk_start <= end:
        chunk_end = min(end, chunk_start + timedelta(days=350))
        cache_file = CACHE / f"nifty50_official_{chunk_start:%Y%m%d}_{chunk_end:%Y%m%d}.csv"
        if cache_file.exists() and not force:
            frames.append(pd.read_csv(cache_file, parse_dates=["session_date"]).assign(
                session_date=lambda x: x["session_date"].dt.date
            ))
        else:
            info = {
                "name": "NIFTY 50",
                "startDate": chunk_start.strftime("%d-%b-%Y"),
                "endDate": chunk_end.strftime("%d-%b-%Y"),
                "indexName": "NIFTY 50",
            }
            body = {"cinfo": "{" + ",".join(f"'{k}':'{v}'" for k, v in info.items()) + "}"}
            response = session.post(NIFTY_URL, json=body, timeout=(15, 60))
            response.raise_for_status()
            payload = response.json()
            frame = parse_niftyindices_response(payload)
            frame = frame[(frame["session_date"] >= chunk_start) & (frame["session_date"] <= chunk_end)]
            if frame.empty:
                raise RuntimeError(f"Official NIFTY data empty for {chunk_start} to {chunk_end}")
            frame.to_csv(cache_file, index=False)
            frames.append(frame)
            time.sleep(1.0)
        chunk_start = chunk_end + timedelta(days=1)
    combined = pd.concat(frames, ignore_index=True).drop_duplicates("session_date").sort_values("session_date")
    if combined.empty:
        raise RuntimeError("Official NIFTY history is empty")
    return combined.reset_index(drop=True)


def weekly_nominals(start: date, end: date) -> list[date]:
    """Generate the documented weekly expiry regime schedule, not final verified dates."""
    first = max(start, FIRST_WEEKLY)
    dates: list[date] = []
    d = first
    while d <= end:
        weekday = 1 if d >= TUESDAY_REGIME else 3  # Tuesday from Sep-2025; Thursday before
        delta = (weekday - d.weekday()) % 7
        nominal = d + timedelta(days=delta)
        if nominal > end:
            break
        dates.append(nominal)
        d = nominal + timedelta(days=1)
        while d.weekday() != weekday:
            d += timedelta(days=1)
    return sorted(set(dates))


def parse_bhavcopy_contract_expiries(blob: bytes, trade_date: date) -> set[date]:
    """Return NIFTY weekly option expiry dates from legacy or UDiFF NSE F&O bhavcopy."""
    try:
        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
            if not names:
                raise ValueError("NSE bhavcopy ZIP contains no CSV")
            raw = zf.read(names[0])
    except zipfile.BadZipFile:
        raw = blob
    frame = pd.read_csv(io.BytesIO(raw), low_memory=False)
    canonical = {re.sub(r"[^a-z0-9]", "", str(c).lower()): c for c in frame.columns}
    symbol_col = next((canonical[k] for k in ("symbol", "tckrsymb", "underlying") if k in canonical), None)
    instrument_col = next((canonical[k] for k in ("instrument", "fininstrmtp", "instrumenttype") if k in canonical), None)
    expiry_col = next((canonical[k] for k in ("expiry", "expirydate", "expirydt", "xprydt", "expiry_dt") if k in canonical), None)
    option_type_col = next((canonical[k] for k in ("optiontype", "optiontyp", "optn", "optn_tp", "opntp", "option_type") if k in canonical), None)
    if symbol_col is None or expiry_col is None:
        raise ValueError("Unrecognized NSE F&O bhavcopy schema: " + ",".join(map(str, frame.columns)))
    symbols = frame[symbol_col].astype(str).str.upper().str.strip().eq("NIFTY")
    if instrument_col:
        inst = frame[instrument_col].astype(str).str.upper().str.strip()
        symbols &= inst.isin({"OPTIDX", "OPT", "INDEX OPTIONS"})
    if option_type_col:
        opts = frame[option_type_col].astype(str).str.upper().str.strip()
        symbols &= opts.isin({"CE", "PE"})
    expiry = pd.to_datetime(frame.loc[symbols, expiry_col], errors="coerce", dayfirst=True)
    return set(expiry.dropna().dt.date)


def fetch_bhavcopy(trade_date: date, session: requests.Session) -> bytes:
    """Try official NSE legacy then UDiFF archive URLs for a trading date."""
    mon = trade_date.strftime("%b").upper()
    old = f"https://archives.nseindia.com/content/historical/DERIVATIVES/{trade_date:%Y}/{mon}/fo{trade_date:%d}{mon}{trade_date:%Y}bhav.csv.zip"
    new = f"https://archives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{trade_date:%Y%m%d}_F_0000.csv.zip"
    headers = {"User-Agent": UA, "Referer": "https://www.nseindia.com/all-reports-derivatives"}
    failures = []
    for url in (new, old):
        try:
            response = session.get(url, headers=headers, timeout=(10, 30))
            if response.status_code == 200 and len(response.content) > 100:
                return response.content
            failures.append(f"{response.status_code}:{url.rsplit('/', 1)[-1]}")
        except requests.RequestException as exc:
            failures.append(type(exc).__name__)
    raise RuntimeError("NSE F&O bhavcopy unavailable for " + trade_date.isoformat() + " (" + ";".join(failures) + ")")


def run(start: date, end: date, force: bool = False, max_expiries: int = 0) -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "generated_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "start_date": start.isoformat(), "end_date": end.isoformat(),
        "official_price_source": "NSE Indices NIFTY 50 historical price-index OHLC endpoint",
        "official_expiry_source": "NSE F&O daily bhavcopy, NIFTY OPTIDX CE/PE contracts",
        "status": "BLOCKED", "errors": [], "counts": {},
    }
    try:
        official = fetch_official_daily(start, end, force=force)
        official.to_csv(OUT / "nifty50_official_daily.csv", index=False)
        candidate = pd.read_csv(ROOT / "data" / "processed" / "candidate_expiry_calendar.csv")
        candidate["nominal_expiry"] = pd.to_datetime(candidate["nominal_expiry"], errors="coerce").dt.date
        source_cross = pd.read_csv(ROOT / "research" / "results" / "yahoo_daily_crosscheck.csv")
        source_cross["session_date"] = pd.to_datetime(source_cross["session_date"], errors="coerce").dt.date
        official_map = official.set_index("session_date")["official_close"].to_dict()
        source_cross["official_close"] = source_cross["session_date"].map(official_map)
        source_cross["official_abs_difference"] = (source_cross["session_close"] - source_cross["official_close"]).abs()
        source_cross["official_over_1pt"] = source_cross["official_abs_difference"] > 1.0
        source_cross.to_csv(OUT / "minute_vs_official_daily.csv", index=False)
        candidate_dates = sorted(set(x for x in candidate["nominal_expiry"].dropna() if start <= x <= end))
        if max_expiries:
            candidate_dates = candidate_dates[:max_expiries]
        sessions = sorted(official_map)
        session = requests.Session()
        session.headers.update({"User-Agent": UA, "Accept": "*/*"})
        verified: list[dict[str, Any]] = []
        for candidate_date in candidate_dates:
            # Find last official session on or before candidate date; official price sessions
            # encode holidays, but the contract must still appear in the NSE F&O bhavcopy.
            possible = [d for d in sessions if d <= candidate_date]
            if not possible:
                verified.append({"candidate_date": candidate_date.isoformat(), "status": "no_official_session"})
                continue
            actual = possible[-1]
            try:
                cache_file = CACHE / "fo" / f"fo_{actual:%Y%m%d}.zip"
                if cache_file.exists() and not force:
                    blob = cache_file.read_bytes()
                else:
                    blob = fetch_bhavcopy(actual, session)
                    cache_file.parent.mkdir(parents=True, exist_ok=True)
                    cache_file.write_bytes(blob)
                expiries = parse_bhavcopy_contract_expiries(blob, actual)
                exists = actual in expiries
                verified.append({
                    "candidate_date": candidate_date.isoformat(),
                    "candidate_previous_session": actual.isoformat(),
                    "contract_expiry_present": exists,
                    "status": "verified_nifty_weekly_expiry" if exists else "not_verified_in_bhavcopy",
                    "nifty_option_expiries_in_bhavcopy": sorted(x.isoformat() for x in expiries),
                })
            except Exception as exc:
                verified.append({
                    "candidate_date": candidate_date.isoformat(),
                    "candidate_previous_session": actual.isoformat(),
                    "status": "source_error",
                    "error_type": type(exc).__name__,
                    "error": str(exc)[:250],
                })
            time.sleep(0.35)
        pd.DataFrame(verified).to_csv(OUT / "expiry_verification.csv", index=False)
        n = len(verified)
        good = sum(x.get("status") == "verified_nifty_weekly_expiry" for x in verified)
        errs = sum(x.get("status") == "source_error" for x in verified)
        cross_rows = source_cross.dropna(subset=["official_close"])
        mismatch = int(cross_rows["official_over_1pt"].sum())
        report["counts"] = {
            "official_daily_rows": len(official),
            "candidate_expiries_checked": n,
            "contract_verified_expiries": good,
            "expiry_source_errors": errs,
            "daily_source_rows_compared": len(cross_rows),
            "minute_vs_official_mismatches_over_1_point": mismatch,
        }
        report["status"] = "PASS" if n > 0 and good == n and errs == 0 and mismatch == 0 else "BLOCKED"
        if report["status"] == "BLOCKED":
            report["errors"].append("One or more candidate expiry dates were not confirmed in official F&O data, or minute archive daily closes differ from official NIFTY 50 closes by >1 point.")
    except Exception as exc:
        report["errors"].append(type(exc).__name__ + ": " + str(exc)[:500])
    (OUT / "source_reconciliation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=date.fromisoformat, default=date(2019, 2, 1))
    parser.add_argument("--end", type=date.fromisoformat, default=date.today())
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--max-expiries", type=int, default=0, help="Diagnostic cap; 0 checks all candidate expiries")
    args = parser.parse_args()
    report = run(args.start, args.end, args.force, args.max_expiries)
    return 0 if report.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
