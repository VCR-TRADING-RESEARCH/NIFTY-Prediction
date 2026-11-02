from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUS = ROOT / "research" / "constituent_weekly" / "STATUS.md"
MANIFEST = ROOT / "research" / "constituent_weekly" / "C1_OFFICIAL_WEIGHT_MANIFEST.json"
START = "<!-- C1_FETCH_STATUS_START -->"
END = "<!-- C1_FETCH_STATUS_END -->"


def main() -> int:
    if MANIFEST.exists():
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    else:
        data = {"status": "NO_MANIFEST", "archives": []}

    stamp = datetime.now(timezone.utc).isoformat()
    lines = [
        START,
        "## Latest automated C1 offline-source audit",
        "",
        f"- Recorded at (UTC): {stamp}",
        f"- Audit status: {data.get('status')}",
        f"- Network collection performed: {data.get('network_access_performed', False)}",
        "- This is file-integrity/schema evidence only; it is not point-in-time membership, source permission, weight validity or trading-data validation.",
    ]
    for archive in data.get("archives", []):
        lines.append(
            f"- {archive.get('filename')}: {archive.get('status')}; sha256={archive.get('sha256')}; zip_members={archive.get('file_count')}"
        )
        for member in archive.get("members", []):
            audit = member.get("weight_table_audit", {})
            if audit:
                lines.append(
                    f"  - {member.get('name')}: {audit.get('status')}; rows={audit.get('constituent_rows')}; unique={audit.get('unique_symbols')}; weights_sum_100={audit.get('weights_sum_to_100_within_0_01')}"
                )
    lines.extend([
        "- C1 acceptance: NOT PASSED until licensed/authorised point-in-time weights, membership, identifiers, corporate actions, equity bar coverage and basket reconciliation pass.",
        END,
    ])
    block = "\n".join(lines)
    current = STATUS.read_text(encoding="utf-8")
    if START in current and END in current:
        before = current.split(START, 1)[0].rstrip()
        after = current.split(END, 1)[1].lstrip()
        updated = before + "\n\n" + block + "\n\n" + after
    else:
        updated = current.rstrip() + "\n\n" + block + "\n"
    STATUS.write_text(updated, encoding="utf-8")
    print(f"Updated C1 status with offline source-audit result: {data.get('status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
