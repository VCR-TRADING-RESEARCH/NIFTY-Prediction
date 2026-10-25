#!/usr/bin/env python3
"""Run the bounded NIFTY weekly-expiry research cycle and persist audit artifacts."""
from __future__ import annotations

import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "nifty50"
PROCESSED = ROOT / "data" / "processed"
RESULTS = ROOT / "research" / "results"
LOGS = ROOT / "logs"
sys.path.insert(0, str(ROOT / "scripts"))

from research_core import (  # noqa: E402
    load_minute_files, daily_aggregates, apply_official_daily_closes, construct_weekly_table,
    evaluate_research, try_yahoo_daily_validation, save_figures,
)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def append_error(message: str, run_id: str) -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    path = LOGS / "ERROR_LOG.md"
    stamp = datetime.now(timezone.utc).isoformat()
    entry = (
        "\n\n## Automated run " + run_id + " — " + stamp + " — Phase pipeline error\n"
        "- Severity: High for the current run; research acceptance gate is blocked until fixed.\n"
        "- Symptom: Automated run did not complete the full data-to-results pipeline.\n"
        "- Details: " + message.replace("\n", " ")[:1200] + "\n"
        "- Required action: inspect the GitHub Actions log, correct the root cause, add a regression test, and rerun.\n"
        "- Sensitive values: request/response bodies and secrets are not recorded here.\n"
    )
    with path.open("a", encoding="utf-8") as handle:
        handle.write(entry)


def append_success(summary: dict, quality: dict) -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    path = LOGS / "RESEARCH_LOG.md"
    run_id = os.getenv("GITHUB_RUN_ID", "local")
    stamp = datetime.now(timezone.utc).isoformat()
    entry = (
        "\n\n## Automated run " + str(run_id) + " — " + stamp + "\n"
        "- Status: pipeline completed; empirical findings remain exploratory until calendar and instrument-cost gates pass.\n"
        "- Source files read: " + str(quality.get("source_files_read")) + "; valid minute bars: " + str(quality.get("valid_in_session_rows")) + ".\n"
        "- Weekly labels: " + str(summary.get("observations_total_labels")) + "; binary rows: " + str(summary.get("binary_rows")) + "; feature-complete rows: " + str(summary.get("feature_complete_binary_rows")) + ".\n"
        "- Development rows / held-out rows: " + str(summary.get("development_rows")) + " / " + str(summary.get("heldout_rows")) + ".\n"
        "- Development-selected model: " + str(summary.get("development_selected_model")) + ".\n"
        "- Calendar gate: " + str(summary.get("calendar_status")) + " — " + str(summary.get("reason_not_confirmatory")) + "\n"
        "- Usable trading strategy: NOT VALIDATED. " + str(summary.get("trading_strategy_blocker")) + "\n"
        "- Artifacts: data/processed/weekly_labels_features.csv, research/results/holdout_metrics.csv, research/results/summary.json and the associated plots.\n"
    )
    with path.open("a", encoding="utf-8") as handle:
        handle.write(entry)


def compare_recent_dhan(minutes: pd.DataFrame) -> dict:
    """Compare recent Dhan bars to the public archive without storing private raw Dhan bars in Git."""
    path = ROOT / "data" / "raw" / "dhan" / "NIFTY50_DHAN_recent.csv"
    report = {
        "attempted": path.exists(),
        "available": False,
        "matched_timestamps": 0,
        "mismatched_closes_over_1_point": None,
        "median_absolute_close_difference": None,
        "p95_absolute_close_difference": None,
        "raw_dhan_bars_committed": False,
    }
    if not path.exists():
        report["note"] = "Dhan recent cross-check bars were not available for this run."
        return report
    try:
        dhan, dhan_quality = load_minute_files([path])
        overlap = minutes[["timestamp", "close"]].merge(
            dhan[["timestamp", "close"]], on="timestamp", how="inner", suffixes=("_public", "_dhan")
        )
        if overlap.empty:
            report["note"] = "No exact overlapping minute timestamps between the public archive and Dhan."
            report["public_bars"] = int(len(minutes))
            report["dhan_bars"] = int(len(dhan))
            return report
        diff = (overlap["close_public"] - overlap["close_dhan"]).abs()
        report.update({
            "available": True,
            "matched_timestamps": int(len(overlap)),
            "mismatched_closes_over_1_point": int((diff > 1.0).sum()),
            "median_absolute_close_difference": float(diff.median()),
            "p95_absolute_close_difference": float(diff.quantile(0.95)),
            "dhan_source_rows": int(dhan_quality["valid_in_session_rows"]),
            "comparison_tolerance_index_points": 1.0,
            "note": "Summary-only comparison; Dhan raw bars are cached in the runner and are not committed.",
        })
        return report
    except Exception as exc:
        report["error"] = type(exc).__name__ + ": " + str(exc)[:200]
        return report


