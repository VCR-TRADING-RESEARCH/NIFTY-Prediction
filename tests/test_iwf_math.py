from decimal import Decimal

import pytest

from scripts.constituent_weekly.iwf_math import (
    IWF_EXCLUSION_IDS,
    IWFInputError,
    assess_exclusion_coverage,
    calculate_freefloat_weights,
    calculate_iwf,
)


def test_nse_published_iwf_example_reproduces_six_decimal_result():
    # NSE Indices IWF guideline, page 2.
    exclusions = [
        ("promoter", 1_975_000),
        ("fdi", 50_000),
        ("promoter_dr", 250_000),
        ("cross_holding", 12_575),
        ("employee_welfare_trust", 145_987),
        ("public_lock_in", 1_478_500),
    ]
    assert calculate_iwf(10_000_000, exclusions) == Decimal("0.608794")


def test_iwf_rejects_duplicate_position_to_prevent_double_deduction():
    with pytest.raises(IWFInputError, match="duplicate"):
        calculate_iwf(1000, [("same_position", 100), ("same_position", 100)])


def test_iwf_requires_total_shares_denominator_and_valid_share_counts():
    with pytest.raises(IWFInputError):
        calculate_iwf(0, [])
    with pytest.raises(IWFInputError):
        calculate_iwf(100, [("x", -1)])
    with pytest.raises(IWFInputError):
        calculate_iwf(100, [("x", 101)])


def test_all_22_exclusion_dispositions_are_mandatory():
    complete = {i: "QUANTIFIED" for i in IWF_EXCLUSION_IDS}
    assert assess_exclusion_coverage(complete)["passed"] is True

    incomplete = dict(complete)
    del incomplete[22]
    result = assess_exclusion_coverage(incomplete)
    assert result["passed"] is False
    assert result["missing_ids"] == [22]


def test_unresolved_exclusion_does_not_pass_coverage_gate():
    status = {i: "QUANTIFIED" for i in IWF_EXCLUSION_IDS}
    status[11] = "UNRESOLVED"
    result = assess_exclusion_coverage(status)
    assert result["passed"] is False
    assert result["unresolved_ids"] == [11]


def test_freefloat_weights_normalise_full_market_cap_times_iwf():
    result = calculate_freefloat_weights([
        ("AAA", 1000, Decimal("0.50")),
        ("BBB", 500, Decimal("1.00")),
    ])
    assert result["AAA"] == Decimal("0.500000000000")
    assert result["BBB"] == Decimal("0.500000000000")
    assert sum(result.values()) == Decimal("1.000000000000")


def test_freefloat_weight_rejects_duplicate_symbol_or_bad_iwf():
    with pytest.raises(IWFInputError, match="duplicate"):
        calculate_freefloat_weights([("AAA", 100, 0.5), ("AAA", 100, 0.5)])
    with pytest.raises(IWFInputError, match="between 0 and 1"):
        calculate_freefloat_weights([("AAA", 100, 1.1)])
