#!/usr/bin/env python3
"""Audit readiness for new weekly-expiry methods without fitting models on blocked labels.

A blocked source gate is a valid research outcome. This script deliberately reports
prerequisites and does not train, tune or select a candidate estimator.
"""
from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUALITY_PATH = ROOT / "data" / "processed" / "data_quality_report.json"
SUMMARY_PATH = ROOT / "research" / "results" / "summary.json"
FEATURES_PATH = ROOT / "data" / "processed" / "weekly_labels_features.csv"
METRICS_PATH = ROOT / "research" / "results" / "holdout_metrics.csv"
REGISTRY_PATH = ROOT / "research" / "results" / "experiment_registry.json"
OUTPUT_PATH = ROOT / "research" / "results" / "method_discovery_readiness.json"
RESEARCH_LOG = ROOT / "logs" / "RESEARCH_LOG.md"
ERROR_LOG = ROOT / "logs" / "ERROR_LOG.md"
README_PATH = ROOT / "README.md"

START_MARKER = "<!-- METHOD_DISCOVERY_STATUS_START -->"
END_MARKER = "<!-- METHOD_DISCOVERY_STATUS_END -->"


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError("Required audit input missing: " + str(path.relative_to(ROOT)))
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("Expected JSON object in " + str(path.relative_to(ROOT)))
    return value


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.is_file():
        raise FileNotFoundError("Required CSV input missing: " + str(path.relative_to(ROOT)))
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV header missing: " + str(path.relative_to(ROOT)))
        rows = list(reader)
        return list(reader.fieldnames), rows


def assess_source_gate(quality: dict[str, Any], summary: dict[str, Any]) -> tuple[str, list[str]]:
    """Fail closed unless independent anchor and source reconciliation explicitly pass."""
    blockers: list[str] = []
    status = str(quality.get("confirmatory_status") or summary.get("confirmatory_status") or "").upper()
    if status.startswith("BLOCKED"):
        blockers.append("Repository data-quality report marks confirmatory target construction BLOCKED.")

    source_quality = quality.get("source_quality") or {}
    daily_audit = source_quality.get("official_daily_close_validation") or {}
    mismatches = daily_audit.get("archive_close_mismatches_over_1_point")
    if mismatches is None:
        blockers.append("No audited minute-archive-versus-official-close mismatch count is available.")
    else:
        try:
            mismatch_count = int(mismatches)
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid archive_close_mismatches_over_1_point value") from exc
        if mismatch_count > 0:
            blockers.append(
                f"{mismatch_count} preserved minute-archive daily closes differ from official closes by more than one point."
            )

    target = quality.get("target_construction") or {}
    eligible = target.get("confirmatory_eligible_rows")
    if eligible is None:
        blockers.append("Confirmatory-eligible row count is missing.")
    else:
        try:
            eligible_count = int(eligible)
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid confirmatory_eligible_rows value") from exc
        if eligible_count <= 0:
            blockers.append("No rows are marked confirmatory-eligible; the independent 10:00 anchor/source gate remains unresolved.")

    intraday = quality.get("independent_recent_minute_crosscheck") or {}
    if intraday.get("available") is not True:
        blockers.append("Independent intraday-source cross-check is unavailable in the current quality report.")

    if blockers:
        return "BLOCKED_EMPIRICAL_METHOD_SEARCH", blockers
    return "READY_FOR_PREREGISTERED_METHOD_COMPARISON", blockers


