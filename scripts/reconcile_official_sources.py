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
NIFTY_URL = "https://www.niftyindices.com/BackPage.aspx/getHistoricaldatatabletoString"
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
    field_aliases = {
        "official_open": ("OPEN", "Open", "Opening Index Value", "EOD_OPEN_INDEX_VAL"),
        "official_high": ("HIGH", "High", "High Index Value", "EOD_HIGH_INDEX_VAL"),
        "official_low": ("LOW", "Low", "Low Index Value", "EOD_LOW_INDEX_VAL"),
    }
    keep = ["session_date"]
    for output_col, aliases in field_aliases.items():
        source_col = next((c for c in aliases if c in frame), None)
        if source_col is not None:
            frame[output_col] = pd.to_numeric(frame[source_col].astype(str).str.replace(",", "", regex=False), errors="coerce")
            keep.append(output_col)
    frame["official_close"] = pd.to_numeric(frame[close_col].astype(str).str.replace(",", "", regex=False), errors="coerce")
    keep.append("official_close")
    frame = frame.dropna(subset=["session_date", "official_close"])
    frame = frame[keep].drop_duplicates("session_date").sort_values("session_date")
    if frame.empty:
        raise ValueError("No valid official NIFTY 50 OHLC rows after parsing")
    return frame.reset_index(drop=True)


def fetch_nse_daily_fallback(start: date, end: date, force: bool = False) -> pd.DataFrame:
    """Fallback to NSE's official daily all-index-close archives for known session dates."""
    source_path = ROOT / "research" / "results" / "yahoo_daily_crosscheck.csv"
    source = pd.read_csv(source_path)
    source["session_date"] = pd.to_datetime(source["session_date"], errors="coerce").dt.date
    dates = sorted(set(d for d in source["session_date"].dropna() if start <= d <= end))
    if not dates:
        raise RuntimeError("No source-session dates available to request NSE ind_close_all files")
    (CACHE / "nse_daily").mkdir(parents=True, exist_ok=True)

    import threading
    local = threading.local()

    def get_session() -> requests.Session:
        session = getattr(local, "session", None)
        if session is None:
            session = requests.Session()
            session.headers.update({
                "User-Agent": UA,
                "Referer": "https://www.nseindia.com/all-reports",
                "Accept": "text/csv,text/plain,*/*",
            })
            try:
                session.get("https://www.nseindia.com/all-reports", timeout=(5, 8))
            except requests.RequestException:
                pass
            local.session = session
        return session

    def get_one(day: date) -> dict[str, Any]:
        cache_file = CACHE / "nse_daily" / f"ind_close_all_{day:%d%m%Y}.csv"
        if cache_file.exists() and not force:
            content = cache_file.read_bytes()
        else:
            session = get_session()
            url = f"https://nsearchives.nseindia.com/content/indices/ind_close_all_{day:%d%m%Y}.csv"
            response = session.get(url, timeout=(5, 12))
            response.raise_for_status()
            content = response.content
            if len(content) < 100:
                raise RuntimeError("NSE ind_close_all response is too small")
            cache_file.write_bytes(content)
        try:
            frame = pd.read_csv(io.BytesIO(content), low_memory=False)
            cols = {re.sub(r"[^a-z0-9]", "", str(col).lower()): col for col in frame.columns}
            name_col = next((cols[k] for k in ("indexname", "index") if k in cols), None)
            close_col = next((cols[k] for k in ("closingindexvalue", "close", "closingvalue") if k in cols), None)
            if name_col is None or close_col is None:
                raise ValueError("Unexpected NSE index-close schema: " + ",".join(map(str, frame.columns)))
            selected = frame[frame[name_col].astype(str).str.strip().str.casefold().eq("nifty 50")]
            if selected.empty:
                raise ValueError("NIFTY 50 row absent from official daily index file")
            row = selected.iloc[0]
            close = pd.to_numeric(str(row[close_col]).replace(",", ""), errors="coerce")
            if pd.isna(close) or float(close) <= 0:
                raise ValueError("Invalid official NIFTY 50 close")
            answer = {"session_date": day, "official_close": float(close), "status": "ok"}
            for output_col, aliases in {
                "official_open": ("openindexvalue", "openingindexvalue", "open"),
                "official_high": ("highindexvalue", "high"),
                "official_low": ("lowindexvalue", "low"),
            }.items():
                source_col = next((cols[k] for k in aliases if k in cols), None)
                if source_col is not None:
                    value = pd.to_numeric(str(row[source_col]).replace(",", ""), errors="coerce")
                    answer[output_col] = float(value) if pd.notna(value) else None
            return answer
        except Exception as exc:
            return {"session_date": day, "official_close": None, "status": type(exc).__name__ + ": " + str(exc)[:180]}

    # Keep request pressure bounded; every day is cached and missing rows are visible.
    from concurrent.futures import ThreadPoolExecutor, as_completed
    rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(get_one, day): day for day in dates}
        for future in as_completed(futures):
            try:
                rows.append(future.result())
            except Exception as exc:
                rows.append({"session_date": futures[future], "official_close": None, "status": type(exc).__name__ + ": " + str(exc)[:180]})
    result = pd.DataFrame(rows)
    failed = result[result["official_close"].isna()]
    if len(failed):
        failure_path = OUT / "nse_daily_fetch_errors.csv"
        failed.to_csv(failure_path, index=False)
    for col in ("official_open", "official_high", "official_low"):
        if col not in result.columns:
            result[col] = pd.NA
    result = result.dropna(subset=["official_close"])[["session_date", "official_open", "official_high", "official_low", "official_close"]]
    result = result.drop_duplicates("session_date").sort_values("session_date").reset_index(drop=True)
    if result.empty:
        raise RuntimeError("NSE daily archive fallback returned no usable NIFTY 50 closes")
    result.attrs["source"] = "NSE official ind_close_all daily archive (fallback after NiftyIndices endpoint failed)"
    return result


