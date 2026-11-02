from __future__ import annotations

import gzip
import hashlib
import json
import os
import sys
import time
import traceback
from collections import defaultdict
from datetime import date, timedelta, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import requests
from scipy.stats import norm
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from live_api.app import MASTER_URL, find_nifty50_security
from scripts.constituent_weekly.dhan_equity_preflight import (
    IST, acquire_access_token, apply_historical_security_aliases, request_profile, resolve_ids,
)
from scripts.constituent_weekly.audit_c1_continuous_dhan_coverage import (
    CHUNK_DAYS, SPECIAL_EVENING_ONLY_SESSIONS, build_expiry_cycles, chunk_key, make_chunks,
    request_intraday_window, verified_expiry_dates,
)
from scripts.constituent_weekly.audit_c1_daily_history import (
    decrypt_tejhq_cache_bytes, encrypt_tejhq_cache_bytes, parse_daily_payload,
    request_daily_history, resolve_tejhq_encrypted_cache_dir,
    load_tejhq_nse_year, load_direct_nse_special_cache,
)
from scripts.constituent_weekly.security_identity import point_in_time_symbol

MEMBERSHIP = ROOT / "data/constituent_weekly/nifty50_membership_intervals.csv"
ALIASES = ROOT / "data/constituent_weekly/security_alias_history.csv"
ACTIONS = ROOT / "data/constituent_weekly/security_corporate_action_events.csv"
EXPIRY = ROOT / "data/reconciliation/expiry_verification.csv"
INDEX_DAILY = ROOT / "data/reconciliation/nifty50_official_daily.csv"
OUT_JSON = ROOT / "research/constituent_weekly/C2_MODEL_RESULTS.json"
OUT_MD = ROOT / "research/constituent_weekly/C2_MODEL_RESULTS.md"
OUT_INDEX = ROOT / "research/constituent_weekly/C2_INDEX_OOF_FORECASTS.csv"
OUT_STOCK = ROOT / "research/constituent_weekly/C2_STOCK_OOF_FORECASTS.csv"
OUT_CYCLE = ROOT / "research/constituent_weekly/C2_CYCLE_FEATURE_SUMMARIES.csv"
OUT_PANEL_JSON = ROOT / "research/constituent_weekly/C2_PANEL_BUILD.json"
OUT_PANEL_MD = ROOT / "research/constituent_weekly/C2_PANEL_BUILD.md"

