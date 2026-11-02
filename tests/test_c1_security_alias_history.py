from __future__ import annotations

from pathlib import Path

from scripts.constituent_weekly.security_identity import point_in_time_symbol

ROOT = Path(__file__).resolve().parents[1]
ALIASES = ROOT / "data" / "constituent_weekly" / "security_alias_history.csv"


def test_ltimindtree_membership_period_uses_ltim_not_later_ltm():
    assert point_in_time_symbol("LTM", "2023-07-13", ALIASES) == "LTIM"
    assert point_in_time_symbol("LTM", "2024-09-29", ALIASES) == "LTIM"
    assert point_in_time_symbol("LTM", "2024-09-30", ALIASES) == "LTIM"
    assert point_in_time_symbol("LTM", "2026-02-26", ALIASES) == "LTIM"
    assert point_in_time_symbol("LTM", "2026-02-27", ALIASES) == "LTM"


def test_eternal_membership_entry_alias_uses_zomato_until_exchange_rename():
    assert point_in_time_symbol("ETERNAL", "2025-03-28", ALIASES) == "ZOMATO"
    assert point_in_time_symbol("ETERNAL", "2025-04-08", ALIASES) == "ZOMATO"
    assert point_in_time_symbol("ETERNAL", "2025-04-09", ALIASES) == "ETERNAL"


def test_tataconsum_symbol_alias_respects_2020_event_date():
    assert point_in_time_symbol("TATACONSUM", "2020-02-26", ALIASES) == "TATAGLOBAL"
    assert point_in_time_symbol("TATACONSUM", "2020-02-27", ALIASES) == "TATACONSUM"


def test_tata_motors_alias_respects_rename_date_but_not_adjustment():
    assert point_in_time_symbol("TMPV", "2025-10-23", ALIASES) == "TATAMOTORS"
    assert point_in_time_symbol("TMPV", "2025-10-24", ALIASES) == "TMPV"


def test_hdfc_remains_separate_and_is_not_aliased_to_hdfcbank():
    assert point_in_time_symbol("HDFC", "2023-06-30", ALIASES) == "HDFC"
    assert point_in_time_symbol("HDFCBANK", "2023-06-30", ALIASES) == "HDFCBANK"
