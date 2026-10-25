#!/usr/bin/env python3
"""Generate leakage-safe historical as-of forecasts and the latest provisional expiry forecast.

This output is exploratory until the registered price-source and anchor gates pass.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, time, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/nifty50"
RECON = ROOT / "data/reconciliation"
OUT = ROOT / "docs/prediction"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "scripts"))

from research_core import (  # noqa: E402
    FEATURE_COLUMNS, _calculate_features, _make_model, _prob_up,
    apply_official_daily_closes, construct_weekly_table, daily_aggregates, load_minute_files,
)

MIN_TRAIN = 104
AS_OF_START = pd.Timestamp("2023-01-01")


def stamp(value) -> str:
    return pd.Timestamp(value).strftime("%Y-%m-%d")


def next_tuesday_after(value: pd.Timestamp) -> pd.Timestamp:
    value = pd.Timestamp(value).normalize()
    days = (1 - value.weekday()) % 7
    return value + pd.Timedelta(days=days or 7)


def valid_training(frame: pd.DataFrame, cutoff: pd.Timestamp) -> pd.DataFrame:
    result = frame.loc[pd.to_datetime(frame["expiry_date"]).dt.normalize() < cutoff].copy()
    result = result[result["label"].isin(["UP", "DOWN"])]
    return result.dropna(subset=FEATURE_COLUMNS)


def predict(train: pd.DataFrame, row: pd.Series) -> tuple[int, float, int]:
    train = train.dropna(subset=FEATURE_COLUMNS).copy()
    if len(train) < MIN_TRAIN or train["label"].nunique() < 2:
        raise ValueError(f"Insufficient causal training history: {len(train)} rows")
    model = _make_model("extra_trees")
    model.fit(train[FEATURE_COLUMNS], train["label"].map({"DOWN": 0, "UP": 1}).astype(int))
    x = pd.DataFrame([{c: row.get(c, np.nan) for c in FEATURE_COLUMNS}], columns=FEATURE_COLUMNS)
    p_up = _prob_up(model, x)
    return int(p_up >= 0.5), float(p_up), int(len(train))


def main() -> int:
    files = sorted(RAW.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No minute data under {RAW}")
    minutes, source_quality = load_minute_files(files)
    daily = daily_aggregates(minutes)
    official_path = RECON / "nifty50_official_daily.csv"
    expiry_path = RECON / "expiry_verification.csv"
    if not official_path.is_file() or not expiry_path.is_file():
        raise FileNotFoundError("Official daily close and expiry verification files are required")
    daily, close_quality = apply_official_daily_closes(daily, official_path)
    cycles, _, construction_quality = construct_weekly_table(minutes, daily, expiry_path)
    cycles["expiry_date"] = pd.to_datetime(cycles["expiry_date"]).dt.normalize()
    cycles["anchor_date"] = pd.to_datetime(cycles["anchor_date"]).dt.normalize()

    history = []
    for _, row in cycles.iterrows():
        asof = pd.Timestamp(row["anchor_date"]).normalize()
        if asof < AS_OF_START:
            continue
        try:
            pred, p_up, n_train = predict(valid_training(cycles, asof), row)
            history.append({
                "as_of_date": stamp(asof),
                "forecast_time_ist": f"{stamp(asof)} 10:00",
                "target_expiry_date": stamp(row["expiry_date"]),
                "prediction": "UP" if pred else "DOWN",
                "p_up": round(p_up, 6),
                "p_down": round(1 - p_up, 6),
                "training_rows": n_train,
                "mode": "historical_walk_forward",
                "status": "EXPLORATORY — source gate blocked",
            })
        except ValueError:
            continue

    verified = pd.read_csv(expiry_path)
    verified["verified_expiry_trade_date"] = pd.to_datetime(
        verified["verified_expiry_trade_date"], errors="coerce"
    ).dt.normalize()
    verified = verified.dropna(subset=["verified_expiry_trade_date"])
    prior_expiries = sorted(set(verified["verified_expiry_trade_date"]))
    if not prior_expiries:
        raise ValueError("No verified expiry dates are present")
    last_expiry = pd.Timestamp(prior_expiries[-1]).normalize()
    session_dates = pd.to_datetime(daily["session_date"]).dt.normalize()
    next_sessions = sorted(session_dates[session_dates > last_expiry].unique())
    if not next_sessions:
        raise ValueError("No observed session after the last verified expiry; cannot build a current as-of forecast")
    asof = pd.Timestamp(next_sessions[0]).normalize()
    anchor_day = minutes.loc[minutes["timestamp"].dt.date.eq(asof.date())].sort_values("timestamp")
    clock = anchor_day["timestamp"].dt.time
    anchor_candidates = anchor_day.loc[(clock >= time(10, 0)) & (clock <= time(10, 3))]
    if anchor_candidates.empty:
        raise ValueError(f"No valid 10:00–10:03 anchor bar for as-of date {stamp(asof)}")
    anchor = anchor_candidates.iloc[0]
    previous_rows = cycles.loc[cycles["expiry_date"] < asof].sort_values("expiry_date")
    if previous_rows.empty:
        raise ValueError("No completed expiry cycles available before the current as-of date")
    previous_cycle = previous_rows.iloc[-1]
    feature_row = pd.Series(_calculate_features(
        daily,
        minutes,
        asof,
        pd.Series({"anchor_price": float(anchor["open"]), "anchor_timestamp": anchor["timestamp"]}),
        float(previous_cycle["return_pct"]),
        str(previous_cycle["label"]),
        pd.Timestamp(previous_cycle["expiry_date"]),
    ))
    pred, p_up, n_train = predict(valid_training(cycles, asof), feature_row)
    target_expiry = next_tuesday_after(asof)
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "as_of_date": stamp(asof),
        "forecast_time_ist": f"{stamp(asof)} 10:00 IST",
        "reference_price": round(float(anchor["open"]), 2),
        "target_expiry_date": stamp(target_expiry),
        "target_expiry_status": "PROVISIONAL — next Tuesday estimate; holiday adjustment not independently verified",
        "prediction": "UP" if pred else "DOWN",
        "p_up": round(p_up, 6),
        "p_down": round(1 - p_up, 6),
        "training_rows": n_train,
        "model": "ExtraTreesClassifier",
        "model_parameters": "300 trees; max_depth=3; min_samples_leaf=8; max_features=0.8; class_weight=balanced; random_state=42",
        "historical_source_gate": "BLOCKED",
        "archive_close_mismatches_over_1_point": close_quality.get("archive_close_mismatches_over_1_point"),
        "official_sessions_compared": close_quality.get("official_sessions_matched"),
        "anchor_source": "Public minute archive; not independently validated",
        "prediction_status": "EXPLORATORY ONLY — NOT FOR LIVE TRADING",
        "limitations": [
            "Historical archive closes fail the registered independent close-agreement gate.",
            "The 10:00 anchor source is not independently validated.",
            "The upcoming expiry date is a weekday estimate, not a verified future contract record.",
            "Spot direction is not options P&L; contract quotes, spreads, fills and date-effective Paytm Money costs are not included."
        ],
    }
    (OUT / "latest_prediction.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    pd.DataFrame(history).to_csv(OUT / "prediction_history.csv", index=False)
    print(json.dumps({
        "latest_prediction": payload,
        "historical_predictions": len(history),
        "source_quality": source_quality,
        "construction_quality": construction_quality,
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