def fetch_nse_history_api(start: date, end: date) -> pd.DataFrame:
    """Try NSE's official historicalOR JSON endpoint before per-day archive downloads."""
    session = requests.Session()
    headers = {
        "User-Agent": UA,
        "Referer": "https://www.nseindia.com/reports-indices-historical-index-data",
        "Accept": "application/json,text/plain,*/*",
        "Accept-Language": "en-US,en;q=0.9",
    }
    session.headers.update(headers)
    session.get("https://www.nseindia.com/reports-indices-historical-index-data", timeout=(5, 12))
    frames: list[pd.DataFrame] = []
    chunk_start = start
    while chunk_start <= end:
        chunk_end = min(end, chunk_start + timedelta(days=55))
        url = "https://www.nseindia.com/api/historicalOR/indicesHistory"
        response = session.get(url, params={
            "indexType": "NIFTY 50",
            "from": chunk_start.strftime("%d-%m-%Y"),
            "to": chunk_end.strftime("%d-%m-%Y"),
        }, timeout=(8, 20))
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data", [])
        if isinstance(data, dict):
            rows = data.get("indexCloseOnlineRecords") or data.get("indexCloseRecords") or []
        elif isinstance(data, list):
            rows = data
        else:
            rows = []
        if not rows:
            raise RuntimeError(f"NSE historicalOR returned no index rows for {chunk_start} to {chunk_end}")
        frame = pd.DataFrame(rows)
        date_col = next((k for k in ("EOD_TIMESTAMP", "HistoricalDate", "date", "Date") if k in frame), None)
        close_col = next((k for k in ("EOD_CLOSE_INDEX_VAL", "CLOSE", "Closing Index Value") if k in frame), None)
        if date_col is None or close_col is None:
            raise ValueError("Unexpected NSE historicalOR schema: " + ",".join(map(str, frame.columns)))
        frame["session_date"] = pd.to_datetime(frame[date_col], errors="coerce", dayfirst=True).dt.date
        field_aliases = {
            "official_open": ("EOD_OPEN_INDEX_VAL", "OPEN", "Open", "Opening Index Value"),
            "official_high": ("EOD_HIGH_INDEX_VAL", "HIGH", "High", "High Index Value"),
            "official_low": ("EOD_LOW_INDEX_VAL", "LOW", "Low", "Low Index Value"),
        }
        keep = ["session_date"]
        for output_col, aliases in field_aliases.items():
            source_col = next((k for k in aliases if k in frame), None)
            if source_col is not None:
                frame[output_col] = pd.to_numeric(frame[source_col].astype(str).str.replace(",", "", regex=False), errors="coerce")
                keep.append(output_col)
        frame["official_close"] = pd.to_numeric(frame[close_col].astype(str).str.replace(",", "", regex=False), errors="coerce")
        keep.append("official_close")
        frame = frame.dropna(subset=["session_date", "official_close"])
        frame = frame[(frame["session_date"] >= chunk_start) & (frame["session_date"] <= chunk_end)]
        if frame.empty:
            raise RuntimeError(f"NSE historicalOR rows failed date/close validation for {chunk_start} to {chunk_end}")
        frames.append(frame[keep])
        chunk_start = chunk_end + timedelta(days=1)
        time.sleep(0.25)
    result = pd.concat(frames, ignore_index=True).drop_duplicates("session_date").sort_values("session_date").reset_index(drop=True)
    result.attrs["source"] = "NSE official historicalOR/indicesHistory JSON endpoint"
    return result


