from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from research_core import FEATURE_COLUMNS  # noqa: E402
from build_pages_forecasts import build_walk_forward_forecasts  # noqa: E402


def _cycles(n: int = 36) -> pd.DataFrame:
    rows = []
    first_expiry = pd.Timestamp("2020-01-02")
    for i in range(n):
        expiry = first_expiry + pd.Timedelta(days=7 * i)
        row = {
            "expiry_date": expiry,
            "anchor_date": expiry - pd.Timedelta(days=6),
            "label": "UP" if i % 2 else "DOWN",
            "return_pct": 0.01 if i % 2 else -0.01,
        }
        for j, column in enumerate(FEATURE_COLUMNS):
            row[column] = ((i + 3) * (j + 5) % 37) / 37.0
        rows.append(row)
    return pd.DataFrame(rows)


def test_walk_forward_only_uses_rows_before_target_anchor() -> None:
    cycles = _cycles()
    first_holdout_expiry = pd.Timestamp(cycles.iloc[30]["expiry_date"])
    predictions = build_walk_forward_forecasts(
        cycles,
        holdout_start=first_holdout_expiry,
        minimum_history=30,
    )
    assert len(predictions) == 6
    first = predictions[0]
    assert first["target_expiry_date"] == first_holdout_expiry.date().isoformat()
    assert first["training_rows"] == 30
    assert first["trained_through_expiry_date"] < first["as_of_date"]
    assert first["direction"] in {"UP", "DOWN"}
    assert 0.0 <= first["p_up"] <= 1.0


def test_current_target_label_does_not_change_its_prediction() -> None:
    cycles = _cycles()
    first_holdout_expiry = pd.Timestamp(cycles.iloc[30]["expiry_date"])
    baseline = build_walk_forward_forecasts(
        cycles,
        holdout_start=first_holdout_expiry,
        minimum_history=30,
    )[0]

    changed = cycles.copy()
    changed.loc[30, "label"] = "UP" if changed.loc[30, "label"] == "DOWN" else "DOWN"
    changed_prediction = build_walk_forward_forecasts(
        changed,
        holdout_start=first_holdout_expiry,
        minimum_history=30,
    )[0]

    assert changed_prediction["direction"] == baseline["direction"]
    assert changed_prediction["p_up"] == baseline["p_up"]


def test_historical_predictions_begin_at_requested_locked_boundary() -> None:
    cycles = _cycles()
    boundary = pd.Timestamp(cycles.iloc[32]["expiry_date"])
    predictions = build_walk_forward_forecasts(
        cycles,
        holdout_start=boundary,
        minimum_history=30,
    )
    assert predictions
    assert predictions[0]["target_expiry_date"] == boundary.date().isoformat()
    assert all(p["prediction_kind"] == "LOCKED_CHRONOLOGICAL_HOLDOUT" for p in predictions)
