from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUS = ROOT / "research" / "constituent_weekly" / "STATUS.md"
RESULT = ROOT / "research" / "constituent_weekly" / "C1_DHAN_PREFLIGHT.json"
START = "<!-- C1_DHAN_STATUS_START -->"
END = "<!-- C1_DHAN_STATUS_END -->"


def main() -> int:
    if RESULT.exists():
        data = json.loads(RESULT.read_text(encoding="utf-8"))
    else:
        data = {"status": "NO_PREFLIGHT_RESULT"}
    probes = data.get("intraday_probe", [])
    passed = sum(1 for p in probes if p.get("status") == "PASS")
    expected = data.get("intraday_probe_expected", 0)
    close_probes = data.get("targeted_expiry_close_probe", [])
    close_passed = sum(1 for p in close_probes if p.get("status") == "PASS")
    close_expected = data.get("targeted_expiry_close_expected", len(close_probes))
    lines = [
        START,
        "## Latest Dhan equity preflight",
        "",
        f"- Recorded at (UTC): {datetime.now(timezone.utc).isoformat()}",
        f"- Status: {data.get('status')}",
        f"- Data plan active: {data.get('data_plan_active')}",
        f"- Current universe security IDs resolved: {data.get('current_universe_resolved_count', 'NOT_RUN')}/{data.get('current_universe_symbol_count', 'NOT_RUN')}",
        f"- Historical membership symbols found in current scrip master: {data.get('historical_membership_symbols_found_in_current_master_count', 'NOT_RUN')}/{data.get('historical_membership_symbol_count', 'NOT_RUN')}",
        f"- Five-symbol price probe IDs resolved: {len(data.get('resolved_probe_symbols', []))}",
        f"- Missing symbols from current scrip master: {len(data.get('missing_probe_symbols', []))}",
        f"- One-minute probe windows passing: {passed}/{expected}",
        f"- Targeted 2026 expiry-close windows passing: {close_passed}/{close_expected}",
        f"- Deep daily-history probe: {data.get('daily_history_probe', {}).get('status', 'NOT_RUN')}",
        "- Raw bars, prices, security IDs, credentials and tokens are not stored in this report.",
        "- This probe does not establish inactive/delisted instrument history, point-in-time membership or index weights.",
        END,
    ]
    block = "\n".join(lines)
    current = STATUS.read_text(encoding="utf-8")
    if START in current and END in current:
        before = current.split(START, 1)[0].rstrip()
        after = current.split(END, 1)[1].lstrip()
        updated = before + "\n\n" + block + "\n\n" + after
    else:
        updated = current.rstrip() + "\n\n" + block + "\n"
    STATUS.write_text(updated, encoding="utf-8")
    print(f"Updated BUP-01 status with Dhan preflight result: {data.get('status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
