#!/usr/bin/env python3
"""Recompute Phase 3 close comparisons from preserved raw-minute aggregates.

This step deliberately does not use yahoo_daily_crosscheck.csv: that file may be
computed from official-close-overridden daily values in the downstream pipeline.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "reconciliation"
REPORT = OUT / "source_reconciliation_report.json"
OFFICIAL = OUT / "nifty50_official_daily.csv"
ARCHIVE = ROOT / "data" / "processed" / "daily_aggregates.csv"


def compare_archive_to_official(archive: pd.DataFrame, official: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    required_archive = {"session_date", "session_open", "session_high", "session_low", "session_close_archive"}
    required_official = {"session_date", "official_open", "official_high", "official_low", "official_close"}
    if not required_archive.issubset(archive.columns):
        raise ValueError("Archive daily aggregate is missing preserved source fields: " + str(sorted(required_archive - set(archive.columns))))
    if not required_official.issubset(official.columns):
        raise ValueError("Official daily file is missing fields: " + str(sorted(required_official - set(official.columns))))
    a = archive[list(required_archive)].copy()
    o = official[list(required_official)].copy()
    a["session_date"] = pd.to_datetime(a["session_date"], errors="coerce").dt.date
    o["session_date"] = pd.to_datetime(o["session_date"], errors="coerce").dt.date
    if a["session_date"].duplicated().any() or o["session_date"].duplicated().any():
        raise ValueError("Duplicate daily session dates found in source data")
    a = a.rename(columns={"session_close_archive": "archive_close"})
    merged = a.merge(o, on="session_date", how="inner", validate="one_to_one")
    if merged.empty:
        raise ValueError("No overlapping archive sessions and official daily rows")
    fields = {
        "open": ("session_open", "official_open"),
        "high": ("session_high", "official_high"),
        "low": ("session_low", "official_low"),
        "close": ("archive_close", "official_close"),
    }
    metrics = {"daily_source_rows_compared": int(len(merged))}
    for name, (source_col, official_col) in fields.items():
        diff = (pd.to_numeric(merged[source_col], errors="coerce") - pd.to_numeric(merged[official_col], errors="coerce")).abs()
        merged[name + "_abs_difference"] = diff
        merged[name + "_over_1pt"] = diff > 1.0
        metrics["minute_vs_official_" + name + "_rows_compared"] = int(diff.notna().sum())
        metrics["minute_vs_official_" + name + "_mismatches_over_1_point"] = int((diff > 1.0).sum())
        metrics["minute_vs_official_" + name + "_abs_difference_median_points"] = float(diff.median())
        metrics["minute_vs_official_" + name + "_abs_difference_p95_points"] = float(diff.quantile(0.95))
        metrics["minute_vs_official_" + name + "_abs_difference_max_points"] = float(diff.max())
    close_diff = merged["close_abs_difference"]
    metrics["daily_source_rows_expected"] = int(len(a[(a["session_date"] >= min(o["session_date"])) & (a["session_date"] <= max(o["session_date"]))]))
    metrics["daily_source_rows_missing_official_close"] = int(max(0, metrics["daily_source_rows_expected"] - len(merged)))
    metrics["minute_vs_official_mismatches_over_1_point"] = int((close_diff > 1.0).sum())
    metrics["minute_vs_official_abs_difference_median_points"] = float(close_diff.median())
    metrics["minute_vs_official_abs_difference_p95_points"] = float(close_diff.quantile(0.95))
    metrics["minute_vs_official_abs_difference_max_points"] = float(close_diff.max())
    metrics["minute_vs_official_within_1_point"] = int((close_diff <= 1.0).sum())
    return merged, metrics


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {
        "generated_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "counts": {},
        "errors": [],
        "status": "BLOCKED",
    }
    try:
        if not ARCHIVE.exists() or not OFFICIAL.exists():
            raise FileNotFoundError("Need both preserved daily archive aggregates and official NSE daily data")
        archive = pd.read_csv(ARCHIVE)
        official = pd.read_csv(OFFICIAL)
        merged, metrics = compare_archive_to_official(archive, official)
        merged.to_csv(OUT / "minute_vs_official_daily.csv", index=False)
        merged["year"] = pd.to_datetime(merged["session_date"]).dt.year
        yearly = merged.groupby("year", sort=True).agg(
            rows_compared=("session_date", "size"),
            close_mismatches_over_1_point=("close_over_1pt", "sum"),
            close_median_abs_difference_points=("close_abs_difference", "median"),
            close_p95_abs_difference_points=("close_abs_difference", lambda s: s.quantile(0.95)),
            open_mismatches_over_1_point=("open_over_1pt", "sum"),
            high_mismatches_over_1_point=("high_over_1pt", "sum"),
            low_mismatches_over_1_point=("low_over_1pt", "sum"),
        ).reset_index()
        yearly.to_csv(OUT / "daily_close_mismatch_summary_by_year.csv", index=False)
        report.setdefault("counts", {}).update(metrics)
        counts = report["counts"]
        errors = []
        checked = int(counts.get("candidate_expiries_checked", 0))
        verified = int(counts.get("contract_verified_expiries", 0))
        unverified = int(counts.get("contract_unverified_expiries", 0))
        source_errors = int(counts.get("expiry_source_errors", 0))
        if checked == 0 or verified != checked or unverified or source_errors:
            errors.append("Official expiry-calendar verification is incomplete.")
        if metrics["daily_source_rows_missing_official_close"] > 0:
            errors.append("Some minute-archive sessions lack an official daily close.")
        if metrics["minute_vs_official_mismatches_over_1_point"] > 0:
            errors.append("Minute-archive daily closes differ from official NSE closes by more than one index point.")
        report["status"] = "PASS" if not errors else "BLOCKED"
        report["errors"] = errors
        report["candidate_close_source"] = "preserved session_close_archive from data/processed/daily_aggregates.csv"
        report["independence_note"] = "The close comparison uses preserved original minute-archive closes, not the official-close-overridden session_close or Yahoo comparison file."
        report["generated_utc"] = pd.Timestamp.now(tz="UTC").isoformat()
        REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("ARCHIVE_CLOSE_AUDIT:", json.dumps({"status": report["status"], "counts": metrics, "errors": errors}, indent=2))
    except Exception as exc:
        report["status"] = "BLOCKED"
        report["errors"] = ["Archive-vs-official close audit failed: " + type(exc).__name__ + ": " + str(exc)[:500]]
        report["candidate_close_source"] = "unavailable"
        REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("ARCHIVE_CLOSE_AUDIT_FAILED:", json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
