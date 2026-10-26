#!/usr/bin/env python3
"""Ensure a complete five-year Dhan minute-history cache exists for Phase 10.

Raw bars remain under data/cache/dhan-anchors and must not be committed.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache" / "dhan-anchors"
OUT = ROOT / "data" / "processed" / "dhan_history_manifest.json"
MASTER_URL = "https://images.dhan.co/api-data/api-scrip-master.csv"


def _window() -> tuple[date, date, list[tuple[date, date, Path]]]:
    end = date.today() - timedelta(days=1)
    today = date.today()
    try:
        start = date(today.year - 5, today.month, today.day)
    except ValueError:
        start = date(today.year - 5, today.month, 28)
    chunks: list[tuple[date, date, Path]] = []
    cursor = start
    while cursor <= end:
        chunk_end = min(cursor + timedelta(days=89), end)
        chunks.append((cursor, chunk_end, CACHE / f"dhan_{cursor:%Y%m%d}_{chunk_end:%Y%m%d}.csv"))
        cursor = chunk_end + timedelta(days=1)
    return start, end, chunks


def _cached_chunk(path: Path) -> dict[str, Any]:
    frame = pd.read_csv(path, low_memory=False)
    required = {"timestamp", "open", "high", "low", "close"}
    if not required.issubset(frame.columns):
        raise ValueError("Cached Dhan chunk lacks canonical OHLC columns: " + path.name)
    ts = pd.to_datetime(frame["timestamp"], errors="coerce", utc=True).dt.tz_convert("Asia/Kolkata")
    valid = ts.notna() & (pd.to_numeric(frame["open"], errors="coerce") > 0)
    if not valid.any():
        raise ValueError("Cached Dhan chunk has no valid timestamp/price rows: " + path.name)
    payload = path.read_bytes()
    return {
        "file": path.name,
        "status": "cached",
        "rows": int(len(frame)),
        "bytes": int(len(payload)),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "first_timestamp": ts.loc[valid].min().isoformat(),
        "last_timestamp": ts.loc[valid].max().isoformat(),
    }


def main() -> int:
    force = os.getenv("FORCE_REFRESH_DHAN_ANCHORS", "false").strip().lower() == "true"
    start, end, chunks = _window()
    CACHE.mkdir(parents=True, exist_ok=True)
    manifest_chunks: list[dict[str, Any]] = []
    missing = [(a, b, p) for a, b, p in chunks if force or not p.is_file() or p.stat().st_size <= 100]
    downloaded_count = 0
    if missing:
        client_id = os.getenv("DHAN_CLIENT_ID", "").strip()
        pin = os.getenv("DHAN_PIN", "").strip()
        secret = os.getenv("DHAN_TOTP_SECRET", "").strip()
        if not all((client_id, pin, secret)):
            report = {
                "status": "BLOCKED_MISSING_DHAN_CACHE_OR_CREDENTIALS",
                "generated_utc": pd.Timestamp.now(tz="UTC").isoformat(),
                "window": {"start": str(start), "end": str(end)},
                "expected_chunks": len(chunks),
                "missing_chunk_count": len(missing),
                "message": "The complete five-year Dhan cache is not present and required authentication secrets are unavailable.",
                "secret_values_logged": False,
            }
            OUT.parent.mkdir(parents=True, exist_ok=True)
            OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(report, indent=2))
            return 2
        try:
            from scripts.audit_dhan_anchor_source import get_access_token, find_nifty50_security, fetch_chunk
        except ImportError:
            sys.path.insert(0, str(ROOT / "scripts"))
            from audit_dhan_anchor_source import get_access_token, find_nifty50_security, fetch_chunk

        token = get_access_token(client_id, pin, secret)
        master_response = requests.get(MASTER_URL, timeout=60, headers={"User-Agent": "NIFTYPredictionResearch/1.0"})
        master_response.raise_for_status()
        master_bytes = master_response.content
        master = pd.read_csv(pd.io.common.BytesIO(master_bytes), low_memory=False)
        security_id = find_nifty50_security(master)
        for chunk_start, chunk_end, path in chunks:
            if not force and path.is_file() and path.stat().st_size > 100:
                continue
            bars, item = fetch_chunk(chunk_start, chunk_end, token, client_id, security_id, force=True)
            if item.get("status") != "downloaded" or bars.empty:
                manifest_chunks.append(item)
                raise RuntimeError("Dhan history fetch failed for chunk " + path.name + "; sanitized status=" + str(item.get("status")))
            downloaded_count += 1
    for chunk_start, chunk_end, path in chunks:
        if not path.is_file() or path.stat().st_size <= 100:
            raise FileNotFoundError("Expected five-year Dhan chunk is missing: " + path.name)
        manifest_chunks.append(_cached_chunk(path))
    first_times = [item["first_timestamp"] for item in manifest_chunks if item.get("first_timestamp")]
    last_times = [item["last_timestamp"] for item in manifest_chunks if item.get("last_timestamp")]
    report = {
        "status": "READY",
        "generated_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "source": "Authenticated DhanHQ v2 NIFTY 50 INDEX one-minute history",
        "window": {"start": str(start), "end": str(end)},
        "expected_chunks": len(chunks),
        "chunks_ready": len(manifest_chunks),
        "chunks_downloaded_this_run": int(downloaded_count),
        "total_raw_rows": int(sum(item.get("rows", 0) for item in manifest_chunks)),
        "first_timestamp": min(first_times) if first_times else None,
        "last_timestamp": max(last_times) if last_times else None,
        "chunks": manifest_chunks,
        "cache_path": "data/cache/dhan-anchors (never committed)",
        "secret_values_logged": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "chunks"}, indent=2))
    if len(manifest_chunks) != len(chunks) or not first_times or not last_times:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
