#!/usr/bin/env python3
"""Audit a separate published NIFTY 50 minute dataset against NSE daily OHLC.

Dataset: sandeepkapri/Nifty50-Minute-Data, 2015-01-09 through 2024-03-27.
The repository README does not identify the underlying data provider in enough detail to
prove independent vendor lineage. This is a second-published-dataset diagnostic, not official
ground truth. Raw data stays in the Actions cache and is not committed to the research repo.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "reconciliation"
CACHE = ROOT / "data" / "cache" / "alternative-minute"
URL = "https://raw.githubusercontent.com/sandeepkapri/Nifty50-Minute-Data/main/nifty50_candlestick_data.csv"
START = date(2019, 2, 1)
END = date(2024, 3, 27)
UA = "Mozilla/5.0 (compatible; NIFTYPredictionResearch/1.0)"


def fetch_source(force: bool = False) -> tuple[Path, dict[str, Any]]:
    path = CACHE / "sandeep_nifty50_candlestick_data.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 1_000_000 and not force:
        payload = path.read_bytes()
        downloaded = False
    else:
        last_error = "unknown error"
        session = requests.Session()
        session.headers.update({"User-Agent": UA, "Accept": "text/csv,*/*"})
        for attempt in range(3):
            try:
                response = session.get(URL, timeout=(10, 120))
                response.raise_for_status()
                payload = response.content
                if len(payload) < 1_000_000:
                    raise ValueError("CSV smaller than expected; source may have returned an error page")
                temp = path.with_suffix(path.suffix + ".tmp")
                temp.write_bytes(payload)
                temp.replace(path)
                downloaded = True
                break
            except Exception as exc:
                last_error = f"{type(exc).__name__}: {str(exc)[:240]}"
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))
        else:
            raise RuntimeError(f"Could not download secondary dataset: {last_error}")
    manifest = {
        "source_url": URL,
        "source_repository": "https://github.com/sandeepkapri/Nifty50-Minute-Data",
        "source_is_official": False,
        "published_repository_differs_from_primary_source_repository": True,
        "underlying_provider_lineage_independently_verified": False,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "downloaded_this_run": downloaded,
        "cache_path": str(path.relative_to(ROOT)),
    }
    return path, manifest


def _find_column(frame: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    columns = {str(column).strip().casefold(): column for column in frame.columns}
    for candidate in candidates:
        if candidate.casefold() in columns:
            return columns[candidate.casefold()]
    return None


def aggregate_sandeep_frame(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Aggregate ordinary 09:15-15:29 IST minute rows into daily OHLC."""
    date_col = _find_column(frame, ("Date",))
    time_col = _find_column(frame, ("Time",))
    if date_col is None or time_col is None:
        raise ValueError("Expected separate Date and Time columns; found " + ",".join(map(str, frame.columns)))

    date_text = frame[date_col].astype(str).str.strip()
    time_text = frame[time_col].astype(str).str.strip()
    parsed_date = pd.to_datetime(date_text, format="%d-%m-%y", errors="coerce")
    remaining = parsed_date.isna()
    if remaining.any():
        parsed_date.loc[remaining] = pd.to_datetime(date_text.loc[remaining], errors="coerce", dayfirst=True)
    timestamp = pd.to_datetime(
        parsed_date.dt.strftime("%Y-%m-%d") + " " + time_text,
        errors="coerce",
    )

    source_cols = {name: _find_column(frame, (name, name.title())) for name in ("open", "high", "low", "close")}
    if any(value is None for value in source_cols.values()):
        raise ValueError("Expected Open/High/Low/Close columns; found " + ",".join(map(str, frame.columns)))

    bars = pd.DataFrame({
        "timestamp": timestamp,
        "open": pd.to_numeric(frame[source_cols["open"]], errors="coerce"),
        "high": pd.to_numeric(frame[source_cols["high"]], errors="coerce"),
        "low": pd.to_numeric(frame[source_cols["low"]], errors="coerce"),
        "close": pd.to_numeric(frame[source_cols["close"]], errors="coerce"),
    })
    raw_count = len(bars)
    bars = bars.dropna(subset=["timestamp", "open", "high", "low", "close"])
    bars = bars[(bars["timestamp"].dt.date >= START) & (bars["timestamp"].dt.date <= END)]
    clock = bars["timestamp"].dt.time
    bars = bars[(clock >= pd.Timestamp("09:15:00").time()) & (clock <= pd.Timestamp("15:29:59").time())]
    bars = bars.sort_values("timestamp").drop_duplicates("timestamp", keep="last")
    bad_ohlc = (
        (bars["low"] > bars["high"]) |
        (bars["open"] < bars["low"]) |
        (bars["open"] > bars["high"]) |
        (bars["close"] < bars["low"]) |
        (bars["close"] > bars["high"]) |
        (bars[["open", "high", "low", "close"]] <= 0).any(axis=1)
    )
    bad_ohlc_count = int(bad_ohlc.sum())
    bars = bars.loc[~bad_ohlc].copy()
    bars["session_date"] = bars["timestamp"].dt.date
    if bars.empty:
        raise ValueError("No valid minute bars remain in the comparison window")

    daily = bars.groupby("session_date", sort=True).agg(
        alternative_open=("open", "first"),
        alternative_high=("high", "max"),
        alternative_low=("low", "min"),
        alternative_close=("close", "last"),
        alternative_bars=("close", "size"),
        first_bar=("timestamp", "min"),
        last_bar=("timestamp", "max"),
    ).reset_index()
    quality = {
        "source_rows": int(raw_count),
        "valid_rows_in_comparison_window": int(len(bars)),
        "daily_sessions": int(len(daily)),
        "rows_dropped_or_filtered": int(raw_count - len(bars)),
        "invalid_ohlc_rows_after_time_filter": bad_ohlc_count,
        "first_session": daily["session_date"].min().isoformat(),
        "last_session": daily["session_date"].max().isoformat(),
    }
    return daily, quality


