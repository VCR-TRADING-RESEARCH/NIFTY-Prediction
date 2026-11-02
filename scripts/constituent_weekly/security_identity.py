from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ALIAS_PATH = ROOT / "data" / "constituent_weekly" / "security_alias_history.csv"


def point_in_time_symbol(
    canonical_symbol: str,
    as_of: str | date,
    alias_path: Path = DEFAULT_ALIAS_PATH,
) -> str:
    """Resolve a project-canonical symbol to the exchange symbol on a date.

    This maps names/aliases only. It never merges distinct securities or
    calculates a corporate-action price adjustment.
    """
    stamp = date.fromisoformat(as_of) if isinstance(as_of, str) else as_of
    matches: list[str] = []
    with alias_path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["canonical_symbol"].strip().upper() != canonical_symbol.upper():
                continue
            start = date.fromisoformat(row["effective_from"])
            end_raw = row["effective_to_exclusive"].strip()
            end = date.fromisoformat(end_raw) if end_raw else None
            if stamp >= start and (end is None or stamp < end):
                matches.append(row["point_in_time_symbol"].strip().upper())
    if len(matches) > 1:
        raise ValueError(
            f"Overlapping point-in-time symbol aliases for {canonical_symbol} on {stamp.isoformat()}."
        )
    return matches[0] if matches else canonical_symbol.upper()
