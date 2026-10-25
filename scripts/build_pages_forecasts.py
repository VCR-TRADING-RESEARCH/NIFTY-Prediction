#!/usr/bin/env python3
"""Build leakage-aware ExtraTrees prediction records for the static GitHub Pages UI.

Historical records start at the locked 2025-04-09 holdout expiry. Each row is
re-created walk-forward using only labels whose expiry dates precede the target
anchor. The latest forecast is trained only on completed historical cycles and
uses the next eligible 10:00 IST anchor after the most recent verified expiry.
"""
from __future__ import annotations

import json
import math
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys_path = str(ROOT / "scripts")
import sys
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

from research_core import (  # noqa: E402
    FEATURE_COLUMNS,
    EXPIRY_REGIME_CHANGE,
    IST,
    _calculate_features,
    _day_minutes,
    _first_anchor,
    _make_model,
    _prob_up,
)

# This is the beginning of the registered final chronological holdout. Keep it
# fixed: do not move the boundary as new weekly observations arrive.
LOCKED_HOLDOUT_START = pd.Timestamp("2025-04-09")

# Official NSE 2026 trading holidays relevant to future Tuesday expiry shifts.
# Source: NSE circular FAOP71777, 12-Dec-2025. These dates are used only to
# identify known holiday shifts; future contract dates remain unverified until
# the official expiry source confirms them.
NSE_HOLIDAYS_2026 = {
    "2026-01-15", "2026-01-26", "2026-03-03", "2026-03-26",
    "2026-03-31", "2026-04-03", "2026-04-14", "2026-05-01",
    "2026-05-28", "2026-06-26", "2026-09-14", "2026-10-02",
    "2026-10-20", "2026-11-10", "2026-11-24", "2026-12-25",
}