def fetch_official_daily(start: date, end: date, force: bool = False) -> pd.DataFrame:
    """Prefer NiftyIndices history, then fall back to official NSE daily index archives."""
    CACHE.mkdir(parents=True, exist_ok=True)
    try:
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
            use_cache = False
            if cache_file.exists() and not force:
                cached = pd.read_csv(cache_file, parse_dates=["session_date"])
                required_ohlc = {"official_open", "official_high", "official_low"}
                if required_ohlc.issubset(cached.columns):
                    frames.append(cached.assign(session_date=lambda x: x["session_date"].dt.date))
                    use_cache = True
            if not use_cache:
                info = {
                    "name": "NIFTY 50",
                    "startDate": chunk_start.strftime("%d-%b-%Y"),
                    "endDate": chunk_end.strftime("%d-%b-%Y"),
                    "indexName": "NIFTY 50",
                }
                body = {"cinfo": "{" + ",".join(f"'{k}':'{v}'" for k, v in info.items()) + "}"}
                response = session.post(NIFTY_URL, json=body, timeout=(10, 25))
                response.raise_for_status()
                frame = parse_niftyindices_response(response.json())
                frame = frame[(frame["session_date"] >= chunk_start) & (frame["session_date"] <= chunk_end)]
                if frame.empty:
                    raise RuntimeError(f"Official NIFTY data empty for {chunk_start} to {chunk_end}")
                frame.to_csv(cache_file, index=False)
                frames.append(frame)
                time.sleep(0.5)
            chunk_start = chunk_end + timedelta(days=1)
        combined = pd.concat(frames, ignore_index=True).drop_duplicates("session_date").sort_values("session_date").reset_index(drop=True)
        if combined.empty:
            raise RuntimeError("Official NIFTY history is empty")
        combined.attrs["source"] = "NSE Indices official NIFTY 50 historical price-index OHLC endpoint"
        return combined
    except Exception as exc:
        print(f"NIFTYINDICES_ENDPOINT_FAILED: {type(exc).__name__}: {str(exc)[:400]}", file=sys.stderr)
        try:
            return fetch_nse_history_api(start, end)
        except Exception as nse_exc:
            print(f"NSE_HISTORY_API_FAILED: {type(nse_exc).__name__}: {str(nse_exc)[:250]}", file=sys.stderr)
            return fetch_nse_daily_fallback(start, end, force=force)


