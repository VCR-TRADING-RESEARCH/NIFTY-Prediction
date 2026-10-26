#!/usr/bin/env python3
"""Compare the 10:00–10:03 NIFTY anchor across published minute archives.

The second repository is not official and its original data provider is unverified.
Outputs are diagnostic only. The script also measures whether the observed anchor-price
differences alter weekly direction labels when official expiry closes are held constant.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache" / "alternative-minute"
OUT = ROOT / "data" / "reconciliation"
SECONDARY_URL = "https://raw.githubusercontent.com/sandeepkapri/Nifty50-Minute-Data/main/nifty50_candlestick_data.csv"
START = date(2019, 2, 1)
END = date(2024, 3, 27)
IST = "Asia/Kolkata"


def normalize_timestamps(values: pd.Series) -> pd.Series:
    """Return tz-aware IST timestamps; naive timestamps in these sources mean local IST."""
    parsed = pd.to_datetime(values, errors="coerce")
    if parsed.dt.tz is None:
        return parsed.dt.tz_localize(IST)
    return parsed.dt.tz_convert(IST)


def secondary_minutes(force: bool = False) -> tuple[pd.DataFrame, dict[str, Any]]:
    path = CACHE / "sandeep_nifty50_candlestick_data.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    downloaded = False
    if not path.exists() or force:
        response = requests.get(
            SECONDARY_URL,
            headers={"User-Agent": "NIFTYPredictionResearch/1.0"},
            timeout=(10, 180),
        )
        response.raise_for_status()
        payload = response.content
        if len(payload) < 1_000_000:
            raise ValueError("Secondary CSV unexpectedly small")
        temp = path.with_suffix(".tmp")
        temp.write_bytes(payload)
        temp.replace(path)
        downloaded = True
    payload = path.read_bytes()
    frame = pd.read_csv(path, low_memory=False)
    columns = {str(c).strip().casefold(): c for c in frame.columns}

    def col(*names: str) -> str:
        for name in names:
            if name.casefold() in columns:
                return columns[name.casefold()]
        raise ValueError("Missing expected source column: " + "/".join(names))

    dates = frame[col("Date")].astype(str).str.strip()
    times = frame[col("Time")].astype(str).str.strip()
    parsed_dates = pd.to_datetime(dates, format="%d-%m-%y", errors="coerce")
    missing = parsed_dates.isna()
    if missing.any():
        # ISO dates must be parsed as ISO; day-first applies only to non-ISO legacy strings.
        iso_mask = dates.str.match(r"^\d{4}-\d{2}-\d{2}(?:$|T| )", na=False)
        iso_dates = pd.to_datetime(dates.where(iso_mask), errors="coerce")
        parsed_dates.loc[missing & iso_mask] = iso_dates.loc[missing & iso_mask]
        remaining = parsed_dates.isna()
        if remaining.any():
            parsed_dates.loc[remaining] = pd.to_datetime(dates.loc[remaining], errors="coerce", dayfirst=True)
    timestamp = pd.to_datetime(parsed_dates.dt.strftime("%Y-%m-%d") + " " + times, errors="coerce")
    # Source convention is local Indian exchange time.
    timestamp = timestamp.dt.tz_localize(IST)

    bars = pd.DataFrame({
        "timestamp": timestamp,
        "open": pd.to_numeric(frame[col("Open")], errors="coerce"),
        "high": pd.to_numeric(frame[col("High")], errors="coerce"),
        "low": pd.to_numeric(frame[col("Low")], errors="coerce"),
        "close": pd.to_numeric(frame[col("Close")], errors="coerce"),
    })
    bars = bars.dropna().sort_values("timestamp").drop_duplicates("timestamp", keep="last")
    local_dates = bars.timestamp.dt.date
    bars = bars[(local_dates >= START) & (local_dates <= END)]
    clock = bars.timestamp.dt.time
    bars = bars[(clock >= pd.Timestamp("09:15").time()) & (clock <= pd.Timestamp("15:29:59").time())]
    valid = (
        (bars[["open", "high", "low", "close"]] > 0).all(axis=1)
        & (bars.low <= bars[["open", "close"]].min(axis=1))
        & (bars.high >= bars[["open", "close"]].max(axis=1))
        & (bars.low <= bars.high)
    )
    bars = bars.loc[valid].copy()
    return bars, {
        "source_url": SECONDARY_URL,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "bars": int(len(bars)),
        "downloaded_this_run": downloaded,
        "lineage_independently_verified": False,
        "official_source": False,
    }


def anchors(frame: pd.DataFrame, prefix: str) -> pd.DataFrame:
    frame = frame.copy()
    frame["timestamp"] = normalize_timestamps(frame["timestamp"])
    frame["session_date"] = frame.timestamp.dt.date
    clock = frame.timestamp.dt.time
    frame = frame[
        (clock >= pd.Timestamp("10:00").time())
        & (clock <= pd.Timestamp("10:03").time())
    ].sort_values("timestamp")
    frame = frame.drop_duplicates("session_date", keep="first")
    return frame[["session_date", "timestamp", "open"]].rename(
        columns={"timestamp": prefix + "_timestamp", "open": prefix + "_anchor_open"}
    )


def compare_weekly_labels(
    weekly: pd.DataFrame,
    anchor_comparison: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Recalculate historical weekly direction using the secondary anchor and unchanged close."""
    if weekly.empty:
        return pd.DataFrame(), {"status": "NOT_AVAILABLE", "reason": "Weekly label table is empty."}
    required = {"anchor_date", "anchor_price", "expiry_close", "label"}
    if not required.issubset(weekly.columns):
        return pd.DataFrame(), {
            "status": "NOT_AVAILABLE",
            "reason": "Weekly label table lacks: " + ", ".join(sorted(required - set(weekly.columns))),
        }
    w = weekly.copy()
    w["anchor_date"] = pd.to_datetime(w["anchor_date"], errors="coerce").dt.date
    if "expiry_date" in w.columns:
        w["expiry_date"] = pd.to_datetime(w["expiry_date"], errors="coerce").dt.date
    compare_cols = ["session_date", "secondary_anchor_open", "absolute_anchor_open_difference", "mismatch_over_1_point"]
    joined = w.merge(anchor_comparison[compare_cols], left_on="anchor_date", right_on="session_date",
                     how="inner", validate="one_to_one")
    joined["primary_anchor_recomputed_return"] = pd.to_numeric(joined["expiry_close"], errors="coerce") / pd.to_numeric(joined["anchor_price"], errors="coerce") - 1.0
    joined["secondary_anchor_return"] = pd.to_numeric(joined["expiry_close"], errors="coerce") / pd.to_numeric(joined["secondary_anchor_open"], errors="coerce") - 1.0
    joined["primary_label_recomputed"] = joined["primary_anchor_recomputed_return"].map(lambda x: "UP" if x > 0 else ("DOWN" if x < 0 else "FLAT"))
    joined["secondary_anchor_label"] = joined["secondary_anchor_return"].map(lambda x: "UP" if x > 0 else ("DOWN" if x < 0 else "FLAT"))
    joined["label_changed"] = joined["primary_label_recomputed"] != joined["secondary_anchor_label"]
    joined["label_agreement"] = joined["label"] == joined["secondary_anchor_label"]
    n = len(joined)
    switched = int(joined["label_changed"].sum())
    diff = joined["absolute_anchor_open_difference"]
    stats = {
        "status": "DIAGNOSTIC_ONLY",
        "weekly_cycles_with_secondary_anchor": int(n),
        "primary_vs_secondary_direction_switches": switched,
        "label_switch_rate": float(switched / n) if n else None,
        "labels_agreeing_with_original_published_label": int(joined["label_agreement"].sum()),
        "label_agreement_rate": float(joined["label_agreement"].mean()) if n else None,
        "anchor_difference_median_points": float(diff.median()) if n else None,
        "anchor_difference_p95_points": float(diff.quantile(0.95)) if n else None,
        "anchor_difference_max_points": float(diff.max()) if n else None,
        "caveat": "Same official expiry closes are used for both returns. This only measures label sensitivity to the secondary anchor; secondary provider lineage is unverified and labels remain exploratory.",
    }
    return joined, stats


