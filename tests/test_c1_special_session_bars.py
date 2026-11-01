from __future__ import annotations

import pandas as pd

from scripts.constituent_weekly.probe_c1_special_session_bars import (
    normalize_nse_frame,
    validate_rows,
)


def test_normalize_legacy_bhavcopy_schema():
    raw = pd.DataFrame({
        "SYMBOL": ["HDFC", "HDFCBANK"],
        "SERIES": ["EQ", "EQ"],
        "TIMESTAMP": ["07-NOV-2018", "07-NOV-2018"],
        "OPEN": [1980.0, 2100.0],
        "HIGH": [1990.0, 2110.0],
        "LOW": [1970.0, 2090.0],
        "CLOSE": [1985.0, 2105.0],
        "TOTTRDQTY": [12345, 54321],
        "ISIN": ["INE001A01036", "INE040A01034"],
    })
    result = validate_rows(normalize_nse_frame(raw), "HDFC", "2018-11-07")
    assert result["status"] == "VALID"
    assert result["row_count"] == 1
    assert result["isin_present"] is True


def test_normalize_new_sec_bhavdata_schema():
    raw = pd.DataFrame({
        "SYMBOL": ["TATAMOTORS"],
        "SERIES": ["EQ"],
        "DATE1": ["21-OCT-2025"],
        "OPEN_PRICE": [402.8],
        "HIGH_PRICE": [403.4],
        "LOW_PRICE": [400.05],
        "CLOSE_PRICE": [401.85],
        "TTL_TRD_QNTY": [3449156],
    })
    result = validate_rows(normalize_nse_frame(raw), "TATAMOTORS", "2025-10-21")
    assert result["status"] == "VALID"


def test_normalize_udiff_schema():
    raw = pd.DataFrame({
        "TckrSymb": ["HDFC"],
        "SctySrs": ["EQ"],
        "TradDt": ["2020-02-01"],
        "OpnPric": [2400.0],
        "HghPric": [2410.0],
        "LwPric": [2390.0],
        "ClsPric": [2405.0],
        "TtlTradgVol": [1000],
    })
    result = validate_rows(normalize_nse_frame(raw), "HDFC", "2020-02-01")
    assert result["status"] == "VALID"


def test_wrong_security_is_not_used():
    raw = pd.DataFrame({
        "SYMBOL": ["HDFCBANK"],
        "SERIES": ["EQ"],
        "TIMESTAMP": ["07-NOV-2018"],
        "OPEN": [100.0],
        "HIGH": [101.0],
        "LOW": [99.0],
        "CLOSE": [100.5],
        "TOTTRDQTY": [1000],
    })
    result = validate_rows(normalize_nse_frame(raw), "HDFC", "2018-11-07")
    assert result["status"] == "NO_EQ_ROW"
    assert result["valid"] is False


def test_duplicate_target_rows_are_rejected():
    raw = pd.DataFrame({
        "SYMBOL": ["HDFC", "HDFC"],
        "SERIES": ["EQ", "EQ"],
        "TIMESTAMP": ["07-NOV-2018", "07-NOV-2018"],
        "OPEN": [100.0, 100.0],
        "HIGH": [101.0, 101.0],
        "LOW": [99.0, 99.0],
        "CLOSE": [100.5, 100.5],
        "TOTTRDQTY": [1000, 1000],
    })
    result = validate_rows(normalize_nse_frame(raw), "HDFC", "2018-11-07")
    assert result["status"] == "DUPLICATE_EQ_ROWS"
    assert result["valid"] is False


def test_invalid_ohlc_invariants_are_rejected():
    raw = pd.DataFrame({
        "SYMBOL": ["HDFC"],
        "SERIES": ["EQ"],
        "TIMESTAMP": ["07-NOV-2018"],
        "OPEN": [102.0],
        "HIGH": [101.0],
        "LOW": [99.0],
        "CLOSE": [100.5],
        "TOTTRDQTY": [1000],
    })
    result = validate_rows(normalize_nse_frame(raw), "HDFC", "2018-11-07")
    assert result["status"] == "INVALID_OHLCV"
    assert result["valid"] is False
