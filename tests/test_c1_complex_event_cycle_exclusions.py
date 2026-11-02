from scripts.constituent_weekly.audit_c1_complex_event_cycle_exclusions import (
    coverage_sensitivity, event_overlaps_cycle, passes_member_coverage,
)


def test_event_on_anchor_is_not_inside_prediction_window():
    assert not event_overlaps_cycle("2024-01-08", "2024-01-11", "2024-01-08")


def test_event_on_expiry_is_inside_prediction_window():
    assert event_overlaps_cycle("2024-01-08", "2024-01-11", "2024-01-11")


def test_event_after_expiry_is_outside_prediction_window():
    assert not event_overlaps_cycle("2024-01-08", "2024-01-11", "2024-01-12")


def test_both_registered_coverage_thresholds_apply():
    assert passes_member_coverage(47, 50)
    assert passes_member_coverage(47, 49)
    assert not passes_member_coverage(46, 49)
    assert not passes_member_coverage(46, 50)


def test_exclusion_sensitivity_reports_a_coverage_breach():
    result = coverage_sensitivity(
        {0: 50, 1: 50, 2: 49},
        {0: 50, 1: 50, 2: 47},
        {0: 3, 1: 4},
    )
    assert result["baseline_passing_cycles"] == 3
    assert result["post_exclusion_passing_cycles"] == 2
    assert result["post_exclusion_failing_cycles"] == 1
    assert result["status"] == "FAIL_47_94_SOME_CYCLES"
