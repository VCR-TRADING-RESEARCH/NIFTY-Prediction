from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.constituent_weekly.run_c2_panel_and_models import (
    arrays_from_body,
    equal_cycle_weights,
    event_flags,
    metrics,
    parse_target_bars,
    stock_features,
)


def _epoch(value: str) -> int:
    return int(pd.Timestamp(value, tz="Asia/Kolkata").timestamp())


def test_target_parser_uses_first_anchor_and_latest_expiry_proxy_only():
    day = "2026-10-01"
    clocks = ["10:00", "10:01", "15:13", "15:14", "15:25"]
    timestamps = [_epoch(f"{day} {clock}") for clock in clocks]
    body = {
        "timestamp": timestamps,
        "open": [100, 101, 102, 103, 104],
        "high": [101, 102, 104, 105, 999],
        "low": [99, 100, 101, 102, 103],
        "close": [100.5, 101.5, 103, 104, 999],
        "volume": [10, 11, 12, 13, 14],
    }
    result = parse_target_bars(body, {day}, {day}, require_volume=True)[day]
    assert result["anchor_ok"] is True
    assert result["expiry_ok"] is True
    assert result["anchor_open"] == 100.0
    assert result["expiry_close"] == 104.0
    assert result["expiry_time"].startswith(f"{day}T15:14:00")


def test_target_parser_rejects_invalid_ohlc_and_missing_stock_volume():
    day = "2026-10-01"
    invalid = {
        "timestamp": [_epoch(f"{day} 10:00"), _epoch(f"{day} 15:14")],
        "open": [100, 100], "high": [99, 101], "low": [98, 99],
        "close": [100, 100], "volume": [1, 1],
    }
    result = parse_target_bars(invalid, {day}, {day}, require_volume=True)[day]
    assert result["anchor_ok"] is False
    assert result["expiry_ok"] is True

    missing_volume = {k: v for k, v in invalid.items() if k != "volume"}
    assert arrays_from_body(missing_volume, require_volume=True) is None


def test_stock_features_are_asof_safe_and_ignore_future_rows():
    dates = pd.bdate_range("2026-06-01", periods=90)
    close = 100 * np.cumprod(1 + np.linspace(-0.002, 0.003, len(dates)))
    frame = pd.DataFrame({
        "session_date": dates.strftime("%Y-%m-%d"),
        "open": close * 0.999, "high": close * 1.01, "low": close * 0.99,
        "close": close, "volume": np.arange(len(dates)) + 1000,
    })
    asof = dates[75].strftime("%Y-%m-%d")
    original = stock_features(frame, asof)
    changed = frame.copy()
    changed.loc[changed["session_date"] >= asof, ["open", "high", "low", "close", "volume"]] = 1e9
    future_changed = stock_features(changed, asof)
    assert original is not None and future_changed is not None
    assert original == future_changed


def test_event_crossing_flag_is_date_bounded():
    events = pd.DataFrame([{
        "event_date": "2025-10-14",
        "affected_symbols": "TATAMOTORS;DUMMYTATAM;TMPV",
    }])
    assert event_flags("TATAMOTORS", "2025-10-08", "2025-10-14", events) == (1, 1)
    assert event_flags("TATAMOTORS", "2025-10-14", "2025-10-21", events) == (1, 0)
    assert event_flags("RELIANCE", "2025-10-08", "2025-10-14", events) == (0, 0)


def test_training_sample_weights_equalise_expiry_cycles():
    cycle_ids = pd.Series([1, 1, 2, 2, 2, 2])
    weights = equal_cycle_weights(cycle_ids)
    assert np.isclose(weights[:2].sum(), weights[2:].sum())
    assert np.isclose(weights.mean(), 1.0)


def test_model_metric_calculation_is_well_formed():
    result = metrics(np.array([0, 0, 1, 1]), np.array([0.2, 0.4, 0.6, 0.8]))
    assert result["n"] == 4
    assert result["accuracy"] == 1.0
    assert result["balanced_accuracy"] == 1.0
    assert result["brier"] < 0.1
    assert result["roc_auc"] == 1.0