def candidate_verification_sessions(candidate_date: date, sessions: list[date], max_calendar_days: int = 4) -> list[date]:
    """Return candidate date plus nearby prior sessions for holiday-shift verification."""
    eligible = [
        day for day in sessions
        if day <= candidate_date and (candidate_date - day).days <= max_calendar_days
    ]
    return list(reversed(eligible))


def weekly_nominals(start: date, end: date) -> list[date]:
    """Generate the documented weekly expiry regime schedule, not final verified dates."""
    first = max(start, FIRST_WEEKLY)
    dates: list[date] = []
    d = first
    while d <= end:
        weekday = 1 if d >= TUESDAY_REGIME else 3  # Tuesday from Sep-2025; Thursday before
        if d.weekday() == weekday:
            dates.append(d)
        d += timedelta(days=1)
    return dates


def _extract_bhavcopy_csv(blob: bytes) -> bytes:
    """Extract the contract CSV from a legacy/UDiFF ZIP or accept a direct CSV."""
    try:
        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
            if not names:
                raise ValueError("NSE bhavcopy ZIP contains no CSV")
            return zf.read(names[0])
    except zipfile.BadZipFile:
        return blob


def _parse_date_values(values: pd.Series) -> pd.Series:
    """Parse compact, ISO year-first, ISO timestamp and legacy day-first date values safely."""
    text = values.astype(str).str.strip()
    parsed = pd.Series(pd.NaT, index=values.index, dtype="datetime64[ns]")

    compact_mask = text.str.fullmatch(r"\d{8}")
    iso_day_mask = text.str.fullmatch(r"\d{4}-\d{2}-\d{2}")
    iso_datetime_mask = text.str.match(r"^\d{4}-\d{2}-\d{2}[T ]")
    year_first_mask = iso_day_mask | iso_datetime_mask
    legacy_mask = ~(compact_mask | year_first_mask)

    if compact_mask.any():
        parsed.loc[compact_mask] = pd.to_datetime(text.loc[compact_mask], format="%Y%m%d", errors="coerce")
    if iso_day_mask.any():
        parsed.loc[iso_day_mask] = pd.to_datetime(text.loc[iso_day_mask], format="%Y-%m-%d", errors="coerce")
    if iso_datetime_mask.any():
        parsed.loc[iso_datetime_mask] = pd.to_datetime(text.loc[iso_datetime_mask], errors="coerce", yearfirst=True)
    if legacy_mask.any():
        parsed.loc[legacy_mask] = pd.to_datetime(text.loc[legacy_mask], errors="coerce", dayfirst=True)
    return parsed


def _validate_bhavcopy_blob(blob: bytes, trade_date: date) -> None:
    """Reject an HTML/error response, unexpected schema, or archive for another date."""
    raw = _extract_bhavcopy_csv(blob)
    frame = pd.read_csv(io.BytesIO(raw), low_memory=False, nrows=8)
    canonical = {re.sub(r"[^a-z0-9]", "", str(c).lower()): c for c in frame.columns}
    symbol_col = next((canonical[k] for k in ("symbol", "tckrsymb", "underlying", "undrlyginstrm") if k in canonical), None)
    expiry_col = next((canonical[k] for k in ("expiry", "expirydate", "expirydt", "xprydt", "fininstrmactlxprydt") if k in canonical), None)
    if symbol_col is None or expiry_col is None:
        raise ValueError("Unrecognized NSE F&O bhavcopy schema: " + ",".join(map(str, frame.columns)))
    trade_col = next((canonical[k] for k in ("traddt", "tradedate", "bizdt", "businessdate", "timestamp", "tradedt", "traddate") if k in canonical), None)
    if trade_col:
        parsed = _parse_date_values(frame[trade_col])
        source_dates = set(parsed.dropna().dt.date)
        if source_dates and trade_date not in source_dates:
            raise ValueError(
                f"Bhavcopy trade-date mismatch: expected {trade_date.isoformat()}, "
                f"file identifies {','.join(sorted(d.isoformat() for d in source_dates)[:3])}"
            )


