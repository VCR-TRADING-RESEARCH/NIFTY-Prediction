from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "research" / "constituent_weekly" / "C1_DAILY_COVERAGE.json"
REPORT = ROOT / "research" / "constituent_weekly" / "C1_DAILY_COVERAGE_REPORT.md"
STATUS = ROOT / "research" / "constituent_weekly" / "STATUS.md"
RESEARCH_LOG = ROOT / "logs" / "RESEARCH_LOG.md"
ERROR_LOG = ROOT / "logs" / "ERROR_LOG.md"
START = "<!-- C1_DAILY_COVERAGE_START -->"
END = "<!-- C1_DAILY_COVERAGE_END -->"


def main() -> int:
    if not RESULT.exists():
        raise SystemExit("Daily coverage JSON is missing; cannot publish status.")
    data = json.loads(RESULT.read_text(encoding="utf-8"))
    summary = data.get("summary", {})
    updated = data.get("updated_at_utc") or datetime.now(timezone.utc).isoformat()
    status = data.get("status", "UNKNOWN")
    symbol_results = data.get("symbol_results", {})

    block_lines = [
        START,
        "## Daily OHLCV member-session coverage audit",
        "",
        f"- Updated (UTC): {updated}",
        f"- Auditor status: **{status}**",
        f"- Window: {summary.get('window_start', data.get('input_manifest', {}).get('window_start', 'NOT_SET'))} to {summary.get('window_end', data.get('input_manifest', {}).get('window_end', 'NOT_SET'))}",
        f"- Point-in-time symbols: {summary.get('point_in_time_symbols_expected', 0)}",
        f"- Parseable daily API responses: {summary.get('symbols_with_parseable_daily_responses', 0)}",
        f"- Expected member sessions: {summary.get('expected_member_sessions', 0)}",
        f"- Valid OHLC member sessions: {summary.get('valid_member_sessions_ohlc', 0)} ({summary.get('weighted_ohlc_session_coverage_fraction', 0):.2%})",
        f"- Valid OHLCV member sessions: {summary.get('valid_member_sessions_ohlcv', 0)} ({summary.get('weighted_ohlcv_session_coverage_fraction', 0):.2%})",
        f"- Unresolved security IDs: {summary.get('symbols_with_unresolved_security_id', len(data.get('unresolved_symbols', [])))}",
        f"- Dhan requests in this run: {data.get('requests_this_run', 0)}",
        f"- Reused cached symbols: {data.get('cache_reused_symbols', 0)}",
        f"- TejHQ fallback disposition: {data.get('tejhq_fallback', {}).get('status', 'NOT_RECORDED')}",
        f"- TejHQ fallback symbols accepted: {sum(1 for item in data.get('tejhq_fallback', {}).get('symbols', {}).values() if item.get('status') == 'PASS')}",
        f"- TejHQ fallback member sessions added: {summary.get('tejhq_fallback_member_sessions_added', 0)}",
        "- Raw prices, OHLC arrays, volumes, security IDs and credentials are not published.",
        "- The plan does not set a separate daily-coverage percentage gate; this is descriptive evidence to support the C1 feature-data decision.",
        END,
    ]
    block = "\n".join(block_lines)
    current = STATUS.read_text(encoding="utf-8") if STATUS.exists() else "# BUP-01 status\n"
    if START in current and END in current:
        before, remaining = current.split(START, 1)
        _, after = remaining.split(END, 1)
        new_status = before.rstrip() + "\n\n" + block + "\n\n" + after.lstrip()
    else:
        new_status = current.rstrip() + "\n\n" + block + "\n"
    STATUS.write_text(new_status, encoding="utf-8")

    rows = []
    for symbol in sorted(symbol_results):
        item = symbol_results[symbol]
        rows.append(
            f"| {symbol} | {item.get('expected_session_count', 0)} | "
            f"{item.get('valid_ohlc_session_count', 0)} | "
            f"{item.get('ohlc_coverage_fraction', 0):.2%} | "
            f"{item.get('valid_volume_session_count', 0)} | "
            f"{item.get('volume_coverage_fraction', 0):.2%} | "
            f"{item.get('missing_session_count', 0)} | {item.get('status', 'UNKNOWN')} |"
        )
    report_lines = [
        "# C1 Daily OHLCV Member-Session Coverage Report",
        "",
        f"**Updated:** {updated}",
        f"**Auditor status:** {status}",
        "",
        "## Scope",
        "",
        "- Daily OHLCV for each point-in-time tradable NIFTY 50 security/member session from 2018-04-01 to the latest available official daily session.",
        "- Membership intervals are half-open: valid_from is inclusive and valid_to is exclusive.",
        "- The NIFTY session calendar is taken from the cached official daily reference; non-member days are not counted for that security.",
        "- The report checks OHLC invariants and daily volume validity separately.",
        "- Dhan daily history is requested through the historical daily endpoint; no minute/90-day window is requested here.",
        "- Restricted fallback uses personal-use TejHQ raw NSE EQ bhavcopy pinned to a fixed dataset commit. Raw Parquet is read in temporary storage; only AES-256-GCM encrypted cache files and sanitized coverage metadata may persist.",
        "- TejHQ terms (updated 2026-10-30) permit personal research and one's own trading decisions, but not client/business use or raw-data redistribution. The MIT licence covers code, not exchange data; NSE terms continue to apply.",
        "- Source terms: https://tejhq.dev/data-terms; dataset description: https://huggingface.co/datasets/tejhq/indian-markets.",
        "- Raw market bars and numeric price/volume values are discarded after QA and are not written to this artifact.",
        "",
        "## Aggregate results",
        "",
        f"- Symbols expected: {summary.get('point_in_time_symbols_expected', 0)}",
        f"- Symbols with parseable daily responses: {summary.get('symbols_with_parseable_daily_responses', 0)}",
        f"- Expected member sessions: {summary.get('expected_member_sessions', 0)}",
        f"- OHLC coverage: {summary.get('valid_member_sessions_ohlc', 0)} / {summary.get('expected_member_sessions', 0)} ({summary.get('weighted_ohlc_session_coverage_fraction', 0):.2%})",
        f"- OHLCV coverage: {summary.get('valid_member_sessions_ohlcv', 0)} / {summary.get('expected_member_sessions', 0)} ({summary.get('weighted_ohlcv_session_coverage_fraction', 0):.2%})",
        "",
        "## Per-symbol coverage",
        "",
        "| Canonical member symbol | Expected sessions | Valid OHLC | OHLC coverage | Valid OHLCV | OHLCV coverage | Missing OHLC sessions | API status |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
        *rows,
        "",
        "## Restricted fallback summary",
        "",
        f"- Dataset: {data.get('tejhq_fallback', {}).get('dataset_repo', 'NOT_USED')} at revision {data.get('tejhq_fallback', {}).get('dataset_revision', 'NOT_USED')}.",
        f"- Fallback status: {data.get('tejhq_fallback', {}).get('status', 'NOT_USED')}.",
        f"- Accepted symbols: {', '.join(s for s, item in data.get('tejhq_fallback', {}).get('symbols', {}).items() if item.get('status') == 'PASS') or 'None'}.",
        f"- Encrypted local cache hits: {data.get('tejhq_fallback', {}).get('encrypted_cache_hits', 0)}; encrypted cache downloads: {data.get('tejhq_fallback', {}).get('year_partitions_downloaded', 0)}.",
        "- Raw exchange-derived parquet is never persisted in this repository or uploaded as a workflow artifact.",
        "",
        "## Interpretation and limitations",
        "",
        "- Daily history is a mandatory feature source in the registered plan. This report provides actual coverage counts but does not add a new acceptance threshold after the plan was locked.",
        "- A valid daily API response is not by itself a full C1 pass; historical security IDs, point-in-time aliases, corporate actions and target coverage remain separate checks.",
        "- Daily raw prices are not adjusted here for dividends, splits, bonuses, rights, mergers or demergers. The corporate-action adjustment review remains open.",
        "- Volume coverage is measured independently; missing volume stays missing and must not be silently imputed.",
        "- No raw market bars, raw prices, raw volumes, security IDs or credentials are included in this report.",
        "",
        "## Reproducibility",
        "",
        f"- Membership SHA-256: {data.get('input_manifest', {}).get('membership_sha256', 'NOT_RECORDED')}",
        f"- Official daily-session SHA-256: {data.get('input_manifest', {}).get('official_daily_session_sha256', 'NOT_RECORDED')}",
        f"- Dhan scrip-master SHA-256: {data.get('input_manifest', {}).get('dhan_scrip_master_sha256', 'NOT_RECORDED')}",
        f"- Requests this run: {data.get('requests_this_run', 0)}; cached symbols reused: {data.get('cache_reused_symbols', 0)}",
    ]
    REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    log = RESEARCH_LOG.read_text(encoding="utf-8") if RESEARCH_LOG.exists() else "# Research log\n"
    log_key = f"## {updated[:10]} — C1 Dhan daily OHLCV coverage"
    if log_key not in log:
        log += f"""

{log_key}

- **Auditor status:** {status}.
- **Window:** {summary.get('window_start', 'NOT_SET')} to {summary.get('window_end', 'NOT_SET')}.
- **Coverage:** {summary.get('symbols_with_parseable_daily_responses', 0)}/{summary.get('point_in_time_symbols_expected', 0)} parseable symbols; {summary.get('valid_member_sessions_ohlc', 0)}/{summary.get('expected_member_sessions', 0)} valid OHLC member sessions; weighted OHLCV coverage {summary.get('weighted_ohlcv_session_coverage_fraction', 0):.2%}.
- **API/cache:** {data.get('requests_this_run', 0)} requests; {data.get('cache_reused_symbols', 0)} symbols reused from the sanitized QA cache.
- **Interpretation:** daily OHLCV coverage is reported independently from intraday target coverage, historical identity and action-adjusted return integrity. No model is trained and C2 remains gated.
- **Artifacts:** C1_DAILY_COVERAGE.json and C1_DAILY_COVERAGE_REPORT.md.
"""
        RESEARCH_LOG.write_text(log, encoding="utf-8")

    if status in ("BLOCKED_AUTH_OR_ENTITLEMENT", "PARTIAL_OR_BLOCKED_RUNTIME_ERROR"):
        errors = ERROR_LOG.read_text(encoding="utf-8") if ERROR_LOG.exists() else "# Error log\n"
        entry = f"""

## C1 daily OHLCV coverage audit — {updated}

- **Status:** {status}.
- **Sanitized failure category:** {data.get('fatal_error') or 'not recorded'}.
- **Requests completed:** {data.get('requests_this_run', 0)}.
- **Impact:** daily feature-source coverage remains unproven; C2 is not unlocked.
"""
        if updated not in errors:
            ERROR_LOG.write_text(errors + entry, encoding="utf-8")

    print(
        f"Updated daily coverage status: {status}; "
        f"OHLCV session coverage={summary.get('weighted_ohlcv_session_coverage_fraction', 0):.2%}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
