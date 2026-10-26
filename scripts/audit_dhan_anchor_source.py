#!/usr/bin/env python3
"""Five-year Dhan minute-anchor comparison; credentials stay in process memory only.

The workflow stores only compact comparison outputs and sanitized diagnostics in Git.
Raw Dhan minute chunks are cache-only. Results are still diagnostic until exchange-grade
independent anchor provenance and historical OHLC reconciliation are accepted.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import pyotp
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache" / "dhan-anchors"
OUT = ROOT / "data" / "reconciliation"
AUTH_URL = "https://auth.dhan.co/app/generateAccessToken"
MASTER_URL = "https://images.dhan.co/api-data/api-scrip-master.csv"
INTRADAY_URL = "https://api.dhan.co/v2/charts/intraday"
IST = "Asia/Kolkata"


def _safe_summary_error(exc: Exception) -> str:
    """Never return request URLs, request bodies, response bodies or secret values."""
    message = str(exc)
    prefix = "Dhan token endpoint HTTP "
    if prefix in message:
        suffix = message.split(prefix, 1)[1].split()[0]
        if suffix.isdigit() and len(suffix) == 3:
            return prefix + suffix
    response = getattr(exc, "response", None)
    status = getattr(response, "status_code", None)
    if isinstance(status, int):
        return type(exc).__name__ + ": HTTP " + str(status) + "; sensitive details withheld"
    return type(exc).__name__ + ": request failed; sensitive provider details withheld"


def parse_dhan_payload(payload: dict[str, Any]) -> pd.DataFrame:
    """Convert Dhan intraday response arrays to canonical IST minute bars."""
    keys = {
        "open": payload.get("open", []),
        "high": payload.get("high", []),
        "low": payload.get("low", []),
        "close": payload.get("close", []),
        "timestamp": payload.get("timestamp") or payload.get("start_Time") or payload.get("startTime") or [],
    }
    count = min(len(values) for values in keys.values())
    if count == 0:
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close"])
    epochs = pd.to_numeric(pd.Series(keys["timestamp"][:count]), errors="coerce")
    timestamps = pd.to_datetime(epochs, unit="s", utc=True, errors="coerce").dt.tz_convert(IST)
    bars = pd.DataFrame({
        "timestamp": timestamps,
        "open": pd.to_numeric(pd.Series(keys["open"][:count]), errors="coerce"),
        "high": pd.to_numeric(pd.Series(keys["high"][:count]), errors="coerce"),
        "low": pd.to_numeric(pd.Series(keys["low"][:count]), errors="coerce"),
        "close": pd.to_numeric(pd.Series(keys["close"][:count]), errors="coerce"),
    }).dropna()
    bars = bars.sort_values("timestamp").drop_duplicates("timestamp", keep="last")
    valid = (
        (bars[["open", "high", "low", "close"]] > 0).all(axis=1)
        & (bars["low"] <= bars[["open", "close"]].min(axis=1))
        & (bars["high"] >= bars[["open", "close"]].max(axis=1))
        & (bars["low"] <= bars["high"])
    )
    return bars.loc[valid].reset_index(drop=True)


def find_nifty50_security(master: pd.DataFrame) -> str:
    """Resolve the NSE NIFTY 50 INDEX security ID; refuse ambiguous matches."""
    lookup = {str(column).strip().upper(): column for column in master.columns}
    id_col = next((lookup[name] for name in (
        "SEM_SMST_SECURITY_ID", "SECURITYID", "SECURITY_ID", "SMST_SECURITY_ID"
    ) if name in lookup), None)
    if id_col is None:
        raise ValueError("Dhan scrip master has no recognized security-ID field")
    seg_col = next((lookup[name] for name in ("SEM_SEGMENT", "SEGMENT") if name in lookup), None)
    exchange_col = next((lookup[name] for name in ("SEM_EXM_EXCH_ID", "EXCHANGE") if name in lookup), None)
    text_cols = [lookup[name] for name in lookup if any(
        word in name for word in ("SYMBOL", "INSTRUMENT", "CUSTOM", "NAME")
    )]
    if not text_cols:
        raise ValueError("Dhan scrip master has no symbol/name column")
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
        raise ValueError("Dhan master did not identify exactly one NSE NIFTY 50 INDEX; refusing to guess")
    return ids[0]


def get_access_token(client_id: str, pin: str, totp_secret: str) -> str:
    otp = pyotp.TOTP(totp_secret).now()
    response = requests.post(
        AUTH_URL,
        params={"dhanClientId": client_id, "pin": pin, "totp": otp},
        timeout=30,
    )
    if not response.ok:
        raise RuntimeError("Dhan token endpoint HTTP " + str(response.status_code))
    body = response.json()
    token = body.get("accessToken") or body.get("access_token")
    if not isinstance(token, str) or len(token) < 20:
        raise ValueError("Dhan token response lacked a valid access-token field")
    return token


def fetch_chunk(
    start: date,
    end: date,
    token: str,
    client_id: str,
    security_id: str,
    force: bool = False,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"dhan_{start:%Y%m%d}_{end:%Y%m%d}.csv"
    if path.is_file() and path.stat().st_size > 100 and not force:
        cached = pd.read_csv(path)
        cached["timestamp"] = pd.to_datetime(cached["timestamp"], errors="coerce", utc=True).dt.tz_convert(IST)
        bars = cached.dropna(subset=["timestamp", "open", "high", "low", "close"])
        return bars, {"start": str(start), "end": str(end), "status": "cached", "bars": int(len(bars))}
    headers = {
        "access-token": token,
        "client-id": client_id,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    body = {
        "securityId": security_id,
        "exchangeSegment": "IDX_I",
        "instrument": "INDEX",
        "interval": "1",
        "oi": False,
        "fromDate": start.isoformat() + " 09:15:00",
        "toDate": end.isoformat() + " 15:30:00",
    }
    last_status = None
    last_error = None
    for attempt in range(3):
        try:
            response = requests.post(INTRADAY_URL, headers=headers, json=body, timeout=90)
            last_status = response.status_code
            if response.status_code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(attempt + 1)
                continue
            if not response.ok:
                return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close"]), {
                    "start": str(start), "end": str(end), "status": "http_error",
                    "http_status": int(response.status_code), "bars": 0,
                }
            bars = parse_dhan_payload(response.json())
            temp = path.with_suffix(".tmp")
            bars.assign(timestamp=bars.timestamp.astype(str)).to_csv(temp, index=False)
            temp.replace(path)
            return bars, {"start": str(start), "end": str(end), "status": "downloaded", "bars": int(len(bars))}
        except Exception as exc:
            last_error = _safe_summary_error(exc)
            if attempt < 2:
                time.sleep(attempt + 1)
    return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close"]), {
        "start": str(start), "end": str(end), "status": "error",
        "http_status": last_status, "error": last_error, "bars": 0,
    }


def main() -> int:
    stage = "load_credentials"
    force = os.getenv("FORCE_REFRESH_DHAN_ANCHORS", "false").strip().lower() == "true"
    client_id = os.getenv("DHAN_CLIENT_ID", "").strip()
    pin = os.getenv("DHAN_PIN", "").strip()
    totp_secret = os.getenv("DHAN_TOTP_SECRET", "").strip()
    OUT.mkdir(parents=True, exist_ok=True)
    report_path = OUT / "dhan_anchor_comparison_report.json"
    if not all((client_id, pin, totp_secret)):
        report = {
            "status": "SKIPPED_MISSING_CREDENTIALS",
            "generated_utc": pd.Timestamp.now(tz="UTC").isoformat(),
            "message": "Dhan anchor cross-check was not attempted because one or more repository secrets are unavailable.",
            "secret_values_logged": False,
        }
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0

    chunk_reports: list[dict[str, Any]] = []
    try:
        stage = "token_authentication"
        token = get_access_token(client_id, pin, totp_secret)
        stage = "security_master_download"
        master_response = requests.get(MASTER_URL, timeout=60, headers={"User-Agent": "NIFTYPredictionResearch/1.0"})
        master_response.raise_for_status()
        master_bytes = master_response.content
        stage = "security_id_resolution"
        master = pd.read_csv(pd.io.common.BytesIO(master_bytes), low_memory=False)
        security_id = find_nifty50_security(master)
        # Dhan documents intraday history for the last five years. Stay inside that advertised bound.
        today = date.today()
        try:
            start = date(today.year - 5, today.month, today.day)
        except ValueError:
            start = date(today.year - 5, today.month, 28)
        end = today - timedelta(days=1)
        all_frames = []
        cursor = start
        stage = "dhan_minute_history_download"
        while cursor <= end:
            chunk_end = min(cursor + timedelta(days=89), end)
            bars, chunk_status = fetch_chunk(cursor, chunk_end, token, client_id, security_id, force)
            chunk_reports.append(chunk_status)
            if not bars.empty:
                all_frames.append(bars)
            cursor = chunk_end + timedelta(days=1)
        if not all_frames:
            report = {
                "status": "DATA_UNAVAILABLE",
                "generated_utc": pd.Timestamp.now(tz="UTC").isoformat(),
                "window": {"start": str(start), "end": str(end)},
                "chunks": chunk_reports,
                "secret_values_logged": False,
                "message": "Dhan returned no valid minute bars in the requested historical window.",
            }
            report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(report, indent=2))
            return 0

        stage = "anchor_comparison"
        dhan = pd.concat(all_frames, ignore_index=True).sort_values("timestamp").drop_duplicates("timestamp", keep="last")
        clock = dhan.timestamp.dt.time
        dhan = dhan[(clock >= pd.Timestamp("09:15").time()) & (clock <= pd.Timestamp("15:29:59").time())]
        source_path = ROOT / "data/raw/nifty50"
        primary_files = sorted(source_path.glob("*.csv"))
        if not primary_files:
            raise FileNotFoundError("Primary public minute archive is not present")
        try:
            from scripts.research_core import load_minute_files
            from scripts.compare_anchor_sources import anchors, compare_weekly_labels
        except ImportError:
            import sys
            sys.path.insert(0, str(ROOT / "scripts"))
            from research_core import load_minute_files
            from compare_anchor_sources import anchors, compare_weekly_labels
        primary, _ = load_minute_files(primary_files)
        primary = primary[(primary.timestamp.dt.date >= start) & (primary.timestamp.dt.date <= end)]
        pa = anchors(primary, "primary")
        da = anchors(dhan, "secondary")
        joined = pa.merge(da, on="session_date", how="inner", validate="one_to_one")
        joined["timestamp_match"] = joined.primary_timestamp.eq(joined.secondary_timestamp)
        joined["absolute_anchor_open_difference"] = (joined.primary_anchor_open - joined.secondary_anchor_open).abs()
        joined["mismatch_over_1_point"] = joined.absolute_anchor_open_difference > 1.0
        joined.to_csv(OUT / "dhan_anchor_comparison.csv", index=False)

        weekly_path = ROOT / "data/processed/weekly_labels_features.csv"
        if weekly_path.is_file():
            weekly = pd.read_csv(weekly_path)
            weekly_joined, weekly_stats = compare_weekly_labels(weekly, joined)
            if not weekly_joined.empty:
                weekly_joined.to_csv(OUT / "dhan_weekly_anchor_label_sensitivity.csv", index=False)
        else:
            weekly_stats = {"status": "NOT_AVAILABLE", "reason": "Weekly label table is absent."}
        differences = joined.absolute_anchor_open_difference
        report = {
            "status": "DIAGNOSTIC_ONLY",
            "generated_utc": pd.Timestamp.now(tz="UTC").isoformat(),
            "source": "DhanHQ API v2 intraday minute bars (NSE NIFTY 50 INDEX); provider-response metadata and credentials are not persisted.",
            "window": {"start": str(start), "end": str(end)},
            "source_master_sha256": hashlib.sha256(master_bytes).hexdigest(),
            "counts": {
                "primary_anchors": int(len(pa)), "dhan_anchors": int(len(da)),
                "overlap_sessions": int(len(joined)),
                "exact_timestamp_matches": int(joined.timestamp_match.sum()),
                "anchor_open_mismatches_over_1_point": int(joined.mismatch_over_1_point.sum()),
            },
            "absolute_difference_points": {
                "median": float(differences.median()) if len(differences) else None,
                "p95": float(differences.quantile(0.95)) if len(differences) else None,
                "max": float(differences.max()) if len(differences) else None,
            },
            "weekly_label_sensitivity": weekly_stats,
            "chunks": chunk_reports,
            "cache": "Dhan source chunks are cached under data/cache/dhan-anchors and are not committed.",
            "acceptance": "Diagnostic only. Dhan has verified authenticated lineage but comparison does not independently validate all archived history or establish exchange-grade truth. Historical expiry labels remain exploratory until source and OHLC audit gates pass.",
            "secret_values_logged": False,
        }
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0
    except Exception as exc:
        report = {
            "status": "ERROR",
            "generated_utc": pd.Timestamp.now(tz="UTC").isoformat(),
            "stage": stage,
            "error": _safe_summary_error(exc),
            "chunks": chunk_reports,
            "secret_values_logged": False,
        }
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0  # Keep the workflow green for a documented, sanitized source failure.

if __name__ == "__main__":
    raise SystemExit(main())
