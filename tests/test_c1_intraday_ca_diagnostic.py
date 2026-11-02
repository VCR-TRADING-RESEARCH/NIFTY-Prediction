import math

from scripts.constituent_weekly.audit_c1_intraday_ca_diagnostic import classify_intraday_scale


def test_raw_scale_detected_for_bonus():
    assert classify_intraday_scale(0.51, 0.5) == "RAW_SCALE_UNADJUSTED_INTRADAY"


def test_adjusted_scale_detected_for_bonus():
    assert classify_intraday_scale(0.99, 0.5) == "ADJUSTED_SCALE_INTRADAY"


def test_raw_scale_detected_for_split_bonus():
    assert classify_intraday_scale(0.102, 0.1) == "RAW_SCALE_UNADJUSTED_INTRADAY"


def test_ambiguous_market_gap_is_not_forced_to_pass():
    assert classify_intraday_scale(0.67, 0.5) == "AMBIGUOUS_GAP_OR_SCALE"


def test_invalid_ratio_and_factor():
    assert classify_intraday_scale(float("nan"), 0.5) == "INVALID_RATIO"
    assert classify_intraday_scale(1.0, 1.0) == "INVALID_EXPECTED_FACTOR"
