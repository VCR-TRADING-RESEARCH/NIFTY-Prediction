from __future__ import annotations

import pandas as pd

from scripts.constituent_weekly.audit_c1_corporate_actions import (
    catalogue,
    load_member_intervals,
    normalise_type,
)


def test_action_type_map_keeps_distinct_handling_families():
    assert normalise_type("dividend") == "dividend"
    assert normalise_type("split") == "split"
    assert normalise_type("bonus") == "bonus"
    assert normalise_type("rights") == "rights"
    assert normalise_type("buyback") == "buyback"
    assert normalise_type("demerger") == "merger_demerger"
    assert normalise_type("unknown-new-event") == "unclassified"


def test_membership_ledger_excludes_zero_price_dummy():
    intervals = load_member_intervals()
    assert "DUMMYTATAM" not in set(intervals["symbol"])
    assert "TATAMOTORS" in set(intervals["symbol"])


def test_action_catalogue_resolves_dated_symbol_aliases():
    intervals = pd.DataFrame([
        {"symbol": "LTM", "valid_from": "2023-07-13", "valid_to": "2024-09-30"},
        {"symbol": "ETERNAL", "valid_from": "2025-03-28", "valid_to": ""},
        {"symbol": "TATAMOTORS", "valid_from": "2014-01-01", "valid_to": "2025-10-24"},
    ])
    events = pd.DataFrame([
        ["NSE", "LTIM", "INE214T01019", "LTIMindtree", "2024-01-15", None, "dividend", None, None, 20.0, None, None, "private source subject"],
        ["NSE", "ZOMATO", "INE758T01015", "Zomato", "2025-04-01", None, "bonus", 1, 1, None, None, None, "private source subject"],
        ["NSE", "TATAMOTORS", "INE155A01022", "Tata Motors", "2025-10-14", None, "demerger", None, None, None, None, None, "private source subject"],
        ["NSE", "DUMMYTATAM", None, "Placeholder", "2025-10-15", None, "other", None, None, None, None, None, "private source subject"],
        ["NSE", "UNKNOWN", "INE000000000", "Unknown", "2024-02-01", None, "other", None, None, None, None, None, "private source subject"],
    ], columns=[
        "exchange", "symbol", "isin", "company", "ex_date", "record_date", "type",
        "ratio_num", "ratio_den", "cash_amount", "face_value_from", "face_value_to", "raw_subject",
    ])
    result = catalogue([events], intervals)
    assert result["deduplicated_events"] == 5
    assert result["matched_pit_member_events"] == 3
    assert result["unmatched_or_non_member_events"] == 2
    assert result["events_by_type"]["dividend"] == 1
    assert result["events_by_type"]["bonus"] == 1
    assert result["events_by_type"]["merger_demerger"] == 1
    assert result["corporate_action_gate"] == "NOT_PASSED"


def test_duplicate_events_are_counted_and_deduplicated():
    intervals = pd.DataFrame([
        {"symbol": "LTM", "valid_from": "2023-07-13", "valid_to": "2024-09-30"},
    ])
    event = pd.DataFrame([
        ["NSE", "LTIM", "INE214T01019", "LTIMindtree", "2024-01-15", None, "dividend", None, None, 20.0, None, None, "private subject"],
    ], columns=[
        "exchange", "symbol", "isin", "company", "ex_date", "record_date", "type",
        "ratio_num", "ratio_den", "cash_amount", "face_value_from", "face_value_to", "raw_subject",
    ])
    result = catalogue([pd.concat([event, event], ignore_index=True)], intervals)
    assert result["raw_rows_in_window"] == 2
    assert result["duplicate_rows"] == 1
    assert result["deduplicated_events"] == 1


def test_unknown_actions_remain_unclassified_and_gate_stays_closed():
    intervals = pd.DataFrame([
        {"symbol": "LTM", "valid_from": "2023-07-13", "valid_to": "2024-09-30"},
    ])
    event = pd.DataFrame([
        ["NSE", "LTIM", "INE214T01019", "LTIMindtree", "2024-01-15", None, "spin_off", None, None, None, None, None, "private subject"],
    ], columns=[
        "exchange", "symbol", "isin", "company", "ex_date", "record_date", "type",
        "ratio_num", "ratio_den", "cash_amount", "face_value_from", "face_value_to", "raw_subject",
    ])
    result = catalogue([event], intervals)
    assert result["events_by_type"]["unclassified"] == 1
    assert result["corporate_action_gate"] == "NOT_PASSED"


def test_public_summary_excludes_raw_event_fields():
    intervals = pd.DataFrame([
        {"symbol": "LTM", "valid_from": "2023-07-13", "valid_to": "2024-09-30"},
    ])
    event = pd.DataFrame([
        ["NSE", "LTIM", "INE214T01019", "LTIMindtree", "2024-01-15", None, "dividend", None, None, 20.0, None, None, "private subject"],
    ], columns=[
        "exchange", "symbol", "isin", "company", "ex_date", "record_date", "type",
        "ratio_num", "ratio_den", "cash_amount", "face_value_from", "face_value_to", "raw_subject",
    ])
    result = catalogue([event], intervals)
    forbidden = {"symbol", "isin", "company", "cash_amount", "ratio_num", "ratio_den", "raw_subject"}
    assert not (forbidden & set(result))
    assert result["raw_event_rows_published"] is False

def test_corporate_action_audit_uses_shared_expanded_cache_directory():
    from scripts.constituent_weekly.audit_c1_daily_history import resolve_tejhq_encrypted_cache_dir

    configured = "${{ runner.temp }}/bup01-tejhq-encrypted"
    resolved = resolve_tejhq_encrypted_cache_dir(configured)
    assert resolved.is_absolute()
    assert resolved.name == "bup01-tejhq-encrypted"