def compare(alternative: pd.DataFrame, official: pd.DataFrame, primary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    official = official.copy()
    official["session_date"] = pd.to_datetime(official["session_date"], errors="coerce").dt.date
    official_cols = ["session_date"] + [
        column for column in ("official_open", "official_high", "official_low", "official_close")
        if column in official.columns
    ]
    official = official[official_cols].drop_duplicates("session_date")
    primary = primary.copy()
    primary["session_date"] = pd.to_datetime(primary["session_date"], errors="coerce").dt.date
    primary_cols = ["session_date"] + [
        column for column in ("session_open", "session_high", "session_low", "session_close")
        if column in primary.columns
    ]
    primary = primary[primary_cols].drop_duplicates("session_date")

    merged = alternative.merge(official, on="session_date", how="inner", validate="one_to_one")
    merged = merged.merge(primary, on="session_date", how="left", validate="one_to_one")
    merged["year"] = pd.to_datetime(merged["session_date"]).dt.year
    yearly = []
    for year, group in merged.groupby("year", sort=True):
        row = {"year": int(year), "sessions_compared": int(len(group))}
        for field in ("open", "high", "low", "close"):
            official_col = "official_close" if field == "close" else f"official_{field}"
            alternative_col = f"alternative_{field}"
            primary_col = f"session_{field}"
            if official_col not in group:
                continue
            diff = (group[alternative_col] - group[official_col]).abs()
            merged.loc[group.index, f"secondary_{field}_abs_difference"] = diff
            merged.loc[group.index, f"secondary_{field}_over_1pt"] = diff > 1.0
            row[f"secondary_{field}_mismatches_over_1pt"] = int((diff > 1.0).sum())
            row[f"secondary_{field}_median_abs_difference"] = float(diff.median())
            row[f"secondary_{field}_p95_abs_difference"] = float(diff.quantile(0.95))
            if primary_col in group:
                primary_diff = (group[primary_col] - group[official_col]).abs()
                merged.loc[group.index, f"primary_{field}_abs_difference"] = primary_diff
                row[f"primary_{field}_mismatches_over_1pt"] = int((primary_diff > 1.0).sum())
                row[f"primary_{field}_median_abs_difference"] = float(primary_diff.median())
                row[f"primary_{field}_p95_abs_difference"] = float(primary_diff.quantile(0.95))

    merged["secondary_vs_primary_close_abs_difference"] = (
        merged["alternative_close"] - merged["session_close"]
    ).abs()
    close_diff = merged["secondary_close_abs_difference"].dropna()
    primary_diff = merged["primary_close_abs_difference"].dropna() if "primary_close_abs_difference" in merged else pd.Series(dtype=float)
    report = {
        "generated_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "source": "sandeepkapri/Nifty50-Minute-Data",
        "source_url": URL,
        "source_repository_differs_from_primary_source_repository": True,
        "underlying_provider_lineage_independently_verified": False,
        "source_is_official": False,
        "data_status": "DIAGNOSTIC_ONLY",
        "coverage_start": str(merged["session_date"].min()) if len(merged) else None,
        "coverage_end": str(merged["session_date"].max()) if len(merged) else None,
        "official_rows_in_overlap": int(len(merged)),
        "sessions_compared": int(len(merged)),
        "alternative_close_mismatches_over_1_point": int((close_diff > 1.0).sum()),
        "alternative_close_median_abs_difference_points": float(close_diff.median()) if len(close_diff) else None,
        "alternative_close_p95_abs_difference_points": float(close_diff.quantile(0.95)) if len(close_diff) else None,
        "alternative_close_max_abs_difference_points": float(close_diff.max()) if len(close_diff) else None,
        "primary_close_mismatches_over_1_point": int((primary_diff > 1.0).sum()),
        "primary_close_median_abs_difference_points": float(primary_diff.median()) if len(primary_diff) else None,
        "primary_close_p95_abs_difference_points": float(primary_diff.quantile(0.95)) if len(primary_diff) else None,
        "secondary_vs_primary_close_median_abs_difference_points": float(merged["secondary_vs_primary_close_abs_difference"].median()) if len(merged) else None,
        "secondary_vs_primary_close_exact_matches": int((merged["secondary_vs_primary_close_abs_difference"].dropna() == 0.0).sum()),
        "secondary_vs_primary_close_comparison_rows": int(merged["secondary_vs_primary_close_abs_difference"].notna().sum()),
        "source_limitations": [
            "Different published GitHub repository, but the actual market-data provider is not established by the README.",
            "Not an official exchange feed and cannot by itself validate the source gate.",
            "Comparison covers only through 2024-03-27, so it cannot validate 2024-04 through 2026.",
            "The primary archive may use a different minute timestamp convention; 15:29 bar close may differ from official EOD close."
        ],
    }
    return merged, pd.DataFrame(yearly).sort_values("year"), report


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report_path = OUT / "sandeep_minute_source_report.json"
    try:
        force = os.getenv("FORCE_REFRESH", "false").casefold() == "true"
        source_path, manifest = fetch_source(force)
        source_frame = pd.read_csv(source_path, low_memory=False)
        alternative, quality = aggregate_sandeep_frame(source_frame)
        official_path = OUT / "nifty50_official_daily.csv"
        primary_path = OUT / "minute_vs_official_daily.csv"
        if not official_path.exists() or not primary_path.exists():
            raise FileNotFoundError("Run official-source reconciliation first")
        rows, yearly, report = compare(alternative, pd.read_csv(official_path), pd.read_csv(primary_path))
        report["download_manifest"] = manifest
        report["alternative_source_quality"] = quality
        rows.to_csv(OUT / "sandeep_minute_vs_official_daily.csv", index=False)
        yearly.to_csv(OUT / "sandeep_minute_comparison_by_year.csv", index=False)
        report_path.write_text(json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")
        print("SANDEEP_MINUTE_SOURCE_AUDIT:", json.dumps({
            key: report[key] for key in (
                "data_status", "coverage_start", "coverage_end", "sessions_compared",
                "alternative_close_mismatches_over_1_point",
                "alternative_close_median_abs_difference_points",
                "primary_close_mismatches_over_1_point",
                "primary_close_median_abs_difference_points",
                "secondary_vs_primary_close_exact_matches",
                "secondary_vs_primary_close_comparison_rows"
            )
        }, indent=2))
    except Exception as exc:
        failure = {
            "generated_utc": pd.Timestamp.now(tz="UTC").isoformat(),
            "source": "sandeepkapri/Nifty50-Minute-Data",
            "data_status": "SOURCE_FAILED",
            "error": f"{type(exc).__name__}: {str(exc)[:700]}",
            "note": "Source failure does not imply that any other source passes validation."
        }
        report_path.write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")
        print("SANDEEP_MINUTE_SOURCE_AUDIT_FAILED:", json.dumps(failure, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
