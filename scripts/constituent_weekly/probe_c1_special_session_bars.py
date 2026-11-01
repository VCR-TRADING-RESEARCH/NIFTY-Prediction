from __future__ import annotations

import hashlib
import io
import json
import math
import time
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "research" / "constituent_weekly" / "C1_SPECIAL_SESSION_BAR_CROSSCHECK.json"
OUT_MD = ROOT / "research" / "constituent_weekly" / "C1_SPECIAL_SESSION_BAR_CROSSCHECK_REPORT.md"

# Pinned mirror repository documents its daily OHLCV inputs as NSE archive files.
# Downloaded raw data are processed only in the temporary Actions runner.
MIRROR_REPO = "floyds1995/Auto-Index-Constituents-Tracker"
MIRROR_REVISION = "aa57b1050383c33e436f81844230ad2a4d52c949"
TARGETS = [
    ("HDFC", "2018-11-07"),
    ("HDFC", "2019-10-27"),
    ("HDFC", "2020-02-01"),
    ("HDFC", "2020-11-14"),
    ("HDFC", "2021-11-04"),
    ("HDFC", "2022-10-24"),
    ("TATAMOTORS", "2025-10-21"),
]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; BUP01-research-audit/1.0)",
    "Accept": "text/csv,application/zip,application/octet-stream,*/*",
    "Accept-Encoding": "identity",
    "Referer": "https://www.nseindia.com/",
}
TIMEOUT = 45
REQUEST_PAUSE = 1.1


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def norm(value: Any) -> str:
    return str(value).strip().upper()


def column(frame: pd.DataFrame, *names: str) -> str | None:
    lookup = {norm(name): name for name in frame.columns}
    for name in names:
        if norm(name) in lookup:
            return lookup[norm(name)]
    return None


def normalize_nse_frame(raw: pd.DataFrame) -> pd.DataFrame:
    """Normalize legacy CM bhavcopy, sec_bhavdata_full, and UDIFF schemas."""
    date_col = column(raw, "DATE1", "TIMESTAMP", "TRDDT", "TRADDT", "DATE", "TradDt")
    symbol_col = column(raw, "SYMBOL", "TckrSymb")
    series_col = column(raw, "SERIES", "SctySrs")
    open_col = column(raw, "OPEN_PRICE", "OPEN", "OpnPric")
    high_col = column(raw, "HIGH_PRICE", "HIGH", "HghPric")
    low_col = column(raw, "LOW_PRICE", "LOW", "LwPric")
    close_col = column(raw, "CLOSE_PRICE", "CLOSE", "ClsPric")
    volume_col = column(raw, "TTL_TRD_QNTY", "TOTTRDQTY", "TtlTradgVol", "VOLUME")
    isin_col = column(raw, "ISIN", "ISINCode")
    if any(v is None for v in [
        date_col, symbol_col, series_col, open_col, high_col, low_col, close_col, volume_col
    ]):
        raise ValueError("Unsupported NSE bhavcopy schema")

    # ISO YYYY-MM-DD must be parsed explicitly; dayfirst=True can invert
    # its month/day fields (for example, 2020-02-01 -> 2020-01-02).
    date_text = raw[date_col].astype("string").str.strip()
    iso_mask = date_text.str.len().eq(10) & date_text.str.slice(4, 5).eq("-") & date_text.str.slice(7, 8).eq("-")
    parsed_dates = pd.Series(pd.NaT, index=raw.index, dtype="datetime64[ns]")
    if iso_mask.any():
        parsed_dates.loc[iso_mask] = pd.to_datetime(
            date_text.loc[iso_mask], format="%Y-%m-%d", errors="coerce"
        )
    if (~iso_mask).any():
        parsed_dates.loc[~iso_mask] = pd.to_datetime(
            date_text.loc[~iso_mask], errors="coerce", dayfirst=True
        )
    return pd.DataFrame({
        "date": parsed_dates.dt.strftime("%Y-%m-%d"),
        "symbol": raw[symbol_col].astype("string").str.strip().str.upper(),
        "series": raw[series_col].astype("string").str.strip().str.upper(),
        "open": pd.to_numeric(raw[open_col], errors="coerce"),
        "high": pd.to_numeric(raw[high_col], errors="coerce"),
        "low": pd.to_numeric(raw[low_col], errors="coerce"),
        "close": pd.to_numeric(raw[close_col], errors="coerce"),
        "volume": pd.to_numeric(raw[volume_col], errors="coerce"),
        "isin": raw[isin_col].astype("string").str.strip() if isin_col else pd.Series([pd.NA] * len(raw)),
    })


