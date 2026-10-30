#!/usr/bin/env python3
"""Download/cache and audit candidate NIFTY option parquet partitions.

This is a DATA GATE only. It deliberately does not calculate strategy P&L.
"""
from __future__ import annotations
import json, os, hashlib
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
from huggingface_hub import hf_hub_download

REPO_ID = "rissin/nse-options-intraday"
YEARS = (2024, 2025, 2026)
CACHE = Path(os.environ.get("HF_DATASETS_CACHE", ".cache/hf-options"))
OUT = Path("research/options_backtest/data_audit.json")

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> None:
    import pyarrow.parquet as pq
    CACHE.mkdir(parents=True, exist_ok=True)
    reports = []
    for year in YEARS:
        name = f"upstox_intraday/NIFTY/NIFTY_{year}.parquet"
        path = Path(hf_hub_download(
            repo_id=REPO_ID, filename=name, repo_type="dataset",
            token=os.environ.get("HF_TOKEN") or None,
            cache_dir=str(CACHE),
        ))
        pf = pq.ParquetFile(path)
        required = {"date","timestamp","underlying","expiry","strike","option_type",
                    "open","high","low","close","volume","granularity"}
        schema = set(pf.schema.names)
        missing = sorted(required - schema)
        if missing:
            raise RuntimeError(f"{name}: required columns missing: {missing}")
        total_rows = 0
        nifty_rows = 0
        one_min_rows = 0
        null_ohlc = 0
        nonpositive_ohlc = 0
        malformed_ohlc = 0
        null_oi = 0
        null_volume = 0
        zero_volume = 0
        negative_volume = 0
        invalid_timestamps = 0
        min_ts = max_ts = None
        min_expiry = max_expiry = None
        for batch in pf.iter_batches(batch_size=250_000, columns=sorted(required)):
            df = batch.to_pandas()
            total_rows += len(df)
            df = df[(df["underlying"].astype(str).str.upper() == "NIFTY")]
            nifty_rows += len(df)
            df = df[df["granularity"].astype(str).str.lower().isin(["1min","1m"])]
            one_min_rows += len(df)
            if df.empty:
                continue
            ohlc = ["open","high","low","close"]
            null_ohlc += int(df[ohlc].isna().any(axis=1).sum())
            nonpositive_ohlc += int((df[ohlc] <= 0).any(axis=1).sum())
            if "oi" in df.columns:
                null_oi += int(pd.to_numeric(df["oi"], errors="coerce").isna().sum())
            else:
                null_oi += int(len(df))
            volume_values = pd.to_numeric(df["volume"], errors="coerce")
            null_volume += int(volume_values.isna().sum())
            zero_volume += int((volume_values == 0).sum())
            negative_volume += int((volume_values < 0).sum())
            malformed_ohlc += int(((df["low"] > df[["open","close","high"]].min(axis=1)) |
                                   (df["high"] < df[["open","close","low"]].max(axis=1))).sum())
            ts = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
            invalid_timestamps += int(ts.isna().sum())
            lo, hi = ts.min(), ts.max()
            if pd.notna(lo): min_ts = lo if min_ts is None else min(min_ts, lo)
            if pd.notna(hi): max_ts = hi if max_ts is None else max(max_ts, hi)
            ex = pd.to_datetime(df["expiry"], errors="coerce")
            elo, ehi = ex.min(), ex.max()
            if pd.notna(elo): min_expiry = elo if min_expiry is None else min(min_expiry, elo)
            if pd.notna(ehi): max_expiry = ehi if max_expiry is None else max(max_expiry, ehi)
        reports.append({
            "file": name, "bytes": path.stat().st_size, "sha256": sha256(path),
            "parquet_rows": pf.metadata.num_rows, "scanned_rows": total_rows,
            "nifty_rows": nifty_rows, "nifty_1min_rows": one_min_rows,
            "null_ohlc_rows": null_ohlc, "nonpositive_ohlc_rows": nonpositive_ohlc,
            "malformed_ohlc_rows": malformed_ohlc,
            "null_oi_rows": null_oi, "null_volume_rows": null_volume,
            "zero_volume_rows": zero_volume, "negative_volume_rows": negative_volume,
            "invalid_timestamp_rows": invalid_timestamps,
            "min_timestamp_utc": str(min_ts), "max_timestamp_utc": str(max_ts),
            "min_expiry": str(min_expiry), "max_expiry": str(max_expiry),
            "schema": sorted(schema),
        })
    result = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": REPO_ID, "purpose": "data audit only; no strategy P&L",
        "source_license_label": "other; review dataset/source terms before redistribution",
        "partitions": reports,
        "gate": "PASS_CANDIDATE_SCHEMA" if all(x["nifty_1min_rows"] > 0 and
            x["null_ohlc_rows"] == 0 and x["nonpositive_ohlc_rows"] == 0 and
            x["malformed_ohlc_rows"] == 0 for x in reports) else "FAIL_OR_INCOMPLETE",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, default=str) + "\n")
    print(json.dumps(result, indent=2, default=str))
    if result["gate"] != "PASS_CANDIDATE_SCHEMA":
        raise SystemExit("Option data quality gate failed; do not run strategy backtest.")

if __name__ == "__main__":
    main()