def main() -> int:
    force = os.getenv("FORCE_REFRESH_SECONDARY", "false").lower() == "true"
    try:
        try:
            from scripts.research_core import load_minute_files
        except ImportError:
            sys.path.insert(0, str(ROOT / "scripts"))
            from research_core import load_minute_files

        primary_files = sorted((ROOT / "data/raw/nifty50").glob("*.csv"))
        if not primary_files:
            raise FileNotFoundError("Primary archive absent; run scripts/fetch_data.py first")
        primary, _ = load_minute_files(primary_files)
        primary = primary[(primary.timestamp.dt.date >= START) & (primary.timestamp.dt.date <= END)]
        secondary, manifest = secondary_minutes(force)
        primary_anchors = anchors(primary, "primary")
        secondary_anchors = anchors(secondary, "secondary")
        joined = primary_anchors.merge(
            secondary_anchors, on="session_date", how="inner", validate="one_to_one"
        )
        joined["timestamp_match"] = joined.primary_timestamp.eq(joined.secondary_timestamp)
        joined["absolute_anchor_open_difference"] = (
            joined.primary_anchor_open - joined.secondary_anchor_open
        ).abs()
        joined["mismatch_over_1_point"] = joined.absolute_anchor_open_difference > 1.0

        OUT.mkdir(parents=True, exist_ok=True)
        joined.to_csv(OUT / "anchor_source_comparison.csv", index=False)
        weekly_path = ROOT / "data/processed/weekly_labels_features.csv"
        if weekly_path.is_file():
            weekly = pd.read_csv(weekly_path)
            weekly_comparison, label_stats = compare_weekly_labels(weekly, joined)
            if not weekly_comparison.empty:
                weekly_comparison.to_csv(OUT / "weekly_anchor_label_sensitivity.csv", index=False)
        else:
            label_stats = {"status": "NOT_AVAILABLE", "reason": "data/processed/weekly_labels_features.csv not present on this branch."}

        diff = joined.absolute_anchor_open_difference
        report = {
            "generated_utc": pd.Timestamp.now(tz="UTC").isoformat(),
            "status": "DIAGNOSTIC_ONLY",
            "primary_source": "technovusin/nifty50-historical-data; the pipeline's current input archive",
            "secondary_source": manifest,
            "window": {"start": str(START), "end": str(END)},
            "counts": {
                "primary_anchors": int(len(primary_anchors)),
                "secondary_anchors": int(len(secondary_anchors)),
                "overlap_sessions": int(len(joined)),
                "exact_timestamp_matches": int(joined.timestamp_match.sum()),
                "anchor_open_mismatches_over_1_point": int(joined.mismatch_over_1_point.sum()),
            },
            "absolute_difference_points": {
                "median": float(diff.median()) if len(diff) else None,
                "p95": float(diff.quantile(0.95)) if len(diff) else None,
                "max": float(diff.max()) if len(diff) else None,
            },
            "weekly_label_sensitivity": label_stats,
            "acceptance": "Does not pass the independent-anchor gate: the secondary data's provider lineage is unverified and neither published archive is official ground truth. Use this report to locate source discrepancies only.",
            "outputs": [
                "data/reconciliation/anchor_source_comparison.csv",
                "data/reconciliation/weekly_anchor_label_sensitivity.csv",
            ],
        }
        (OUT / "anchor_source_comparison_report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(json.dumps(report, indent=2))
        return 0
    except Exception as exc:
        safe_message = " ".join(str(exc).split())[:500]
        print(json.dumps({"status": "ERROR", "error_type": type(exc).__name__, "message": safe_message}))
        raise


if __name__ == "__main__":
    raise SystemExit(main())
