from __future__ import annotations

import pandas as pd

from scripts.audit_dhan_anchor_source import find_nifty50_security, parse_dhan_payload


def test_dhan_payload_epochs_become_ist_timestamps_and_valid_ohlc():
    epoch = int(pd.Timestamp("2024-02-01 10:00:00", tz="Asia/Kolkata").timestamp())
    payload = {
        "timestamp": [epoch, epoch + 60],
        "open": [22000.0, 22001.0],
        "high": [22005.0, 22004.0],
        "low": [21998.0, 22000.5],
        "close": [22002.0, 22002.0],
    }
    bars = parse_dhan_payload(payload)
    assert len(bars) == 2
    assert str(bars["timestamp"].dt.tz) == "Asia/Kolkata"
    assert bars.iloc[0]["timestamp"] == pd.Timestamp("2024-02-01 10:00:00", tz="Asia/Kolkata")


def test_dhan_payload_drops_invalid_ohlc_and_handles_empty_response():
    epoch = int(pd.Timestamp("2024-02-01 10:00:00", tz="Asia/Kolkata").timestamp())
    invalid = {
        "timestamp": [epoch],
        "open": [22000.0],
        "high": [21990.0],
        "low": [21995.0],
        "close": [22001.0],
    }
    assert parse_dhan_payload(invalid).empty
    assert parse_dhan_payload({}).empty


def test_dhan_security_mapping_refuses_ambiguous_matches():
    master = pd.DataFrame({
        "SEM_SMST_SECURITY_ID": ["13", "99"],
        "SEM_SEGMENT": ["IDX_I", "IDX_I"],
        "SEM_EXM_EXCH_ID": ["NSE", "NSE"],
        "SEM_CUSTOM_SYMBOL": ["NIFTY 50", "NIFTY 50 INDEX"],
    })
    try:
        find_nifty50_security(master)
    except ValueError as exc:
        assert "exactly one" in str(exc)
    else:
        raise AssertionError("Ambiguous NIFTY 50 security should not be selected")


def test_dhan_security_mapping_accepts_single_index_match():
    master = pd.DataFrame({
        "SEM_SMST_SECURITY_ID": ["13", "99"],
        "SEM_SEGMENT": ["IDX_I", "NSE_EQ"],
        "SEM_EXM_EXCH_ID": ["NSE", "NSE"],
        "SEM_CUSTOM_SYMBOL": ["NIFTY 50", "RELIANCE"],
    })
    assert find_nifty50_security(master) == "13"
