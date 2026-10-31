from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
STATUS = ROOT / "research" / "constituent_weekly" / "STATUS.md"
MANIFEST = ROOT / "research" / "constituent_weekly" / "C1_OFFICIAL_WEIGHT_MANIFEST.json"
START = "<!-- C1_FETCH_STATUS_START -->"
END = "<!-- C1_FETCH_STATUS_END -->"


def main() -> int:
    if MANIFEST.exists():
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    else:
        data = {"status": "NO_MANIFEST", "families": {}}
    stamp = datetime.now(timezone.utc).isoformat()
    lines = [
        START,
        "## Latest automated C1 source-fetch result",
        "",
        f"- Recorded at (UTC): {stamp}",
        f"- Official report retrieval status: {data.get('status')}",
        "- This result is source-fetch/inventory only; it is not a historical weight, membership, or trading-data validation.",
    ]
    for family, result in data.get("families", {}).items():
        lines.append(
            f"- {family}: {result.get('status')}; file={result.get('filename')}; sha256={result.get('sha256')}; error={result.get('error')}"
        )
    lines.extend([
        "- C1 acceptance: NOT PASSED; historical reports, point-in-time availability, membership and basket reconciliation remain required.",
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
    print(f"Updated C1 status with source-fetch result: {data.get('status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