def main() -> int:
    run_id = os.getenv("GITHUB_RUN_ID", "local")
    PROCESSED.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    try:
        if not RAW.exists():
            raise FileNotFoundError("Raw data directory does not exist: " + str(RAW))
        files = list(RAW.glob("*.csv"))
        if not files:
            raise FileNotFoundError("No raw CSV files exist under " + str(RAW))
        minutes, quality = load_minute_files(files)
        daily = daily_aggregates(minutes)
        official_close_path = ROOT / "data" / "reconciliation" / "nifty50_official_daily.csv"
        expiry_verification_path = ROOT / "data" / "reconciliation" / "expiry_verification.csv"
        daily, official_close_quality = apply_official_daily_closes(daily, official_close_path)
        quality["official_daily_close_validation"] = official_close_quality
        if not expiry_verification_path.is_file():
            raise FileNotFoundError("Official NSE expiry verification table is required.")
        quality["daily_sessions"] = int(len(daily))
        quality["sessions_with_less_than_250_bars"] = int((daily["bars"] < 250).sum())
        quality["sessions_with_unchanged_close_run_over_10"] = int((daily["max_unchanged_close_run"] > 10).sum())
        quality["maximum_unchanged_close_run"] = int(daily["max_unchanged_close_run"].max()) if len(daily) else None
        daily.to_csv(PROCESSED / "daily_aggregates.csv", index=False)

        cycles, calendar, construction_report = construct_weekly_table(minutes, daily, expiry_verification_path)
        # Keep a minimal expiry schedule plus explicit flags for audit.
        calendar.to_csv(PROCESSED / "candidate_expiry_calendar.csv", index=False)
        cycles.to_csv(PROCESSED / "weekly_labels_features.csv", index=False)
        excluded = construction_report.pop("_excluded_detail", [])
        pd.DataFrame(excluded).to_csv(PROCESSED / "excluded_cycle_candidates.csv", index=False)

        yahoo_check = try_yahoo_daily_validation(daily, calendar, RESULTS)
        dhan_check = compare_recent_dhan(minutes)
        quality_report = {
            "run_id": run_id,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "source_quality": quality,
            "target_construction": construction_report,
            "independent_daily_close_crosscheck": yahoo_check,
            "independent_recent_minute_crosscheck": dhan_check,
            "confirmatory_status": "BLOCKED: candidate expiry dates are not yet reconciled against a complete official historical weekly-contract expiry calendar.",
            "data_scope_warning": "The public minute archive is a candidate source with known missing/frozen/partial sessions. Spot bar checks and Yahoo comparisons are diagnostics, not proof of official exchange data lineage.",
        }
        write_json(PROCESSED / "data_quality_report.json", quality_report)
        summary = evaluate_research(cycles, RESULTS)
        summary["run_id"] = run_id
        summary["source_quality"] = {
            "source_files_read": quality["source_files_read"],
            "valid_in_session_rows": quality["valid_in_session_rows"],
            "daily_sessions": len(daily),
            "data_quality_warnings": int(quality["conflicting_duplicate_timestamp_groups"]),
            "independent_close_check_available": bool(yahoo_check.get("available")),
            "independent_close_check_mismatches": yahoo_check.get("mismatch_rows"),
            "dhan_minute_check_available": bool(dhan_check.get("available")),
            "dhan_minute_match_count": dhan_check.get("matched_timestamps"),
            "dhan_minute_mismatches": dhan_check.get("mismatched_closes_over_1_point"),
        }
        summary["target_definition"] = "NSE official daily close on verified weekly expiry date relative to the first minute-archive bar open at or after 10:00 and no later than 10:03 on the first trading session after the previous verified expiry."
        summary["calendar_status"] = "EXPLORATORY_ONLY"
        write_json(RESULTS / "summary.json", summary)
        created_plots = save_figures(cycles, RESULTS)
        summary["plots_created"] = created_plots
        write_json(RESULTS / "summary.json", summary)
        write_json(RESULTS / "data_quality_summary.json", quality_report)

        # A machine-readable registry lets a later independent reviewer see exactly what was attempted.
        registry = {
            "run_id": run_id,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "models": [
                {"name": "expanding_majority", "type": "baseline", "pre_registered": True},
                {"name": "prior_cycle_direction", "type": "rule", "pre_registered": True},
                {"name": "5_session_momentum_sign", "type": "rule", "pre_registered": True},
                {"name": "prior_cycle_return_sign", "type": "rule", "pre_registered": True},
                {"name": "logistic", "type": "regularized_logistic_regression", "pre_registered": True},
                {"name": "extra_trees", "type": "shallow_ensemble", "pre_registered": True},
            ],
            "model_selection": "Development walk-forward balanced accuracy; tie-break by Brier score. Held-out block not used for selection.",
            "candidate_search_budget": "Fixed v1.0 candidate list; no unrestricted evolutionary search during the core confirmatory pipeline.",
            "not_run": [
                "PySR symbolic-regression expansion",
                "Quantevolve evolutionary search",
                "TradingAgents multi-agent feature research",
                "Futures/options instrument-level P&L simulation",
                "Options open-interest/IV/skew and FII/DII/global-feature model",
            ],
            "why_not_run": "Core target/calendar data-quality validation is a prerequisite; additional model searches would magnify data-mining risk before the label and instrument execution data are verified.",
        }
        write_json(RESULTS / "experiment_registry.json", registry)
        append_success(summary, quality)
        print("RESEARCH_RUN_OK:", run_id)
        print("Rows:", summary.get("feature_complete_binary_rows"), "held-out:", summary.get("heldout_rows"))
        print("Selected:", summary.get("development_selected_model"))
        print("Status: EXPLORATORY_ONLY; no usable trading strategy is certified.")
        return 0
    except Exception as exc:
        # Keep logs useful but do not record any environment secret.
        message = type(exc).__name__ + ": " + str(exc)[:900]
        append_error(message, str(run_id))
        traceback.print_exc(limit=8)
        print("RESEARCH_RUN_ERROR:", message, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
