#!/usr/bin/env python3
"""Rebuild weekly NIFTY labels from official NSE daily OHLC and Dhan intraday bars.

The source dataset is bounded by available authenticated Dhan history. Raw Dhan bars stay
in the runner cache. This script writes an auditable, chronological model comparison and
does not claim that a directional result is an executable trading strategy.
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    log_loss,
    matthews_corrcoef,
    roc_auc_score,
)

ROOT = Path(__file__).resolve().parents[1]
RAW_DHAN = ROOT / "data" / "cache" / "dhan-anchors"
OFFICIAL_PATH = ROOT / "data" / "reconciliation" / "nifty50_official_daily.csv"
EXPIRY_PATH = ROOT / "data" / "reconciliation" / "expiry_verification.csv"
DHAN_MANIFEST_PATH = ROOT / "data" / "processed" / "dhan_history_manifest.json"
DHAN_CROSSCHECK_PATH = ROOT / "data" / "reconciliation" / "dhan_anchor_comparison_report.json"
PROCESSED = ROOT / "data" / "processed"
RESULTS = ROOT / "research" / "results" / "phase10"
MANUSCRIPT = ROOT / "research" / "manuscript.md"
README = ROOT / "README.md"
RESEARCH_LOG = ROOT / "logs" / "RESEARCH_LOG.md"
ERROR_LOG = ROOT / "logs" / "ERROR_LOG.md"

sys.path.insert(0, str(ROOT / "scripts"))
from research_core import (  # noqa: E402
    FEATURE_COLUMNS,
    IST,
    _heuristic_predictions,
    _make_model,
    _prob_up,
    daily_aggregates,
    construct_weekly_table,
    load_minute_files,
)

NEW_FEATURES = [
    "momentum_spread_5_20",
    "rv_ratio_5_20",
    "trend_efficiency_20",
    "downside_semivol_20",
    "upside_semivol_20",
    "semivol_asymmetry_20",
]
BASELINES = ["majority", "prior_cycle", "momentum_5d", "prior_cycle_return", "logistic_base", "extra_trees_base"]
CHALLENGERS = ["logistic_augmented", "extra_trees_augmented"]
ALL_CANDIDATES = BASELINES + CHALLENGERS
MIN_HISTORY = 104
HOLDOUT_FRACTION = 0.20
BOOTSTRAP_BLOCK = 4
BOOTSTRAP_REPS = 2000
SEED = 20261026
PHASE10_START = "<!-- PHASE10_RESULTS_START -->"
PHASE10_END = "<!-- PHASE10_RESULTS_END -->"
README_START = "<!-- PHASE10_STATUS_START -->"
README_END = "<!-- PHASE10_STATUS_END -->"


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError("Required report missing: " + str(path.relative_to(ROOT)))
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Required report is not a JSON object: " + str(path.relative_to(ROOT)))
    return data


def build_official_daily_calendar(
    official_raw: pd.DataFrame,
    minutes: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Use NSE calendar/OHLC for every official session; keep Dhan bar counts separate."""
    required = {"session_date", "official_open", "official_high", "official_low", "official_close"}
    if not required.issubset(official_raw.columns):
        raise ValueError("Official daily OHLC is missing fields: " + ", ".join(sorted(required - set(official_raw.columns))))
    official = official_raw.copy()
    official["session_date"] = pd.to_datetime(official["session_date"], errors="coerce").dt.normalize()
    for col in ("official_open", "official_high", "official_low", "official_close"):
        official[col] = pd.to_numeric(official[col], errors="coerce")
    official = official.dropna(subset=["session_date", "official_open", "official_high", "official_low", "official_close"])
    if official["session_date"].duplicated().any():
        raise ValueError("Official daily OHLC contains duplicate session dates")
    valid_ohlc = (
        (official[["official_open", "official_high", "official_low", "official_close"]] > 0).all(axis=1)
        & (official["official_low"] <= official[["official_open", "official_close"]].min(axis=1))
        & (official["official_high"] >= official[["official_open", "official_close"]].max(axis=1))
        & (official["official_low"] <= official["official_high"])
    )
    if not bool(valid_ohlc.all()):
        raise ValueError("Official daily OHLC contains invalid price rows")

    dhan_daily_raw = daily_aggregates(minutes)
    rename = {
        "session_open": "session_open_dhan_aggregate",
        "session_high": "session_high_dhan_aggregate",
        "session_low": "session_low_dhan_aggregate",
        "session_close": "session_close_dhan_aggregate",
        "session_return": "session_return_dhan_aggregate",
        "range_pct": "range_pct_dhan_aggregate",
    }
    dhan_daily = dhan_daily_raw.rename(columns=rename)
    daily = official.merge(dhan_daily, on="session_date", how="left", validate="one_to_one")
    daily["session_open_archive"] = daily["session_open_dhan_aggregate"]
    daily["session_high_archive"] = daily["session_high_dhan_aggregate"]
    daily["session_low_archive"] = daily["session_low_dhan_aggregate"]
    daily["session_close_archive"] = daily["session_close_dhan_aggregate"]

    # Critical: official daily OHLC, not potentially corrupted minute-archive aggregates,
    # are the canonical values for lagged features and expiry closes.
    daily["session_open"] = daily["official_open"].astype(float)
    daily["session_high"] = daily["official_high"].astype(float)
    daily["session_low"] = daily["official_low"].astype(float)
    daily["session_close"] = daily["official_close"].astype(float)
    daily["official_close"] = daily["official_close"].astype(float)
    daily["bars"] = pd.to_numeric(daily["bars"], errors="coerce").fillna(0).astype(int)
    daily["max_unchanged_close_run"] = pd.to_numeric(
        daily["max_unchanged_close_run"], errors="coerce"
    ).fillna(0).astype(int)
    daily["unchanged_close_fraction"] = pd.to_numeric(daily["unchanged_close_fraction"], errors="coerce")
    daily["session_return"] = daily["session_close"].pct_change()
    daily["range_pct"] = (daily["session_high"] - daily["session_low"]) / daily["session_close"].shift(1)

    anchor_window = daily.loc[daily["bars"] > 0]
    diff_summary: dict[str, Any] = {}
    for field in ("open", "high", "low", "close"):
        source_col = f"session_{field}_dhan_aggregate"
        official_col = f"official_{field}"
        overlap = daily[source_col].notna() & daily[official_col].notna()
        diffs = (daily.loc[overlap, source_col] - daily.loc[overlap, official_col]).abs()
        diff_summary[field] = {
            "compared_sessions": int(len(diffs)),
            "median_absolute_difference_points": float(diffs.median()) if len(diffs) else None,
            "p95_absolute_difference_points": float(diffs.quantile(0.95)) if len(diffs) else None,
            "mismatches_over_1_point": int((diffs > 1.0).sum()) if len(diffs) else None,
            "max_absolute_difference_points": float(diffs.max()) if len(diffs) else None,
        }
    quality = {
        "official_sessions": int(len(daily)),
        "official_first_session": daily["session_date"].min().date().isoformat(),
        "official_last_session": daily["session_date"].max().date().isoformat(),
        "official_sessions_with_dhan_intraday": int(len(anchor_window)),
        "official_sessions_without_dhan_intraday": int((daily["bars"] == 0).sum()),
        "dhan_sessions_with_at_least_250_bars": int((daily["bars"] >= 250).sum()),
        "official_daily_ohlc_checks": "PASS",
        "lagged_feature_source": "official NSE daily OHLC snapshot",
        "session_calendar_source": "official NSE daily dates",
        "dhan_aggregate_vs_official_differences": diff_summary,
    }
    return daily.sort_values("session_date").reset_index(drop=True), quality


