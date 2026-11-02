from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.constituent_weekly.fetch_nifty50_weights import validate_weights_payload


def make_payload(row_values=(2.0,) * 49 + (2.0,)) -> bytes:
    columns = ["TICKER" + str(i) for i in range(50)]
    rows = []
    for date in ("2025-01-31", "2025-02-28"):
        rows.append([date, *row_values])
    frame = pd.DataFrame(rows, columns=["DATE", *columns])
    return frame.to_csv(index=False).encode("utf-8")


def test_weight_payload_accepts_50_columns_and_normalized_rows():
    stats = validate_weights_payload(make_payload())
    assert stats["rows"] == 2
    assert stats["ticker_columns"] == 50
    assert stats["first_date"] == "2025-01-31"
    assert stats["last_date"] == "2025-02-28"
    assert stats["max_abs_row_sum_deviation"] <= 1e-6
    assert len(stats["sha256"]) == 64


def test_weight_payload_rejects_non_100_row_sum():
    payload = make_payload((1.0,) * 50)
    with pytest.raises(ValueError, match="does not sum to 100"):
        validate_weights_payload(payload)


def test_weight_payload_rejects_duplicate_dates():
    columns = ["TICKER" + str(i) for i in range(50)]
    frame = pd.DataFrame(
        [["2025-01-31", *([2.0] * 50)], ["2025-01-31", *([2.0] * 50)]],
        columns=["DATE", *columns],
    )
    with pytest.raises(ValueError, match="unique and ascending"):
        validate_weights_payload(frame.to_csv(index=False).encode("utf-8"))


def test_weight_payload_rejects_missing_values():
    columns = ["TICKER" + str(i) for i in range(50)]
    frame = pd.DataFrame(
        [["2025-01-31", *([2.0] * 49), None]],
        columns=["DATE", *columns],
    )
    with pytest.raises(ValueError, match="missing or non-numeric"):
        validate_weights_payload(frame.to_csv(index=False).encode("utf-8"))


def test_weight_payload_rejects_non_finite_or_out_of_range_values():
    columns = ["TICKER" + str(i) for i in range(50)]
    for invalid in (float("inf"), -0.1, 100.1):
        frame = pd.DataFrame(
            [["2025-01-31", *([2.0] * 49), invalid]],
            columns=["DATE", *columns],
        )
        payload = frame.to_csv(index=False).encode("utf-8")
        with pytest.raises(ValueError, match="finite and in \\[0, 100\\]"):
            validate_weights_payload(payload)
