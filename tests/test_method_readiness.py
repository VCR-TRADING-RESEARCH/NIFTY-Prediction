from __future__ import annotations

from scripts.audit_new_method_readiness import assess_source_gate, build_method_matrix


def test_source_gate_blocks_empirical_search_when_anchor_is_provisional():
    quality = {
        "confirmatory_status": "BLOCKED: 10:00 anchor not independently validated",
        "source_quality": {
            "official_daily_close_validation": {
                "archive_close_mismatches_over_1_point": 1719,
            }
        },
        "target_construction": {"confirmatory_eligible_rows": 0},
        "independent_recent_minute_crosscheck": {"available": False},
    }
    summary = {"confirmatory_status": "BLOCKED"}
    status, blockers = assess_source_gate(quality, summary)
    assert status == "BLOCKED_EMPIRICAL_METHOD_SEARCH"
    assert len(blockers) >= 4
    assert any("independent 10:00 anchor" in item for item in blockers)


def test_source_gate_requires_explicit_pass_evidence():
    quality = {
        "confirmatory_status": "PASS",
        "source_quality": {
            "official_daily_close_validation": {
                "archive_close_mismatches_over_1_point": 0,
            }
        },
        "target_construction": {"confirmatory_eligible_rows": 250},
        "independent_recent_minute_crosscheck": {"available": True},
    }
    summary = {"confirmatory_status": "PASS"}
    status, blockers = assess_source_gate(quality, summary)
    assert status == "READY_FOR_PREREGISTERED_METHOD_COMPARISON"
    assert blockers == []


def test_method_matrix_distinguishes_present_features_from_missing_sources():
    columns = {"ret_5", "ret_20", "rv_5", "rv_20", "overnight_gap"}
    matrix = build_method_matrix(columns, set())
    by_family = {row["family"]: row for row in matrix}
    assert by_family["Multiscale trend, gap, range and volatility interactions"]["current_input_status"] == "features_present_source_gate_blocked"
    assert by_family["Point-in-time options surface and positioning"]["current_input_status"] == "unavailable_in_current_feature_table"
    assert by_family["Global overnight and cross-market inputs"]["current_input_status"] == "unavailable_in_current_feature_table"
    assert by_family["PySR symbolic and Quantevolve-inspired bounded search"]["current_input_status"] == "not_run_deferred_by_source_gate"


def test_source_gate_fails_closed_when_mismatch_count_is_missing():
    quality = {
        "confirmatory_status": "PASS",
        "source_quality": {"official_daily_close_validation": {}},
        "target_construction": {"confirmatory_eligible_rows": 250},
        "independent_recent_minute_crosscheck": {"available": True},
    }
    status, blockers = assess_source_gate(quality, {"confirmatory_status": "PASS"})
    assert status == "BLOCKED_EMPIRICAL_METHOD_SEARCH"
    assert any("mismatch count" in item for item in blockers)
