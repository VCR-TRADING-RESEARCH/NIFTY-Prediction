#!/usr/bin/env python3
"""Fetch a public NIFTY 50 one-minute data archive; raw files remain in Actions cache."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "data" / "raw" / "nifty50"
API_ROOT = "https://api.github.com/repos/technovusin/nifty50-historical-data/contents/1min?ref=main"
MANIFEST = ROOT / "data" / "processed" / "source_manifest.json"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "NIFTY-Prediction-Research/1.0", "Accept": "application/vnd.github+json"})
if os.getenv("GITHUB_TOKEN"):
    SESSION.headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]


def get_json(url: str) -> Any:
    response = SESSION.get(url, timeout=60)
    response.raise_for_status()
    return response.json()


def download(url: str, path: Path, force: bool = False) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0 and not force:
        payload = path.read_bytes()
        downloaded = False
    else:
        response = SESSION.get(url, timeout=180)
        response.raise_for_status()
        payload = response.content
        if not payload or len(payload) < 100:
            raise RuntimeError("Downloaded file appears empty or too small: " + path.name)
        path.write_bytes(payload)
        downloaded = True
    return {
        "filename": path.name,
        "source_url": url,
        "local_path": str(path.relative_to(ROOT)),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "downloaded_this_run": downloaded,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
    }


def source_files() -> list[dict[str, Any]]:
    entries = get_json(API_ROOT)
    candidates: list[dict[str, Any]] = []
    for folder in entries:
        if folder.get("type") != "dir" or not folder.get("name", "").isdigit():
            continue
        year = int(folder["name"])
        if year < 2017:
            continue
        children = get_json(folder["url"])
        csvs = [entry for entry in children if entry.get("type") == "file" and entry.get("name", "").lower().endswith(".csv")]
        # Older folders normally contain one yearly file; newer/current folders may contain monthly files.
        for entry in csvs:
            name = entry.get("name", "")
            if not entry.get("download_url"):
                continue
            candidates.append({
                "year": year,
                "name": name,
                "download_url": entry["download_url"],
                "force_refresh": year == datetime.now().year,
            })
    candidates.sort(key=lambda x: (x["year"], x["name"]))
    return candidates


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--force", action="store_true", help="Redownload all source files")
    parser.add_argument("--max-files", type=int, default=0, help="Testing only: limit number of CSV files")
    args = parser.parse_args()
    args.output_dir = args.output_dir.resolve()

    try:
        candidates = source_files()
        if args.max_files > 0:
            candidates = candidates[-args.max_files:]
        if not candidates:
            raise RuntimeError("No CSV files found under the upstream 1min archive")
        records = []
        for item in candidates:
            dest = args.output_dir / item["name"]
            should_refresh = args.force or item["force_refresh"]
            record = download(item["download_url"], dest, force=should_refresh)
            record["year"] = item["year"]
            records.append(record)
            print("Data file ready:", record["filename"], "bytes=", record["bytes"], "downloaded=", record["downloaded_this_run"])
        manifest = {
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "source_repository": "https://github.com/technovusin/nifty50-historical-data",
            "source_license_note": "Upstream repository publishes MIT license; underlying market-data redistribution rights are not independently established.",
            "files": records,
        }
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print("Source manifest written:", MANIFEST.relative_to(ROOT))
        print("CSV file count:", len(records))
        return 0
    except Exception as exc:
        # Avoid dumping request URLs containing credentials; this source fetch does not use secrets.
        print("DATA_FETCH_ERROR:", type(exc).__name__, str(exc)[:500], file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