def parse_bhavcopy_contract_expiries(blob: bytes, trade_date: date) -> set[date]:
    """Return NIFTY option expiries from legacy or UDiFF NSE F&O bhavcopy.

    UDiFF exposes scheduled and actual expiry fields. Prefer actual expiry when
    populated, and validate that the archive is for the requested trade date.
    """
    raw = _extract_bhavcopy_csv(blob)
    frame = pd.read_csv(io.BytesIO(raw), low_memory=False)
    canonical = {re.sub(r"[^a-z0-9]", "", str(c).lower()): c for c in frame.columns}

    trade_col = next((canonical[k] for k in ("traddt", "tradedate", "bizdt", "businessdate", "timestamp", "tradedt", "traddate") if k in canonical), None)
    if trade_col:
        parsed_trade_dates = _parse_date_values(frame[trade_col])
        source_dates = set(parsed_trade_dates.dropna().dt.date)
        if source_dates and trade_date not in source_dates:
            raise ValueError(
                f"Bhavcopy trade-date mismatch: expected {trade_date.isoformat()}, "
                f"file identifies {','.join(sorted(d.isoformat() for d in source_dates)[:3])}"
            )

    symbol_col = next((canonical[k] for k in ("symbol", "tckrsymb", "underlying", "undrlyginstrm") if k in canonical), None)
    instrument_col = next((canonical[k] for k in ("instrument", "fininstrmtp", "instrumenttype") if k in canonical), None)
    expiry_col = next((canonical[k] for k in ("expiry", "expirydate", "expirydt", "xprydt") if k in canonical), None)
    actual_expiry_col = canonical.get("fininstrmactlxprydt")
    option_type_col = next((canonical[k] for k in ("optiontype", "optiontyp", "optn", "optn_tp", "optntp", "optntyp", "option_type") if k in canonical), None)
    if symbol_col is None or expiry_col is None:
        raise ValueError("Unrecognized NSE F&O bhavcopy schema: " + ",".join(map(str, frame.columns)))

    symbols = frame[symbol_col].astype(str).str.upper().str.strip().eq("NIFTY")
    if instrument_col:
        inst = frame[instrument_col].astype(str).str.upper().str.strip()
        symbols &= inst.isin({"OPTIDX", "OPT", "INDEX OPTIONS", "IDO", "OPTIDX CE", "OPTIDX PE"})
    if option_type_col:
        opts = frame[option_type_col].astype(str).str.upper().str.strip()
        symbols &= opts.isin({"CE", "PE"})

    scheduled = _parse_date_values(frame.loc[symbols, expiry_col])
    expiry_dates = scheduled.copy()
    if actual_expiry_col:
        actual = _parse_date_values(frame.loc[symbols, actual_expiry_col])
        expiry_dates = actual.where(actual.notna(), scheduled)
    return set(expiry_dates.dropna().dt.date)


def bhavcopy_urls(trade_date: date) -> list[str]:
    """Return source URLs in the official format's historical date order.

    NSE used the legacy derivative CSV through 5 July 2024; UDiFF replaced it
    from 8 July 2024. Prefer the matching format and the documented UDiFF host.
    """
    mon = trade_date.strftime("%b").upper()
    legacy = (
        f"https://archives.nseindia.com/content/historical/DERIVATIVES/"
        f"{trade_date:%Y}/{mon}/fo{trade_date:%d}{mon}{trade_date:%Y}bhav.csv.zip"
    )
    udiff = (
        "https://nsearchives.nseindia.com/content/fo/"
        f"BhavCopy_NSE_FO_0_0_0_{trade_date:%Y%m%d}_F_0000.csv.zip"
    )
    udiff_alt = (
        "https://archives.nseindia.com/content/fo/"
        f"BhavCopy_NSE_FO_0_0_0_{trade_date:%Y%m%d}_F_0000.csv.zip"
    )
    if trade_date < date(2024, 7, 8):
        return [legacy, udiff, udiff_alt]
    return [udiff, udiff_alt, legacy]


