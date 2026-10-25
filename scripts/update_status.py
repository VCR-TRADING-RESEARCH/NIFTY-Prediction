#!/usr/bin/env python3
"""Refresh a compact, factual status section in README from generated run artifacts."""
from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
SUMMARY = ROOT / "research" / "results" / "summary.json"
METRICS = ROOT / "research" / "results" / "holdout_metrics.csv"
QUALITY = ROOT / "data" / "processed" / "data_quality_report.json"
START = "<!-- AUTO_STATUS_START -->"
END = "<!-- AUTO_STATUS_END -->"


def load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def render() -> str:
    summary = load_json(SUMMARY)
    quality = load_json(QUALITY)
    today = pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M UTC")
    lines = [START, "## Latest automated research status", "", "Last status refresh: " + today, ""]
    if summary is None:
        lines += [
            "**Status: BLOCKED / NOT YET RUN.** No complete summary.json artifact exists for this branch yet.",
            "",
            "A successful workflow must validate the source data and expiry alignment before any strategy can be considered.",
        ]
    else:
        lines += [
            "- Run ID: " + str(summary.get("run_id", "unknown")),
            "- Target labels: " + str(summary.get("observations_total_labels", "n/a")),
            "- Binary rows with sufficient features: " + str(summary.get("feature_complete_binary_rows", "n/a")),
            "- Development / final holdout rows: " + str(summary.get("development_rows", "n/a")) + " / " + str(summary.get("heldout_rows", "n/a")),
            "- Model selected on development data: " + str(summary.get("development_selected_model", "n/a")),
            "- Calendar status: **" + str(summary.get("calendar_status", "UNKNOWN")) + "**",
            "- Independently validated usable trading strategy: **NO**",
            "",
            "The current pipeline labels the weekday-derived expiry calendar as exploratory; performance metrics are not a verified trading edge. The spot index is not a directly executable instrument, and contract-level quotes, dated costs, spread/slippage and fills are not yet joined.",
        ]
        if quality:
            source = quality.get("source_quality", {})
            yahoo = quality.get("independent_daily_close_crosscheck", {})
            lines += [
                "",
                "- Source CSV files: " + str(source.get("source_files_read", "n/a")),
                "- Valid minute bars after checks: " + str(source.get("valid_in_session_rows", "n/a")),
                "- Yahoo daily-close check: " + ("available" if yahoo.get("available") else "unavailable / failed") + "; compared rows: " + str(yahoo.get("matched_rows", "n/a")) + "; expiry-date mismatches over tolerance: " + str(yahoo.get("mismatch_rows", "n/a")),
            ]
        if METRICS.exists():
            try:
                frame = pd.read_csv(METRICS)
                if not frame.empty and "candidate" in frame:
                    lines += ["", "### Final holdout metrics (exploratory)"]
                    for _, row in frame.iterrows():
                        acc = "n/a" if pd.isna(row.get("accuracy")) else f"{float(row['accuracy']):.3f}"
                        bal = "n/a" if pd.isna(row.get("balanced_accuracy")) else f"{float(row['balanced_accuracy']):.3f}"
                        lines.append("- " + str(row["candidate"]) + ": accuracy " + acc + ", balanced accuracy " + bal + ", n=" + str(int(row.get("n", 0))))
            except Exception:
                lines += ["", "Holdout metrics file is present but could not be rendered; inspect research/results/holdout_metrics.csv."]
    lines += ["", "See the research log, error log, pre-registered plan, data-quality report, and manuscript for details.", END]
    return "\n".join(lines)


def main() -> int:
    if not README.exists():
        raise FileNotFoundError("README.md is missing")
    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise ValueError("README is missing automatic status markers")
    before = text.split(START, 1)[0]
    after = text.split(END, 1)[1]
    README.write_text(before + render() + after, encoding="utf-8")
    print("README_STATUS_UPDATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