def add_causal_features(cycles: pd.DataFrame, daily: pd.DataFrame) -> pd.DataFrame:
    """Add six features using official daily data strictly before each 10:00 anchor."""
    frame = cycles.copy().sort_values("expiry_date").reset_index(drop=True)
    feature_rows: list[dict[str, float]] = []
    for _, row in frame.iterrows():
        anchor_date = pd.Timestamp(row["anchor_date"]).normalize()
        prior = daily.loc[pd.to_datetime(daily["session_date"]).dt.normalize() < anchor_date].sort_values("session_date")
        close = prior["session_close"].astype(float).reset_index(drop=True)
        returns = close.pct_change().dropna().tail(20)
        ret_5 = float(row["ret_5"]) if pd.notna(row.get("ret_5")) else np.nan
        ret_20 = float(row["ret_20"]) if pd.notna(row.get("ret_20")) else np.nan
        rv_5 = float(row["rv_5"]) if pd.notna(row.get("rv_5")) else np.nan
        rv_20 = float(row["rv_20"]) if pd.notna(row.get("rv_20")) else np.nan
        momentum_spread = ret_5 - ret_20 * 0.25 if np.isfinite(ret_5) and np.isfinite(ret_20) else np.nan
        rv_ratio = rv_5 / rv_20 if np.isfinite(rv_5) and np.isfinite(rv_20) and rv_20 > 0 else np.nan

        efficiency = np.nan
        if len(close) >= 21 and len(returns) >= 20:
            gross_return = abs(float(close.iloc[-1] / close.iloc[-21] - 1.0))
            path_length = float(returns.abs().sum())
            if path_length > 0:
                efficiency = gross_return / path_length

        downside = np.nan
        upside = np.nan
        asymmetry = np.nan
        if len(returns) >= 15:
            downside = float(np.sqrt(np.mean(np.square(np.minimum(returns.to_numpy(), 0.0)))))
            upside = float(np.sqrt(np.mean(np.square(np.maximum(returns.to_numpy(), 0.0)))))
            if upside > 0:
                asymmetry = downside / upside
        feature_rows.append({
            "momentum_spread_5_20": momentum_spread,
            "rv_ratio_5_20": rv_ratio,
            "trend_efficiency_20": efficiency,
            "downside_semivol_20": downside,
            "upside_semivol_20": upside,
            "semivol_asymmetry_20": asymmetry,
        })
    return pd.concat([frame.reset_index(drop=True), pd.DataFrame(feature_rows)], axis=1)


def row_source_gate(cycles: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    frame = cycles.copy()
    verified_calendar = frame["calendar_status"].astype(str).str.startswith("official_verified")
    verified_close = frame["expiry_close_source"].eq("NSE_official_daily_close")
    anchor_delay = pd.to_numeric(frame["anchor_bar_delay_minutes"], errors="coerce")
    anchor_coverage = pd.to_numeric(frame["anchor_session_bars"], errors="coerce") >= 250
    expiry_coverage = pd.to_numeric(frame["expiry_session_bars"], errors="coerce") >= 250
    anchor_ts = pd.to_datetime(frame["anchor_timestamp"], errors="coerce", utc=True).dt.tz_convert(IST)
    anchor_clock = anchor_ts.dt.time
    timing_ok = anchor_ts.notna() & (anchor_clock >= pd.Timestamp("10:00").time()) & (
        anchor_clock <= pd.Timestamp("10:03").time()
    ) & (anchor_delay >= 0) & (anchor_delay <= 3)
    gate = verified_calendar & verified_close & anchor_coverage & expiry_coverage & timing_ok
    frame["source_gate_pass"] = gate
    frame["confirmatory_eligible"] = gate
    frame["source_quality_status"] = np.where(
        gate,
        "official_NSE_daily_OHLC_verified_expiry_DhanHQ_anchor",
        "excluded_source_or_coverage_check_failed",
    )
    summary = {
        "cycles_built": int(len(frame)),
        "row_source_gate_pass": int(gate.sum()),
        "row_source_gate_fail": int((~gate).sum()),
        "all_passing_rows_use_official_daily_expiry_close": bool(frame.loc[gate, "expiry_close_source"].eq("NSE_official_daily_close").all()),
        "calendar_status_counts": {str(k): int(v) for k, v in frame["calendar_status"].value_counts(dropna=False).items()},
        "exclusion_or_flag_counts": {
            "anchor_delay_outside_0_to_3_minutes": int((~timing_ok).sum()),
            "official_calendar_not_verified": int((~verified_calendar).sum()),
            "expiry_close_not_official": int((~verified_close).sum()),
            "anchor_session_under_250_Dhan_bars": int((~anchor_coverage).sum()),
            "expiry_session_under_250_Dhan_bars": int((~expiry_coverage).sum()),
        },
    }
    return frame, summary


def wilson_interval(successes: int, n: int, z: float = 1.959963984540054) -> tuple[float | None, float | None]:
    if n <= 0:
        return None, None
    p = successes / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2.0 * n)) / denom
    margin = z * math.sqrt((p * (1.0 - p) / n) + z * z / (4.0 * n * n)) / denom
    return max(0.0, centre - margin), min(1.0, centre + margin)