def row_digest(row: pd.Series) -> str:
    # Retain only a digest; do not publish the OHLCV values.
    payload = {
        "date": str(row["date"]),
        "symbol": norm(row["symbol"]),
        "series": norm(row["series"]),
        "open": f"{float(row['open']):.2f}",
        "high": f"{float(row['high']):.2f}",
        "low": f"{float(row['low']):.2f}",
        "close": f"{float(row['close']):.2f}",
        "volume": str(int(row["volume"])),
    }
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())


def validate_rows(rows: pd.DataFrame, symbol: str, session_date: str) -> dict[str, Any]:
    exact = rows.loc[
        rows["symbol"].astype(str).str.upper().eq(symbol)
        & rows["series"].astype(str).str.upper().eq("EQ")
        & rows["date"].astype(str).eq(session_date)
    ].copy()
    if len(exact) == 0:
        return {"status": "NO_EQ_ROW", "row_count": 0, "valid": False}
    if len(exact) != 1:
        return {"status": "DUPLICATE_EQ_ROWS", "row_count": int(len(exact)), "valid": False}

    row = exact.iloc[0]
    try:
        open_, high, low, close, volume = [float(row[k]) for k in ("open", "high", "low", "close", "volume")]
    except (TypeError, ValueError):
        return {"status": "NON_NUMERIC_OHLCV", "row_count": 1, "valid": False}
    finite = all(math.isfinite(v) for v in (open_, high, low, close, volume))
    valid_ohlc = (
        finite and all(v > 0 for v in (open_, high, low, close))
        and low <= min(open_, close) and high >= max(open_, close) and high >= low
    )
    valid_volume = finite and volume >= 0 and volume.is_integer()
    valid = bool(valid_ohlc and valid_volume)
    return {
        "status": "VALID" if valid else "INVALID_OHLCV",
        "row_count": 1,
        "valid": valid,
        "ohlc_valid": bool(valid_ohlc),
        "volume_valid": bool(valid_volume),
        "isin_present": bool(pd.notna(row["isin"]) and str(row["isin"]).strip()),
        "row_sha256": row_digest(row) if valid else None,
    }


def fetch_mirror_month(session: requests.Session, month: str):
    filename = f"{month}.parquet"
    url = (
        f"https://raw.githubusercontent.com/{MIRROR_REPO}/"
        f"{MIRROR_REVISION}/NSE/RawDataOHLCV/parquet/{filename}"
    )
    try:
        response = session.get(url, timeout=TIMEOUT)
    except requests.RequestException as exc:
        return None, {"status": "NETWORK_ERROR", "error_type": type(exc).__name__}
    if response.status_code != 200:
        return None, {"status": f"HTTP_{response.status_code}"}
    content = response.content
    if len(content) < 1000:
        return None, {"status": "EMPTY_OR_INVALID_FILE"}
    try:
        frame = pd.read_parquet(
            io.BytesIO(content),
            columns=["SYMBOL", "SERIES", "DATE", "OPEN", "HIGH", "LOW", "CLOSE", "VOLUME", "ISIN"],
        )
    except Exception as exc:
        return None, {"status": "PARQUET_READ_ERROR", "error_type": type(exc).__name__}
    frame = frame.rename(columns={c: c.lower() for c in frame.columns})
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    frame["symbol"] = frame["symbol"].astype("string").str.strip().str.upper()
    frame["series"] = frame["series"].astype("string").str.strip().str.upper()
    meta = {
        "status": "LOADED",
        "http_status": int(response.status_code),
        "bytes": len(content),
        "file_sha256": sha256(content),
        "row_count": int(len(frame)),
        "filename": filename,
    }
    return frame, meta