def build_method_matrix(feature_columns: set[str], source_artifacts: set[str] | None = None) -> list[dict[str, Any]]:
    artifacts = source_artifacts or set()

    has_vol = {"rv_5", "rv_20"}.issubset(feature_columns)
    has_trend = {"ret_5", "ret_20"}.issubset(feature_columns)
    options_present = (
        "options_snapshots" in artifacts
        or bool(feature_columns.intersection({"atm_iv", "atm_iv_10am", "put_call_oi_ratio", "risk_reversal_25d"}))
    )
    cross_market_present = (
        "cross_market_history" in artifacts
        or bool(feature_columns.intersection({"gift_nifty_return", "sp500_overnight_return", "usd_inr_return"}))
    )
    flows_present = (
        "flow_history" in artifacts
        or bool(feature_columns.intersection({"fii_net_cash", "dii_net_cash", "participant_futures_oi_change"}))
    )

    return [
        {
            "priority": "P0",
            "family": "Independent anchor and source integrity",
            "hypothesis": "Correct labels and verified timestamps are prerequisites for directional inference.",
            "current_input_status": "blocked",
            "evidence": "The source-quality report records official-close discrepancies and no accepted independent 10:00 anchor.",
            "next_action": "Reconcile row-level 10:00 anchor prices against a genuinely independent source and explain the daily-close mismatch.",
        },
        {
            "priority": "P1",
            "family": "Multiscale trend, gap, range and volatility interactions",
            "hypothesis": "Trend strength and reversal features conditional on volatility may add information beyond the current weekly-cycle features.",
            "current_input_status": "features_present_source_gate_blocked" if has_vol and has_trend else "feature_engineering_needed",
            "evidence": "The current table has ret_1/5/10/20, rv_5/10/20, range_5/10/20, overnight_gap, pre_anchor_return and anchor_jump.",
            "next_action": "After source acceptance, add causal ratios and interactions, then compare nested walk-forward ablations.",
        },
        {
            "priority": "P1",
            "family": "India VIX and conditional volatility state",
            "hypothesis": "Directional effects may vary across volatility regimes; volatility alone is not assumed to predict direction.",
            "current_input_status": "source_series_not_joined",
            "evidence": "No verified point-in-time India VIX series is joined to the current weekly feature table.",
            "next_action": "Acquire official VIX history, align availability times, and compute fold-local state/rank features.",
        },
        {
            "priority": "P1",
            "family": "Point-in-time options surface and positioning",
            "hypothesis": "ATM IV, skew, term structure, straddle-implied move and OI changes may add information beyond spot OHLC.",
            "current_input_status": "candidate_columns_detected_source_gate_blocked" if options_present else "unavailable_in_current_feature_table",
            "evidence": "No historical 10:00 option-chain snapshot table is currently linked to the labelled rows. End-of-day OI cannot be backdated to the 10:00 forecast.",
            "next_action": "Inspect selective Zenodo/Hugging Face partitions and Dhan history; validate contracts, timestamps, rights and missingness.",
        },
        {
            "priority": "P1",
            "family": "Global overnight and cross-market inputs",
            "hypothesis": "Overnight global price discovery may help explain NIFTY movement from 10:00 to expiry close.",
            "current_input_status": "candidate_columns_detected_source_gate_blocked" if cross_market_present else "unavailable_in_current_feature_table",
            "evidence": "No timestamp-audited GIFT NIFTY, US/Asia, FX or commodity panel is joined to the labelled rows.",
            "next_action": "Build a lag-safe panel with market-specific timezones, holidays, closes and publication-time metadata.",
        },
        {
            "priority": "P2",
            "family": "FII/DII, participant OI and breadth",
            "hypothesis": "Lagged flow, positioning or breadth measures may explain conditional weekly direction.",
            "current_input_status": "candidate_columns_detected_source_gate_blocked" if flows_present else "unavailable_in_current_feature_table",
            "evidence": "A verified point-in-time flow/participant table is not joined to the current feature table.",
            "next_action": "Use the last report actually published by the forecast cutoff; do not use post-close information at 10:00.",
        },
        {
            "priority": "P2",
            "family": "Fold-local regime models and change-point features",
            "hypothesis": "Transparent volatility state labels or regime interactions may improve stability over one global estimator.",
            "current_input_status": "design_only_source_gate_blocked",
            "evidence": "The weekly sample is approximately 400 cycles and current source quality blocks model fitting or tuning.",
            "next_action": "Start with simple development-fold volatility thresholds and regularised interactions before complex hidden-state models.",
        },
        {
            "priority": "P2",
            "family": "Probability calibration and abstention",
            "hypothesis": "Uncertainty estimates may improve selective decision quality by abstaining on ambiguous cycles.",
            "current_input_status": "design_only_source_gate_blocked",
            "evidence": "Current holdout probabilities are exploratory; sequential coverage has not been accepted.",
            "next_action": "Calibrate inside development folds and measure sequential uncertainty coverage/abstention versus error.",
        },
        {
            "priority": "P3 bounded",
            "family": "PySR symbolic and Quantevolve-inspired bounded search",
            "hypothesis": "A compact formula may reveal an interpretable interaction missed by fixed features.",
            "current_input_status": "not_run_deferred_by_source_gate",
            "evidence": "The experiment registry explicitly lists PySR and Quantevolve searches as not run.",
            "next_action": "Only after source acceptance: cap at 100 candidate expressions/rules and up to 3 development-only generations, with complexity controls and a complete registry.",
        },
        {
            "priority": "Deferred",
            "family": "LLM news agents and deep sequence models",
            "hypothesis": "Potential value depends on richer, correctly timestamped inputs than the current weekly sample contains.",
            "current_input_status": "deferred_low_sample_and_data_requirements",
            "evidence": "About 398 weekly rows are not a sound basis for unrestricted neural sequence search.",
            "next_action": "Use LLMs only to propose auditable hypotheses; defer deep sequence models until a larger, independently validated sample exists.",
        },
    ]


