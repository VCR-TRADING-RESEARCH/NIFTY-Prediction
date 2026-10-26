from __future__ import annotations

import pandas as pd

from scripts.compare_anchor_sources import compare_weekly_labels, normalize_timestamps


def test_naive_secondary_timestamps_are_localized_to_ist_for_comparison():
    naive = pd.Series(pd.to_datetime(["2024-02-01 10:00:00", "2024-02-02 10:03:00"]))
    aware = pd.Series(pd.to_datetime(["2024-02-01 10:00:00+05:30", "2024-02-02 10:03:00+05:30"]))
    normalized_naive = normalize_timestamps(naive)
    normalized_aware = normalize_timestamps(aware)
    assert str(normalized_naive.dt.tz) == "Asia/Kolkata"
    assert normalized_naive.equals(normalized_aware)


def test_weekly_label_sensitivity_uses_same_expiry_close_for_each_anchor():
    weekly = pd.DataFrame({
        "anchor_date": ["2024-02-01", "2024-02-02"],
        "anchor_price": [100.0, 100.0],
        "expiry_close": [100.5, 99.5],
        "label": ["UP", "DOWN"],
    })
    anchor_comparison = pd.DataFrame({
        "session_date": [pd.Timestamp("2024-02-01").date(), pd.Timestamp("2024-02-02").date()],
        "secondary_anchor_open": [101.0, 99.0],
        "absolute_anchor_open_difference": [1.0, 1.0],
        "mismatch_over_1_point": [False, False],
    })
    compared, stats = compare_weekly_labels(weekly, anchor_comparison)
    assert len(compared) == 2
    assert stats["primary_vs_secondary_direction_switches"] == 2
    assert stats["label_switch_rate"] == 1.0
    assert list(compared["secondary_anchor_label"]) == ["DOWN", "UP"]


def test_equal_anchor_prices_leave_weekly_direction_unchanged():
    weekly = pd.DataFrame({
        "anchor_date": ["2024-02-01"],
        "anchor_price": [100.0],
        "expiry_close": [105.0],
        "label": ["UP"],
    })
    anchor_comparison = pd.DataFrame({
        "session_date": [pd.Timestamp("2024-02-01").date()],
        "secondary_anchor_open": [100.0],
        "absolute_anchor_open_difference": [0.0],
        "mismatch_over_1_point": [False],
    })
    compared, stats = compare_weekly_labels(weekly, anchor_comparison)
    assert stats["primary_vs_secondary_direction_switches"] == 0
    assert stats["label_agreement_rate"] == 1.0
    assert compared.iloc[0]["primary_label_recomputed"] == "UP"
    assert compared.iloc[0]["secondary_anchor_label"] == "UP"
