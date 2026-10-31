from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUS = ROOT / "research" / "constituent_weekly" / "STATUS.md"
RESULT = ROOT / "research" / "constituent_weekly" / "C1_DHAN_PREFLIGHT.json"
WEIGHT_AUDIT = ROOT / "research" / "constituent_weekly" / "C1_NIFTY50_WEIGHT_AUDIT.json"
START = "<!-- C1_DHAN_STATUS_START -->"
END = "<!-- C1_DHAN_STATUS_END -->"


def main() -> int:
    data = json.loads(RESULT.read_text(encoding="utf-8")) if RESULT.exists() else {"status": "NO_PREFLIGHT_RESULT"}
    weight = json.loads(WEIGHT_AUDIT.read_text(encoding="utf-8")) if WEIGHT_AUDIT.exists() else {"status": "NOT_RUN"}

    probes = data.get("intraday_probe", [])
    passed = sum(1 for probe in probes if probe.get("status") == "PASS")
    expected = data.get("intraday_probe_expected", len(probes))
    legacy = data.get("legacy_identity_probe", [])
    legacy_passed = sum(1 for probe in legacy if probe.get("status") == "PASS")
    proxy_times = sorted({probe.get("expiry_proxy_bar_time_ist") for probe in probes if probe.get("expiry_proxy_bar_time_ist")})

    lines = [
        START,
        "## Latest Dhan equity preflight",
        "",
        f"- Recorded at (UTC): {data.get('finished_at_utc', datetime.now(timezone.utc).isoformat())}",
        f"- Dhan auth method/status: {data.get('auth_method', 'NOT_RECORDED')} / {data.get('token_refresh_status', 'NOT_RECORDED')}",
        f"- Profile HTTP status: {data.get('profile_status', 'NOT_RECORDED')}",
        f"- Status: {data.get('status')}",
        f"- Data plan active: {data.get('data_plan_active')}",
        f"- Current NIFTY 50 universe resolved in current Dhan master: {data.get('current_universe_resolved_count', 'NOT_RUN')}/{data.get('current_universe_symbol_count', 'NOT_RUN')}",
        f"- Historical membership symbol aliases matched in current Dhan master: {data.get('historical_membership_symbols_found_in_current_master_count', 'NOT_RUN')}/{data.get('historical_membership_symbol_count', 'NOT_RUN')}",
        f"- Five-symbol one-minute anchor/expiry-proxy checks: {passed}/{expected}",
        f"- Full point-in-time NIFTY 50 probe: {data.get('full_universe_probe_passed', 'NOT_RUN')}/{data.get('full_universe_probe_expected', 'NOT_RUN')} passed; resolved {data.get('full_universe_probe_resolved', 'NOT_RUN')}; date {data.get('full_universe_probe_date', 'NOT_RUN')}",
        f"- Accepted expiry proxy: last returned one-minute candle at/before {data.get('expiry_proxy_cutoff_ist', '15:15:00')} IST; sample proxy timestamp(s): {', '.join(proxy_times) if proxy_times else 'NOT_RECORDED'}",
        f"- Historic HDFC Ltd legacy-security-ID probes: {legacy_passed}/{len(legacy)} passed",
        f"- Deep daily-history probe: {data.get('daily_history_probe', {}).get('status', 'NOT_RUN')}",
        f"- Historical-weight candidate cache: {weight.get('status', 'NOT_RUN')}; {weight.get('rows', 'N/A')} rows, {weight.get('ticker_columns', 'N/A')} ticker columns, {weight.get('first_date', 'N/A')} to {weight.get('last_date', 'N/A')}",
        f"- Weight candidate licence: {weight.get('license', 'NOT_RECORDED')}; commercial use permitted: {weight.get('commercial_use_permitted', 'NOT_RECORDED')}",
        "- This is a five-symbol/two-date market-data sample, not full-universe OHLCV certification.",
        "- Raw bars, prices, security IDs, credentials and tokens are not stored in this report.",
        "- C1 remains gated by official/authorised point-in-time weights, the 2025-09 onward weight gap, full historical security identity and coverage, and index-basket reconciliation.",
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
