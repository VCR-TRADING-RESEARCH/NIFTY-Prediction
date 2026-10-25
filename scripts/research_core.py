#!/usr/bin/env python3
"""Deterministic data construction, expiry-cycle labels, baselines and walk-forward tests."""
from __future__ import annotations

import json
import math
import re
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, brier_score_loss, confusion_matrix,
    f1_score, matthews_corrcoef, precision_score, recall_score, log_loss, roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

IST = "Asia/Kolkata"
FIRST_WEEKLY_EXPIRY = pd.Timestamp("2019-02-14")
EXPIRY_REGIME_CHANGE = pd.Timestamp("2025-09-01")
EXPECTED_CLOSE_START = time(15, 25)
EXPECTED_CLOSE_END = time(15, 29)
ANCHOR_START = time(10, 0)
ANCHOR_END = time(10, 3)

FEATURE_COLUMNS = [
    "ret_1", "ret_5", "ret_10", "ret_20",
    "rv_5", "rv_10", "rv_20",
    "range_5", "range_10", "range_20",
    "overnight_gap", "pre_anchor_return", "anchor_jump",
    "prior_cycle_return", "prior_cycle_up",
    "prior_close_range_position", "session_gap_days",
    "post_expiry_change", "month_sin", "month_cos",
]


def _jsonable(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()
    if pd.isna(value):
        return None
    return value


def _parse_timestamp_column(series: pd.Series) -> pd.Series:
    """Treat naive source timestamps as IST; convert offset-aware timestamps to IST."""
    raw = series.astype(str).str.strip()
    has_offset = raw.str.contains(r"(?:Z|[+-]\d{2}:?\d{2})$", regex=True, case=False)
    output = pd.Series(pd.NaT, index=series.index, dtype=f"datetime64[ns, {IST}]")
    if (~has_offset).any():
        naive = pd.to_datetime(raw.loc[~has_offset], errors="coerce")
        if getattr(naive.dt, "tz", None) is not None:
            naive = naive.dt.tz_convert(IST).dt.tz_localize(None)
        localized = naive.dt.tz_localize(IST, ambiguous="NaT", nonexistent="NaT")
        output.loc[~has_offset] = localized
    if has_offset.any():
        aware = pd.to_datetime(raw.loc[has_offset], errors="coerce", utc=True)
        output.loc[has_offset] = aware.dt.tz_convert(IST)
    return output


def load_minute_files(files: Iterable[Path]) -> tuple[pd.DataFrame, dict[str, Any]]:
    frames: list[pd.DataFrame] = []
    source_count = 0
    row_count_before = 0
    for path in sorted(Path(p) for p in files):
        if not path.is_file() or path.stat().st_size == 0:
            continue
        frame = pd.read_csv(path, low_memory=False)
        source_count += 1
        row_count_before += len(frame)
        canonical = {str(c).strip().lower(): c for c in frame.columns}
        ts_name = canonical.get("timestamp") or canonical.get("datetime") or canonical.get("date_time")
        if ts_name is None:
            raise ValueError("No Timestamp/Datetime column in " + path.name)
        renames = {}
        for target in ("open", "high", "low", "close", "volume", "epoch"):
            if target in canonical:
                renames[canonical[target]] = target
        frame = frame.rename(columns=renames)
        if not all(k in frame.columns for k in ("open", "high", "low", "close")):
            raise ValueError("Missing one or more OHLC columns in " + path.name)
        frame["timestamp"] = _parse_timestamp_column(frame[ts_name])
        frame["source_file"] = path.name
        for col in ("open", "high", "low", "close"):
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
        frames.append(frame[["timestamp", "open", "high", "low", "close", "source_file"]])
    if not frames:
        raise FileNotFoundError("No readable CSV market data files were found.")
    data = pd.concat(frames, ignore_index=True)
    unparsed = int(data["timestamp"].isna().sum())
    data = data.dropna(subset=["timestamp"])
    data = data.sort_values(["timestamp", "source_file"], kind="stable").reset_index(drop=True)

    duplicate_mask = data.duplicated(subset=["timestamp"], keep=False)
    duplicate_rows = int(duplicate_mask.sum())
    conflicting_duplicate_groups = 0
    if duplicate_mask.any():
        for _, group in data.loc[duplicate_mask].groupby("timestamp", sort=False):
            if group[["open", "high", "low", "close"]].drop_duplicates().shape[0] > 1:
                conflicting_duplicate_groups += 1
    data = data.drop_duplicates(subset=["timestamp"], keep="last").copy()

    valid = (
        data[["open", "high", "low", "close"]].notna().all(axis=1)
        & (data[["open", "high", "low", "close"]] > 0).all(axis=1)
        & (data["low"] <= data[["open", "close"]].min(axis=1))
        & (data["high"] >= data[["open", "close"]].max(axis=1))
        & (data["high"] >= data["low"])
    )
    invalid_rows = int((~valid).sum())
    data = data.loc[valid].copy()
    data = data.sort_values("timestamp").reset_index(drop=True)
    local_time = data["timestamp"].dt.time
    data["session_date"] = data["timestamp"].dt.date
    data["clock_time"] = local_time
    data = data[
        (data["timestamp"].dt.dayofweek < 5)
        & (data["clock_time"] >= time(9, 15))
        & (data["clock_time"] <= time(15, 29))
    ].copy()
    quality = {
        "source_files_read": source_count,
        "raw_rows_before_deduplication": int(row_count_before),
        "unparsed_timestamps": unparsed,
        "duplicate_timestamp_rows": duplicate_rows,
        "conflicting_duplicate_timestamp_groups": conflicting_duplicate_groups,
        "invalid_ohlc_rows_removed": invalid_rows,
        "valid_in_session_rows": int(len(data)),
        "first_timestamp": data["timestamp"].min().isoformat() if len(data) else None,
        "last_timestamp": data["timestamp"].max().isoformat() if len(data) else None,
        "timezone": IST,
        "timestamp_assumption": "Naive source timestamps are interpreted as IST; offset-aware values converted to IST.",
        "source_archive": "technovusin/nifty50-historical-data",
    }
    return data, quality


def daily_aggregates(minutes: pd.DataFrame) -> pd.DataFrame:
    if minutes.empty:
        raise ValueError("No market bars after validation.")
    ordered = minutes.sort_values("timestamp").copy()
    result = ordered.groupby("session_date", sort=True).agg(
        session_open=("open", "first"),
        session_high=("high", "max"),
        session_low=("low", "min"),
        session_close=("close", "last"),
        first_bar=("timestamp", "first"),
        last_bar=("timestamp", "last"),
        bars=("timestamp", "size"),
    ).reset_index()
    result["session_date"] = pd.to_datetime(result["session_date"])
    result["max_unchanged_close_run"] = 1
    result["unchanged_close_fraction"] = 0.0
    for session_date, indices in ordered.groupby("session_date", sort=True).groups.items():
        group = ordered.loc[indices].sort_values("timestamp")
        unchanged = group["close"].eq(group["close"].shift()).fillna(False)
        run_ids = group["close"].ne(group["close"].shift()).cumsum()
        run_lengths = group.groupby(run_ids)["close"].transform("size")
        max_run = int(run_lengths.max()) if len(run_lengths) else 0
        same_fraction = float(unchanged.mean()) if len(group) else 0.0
        mask = result["session_date"].eq(pd.Timestamp(session_date))
        result.loc[mask, "max_unchanged_close_run"] = max_run
        result.loc[mask, "unchanged_close_fraction"] = same_fraction
    result["session_return"] = result["session_close"].pct_change()
    result["range_pct"] = (result["session_high"] - result["session_low"]) / result["session_close"].shift(1)
    return result.sort_values("session_date").reset_index(drop=True)


def build_expiry_candidates(daily: pd.DataFrame) -> pd.DataFrame:
    """Build a discovery calendar, explicitly marked heuristic until official dates are supplied."""
    sessions = daily["session_date"].sort_values().drop_duplicates().reset_index(drop=True)
    if sessions.empty:
        return pd.DataFrame(columns=["nominal_expiry", "resolved_expiry", "calendar_status"])
    last = sessions.max()
    nominal_dates = pd.date_range(FIRST_WEEKLY_EXPIRY, last, freq="D")
    session_set = set(sessions.tolist())
    rows: list[dict[str, Any]] = []
    for nominal in nominal_dates:
        weekday = 3 if nominal < EXPIRY_REGIME_CHANGE else 1  # Thu -> Tue expiry change
        if nominal.weekday() != weekday:
            continue
        if nominal in session_set:
            resolved = nominal
            status = "weekday_heuristic_nominal"
        else:
            earlier = sessions[(sessions < nominal) & (sessions >= nominal - pd.Timedelta(days=4))]
            if len(earlier):
                resolved = earlier.iloc[-1]
                status = "shift_inferred_from_missing_session"
            else:
                resolved = pd.NaT
                status = "unresolved_missing_session"
        n_bars = None
        if pd.notna(resolved):
            match = daily.loc[daily["session_date"].eq(pd.Timestamp(resolved)), "bars"]
            n_bars = int(match.iloc[0]) if len(match) else None
        if n_bars is not None and n_bars < 250:
            status = "uncertain_low_coverage"
        rows.append({
            "nominal_expiry": nominal,
            "resolved_expiry": resolved,
            "calendar_status": status,
            "candidate_bars": n_bars,
            "calendar_verified": False,
        })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["nominal_expiry"] = pd.to_datetime(out["nominal_expiry"])
    out["resolved_expiry"] = pd.to_datetime(out["resolved_expiry"])
    return out


def _first_anchor(minute_day: pd.DataFrame) -> pd.Series | None:
    day = minute_day.sort_values("timestamp").copy()
    clock = day["timestamp"].dt.time
    valid = day[(clock >= ANCHOR_START) & (clock <= ANCHOR_END)]
    if valid.empty:
        return None
    return valid.iloc[0]


def _expiry_close(minute_day: pd.DataFrame) -> pd.Series | None:
    day = minute_day.sort_values("timestamp").copy()
    clock = day["timestamp"].dt.time
    valid = day[(clock >= EXPECTED_CLOSE_START) & (clock <= EXPECTED_CLOSE_END)]
    if valid.empty:
        return None
    return valid.iloc[-1]


def _day_minutes(minutes: pd.DataFrame, target: pd.Timestamp) -> pd.DataFrame:
    target_date = target.date()
    return minutes.loc[minutes["session_date"].eq(target_date)].copy()


def _calculate_features(
    daily: pd.DataFrame,
    minutes: pd.DataFrame,
    anchor_date: pd.Timestamp,
    anchor_row: pd.Series,
    previous_cycle_return: float | None,
    previous_cycle_label: str | None,
    previous_expiry: pd.Timestamp,
) -> dict[str, Any]:
    prior = daily.loc[daily["session_date"] < anchor_date].sort_values("session_date")
    prior = prior.tail(80)
    values: dict[str, Any] = {}
    close = prior["session_close"].astype(float).reset_index(drop=True)
    returns = close.pct_change().dropna()
    for n in (1, 5, 10, 20):
        values[f"ret_{n}"] = float(close.iloc[-1] / close.iloc[-1 - n] - 1) if len(close) > n else np.nan
    for n in (5, 10, 20):
        values[f"rv_{n}"] = float(returns.tail(n).std(ddof=1)) if len(returns.tail(n)) >= max(3, n // 2) else np.nan
        lows = prior["session_low"].tail(n)
        highs = prior["session_high"].tail(n)
        prev_close = close.iloc[-1] if len(close) else np.nan
        values[f"range_{n}"] = float((highs.max() - lows.min()) / prev_close) if len(lows) and prev_close > 0 else np.nan
    prev_close = float(prior["session_close"].iloc[-1]) if len(prior) else np.nan
    anchor_price = float(anchor_row["anchor_price"])
    values["overnight_gap"] = anchor_price / prev_close - 1 if np.isfinite(prev_close) and prev_close > 0 else np.nan
    today_minutes = _day_minutes(minutes, anchor_date)
    anchor_timestamp = pd.Timestamp(anchor_row["anchor_timestamp"])
    time_of_anchor = anchor_timestamp.time()
    past_bars = today_minutes.loc[today_minutes["timestamp"].lt(anchor_timestamp)].sort_values("timestamp")
    prior_bar = past_bars.iloc[-1] if len(past_bars) else None
    first_bar = today_minutes.sort_values("timestamp").iloc[0] if len(today_minutes) else None
    values["pre_anchor_return"] = anchor_price / float(first_bar["open"]) - 1 if first_bar is not None and float(first_bar["open"]) > 0 else np.nan
    values["anchor_jump"] = anchor_price / float(prior_bar["close"]) - 1 if prior_bar is not None and float(prior_bar["close"]) > 0 else np.nan
    values["prior_cycle_return"] = float(previous_cycle_return) if previous_cycle_return is not None and np.isfinite(previous_cycle_return) else np.nan
    values["prior_cycle_up"] = 1.0 if previous_cycle_label == "UP" else (0.0 if previous_cycle_label == "DOWN" else np.nan)
    nrange = prior.tail(20)
    if len(nrange) and nrange["session_high"].max() > nrange["session_low"].min():
        values["prior_close_range_position"] = float(
            (prev_close - nrange["session_low"].min()) / (nrange["session_high"].max() - nrange["session_low"].min())
        )
    else:
        values["prior_close_range_position"] = np.nan
    values["session_gap_days"] = int((anchor_date - previous_expiry).days)
    values["post_expiry_change"] = 1.0 if anchor_date >= EXPIRY_REGIME_CHANGE else 0.0
    month_angle = 2.0 * math.pi * (anchor_date.month - 1) / 12.0
    values["month_sin"] = math.sin(month_angle)
    values["month_cos"] = math.cos(month_angle)
    return values


def construct_weekly_table(minutes: pd.DataFrame, daily: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    calendar = build_expiry_candidates(daily)
    if calendar.empty or len(calendar) < 2:
        raise ValueError("Insufficient candidate expiry dates to construct weekly cycles.")
    grouped = {pd.Timestamp(d): g for d, g in minutes.groupby(minutes["timestamp"].dt.normalize(), sort=True)}
    # Group keys are midnight timestamps in IST.
    cycle_rows: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    seen_resolved: set[pd.Timestamp] = set()
    for i in range(1, len(calendar)):
        previous_event = calendar.iloc[i - 1]
        current_event = calendar.iloc[i]
        prev_expiry = previous_event["resolved_expiry"]
        expiry = current_event["resolved_expiry"]
        nominal_prev = previous_event["nominal_expiry"]
        nominal_expiry = current_event["nominal_expiry"]
        if pd.isna(prev_expiry) or pd.isna(expiry):
            exclusions.append({"nominal_expiry": nominal_expiry, "reason": "unresolved_expiry_calendar"})
            continue
        prev_expiry = pd.Timestamp(prev_expiry)
        expiry = pd.Timestamp(expiry)
        if expiry in seen_resolved:
            exclusions.append({"nominal_expiry": nominal_expiry, "reason": "duplicate_resolved_expiry"})
            continue
        seen_resolved.add(expiry)
        spacing = (expiry - prev_expiry).days
        if spacing < 4 or spacing > 9:
            exclusions.append({"nominal_expiry": nominal_expiry, "reason": "unexpected_expiry_spacing_" + str(spacing)})
            continue
        anchor_candidates = daily.loc[daily["session_date"] > prev_expiry, "session_date"].sort_values()
        if anchor_candidates.empty:
            exclusions.append({"nominal_expiry": nominal_expiry, "reason": "no_anchor_session"})
            continue
        anchor_date = pd.Timestamp(anchor_candidates.iloc[0])
        if (anchor_date - prev_expiry).days > 4:
            exclusions.append({"nominal_expiry": nominal_expiry, "reason": "anchor_session_gap_too_large"})
            continue
        anchor_day = _day_minutes(minutes, anchor_date)
        expiry_day = _day_minutes(minutes, expiry)
        arow = _first_anchor(anchor_day)
        crow = _expiry_close(expiry_day)
        if arow is None:
            exclusions.append({"nominal_expiry": nominal_expiry, "reason": "missing_1000_anchor_bar"})
            continue
        if crow is None:
            exclusions.append({"nominal_expiry": nominal_expiry, "reason": "missing_expiry_close_bar"})
            continue
        daily_anchor = daily.loc[daily["session_date"].eq(anchor_date)]
        daily_expiry = daily.loc[daily["session_date"].eq(expiry)]
        if daily_anchor.empty or daily_expiry.empty or int(daily_anchor["bars"].iloc[0]) < 250 or int(daily_expiry["bars"].iloc[0]) < 250:
            exclusions.append({"nominal_expiry": nominal_expiry, "reason": "low_session_coverage"})
            continue
        anchor_price = float(arow["open"])
        closing_price = float(crow["close"])
        if not np.isfinite(anchor_price) or anchor_price <= 0 or not np.isfinite(closing_price) or closing_price <= 0:
            exclusions.append({"nominal_expiry": nominal_expiry, "reason": "invalid_anchor_or_close_price"})
            continue
        ret = closing_price / anchor_price - 1.0
        label = "UP" if ret > 0 else ("DOWN" if ret < 0 else "FLAT")
        p_status = str(previous_event["calendar_status"])
        c_status = str(current_event["calendar_status"])
        calendar_status = "weekday_heuristic_nominal"
        if p_status != "weekday_heuristic_nominal" or c_status != "weekday_heuristic_nominal":
            calendar_status = "shift_or_data_gap_inferred"
        if p_status == "uncertain_low_coverage" or c_status == "uncertain_low_coverage":
            calendar_status = "uncertain_low_coverage"
        cycle_rows.append({
            "previous_nominal_expiry": pd.Timestamp(nominal_prev),
            "nominal_expiry": pd.Timestamp(nominal_expiry),
            "previous_expiry": prev_expiry,
            "expiry_date": expiry,
            "anchor_date": anchor_date,
            "anchor_timestamp": pd.Timestamp(arow["timestamp"]),
            "anchor_price": anchor_price,
            "expiry_close_timestamp": pd.Timestamp(crow["timestamp"]),
            "expiry_close": closing_price,
            "return_pct": ret,
            "label": label,
            "previous_calendar_status": p_status,
            "calendar_status": calendar_status,
            "source_quality_status": "validated_ohlc_not_independently_verified",
            "confirmatory_eligible": False,
            "anchor_bar_delay_minutes": int((pd.Timestamp(arow["timestamp"]) - anchor_date.tz_localize(IST) - pd.Timedelta(hours=10)).total_seconds() // 60),
            "anchor_session_bars": int(daily_anchor["bars"].iloc[0]),
            "expiry_session_bars": int(daily_expiry["bars"].iloc[0]),
            "expiry_max_unchanged_close_run": int(daily_expiry["max_unchanged_close_run"].iloc[0]),
        })
    if not cycle_rows:
        raise ValueError("No weekly cycles passed basic target-data checks. Inspect candidate calendar and data-quality outputs.")
    cycles = pd.DataFrame(cycle_rows).sort_values("expiry_date").reset_index(drop=True)
    # Features may use earlier cycle outcomes only. Current expiry outcome never enters current features.
    features: list[dict[str, Any]] = []
    previous_returns: list[float | None] = []
    previous_labels: list[str | None] = []
    for idx, row in cycles.iterrows():
        linked_previous = idx > 0 and pd.Timestamp(cycles.iloc[idx - 1]["expiry_date"]) == pd.Timestamp(row["previous_expiry"])
        prev_return = cycles.iloc[idx - 1]["return_pct"] if linked_previous else None
        prev_label = cycles.iloc[idx - 1]["label"] if linked_previous else None
        previous_returns.append(float(prev_return) if prev_return is not None else None)
        previous_labels.append(str(prev_label) if prev_label is not None else None)
        feat = _calculate_features(
            daily, minutes, pd.Timestamp(row["anchor_date"]), row,
            previous_returns[-1], previous_labels[-1], pd.Timestamp(row["previous_expiry"])
        )
        features.append(feat)
    feature_frame = pd.DataFrame(features)
    cycles = pd.concat([cycles.reset_index(drop=True), feature_frame.reset_index(drop=True)], axis=1)
    # Calendar-derived rows are exploratory until a canonical exchange expiry schedule is attached and verified.
    quality = {
        "candidate_expiry_events": int(len(calendar)),
        "weekly_cycles_labelled": int(len(cycles)),
        "label_counts": {str(k): int(v) for k, v in cycles["label"].value_counts(dropna=False).items()},
        "calendar_status_counts": {str(k): int(v) for k, v in cycles["calendar_status"].value_counts(dropna=False).items()},
        "confirmatory_eligible_rows": int(cycles["confirmatory_eligible"].sum()),
        "calendar_warning": "The weekly schedule is inferred from known weekday regimes. Holiday shifts are not independently linked to official contract archives; all results remain exploratory until this is resolved.",
        "excluded_cycle_candidates": int(len(exclusions)),
        "exclusion_reason_counts": {},
    }
    if exclusions:
        reason_counts = pd.Series([x["reason"] for x in exclusions]).value_counts()
        quality["exclusion_reason_counts"] = {str(k): int(v) for k, v in reason_counts.items()}
    excluded = pd.DataFrame(exclusions)
    return cycles, calendar, {**quality, "_excluded_detail": excluded.to_dict(orient="records")}


def wilson_interval(successes: int, n: int, z: float = 1.959963984540054) -> tuple[float | None, float | None]:
    if n <= 0:
        return None, None
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return max(0.0, center - half), min(1.0, center + half)


def _make_model(name: str) -> Pipeline:
    if name == "logistic":
        return Pipeline([
            ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(C=0.25, max_iter=2000, random_state=42)),
        ])
    if name == "extra_trees":
        return Pipeline([
            ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
            ("model", ExtraTreesClassifier(
                n_estimators=300, max_depth=3, min_samples_leaf=8,
                max_features=0.8, class_weight="balanced", random_state=42, n_jobs=-1,
            )),
        ])
    raise ValueError("Unknown model: " + name)


def _prob_up(model: Pipeline, x: pd.DataFrame) -> float:
    probs = model.predict_proba(x)[0]
    classes = list(model.named_steps["model"].classes_)
    return float(probs[classes.index(1)]) if 1 in classes else float(np.mean(model.named_steps["model"].predict(x) == 1))


def _safe_score(metrics_fun: Any, y: np.ndarray, pred: np.ndarray) -> float | None:
    try:
        value = float(metrics_fun(y, pred))
        return value if np.isfinite(value) else None
    except Exception:
        return None


def compute_metrics(
    name: str, y_true: Iterable[int], y_pred: Iterable[int],
    p_up: Iterable[float] | None = None, is_probability: bool = True,
) -> dict[str, Any]:
    y = np.asarray(list(y_true), dtype=int)
    pred = np.asarray(list(y_pred), dtype=int)
    n = len(y)
    up = int((pred == 1).sum())
    correct = int((pred == y).sum())
    low, high = wilson_interval(correct, n)
    cm = confusion_matrix(y, pred, labels=[0, 1]) if n else np.zeros((2, 2), dtype=int)
    row: dict[str, Any] = {
        "candidate": name,
        "n": n,
        "up_prevalence": float(np.mean(y)) if n else None,
        "predicted_up_fraction": float(np.mean(pred)) if n else None,
        "accuracy": _safe_score(accuracy_score, y, pred) if n else None,
        "balanced_accuracy": _safe_score(balanced_accuracy_score, y, pred) if n else None,
        "precision_up": _safe_score(lambda a, b: precision_score(a, b, pos_label=1, zero_division=0), y, pred) if n else None,
        "recall_up": _safe_score(lambda a, b: recall_score(a, b, pos_label=1, zero_division=0), y, pred) if n else None,
        "precision_down": _safe_score(lambda a, b: precision_score(a, b, pos_label=0, zero_division=0), y, pred) if n else None,
        "recall_down": _safe_score(lambda a, b: recall_score(a, b, pos_label=0, zero_division=0), y, pred) if n else None,
        "f1_macro": _safe_score(lambda a, b: f1_score(a, b, average="macro", zero_division=0), y, pred) if n else None,
        "mcc": _safe_score(matthews_corrcoef, y, pred) if n else None,
        "accuracy_wilson_95_low": low,
        "accuracy_wilson_95_high": high,
        "true_down_pred_down": int(cm[0, 0]) if n else None,
        "true_down_pred_up": int(cm[0, 1]) if n else None,
        "true_up_pred_down": int(cm[1, 0]) if n else None,
        "true_up_pred_up": int(cm[1, 1]) if n else None,
        "probability_metrics_valid": False,
        "brier": None,
        "log_loss": None,
        "roc_auc": None,
    }
    if is_probability and p_up is not None and n:
        p = np.clip(np.asarray(list(p_up), dtype=float), 1e-6, 1 - 1e-6)
        if len(p) == n and np.isfinite(p).all():
            row["probability_metrics_valid"] = True
            row["brier"] = float(brier_score_loss(y, p))
            row["log_loss"] = float(log_loss(y, np.column_stack([1 - p, p]), labels=[0, 1]))
            if len(np.unique(y)) == 2:
                row["roc_auc"] = float(roc_auc_score(y, p))
    return row


def _heuristic_predictions(name: str, train: pd.DataFrame, test: pd.DataFrame) -> tuple[np.ndarray, np.ndarray | None]:
    train_y = train["target"].astype(int).to_numpy()
    majority = int(np.mean(train_y) > 0.5)
    prevalence = float((train_y.sum() + 1.0) / (len(train_y) + 2.0))
    preds = []
    for _, row in test.iterrows():
        if name == "majority":
            pred = majority
        elif name == "prior_cycle":
            pred = int(row["prior_cycle_up"]) if pd.notna(row.get("prior_cycle_up")) else majority
        elif name == "momentum_5d":
            pred = int(float(row["ret_5"]) > 0) if pd.notna(row.get("ret_5")) else majority
        elif name == "prior_cycle_return":
            pred = int(float(row["prior_cycle_return"]) > 0) if pd.notna(row.get("prior_cycle_return")) else majority
        else:
            raise ValueError("Unknown baseline: " + name)
        preds.append(pred)
    # Only the expanding-rate candidate has a coherent probability forecast; directional heuristics have no fitted probability.
    return np.asarray(preds, dtype=int), np.full(len(test), prevalence) if name == "majority" else None


def _rolling_predictions(
    data: pd.DataFrame,
    feature_cols: list[str],
    model_names: list[str],
    minimum_history: int,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, int]]:
    records: dict[str, list[dict[str, Any]]] = {}
    fitted_counts: dict[str, int] = {}
    for name in ["majority", "prior_cycle", "momentum_5d", "prior_cycle_return"] + model_names:
        records[name] = []
        fitted_counts[name] = 0
    for i in range(minimum_history, len(data)):
        train = data.iloc[:i].copy()
        test = data.iloc[[i]].copy()
        train_y = train["target"].astype(int).to_numpy()
        truth = int(test["target"].iloc[0])
        common = {
            "expiry_date": pd.Timestamp(test["expiry_date"].iloc[0]).date().isoformat(),
            "anchor_date": pd.Timestamp(test["anchor_date"].iloc[0]).date().isoformat(),
            "y_true": truth,
            "train_size": len(train),
        }
        for name in ["majority", "prior_cycle", "momentum_5d", "prior_cycle_return"]:
            pred, prob = _heuristic_predictions(name, train, test)
            records[name].append({**common, "y_pred": int(pred[0]), "p_up": float(prob[0]) if prob is not None else np.nan})
        for name in model_names:
            if len(np.unique(train_y)) < 2:
                p = float((train_y.sum() + 1.0) / (len(train_y) + 2.0))
                pred = int(p > 0.5)
            else:
                model = _make_model(name)
                model.fit(train[feature_cols], train_y)
                p = _prob_up(model, test[feature_cols])
                pred = int(p >= 0.5)
            records[name].append({**common, "y_pred": pred, "p_up": p})
            fitted_counts[name] += 1
    return records, fitted_counts


def evaluate_research(cycles: pd.DataFrame, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    data = cycles.copy().sort_values("expiry_date").reset_index(drop=True)
    data["target"] = data["label"].map({"DOWN": 0, "UP": 1, "FLAT": np.nan})
    data = data.loc[data["target"].notna()].copy().reset_index(drop=True)
    data["target"] = data["target"].astype(int)
    # Feature rows at the very beginning can be incomplete; keep them for audit but not model fitting.
    feature_complete = data[FEATURE_COLUMNS].notna().sum(axis=1) >= len(FEATURE_COLUMNS) - 2
    feature_data = data.loc[feature_complete].copy().reset_index(drop=True)
    if len(feature_data) < 80:
        raise ValueError("Only " + str(len(feature_data)) + " binary rows with mostly complete features; insufficient for a meaningful walk-forward test.")
    split_idx = max(1, int(math.floor(0.8 * len(feature_data))))
    dev = feature_data.iloc[:split_idx].copy().reset_index(drop=True)
    holdout = feature_data.iloc[split_idx:].copy().reset_index(drop=True)
    # Honor 104-row target when possible; lower only for sample-size feasibility and report it.
    min_history = min(104, max(30, int(len(dev) * 0.40)))
    models = ["logistic", "extra_trees"]
    dev_pred_records, _ = _rolling_predictions(dev, FEATURE_COLUMNS, models, min_history)
    dev_rows: list[dict[str, Any]] = []
    for name, records in dev_pred_records.items():
        if records:
            frame = pd.DataFrame(records)
            probability_valid = name in ("majority", "logistic", "extra_trees")
            metrics = compute_metrics(name, frame["y_true"], frame["y_pred"], frame["p_up"] if probability_valid else None, probability_valid)
            dev_rows.append(metrics)
    dev_metrics = pd.DataFrame(dev_rows)
    dev_metrics.to_csv(output_dir / "development_metrics.csv", index=False)
    # Frozen selection from development only: maximize balanced accuracy, break ties using lower Brier where present.
    model_metric = dev_metrics.loc[dev_metrics["candidate"].isin(models)].copy()
    model_metric = model_metric.sort_values(["balanced_accuracy", "brier"], ascending=[False, True], na_position="last")
    chosen = str(model_metric.iloc[0]["candidate"]) if len(model_metric) else "logistic"
    hold_records, _ = _rolling_predictions(feature_data, FEATURE_COLUMNS, ["logistic", "extra_trees"], split_idx)
    hold_rows = {}
    holdout_records: list[dict[str, Any]] = []
    for name, records in hold_records.items():
        # Keep only the held-out part; records were emitted at indices >= split_idx.
        frame = pd.DataFrame(records)
        if frame.empty:
            continue
        frame["candidate"] = name
        frame = frame.loc[frame["expiry_date"].isin(holdout["expiry_date"].map(lambda x: pd.Timestamp(x).date().isoformat()))]
        if frame.empty:
            continue
        holdout_records.extend(frame.to_dict(orient="records"))
        probability_valid = name in ("majority", "logistic", "extra_trees")
        metrics = compute_metrics(name, frame["y_true"], frame["y_pred"], frame["p_up"] if probability_valid else None, probability_valid)
        metrics["chosen_on_development"] = name == chosen
        metrics["development_selected_model"] = chosen
        metrics["validation_scope"] = "EXPLORATORY_ONLY: historical expiry calendar has not been fully verified"
        hold_rows[name] = metrics
    hold_metrics = pd.DataFrame(hold_rows.values()).sort_values("balanced_accuracy", ascending=False)
    hold_metrics.to_csv(output_dir / "holdout_metrics.csv", index=False)
    pred_frame = pd.DataFrame(holdout_records)
    if len(pred_frame):
        pred_frame["chosen_on_development"] = pred_frame["candidate"].eq(chosen)
        pred_frame.to_csv(output_dir / "holdout_predictions.csv", index=False)
    dev_pred_rows: list[dict[str, Any]] = []
    for name, recs in dev_pred_records.items():
        for rec in recs:
            dev_pred_rows.append({**rec, "candidate": name})
    pd.DataFrame(dev_pred_rows).to_csv(output_dir / "development_predictions.csv", index=False)

    by_year = feature_data.assign(year=pd.to_datetime(feature_data["expiry_date"]).dt.year).groupby("year").agg(
        observations=("target", "size"),
        up_prevalence=("target", "mean"),
        mean_cycle_return=("return_pct", "mean"),
        median_cycle_return=("return_pct", "median"),
        calendar_heuristic_fraction=("confirmatory_eligible", lambda x: float((~x.astype(bool)).mean())),
    ).reset_index()
    by_year.to_csv(output_dir / "yearly_target_summary.csv", index=False)
    summary = {
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "observations_total_labels": int(len(cycles)),
        "binary_rows": int(len(data)),
        "feature_complete_binary_rows": int(len(feature_data)),
        "development_rows": int(len(dev)),
        "heldout_rows": int(len(holdout)),
        "split_date_first_holdout_expiry": pd.Timestamp(holdout["expiry_date"].iloc[0]).date().isoformat() if len(holdout) else None,
        "minimum_training_history": int(min_history),
        "pre_registered_target_training_history": 104,
        "development_selected_model": chosen,
        "calendar_status": "EXPLORATORY_ONLY",
        "reason_not_confirmatory": "Weekly expiry dates were generated from weekday regimes and inferred from available bars; official historical expiry calendar and holiday shifts are not independently reconciled.",
        "usable_trading_strategy_validated": False,
        "trading_strategy_blocker": "No verified historical futures/options fills, contract-specific price series, dated Paytm Money cost schedule and bid-ask/slippage data have been joined. Spot-direction classification is not executable P&L.",
        "important_warning": "All metrics are exploratory until the official expiry calendar and underlying data quality are verified; model discovery does not certify future performance.",
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=_jsonable), encoding="utf-8")
    return summary


def try_yahoo_daily_validation(daily: pd.DataFrame, calendar: pd.DataFrame, output_dir: Path) -> dict[str, Any]:
    """Optional free-source cross-check; failure is recorded and does not silently pass the quality gate."""
    result: dict[str, Any] = {"attempted": False, "available": False, "source": "Yahoo Finance ^NSEI via yfinance", "matched_rows": 0, "mismatch_rows": 0}
    try:
        import yfinance as yf
        result["attempted"] = True
        start = daily["session_date"].min().date().isoformat()
        end = (daily["session_date"].max() + pd.Timedelta(days=2)).date().isoformat()
        raw = yf.download("^NSEI", start=start, end=end, auto_adjust=False, progress=False, threads=False)
        if raw is None or raw.empty:
            result["error"] = "Yahoo daily history returned no rows"
            return result
        close_col = raw["Close"]
        if isinstance(close_col, pd.DataFrame):
            close_col = close_col.iloc[:, 0]
        yahoo = pd.DataFrame({"session_date": pd.to_datetime(close_col.index).tz_localize(None).normalize(), "yahoo_close": np.asarray(close_col, dtype=float)})
        merged = daily.merge(yahoo, on="session_date", how="inner")
        # Compare last available spot close against independent daily-close values. Keep every mismatch for audit.
        merged["absolute_difference"] = (merged["session_close"] - merged["yahoo_close"]).abs()
        merged["relative_difference"] = merged["absolute_difference"] / merged["yahoo_close"].abs()
        merged.to_csv(output_dir / "yahoo_daily_crosscheck.csv", index=False)
        expiry_dates = set(pd.to_datetime(calendar["resolved_expiry"].dropna()).dt.normalize())
        expiry_overlap = merged.loc[merged["session_date"].isin(expiry_dates)].copy()
        tolerance_points = 1.0
        result.update({
            "available": True,
            "matched_rows": int(len(merged)),
            "expiry_dates_compared": int(len(expiry_overlap)),
            "mismatch_rows": int((expiry_overlap["absolute_difference"] > tolerance_points).sum()),
            "tolerance_index_points": tolerance_points,
            "median_abs_difference": float(merged["absolute_difference"].median()) if len(merged) else None,
            "p95_abs_difference": float(merged["absolute_difference"].quantile(0.95)) if len(merged) else None,
            "note": "Daily close cross-check is an independent public-data diagnostic, not official expiry-calendar proof.",
        })
        return result
    except Exception as exc:
        result["error"] = type(exc).__name__ + ": " + str(exc)[:250]
        return result


def save_figures(cycles: pd.DataFrame, results_dir: Path) -> list[str]:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        return ["plotting skipped: " + type(exc).__name__]
    created: list[str] = []
    yearly = cycles.copy()
    yearly["year"] = pd.to_datetime(yearly["expiry_date"]).dt.year
    yearly["up"] = yearly["label"].eq("UP").astype(float)
    prevalence = yearly.groupby("year").agg(up_rate=("up", "mean"), n=("label", "size")).reset_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(prevalence["year"], prevalence["up_rate"], marker="o")
    ax.axhline(0.5, linestyle="--")
    ax.set_ylim(0, 1)
    ax.set_xlabel("Expiry year")
    ax.set_ylabel("Share of UP outcomes")
    ax.set_title("NIFTY Weekly Expiry Direction: Annual UP Prevalence (Exploratory)")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    p1 = results_dir / "annual_up_prevalence.png"
    fig.savefig(p1, dpi=150)
    plt.close(fig)
    created.append(p1.name)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(cycles["return_pct"].dropna() * 100, bins=35)
    ax.axvline(0, linestyle="--")
    ax.set_xlabel("Cycle return (%)")
    ax.set_ylabel("Count")
    ax.set_title("NIFTY Weekly Expiry Cycle Returns (Exploratory)")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    p2 = results_dir / "cycle_return_distribution.png"
    fig.savefig(p2, dpi=150)
    plt.close(fig)
    created.append(p2.name)
    return created