def fetch_bhavcopy(trade_date: date, session: requests.Session) -> bytes:
    """Fetch the expected official NSE bhavcopy format, validating date and schema."""
    headers = {"User-Agent": UA, "Referer": "https://www.nseindia.com/all-reports-derivatives"}
    failures = []
    for url in bhavcopy_urls(trade_date):
        try:
            response = session.get(url, headers=headers, timeout=(5, 10))
            if response.status_code != 200 or len(response.content) <= 100:
                failures.append(f"{response.status_code}:{url.rsplit('/', 1)[-1]}")
                continue
            try:
                _validate_bhavcopy_blob(response.content, trade_date)
            except Exception as exc:
                failures.append(f"invalid:{url.rsplit('/', 1)[-1]}:{type(exc).__name__}:{str(exc)[:260]}")
                continue
            return response.content
        except requests.RequestException as exc:
            failures.append(f"{type(exc).__name__}:{url.rsplit('/', 1)[-1]}")
    raise RuntimeError("NSE F&O bhavcopy unavailable/invalid for " + trade_date.isoformat() + " (" + ";".join(failures) + ")")

def run(start: date, end: date, force: bool = False, max_expiries: int = 0) -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "generated_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "start_date": start.isoformat(), "end_date": end.isoformat(),
        "official_price_source": "NSE Indices historical OHLC with NSE ind_close_all archive fallback",
        "official_expiry_source": "NSE F&O daily bhavcopy, NIFTY OPTIDX CE/PE contracts",
        "status": "BLOCKED", "errors": [], "counts": {},
    }
    try:
        official = fetch_official_daily(start, end, force=force)
        report["official_price_source_used"] = official.attrs.get("source", "official daily index source; source label unavailable")
        official.to_csv(OUT / "nifty50_official_daily.csv", index=False)
        candidate = pd.read_csv(ROOT / "data" / "processed" / "candidate_expiry_calendar.csv")
        candidate["nominal_expiry"] = pd.to_datetime(candidate["nominal_expiry"], errors="coerce").dt.date
        source_cross = pd.read_csv(ROOT / "research" / "results" / "yahoo_daily_crosscheck.csv")
        source_cross["session_date"] = pd.to_datetime(source_cross["session_date"], errors="coerce").dt.date
        source_cross = source_cross[(source_cross["session_date"] >= start) & (source_cross["session_date"] <= end)].copy()
        official_index = official.set_index("session_date")
        official_map = official_index["official_close"].to_dict()
        source_cross["official_close"] = source_cross["session_date"].map(official_map)
        source_cross["official_abs_difference"] = (source_cross["session_close"] - source_cross["official_close"]).abs()
        source_cross["official_over_1pt"] = source_cross["official_abs_difference"] > 1.0
        for field in ("open", "high", "low"):
            official_col = f"official_{field}"
            minute_col = f"session_{field}"
            if official_col in official_index.columns:
                mapping = official_index[official_col].to_dict()
                source_cross[official_col] = source_cross["session_date"].map(mapping)
                source_cross[f"{field}_abs_difference"] = (source_cross[minute_col] - source_cross[official_col]).abs()
                source_cross[f"{field}_over_1pt"] = source_cross[f"{field}_abs_difference"] > 1.0
        source_cross.to_csv(OUT / "minute_vs_official_daily.csv", index=False)
        diagnostic_rows = source_cross.dropna(subset=["official_close"]).copy()
        diagnostic_rows["year"] = pd.to_datetime(diagnostic_rows["session_date"]).dt.year
        daily_summary_rows = []
        for year, group in diagnostic_rows.groupby("year", sort=True):
            row = {
                "year": int(year),
                "rows_compared": int(len(group)),
                "mismatches_over_1_point": int(group["official_over_1pt"].sum()),
                "median_abs_difference_points": float(group["official_abs_difference"].median()),
                "p95_abs_difference_points": float(group["official_abs_difference"].quantile(0.95)),
            }
            for field in ("open", "high", "low"):
                diff_col = f"{field}_abs_difference"
                if diff_col in group:
                    valid = group[diff_col].dropna()
                    row[f"{field}_mismatches_over_1_point"] = int((valid > 1.0).sum())
                    row[f"{field}_rows_compared"] = int(len(valid))
                    row[f"{field}_median_abs_difference_points"] = float(valid.median()) if len(valid) else None
            daily_summary_rows.append(row)
        pd.DataFrame(daily_summary_rows).to_csv(OUT / "daily_close_mismatch_summary_by_year.csv", index=False)
        candidate_dates = sorted(set(x for x in candidate["nominal_expiry"].dropna() if start <= x <= end))
        if max_expiries:
            candidate_dates = candidate_dates[:max_expiries]
        sessions = sorted(official_map)
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import threading
        local = threading.local()
        def get_fo_session() -> requests.Session:
            s = getattr(local, "session", None)
            if s is None:
                s = requests.Session()
                s.headers.update({
                    "User-Agent": UA,
                    "Accept": "*/*",
                    "Referer": "https://www.nseindia.com/all-reports-derivatives",
                })
                # NSE archives can return an HTML interstitial without a warmed session.
                try:
                    s.get("https://www.nseindia.com/all-reports-derivatives", timeout=(5, 8))
                except requests.RequestException:
                    pass
                local.session = s
            return s

        candidate_jobs: list[tuple[date, date]] = []
        for candidate_date in candidate_dates:
            possible = [d for d in sessions if d <= candidate_date]
            if possible:
                candidate_jobs.append((candidate_date, possible[-1]))

        def verify_candidate(job: tuple[date, date]) -> dict[str, Any]:
            candidate_date, actual = job
            checked_dates: list[str] = []
            source_errors: list[str] = []
            for verify_day in candidate_verification_sessions(candidate_date, sessions):
                checked_dates.append(verify_day.isoformat())
                try:
                    cache_file = CACHE / "fo" / f"fo_{verify_day:%Y%m%d}.zip"
                    if cache_file.exists() and not force:
                        blob = cache_file.read_bytes()
                    else:
                        blob = fetch_bhavcopy(verify_day, get_fo_session())
                        cache_file.parent.mkdir(parents=True, exist_ok=True)
                        cache_file.write_bytes(blob)
                    expiries = parse_bhavcopy_contract_expiries(blob, verify_day)
                    if verify_day in expiries:
                        shifted = verify_day != actual
                        return {
                            "candidate_date": candidate_date.isoformat(),
                            "candidate_previous_session": actual.isoformat(),
                            "verified_expiry_trade_date": verify_day.isoformat(),
                            "calendar_shift_days": (candidate_date - verify_day).days,
                            "contract_expiry_present": True,
                            "status": "verified_shifted_nifty_weekly_expiry" if shifted else "verified_nifty_weekly_expiry",
                            "checked_trade_dates": checked_dates,
                            "nifty_option_expiries_in_bhavcopy": sorted(x.isoformat() for x in expiries),
                        }
                except Exception as exc:
                    source_errors.append(f"{verify_day.isoformat()}: {type(exc).__name__}: {str(exc)[:260]}")
            if source_errors:
                return {
                    "candidate_date": candidate_date.isoformat(),
                    "candidate_previous_session": actual.isoformat(),
                    "status": "source_error",
                    "error_type": "SourceValidationError",
                    "error": " | ".join(source_errors)[:700],
                    "checked_trade_dates": checked_dates,
                }
            return {
                "candidate_date": candidate_date.isoformat(),
                "candidate_previous_session": actual.isoformat(),
                "contract_expiry_present": False,
                "status": "not_verified_in_bhavcopy",
                "checked_trade_dates": checked_dates,
                "nifty_option_expiries_in_bhavcopy": [],
            }
        verified: list[dict[str, Any]] = []
        # Four workers reduce a long sequential run while limiting pressure on NSE.
        # Work in bounded batches; if a whole batch has source failures, stop rather
        # than hammering a blocked endpoint across the remaining calendar.
        batch_size = 24
        with ThreadPoolExecutor(max_workers=4) as pool:
            for batch_start in range(0, len(candidate_jobs), batch_size):
                batch = candidate_jobs[batch_start:batch_start + batch_size]
                results = list(pool.map(verify_candidate, batch))
                verified.extend(results)
                batch_errors = sum(row.get("status") == "source_error" for row in results)
                if batch and batch_errors == len(batch):
                    for candidate_date in candidate_dates[len(verified):]:
                        verified.append({"candidate_date": candidate_date.isoformat(), "status": "source_unavailable_after_repeated_errors"})
                    break
        expiry_frame = pd.DataFrame(verified)
        expiry_frame.to_csv(OUT / "expiry_verification.csv", index=False)
        expiry_frame["year"] = pd.to_datetime(expiry_frame["candidate_date"], errors="coerce").dt.year
        is_verified = expiry_frame["status"].isin({"verified_nifty_weekly_expiry", "verified_shifted_nifty_weekly_expiry"})
        expiry_frame["_verified"] = is_verified.astype(int)
        expiry_frame["_source_error"] = expiry_frame["status"].eq("source_error").astype(int)
        expiry_frame["_not_verified"] = (~is_verified & ~expiry_frame["status"].eq("source_error")).astype(int)
        expiry_summary = expiry_frame.groupby("year", dropna=True).agg(
            expiry_candidates=("candidate_date", "count"),
            contract_verified=("_verified", "sum"),
            not_verified=("_not_verified", "sum"),
            source_errors=("_source_error", "sum"),
        ).reset_index()
        expiry_summary["year"] = expiry_summary["year"].astype(int)
        expiry_summary.to_csv(OUT / "expiry_verification_summary_by_year.csv", index=False)
        n = len(verified)
        good = sum(x.get("status") in {"verified_nifty_weekly_expiry", "verified_shifted_nifty_weekly_expiry"} for x in verified)
        errs = sum(x.get("status") == "source_error" for x in verified)
        cross_rows = source_cross.dropna(subset=["official_close"])
        mismatch = int(cross_rows["official_over_1pt"].sum())
        report["counts"] = {
            "official_daily_rows": len(official),
            "candidate_expiries_checked": n,
            "contract_verified_expiries": good,
            "contract_unverified_expiries": n - good - errs,
            "expiry_source_errors": errs,
            "daily_source_rows_expected": len(source_cross),
            "daily_source_rows_compared": len(cross_rows),
            "daily_source_rows_missing_official_close": int(source_cross["official_close"].isna().sum()),
            "minute_vs_official_mismatches_over_1_point": mismatch,
            "minute_vs_official_abs_difference_median_points": float(cross_rows["official_abs_difference"].median()) if len(cross_rows) else None,
            "minute_vs_official_abs_difference_p95_points": float(cross_rows["official_abs_difference"].quantile(0.95)) if len(cross_rows) else None,
            "minute_vs_official_abs_difference_max_points": float(cross_rows["official_abs_difference"].max()) if len(cross_rows) else None,
            "minute_vs_official_within_1_point": int((~cross_rows["official_over_1pt"]).sum()),
        }
        for field in ("open", "high", "low"):
            diff_col = f"{field}_abs_difference"
            if diff_col in source_cross:
                valid = source_cross[diff_col].dropna()
                report["counts"][f"minute_vs_official_{field}_rows_compared"] = int(len(valid))
                report["counts"][f"minute_vs_official_{field}_mismatches_over_1_point"] = int((valid > 1.0).sum())
                report["counts"][f"minute_vs_official_{field}_abs_difference_median_points"] = float(valid.median()) if len(valid) else None
        coverage_complete = len(cross_rows) == len(source_cross) and len(source_cross) > 0
        report["status"] = "PASS" if n > 0 and good == n and errs == 0 and mismatch == 0 and coverage_complete else "BLOCKED"
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
