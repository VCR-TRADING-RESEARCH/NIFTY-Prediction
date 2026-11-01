from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.constituent_weekly.diagnose_shreecem_edge_volume import negative_volume_diagnostics


def epoch_ist(value: str) -> int:
    return int(datetime.fromisoformat(value).replace(tzinfo=ZoneInfo("Asia/Kolkata")).timestamp())


def test_negative_volume_diagnostic_reports_timestamp_without_values():
    times = [
        "2021-11-01T10:00:00",
        "2021-11-01T11:11:00",
        "2021-11-04T18:45:00",
        "2022-01-28T15:14:00",
    ]
    body = {
        "open": [100.0, 100.0, 100.0, 100.0],
        "high": [101.0, 101.0, 101.0, 101.0],
        "low": [99.0, 99.0, 99.0, 99.0],
        "close": [100.5, 100.5, 100.5, 100.5],
        "volume": [100, -7, -99, 250],
        "timestamp": [epoch_ist(value) for value in times],
    }
    result = negative_volume_diagnostics(body, "2021-11-01", "2022-01-29")
    assert result["status"] == "NEGATIVE_VOLUME_ROWS_FOUND"
    assert result["negative_volume_row_count"] == 1
    assert result["negative_volume_timestamps_ist"] == ["2021-11-01T11:11:00+05:30"]
    assert result["special_session_dates_excluded"] == ["2021-11-04"]
    assert result["contains_raw_price_or_volume_values"] is False
    assert "-7" not in str(result)
    assert "-99" not in str(result)


def test_negative_volume_diagnostic_rejects_mismatched_arrays():
    result = negative_volume_diagnostics(
        {"open": [1], "high": [1], "low": [1], "close": [1], "volume": [], "timestamp": [1]},
        "2021-11-01",
        "2022-01-29",
    )
    assert result["status"] == "EMPTY_OR_MISMATCHED_ARRAYS"
