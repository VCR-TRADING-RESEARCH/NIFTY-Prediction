from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "research" / "constituent_weekly" / "C1_CONTINUOUS_COVERAGE.json"
REPORT = ROOT / "research" / "constituent_weekly" / "C1_CONTINUOUS_COVERAGE_REPORT.md"
STATUS = ROOT / "research" / "constituent_weekly" / "STATUS.md"
RESEARCH_LOG = ROOT / "logs" / "RESEARCH_LOG.md"
ERROR_LOG = ROOT / "logs" / "ERROR_LOG.md"
START = "<!-- C1_CONTINUOUS_COVERAGE_START -->"
END = "<!-- C1_CONTINUOUS_COVERAGE_END -->"


def main() -> int:
    if not RESULT.exists():
        raise SystemExit("Continuous coverage JSON is missing; cannot publish a status.")
    data = json.loads(RESULT.read_text(encoding="utf-8"))
    summary = data.get("summary", {})
    status = data.get("status", "UNKNOWN")
    gate = data.get("target_coverage_status", "NOT_EVALUATED")
    identity = data.get("identity_status", "NOT_EVALUATED")
    cycles = data.get("cycle_results", [])
    updated = data.get("updated_at_utc") or datetime.now(timezone.utc).isoformat()
    reused_index = data.get("cache_reused_index_chunks", 0)
    reused_stocks = data.get("cache_reused_stock_chunks", 0)

    lines = [
        START,
        "## Latest continuous Dhan stock + NIFTY target coverage audit",
        "",
        f"- Updated (UTC): {updated}",
        f"- Auditor status: **{status}**",
        f"- Stock/index data-coverage gate: **{gate}**",
        f"- Security/action identity gate: **{identity}**",
        f"- Window: {data.get('cycle_window', {}).get('first_anchor', 'NOT_SET')} to {data.get('cycle_window', {}).get('last_expiry', 'NOT_SET')}",
        f"- Scheduled expiry cycles: {summary.get('scheduled_cycles', data.get('scheduled_cycles', 'NOT_EVALUATED'))}",
        f"- Valid observed NIFTY anchor/expiry targets: {summary.get('index_target_valid_cycles', 0)} / {summary.get('scheduled_cycles', 0)} ({summary.get('index_target_valid_fraction', 0):.2%})",
        f"- Cycles meeting the 47-stock / 94% member coverage gate: {summary.get('cycles_meeting_47_and_94_percent_stock_gate', 0)}",
        f"- Cycles accepted for data coverage (including the observed NIFTY target): {summary.get('cycles_accepted_for_coverage', 0)}",
        f"- Confirmatory cycles after 104 prior accepted cycles: {summary.get('confirmatory_cycles_after_104_prior_cycles', 0)}",
        f"- Minimum cycle member coverage: {summary.get('minimum_member_coverage_fraction', 0):.2%}",
        f"- Median valid member count: {summary.get('median_valid_member_count', 0)}",
        f"- Dhan requests in this run: {data.get('requests_this_run', 0)}",
        f"- Reused cached 90-day chunks: index={reused_index}, stock-symbol={reused_stocks}",
        f"- Unresolved security symbols: {len(data.get('unresolved_security_symbols', []))}",
        "- Raw market bars, prices, volumes, Dhan security IDs and credentials are not included in this report.",
        "- A passing market-data coverage sub-gate does not complete corporate-action review or unlock C2 by itself.",
        END,
    ]
    block = "\n".join(lines)
    current = STATUS.read_text(encoding="utf-8") if STATUS.exists() else "# BUP-01 status\n"
    if START in current and END in current:
        before = current.split(START, 1)[0].rstrip()
        after = current.split(END, 1)[1].lstrip()
        updated_status = before + "\n\n" + block + "\n\n" + after
    else:
        updated_status = current.rstrip() + "\n\n" + block + "\n"
    STATUS.write_text(updated_status, encoding="utf-8")

    report_lines = [
        "# C1 Continuous Dhan Stock and NIFTY Target Coverage Report",
        "",
        f"**Updated:** {updated}",
        f"**Status:** {status}",
        f"**Target coverage gate:** {gate}",
        f"**Security/action gate:** {identity}",
        "",
        "## Registered scope",
        "",
        "- Point-in-time NIFTY 50 tradable constituents at each weekly forecast anchor.",
        "- One-minute stock candles for the 10:00–10:03 anchor and latest 15:00–15:14 expiry proxy.",
        "- One-minute NIFTY 50 index candles for the same target timestamps; index volume is not required.",
        "- Inclusive Dhan request windows are limited to 90 calendar days.",
        "- The target outcome remains the observed NIFTY 50 index direction; no weight or ETF comparison is involved.",
        "",
        "## Coverage summary",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| Scheduled cycles | {summary.get('scheduled_cycles', 0)} |",
        f"| Valid NIFTY target cycles | {summary.get('index_target_valid_cycles', 0)} |",
        f"| NIFTY target valid fraction | {summary.get('index_target_valid_fraction', 0):.2%} |",
        f"| Cycles meeting 47 / 94% stock rule | {summary.get('cycles_meeting_47_and_94_percent_stock_gate', 0)} |",
        f"| Cycles meeting stock + index data gates | {summary.get('cycles_accepted_for_coverage', 0)} |",
        f"| Confirmatory cycles after 104 prior cycles | {summary.get('confirmatory_cycles_after_104_prior_cycles', 0)} |",
        f"| Minimum constituent coverage fraction | {summary.get('minimum_member_coverage_fraction', 0):.2%} |",
        f"| Median valid constituents | {summary.get('median_valid_member_count', 0)} |",
        "",
        "## Known corporate-action crossing exclusions",
        "",
    ]
    action_cycles = [item for item in cycles if item.get("known_corporate_action_excluded_symbols")]
    if action_cycles:
        report_lines += [
            "| Anchor | Expiry | Excluded security aliases |",
            "|---|---|---|",
        ]
        for item in action_cycles:
            report_lines.append(
                f"| {item.get('anchor_date')} | {item.get('expiry_date')} | "
                f"{', '.join(item.get('known_corporate_action_excluded_symbols', []))} |"
            )
    else:
        report_lines.append("No known HDFC merger or Tata Motors demerger crossing week was detected.")
    report_lines += [
        "",
        "## Identity and remaining C1 limitations",
        "",
        f"- Unresolved symbols: {', '.join(data.get('unresolved_security_symbols', [])) or 'None in current scrip-master resolution.'}",
        "- The current scrip master provides a present-day identifier mapping, not complete historical proof for every inactive security.",
        "- HDFC Ltd and Tata Motors known target-crossing action weeks are separately excluded. All issuer actions, adjustments and symbol/security-ID intervals still require a full dated audit.",
        "- Coverage flags establish that source bars were returned and passed target-window OHLC checks; they do not establish adjusted-return correctness or model skill.",
        "- No raw market bars, raw price/volume values, credentials, access tokens or security IDs are published.",
        "- This report does not pass the entire C1 gate, unlock C2 or certify a trading strategy.",
        "",
        "## Reproducibility",
        "",
        f"- Membership SHA-256: {data.get('input_manifest', {}).get('membership_sha256', 'NOT_RECORDED')}",
        f"- Expiry calendar SHA-256: {data.get('input_manifest', {}).get('expiry_calendar_sha256', 'NOT_RECORDED')}",
        f"- Official NIFTY daily-session SHA-256: {data.get('input_manifest', {}).get('official_daily_session_sha256', 'NOT_RECORDED')}",
        f"- Dhan scrip-master SHA-256: {data.get('input_manifest', {}).get('dhan_scrip_master_sha256', 'NOT_RECORDED')}",
        f"- Dhan requests this run: {data.get('requests_this_run', 0)}",
        f"- Cached index chunks: {len(data.get('index_chunks', {}))}; cached stock-symbol chunks: {len(data.get('stock_chunks', {}))}",
        "",
        "The machine-readable companion C1_CONTINUOUS_COVERAGE.json contains only source-window status, timestamps, QA flags, and constituent symbols; it does not contain raw market prices or Dhan security IDs.",
    ]
    REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    log = RESEARCH_LOG.read_text(encoding="utf-8") if RESEARCH_LOG.exists() else "# Research log\n"
    log_key = f"## {updated[:10]} — C1 continuous stock/index target coverage"
    if log_key not in log:
        log += f"""

{log_key}

- **Auditor status:** {status}; data-coverage gate: {gate}; identity/action gate: {identity}.
- **Window:** {data.get('cycle_window', {}).get('first_anchor', 'NOT_SET')} to {data.get('cycle_window', {}).get('last_expiry', 'NOT_SET')}.
- **Coverage:** {summary.get('index_target_valid_cycles', 0)}/{summary.get('scheduled_cycles', 0)} valid NIFTY targets; {summary.get('cycles_accepted_for_coverage', 0)} cycles meet the stock and index data rules; {summary.get('confirmatory_cycles_after_104_prior_cycles', 0)} confirmatory cycles after the 104-cycle warm-up.
- **API/cache:** {data.get('requests_this_run', 0)} requests this run; reused {reused_index} index and {reused_stocks} stock-symbol chunks.
- **Interpretation:** data coverage is assessed independently of security identity/corporate-action treatment. This audit does not train or evaluate a model and does not unlock C2.
- **Artifacts:** C1_CONTINUOUS_COVERAGE.json and C1_CONTINUOUS_COVERAGE_REPORT.md.
"""
        RESEARCH_LOG.write_text(log, encoding="utf-8")

    if status in ("BLOCKED_AUTH_OR_ENTITLEMENT", "PARTIAL_OR_BLOCKED_RUNTIME_ERROR"):
        errors = ERROR_LOG.read_text(encoding="utf-8") if ERROR_LOG.exists() else "# Error log\n"
        entry = f"""
## C1 continuous coverage audit — {updated}

- **Status:** {status}.
- **Sanitised failure category:** {data.get('fatal_error') or 'not recorded'}.
- **Requests completed before stop:** {data.get('requests_this_run', 0)}.
- **Impact:** continuous C1 stock/index coverage remains unproven; C2 is not unlocked.
"""
        if updated not in errors:
            ERROR_LOG.write_text(errors + entry, encoding="utf-8")

    print(f"Updated C1 continuous coverage status: {status}; target_gate={gate}; identity={identity}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