def _candidate_features(candidate: str) -> tuple[str, list[str] | None]:
    if candidate == "logistic_base":
        return "logistic", list(FEATURE_COLUMNS)
    if candidate == "extra_trees_base":
        return "extra_trees", list(FEATURE_COLUMNS)
    if candidate == "logistic_augmented":
        return "logistic", list(FEATURE_COLUMNS) + NEW_FEATURES
    if candidate == "extra_trees_augmented":
        return "extra_trees", list(FEATURE_COLUMNS) + NEW_FEATURES
    return "", None


def walk_forward_predictions(data: pd.DataFrame, split_idx: int) -> pd.DataFrame:
    """One-step-ahead expanding walk-forward predictions, with fixed pre-registered models."""
    records: list[dict[str, Any]] = []
    for i in range(MIN_HISTORY, len(data)):
        train = data.iloc[:i].copy()
        test = data.iloc[[i]].copy()
        train_y = train["target"].astype(int).to_numpy()
        truth = int(test["target"].iloc[0])
        common = {
            "row_index": int(i),
            "split": "development" if i < split_idx else "holdout",
            "expiry_date": pd.Timestamp(test["expiry_date"].iloc[0]).date().isoformat(),
            "anchor_date": pd.Timestamp(test["anchor_date"].iloc[0]).date().isoformat(),
            "y_true": truth,
            "train_size": int(len(train)),
        }
        for candidate in ("majority", "prior_cycle", "momentum_5d", "prior_cycle_return"):
            pred, prob = _heuristic_predictions(candidate, train, test)
            records.append({
                **common,
                "candidate": candidate,
                "y_pred": int(pred[0]),
                "p_up": float(prob[0]) if prob is not None else np.nan,
            })
        for candidate in ("logistic_base", "extra_trees_base", "logistic_augmented", "extra_trees_augmented"):
            model_name, features = _candidate_features(candidate)
            if len(np.unique(train_y)) < 2:
                p_up = float((train_y.sum() + 1.0) / (len(train_y) + 2.0))
                pred = int(p_up >= 0.5)
            else:
                model = _make_model(model_name)
                model.fit(train[features], train_y)
                p_up = _prob_up(model, test[features])
                pred = int(p_up >= 0.5)
            records.append({
                **common,
                "candidate": candidate,
                "y_pred": int(pred),
                "p_up": float(p_up),
            })
    return pd.DataFrame(records)


def compute_metric_row(candidate: str, records: pd.DataFrame, split_name: str) -> dict[str, Any]:
    subset = records.loc[(records["candidate"] == candidate) & (records["split"] == split_name)].copy()
    if subset.empty:
        return {"candidate": candidate, "split": split_name, "n": 0}
    y = subset["y_true"].astype(int).to_numpy()
    pred = subset["y_pred"].astype(int).to_numpy()
    n = len(y)
    correct = int((pred == y).sum())
    ci_low, ci_high = wilson_interval(correct, n)
    cm = confusion_matrix(y, pred, labels=[0, 1])
    tn, fp, fn, tp = [int(x) for x in cm.ravel()]
    row: dict[str, Any] = {
        "candidate": candidate,
        "split": split_name,
        "n": n,
        "up_prevalence": float(np.mean(y)),
        "predicted_up_fraction": float(np.mean(pred)),
        "accuracy": float(accuracy_score(y, pred)),
        "accuracy_wilson_95_low": ci_low,
        "accuracy_wilson_95_high": ci_high,
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)) if len(np.unique(y)) == 2 else None,
        "mcc": float(matthews_corrcoef(y, pred)) if len(np.unique(pred)) > 1 and len(np.unique(y)) > 1 else 0.0,
        "precision_up": float(tp / (tp + fp)) if tp + fp else 0.0,
        "recall_up": float(tp / (tp + fn)) if tp + fn else 0.0,
        "precision_down": float(tn / (tn + fn)) if tn + fn else 0.0,
        "recall_down": float(tn / (tn + fp)) if tn + fp else 0.0,
        "tn": tn, "fp": fp, "fn": fn, "tp": tp,
    }
    probs = pd.to_numeric(subset["p_up"], errors="coerce")
    valid_prob = probs.notna() & np.isfinite(probs)
    if int(valid_prob.sum()) == n:
        p = np.clip(probs.to_numpy(dtype=float), 1e-6, 1.0 - 1e-6)
        row["brier"] = float(np.mean(np.square(p - y)))
        row["log_loss"] = float(log_loss(y, p, labels=[0, 1]))
        row["roc_auc"] = float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None
    else:
        row["brier"] = None
        row["log_loss"] = None
        row["roc_auc"] = None
    return row


def select_development_candidates(development_metrics: pd.DataFrame) -> tuple[str, str]:
    """Return the best base baseline and best augmented candidate; never read holdout metrics."""
    def choose(names: list[str]) -> str:
        subset = development_metrics.loc[development_metrics["candidate"].isin(names)].copy()
        subset = subset.loc[subset["n"] > 0]
        if subset.empty:
            raise ValueError("No development predictions for candidate group: " + ", ".join(names))
        subset["brier_sort"] = pd.to_numeric(subset["brier"], errors="coerce").fillna(9.0)
        subset = subset.sort_values(["balanced_accuracy", "brier_sort", "candidate"], ascending=[False, True, True], na_position="last")
        return str(subset.iloc[0]["candidate"])
    return choose(BASELINES), choose(CHALLENGERS)