def nse_urls(day: date) -> list[tuple[str, str]]:
    modern = (
        "https://nsearchives.nseindia.com/products/content/"
        f"sec_bhavdata_full_{day.day:02d}{day.month:02d}{day.year}.csv"
    )
    month = day.strftime("%b").upper()
    legacy = (
        "https://nsearchives.nseindia.com/content/historical/EQUITIES/"
        f"{day.year}/{month}/cm{day.day:02d}{month}{day.year}bhav.csv.zip"
    )
    return [("sec_bhavdata_full", modern), ("legacy_cm_bhavcopy", legacy)]


def parse_nse_response(content: bytes) -> pd.DataFrame:
    if content[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            csvs = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if not csvs:
                raise ValueError("ZIP contains no CSV")
            with archive.open(csvs[0]) as handle:
                raw = pd.read_csv(handle)
    else:
        if content.lstrip().startswith(b"<"):
            raise ValueError("HTML response, not a CSV")
        raw = pd.read_csv(io.BytesIO(content))
    return normalize_nse_frame(raw)


def fetch_direct_nse(session: requests.Session, symbol: str, session_date: str) -> dict[str, Any]:
    day = date.fromisoformat(session_date)
    attempts = []
    for source_name, url in nse_urls(day):
        try:
            response = session.get(url, timeout=TIMEOUT)
            if response.status_code != 200:
                attempts.append({"source": source_name, "http_status": int(response.status_code)})
            else:
                try:
                    frame = parse_nse_response(response.content)
                    checked = validate_rows(frame, symbol, session_date)
                    attempts.append({
                        "source": source_name,
                        "http_status": 200,
                        "response_sha256": sha256(response.content),
                        **checked,
                    })
                    if checked.get("valid"):
                        return {
                            "status": "VALID_OFFICIAL_NSE_ROW",
                            "selected_source": source_name,
                            "attempts": attempts,
                            "row_sha256": checked["row_sha256"],
                            "isin_present": checked["isin_present"],
                        }
                except Exception as exc:
                    attempts.append({
                        "source": source_name,
                        "http_status": 200,
                        "response_sha256": sha256(response.content),
                        "parse_status": "PARSE_ERROR",
                        "error_type": type(exc).__name__,
                    })
        except requests.RequestException as exc:
            attempts.append({"source": source_name, "error_type": type(exc).__name__})
        time.sleep(REQUEST_PAUSE)
    return {"status": "NO_VALID_OFFICIAL_ROW", "attempts": attempts}


def main() -> int:
    session = requests.Session()
    session.headers.update(HEADERS)
    frames: dict[str, pd.DataFrame | None] = {}
    mirror_files: dict[str, dict[str, Any]] = {}
    results = []

    for symbol, session_date in TARGETS:
        month = session_date[:7]
        if month not in frames:
            frames[month], mirror_files[month] = fetch_mirror_month(session, month)
        frame = frames[month]
        mirror = (
            validate_rows(frame, symbol, session_date)
            if frame is not None
            else {"status": mirror_files[month]["status"], "row_count": 0, "valid": False}
        )
        mirror_hash = mirror.pop("row_sha256", None)
        direct = fetch_direct_nse(session, symbol, session_date)
        direct_hash = direct.get("row_sha256")
        mirror_match = bool(mirror_hash and direct_hash and mirror_hash == direct_hash)
        if direct.get("status") == "VALID_OFFICIAL_NSE_ROW":
            disposition = "DIRECT_NSE_VALIDATED"
            if mirror.get("valid") and mirror_match:
                disposition = "DIRECT_NSE_AND_PINNED_MIRROR_MATCH"
        elif mirror.get("valid"):
            disposition = "MIRROR_ONLY_NOT_ACCEPTED"
        else:
            disposition = "UNRESOLVED"
        results.append({
            "symbol": symbol,
            "date": session_date,
            "series_expected": "EQ",
            "issuer": "HDFC Limited" if symbol == "HDFC" else "Tata Motors Passenger Vehicles Limited (dated alias TMPV)",
            "mirror": {**mirror, "file": f"{month}.parquet", "row_sha256": mirror_hash},
            "direct_nse": direct,
            "mirror_exact_match_to_nse": mirror_match,
            "disposition": disposition,
        })
        time.sleep(REQUEST_PAUSE)

    valid_direct = sum(r["direct_nse"].get("status") == "VALID_OFFICIAL_NSE_ROW" for r in results)
    valid_mirror = sum(r["mirror"].get("valid", False) for r in results)
    exact_mirror = sum(r["mirror_exact_match_to_nse"] for r in results)
    unresolved = sum(r["disposition"] == "UNRESOLVED" for r in results)
    status = (
        "ALL_SEVEN_DIRECT_NSE_ROWS_VALID" if valid_direct == 7
        else "PARTIAL_DIRECT_NSE_COVERAGE" if valid_direct
        else "NO_DIRECT_NSE_ROWS_VALID"
    )
    report = {
        "schema_version": 1,
        "methodology": "c1-special-session-source-crosscheck-v1",
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "source_controls": {
            "mirror_repository": MIRROR_REPO,
            "mirror_revision": MIRROR_REVISION,
            "raw_data_persisted": False,
            "raw_data_redistributed": False,
            "market_data_licence": "No separate market-data licence identified; software MIT only; raw files temporary-only",
        },
        "summary": {
            "targets": len(TARGETS),
            "valid_direct_nse_rows": int(valid_direct),
            "valid_mirror_rows": int(valid_mirror),
            "exact_mirror_matches_to_direct_nse": int(exact_mirror),
            "unresolved_pairs": int(unresolved),
        },
        "mirror_files": mirror_files,
        "results": results,
        "limitations": [
            "The pinned mirror maintainer documents NSE archive inputs, but its MIT software licence is not a market-data licence.",
            "A mirror-only row is not accepted as a confirmed observation; direct exchange evidence remains required.",
            "The mirror collector enumerates weekdays, so absence of weekend Muhurat or Budget sessions is not evidence that the exchange archive lacks them.",
            "A valid daily bar does not close point-in-time security identity, membership, or corporate-action continuity gates.",
            "No OHLCV values are persisted in this report.",
        ],
    }

    lines = [
        "# C1 Special-Session OHLCV Cross-Check",
        "",
        f"**Updated:** {report['updated_at_utc']}",
        f"**Status:** {status}",
        "",
        "## Source controls",
        "",
        f"- Pinned mirror: {MIRROR_REPO} at revision {MIRROR_REVISION}.",
        "- The mirror maintainer documents daily OHLCV downloads from NSE archive endpoints.",
        "- Direct NSE daily files are queried separately for each security/date.",
        "- Raw data are processed in temporary runner storage only; no price/volume values are published or cached.",
        "- The mirror repository's MIT licence covers software; no separate market-data licence was identified.",
        "",
        "## Results",
        "",
        "| Security/date | Mirror result | Direct NSE result | Disposition |",
        "|---|---|---|---|",
    ]
    for item in results:
        lines.append(
            f"| {item['symbol']} {item['date']} | {item['mirror'].get('status')} | "
            f"{item['direct_nse'].get('status')} | {item['disposition']} |"
        )
    lines += [
        "",
        "## Summary",
        "",
        f"- Direct NSE rows valid: {valid_direct}/7.",
        f"- Valid mirror rows: {valid_mirror}/7.",
        f"- Exact mirror-to-NSE matches: {exact_mirror}/7.",
        f"- Unresolved security/date pairs: {unresolved}.",
        "- No denominator change, no imputation, and no daily coverage pass is inferred from calendar classification.",
        "- C1 corporate-action validation remains a separate blocker.",
        "",
        "## Reproducibility",
        "",
        f"- Mirror revision: {MIRROR_REVISION}.",
    ]
    for name, meta in sorted(mirror_files.items()):
        lines.append(
            f"- {name}.parquet: status {meta.get('status')}; SHA-256 {meta.get('file_sha256', 'unavailable')}."
        )
    lines.append("")

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("C1_SPECIAL_SESSION_CROSSCHECK", status)
    print("DIRECT_NSE_VALID", valid_direct, "MIRROR_VALID", valid_mirror,
          "EXACT_MIRROR_MATCH", exact_mirror, "UNRESOLVED", unresolved)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
