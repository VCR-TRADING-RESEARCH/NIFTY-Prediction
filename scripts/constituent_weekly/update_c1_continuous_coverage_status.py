from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "research" / "constituent_weekly" / "C1_CONTINUOUS_COVERAGE.json"
STATUS = ROOT / "research" / "constituent_weekly" / "STATUS.md"
START = "<!-- C1_CONTINUOUS_COVERAGE_STATUS_START -->"
END = "<!-- C1_CONTINUOUS_COVERAGE_STATUS_END -->"


def render(report: dict) -> str:
    summary = report.get("summary", {})
    index_ratio = summary.get("index_target_valid_fraction")
    index_display = f"{100 * index_ratio:.2f}%" if isinstance(index_ratio, (int, float)) else "not evaluated"
    return "\n".join([
        START,
        "## Continuous Dhan stock + NIFTY target coverage audit",
        "",
        f"- Updated (UTC): {datetime.now(timezone.utc).isoformat()}",
        f"- Run status: **{report.get('status', 'UNKNOWN')}**",
        f"- Target coverage sub-gate: **{report.get('target_coverage_status', 'NOT_EVALUATED')}**",
        f"- Separate security/action identity gate: **{report.get('identity_status', 'NOT_EVALUATED')}**",
        f"- Intraday coverage window: {report.get('cycle_window', {}).get('first_anchor', 'unknown')} to {report.get('cycle_window', {}).get('last_expiry', 'unknown')}",
        f"- Scheduled weekly cycles: {summary.get('scheduled_cycles', report.get('scheduled_cycles', 0))}",
        f"- Valid observed NIFTY anchor + expiry-proxy targets: {summary.get('index_target_valid_cycles', 0)} / {summary.get('scheduled_cycles', 0)} ({index_display})",
        f"- Cycles meeting the 47-stock / 94% coverage threshold: {summary.get('cycles_meeting_47_and_94_percent_stock_gate', 0)}",
        f"- Cycles accepted for the panel: {summary.get('cycles_accepted_for_panel', 0)}",
        f"- Confirmatory cycles after 104 earlier accepted cycles: {summary.get('confirmatory_cycles_after_104_prior_cycles', 0)}",
        f"- Unique unresolved member symbols: {len(report.get('unresolved_security_symbols', []))}",
        f"- Dhan data requests in this run: {report.get('requests_this_run', 0)}",
        f"- Reused cached completed index chunks: {report.get('cache_reused_index_chunks', 0)}",
        f"- Reused cached completed stock-symbol chunks: {report.get('cache_reused_stock_chunks', 0)}",
        f"- Fatal diagnostic category: {report.get('fatal_error') or 'none'}",
        "",
        "Only sanitized coverage flags, selected bar times, date gaps, and hashes are retained. Raw OHLCV values, tokens, and security IDs are not written to this public repository.",
        "",
        "Detailed machine-readable report: [C1_CONTINUOUS_COVERAGE.json](C1_CONTINUOUS_COVERAGE.json).",
        END,
    ])


def main() -> int:
    if not REPORT.is_file():
        raise SystemExit("Continuous coverage report is missing.")
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    text = STATUS.read_text(encoding="utf-8")
    section = render(report)
    if START in text and END in text:
        pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
        text = pattern.sub(section, text, count=1)
    else:
        text = text.rstrip() + "\n\n" + section + "\n"
    text = re.sub(
        r"^\*\*Last updated:\*\*.*$",
        "**Last updated:** " + datetime.now(timezone.utc).strftime("%Y-%m-%d") + "  ",
        text,
        count=1,
        flags=re.M,
    )
    STATUS.write_text(text, encoding="utf-8")
    print(f"C1_CONTINUOUS_STATUS_UPDATED {report.get('target_coverage_status', 'NOT_EVALUATED')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