def current_metrics_snapshot(rows: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    fields = ("accuracy", "balanced_accuracy", "mcc", "brier", "log_loss", "roc_auc", "n", "validation_scope")
    snapshot: dict[str, dict[str, Any]] = {}
    for row in rows:
        name = row.get("candidate")
        if name not in {"extra_trees", "logistic", "majority"}:
            continue
        values: dict[str, Any] = {}
        for field in fields:
            value = row.get(field)
            if value in (None, ""):
                continue
            try:
                values[field] = int(value) if field == "n" else float(value)
            except (TypeError, ValueError):
                values[field] = value
        snapshot[str(name)] = values
    return snapshot


def render_readme_block(report: dict[str, Any]) -> str:
    blocked = report["status"] == "BLOCKED_EMPIRICAL_METHOD_SEARCH"
    label = "BLOCKED — source/anchor quality gate" if blocked else "READY — preregistered comparison gate"
    reason = report["blockers"][0] if report.get("blockers") else "No registered source-quality blocker was detected."
    return "\n".join(
        [
            START_MARKER,
            "## Phase 9 — New weekly-expiry direction methods",
            f"- **Readiness status:** {label}.",
            "- **Research plan:** [Phase 9 method plan](docs/PHASE_9_NEW_DIRECTION_METHODS.md); [Version 1.1 addendum](docs/RESEARCH_PLAN_V1_1_METHODS_ADDENDUM.md).",
            "- **Automated report:** [method-discovery readiness JSON](research/results/method_discovery_readiness.json).",
            f"- **Current blocker:** {reason}",
            "- **Interpretation:** the readiness audit trains no new model; existing ExtraTrees metrics remain exploratory and no trading strategy is validated.",
            END_MARKER,
        ]
    )


def update_readme(report: dict[str, Any]) -> None:
    existing = README_PATH.read_text(encoding="utf-8")
    block = render_readme_block(report)
    if START_MARKER in existing and END_MARKER in existing:
        start = existing.index(START_MARKER)
        end = existing.index(END_MARKER, start) + len(END_MARKER)
        updated = existing[:start] + block + existing[end:]
    else:
        updated = existing.rstrip() + "\n\n" + block + "\n"
    README_PATH.write_text(updated, encoding="utf-8")


def append_research_log(report: dict[str, Any]) -> None:
    stamp = datetime.now(timezone.utc).isoformat()
    run_id = os.getenv("GITHUB_RUN_ID", "local")
    blockers = "\n".join("- " + item for item in report.get("blockers", [])) or "- None."
    entry = (
        f"\n\n## Phase 9 method-readiness audit — run {run_id} — {stamp}\n"
        f"- Phase status: {report['phase_status']}.\n"
        f"- Gate outcome: {report['status']}.\n"
        "- Completed: repository input audit, candidate-method priority matrix and readiness report.\n"
        "- Models trained in this audit: NO. New model selection is blocked while the source/anchor gate remains unresolved.\n"
        f"- Candidate feature rows available: {report['dataset']['feature_rows']}; feature columns: {report['dataset']['feature_column_count']}.\n"
        f"- Current ExtraTrees metrics retained for context only: {json.dumps(report.get('current_exploratory_metrics', {}).get('extra_trees', {}), sort_keys=True)}.\n"
        f"- Blockers:\n{blockers}\n"
        "- Next action: independently validate the 10:00 anchor and repair the official-close/source discrepancy; rebuild labels and freeze a new holdout before any new method comparison.\n"
        "- Output: research/results/method_discovery_readiness.json; README Phase 9 status block refreshed.\n"
    )
    RESEARCH_LOG.parent.mkdir(parents=True, exist_ok=True)
    with RESEARCH_LOG.open("a", encoding="utf-8") as handle:
        handle.write(entry)


def append_error(message: str) -> None:
    stamp = datetime.now(timezone.utc).isoformat()
    run_id = os.getenv("GITHUB_RUN_ID", "local")
    safe = " ".join(str(message).split())[:500]
    entry = (
        f"\n\n## Phase 9 readiness audit failure — run {run_id} — {stamp}\n"
        "- Severity: Medium; this audit did not produce a complete readiness report.\n"
        f"- Sanitised error: {safe}\n"
        "- Required action: fix the schema/test failure, preserve this record and rerun once.\n"
        "- No provider response bodies, secrets, tokens, PINs or TOTP values are logged.\n"
    )
    ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ERROR_LOG.open("a", encoding="utf-8") as handle:
        handle.write(entry)


def build_report() -> dict[str, Any]:
    quality = load_json(QUALITY_PATH)
    summary = load_json(SUMMARY_PATH)
    feature_columns, feature_rows = read_csv(FEATURES_PATH)
    _, metric_rows = read_csv(METRICS_PATH)
    registry = load_json(REGISTRY_PATH)

    status, blockers = assess_source_gate(quality, summary)
    source_artifacts: set[str] = set()
    if (ROOT / "data" / "processed" / "options_snapshots.csv").is_file():
        source_artifacts.add("options_snapshots")
    if (ROOT / "data" / "processed" / "cross_market_history.csv").is_file():
        source_artifacts.add("cross_market_history")
    if (ROOT / "data" / "processed" / "flow_history.csv").is_file():
        source_artifacts.add("flow_history")

    methods = build_method_matrix(set(feature_columns), source_artifacts)
    return {
        "schema_version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "run_id": os.getenv("GITHUB_RUN_ID", "local"),
        "branch": os.getenv("GITHUB_REF_NAME", "local"),
        "plan_version": "1.1",
        "phase": "phase-9-new-direction-methods",
        "phase_status": "METHOD_DESIGN_COMPLETE; EMPIRICAL_TESTING_BLOCKED" if status == "BLOCKED_EMPIRICAL_METHOD_SEARCH" else "READY_FOR_PREREGISTERED_METHOD_COMPARISON",
        "status": status,
        "blockers": blockers,
        "dataset": {
            "feature_rows": len(feature_rows),
            "feature_column_count": len(feature_columns),
            "feature_columns": feature_columns,
            "binary_rows_in_latest_summary": summary.get("binary_rows"),
            "development_rows_in_latest_summary": summary.get("development_rows"),
            "heldout_rows_in_latest_summary": summary.get("heldout_rows"),
            "confirmatory_eligible_rows": (quality.get("target_construction") or {}).get("confirmatory_eligible_rows"),
        },
        "current_exploratory_metrics": current_metrics_snapshot(metric_rows),
        "method_matrix": methods,
        "experiment_registry": {
            "path": str(REGISTRY_PATH.relative_to(ROOT)),
            "currently_not_run": registry.get("not_run", []),
            "interpretation": "Not-run means no empirical conclusion; it must not be reported as a failed or underperforming model.",
        },
        "guardrail": "This readiness audit did not train or select any candidate estimator.",
        "next_gate": "Independent 10:00 anchor validation and official-close/source discrepancy investigation must pass; then rebuild labels and freeze a new split manifest.",
    }


def main() -> int:
    try:
        report = build_report()
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        append_research_log(report)
        update_readme(report)
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "phase_status": report["phase_status"],
                    "feature_rows": report["dataset"]["feature_rows"],
                    "blocker_count": len(report["blockers"]),
                    "method_families": len(report["method_matrix"]),
                },
                indent=2,
            )
        )
        return 0
    except Exception as exc:
        append_error(type(exc).__name__ + ": " + str(exc))
        raise


if __name__ == "__main__":
    raise SystemExit(main())
