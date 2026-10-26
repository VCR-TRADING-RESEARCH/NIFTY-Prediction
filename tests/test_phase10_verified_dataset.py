from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.fetch_dhan_anchor_history import _window
from scripts.rebuild_dhan_verified_dataset import (
    NEW_FEATURES,
    add_causal_features,
    build_official_daily_calendar,
    row_source_gate,
)


def _valid_minutes(day: str, count: int = 300) -> pd.DataFrame:
    start = pd.Timestamp(day + " 09:15:00", tz="Asia/Kolkata")
    ts = [start + pd.Timedelta(minutes=i) for i in range(count)]
    opens = np.full(count, 100.0)
    closes = np.full(count, 100.1)
    return pd.DataFrame({
        "timestamp": ts,
        "open": opens,
        "high": np.maximum(opens, closes) + 0.05,
        "low": np.minimum(opens, closes) - 0.05,
        "close": closes,
        "session_date": [pd.Timestamp(day).date()] * count,
        "clock_time": [t.time() for t in ts],
    })


def test_dhan_request_windows_are_at_most_90_days_and_contiguous():
    start, end, chunks = _window()
    assert chunks
    assert chunks[0][0] == start
    assert chunks[-1][1] == end
    for i, (chunk_start, chunk_end, path) in enumerate(chunks):
        assert chunk_start <= chunk_end
        assert (chunk_end - chunk_start).days + 1 <= 90
        assert path.name == f"dhan_{chunk_start:%Y%m%d}_{chunk_end:%Y%m%d}.csv"
        if i:
            assert chunks[i - 1][1] + pd.Timedelta(days=1) == chunk_start


def test_official_session_calendar_does_not_shift_when_dhan_bars_are_missing():
    official = pd.DataFrame({
        "session_date": ["2021-10-21", "2021-10-22", "2021-10-25", "2021-10-26"],
        "official_open": [98.0, 99.0, 99.5, 100.0],
        "official_high": [100.0, 101.0, 101.0, 101.0],
        "official_low": [97.0, 98.5, 98.8, 99.0],
        "official_close": [99.0, 100.0, 100.2, 100.1],
    })
    minutes = _valid_minutes("2021-10-26")
    daily, quality = build_official_daily_calendar(official, minutes)
    assert list(daily["session_date"].dt.strftime("%Y-%m-%d")) == official["session_date"].tolist()
    bars = daily.set_index(daily["session_date"].dt.strftime("%Y-%m-%d"))["bars"]
    assert bars.loc["2021-10-21"] == 0
    assert bars.loc["2021-10-22"] == 0
    assert bars.loc["2021-10-25"] == 0
    assert bars.loc["2021-10-26"] == 300
    assert daily.loc[daily["session_date"].eq(pd.Timestamp("2021-10-21")), "session_close"].iloc[0] == 99.0
    assert quality["official_sessions_without_dhan_intraday"] == 3


def test_six_augmented_features_are_causal_to_anchor_date():
    anchor = pd.Timestamp("2024-02-01")
    before_dates = pd.bdate_range(end=anchor - pd.Timedelta(days=1), periods=35)
    before_close = 1000 * np.cumprod(1 + np.linspace(-0.003, 0.004, len(before_dates)))
    prior = pd.DataFrame({
        "session_date": before_dates,
        "session_open": before_close * 0.999,
        "session_high": before_close * 1.005,
        "session_low": before_close * 0.995,
        "session_close": before_close,
        "official_open": before_close * 0.999,
        "official_high": before_close * 1.005,
        "official_low": before_close * 0.995,
        "official_close": before_close,
        "bars": 375,
    })
    cycle = pd.DataFrame([{
        "anchor_date": anchor,
        "expiry_date": pd.Timestamp("2024-02-08"),
        "label": "UP",
        "ret_5": 0.01,
        "ret_20": 0.03,
        "rv_5": 0.004,
        "rv_20": 0.006,
        "overnight_gap": 0.002,
        "anchor_price": 1100.0,
    }])
    original = add_causal_features(cycle, prior)
    future = pd.DataFrame({
        "session_date": pd.bdate_range(start=anchor, periods=5),
        "session_open": [3000.0] * 5,
        "session_high": [4000.0] * 5,
        "session_low": [2000.0] * 5,
        "session_close": [3500.0] * 5,
        "official_open": [3000.0] * 5,
        "official_high": [4000.0] * 5,
        "official_low": [2000.0] * 5,
        "official_close": [3500.0] * 5,
        "bars": [375] * 5,
    })
    extended = add_causal_features(cycle, pd.concat([prior, future], ignore_index=True))
    assert all(name in extended.columns for name in NEW_FEATURES)
    for name in NEW_FEATURES:
        a = original.loc[0, name]
        b = extended.loc[0, name]
        if pd.isna(a):
            assert pd.isna(b)
        else:
            assert a == b


def test_row_source_gate_rejects_unverified_expiry_or_incomplete_session():
    base = {
        "calendar_status": "official_verified",
        "expiry_close_source": "NSE_official_daily_close",
        "anchor_bar_delay_minutes": 0,
        "anchor_timestamp": pd.Timestamp("2024-02-01 10:00:00", tz="Asia/Kolkata"),
        "anchor_session_bars": 375,
        "expiry_session_bars": 375,
    }
    frame = pd.DataFrame([
        base,
        {**base, "calendar_status": "weekday_heuristic_nominal"},
        {**base, "expiry_session_bars": 180},
        {**base, "anchor_bar_delay_minutes": 4},
    ])
    checked, summary = row_source_gate(frame)
    assert list(checked["source_gate_pass"]) == [True, False, False, False]
    assert list(checked["confirmatory_eligible"]) == [True, False, False, False]
    assert summary["row_source_gate_pass"] == 1
