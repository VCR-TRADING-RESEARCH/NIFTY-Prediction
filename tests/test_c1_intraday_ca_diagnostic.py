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



def test_intraday_ohlc_ratios_matching_daily_adjusted_series():
    from scripts.constituent_weekly.audit_c1_intraday_ca_diagnostic import classify_intraday_vs_daily_scale
    pre = {"open": 1.01, "high": 1.02, "low": 0.99, "close": 1.00}
    ex = {"open": 1.00, "high": 1.01, "low": 1.00, "close": 1.00}
    assert classify_intraday_vs_daily_scale(pre, ex, 0.5) == "INTRADAY_MATCHES_DHAN_DAILY_ADJUSTED_SCALE"


def test_intraday_ohlc_ratios_detect_raw_bonus_scale_against_adjusted_daily():
    from scripts.constituent_weekly.audit_c1_intraday_ca_diagnostic import classify_intraday_vs_daily_scale
    pre = {"open": 2.0, "high": 2.02, "low": 1.98, "close": 2.0}
    ex = {"open": 1.0, "high": 1.01, "low": 0.99, "close": 1.0}
    assert classify_intraday_vs_daily_scale(pre, ex, 0.5) == "INTRADAY_RAW_SCALE_VS_DAILY_ADJUSTED"


def test_intraday_ohlc_ratios_detect_raw_split_bonus_scale_against_adjusted_daily():
    from scripts.constituent_weekly.audit_c1_intraday_ca_diagnostic import classify_intraday_vs_daily_scale
    pre = {"open": 10.0, "high": 10.2, "low": 9.8, "close": 10.0}
    ex = {"open": 1.0, "high": 1.02, "low": 0.98, "close": 1.0}
    assert classify_intraday_vs_daily_scale(pre, ex, 0.1) == "INTRADAY_RAW_SCALE_VS_DAILY_ADJUSTED"


def test_intraday_daily_cross_endpoint_ratio_stays_ambiguous_when_neither_scale_fits():
    from scripts.constituent_weekly.audit_c1_intraday_ca_diagnostic import classify_intraday_vs_daily_scale
    pre = {"open": 1.5, "high": 1.5, "low": 1.5, "close": 1.5}
    ex = {"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0}
    assert classify_intraday_vs_daily_scale(pre, ex, 0.5) == "AMBIGUOUS_INTRADAY_DAILY_SCALE"
