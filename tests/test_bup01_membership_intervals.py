from __future__ import annotations

import csv
import calendar
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "constituent_weekly" / "nifty50_membership_intervals.csv"


def load_rows():
    with DATA.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def month_ends(start: date, end: date):
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        last = calendar.monthrange(year, month)[1]
        value = date(year, month, last)
        if start <= value <= end:
            yield value
        month += 1
        if month == 13:
            year += 1
            month = 1


def active_members(rows, on: date):
    active = []
    for row in rows:
        start = date.fromisoformat(row["valid_from"])
        end = date.fromisoformat(row["valid_to"]) if row["valid_to"] else None
        if start <= on and (end is None or on < end):
            active.append(row["symbol"])
    return active


def test_membership_has_50_unique_names_on_each_month_end_from_2018():
    rows = load_rows()
    dates = list(month_ends(date(2018, 4, 1), date(2026, 10, 31)))
    assert len(dates) == 103
    for on in dates:
        names = active_members(rows, on)
        assert len(names) == 50, f"{on}: expected 50 rows, got {len(names)}"
        assert len(set(names)) == 50, f"{on}: duplicate active symbols"


def test_wipro_to_bse_replacement_is_effective_2026_09_30():
    rows = load_rows()
    wipro = [r for r in rows if r["symbol"] == "WIPRO"]
    bse = [r for r in rows if r["symbol"] == "BSE"]
    assert len(wipro) == 1
    assert wipro[0]["valid_to"] == "2026-09-30"
    assert len(bse) == 1
    assert bse[0]["valid_from"] == "2026-09-30"
    assert active_members(rows, date(2026, 9, 29)).count("WIPRO") == 1
    assert "BSE" not in active_members(rows, date(2026, 9, 29))
    assert "WIPRO" not in active_members(rows, date(2026, 9, 30))
    assert active_members(rows, date(2026, 9, 30)).count("BSE") == 1


def test_membership_data_contains_no_fabricated_index_weights():
    rows = load_rows()
    assert rows
    assert all(row["index_id"] == "217" and row["index_name"] == "Nifty 50" for row in rows)
    assert all(row["weightage"] == "" for row in rows)
    assert len({(r["symbol"], r["valid_from"], r["valid_to"]) for r in rows}) == len(rows)

def test_machine_audit_matches_membership_artifact():
    import json
    audit_path = ROOT / "research" / "constituent_weekly" / "C1_MEMBERSHIP_AUDIT.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    assert audit["membership_status"] == "PASS_WITH_LIMITATIONS"
    assert audit["overall_c1_status"] == "BLOCKED"
    assert audit["validation"]["month_end_dates_checked"] == 103
    assert audit["validation"]["failures"] == 0
    assert audit["source_weightage_values_present"] == 0