TZ = ZoneInfo(IST)
START_FLOOR = date(2021, 11, 1)
END_CEILING = date(2026, 10, 30)
VERSION = "bup01-c2-panel-v1"
MIN_HISTORY = 104
MIN_META_HISTORY = 26
MIN_MEMBERS = 47
MIN_FRACTION = 0.94
REQUEST_DELAY = 0.30
FEATURES = [
    "ret_1d", "ret_5d", "ret_10d", "ret_20d", "ret_60d",
    "vol_5d", "vol_20d", "vol_60d", "range_10d", "range_20d",
    "gap_1d", "volume_z20", "cs_rank_ret5", "cs_rank_ret20",
]
INDEX_FEATURES = [
    "idx_ret_1d", "idx_ret_5d", "idx_ret_10d", "idx_ret_20d", "idx_ret_60d",
    "idx_vol_10d", "idx_vol_20d", "idx_vol_60d", "idx_range_10d", "idx_range_20d",
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json_report(path: Path, payload: dict) -> None:
    """Write one standards-compliant JSON document with a real trailing newline."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def summarize_cycle_coverage(index_panel: pd.DataFrame, eligible_counts: pd.Series, member_count: dict[int, int]) -> dict:
    """Summarise per-cycle eligible constituent counts without exposing market values."""
    cycle_ids = (
        sorted(index_panel["cycle_idx"].dropna().astype(int).unique().tolist())
        if isinstance(index_panel, pd.DataFrame) and "cycle_idx" in index_panel
        else []
    )
    counts, denominators, passed = [], [], 0
    histogram: dict[str, int] = defaultdict(int)
    for cycle_id in cycle_ids:
        total = int(member_count.get(cycle_id, 0))
        valid = int(eligible_counts.get(cycle_id, 0)) if eligible_counts is not None else 0
        counts.append(valid)
        denominators.append(total)
        histogram[str(valid)] += 1
        if total > 0 and valid >= MIN_MEMBERS and valid / total >= MIN_FRACTION:
            passed += 1
    return {
        "cycles_with_valid_index_targets": len(cycle_ids),
        "cycles_passing_47_94_rule": int(passed),
        "eligible_stock_count_min": int(min(counts)) if counts else 0,
        "eligible_stock_count_median": float(np.median(counts)) if counts else 0.0,
        "eligible_stock_count_max": int(max(counts)) if counts else 0,
        "point_in_time_member_count_min": int(min(denominators)) if denominators else 0,
        "point_in_time_member_count_max": int(max(denominators)) if denominators else 0,
        "eligible_stock_count_histogram": dict(sorted(histogram.items(), key=lambda item: int(item[0]))),
    }


def panel_failure_diagnostics(local_state: dict) -> dict:
    """Collect value-free acquisition and member-coverage diagnostics on a failed build."""
    diagnostics: dict = {}
    cycles = local_state.get("cycles")
    if isinstance(cycles, list):
        diagnostics["scheduled_cycles"] = len(cycles)
    index_panel, stock_panel = local_state.get("idx_panel"), local_state.get("panel")
    if isinstance(index_panel, pd.DataFrame):
        diagnostics["valid_index_target_cycles"] = int(len(index_panel))
    if isinstance(stock_panel, pd.DataFrame):
        diagnostics["constituent_target_rows"] = int(len(stock_panel))
        diagnostics["identity_flagged_rows"] = int(stock_panel.get("identity_review_flag", pd.Series(dtype=int)).sum())
        diagnostics["action_crossing_flagged_rows"] = int(stock_panel.get("action_crossing_flag", pd.Series(dtype=int)).sum())
        if "primary_flag" in stock_panel:
            diagnostics["primary_eligible_stock_rows_before_cycle_gate"] = int(stock_panel["primary_flag"].sum())
    eligible_counts, member_count = local_state.get("eligible_counts"), local_state.get("member_count")
    if isinstance(index_panel, pd.DataFrame) and isinstance(member_count, dict):
        diagnostics["cycle_coverage"] = summarize_cycle_coverage(index_panel, eligible_counts, member_count)
    failures = local_state.get("failures")
    if failures is not None:
        diagnostics["failure_counts"] = {str(k): int(v) for k, v in failures.items()}
    resolved, unresolved = local_state.get("resolved"), local_state.get("unresolved")
    if isinstance(resolved, dict):
        diagnostics["resolved_symbol_count"] = len(resolved)
    if isinstance(unresolved, list):
        diagnostics["unresolved_symbols"] = sorted(str(x) for x in unresolved)
    for name in ("daily_requests", "daily_hits", "intraday_requests", "intraday_hits"):
        if name in local_state:
            diagnostics[name] = int(local_state[name])
    daily_frames = local_state.get("daily_frames")
    if isinstance(daily_frames, dict):
        row_counts = {str(s): (int(len(df)) if isinstance(df, pd.DataFrame) else 0) for s, df in daily_frames.items()}
        diagnostics["daily_symbols_with_at_least_62_rows"] = sum(v >= 62 for v in row_counts.values())
        diagnostics["daily_symbols_with_fewer_than_62_rows"] = sorted(s for s, n in row_counts.items() if n < 62)
    targets, stock_snap = local_state.get("targets"), local_state.get("stock_snap")
    if isinstance(targets, dict) and isinstance(stock_snap, dict):
        by_symbol = {}
        for symbol, requested in sorted(targets.items()):
            saved = stock_snap.get(symbol, {})
            anchors, expiries = requested.get("anchor", set()), requested.get("expiry", set())
            by_symbol[str(symbol)] = {
                "anchor_required": int(len(anchors)),
                "anchor_valid": int(sum(bool(saved.get(day, {}).get("anchor_ok")) for day in anchors)),
                "expiry_required": int(len(expiries)),
                "expiry_valid": int(sum(bool(saved.get(day, {}).get("expiry_ok")) for day in expiries)),
            }
        diagnostics["stock_intraday_target_coverage_by_symbol"] = by_symbol
    index_snap = local_state.get("index_snap")
    if isinstance(index_snap, dict):
        anchors, expiries = local_state.get("idx_a", set()), local_state.get("idx_e", set())
        diagnostics["index_intraday_target_coverage"] = {
            "anchor_required": int(len(anchors)),
            "anchor_valid": int(sum(bool(index_snap.get(day, {}).get("anchor_ok")) for day in anchors)),
            "expiry_required": int(len(expiries)),
            "expiry_valid": int(sum(bool(index_snap.get(day, {}).get("expiry_ok")) for day in expiries)),
        }
    return diagnostics


def cache_file(cache_dir: Path, family: str, key: str) -> Path:
    digest = hashlib.sha256(key.encode()).hexdigest()[:28]
    path = cache_dir / "c2" / family / f"{digest}.aesgcm"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def read_cache(path: Path, token: str, aad: bytes) -> bytes | None:
    if not path.is_file():
        return None
    try:
        return decrypt_tejhq_cache_bytes(path.read_bytes(), token, aad)
    except Exception:
        path.unlink(missing_ok=True)
        return None


def write_cache(path: Path, payload: bytes, token: str, aad: bytes) -> None:
    temp = path.with_suffix(".tmp")
    temp.write_bytes(encrypt_tejhq_cache_bytes(payload, token, aad))
    temp.replace(path)


def arrays_from_body(body: object, require_volume: bool) -> dict | None:
    if not isinstance(body, dict) or str(body.get("status", "")).casefold() == "failure":
        return None
    payload = body.get("data") if isinstance(body.get("data"), dict) else body
    ts = payload.get("timestamp", payload.get("start_Time", payload.get("startTime")))
    arrays = {
        "timestamp": ts, "open": payload.get("open"), "high": payload.get("high"),
        "low": payload.get("low"), "close": payload.get("close"), "volume": payload.get("volume"),
    }
    if any(not isinstance(arrays[k], list) for k in ("timestamp", "open", "high", "low", "close")):
        return None
    if len({len(arrays[k]) for k in ("timestamp", "open", "high", "low", "close")}) != 1:
        return None
    n = len(arrays["timestamp"])
    if n == 0:
        return None
    if require_volume and (not isinstance(arrays["volume"], list) or len(arrays["volume"]) != n):
        return None
    if isinstance(arrays["volume"], list) and len(arrays["volume"]) != n:
        arrays["volume"] = None
    return arrays


def ohlc_valid(frame: pd.DataFrame, require_volume: bool) -> bool:
    if frame.empty:
        return False
    values = frame[["open", "high", "low", "close"]].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values <= 0).any():
        return False
    if (frame["high"] < frame["low"]).any():
        return False
    if (frame["low"] > frame[["open", "close"]].min(axis=1)).any():
        return False
    if (frame["high"] < frame[["open", "close"]].max(axis=1)).any():
        return False
    if require_volume and (frame["volume"].isna().any() or (frame["volume"] < 0).any()):
        return False
    return True


def parse_target_bars(body: object, anchor_dates: set[str], expiry_dates: set[str], require_volume: bool) -> dict:
    requested = anchor_dates | expiry_dates
    arrays = arrays_from_body(body, require_volume)
    if arrays is None:
        return {d: {"anchor_ok": False, "expiry_ok": False, "status": "INVALID_OR_EMPTY_RESPONSE"} for d in requested}
    frame = pd.DataFrame({
        "timestamp": pd.to_datetime(arrays["timestamp"], unit="s", utc=True, errors="coerce"),
        "open": pd.to_numeric(arrays["open"], errors="coerce"),
        "high": pd.to_numeric(arrays["high"], errors="coerce"),
        "low": pd.to_numeric(arrays["low"], errors="coerce"),
        "close": pd.to_numeric(arrays["close"], errors="coerce"),
    })
    frame["volume"] = pd.to_numeric(arrays["volume"], errors="coerce") if isinstance(arrays["volume"], list) else np.nan
    frame = frame.dropna(subset=["timestamp"]).copy()
    frame["timestamp"] = frame["timestamp"].dt.tz_convert(TZ)
    frame = frame.sort_values("timestamp")
    frame["day"] = frame["timestamp"].dt.strftime("%Y-%m-%d")
    frame["clock"] = frame["timestamp"].dt.strftime("%H:%M")
    result = {}
    for day in requested:
        day_rows = frame.loc[frame["day"].eq(day)]
        anchors = day_rows.loc[day_rows["clock"].between("10:00", "10:03", inclusive="both")]
        closes = day_rows.loc[day_rows["clock"].between("15:00", "15:14", inclusive="both")]
        a_ok = day in anchor_dates and len(anchors) > 0 and not anchors["timestamp"].duplicated().any() and ohlc_valid(anchors, require_volume)
        e_ok = day in expiry_dates and len(closes) > 0 and not closes["timestamp"].duplicated().any() and ohlc_valid(closes, require_volume)
        result[day] = {
            "anchor_ok": bool(a_ok), "anchor_open": float(anchors.iloc[0]["open"]) if a_ok else None,
            "anchor_time": anchors.iloc[0]["timestamp"].isoformat() if a_ok else None,
            "expiry_ok": bool(e_ok), "expiry_close": float(closes.iloc[-1]["close"]) if e_ok else None,
            "expiry_time": closes.iloc[-1]["timestamp"].isoformat() if e_ok else None,
            "status": "PASS" if ((day not in anchor_dates or a_ok) and (day not in expiry_dates or e_ok)) else "TARGET_GAP",
        }
    return result


def fetch_intraday_snapshot(symbol: str, sid: str, segment: str, instrument: str, chunk: dict,
                            anchors: set[str], expiries: set[str], token: str, client_id: str,
                            cache_dir: Path, manifest_hash: str, is_index: bool) -> tuple[dict, bool, int]:
    family = "index" if is_index else "stocks"
    key = f"{VERSION}|{manifest_hash}|{symbol}|{sid}|{chunk['from']}|{chunk['to']}"
    aad = key.encode()
    path = cache_file(cache_dir, f"intraday_{family}", key)
    raw = read_cache(path, token, aad)
    if raw is not None:
        try:
            saved = json.loads(gzip.decompress(raw).decode())
            complete = all(
                d in saved and (d not in anchors or saved[d].get("anchor_ok")) and
                (d not in expiries or saved[d].get("expiry_ok"))
                for d in (anchors | expiries)
            )
            if complete:
                return saved, True, 0
        except Exception:
            pass
    body, attempts = request_intraday_window(
        sid, segment, instrument, token, client_id, chunk["from"], chunk["to"]
    )
    saved = parse_target_bars(body, anchors, expiries, require_volume=not is_index)
    complete = bool(saved) and all(
        (d not in anchors or saved[d].get("anchor_ok")) and
        (d not in expiries or saved[d].get("expiry_ok"))
        for d in (anchors | expiries)
    )
    if complete:
        write_cache(path, gzip.compress(json.dumps(saved, separators=(",", ":")).encode()), token, aad)
    return saved, False, attempts


def fetch_daily(symbol: str, sid: str, token: str, client_id: str, cache_dir: Path,
                manifest_hash: str, from_date: str, to_date: str) -> tuple[pd.DataFrame | None, bool, int, str | None]:
    key = f"{VERSION}|daily|{manifest_hash}|{symbol}|{sid}|{from_date}|{to_date}"
    aad = key.encode()
    path = cache_file(cache_dir, "daily", key)
    raw = read_cache(path, token, aad)
    if raw is not None:
        try:
            body = json.loads(gzip.decompress(raw).decode())
            frame, err = parse_daily_payload(body)
            if frame is not None and not frame.empty and err is None:
                return frame, True, 0, None
        except Exception:
            pass
    body, attempts = request_daily_history(sid, token, client_id, from_date, to_date)
    frame, err = parse_daily_payload(body)
    if frame is not None and not frame.empty and err is None:
        write_cache(path, gzip.compress(json.dumps(body, separators=(",", ":")).encode()), token, aad)
        return frame, False, attempts, None
    status = err or (body.get("status") if isinstance(body, dict) else "INVALID_RESPONSE")
    if isinstance(body, dict):
        nested = body.get("data")
        shape = {
            "status": str(body.get("status", "NO_STATUS"))[:40],
            "top_keys": sorted(str(k) for k in body.keys())[:20],
            "data_type": type(nested).__name__,
            "data_keys": sorted(str(k) for k in nested.keys())[:20] if isinstance(nested, dict) else [],
            "array_lengths": {
                key: len(nested.get(key)) for key in ("timestamp", "start_Time", "start_time", "open", "high", "low", "close", "volume")
                if isinstance(nested, dict) and isinstance(nested.get(key), list)
            },
        }
    else:
        shape = {"body_type": type(body).__name__}
    return None, False, attempts, f"{status}|shape={json.dumps(shape, sort_keys=True)}"


def stock_features(frame: pd.DataFrame | None, asof: str) -> dict | None:
    if frame is None or frame.empty:
        return None
    data = frame.loc[frame["session_date"].astype(str) < asof].sort_values("session_date").copy()
    if len(data) < 62:
        return None
    for c in ("open", "high", "low", "close", "volume"):
        data[c] = pd.to_numeric(data[c], errors="coerce")
    data = data.dropna(subset=["open", "high", "low", "close"])
    close = data["close"]
    returns = close.pct_change()
    out = {}
    for h in (1, 5, 10, 20, 60):
        out[f"ret_{h}d"] = float(close.iloc[-1] / close.iloc[-(h + 1)] - 1)
    for h in (5, 20, 60):
        out[f"vol_{h}d"] = float(returns.dropna().tail(h).std(ddof=1))
    for h in (10, 20):
        out[f"range_{h}d"] = float(((data["high"] - data["low"]) / data["close"]).tail(h).mean())
    out["gap_1d"] = float(data["open"].iloc[-1] / close.iloc[-2] - 1) if close.iloc[-2] else np.nan
    vol = pd.to_numeric(data["volume"], errors="coerce").dropna()
    logs = np.log1p(vol.tail(21))
    out["volume_z20"] = float((logs.iloc[-1] - logs.iloc[:-1].mean()) / (logs.iloc[:-1].std(ddof=1) + 1e-12)) if len(logs) >= 20 else np.nan
    return out if np.isfinite(list(out.values())).all() else None


def index_features(frame: pd.DataFrame, asof: str) -> dict | None:
    data = frame.copy()
    data["session_date"] = pd.to_datetime(data["session_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    data = data.loc[data["session_date"] < asof].sort_values("session_date")
    if len(data) < 62:
        return None
    columns = {str(c).casefold(): c for c in data.columns}
    close_col = columns.get("close") or columns.get("official_close")
    high_col = columns.get("high") or columns.get("official_high")
    low_col = columns.get("low") or columns.get("official_low")
    if not all((close_col, high_col, low_col)):
        raise ValueError("NIFTY daily file must provide close/high/low or official_close/official_high/official_low.")
    close = pd.to_numeric(data[close_col], errors="coerce")
    high = pd.to_numeric(data[high_col], errors="coerce")
    low = pd.to_numeric(data[low_col], errors="coerce")
    rets = close.pct_change()
    out = {}
    for h in (1, 5, 10, 20, 60):
        out[f"idx_ret_{h}d"] = float(close.iloc[-1] / close.iloc[-(h + 1)] - 1)
    for h in (10, 20, 60):
        out[f"idx_vol_{h}d"] = float(rets.dropna().tail(h).std(ddof=1))
    for h in (10, 20):
        out[f"idx_range_{h}d"] = float(((high - low) / close).tail(h).mean())
    return out if np.isfinite(list(out.values())).all() else None


def event_flags(symbol: str, anchor: str, expiry: str, events: pd.DataFrame) -> tuple[int, int]:
    identity = int(symbol in {"HDFC", "TATAMOTORS"})
    crossing = 0
    for row in events.itertuples(index=False):
        day = str(row.event_date)[:10]
        if symbol in set(str(row.affected_symbols).split(";")) and anchor < day <= expiry:
            crossing = 1
    return identity, crossing


def classifier(name: str) -> Pipeline:
    if name == "logistic":
        return Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("model", LogisticRegression(C=0.5, max_iter=2000, class_weight="balanced")),
        ])
    return Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("model", ExtraTreesClassifier(n_estimators=120, max_depth=8, min_samples_leaf=15,
                                       max_features=0.85, class_weight="balanced",
                                       random_state=20261102, n_jobs=-1)),
    ])


def regressor() -> Pipeline:
    return Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("model", ExtraTreesRegressor(n_estimators=100, max_depth=8, min_samples_leaf=20,
                                      max_features=0.85, random_state=20261103, n_jobs=-1)),
    ])


def equal_cycle_weights(cycle_ids: pd.Series) -> np.ndarray:
    counts = cycle_ids.value_counts()
    w = cycle_ids.map(lambda c: 1.0 / counts.loc[c]).to_numpy(float)
    return w / np.mean(w)


def metrics(y: np.ndarray, p: np.ndarray) -> dict:
    if len(y) == 0:
        return {"n": 0}
    pred = (p >= 0.5).astype(int)
    return {
        "n": int(len(y)), "accuracy": float(accuracy_score(y, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "roc_auc": float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None,
        "brier": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, np.clip(p, 1e-6, 1 - 1e-6), labels=[0, 1])),
        "up_fraction": float(np.mean(y)),
    }


def wilson_ci(k: int, n: int) -> list[float] | None:
    if not n:
        return None
    z = float(norm.ppf(0.975))
    ph = k / n
    den = 1 + z * z / n
    centre = (ph + z * z / (2 * n)) / den
    half = z * np.sqrt((ph * (1 - ph) + z * z / (4 * n)) / n) / den
    return [float(max(0, centre - half)), float(min(1, centre + half))]


def block_bootstrap_accuracy(frame: pd.DataFrame, y_col: str, p_col: str, n_boot: int = 1000) -> list[float] | None:
    groups = [g for _, g in frame.groupby("cycle_idx", sort=True)]
    if len(groups) < 5:
        return None
    rng = np.random.default_rng(20261102)
    vals = []
    for _ in range(n_boot):
        ix = rng.integers(0, len(groups), len(groups))
        sample = pd.concat([groups[i] for i in ix], ignore_index=True)
        vals.append(float(np.mean((sample[p_col].to_numpy() >= 0.5) == sample[y_col].to_numpy())))
    return [float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975))]


def write_report(result: dict) -> None:
    p = result.get("panel", {})
    a = result.get("data_acquisition", {})
    lines = [
        "# C2 Constituent Panel and Walk-Forward Model Results", "",
        f"**Updated:** {result.get('created_at_utc')}",
        f"**Status:** {result.get('status')}", "",
        "## Data build", "",
        f"- Scheduled weekly cycles: {p.get('scheduled_cycles', 'not built')}",
        f"- Index target rows: {p.get('index_target_rows', 'not built')}",
        f"- Constituent target rows: {p.get('constituent_target_rows', 'not built')}",
        f"- Primary eligible rows / cycles: {p.get('primary_eligible_stock_rows', 'not built')} / {p.get('primary_eligible_cycles', 'not built')}",
        f"- Stock-level OOF cycles: {p.get('stock_oof_cycles', 'not run')}",
        f"- Index meta-model OOF cycles: {p.get('meta_oof_cycles', 'not run')}",
        f"- Encrypted intraday cache hits / requests: {a.get('intraday_encrypted_cache_hits', 0)} / {a.get('intraday_requests', 0)}",
        f"- Encrypted daily cache hits / requests: {a.get('daily_encrypted_cache_hits', 0)} / {a.get('daily_requests', 0)}",
        "", "## Stock-level results", "",
    ]
    for name, m in result.get("stock_models", {}).items():
        lines += [
            f"### {name}", "",
            f"- Accuracy: {m.get('accuracy')}; balanced accuracy: {m.get('balanced_accuracy')}",
            f"- ROC AUC: {m.get('roc_auc')}; Brier: {m.get('brier')}",
            f"- Five-day momentum baseline accuracy: {m.get('momentum_baseline', {}).get('accuracy')}", "",
        ]
    lines += ["## NIFTY 50 direction results", ""]
    for name, bundle in result.get("index_models", {}).get("meta_models", {}).items():
        if "all_oof" not in bundle:
            continue
        for section in ("all_oof", "development", "final_holdout"):
            m = bundle.get(section, {})
            lines.append(f"- {name} — {section}: accuracy {m.get('accuracy')}; balanced accuracy {m.get('balanced_accuracy')}; AUC {m.get('roc_auc')}; Brier {m.get('brier')}")
        lines.append(f"- {name} — final holdout Wilson 95% accuracy CI: {bundle.get('final_holdout', {}).get('accuracy_wilson_95')}")
        lines.append(f"- {name} — final holdout cycle-block bootstrap 95% accuracy CI: {bundle.get('final_holdout', {}).get('cycle_block_bootstrap_accuracy_95')}")
        lines.append("")
    lines += ["## Limitations", ""]
    lines += [f"- {x}" for x in result.get("limitations", [])]
    lines += [
        "- The final holdout is a chronological tail and must not be repeatedly used for model tuning.",
        "- Model forecasts are not a trading strategy; no options/futures fills, Paytm Money brokerage, statutory levies, spreads or slippage are tested.",
        "- Raw price levels and provider payloads remain in the AES-GCM encrypted Actions cache; only labels, model forecasts and aggregate results are published.",
        "", "## Reproducibility", "",
        f"- Input manifest hash: {result.get('input_manifest', {}).get('hash')}",
        "- Execution script: scripts/constituent_weekly/run_c2_panel_and_models.py",
        "- Workflow: .github/workflows/bup01-c2-constituent-panel.yml",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    started = time.monotonic()
    result = {
        "schema_version": 1, "methodology_version": VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(), "status": "IN_PROGRESS",
        "auth_method": None, "token_refresh_status": None, "input_manifest": {},
        "data_acquisition": {}, "panel": {}, "stock_models": {}, "index_models": {},
        "limitations": [
            "The user explicitly waived the remaining historical identity and corporate-action checks as preconditions. This is a scope decision, not a claim that those checks passed.",
            "No unverified corporate-action factor is applied; unadjusted event-exposed rows are flagged and excluded from the primary sensitivity panel.",
            "The expiry target is the latest valid 15:00-15:14 one-minute candle close, treated as a 15:15 proxy, not the official 15:30 close.",
            "No executable options/futures P&L or transaction-cost simulation is performed in C2.",
        ],
    }
    try:
        token, client_id, auth_method, refresh_status, _auth_diag = acquire_access_token()
        result["auth_method"], result["token_refresh_status"] = auth_method, refresh_status
        profile = request_profile(token)
        if not profile.ok or str(profile.json().get("dataPlan", "")).casefold() != "active":
            raise RuntimeError("Dhan profile/data-plan authorization check failed.")
        hf_token = os.environ.get("HF_TOKEN", "").strip()
        if not hf_token:
            raise RuntimeError("HF_TOKEN is required for encrypted C2 cache persistence.")
        cache_dir = resolve_tejhq_encrypted_cache_dir(os.environ.get(
            "BUP01_ENCRYPTED_CACHE_DIR", str(Path.home() / ".cache" / "bup01-tejhq-encrypted")
        ))

        membership = pd.read_csv(MEMBERSHIP, low_memory=False)
        expiry_frame = pd.read_csv(EXPIRY, low_memory=False)
        index_daily = pd.read_csv(INDEX_DAILY, low_memory=False)
        sessions = sorted(pd.to_datetime(index_daily["session_date"], errors="coerce").dropna().dt.strftime("%Y-%m-%d").unique())
        expiries = verified_expiry_dates(expiry_frame)
        cycles = build_expiry_cycles(
            expiries, sessions, membership, START_FLOOR.isoformat(), END_CEILING.isoformat(),
            SPECIAL_EVENING_ONLY_SESSIONS,
        )
        if len(cycles) < MIN_HISTORY + 1:
            raise RuntimeError(f"Only {len(cycles)} verified expiry cycles were built.")

        master_response = requests.get(MASTER_URL, timeout=45)
        master_response.raise_for_status()
        master_bytes = master_response.content
        master = pd.read_csv(pd.io.common.BytesIO(master_bytes), low_memory=False)
        index_sid = find_nifty50_security(master)
        all_symbols = sorted({s for c in cycles for s in c["members"]})
        resolved = resolve_ids(master, all_symbols)
        resolved = apply_historical_security_aliases(all_symbols, resolved, resolve_ids(master, ["TMPV"]))
        unresolved = sorted(set(all_symbols) - set(resolved))
        if not index_sid:
            raise RuntimeError("NIFTY 50 index security ID was not resolved.")

        manifest = {
            "membership_sha256": sha256(MEMBERSHIP.read_bytes()),
            "expiry_sha256": sha256(EXPIRY.read_bytes()),
            "index_daily_sha256": sha256(INDEX_DAILY.read_bytes()),
            "alias_sha256": sha256(ALIASES.read_bytes()),
            "action_event_sha256": sha256(ACTIONS.read_bytes()),
            "scrip_master_sha256": sha256(master_bytes),
            "first_anchor": min(c["anchor_date"] for c in cycles),
            "last_expiry": max(c["expiry_date"] for c in cycles),
            "cycle_count": len(cycles), "symbol_count": len(all_symbols),
        }
        manifest_hash = sha256(json.dumps(manifest, sort_keys=True).encode())
        result["input_manifest"] = {**manifest, "hash": manifest_hash}

        # Reuse the same pinned, independently audited NSE EOD source as C1.
        # Dhan's daily-history payload shape changed and returned no arrays for all
        # 62 symbols; repeating those requests would waste time and discard C1's
        # already validated 100% composite coverage. Restore the C1 encrypted
        # partition cache first, then download only missing yearly partitions.
        if os.environ.get("TEJHQ_PERSONAL_USE_ONLY") != "1":
            raise RuntimeError("TEJHQ_PERSONAL_USE_ONLY=1 is required for this personal-use dataset.")
        daily_frames = {}
        daily_hits = daily_requests = 0
        years = range(2018, date.fromisoformat(manifest["last_expiry"]).year + 1)
        yearly_frames = []
        yearly_audit = []
        for year in years:
            year_frame, year_meta = load_tejhq_nse_year(year, hf_token, cache_dir)
            yearly_frames.append(year_frame)
            yearly_audit.append({
                "year": int(year), "cache_hit": bool(year_meta.get("encrypted_cache_hit")),
                "raw_file_sha256": year_meta.get("raw_file_sha256"),
                "dataset_revision": year_meta.get("dataset_revision"),
            })
            daily_hits += int(bool(year_meta.get("encrypted_cache_hit")))
            daily_requests += int(not bool(year_meta.get("encrypted_cache_hit")))
            print(f"C2_DAILY_PARTITION {year} {'CACHE_HIT' if year_meta.get('encrypted_cache_hit') else 'DOWNLOADED'}")
        all_daily = pd.concat(yearly_frames, ignore_index=True) if yearly_frames else pd.DataFrame()
        if all_daily.empty:
            raise RuntimeError("Pinned NSE EOD partitions returned no daily rows.")
        all_daily["symbol"] = all_daily["symbol"].astype(str).str.strip().str.upper()
        all_daily["series"] = all_daily["series"].astype(str).str.strip().str.upper()
        all_daily["session_date"] = pd.to_datetime(all_daily["date"], errors="coerce").dt.strftime("%Y-%m-%d")
        for col in ("open", "high", "low", "close", "volume"):
            all_daily[col] = pd.to_numeric(all_daily[col], errors="coerce")
        all_daily = all_daily.loc[
            all_daily["symbol"].isin(set(all_symbols)) & all_daily["series"].eq("EQ")
        ].copy()
        direct_daily, direct_meta = load_direct_nse_special_cache(hf_token, cache_dir)
        if not direct_daily.empty:
            direct_daily = direct_daily.loc[
                direct_daily["symbol"].isin(set(all_symbols)) & direct_daily["series"].eq("EQ")
            ].copy()
            all_daily = pd.concat([all_daily, direct_daily], ignore_index=True)
        all_daily = all_daily.dropna(subset=["session_date"])
        all_daily = all_daily.sort_values(["symbol", "session_date"]).drop_duplicates(
            subset=["symbol", "session_date"], keep="last"
        )
        for n, symbol in enumerate(all_symbols, 1):
            frame = all_daily.loc[all_daily["symbol"].eq(symbol)].copy()
            if frame.empty:
                daily_frames[symbol] = None
                status = "NO_NSE_EQ_ROWS"
            else:
                daily_frames[symbol] = frame[["session_date", "open", "high", "low", "close", "volume"]].copy()
                status = f"PASS_{len(frame)}_ROWS"
            print(f"C2_DAILY {n}/{len(all_symbols)} {symbol} {status}")

        chunks = make_chunks(manifest["first_anchor"], manifest["last_expiry"], CHUNK_DAYS)
        date_chunk = {}
        for ch in chunks:
            for d in pd.date_range(ch["from"], ch["to"], freq="D").strftime("%Y-%m-%d"):
                date_chunk[d] = chunk_key(ch)
        idx_a = {c["anchor_date"] for c in cycles}
        idx_e = {c["expiry_date"] for c in cycles}
        targets = defaultdict(lambda: {"anchor": set(), "expiry": set()})
        for c in cycles:
            for s in c["members"]:
                targets[s]["anchor"].add(c["anchor_date"])
                targets[s]["expiry"].add(c["expiry_date"])

        index_snap, stock_snap = {}, defaultdict(dict)
        intraday_requests = intraday_hits = 0
        for n, ch in enumerate(chunks, 1):
            ca = {d for d in idx_a if date_chunk[d] == chunk_key(ch)}
            ce = {d for d in idx_e if date_chunk[d] == chunk_key(ch)}
            if ca or ce:
                saved, hit, attempts = fetch_intraday_snapshot(
                    "NIFTY50", str(index_sid), "IDX_I", "INDEX", ch, ca, ce,
                    token, client_id, cache_dir, manifest_hash, True,
                )
                index_snap.update(saved)
                intraday_hits += int(hit)
                intraday_requests += attempts
            for symbol, req in sorted(targets.items()):
                sa = {d for d in req["anchor"] if date_chunk[d] == chunk_key(ch)}
                se = {d for d in req["expiry"] if date_chunk[d] == chunk_key(ch)}
                if not (sa or se) or symbol not in resolved:
                    continue
                saved, hit, attempts = fetch_intraday_snapshot(
                    symbol, str(resolved[symbol]), "NSE_EQ", "EQUITY", ch, sa, se,
                    token, client_id, cache_dir, manifest_hash, False,
                )
                stock_snap[symbol].update(saved)
                intraday_hits += int(hit)
                intraday_requests += attempts
                if attempts:
                    time.sleep(REQUEST_DELAY)
            print(f"C2_INTRADAY {n}/{len(chunks)} cached={intraday_hits} requests={intraday_requests}")

        events = pd.read_csv(ACTIONS, dtype=str, keep_default_na=False)
        stock_rows, index_rows, failures = [], [], defaultdict(int)
        for cycle_idx, c in enumerate(cycles):
            aa, ee = index_snap.get(c["anchor_date"], {}), index_snap.get(c["expiry_date"], {})
            if not (aa.get("anchor_ok") and ee.get("expiry_ok")):
                failures["index_target_missing"] += 1
                continue
            iret = float(ee["expiry_close"] / aa["anchor_open"] - 1)
            ilabel = 1 if iret > 0 else (0 if iret < 0 else None)
            if ilabel is None:
                failures["flat_index_label"] += 1
                if os.environ.get("C2_PANEL_ONLY") != "1":
                    continue
            ix = index_features(index_daily, c["anchor_date"])
            if ix is None:
                failures["index_daily_features_missing"] += 1
                continue
            index_rows.append({
                "cycle_idx": cycle_idx, "previous_expiry": c["previous_expiry"],
                "anchor_date": c["anchor_date"], "expiry_date": c["expiry_date"],
                "index_return": iret, "index_label": ilabel, **ix,
            })
            for symbol in c["members"]:
                aa_s = stock_snap.get(symbol, {}).get(c["anchor_date"], {})
                ee_s = stock_snap.get(symbol, {}).get(c["expiry_date"], {})
                if not (aa_s.get("anchor_ok") and ee_s.get("expiry_ok")):
                    failures["stock_target_missing"] += 1
                    continue
                sf = stock_features(daily_frames.get(symbol), c["anchor_date"])
                if sf is None:
                    failures["stock_daily_features_missing"] += 1
                    continue
                ret = float(ee_s["expiry_close"] / aa_s["anchor_open"] - 1)
                label = 1 if ret > 0 else (0 if ret < 0 else None)
                identity_flag, action_flag = event_flags(symbol, c["anchor_date"], c["expiry_date"], events)
                stock_rows.append({
                    "cycle_idx": cycle_idx, "previous_expiry": c["previous_expiry"],
                    "anchor_date": c["anchor_date"], "expiry_date": c["expiry_date"],
                    "symbol": symbol, "point_in_time_symbol": point_in_time_symbol(symbol, c["anchor_date"], ALIASES),
                    "stock_return": ret, "stock_label": label,
                    "identity_review_flag": identity_flag, "action_crossing_flag": action_flag,
                    **sf,
                })

        panel = pd.DataFrame(stock_rows)
        idx_panel = pd.DataFrame(index_rows)
        if panel.empty or idx_panel.empty:
            raise RuntimeError("No usable constituent/index target observations.")
        panel["cs_rank_ret5"] = panel.groupby("cycle_idx")["ret_5d"].rank(pct=True)
        panel["cs_rank_ret20"] = panel.groupby("cycle_idx")["ret_20d"].rank(pct=True)
        panel["primary_flag"] = panel["identity_review_flag"].eq(0) & panel["action_crossing_flag"].eq(0)
        panel["stock_label"] = pd.to_numeric(panel["stock_label"], errors="coerce")
        idx_panel["index_label"] = pd.to_numeric(idx_panel["index_label"], errors="coerce")

        # Keep the full exploratory rows in the encrypted cache; primary model excludes flagged identity/action rows.
        member_count = {i: len(c["members"]) for i, c in enumerate(cycles)}
        eligible_counts = panel.loc[panel["primary_flag"]].groupby("cycle_idx").size()
        accepted = set()
        for cycle_id in idx_panel["cycle_idx"].astype(int):
            count = int(eligible_counts.get(cycle_id, 0))
            total = member_count[cycle_id]
            if count >= MIN_MEMBERS and count / total >= MIN_FRACTION:
                accepted.add(cycle_id)
        primary = panel.loc[panel["primary_flag"] & panel["cycle_idx"].isin(accepted)].copy()
        primary = primary.dropna(subset=["stock_label"])
        idx_primary = idx_panel.loc[idx_panel["cycle_idx"].isin(accepted)].sort_values("cycle_idx").copy()
        order = sorted(accepted)
        panel_only = os.environ.get("C2_PANEL_ONLY") == "1"
        minimum_cycles = MIN_HISTORY + 1 if panel_only else MIN_HISTORY + MIN_META_HISTORY + 1
        if len(order) < minimum_cycles:
            raise RuntimeError(f"Only {len(order)} cycles meet 47/94% after flagged rows are excluded; {minimum_cycles} required.")

        if panel_only:
            if panel.duplicated(subset=["cycle_idx", "symbol"]).any():
                raise RuntimeError("Duplicate constituent-cycle rows found.")
            if idx_panel.duplicated(subset=["cycle_idx"]).any():
                raise RuntimeError("Duplicate NIFTY target cycle rows found.")
            index_target_fraction = len(idx_panel) / max(1, len(cycles))
            if index_target_fraction < 0.98:
                raise RuntimeError(f"NIFTY target coverage is {index_target_fraction:.4%}; minimum is 98%.")
            holdout_index = max(1, int(np.floor(0.80 * len(order))))
            holdout_cycle = order[holdout_index] if holdout_index < len(order) else order[-1]
            holdout_info = cycles[holdout_cycle]
            stock_key = f"{VERSION}|frozen_panel|{manifest_hash}|stock"
            index_key = f"{VERSION}|frozen_panel|{manifest_hash}|index"
            stock_aad, index_aad = stock_key.encode(), index_key.encode()
            stock_bytes = gzip.compress(panel.sort_values(["cycle_idx", "symbol"]).to_csv(index=False).encode("utf-8"))
            index_bytes = gzip.compress(idx_panel.sort_values("cycle_idx").to_csv(index=False).encode("utf-8"))
            stock_path = cache_file(cache_dir, "frozen_panel", stock_key)
            index_path = cache_file(cache_dir, "frozen_panel", index_key)
            # Frozen-panel encryption must use the stable HF_TOKEN-derived key.
            # The Dhan access token is rotated and is only for source API/cache requests.
            write_cache(stock_path, stock_bytes, hf_token, stock_aad)
            write_cache(index_path, index_bytes, hf_token, index_aad)
            panel_result = {
                "schema_version": 1,
                "status": "COMPLETED",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "methodology_version": VERSION,
                "input_manifest": {**manifest, "hash": manifest_hash},
                "acceptance": {
                    "scheduled_cycles": int(len(cycles)),
                    "valid_index_target_cycles": int(len(idx_panel)),
                    "valid_index_target_fraction": float(index_target_fraction),
                    "minimum_index_target_fraction": 0.98,
                    "primary_eligible_cycles": int(len(order)),
                    "cycles_for_first_C3_confirmatory_forecast": int(MIN_HISTORY + 1),
                    "stock_member_rule": "at least 47 valid; at least 94% of point-in-time tradable members",
                    "holdout_fraction": 0.20,
                    "holdout_boundary_cycle_idx": int(holdout_cycle),
                    "holdout_boundary_anchor_date": holdout_info["anchor_date"],
                    "holdout_boundary_expiry_date": holdout_info["expiry_date"],
                    "duplicate_constituent_cycle_rows": 0,
                    "duplicate_index_cycle_rows": 0,
                },
                "panel": {
                    "constituent_rows": int(len(panel)),
                    "primary_flagged_rows": int((~panel["primary_flag"]).sum()),
                    "identity_flagged_rows": int(panel["identity_review_flag"].sum()),
                    "known_action_crossing_rows": int(panel["action_crossing_flag"].sum()),
                    "stock_flat_labels": int(panel["stock_label"].isna().sum()),
                    "index_flat_labels": int(idx_panel["index_label"].isna().sum()),
                    "index_rows": int(len(idx_panel)),
                    "accepted_cycles_after_primary_sensitivity": int(len(order)),
                    "symbols": int(panel["symbol"].nunique()),
                    "feature_columns": FEATURES + ["cs_rank_ret5", "cs_rank_ret20"],
                    "index_feature_columns": INDEX_FEATURES,
                    "failure_counts": dict(failures),
                },
                "encrypted_panel_cache": {
                    "stock": {
                        "cache_relative_path": str(stock_path.relative_to(cache_dir)),
                        "ciphertext_sha256": sha256(stock_path.read_bytes()),
                        "ciphertext_bytes": int(stock_path.stat().st_size),
                    },
                    "index": {
                        "cache_relative_path": str(index_path.relative_to(cache_dir)),
                        "ciphertext_sha256": sha256(index_path.read_bytes()),
                        "ciphertext_bytes": int(index_path.stat().st_size),
                    },
                    "encryption": "AES-GCM; HF_TOKEN-derived BUP01 cache key; raw values not published",
                },
                "limitations": [
                    "The user waived remaining historical identity and event-level action checks as progression preconditions; this does not certify those checks as passed.",
                    "No unverified corporate-action adjustment is applied. Identity/action flags remain in the encrypted panel.",
                    "The full row-level panel and all price/feature values remain only in the encrypted Actions cache.",
                    "No model fitting occurs in formal C2; stock models belong to C3 and index aggregation belongs to C4.",
                ],
            }
            OUT_PANEL_JSON.parent.mkdir(parents=True, exist_ok=True)
            write_json_report(OUT_PANEL_JSON, panel_result)
            lines = [
                "# C2 Point-in-Time Constituent Panel Build", "",
                f"**Status:** {panel_result['status']}", "",
                f"- Scheduled expiry cycles: {len(cycles)}",
                f"- Valid NIFTY index targets: {len(idx_panel)} ({index_target_fraction:.2%})",
                f"- Constituent-cycle rows: {len(panel)}",
                f"- Distinct symbols: {panel['symbol'].nunique()}",
                f"- Primary eligible cycles: {len(order)}",
                f"- Identity-flagged rows: {int(panel['identity_review_flag'].sum())}",
                f"- Known action-crossing rows: {int(panel['action_crossing_flag'].sum())}",
                f"- Holdout boundary: {holdout_info['anchor_date']} to {holdout_info['expiry_date']}",
                "- Full panel and prices: AES-GCM encrypted Actions cache only.",
                "- No model fitting occurred in C2.",
                "", "See C2_PANEL_BUILD.json for hashes, acceptance details and encrypted cache references.",
            ]
            OUT_PANEL_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
            print("C2_PANEL_BUILT", len(panel), "rows", len(order), "eligible cycles")
            return 0

        # Expanding walk-forward stock models. All constituents from a given cycle stay in the same test fold.
        stock_oof_rows, summaries = [], []
        for pos, cycle_id in enumerate(order):
            if pos < MIN_HISTORY:
                continue
            train = primary.loc[primary["cycle_idx"].isin(order[:pos])]
            test = primary.loc[primary["cycle_idx"].eq(cycle_id)]
            if len(test) < MIN_MEMBERS or train["stock_label"].nunique() < 2:
                failures["walk_forward_cycle_skipped"] += 1
                continue
            xtr, xte = train[FEATURES].to_numpy(float), test[FEATURES].to_numpy(float)
            ytr = train["stock_label"].astype(int).to_numpy()
            weights = equal_cycle_weights(train["cycle_idx"])
            cycle_preds = {}
            for model_name in ("logistic", "extra_trees"):
                clf = classifier(model_name)
                clf.fit(xtr, ytr, model__sample_weight=weights)
                p = clf.predict_proba(xte)[:, 1]
                block = test[["cycle_idx", "anchor_date", "expiry_date", "symbol", "stock_label"]].copy()
                block["model"] = model_name
                block["p_up"] = p
                block["momentum_p_up"] = np.where(test["ret_5d"].to_numpy() > 0, 0.55, 0.45)
                stock_oof_rows.append(block)
                cycle_preds[model_name] = p
            reg = regressor()
            yreg = train["stock_return"].to_numpy(float)
            lo, hi = np.quantile(yreg, [0.01, 0.99])
            reg.fit(xtr, np.clip(yreg, lo, hi), model__sample_weight=weights)
            mu = reg.predict(xte)
            ip = idx_primary.loc[idx_primary["cycle_idx"].eq(cycle_id)].iloc[0]
            row = {
                "cycle_idx": int(cycle_id), "anchor_date": str(ip["anchor_date"]),
                "expiry_date": str(ip["expiry_date"]), "index_label": int(ip["index_label"]),
                "index_return": float(ip["index_return"]),
                "valid_count": int(len(test)), "valid_fraction": float(len(test) / member_count[cycle_id]),
                **{f: float(ip[f]) for f in INDEX_FEATURES},
            }
            for model_name, p in cycle_preds.items():
                row[f"{model_name}_mean_p"] = float(np.mean(p))
                row[f"{model_name}_median_p"] = float(np.median(p))
                row[f"{model_name}_breadth"] = float(np.mean(p >= 0.5))
                row[f"{model_name}_std_p"] = float(np.std(p, ddof=1))
                row[f"{model_name}_mean_mu"] = float(np.mean(mu))
                row[f"{model_name}_median_mu"] = float(np.median(mu))
                row[f"{model_name}_std_mu"] = float(np.std(mu, ddof=1))
            summaries.append(row)
            print(f"C2_WALK_FORWARD {pos+1}/{len(order)} cycle={cycle_id} stocks={len(test)}")

        stock_oof = pd.concat(stock_oof_rows, ignore_index=True) if stock_oof_rows else pd.DataFrame()
        summary = pd.DataFrame(summaries).sort_values("cycle_idx").reset_index(drop=True)
        if stock_oof.empty or len(summary) < MIN_META_HISTORY + 1:
            raise RuntimeError("Insufficient walk-forward stock forecasts for index meta-model.")

        # OOF constituent forecasts only: meta-training rows all come from earlier stock-model folds.
        meta_predictions = []
        for pos in range(MIN_META_HISTORY, len(summary)):
            train, test = summary.iloc[:pos], summary.iloc[[pos]]
            y = train["index_label"].astype(int).to_numpy()
            if len(np.unique(y)) < 2:
                continue
            for source in ("extra_trees", "logistic"):
                cols = [
                    f"{source}_mean_p", f"{source}_median_p", f"{source}_breadth", f"{source}_std_p",
                    f"{source}_mean_mu", f"{source}_std_mu", "valid_fraction", *INDEX_FEATURES,
                ]
                clf = Pipeline([
                    ("impute", SimpleImputer(strategy="median")),
                    ("scale", StandardScaler()),
                    ("model", LogisticRegression(C=0.25, max_iter=2000, class_weight="balanced")),
                ])
                clf.fit(train[cols].to_numpy(float), y)
                p = float(clf.predict_proba(test[cols].to_numpy(float))[0, 1])
                meta_predictions.append({
                    "cycle_idx": int(test["cycle_idx"].iloc[0]),
                    "anchor_date": test["anchor_date"].iloc[0], "expiry_date": test["expiry_date"].iloc[0],
                    "index_label": int(test["index_label"].iloc[0]), "index_return": float(test["index_return"].iloc[0]),
                    "model": f"bottom_up_{source}_meta_logistic", "p_up": p,
                    "breadth_mean_probability": float(test[f"{source}_mean_p"].iloc[0]),
                    "breadth_majority_vote": float(test[f"{source}_breadth"].iloc[0]),
                })
        meta_oof = pd.DataFrame(meta_predictions)
        if meta_oof.empty:
            raise RuntimeError("No index meta-model OOF forecasts were produced.")

        stock_metrics = {}
        for name in ("logistic", "extra_trees"):
            d = stock_oof.loc[stock_oof["model"].eq(name)]
            m = metrics(d["stock_label"].astype(int).to_numpy(), d["p_up"].to_numpy(float))
            m["momentum_baseline"] = metrics(d["stock_label"].astype(int).to_numpy(), d["momentum_p_up"].to_numpy(float))
            stock_metrics[name] = m

        index_metrics = {}
        for name in sorted(meta_oof["model"].unique()):
            d = meta_oof.loc[meta_oof["model"].eq(name)].sort_values("cycle_idx").copy()
            cut = max(1, int(np.floor(0.8 * len(d))))
            dev, hold = d.iloc[:cut], d.iloc[cut:]
            bundle = {
                "all_oof": metrics(d["index_label"].to_numpy(int), d["p_up"].to_numpy(float)),
                "development": metrics(dev["index_label"].to_numpy(int), dev["p_up"].to_numpy(float)),
                "final_holdout": metrics(hold["index_label"].to_numpy(int), hold["p_up"].to_numpy(float)),
            }
            bundle["final_holdout"]["accuracy_wilson_95"] = wilson_ci(
                int(((hold["p_up"] >= 0.5).to_numpy() == hold["index_label"].to_numpy(int)).sum()), len(hold)
            )
            bundle["final_holdout"]["cycle_block_bootstrap_accuracy_95"] = block_bootstrap_accuracy(hold, "index_label", "p_up")
            bundle["final_holdout"]["holdout_cycles"] = int(len(hold))
            index_metrics[name] = bundle
        for source in ("extra_trees", "logistic"):
            ids = set(meta_oof.loc[meta_oof["model"].eq(f"bottom_up_{source}_meta_logistic"), "cycle_idx"])
            d = summary.loc[summary["cycle_idx"].isin(ids)].sort_values("cycle_idx")
            index_metrics[f"{source}_mean_probability_vote"] = {
                "all_oof": metrics(d["index_label"].to_numpy(int), d[f"{source}_mean_p"].to_numpy(float))
            }
            index_metrics[f"{source}_majority_breadth_vote"] = {
                "all_oof": metrics(d["index_label"].to_numpy(int), d[f"{source}_breadth"].to_numpy(float))
            }

        # Direct-index historical-feature benchmark, expanding and matched to the same cycles.
        direct_rows = []
        for pos, cycle_id in enumerate(order):
            if pos < MIN_HISTORY:
                continue
            train = idx_primary.loc[idx_primary["cycle_idx"].isin(order[:pos])].dropna(subset=["index_label"])
            test = idx_primary.loc[idx_primary["cycle_idx"].eq(cycle_id)]
            if len(train) < 50 or train["index_label"].nunique() < 2 or test.empty:
                continue
            clf = Pipeline([
                ("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler()),
                ("model", LogisticRegression(C=0.5, max_iter=2000, class_weight="balanced")),
            ])
            clf.fit(train[INDEX_FEATURES].to_numpy(float), train["index_label"].astype(int).to_numpy())
            prev = idx_primary.loc[idx_primary["cycle_idx"].lt(cycle_id), "index_label"]
            direct_rows.append({
                "cycle_idx": int(cycle_id), "anchor_date": test["anchor_date"].iloc[0],
                "expiry_date": test["expiry_date"].iloc[0], "index_label": int(test["index_label"].iloc[0]),
                "p_up": float(clf.predict_proba(test[INDEX_FEATURES].to_numpy(float))[0, 1]),
                "prior_cycle_p_up": float(prev.iloc[-1]) if len(prev) else 0.5,
            })
        direct = pd.DataFrame(direct_rows)
        if not direct.empty:
            index_metrics["direct_index_daily_logistic"] = {"all_oof": metrics(direct["index_label"].to_numpy(int), direct["p_up"].to_numpy(float))}
            index_metrics["prior_cycle_direction"] = {"all_oof": metrics(direct["index_label"].to_numpy(int), direct["prior_cycle_p_up"].to_numpy(float))}

        # Outputs hold labels and strictly OOF probabilities, never raw prices or engineered feature values.
        stock_oof.drop(columns=["momentum_p_up"], errors="ignore").to_csv(OUT_STOCK, index=False)
        meta_oof.to_csv(OUT_INDEX, index=False)
        summary[["cycle_idx", "anchor_date", "expiry_date", "index_label", "valid_count", "valid_fraction",
                 "extra_trees_mean_p", "extra_trees_median_p", "extra_trees_breadth", "extra_trees_mean_mu",
                 "extra_trees_std_mu", "logistic_mean_p", "logistic_median_p", "logistic_breadth",
                 "logistic_mean_mu", "logistic_std_mu"]].to_csv(OUT_CYCLE, index=False)

        result["data_acquisition"] = {
            "intraday_requests": int(intraday_requests), "intraday_encrypted_cache_hits": int(intraday_hits),
            "daily_requests": int(daily_requests), "daily_encrypted_cache_hits": int(daily_hits),
            "ninety_day_windows": len(chunks), "resolved_symbols": len(resolved), "unresolved_symbols": unresolved,
            "raw_prices_persisted_to_repo": False, "raw_payloads_in_encrypted_cache_only": True,
        }
        result["panel"] = {
            "scheduled_cycles": len(cycles), "index_target_rows": int(len(idx_panel)),
            "constituent_target_rows": int(len(panel)), "primary_eligible_stock_rows": int(len(primary)),
            "primary_eligible_cycles": int(len(accepted)), "first_anchor": str(idx_primary["anchor_date"].min()),
            "last_expiry": str(idx_primary["expiry_date"].max()), "history_warmup_cycles": MIN_HISTORY,
            "stock_oof_cycles": int(stock_oof["cycle_idx"].nunique()),
            "meta_oof_cycles": int(meta_oof["cycle_idx"].nunique()),
            "flat_stock_labels": int(panel["stock_label"].isna().sum()),
            "identity_flagged_rows": int(panel["identity_review_flag"].sum()),
            "action_crossing_flagged_rows": int(panel["action_crossing_flag"].sum()),
            "build_exclusions": dict(failures),
        }
        result["stock_models"] = stock_metrics
        result["index_models"] = {
            "meta_models": index_metrics, "meta_warmup_oof_cycles": MIN_META_HISTORY,
            "final_holdout_fraction": 0.20, "primary_metric": "balanced_accuracy with accuracy/Brier/AUC and cycle-block uncertainty",
        }
        result["status"] = "COMPLETED_EXPLORATORY"
        result["elapsed_seconds"] = round(time.monotonic() - started, 2)
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        write_json_report(OUT_JSON, result)
        write_report(result)
        print("C2_STATUS", result["status"], "STOCK_OOF", result["panel"]["stock_oof_cycles"], "META_OOF", result["panel"]["meta_oof_cycles"])
        return 0
    except Exception as exc:
        trace = traceback.extract_tb(exc.__traceback__)
        location = {}
        if trace:
            last = trace[-1]
            location = {"file": Path(last.filename).name, "line": int(last.lineno), "function": last.name}
        safe_message = str(exc)[:500]
        for secret_name in ("DHAN_ACCESS_TOKEN", "DHAN_CLIENT_ID", "DHAN_PIN", "DHAN_TOTP_SECRET", "HF_TOKEN"):
            secret_value = os.environ.get(secret_name, "")
            if secret_value:
                safe_message = safe_message.replace(secret_value, "[REDACTED]")
        safe_message = safe_message.replace("\\n", " ")[:500]
        diagnostics = panel_failure_diagnostics(locals())
        if os.environ.get("C2_PANEL_ONLY") == "1":
            failed = {
                "schema_version": 1,
                "status": "FAILED",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "fatal_error_category": type(exc).__name__,
                "fatal_error_message": safe_message,
                "fatal_error_location": location,
                "input_manifest": result.get("input_manifest", {}),
                "diagnostics": diagnostics,
                "limitations": result.get("limitations", []),
            }
            write_json_report(OUT_PANEL_JSON, failed)
            coverage = diagnostics.get("cycle_coverage", {})
            report_lines = [
                "# C2 Point-in-Time Constituent Panel Build",
                "",
                "**Status:** FAILED",
                "",
                f"- Error category: {type(exc).__name__}",
                f"- Error message: {safe_message}",
                f"- Source location: {location}",
                f"- Scheduled cycles: {diagnostics.get('scheduled_cycles', 'not reached')}",
                f"- Valid NIFTY target cycles: {diagnostics.get('valid_index_target_cycles', 'not reached')}",
                f"- Constituent target rows: {diagnostics.get('constituent_target_rows', 'not reached')}",
                f"- Cycles meeting 47/94%: {coverage.get('cycles_passing_47_94_rule', 'not reached')}",
                f"- Eligible constituent-count distribution: {coverage.get('eligible_stock_count_histogram', {})}",
                f"- Build failure counts: {diagnostics.get('failure_counts', {})}",
                "- Detailed value-free diagnostics are in C2_PANEL_BUILD.json.",
            ]
            OUT_PANEL_MD.parent.mkdir(parents=True, exist_ok=True)
            OUT_PANEL_MD.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
        else:
            result["status"] = "FAILED"
            result["fatal_error_category"] = type(exc).__name__
            result["fatal_error_message"] = safe_message
            result["fatal_error_location"] = location
            result["elapsed_seconds"] = round(time.monotonic() - started, 2)
            result["diagnostics"] = diagnostics
            write_json_report(OUT_JSON, result)
            write_report(result)
        print("C2_FAILED", type(exc).__name__, safe_message)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
