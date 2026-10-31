from __future__ import annotations

import calendar
import csv
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# These checks are offline and deliberately independent of NSE/Dhan endpoints.
DATA = ROOT / "data" / "constituent_weekly" / "nifty50_membership_intervals.csv"
AUDIT = ROOT / "research" / "constituent_weekly" / "C1_MEMBERSHIP_AUDIT.json"


def load_rows():
    with DATA.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def month_ends(start: date, end: date):
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        value = date(year, month, calendar.monthrange(year, month)[1])
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


def test_month_end_membership_cardinality_matches_official_temporary_dummy_rule():
    rows = load_rows()
    dates = list(month_ends(date(2018, 4, 1), date(2026, 10, 31)))
    assert len(dates) == 103
    for on in dates:
        names = active_members(rows, on)
        # NSE Indices temporarily added DUMMYTATAM at zero price for the
        # October 2025 Tata Motors demerger adjustment; this creates 51 rows
        # for the October 2025 month-end snapshot, not a 50-name error.
        expected = 51 if on == date(2025, 10, 31) else 50
        assert len(names) == expected, f"{on}: expected {expected} rows, got {len(names)}"
        assert len(set(names)) == expected, f"{on}: duplicate active symbols"


def test_wipro_to_bse_replacement_is_effective_2026_09_30():
    rows = load_rows()
    wipro = [r for r in rows if r["symbol"] == "WIPRO"]
    bse = [r for r in rows if r["symbol"] == "BSE"]
    assert len(wipro) == 1
    assert wipro[0]["valid_to"] == "2026-09-30"
    assert len(bse) == 1
    assert bse[0]["valid_from"] == "2026-09-30"
    assert "WIPRO" in active_members(rows, date(2026, 9, 29))
    assert "BSE" not in active_members(rows, date(2026, 9, 29))
    assert "WIPRO" not in active_members(rows, date(2026, 9, 30))
    assert "BSE" in active_members(rows, date(2026, 9, 30))


def test_tata_motors_symbol_change_is_point_in_time_correct():
    rows = load_rows()
    legacy = [r for r in rows if r["symbol"] == "TATAMOTORS"]
    passenger = [r for r in rows if r["symbol"] == "TMPV"]
    assert len(legacy) == 1
    assert legacy[0]["valid_to"] == "2025-10-24"
    assert len(passenger) == 1
    assert passenger[0]["valid_from"] == "2025-10-24"
    pre = active_members(rows, date(2025, 10, 23))
    ex = active_members(rows, date(2025, 10, 24))
    assert "TATAMOTORS" in pre and "TMPV" not in pre
    assert "TATAMOTORS" not in ex and "TMPV" in ex


def test_temporary_tata_dummy_is_included_then_removed_and_not_a_tradeable_stock():
    rows = load_rows()
    dummy = [r for r in rows if r["symbol"] == "DUMMYTATAM"]
    assert len(dummy) == 1
    row = dummy[0]
    assert row["valid_from"] == "2025-10-14"
    assert row["valid_to"] == "2025-11-17"
    assert row["member_type"] == "zero_price_dummy"
    assert row["market_data_required"] == "FALSE"
    assert "DUMMYTATAM" not in active_members(rows, date(2025, 10, 13))
    assert "DUMMYTATAM" in active_members(rows, date(2025, 10, 14))
    assert "DUMMYTATAM" in active_members(rows, date(2025, 11, 16))
    assert "DUMMYTATAM" not in active_members(rows, date(2025, 11, 17))
    assert len(active_members(rows, date(2025, 11, 17))) == 50


def test_membership_data_contains_no_fabricated_index_weights():
    rows = load_rows()
    assert rows
    assert all(row["index_id"] == "217" and row["index_name"] == "Nifty 50" for row in rows)
    assert all(row["weightage"] == "" for row in rows)
    assert len({(r["symbol"], r["valid_from"], r["valid_to"]) for r in rows}) == len(rows)


def test_machine_audit_matches_membership_artifact():
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    assert audit["membership_status"] == "PASS_WITH_LIMITATIONS"
    assert audit["overall_c1_status"] == "BLOCKED"
    assert audit["project_nifty50_interval_rows"] == 86
    assert audit["unique_symbols_across_history"] == 85
    assert audit["validation"]["month_end_dates_checked"] == 103
    assert audit["validation"]["dates_with_expected_cardinality"] == 103
    assert audit["validation"]["october_2025_expected_dummy_exception_count"] == 51
    assert audit["source_weightage_values_present"] == 0
