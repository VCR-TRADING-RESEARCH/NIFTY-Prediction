#!/usr/bin/env python3
"""Persist Phase 10 run status into repository logs, README and manuscript."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

run = os.getenv("GITHUB_RUN_ID", "local")
stamp = datetime.now(timezone.utc).isoformat()
summary_path = Path("research/results/phase10/summary.json")
failure_path = Path("research/results/phase10/failure_report.json")
readme = Path("README.md")
manuscript = Path("research/manuscript.md")
research_log = Path("logs/RESEARCH_LOG.md")
error_log = Path("logs/ERROR_LOG.md")

status = "BLOCKED_WORKFLOW_FAILURE"
note = ""
if summary_path.exists():
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    status = data.get("model_result_status", "RESULT_REPORTED")
    note = (
        f"- Dataset status: {data.get('dataset_status')}.\n"
        f"- Model result: {data.get('model_result_status')}.\n"
        f"- Source-gated cycles: {data.get('weekly_cycles_built')}; binary rows: {data.get('binary_rows')}; "
        f"development/holdout: {data.get('development_rows')}/{data.get('holdout_rows')}.\n"
        f"- Baseline/challenger selected on development: {data.get('selected_baseline')} / {data.get('selected_augmented_candidate')}.\n"
        f"- Screening details: {json.dumps(data.get('screening', {}), sort_keys=True)}.\n"
        "- Trading strategy: NOT VALIDATED; no contract-level cost-adjusted futures/options P&L was run.\n"
    )
elif failure_path.exists():
    data = json.loads(failure_path.read_text(encoding="utf-8"))
    status = data.get("status", "BLOCKED_REBUILD_ERROR")
    note = (
        f"- Failure status: {status}.\n"
        f"- Sanitized error: {data.get('error_type')}: {data.get('error')}.\n"
        "- No model acceptance or current prediction is implied.\n"
    )
else:
    note = "- No fresh Phase 10 summary or failure report was produced; inspect the exact failed Actions step.\n"

entry = (
    f"\n\n## Phase 10 automated run {run} — {stamp}\n"
    f"- Workflow outcomes: tests={os.getenv('TEST_OUTCOME')}, Dhan history={os.getenv('FETCH_OUTCOME')}, "
    f"rebuild/evaluation={os.getenv('REBUILD_OUTCOME')}.\n"
    f"- Final status: {status}.\n"
    + note
    + "- Plan: docs/PHASE_10_VERIFIED_DATASET.md and docs/RESEARCH_PLAN_V1_2_DHAN_DATASET_ADDENDUM.md.\n"
    + "- Raw Dhan history remains cache-only; only compact metadata and derived results are committed.\n"
)
research_log.parent.mkdir(parents=True, exist_ok=True)
with research_log.open("a", encoding="utf-8") as f:
    f.write(entry)
if any(os.getenv(k) != "success" for k in ("TEST_OUTCOME", "FETCH_OUTCOME", "REBUILD_OUTCOME")):
    with error_log.open("a", encoding="utf-8") as f:
        f.write(entry + "- Review the failed test/data/rebuild step, preserve the error record, add a regression test and retry once.\n")

if not summary_path.exists():
    start = "<!-- PHASE10_STATUS_START -->"
    end = "<!-- PHASE10_STATUS_END -->"
    block = (
        f"{start}\n## Phase 10 — Dhan-backed dataset rebuild\n"
        f"- **Status:** {status}; no successful rebuilt model report is available for this run.\n"
        "- Check [workflow](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions) and the [Phase 10 plan](docs/PHASE_10_VERIFIED_DATASET.md).\n"
        "- No stale result is reused and no trading strategy is validated.\n"
        f"{end}"
    )
    txt = readme.read_text(encoding="utf-8")
    if start in txt and end in txt:
        before = txt.split(start)[0]
        after = txt.split(end, 1)[1]
        txt = before + block + after
    else:
        txt = txt.rstrip() + "\n\n" + block + "\n"
    readme.write_text(txt, encoding="utf-8")

    mstart = "<!-- PHASE10_RESULTS_START -->"
    mend = "<!-- PHASE10_RESULTS_END -->"
    mblock = (
        f"{mstart}\n## Phase 10 execution status\n\n"
        f"**Status:** {status}. The automated Dhan-backed rebuild did not produce a successful summary in run {run}. "
        "This is a blocked execution result, not model performance evidence. See logs/ERROR_LOG.md and "
        "docs/PHASE_10_VERIFIED_DATASET.md.\n"
        f"{mend}"
    )
    mt = manuscript.read_text(encoding="utf-8")
    if mstart in mt and mend in mt:
        before = mt.split(mstart)[0]
        after = mt.split(mend, 1)[1]
        mt = before + mblock + after
    else:
        mt = mt.rstrip() + "\n\n" + mblock + "\n"
    manuscript.write_text(mt, encoding="utf-8")

print(json.dumps({
    "run_id": run,
    "status": status,
    "summary_exists": summary_path.exists(),
    "failure_report_exists": failure_path.exists(),
}, indent=2))