def balanced_acc_from_arrays(y: np.ndarray, pred: np.ndarray) -> float:
    if len(np.unique(y)) != 2:
        return float("nan")
    return float(balanced_accuracy_score(y, pred))


def moving_block_bootstrap_diff(
    y: np.ndarray,
    challenger: np.ndarray,
    baseline: np.ndarray,
    reps: int = BOOTSTRAP_REPS,
    block: int = BOOTSTRAP_BLOCK,
    seed: int = SEED,
) -> dict[str, Any]:
    """Paired four-week moving-block bootstrap of balanced accuracy difference."""
    n = len(y)
    if n < max(12, block * 3) or len(np.unique(y)) < 2:
        return {"status": "UNDERPOWERED", "n": n, "block_length": block, "replicates_requested": reps}
    rng = np.random.default_rng(seed)
    differences: list[float] = []
    max_start = n - block
    if max_start < 0:
        return {"status": "UNDERPOWERED", "n": n, "block_length": block, "replicates_requested": reps}
    attempts = 0
    max_attempts = reps * 20
    while len(differences) < reps and attempts < max_attempts:
        attempts += 1
        indices: list[int] = []
        while len(indices) < n:
            start = int(rng.integers(0, max_start + 1))
            indices.extend(range(start, min(start + block, n)))
        ix = np.asarray(indices[:n], dtype=int)
        yy = y[ix]
        if len(np.unique(yy)) < 2:
            continue
        diff = balanced_acc_from_arrays(yy, challenger[ix]) - balanced_acc_from_arrays(yy, baseline[ix])
        if np.isfinite(diff):
            differences.append(float(diff))
    if len(differences) < max(200, reps // 2):
        return {
            "status": "UNDERPOWERED",
            "n": n,
            "block_length": block,
            "replicates_requested": reps,
            "replicates_valid": len(differences),
        }
    values = np.asarray(differences)
    return {
        "status": "COMPLETED",
        "n": n,
        "block_length": block,
        "replicates_requested": reps,
        "replicates_valid": int(len(values)),
        "difference_mean": float(values.mean()),
        "difference_ci_95_low": float(np.quantile(values, 0.025)),
        "difference_ci_95_high": float(np.quantile(values, 0.975)),
    }


def _fmt(value: Any, digits: int = 3) -> str:
    try:
        if value is None or pd.isna(value):
            return "n/a"
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def render_report(summary: dict[str, Any], data_quality: dict[str, Any], dev_metrics: pd.DataFrame,
                  hold_metrics: pd.DataFrame, bootstrap: dict[str, Any], selected_baseline: str,
                  selected_challenger: str, screen: dict[str, Any]) -> str:
    def make_table(frame: pd.DataFrame) -> str:
        columns = ["candidate", "n", "accuracy", "balanced_accuracy", "mcc", "brier", "log_loss", "roc_auc"]
        available = [col for col in columns if col in frame.columns]
        lines = ["| " + " | ".join(available) + " |", "|" + "|".join(["---"] * len(available)) + "|"]
        for _, row in frame[available].iterrows():
            vals = []
            for col in available:
                vals.append(str(row[col]) if col in ("candidate", "n") else _fmt(row[col]))
            lines.append("| " + " | ".join(vals) + " |")
        return "\n".join(lines)

    return f"""# Phase 10 Results — Dhan-Backed Weekly NIFTY Direction

Generated (UTC): {summary["generated_utc"]}

## Executive result

- **Dataset status:** {summary["dataset_status"]}.
- **Model result:** {summary["model_result_status"]}.
- **Usable trading strategy:** NOT VALIDATED. No contract-level options/futures P&L with complete date-specific Paytm Money charges, spreads, slippage and fills was performed in this bounded model phase.
- **Selected baseline from development:** {selected_baseline}.
- **Selected augmented challenger from development:** {selected_challenger}.
- **Pre-registered screening result:** {"PASS" if screen.get("pass") else "NOT PASSED"} — {screen.get("reason", "see machine-readable summary")}.

## Data and target construction

The target uses the verified actual weekly expiry calendar and official NSE daily OHLC. The anchor and pre-anchor intraday features use authenticated DhanHQ 1-minute bars. The official NSE session list, not the set of observed Dhan sessions, determines the first trading session after the previous expiry. This avoids shifting the anchor when Dhan has a coverage gap.

- Official NSE daily sessions: {data_quality.get("official_sessions", "n/a")} ({data_quality.get("official_first_session", "n/a")} to {data_quality.get("official_last_session", "n/a")}).
- Official sessions with Dhan intraday bars: {data_quality.get("official_sessions_with_dhan_intraday", "n/a")}.
- Weekly cycles built / source-gate rows: {data_quality.get("target_construction", {}).get("cycles_built", "n/a")} / {data_quality.get("target_construction", {}).get("row_source_gate_pass", "n/a")}.
- Dhan anchor cross-check: {json.dumps(data_quality.get("dhan_anchor_crosscheck", {}), sort_keys=True)}.
- Fresh holdout: {summary.get("holdout_first_expiry_date", "n/a")} to {summary.get("holdout_last_expiry_date", "n/a")} ({summary.get("holdout_rows", "n/a")} rows); development predictions start only after {MIN_HISTORY} earlier labelled rows.
- All feature engineering is causal to the 10:00 cutoff; the selected candle's later high/low/close is not used.

## Development walk-forward metrics

{make_table(dev_metrics)}

## Locked chronological holdout metrics

{make_table(hold_metrics)}

## Pre-registered primary comparison

- Baseline: {selected_baseline}; challenger: {selected_challenger}.
- Holdout balanced-accuracy difference: {_fmt(screen.get("balanced_accuracy_difference"))}.
- Paired four-week moving-block bootstrap: {json.dumps(bootstrap, sort_keys=True)}.
- Brier baseline / challenger: {_fmt(screen.get("baseline_brier"))} / {_fmt(screen.get("challenger_brier"))}.
- Log-loss baseline / challenger: {_fmt(screen.get("baseline_log_loss"))} / {_fmt(screen.get("challenger_log_loss"))}.
- Subperiod balanced-accuracy differences (first half / second half): {_fmt(screen.get("first_half_balanced_accuracy_difference"))} / {_fmt(screen.get("second_half_balanced_accuracy_difference"))}.

## Interpretation

{screen.get("interpretation", "Interpret the fixed candidate results cautiously; see summary.json for the registered screening logic.")}

The data rebuild is source-identified for the Dhan coverage window and uses official daily prices/calendars. The earlier public minute archive remains in the error history for its mismatch with official daily OHLC; it was not used for the rebuilt labels or lagged daily features. The secondary-public-source anchor comparison is diagnostic rather than official ground truth.

## Limitations and next steps

The sample is limited to the available Dhan historical window. The holdout is small, and a single positive metric does not establish a repeatable trading edge. Options IV/OI/skew, timestamp-valid global inputs and lagged flow data have not been added in this experiment. No futures/options instrument-level backtest or costs were computed. The correct stopping outcome if the augmented method does not pass the pre-registered screening rule is **no new directional method validated in this bounded run**.

Reproducibility files: phase10_split_manifest.json; data_quality_report.json; development_metrics.csv; holdout_metrics.csv; holdout_predictions.csv; source and exclusion tables; plots.
"""


def update_section(path: Path, start_marker: str, end_marker: str, block: str, before_heading: str | None = None) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    wrapped = start_marker + "\n" + block.strip() + "\n" + end_marker
    if start_marker in existing and end_marker in existing:
        left = existing.index(start_marker)
        right = existing.index(end_marker, left) + len(end_marker)
        updated = existing[:left] + wrapped + existing[right:]
    elif before_heading and before_heading in existing:
        updated = existing.replace(before_heading, wrapped + "\n\n" + before_heading, 1)
    else:
        updated = existing.rstrip() + "\n\n" + wrapped + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(updated, encoding="utf-8")


def plot_results(cycles: pd.DataFrame, development: pd.DataFrame, holdout: pd.DataFrame, baseline: str, challenger: str) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    fixed_order = ALL_CANDIDATES
    dev = development.set_index("candidate").reindex(fixed_order)
    hld = holdout.set_index("candidate").reindex(fixed_order)
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(fixed_order))
    width = 0.38
    ax.bar(x - width / 2, dev["balanced_accuracy"], width=width, label="Development")
    ax.bar(x + width / 2, hld["balanced_accuracy"], width=width, label="Holdout")
    ax.axhline(0.5, linestyle="--", linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(fixed_order, rotation=28, ha="right")
    ax.set_ylabel("Balanced accuracy")
    ax.set_ylim(0, 1)
    ax.set_title("Phase 10 — Fixed candidate walk-forward comparison")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "phase10_method_comparison.png", dpi=160)
    plt.close(fig)

    returns = pd.to_numeric(cycles["return_pct"], errors="coerce").dropna() * 100.0
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(returns, bins=25)
    ax.axvline(0, linestyle="--", linewidth=1)
    ax.set_xlabel("10:00 anchor to official expiry close return (%)")
    ax.set_ylabel("Weekly cycles")
    ax.set_title("Phase 10 — Rebuilt cycle-return distribution")
    fig.tight_layout()
    fig.savefig(RESULTS / "phase10_cycle_return_distribution.png", dpi=160)
    plt.close(fig)


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    try:
        official_raw = pd.read_csv(OFFICIAL_PATH)
        expiry_raw = pd.read_csv(EXPIRY_PATH)
        history_manifest = read_json(DHAN_MANIFEST_PATH)
        if history_manifest.get("status") != "READY":
            raise ValueError("Dhan history manifest is not READY; refusing to build labels.")
        crosscheck: dict[str, Any] = {}
        if DHAN_CROSSCHECK_PATH.is_file():
            crosscheck = read_json(DHAN_CROSSCHECK_PATH)

        cache_files = sorted(RAW_DHAN.glob("dhan_*.csv"))
        if not cache_files:
            raise FileNotFoundError("No Dhan minute chunks exist in the runtime cache.")
        minutes, minute_quality = load_minute_files(cache_files)
        if len(minutes) < 200_000:
            raise ValueError("Dhan five-year cache contains unexpectedly few valid minute bars.")
        actual_first = pd.Timestamp(minutes["timestamp"].min())
        actual_last = pd.Timestamp(minutes["timestamp"].max())
        manifest_start = pd.Timestamp(history_manifest["window"]["start"]).date()
        manifest_end = pd.Timestamp(history_manifest["window"]["end"]).date()
        if actual_first.date() > manifest_start or actual_last.date() < (manifest_end - pd.Timedelta(days=4)):
            raise ValueError("Dhan cache timestamp coverage does not match the declared five-year window.")

        daily, daily_quality = build_official_daily_calendar(official_raw, minutes)
        expiry_raw["status"] = expiry_raw["status"].astype(str)
        contract_ok = expiry_raw["contract_expiry_present"].astype(str).str.casefold().isin({"true", "1"})
        if not expiry_raw["status"].str.startswith("verified_").all() or not contract_ok.all():
            raise ValueError("Official expiry-verification table is incomplete; model evaluation is blocked.")
        expiry_dates = pd.to_datetime(expiry_raw["verified_expiry_trade_date"], errors="coerce")
        if expiry_dates.isna().any() or expiry_dates.dt.normalize().duplicated().any():
            raise ValueError("Official verified expiry dates are invalid or duplicated.")

        cycles, calendar, construction = construct_weekly_table(minutes, daily, EXPIRY_PATH)
        excluded_detail = construction.pop("_excluded_detail", [])
        cycles, source_gate = row_source_gate(cycles)
        cycles = add_causal_features(cycles, daily)
        if not bool(cycles["source_gate_pass"].all()):
            raise ValueError("One or more constructed rows failed the registered Dhan/official-source gate.")
        if len(cycles) < 160:
            raise ValueError("Too few source-gated weekly cycles for a bounded 104-row walk-forward evaluation: " + str(len(cycles)))

        cycles.to_csv(PROCESSED / "phase10_dhan_weekly_labels_features.csv", index=False)
        calendar.to_csv(PROCESSED / "phase10_expiry_calendar_used.csv", index=False)
        pd.DataFrame(excluded_detail).to_csv(PROCESSED / "phase10_excluded_cycle_candidates.csv", index=False)

        binary = cycles.loc[cycles["label"].isin(["UP", "DOWN"])].copy().sort_values("expiry_date").reset_index(drop=True)
        binary["target"] = binary["label"].map({"DOWN": 0, "UP": 1}).astype(int)
        feature_complete = binary[FEATURE_COLUMNS].notna().sum(axis=1) >= len(FEATURE_COLUMNS) - 2
        model_data = binary.loc[feature_complete].copy().reset_index(drop=True)
        if len(model_data) < MIN_HISTORY + 30:
            raise ValueError("Too few feature-complete rows for 104-history and the locked holdout: " + str(len(model_data)))
        split_idx = int(math.floor((1.0 - HOLDOUT_FRACTION) * len(model_data)))
        if split_idx <= MIN_HISTORY + 25 or len(model_data) - split_idx < 30:
            raise ValueError("The registered 80/20 split is underpowered for the minimum-history and holdout requirements.")

        # Freeze the split and the candidate roster before generating any development/holdout metrics.
        split_manifest = {
            "schema_version": 1,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "branch": os.getenv("GITHUB_REF_NAME", "local"),
            "source_data_manifest": "data/processed/dhan_history_manifest.json",
            "source_gate": "PASS_FOR_DHAN_WINDOW; Dhan 10:00 anchor + official NSE daily OHLC + official verified expiry; model performance remains exploratory",
            "target": "official NSE close on verified weekly expiry / Dhan 10:00-10:03 anchor open - 1",
            "label_rule": "UP if return_pct > 0; DOWN if return_pct < 0; FLAT retained in the audit data and excluded from binary fitting",
            "minimum_training_history": MIN_HISTORY,
            "holdout_fraction": HOLDOUT_FRACTION,
            "total_source_gated_cycles": int(len(cycles)),
            "binary_rows": int(len(binary)),
            "feature_complete_rows": int(len(model_data)),
            "development_rows": int(split_idx),
            "heldout_rows": int(len(model_data) - split_idx),
            "development_first_expiry": pd.Timestamp(model_data["expiry_date"].iloc[0]).date().isoformat(),
            "development_last_expiry": pd.Timestamp(model_data["expiry_date"].iloc[split_idx - 1]).date().isoformat(),
            "holdout_first_expiry": pd.Timestamp(model_data["expiry_date"].iloc[split_idx]).date().isoformat(),
            "holdout_last_expiry": pd.Timestamp(model_data["expiry_date"].iloc[-1]).date().isoformat(),
            "base_features": FEATURE_COLUMNS,
            "added_features": NEW_FEATURES,
            "fixed_candidates": ALL_CANDIDATES,
            "selection_rule": "Select strongest baseline and strongest augmented candidate using development expanding-walk-forward balanced accuracy, tie-break by Brier score when available. Do not select using holdout results.",
            "screening_rule": {
                "minimum_balanced_accuracy_improvement": 0.03,
                "paired_moving_block_bootstrap_ci_lower_must_exceed": 0.0,
                "block_length_weeks": BOOTSTRAP_BLOCK,
                "bootstrap_replicates": BOOTSTRAP_REPS,
                "brier_tolerance": 0.01,
                "log_loss_tolerance": 0.02,
                "both_half_periods_must_not_reverse": True,
            },
            "holdout_reuse": "Not used for candidate/feature selection; evaluated once after frozen development selection",
        }
        (RESULTS / "phase10_split_manifest.json").write_text(json.dumps(split_manifest, indent=2) + "\n", encoding="utf-8")

        predictions = walk_forward_predictions(model_data, split_idx)
        predictions.to_csv(RESULTS / "walk_forward_predictions_all_candidates.csv", index=False)
        dev_metric_rows = [compute_metric_row(candidate, predictions, "development") for candidate in ALL_CANDIDATES]
        hold_metric_rows = [compute_metric_row(candidate, predictions, "holdout") for candidate in ALL_CANDIDATES]
        development_metrics = pd.DataFrame(dev_metric_rows)
        holdout_metrics = pd.DataFrame(hold_metric_rows)
        development_metrics.to_csv(RESULTS / "development_metrics.csv", index=False)
        holdout_metrics.to_csv(RESULTS / "holdout_metrics.csv", index=False)
        selected_baseline, selected_challenger = select_development_candidates(development_metrics)
        baseline_hold = predictions.loc[(predictions["candidate"] == selected_baseline) & (predictions["split"] == "holdout")].sort_values("row_index")
        challenger_hold = predictions.loc[(predictions["candidate"] == selected_challenger) & (predictions["split"] == "holdout")].sort_values("row_index")
        merged_hold = baseline_hold[["row_index", "y_true", "y_pred", "p_up"]].merge(
            challenger_hold[["row_index", "y_pred", "p_up"]], on="row_index", how="inner", suffixes=("_baseline", "_challenger"), validate="one_to_one"
        ).sort_values("row_index")
        if merged_hold.empty:
            raise ValueError("Selected baseline/challenger have no paired holdout predictions.")
        y = merged_hold["y_true"].astype(int).to_numpy()
        base_pred = merged_hold["y_pred_baseline"].astype(int).to_numpy()
        chall_pred = merged_hold["y_pred_challenger"].astype(int).to_numpy()
        base_ba = balanced_acc_from_arrays(y, base_pred)
        chall_ba = balanced_acc_from_arrays(y, chall_pred)
        ba_diff = float(chall_ba - base_ba) if np.isfinite(base_ba) and np.isfinite(chall_ba) else None
        bootstrap = moving_block_bootstrap_diff(y, chall_pred, base_pred)
        baseline_metric = compute_metric_row(selected_baseline, predictions, "holdout")
        challenger_metric = compute_metric_row(selected_challenger, predictions, "holdout")
        base_brier = baseline_metric.get("brier")
        challenger_brier = challenger_metric.get("brier")
        base_logloss = baseline_metric.get("log_loss")
        challenger_logloss = challenger_metric.get("log_loss")
        probabilities_comparable = (
            base_brier is not None and challenger_brier is not None
            and base_logloss is not None and challenger_logloss is not None
        )
        first_half_diff = None
        second_half_diff = None
        midpoint = len(merged_hold) // 2
        for segment_name, segment in (("first", merged_hold.iloc[:midpoint]), ("second", merged_hold.iloc[midpoint:])):
            if len(segment) < 8 or segment["y_true"].nunique() < 2:
                diff = None
            else:
                ys = segment["y_true"].astype(int).to_numpy()
                diff = float(balanced_acc_from_arrays(ys, segment["y_pred_challenger"].astype(int).to_numpy()) -
                             balanced_acc_from_arrays(ys, segment["y_pred_baseline"].astype(int).to_numpy()))
            if segment_name == "first":
                first_half_diff = diff
            else:
                second_half_diff = diff
        bootstrap_lower = bootstrap.get("difference_ci_95_low")
        quality_brier = bool(probabilities_comparable and challenger_brier <= base_brier + 0.01)
        quality_logloss = bool(probabilities_comparable and challenger_logloss <= base_logloss + 0.02)
        period_stability = bool(first_half_diff is not None and second_half_diff is not None and first_half_diff >= 0 and second_half_diff >= 0)
        screen_pass = bool(
            ba_diff is not None and ba_diff >= 0.03
            and bootstrap.get("status") == "COMPLETED" and bootstrap_lower is not None and bootstrap_lower > 0
            and quality_brier and quality_logloss and period_stability
        )
        failed = []
        if ba_diff is None or ba_diff < 0.03:
            failed.append("holdout balanced-accuracy improvement is below +0.03")
        if bootstrap.get("status") != "COMPLETED" or bootstrap_lower is None or bootstrap_lower <= 0:
            failed.append("paired four-week bootstrap 95% interval does not establish improvement above zero")
        if not quality_brier:
            failed.append("Brier scores are unavailable or challenger degrades by more than 0.01")
        if not quality_logloss:
            failed.append("log-loss scores are unavailable or challenger degrades by more than 0.02")
        if not period_stability:
            failed.append("one or both holdout subperiods are underpowered or show direction reversal")
        screen = {
            "baseline_candidate": selected_baseline,
            "challenger_candidate": selected_challenger,
            "baseline_balanced_accuracy": float(base_ba) if np.isfinite(base_ba) else None,
            "challenger_balanced_accuracy": float(chall_ba) if np.isfinite(chall_ba) else None,
            "balanced_accuracy_difference": ba_diff,
            "baseline_brier": base_brier,
            "challenger_brier": challenger_brier,
            "baseline_log_loss": base_logloss,
            "challenger_log_loss": challenger_logloss,
            "first_half_balanced_accuracy_difference": first_half_diff,
            "second_half_balanced_accuracy_difference": second_half_diff,
            "brier_non_degradation_pass": quality_brier,
            "log_loss_non_degradation_pass": quality_logloss,
            "subperiod_stability_pass": period_stability,
            "pass": screen_pass,
            "reason": "All pre-registered screening criteria passed." if screen_pass else "; ".join(failed),
            "interpretation": (
                "The augmented model passed the pre-registered statistical screen in this source-identified holdout, but this is still not evidence of profit or stable future performance."
                if screen_pass else
                "No new directional method is validated by the pre-registered screen in this bounded run. Do not continue searching on this holdout; use a new, independently registered sample if further research is justified."
            ),
        }
        screen["paired_bootstrap"] = bootstrap
        (RESULTS / "primary_comparison.json").write_text(json.dumps(screen, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        anchor_crosscheck = crosscheck.get("counts", {}) if crosscheck else {}
        anchor_label_stats = crosscheck.get("weekly_label_sensitivity", {}) if crosscheck else {}
        report_data_quality = {
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "dataset_status": "SOURCE_GATE_PASS_FOR_DHAN_WINDOW",
            "model_status": "EXPLORATORY_ONLY",
            "dhan_history_manifest": history_manifest,
            "minute_source_quality": minute_quality,
            "official_daily_quality": daily_quality,
            "target_construction": construction,
            "row_source_gate": source_gate,
            "dhan_anchor_crosscheck": {
                "report_status": crosscheck.get("status"),
                "counts": anchor_crosscheck,
                "absolute_difference_points": crosscheck.get("absolute_difference_points"),
                "weekly_label_sensitivity": anchor_label_stats,
                "interpretation": "Cross-check covers the overlapping sessions only; the Dhan source is authenticated, but the public comparison is diagnostic rather than exchange-official ground truth.",
            },
            "weekly_cycles_labelled": int(len(cycles)),
            "binary_rows": int(len(binary)),
            "feature_complete_rows": int(len(model_data)),
            "official_calendar_all_rows_verified": bool(expiry_raw["status"].str.startswith("verified_").all() and contract_ok.all()),
            "daily_feature_source": "official NSE daily OHLC for all historical sessions",
            "target_anchor_source": "authenticated DhanHQ v2 NIFTY 50 INDEX 1-minute open in the 10:00–10:03 IST window",
            "target_close_source": "official NSE daily close on verified actual weekly expiry date",
            "anchor_window_start": actual_first.isoformat(),
            "anchor_window_last_bar": actual_last.isoformat(),
            "raw_dhan_bars_committed": False,
        }
        (RESULTS / "data_quality_report.json").write_text(json.dumps(report_data_quality, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")

        all_summary_metrics = pd.concat([
            development_metrics.assign(stage="development"),
            holdout_metrics.assign(stage="holdout"),
        ], ignore_index=True)
        summary = {
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "plan_version": "1.2",
            "dataset_status": "SOURCE_GATE_PASS_FOR_DHAN_WINDOW",
            "model_result_status": "AUGMENTED_METHOD_PASSED_SCREEN" if screen_pass else "NO_NEW_DIRECTIONAL_METHOD_VALIDATED",
            "dataset_window": {
                "first_anchor": pd.Timestamp(model_data["anchor_date"].iloc[0]).date().isoformat(),
                "last_expiry": pd.Timestamp(model_data["expiry_date"].iloc[-1]).date().isoformat(),
            },
            "total_dhan_bars": int(len(minutes)),
            "weekly_cycles_built": int(len(cycles)),
            "source_gate_rows": int(source_gate["row_source_gate_pass"]),
            "binary_rows": int(len(binary)),
            "feature_complete_rows": int(len(model_data)),
            "development_rows": int(split_idx),
            "holdout_rows": int(len(model_data) - split_idx),
            "minimum_training_history": MIN_HISTORY,
            "split_manifest": "research/results/phase10/phase10_split_manifest.json",
            "selected_baseline": selected_baseline,
            "selected_augmented_candidate": selected_challenger,
            "screening": screen,
            "research_conclusion": screen["interpretation"],
            "future_model_search": "STOPPED_AFTER_REGISTERED_PHASE10_PASS; do not retune the holdout",
            "usable_trading_strategy_validated": False,
            "trading_gate": "BLOCKED: instrument-specific historical fills, options/futures price series, dated Paytm Money charges, bid-ask spreads and slippage stress have not been validated.",
        }
        (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        # Fixed registry records every candidate that was registered and run.
        registry = {
            "plan_version": "1.2",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "candidates": ALL_CANDIDATES,
            "base_features": FEATURE_COLUMNS,
            "added_features": NEW_FEATURES,
            "source_window": summary["dataset_window"],
            "selection": "Development predictions only; one base baseline and one augmented challenger were selected before holdout analysis.",
            "holdout_evaluated_once": True,
            "bootstrap": {"method": "paired moving-block bootstrap", "block_weeks": BOOTSTRAP_BLOCK, "replicates": BOOTSTRAP_REPS, "seed": SEED},
            "not_run": [
                "PySR symbolic-regression search",
                "Quantevolve evolutionary search",
                "TradingAgents multi-agent features",
                "options IV/OI/skew and global/FII/DII inputs because a point-in-time historical feature table is not yet joined",
                "instrument-level futures/options P&L because historical fills and dated Paytm Money costs are not validated",
            ],
            "stop_rule": "Stop after this single fixed-candidate evaluation; do not retune using holdout rankings.",
        }
        (RESULTS / "experiment_registry.json").write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        plot_results(model_data, development_metrics, holdout_metrics, selected_baseline, selected_challenger)
        report_md = render_report(summary, report_data_quality, development_metrics, holdout_metrics, bootstrap,
                                  selected_baseline, selected_challenger, screen)
        (RESULTS / "phase10_report.md").write_text(report_md, encoding="utf-8")
        update_section(MANUSCRIPT, PHASE10_START, PHASE10_END, report_md,
                       before_heading="## References")
        readme_block = (
            "## Phase 10 — Dhan-backed dataset rebuild and method test\n"
            f"- **Dataset gate:** {summary['dataset_status']}; {len(cycles)} source-gated weekly cycles from the Dhan history window.\n"
            f"- **Model outcome:** {summary['model_result_status']}; selected augmented challenger {selected_challenger} vs baseline {selected_baseline}.\n"
            f"- **Holdout comparison:** balanced-accuracy difference {_fmt(ba_diff)}; paired bootstrap status {bootstrap.get('status')}. No strategy is approved for trading.\n"
            "- [Phase 10 plan](docs/PHASE_10_VERIFIED_DATASET.md); [machine-readable summary](research/results/phase10/summary.json); [full report](research/results/phase10/phase10_report.md); [data quality](research/results/phase10/data_quality_report.json); [split manifest](research/results/phase10/phase10_split_manifest.json).\n"
            "- [Rebuilt weekly labels/features](data/processed/phase10_dhan_weekly_labels_features.csv); [development metrics](research/results/phase10/development_metrics.csv); [holdout metrics](research/results/phase10/holdout_metrics.csv); [comparison chart](research/results/phase10/phase10_method_comparison.png).\n"
            "- **Trading acceptance:** BLOCKED until contract-level fills and date-effective Paytm Money fees, bid/ask spreads and slippage are tested.\n"
        )
        update_section(README, README_START, README_END, readme_block, before_heading="## Research approach")

        print(json.dumps({
            "dataset_status": summary["dataset_status"],
            "model_result_status": summary["model_result_status"],
            "dhan_bars": int(len(minutes)),
            "weekly_cycles": int(len(cycles)),
            "feature_complete_rows": int(len(model_data)),
            "development_rows": int(split_idx),
            "holdout_rows": int(len(model_data) - split_idx),
            "selected_baseline": selected_baseline,
            "selected_augmented": selected_challenger,
            "holdout_balanced_accuracy_difference": ba_diff,
            "bootstrap": bootstrap,
            "screen_pass": screen_pass,
        }, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        RESULTS.mkdir(parents=True, exist_ok=True)
        failure = {
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "status": "BLOCKED_REBUILD_OR_EVALUATION_ERROR",
            "error_type": type(exc).__name__,
            "error": " ".join(str(exc).split())[:800],
            "next_action": "Inspect this exact stage, fix the root cause, add a regression test, and rerun once. No model acceptance is implied.",
        }
        (RESULTS / "failure_report.json").write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(failure, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
