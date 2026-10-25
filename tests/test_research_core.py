from __future__ import annotations

import pandas as pd

from scripts.research_core import (
    _parse_timestamp_column, load_minute_files, daily_aggregates, construct_weekly_table,
)


def _synthetic_minutes(start="2019-02-13", end="2019-03-01"):
    dates = pd.bdate_range(start=start, end=end)
    rows = []
    for day_index, session_date in enumerate(dates):
        stamps = pd.date_range(
            session_date.replace(hour=9, minute=15),
            session_date.replace(hour=15, minute=29),
            freq="min",
            tz="Asia/Kolkata",
        )
        base = 10000.0 + day_index * 20.0
        for stamp in stamps:
            open_price = base
            close_price = base + 1.0
            if stamp.strftime("%H:%M") == "10:00":
                open_price = base + 5.0
                close_price = base + 25.0  # must not be used as the 10:00 reference
            if stamp.strftime("%H:%M") == "15:28":
                close_price = base + 8.0
            if stamp.strftime("%H:%M") == "15:29":
                close_price = base + 10.0
            high = max(open_price, close_price) + 1.0
            low = min(open_price, close_price) - 1.0
            rows.append({
                "timestamp": stamp,
                "open": open_price,
                "high": high,
                "low": low,
                "close": close_price,
                "source_file": "synthetic",
                "session_date": stamp.date(),
                "clock_time": stamp.time(),
            })
    return pd.DataFrame(rows)


def test_naive_timestamps_are_interpreted_as_ist_and_aware_are_converted():
    values = pd.Series(["2025-01-01 10:00:00", "2025-01-01T04:30:00Z"])
    parsed = _parse_timestamp_column(values)
    assert str(parsed.iloc[0].tz) == "Asia/Kolkata"
    assert parsed.iloc[0].hour == 10
    assert parsed.iloc[1].hour == 10
    assert parsed.iloc[0] == parsed.iloc[1]


def test_load_minute_files_deduplicates_identical_timestamps(tmp_path):
    path = tmp_path / "mini.csv"
    path.write_text(
        "Timestamp,Open,High,Low,Close\n"
        "2025-01-06 09:15:00,100,101,99,100.5\n"
        "2025-01-06 09:16:00,100.5,102,100,101.5\n"
        "2025-01-06 09:16:00,100.5,102,100,101.5\n",
        encoding="utf-8",
    )
    data, quality = load_minute_files([path])
    assert len(data) == 2
    assert quality["duplicate_timestamp_rows"] == 2
    assert quality["conflicting_duplicate_timestamp_groups"] == 0
    assert data["timestamp"].dt.tz is not None


def test_weekly_target_uses_anchor_open_and_last_close_bar():
    minutes = _synthetic_minutes()
    daily = daily_aggregates(minutes)
    cycles, calendar, report = construct_weekly_table(minutes, daily)
    row = cycles.loc[cycles["expiry_date"].eq(pd.Timestamp("2019-02-21"))].iloc[0]
    anchor = minutes.loc[
        minutes["timestamp"].eq(pd.Timestamp("2019-02-15 10:00:00", tz="Asia/Kolkata"))
    ].iloc[0]
    expiry_close = minutes.loc[
        minutes["timestamp"].eq(pd.Timestamp("2019-02-21 15:29:00", tz="Asia/Kolkata"))
    ].iloc[0]
    assert row["anchor_price"] == anchor["open"]
    assert row["anchor_price"] != anchor["close"]
    assert row["expiry_close"] == expiry_close["close"]
    assert row["label"] == "UP"
    assert bool(row["confirmatory_eligible"]) is False
    assert report["calendar_warning"]
    assert not calendar["calendar_verified"].any()


def test_target_return_sign_is_close_over_anchor_minus_one():
    minutes = _synthetic_minutes()
    daily = daily_aggregates(minutes)
    cycles, _, _ = construct_weekly_table(minutes, daily)
    row = cycles.loc[cycles["expiry_date"].eq(pd.Timestamp("2019-02-21"))].iloc[0]
    expected = row["expiry_close"] / row["anchor_price"] - 1.0
    assert abs(row["return_pct"] - expected) < 1e-12
    assert (row["label"] == "UP") == (expected > 0)
    assert (row["label"] == "DOWN") == (expected < 0)


def test_daily_aggregates_counts_equal_close_run_without_off_by_one():
    stamps = pd.date_range("2025-01-06 09:15:00", periods=3, freq="min", tz="Asia/Kolkata")
    frame = pd.DataFrame({
        "timestamp": stamps,
        "open": [100.0, 100.0, 100.0],
        "high": [101.0, 101.0, 101.0],
        "low": [99.0, 99.0, 99.0],
        "close": [100.0, 100.0, 100.0],
        "session_date": [stamp.date() for stamp in stamps],
        "source_file": ["synthetic"] * 3,
    })
    daily = daily_aggregates(frame)
    assert int(daily.iloc[0]["max_unchanged_close_run"]) == 3