def _date_string(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    return pd.Timestamp(value).date().isoformat()


def _as_naive_dates(series: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(series, errors="coerce")
    if getattr(parsed.dt, "tz", None) is not None:
        parsed = parsed.dt.tz_convert(IST).dt.tz_localize(None)
    return parsed.dt.normalize()


def _binary_feature_data(cycles: pd.DataFrame) -> pd.DataFrame:
    data = cycles.copy()
    data["expiry_date"] = _as_naive_dates(data["expiry_date"])
    data["anchor_date"] = _as_naive_dates(data["anchor_date"])
    data["target"] = data["label"].map({"DOWN": 0, "UP": 1, "FLAT": np.nan})
    data = data.loc[data["target"].notna()].copy()
    data["target"] = data["target"].astype(int)
    complete = data[FEATURE_COLUMNS].notna().sum(axis=1) >= len(FEATURE_COLUMNS) - 2
    return data.loc[complete].sort_values("expiry_date").reset_index(drop=True)


def _predict_probability(train: pd.DataFrame, test_x: pd.DataFrame) -> float:
    if train.empty:
        raise ValueError("No historical labelled rows are available for training.")
    model = _make_model("extra_trees")
    model.fit(train[FEATURE_COLUMNS], train["target"].astype(int).to_numpy())
    return float(_prob_up(model, test_x[FEATURE_COLUMNS]))


def build_walk_forward_forecasts(
    cycles: pd.DataFrame,
    holdout_start: pd.Timestamp = LOCKED_HOLDOUT_START,
    minimum_history: int = 104,
) -> list[dict[str, Any]]:
    """Recreate point-in-time ExtraTrees forecasts for the locked holdout."""
    data = _binary_feature_data(cycles)
    start = pd.Timestamp(holdout_start).normalize()
    rows: list[dict[str, Any]] = []
    candidates = data.loc[data["expiry_date"].ge(start)].copy()
    for _, target_row in candidates.iterrows():
        target_date = pd.Timestamp(target_row["expiry_date"])
        anchor_date = pd.Timestamp(target_row["anchor_date"])
        train = data.loc[data["expiry_date"].lt(target_date)].copy()
        if len(train) < minimum_history:
            continue
        # A target label is not known at the anchor. Enforce the exact temporal
        # condition even if an upstream calendar/source row is malformed.
        if train["expiry_date"].max() >= anchor_date:
            continue
        test_x = pd.DataFrame([{name: target_row.get(name, np.nan) for name in FEATURE_COLUMNS}])
        p_up = _predict_probability(train, test_x)
        rows.append({
            "as_of_date": anchor_date.date().isoformat(),
            "as_of_time_ist": "10:00-or-first-valid-bar-by-10:03",
            "target_expiry_date": target_date.date().isoformat(),
            "direction": "UP" if p_up >= 0.5 else "DOWN",
            "p_up": p_up,
            "training_rows": int(len(train)),
            "trained_through_expiry_date": _date_string(train["expiry_date"].max()),
            "prediction_kind": "LOCKED_CHRONOLOGICAL_HOLDOUT",
            "source_gate": "BLOCKED",
        })
    return rows


def _next_weekly_nominal(last_nominal: pd.Timestamp) -> pd.Timestamp:
    """Advance the official/inferred weekly schedule by one seven-day interval."""
    return pd.Timestamp(last_nominal).normalize() + pd.Timedelta(days=7)


def _known_holiday_adjustment(nominal: pd.Timestamp) -> tuple[pd.Timestamp, str]:
    candidate = pd.Timestamp(nominal).normalize()
    if candidate.date().isoformat() not in NSE_HOLIDAYS_2026:
        return candidate, "PROVISIONAL_NEXT_WEEKLY_DATE"
    shifted = candidate - pd.Timedelta(days=1)
    while shifted.weekday() >= 5 or shifted.date().isoformat() in NSE_HOLIDAYS_2026:
        shifted -= pd.Timedelta(days=1)
    return shifted, "KNOWN_HOLIDAY_SHIFT_FROM_NSE_2026_CALENDAR"


def _source_gate(daily: pd.DataFrame) -> dict[str, Any]:
    if not {"session_close_archive", "official_close"}.issubset(daily.columns):
        return {
            "status": "BLOCKED",
            "anchor_status": "PROVISIONAL",
            "detail": "Cannot independently reconcile the preserved archive close in this run.",
        }
    archive = pd.to_numeric(daily["session_close_archive"], errors="coerce")
    official = pd.to_numeric(daily["official_close"], errors="coerce")
    valid = archive.notna() & official.notna()
    diff = (archive[valid] - official[valid]).abs()
    mismatches = int((diff > 1.0).sum())
    return {
        "status": "PASS" if len(diff) > 0 and mismatches == 0 else "BLOCKED",
        "anchor_status": "PROVISIONAL",
        "sessions_compared": int(len(diff)),
        "close_mismatches_over_1_point": mismatches,
        "median_absolute_difference_points": float(diff.median()) if len(diff) else None,
        "p95_absolute_difference_points": float(diff.quantile(0.95)) if len(diff) else None,
        "max_absolute_difference_points": float(diff.max()) if len(diff) else None,
        "detail": (
            "The 10:00 anchor is still sourced from the public minute archive and is not independently validated."
        ),
    }


def build_latest_forecast(
    cycles: pd.DataFrame,
    minutes: pd.DataFrame,
    daily: pd.DataFrame,
    calendar: pd.DataFrame,
) -> tuple[dict[str, Any] | None, str | None]:
    """Build a forecast for the next scheduled expiry without using future labels."""
    if calendar.empty or cycles.empty:
        return None, "The verified expiry calendar or labelled cycles are empty."
    verified = calendar.copy()
    if "calendar_verified" not in verified.columns:
        return None, "The expiry calendar does not mark official verification."
    verified = verified.loc[verified["calendar_verified"].astype(bool)].copy()
    verified["resolved_expiry"] = _as_naive_dates(verified["resolved_expiry"])
    verified["nominal_expiry"] = _as_naive_dates(verified["nominal_expiry"])
    verified = verified.dropna(subset=["resolved_expiry", "nominal_expiry"])
    if verified.empty:
        return None, "No officially verified historical expiry was available."

    last_event = verified.sort_values("resolved_expiry").iloc[-1]
    previous_expiry = pd.Timestamp(last_event["resolved_expiry"]).normalize()
    previous_nominal = pd.Timestamp(last_event["nominal_expiry"]).normalize()
    last_cycle_data = cycles.copy()
    last_cycle_data["expiry_date_normalized"] = _as_naive_dates(last_cycle_data["expiry_date"])
    matching = last_cycle_data.loc[last_cycle_data["expiry_date_normalized"].eq(previous_expiry)]
    if matching.empty:
        return None, "The latest verified expiry has no corresponding completed target row."
    previous_cycle = matching.sort_values("expiry_date_normalized").iloc[-1]

    session_dates = _as_naive_dates(daily["session_date"]).dropna().drop_duplicates().sort_values()
    anchors = session_dates.loc[session_dates.gt(previous_expiry)]
    if anchors.empty:
        return None, "No post-expiry trading session is available for the 10:00 anchor."
    anchor_date = pd.Timestamp(anchors.iloc[0]).normalize()
    anchor_day = _day_minutes(minutes, anchor_date)
    anchor_bar = _first_anchor(anchor_day)
    if anchor_bar is None:
        return None, (
            "The first trading session after the latest verified expiry has no valid 10:00–10:03 minute bar. "
            "Refusing to substitute a later session."
        )

    target_nominal = _next_weekly_nominal(previous_nominal)
    target_expiry, target_calendar_status = _known_holiday_adjustment(target_nominal)
    local_today = pd.Timestamp.now(tz=IST).date()
    if target_expiry.date() <= local_today:
        return None, (
            "The next nominal expiry derived from the latest verified calendar has already passed. "
            "Refresh the official expiry/calendar data before issuing another current forecast."
        )
    # Only completed target labels available by the anchor can be used for fitting.
    data = _binary_feature_data(cycles)
    train = data.loc[
        data["expiry_date"].le(previous_expiry)
        & data["expiry_date"].lt(anchor_date)
    ].copy()
    if len(train) < 104:
        return None, f"Only {len(train)} eligible completed training rows; at least 104 are required."
    if train["expiry_date"].max() >= anchor_date:
        return None, "Training includes a label that was not settled before the forecast anchor."

    anchor_price = float(anchor_bar["open"])
    if not np.isfinite(anchor_price) or anchor_price <= 0:
        return None, "The 10:00 anchor price is missing or invalid."
    anchor_row = pd.Series({
        "anchor_price": anchor_price,
        "anchor_timestamp": anchor_bar["timestamp"],
    })
    prior_return = float(previous_cycle["return_pct"])
    prior_label = str(previous_cycle["label"])
    features = _calculate_features(
        daily=daily,
        minutes=minutes,
        anchor_date=anchor_date,
        anchor_row=anchor_row,
        previous_cycle_return=prior_return,
        previous_cycle_label=prior_label,
        previous_expiry=previous_expiry,
    )
    test_x = pd.DataFrame([{name: features.get(name, np.nan) for name in FEATURE_COLUMNS}])
    if test_x[FEATURE_COLUMNS].notna().sum(axis=1).iloc[0] < len(FEATURE_COLUMNS) - 2:
        return None, "The candidate forecast row has too many missing features."
    p_up = _predict_probability(train, test_x)
    trained_through = _date_string(train["expiry_date"].max())
    return {
        "as_of_date": anchor_date.date().isoformat(),
        "as_of_time_ist": pd.Timestamp(anchor_bar["timestamp"]).strftime("%H:%M"),
        "target_expiry_date": target_expiry.date().isoformat(),
        "target_nominal_date": target_nominal.date().isoformat(),
        "target_calendar_status": target_calendar_status,
        "direction": "UP" if p_up >= 0.5 else "DOWN",
        "p_up": p_up,
        "training_rows": int(len(train)),
        "trained_through_expiry_date": trained_through,
        "prediction_kind": "LATEST_FORWARD_FORECAST",
        "source_gate": "BLOCKED",
        "anchor_price": anchor_price,
        "anchor_source": "public minute archive; independently unverified",
    }, None


def build_forecast_payload(
    cycles: pd.DataFrame,
    minutes: pd.DataFrame,
    daily: pd.DataFrame,
    calendar: pd.DataFrame,
) -> dict[str, Any]:
    historical = build_walk_forward_forecasts(cycles)
    try:
        latest, latest_error = build_latest_forecast(cycles, minutes, daily, calendar)
    except Exception as exc:  # keep historical results visible if the live row cannot be built
        latest = None
        latest_error = type(exc).__name__ + ": " + str(exc)[:240]
    source_gate = _source_gate(daily)
    latest_generated_utc = datetime.now(timezone.utc).isoformat()
    return {
        "schema_version": 1,
        "generated_at_utc": latest_generated_utc,
        "timezone": "Asia/Kolkata",
        "model": {
            "name": "ExtraTreesClassifier",
            "implementation": "scikit-learn",
            "n_estimators": 300,
            "max_depth": 3,
            "min_samples_leaf": 8,
            "max_features": 0.8,
            "class_weight": "balanced",
            "random_state": 42,
            "feature_columns": FEATURE_COLUMNS,
        },
        "validation": {
            "locked_holdout_start_expiry": LOCKED_HOLDOUT_START.date().isoformat(),
            "historical_records": len(historical),
            "holdout_accuracy_reported": 0.6125,
            "holdout_observations": 80,
            "holdout_accuracy_wilson_95": [0.5029365721, 0.7117543487],
            "status": "EXPLORATORY_ONLY",
            "note": (
                "The reported 61.25% is from the historical 80-row holdout. It is not a probability of profit "
                "and does not validate an options strategy."
            ),
        },
        "data_quality": source_gate,
        "historical_predictions": historical,
        "latest_forecast": latest,
        "latest_forecast_error": latest_error,
        "warnings": [
            "Source gate remains blocked until archive closes reconcile with official NSE closes.",
            "The 10:00 anchor is from a public minute archive and remains independently unverified.",
            "Expiry date for the live forecast is a candidate until confirmed against official contract history.",
            "This is a NIFTY spot direction classification, not an executable options trade or a P&L forecast.",
        ],
    }


def write_forecast_payload(
    cycles: pd.DataFrame,
    minutes: pd.DataFrame,
    daily: pd.DataFrame,
    calendar: pd.DataFrame,
    output_path: Path,
) -> dict[str, Any]:
    payload = build_forecast_payload(cycles, minutes, daily, calendar)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, default=str, allow_nan=False) + "\n", encoding="utf-8")
    return {
        "output_path": str(output_path.relative_to(ROOT)),
        "historical_prediction_records": len(payload["historical_predictions"]),
        "latest_forecast_generated": payload["latest_forecast"] is not None,
        "latest_forecast_error": payload["latest_forecast_error"],
        "data_quality_status": payload["data_quality"]["status"],
        "generated_at_utc": payload["generated_at_utc"],
    }
