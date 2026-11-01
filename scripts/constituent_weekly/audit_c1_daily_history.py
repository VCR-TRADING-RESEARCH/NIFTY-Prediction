from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import tempfile
import time
import traceback
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from live_api.app import MASTER_URL, find_nifty50_security
from scripts.constituent_weekly.dhan_equity_preflight import (
    DAILY_URL,
    IST,
    MEMBERSHIP_CSV,
    acquire_access_token,
    apply_historical_security_aliases,
    request_profile,
    resolve_ids,
)

INDEX_DAILY_CSV = ROOT / "data" / "reconciliation" / "nifty50_official_daily.csv"
OUTPUT = ROOT / "research" / "constituent_weekly" / "C1_DAILY_COVERAGE.json"
START_DATE = "2018-04-01"
REQUEST_DELAY_SECONDS = 0.25
REQUEST_TIMEOUT_SECONDS = 60
METHODOLOGY_VERSION = "bup01-c1-daily-feature-coverage-v2"
TEJHQ_REPO_ID = "tejhq/indian-markets"
TEJHQ_REVISION = "f576704883fff86a6facdcde336db6ce19502063"
TEJHQ_FALLBACK_SYMBOLS = {"HDFC", "TATAMOTORS"}
TEJHQ_COMPARISON_DATES = {"TATAMOTORS": ["2025-10-20", "2025-10-22", "2025-10-23"]}
TEJHQ_PARTITION_COLUMNS = [
    "date", "symbol", "series", "isin", "open", "high", "low", "close", "volume"
]


class FatalAccessError(RuntimeError):
    pass


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def build_expected_member_sessions(
    membership: pd.DataFrame,
    session_dates: list[str],
    start_date: str = START_DATE,
) -> dict[str, list[str]]:
    required = {"symbol", "valid_from", "valid_to", "member_type", "market_data_required"}
    missing = required - set(membership.columns)
    if missing:
        raise ValueError("Membership ledger lacks required date or tradability fields.")
    symbols = membership["symbol"].astype("string").str.strip()
    starts = pd.to_datetime(membership["valid_from"], errors="coerce")
    ends = pd.to_datetime(membership["valid_to"], errors="coerce")
    member_type = membership["member_type"].astype(str).str.strip().str.casefold()
    tradable = membership["market_data_required"].astype(str).str.strip().str.upper().isin(("TRUE", "1", "YES"))
    start_cutoff = pd.Timestamp(start_date)
    result: dict[str, list[str]] = {}
    for symbol in sorted(set(symbols.dropna().astype(str))):
        mask = (
            symbols.eq(symbol)
            & member_type.eq("equity_security")
            & tradable
            & starts.notna()
            & starts.le(pd.Timestamp(max(session_dates)))
            & (ends.isna() | ends.gt(start_cutoff))
        )
        intervals = [
            (starts.loc[i], ends.loc[i])
            for i in membership.index[mask]
        ]
        expected = []
        for day in session_dates:
            stamp = pd.Timestamp(day)
            if stamp < start_cutoff:
                continue
            if any(stamp >= left and (pd.isna(right) or stamp < right) for left, right in intervals):
                expected.append(day)
        if expected:
            result[symbol] = expected
    return result


def parse_daily_payload(body: Any) -> tuple[pd.DataFrame | None, str | None]:
    if not isinstance(body, dict):
        return None, "INVALID_JSON_SHAPE"
    if str(body.get("status", "")).casefold() == "failure":
        return None, "PROVIDER_FAILURE"
    payload = body.get("data") if isinstance(body.get("data"), dict) else body
    names = ("timestamp", "open", "high", "low", "close", "volume")
    arrays = {key: payload.get(key) for key in names}
    if any(not isinstance(value, list) for value in arrays.values()):
        return None, "MISSING_DAILY_ARRAY"
    lengths = {len(value) for value in arrays.values()}
    if len(lengths) != 1:
        return None, "DAILY_ARRAY_LENGTH_MISMATCH"
    if not lengths or next(iter(lengths)) == 0:
        return pd.DataFrame(columns=["session_date", "open", "high", "low", "close", "volume"]), "NO_DAILY_BARS"
    frame = pd.DataFrame({
        "timestamp": pd.to_datetime(arrays["timestamp"], unit="s", utc=True, errors="coerce"),
        "open": pd.to_numeric(arrays["open"], errors="coerce"),
        "high": pd.to_numeric(arrays["high"], errors="coerce"),
        "low": pd.to_numeric(arrays["low"], errors="coerce"),
        "close": pd.to_numeric(arrays["close"], errors="coerce"),
        "volume": pd.to_numeric(arrays["volume"], errors="coerce"),
    })
    frame = frame.dropna(subset=["timestamp"]).copy()
    frame["session_date"] = (
        frame["timestamp"].dt.tz_convert(IST).dt.strftime("%Y-%m-%d")
    )
    return frame, None


def parse_daily_index_sessions(body: Any) -> dict[str, Any]:
    """Validate daily NIFTY index OHLC and return only a sorted session-date set.

    Index volume is intentionally not required or used for session-calendar
    construction. No price or volume observations leave this function.
    """
    if not isinstance(body, dict):
        return {"status": "INVALID_JSON_SHAPE", "valid_session_dates": []}
    if str(body.get("status", "")).casefold() == "failure":
        return {"status": "PROVIDER_FAILURE", "valid_session_dates": []}
    payload = body.get("data") if isinstance(body.get("data"), dict) else body
    names = ("timestamp", "open", "high", "low", "close")
    arrays = {key: payload.get(key) for key in names}
    if any(not isinstance(value, list) for value in arrays.values()):
        return {"status": "MISSING_INDEX_OHLC_ARRAY", "valid_session_dates": []}
    lengths = {len(value) for value in arrays.values()}
    if len(lengths) != 1:
        return {"status": "INDEX_ARRAY_LENGTH_MISMATCH", "valid_session_dates": []}
    if not lengths or next(iter(lengths)) == 0:
        return {"status": "NO_INDEX_DAILY_BARS", "valid_session_dates": []}

    frame = pd.DataFrame({
        "timestamp": pd.to_datetime(arrays["timestamp"], unit="s", utc=True, errors="coerce"),
        "open": pd.to_numeric(arrays["open"], errors="coerce"),
        "high": pd.to_numeric(arrays["high"], errors="coerce"),
        "low": pd.to_numeric(arrays["low"], errors="coerce"),
        "close": pd.to_numeric(arrays["close"], errors="coerce"),
    }).dropna(subset=["timestamp"]).copy()
    frame["session_date"] = frame["timestamp"].dt.tz_convert(IST).dt.strftime("%Y-%m-%d")

    values = frame[["open", "high", "low", "close"]].to_numpy(dtype=float)
    finite = np.isfinite(values).all(axis=1)
    positive = (values > 0).all(axis=1)
    low = frame["low"].to_numpy(dtype=float)
    high = frame["high"].to_numpy(dtype=float)
    open_ = frame["open"].to_numpy(dtype=float)
    close = frame["close"].to_numpy(dtype=float)
    invariant = (
        (low <= np.minimum(open_, close))
        & (high >= np.maximum(open_, close))
        & (high >= low)
    )
    frame["valid_ohlc"] = finite & positive & invariant

    counts = frame.groupby("session_date").size()
    duplicate_dates = {day for day, n in counts.items() if n != 1}
    valid_dates = sorted(
        set(frame.loc[frame["valid_ohlc"], "session_date"])
        - duplicate_dates
    )
    return {
        "status": "PASS" if valid_dates else "NO_VALID_INDEX_DAILY_SESSIONS",
        "valid_session_dates": valid_dates,
        "row_count": int(len(frame)),
        "valid_session_count": len(valid_dates),
        "duplicate_session_count": len(duplicate_dates),
        "invalid_ohlc_row_count": int((~frame["valid_ohlc"]).sum()),
        "first_valid_session": valid_dates[0] if valid_dates else None,
        "last_valid_session": valid_dates[-1] if valid_dates else None,
    }


def summarise_daily_coverage(body: Any, expected_dates: list[str]) -> dict[str, Any]:
    frame, parse_error = parse_daily_payload(body)
    if frame is None or frame.empty:
        return {
            "status": parse_error or "INVALID_RESPONSE",
            "expected_session_count": len(expected_dates),
            "available_session_count": 0,
            "valid_ohlc_session_count": 0,
            "valid_volume_session_count": 0,
            "ohlc_coverage_fraction": 0.0,
            "volume_coverage_fraction": 0.0,
            "coverage_fraction": 0.0,
            "duplicate_session_count": 0,
            "invalid_ohlc_row_count": 0,
            "invalid_volume_row_count": 0,
            "missing_session_count": len(expected_dates),
            "missing_session_sample": expected_dates[:20],
        }

    frame["ohlc_valid"] = False
    numeric = frame[["open", "high", "low", "close"]].to_numpy(dtype=float)
    finite = np.isfinite(numeric).all(axis=1)
    positive = (numeric > 0).all(axis=1)
    low = frame["low"].to_numpy(dtype=float)
    high = frame["high"].to_numpy(dtype=float)
    open_ = frame["open"].to_numpy(dtype=float)
    close = frame["close"].to_numpy(dtype=float)
    invariant = (
        (low <= np.minimum(open_, close))
        & (high >= np.maximum(open_, close))
        & (high >= low)
    )
    frame["ohlc_valid"] = finite & positive & invariant
    volume = frame["volume"].to_numpy(dtype=float)
    frame["volume_valid"] = np.isfinite(volume) & (volume >= 0)
    counts = frame.groupby("session_date", dropna=True).size()
    unique_dates = set(counts.index)
    duplicate_dates = sorted(d for d, count in counts.items() if count != 1)

    valid_ohlc_dates = set(
        frame.loc[frame["ohlc_valid"], "session_date"]
    )
    valid_volume_dates = set(
        frame.loc[frame["ohlc_valid"] & frame["volume_valid"], "session_date"]
    )
    duplicates = set(duplicate_dates)
    expected = set(expected_dates)
    valid_ohlc_expected = (valid_ohlc_dates & expected) - duplicates
    valid_volume_expected = (valid_volume_dates & expected) - duplicates
    missing = sorted(expected - valid_ohlc_expected)

    return {
        "status": "PASS_RESPONSE",
        "expected_session_count": len(expected_dates),
        "available_session_count": len(unique_dates & expected),
        "valid_ohlc_session_count": len(valid_ohlc_expected),
        "valid_volume_session_count": len(valid_volume_expected),
        "ohlc_coverage_fraction": round(len(valid_ohlc_expected) / len(expected), 6) if expected else 0.0,
        "volume_coverage_fraction": round(len(valid_volume_expected) / len(expected), 6) if expected else 0.0,
        "duplicate_session_count": len(duplicates & expected),
        "invalid_ohlc_row_count": int((~frame["ohlc_valid"]).sum()),
        "invalid_volume_row_count": int((~frame["volume_valid"]).sum()),
        "first_daily_bar_date": min(unique_dates) if unique_dates else None,
        "last_daily_bar_date": max(unique_dates) if unique_dates else None,
        "missing_session_sample": missing[:20],
        "missing_session_count": len(missing),
    }


def request_daily_history(
    security_id: str,
    token: str,
    client_id: str,
    from_date: str,
    to_date_exclusive: str,
    exchange_segment: str = "NSE_EQ",
    instrument: str = "EQUITY",
) -> tuple[Any, int]:
    headers = {
        "access-token": token,
        "client-id": client_id,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "securityId": str(security_id),
        "exchangeSegment": exchange_segment,
        "instrument": instrument,
        "expiryCode": 0,
        "oi": False,
        "fromDate": from_date,
        "toDate": to_date_exclusive,
    }
    for attempt in range(2):
        try:
            response = requests.post(
                DAILY_URL,
                headers=headers,
                json=payload,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.RequestException as exc:
            return {"status": "NETWORK_ERROR", "error_type": type(exc).__name__}, attempt + 1
        if response.status_code in (401, 403):
            raise FatalAccessError(f"Dhan daily-history authorization failed with HTTP {response.status_code}.")
        if response.status_code == 429 and attempt == 0:
            wait_header = response.headers.get("Retry-After", "2")
            try:
                wait = min(max(float(wait_header), 1.0), 10.0)
            except ValueError:
                wait = 2.0
            time.sleep(wait)
            continue
        if not response.ok:
            return {"status": f"HTTP_{response.status_code}"}, attempt + 1
        try:
            return response.json(), attempt + 1
        except ValueError:
            return {"status": "INVALID_JSON"}, attempt + 1
    return {"status": "HTTP_429"}, 2


def write_report(report: dict[str, Any]) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    report["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    tmp = OUTPUT.with_suffix(".tmp")
    tmp.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(OUTPUT)



def summarise_daily_universe(
    symbols: list[str],
    expected_by_symbol: dict[str, list[str]],
    symbol_results: dict[str, dict[str, Any]],
    unresolved_symbols: list[str] | None = None,
) -> dict[str, Any]:
    """Aggregate every expected member key; missing/unparseable sessions count as zero."""
    unresolved_set = set(unresolved_symbols or [])
    total_expected = sum(len(expected_by_symbol.get(symbol, [])) for symbol in symbols)
    total_ohlc = total_ohlcv = 0
    ohlc_fractions: list[float] = []
    ohlcv_fractions: list[float] = []
    dhan_parseable = fallback_symbols = fallback_sessions = 0
    symbols_with_ohlc_gap = symbols_with_ohlcv_gap = 0

    for symbol in symbols:
        expected_count = len(expected_by_symbol.get(symbol, []))
        result = symbol_results.get(symbol, {})
        combined_status = result.get("status", "UNKNOWN")
        dhan_status = result.get("dhan_status", combined_status)
        parse_ok = (
            combined_status in (
                "PASS_RESPONSE",
                "PASS_WITH_TEJHQ_FALLBACK",
                "PARTIAL_WITH_TEJHQ_FALLBACK",
            )
            and symbol not in unresolved_set
        )
        if dhan_status == "PASS_RESPONSE" and symbol not in unresolved_set:
            dhan_parseable += 1
        if int(result.get("fallback_valid_session_count", 0)) > 0:
            fallback_symbols += 1
            fallback_sessions += int(result.get("fallback_valid_session_count", 0))

        if parse_ok:
            ohlc_count = min(expected_count, int(result.get("valid_ohlc_session_count", 0)))
            ohlcv_count = min(expected_count, int(result.get("valid_volume_session_count", 0)))
        else:
            ohlc_count = ohlcv_count = 0
        ohlc_fraction = ohlc_count / expected_count if expected_count else 0.0
        ohlcv_fraction = ohlcv_count / expected_count if expected_count else 0.0
        total_ohlc += ohlc_count
        total_ohlcv += ohlcv_count
        ohlc_fractions.append(ohlc_fraction)
        ohlcv_fractions.append(ohlcv_fraction)
        symbols_with_ohlc_gap += int(ohlc_count < expected_count)
        symbols_with_ohlcv_gap += int(ohlcv_count < expected_count)

    return {
        "point_in_time_symbols_expected": len(symbols),
        "symbols_with_parseable_daily_responses": dhan_parseable,
        "symbols_with_unresolved_security_id": len(unresolved_set),
        "symbols_with_unparseable_daily_responses": len(symbols) - dhan_parseable,
        "symbols_with_tejhq_fallback": fallback_symbols,
        "tejhq_fallback_member_sessions_added": fallback_sessions,
        "expected_member_sessions": total_expected,
        "valid_member_sessions_ohlc": total_ohlc,
        "valid_member_sessions_ohlcv": total_ohlcv,
        "weighted_ohlc_session_coverage_fraction": round(total_ohlc / total_expected, 6) if total_expected else 0.0,
        "weighted_ohlcv_session_coverage_fraction": round(total_ohlcv / total_expected, 6) if total_expected else 0.0,
        "symbols_with_any_ohlc_gap": symbols_with_ohlc_gap,
        "symbols_with_any_ohlcv_gap": symbols_with_ohlcv_gap,
        "minimum_symbol_ohlc_coverage_fraction": min(ohlc_fractions, default=0.0),
        "median_symbol_ohlc_coverage_fraction": float(np.median(ohlc_fractions)) if ohlc_fractions else 0.0,
        "minimum_symbol_ohlcv_coverage_fraction": min(ohlcv_fractions, default=0.0),
        "median_symbol_ohlcv_coverage_fraction": float(np.median(ohlcv_fractions)) if ohlcv_fractions else 0.0,
    }


def daily_audit_status(summary: dict[str, Any], unresolved_count: int) -> str:
    expected = int(summary.get("expected_member_sessions", 0))
    valid_ohlc = int(summary.get("valid_member_sessions_ohlc", 0))
    valid_ohlcv = int(summary.get("valid_member_sessions_ohlcv", 0))
    return "COMPLETED_WITH_GAPS" if (
        unresolved_count > 0 or valid_ohlc < expected or valid_ohlcv < expected
    ) else "COMPLETE"


def personal_use_fallback_authorized(value: str | None) -> bool:
    """Require an explicit workflow opt-in for personal-use-only source data."""
    return str(value or "").strip() == "1"


def tejhq_cache_key(token: str) -> bytes:
    if not token or not token.strip():
        raise ValueError("HF_TOKEN is required for the encrypted personal-use data cache.")
    return hashlib.sha256(b"BUP01-TejHQ-EOD-cache-v1:" + token.strip().encode()).digest()


def encrypt_tejhq_cache_bytes(payload: bytes, token: str, associated_data: bytes) -> bytes:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    nonce = os.urandom(12)
    return nonce + AESGCM(tejhq_cache_key(token)).encrypt(nonce, payload, associated_data)


def decrypt_tejhq_cache_bytes(payload: bytes, token: str, associated_data: bytes) -> bytes:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    if len(payload) < 13:
        raise ValueError("Encrypted cache is truncated.")
    return AESGCM(tejhq_cache_key(token)).decrypt(payload[:12], payload[12:], associated_data)


def load_tejhq_nse_year(
    year: int, token: str, encrypted_cache_dir: Path
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load a pinned raw NSE bhavcopy partition; cache only AES-GCM ciphertext."""
    from cryptography.exceptions import InvalidTag
    from huggingface_hub import hf_hub_download

    filename = f"nse/year={year}/nse_{year}.parquet"
    cache_path = encrypted_cache_dir / f"nse_{year}.parquet.aesgcm"
    aad = f"{TEJHQ_REPO_ID}@{TEJHQ_REVISION}:{filename}".encode()
    encrypted_cache_dir.mkdir(parents=True, exist_ok=True)
    cache_hit = False
    raw: bytes | None = None
    if cache_path.is_file():
        try:
            raw = decrypt_tejhq_cache_bytes(cache_path.read_bytes(), token, aad)
            cache_hit = True
        except (InvalidTag, ValueError):
            cache_path.unlink(missing_ok=True)

    if raw is None:
        with tempfile.TemporaryDirectory(prefix="bup01-tejhq-") as tmp:
            downloaded = hf_hub_download(
                repo_id=TEJHQ_REPO_ID,
                filename=filename,
                repo_type="dataset",
                revision=TEJHQ_REVISION,
                token=token,
                cache_dir=str(Path(tmp) / "hf-cache"),
            )
            raw = Path(downloaded).read_bytes()
        encrypted = encrypt_tejhq_cache_bytes(raw, token, aad)
        temp_cache = cache_path.with_suffix(".tmp")
        temp_cache.write_bytes(encrypted)
        temp_cache.replace(cache_path)

    raw_sha = hashlib.sha256(raw).hexdigest()
    frame = pd.read_parquet(io.BytesIO(raw), columns=TEJHQ_PARTITION_COLUMNS)
    frame["session_date"] = pd.to_datetime(frame["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    frame["symbol"] = frame["symbol"].astype("string").str.strip().str.upper()
    frame["series"] = frame["series"].astype("string").str.strip().str.upper()
    return frame, {
        "year": int(year),
        "filename": filename,
        "encrypted_cache_hit": cache_hit,
        "raw_file_sha256": raw_sha,
        "dataset_revision": TEJHQ_REVISION,
        "dataset_repo": TEJHQ_REPO_ID,
    }


def inspect_tejhq_member_rows(
    frame: pd.DataFrame, symbol: str, requested_dates: list[str]
) -> tuple[dict[str, Any], pd.DataFrame]:
    """Validate raw NSE EQ rows; never return price values in the report."""
    selected = frame.loc[
        frame["symbol"].eq(symbol.upper())
        & frame["series"].eq("EQ")
        & frame["session_date"].isin(set(requested_dates))
    ].copy()
    if selected.empty:
        return {
            "source_rows_found": 0,
            "unique_isin_count": 0,
            "isin_non_null_row_count": 0,
            "valid_session_dates": [],
            "duplicate_session_count": 0,
            "invalid_ohlc_row_count": 0,
            "invalid_volume_row_count": 0,
        }, selected

    selected["session_date"] = selected["session_date"].astype(str)
    for field in ("open", "high", "low", "close", "volume"):
        selected[field] = pd.to_numeric(selected[field], errors="coerce")
    counts = selected.groupby("session_date").size()
    duplicates = {day for day, n in counts.items() if n != 1}
    isin_values = selected["isin"].dropna().astype(str).str.strip().tolist()
    distinct_isins = {value for value in isin_values if value}
    valid_dates: list[str] = []
    invalid_ohlc = invalid_volume = 0

    for day, group in selected.groupby("session_date"):
        if day in duplicates or len(group) != 1:
            continue
        row = group.iloc[0]
        try:
            open_, high, low, close = [float(row[k]) for k in ("open", "high", "low", "close")]
            volume = float(row["volume"])
        except (TypeError, ValueError, KeyError):
            invalid_ohlc += 1
            invalid_volume += 1
            continue
        ohlc_ok = (
            np.isfinite([open_, high, low, close]).all()
            and min(open_, high, low, close) > 0
            and low <= min(open_, close)
            and high >= max(open_, close)
            and high >= low
        )
        volume_ok = np.isfinite(volume) and volume >= 0
        invalid_ohlc += int(not ohlc_ok)
        invalid_volume += int(not volume_ok)
        if ohlc_ok and volume_ok:
            valid_dates.append(str(day))

    return {
        "source_rows_found": int(len(selected)),
        "unique_isin_count": len(distinct_isins),
        "isin_non_null_row_count": len(isin_values),
        "valid_session_dates": sorted(valid_dates),
        "duplicate_session_count": int(len(duplicates)),
        "invalid_ohlc_row_count": int(invalid_ohlc),
        "invalid_volume_row_count": int(invalid_volume),
    }, selected


def compare_dhan_and_tejhq_daily(
    dhan_body: Any, tejhq_rows: pd.DataFrame, sample_dates: list[str]
) -> dict[str, Any]:
    """Cross-check in-memory observations, retaining only match counts."""
    dhan_frame, error = parse_daily_payload(dhan_body)
    if dhan_frame is None or dhan_frame.empty:
        return {
            "status": "DHAN_SAMPLE_UNAVAILABLE",
            "dates_checked": 0,
            "dates_matched": 0,
            "dates_mismatched": 0,
            "parse_error": error,
        }
    wanted = set(sample_dates)
    dhan_frame = dhan_frame.loc[dhan_frame["session_date"].isin(wanted)]
    tejhq_rows = tejhq_rows.loc[tejhq_rows["session_date"].isin(wanted)]
    matches = mismatches = checked = 0

    for day in sample_dates:
        left = dhan_frame.loc[dhan_frame["session_date"].eq(day)]
        right = tejhq_rows.loc[tejhq_rows["session_date"].eq(day)]
        if len(left) != 1 or len(right) != 1:
            continue
        checked += 1
        same = True
        for field in ("open", "high", "low", "close", "volume"):
            try:
                a, b = float(left.iloc[0][field]), float(right.iloc[0][field])
            except (TypeError, ValueError, KeyError):
                same = False
                break
            different = (a != b) if field == "volume" else (not np.isclose(a, b, rtol=1e-4, atol=0.02))
            if different:
                same = False
                break
        if same:
            matches += 1
        else:
            mismatches += 1

    return {
        "status": "PASS" if checked == len(sample_dates) and matches == len(sample_dates) else "FAIL_OR_INCOMPLETE",
        "dates_checked": checked,
        "dates_matched": matches,
        "dates_mismatched": mismatches,
        "date_sample": sample_dates,
        "price_tolerance": "absolute 0.02 or relative 0.01%; volume exact",
    }


def merge_daily_fallback_coverage(
    result: dict[str, Any],
    expected_dates: list[str],
    fallback_valid_dates: list[str],
    fallback_status: str,
    source_crosscheck: dict[str, Any] | None = None,
    require_crosscheck: bool = False,
) -> dict[str, Any]:
    """Add validated fallback dates only where Dhan was missing."""
    merged = dict(result)
    dhan_status = merged.get("dhan_status", merged.get("status", "UNKNOWN"))
    merged.setdefault("dhan_status", dhan_status)
    primary_ohlc = int(merged.get("dhan_valid_ohlc_session_count", merged.get("valid_ohlc_session_count", 0)))
    primary_volume = int(merged.get("dhan_valid_volume_session_count", merged.get("valid_volume_session_count", 0)))
    expected = set(expected_dates)
    if dhan_status == "PASS_RESPONSE":
        missing_count = int(merged.get("missing_session_count", max(len(expected_dates) - primary_ohlc, 0)))
        sample = set(merged.get("missing_session_sample", []))
        # If the missing-date sample is truncated, do not infer or fill dates
        # from a count alone: that could double-count already valid Dhan bars.
        missing_dates = set() if missing_count == 0 else sample if missing_count <= len(sample) else set()
    else:
        missing_dates = expected

    crosscheck_ok = (not require_crosscheck) or (
        source_crosscheck is not None and source_crosscheck.get("status") == "PASS"
    )
    additions = (
        set(fallback_valid_dates) & missing_dates
        if fallback_status == "PASS" and crosscheck_ok
        else set()
    )
    filled = len(additions)
    expected_count = len(expected_dates)
    combined_ohlc = min(expected_count, primary_ohlc + filled)
    combined_volume = min(expected_count, primary_volume + filled)
    remaining_count = max(expected_count - combined_ohlc, 0)
    merged.update({
        "dhan_valid_ohlc_session_count": primary_ohlc,
        "dhan_valid_volume_session_count": primary_volume,
        "valid_ohlc_session_count": combined_ohlc,
        "valid_volume_session_count": combined_volume,
        "ohlc_coverage_fraction": round(combined_ohlc / expected_count, 6) if expected_count else 0.0,
        "volume_coverage_fraction": round(combined_volume / expected_count, 6) if expected_count else 0.0,
        "fallback_source": "tejhq_raw_nse_bhavcopy",
        "fallback_status": fallback_status,
        "fallback_valid_session_count": filled,
        "fallback_dataset_revision": TEJHQ_REVISION,
        "source_crosscheck": source_crosscheck,
        "missing_session_count": remaining_count,
        "status": (
            "PASS_WITH_TEJHQ_FALLBACK" if remaining_count == 0 and filled > 0
            else "PARTIAL_WITH_TEJHQ_FALLBACK" if filled > 0
            else dhan_status
        ),
    })
    return merged


def _run_daily_audit() -> int:
    started = time.monotonic()
    membership = pd.read_csv(MEMBERSHIP_CSV, low_memory=False)
    official_calendar = pd.read_csv(INDEX_DAILY_CSV, low_memory=False)
    if "session_date" not in official_calendar.columns:
        raise ValueError("Official NIFTY daily-session reference lacks session_date.")
    official_session_dates = sorted({
        pd.Timestamp(value).strftime("%Y-%m-%d")
        for value in official_calendar["session_date"].dropna().astype(str)
        if pd.Timestamp(value) >= pd.Timestamp(START_DATE)
    })
    if not official_session_dates:
        raise ValueError("No official trading-session dates found in feature window.")
    official_window_end = official_session_dates[-1]

    master_response = requests.get(MASTER_URL, timeout=45)
    master_response.raise_for_status()
    master_bytes = master_response.content
    master = pd.read_csv(pd.io.common.BytesIO(master_bytes), low_memory=False)
    master_sha = sha256_bytes(master_bytes)
    index_security_id = find_nifty50_security(master)

    token, client_id, auth_method, refresh_status, _diag = acquire_access_token()
    profile = request_profile(token)
    if not profile.ok:
        raise FatalAccessError(f"Dhan profile authorization failed with HTTP {profile.status_code}.")
    profile_body = profile.json()
    if str(profile_body.get("dataPlan", "")).strip().casefold() != "active":
        raise FatalAccessError("Dhan Data API plan is not active.")

    # Dhan IDX_I daily OHLC fills the missing 2018-04 .. 2019-01 calendar.
    # Existing official dates are retained; Dhan only adds validated sessions.
    index_body, index_attempts = request_daily_history(
        index_security_id,
        token,
        client_id,
        START_DATE,
        (date.fromisoformat(official_window_end) + timedelta(days=1)).isoformat(),
        exchange_segment="IDX_I",
        instrument="INDEX",
    )
    index_calendar = parse_daily_index_sessions(index_body)
    dhan_index_dates = sorted(set(index_calendar.get("valid_session_dates", [])))
    official_set = set(official_session_dates)
    dhan_set = set(dhan_index_dates)
    union_session_dates = sorted(official_set | dhan_set)
    if not union_session_dates:
        raise ValueError("No valid official or Dhan NIFTY daily sessions found.")
    window_end = union_session_dates[-1]

    # HDFC Ltd's last separately tradable session was 2023-06-30, not 2023-07-12.
    hdfc_rows = membership["symbol"].astype(str).str.upper().eq("HDFC")
    membership.loc[hdfc_rows, "valid_to"] = "2023-07-01"
    expected_by_symbol = build_expected_member_sessions(membership, union_session_dates)
    symbols = sorted(expected_by_symbol)

    resolved = resolve_ids(master, symbols)
    alias_ids = resolve_ids(master, ["TMPV"])
    resolved = apply_historical_security_aliases(symbols, resolved, alias_ids)
    unresolved = sorted(set(symbols) - set(resolved))

    expected_total = sum(len(expected_by_symbol[symbol]) for symbol in symbols)
    union_dates_hash = sha256_bytes("\n".join(union_session_dates).encode("utf-8"))
    manifest = {
        "membership_sha256": file_sha256(MEMBERSHIP_CSV),
        "official_daily_session_sha256": file_sha256(INDEX_DAILY_CSV),
        "dhan_scrip_master_sha256": master_sha,
        "daily_endpoint": DAILY_URL,
        "official_session_count": len(official_session_dates),
        "official_first_session": official_session_dates[0],
        "dhan_index_session_count": len(dhan_index_dates),
        "dhan_index_first_session": dhan_index_dates[0] if dhan_index_dates else None,
        "dhan_index_last_session": dhan_index_dates[-1] if dhan_index_dates else None,
        "dhan_index_sessions_added": len(dhan_set - official_set),
        "dhan_index_overlap_sessions": len(dhan_set & official_set),
        "union_calendar_sha256": union_dates_hash,
        "union_session_count": len(union_session_dates),
        "expected_member_session_count": expected_total,
        "window_start": START_DATE,
        "window_end": window_end,
        "hdfc_last_tradable_session": "2023-06-30",
    }
    report = {
        "schema_version": 2,
        "methodology_version": METHODOLOGY_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "IN_PROGRESS",
        "coverage_interpretation": "Descriptive daily OHLCV coverage; no unregistered percentage threshold is added. Dhan is primary. Restricted personal-use TejHQ raw NSE bhavcopy is a fallback only for Dhan-missing HDFC/Tata Motors sessions.",
        "input_manifest": manifest,
        "requests_this_run": int(index_attempts),
        "cache_reused_symbols": 0,
        "symbol_results": {},
        "unresolved_symbols": unresolved,
        "index_calendar_qa": {
            "status": index_calendar.get("status"),
            "official_first_session": official_session_dates[0],
            "official_last_session": official_session_dates[-1],
            "dhan_valid_session_count": len(dhan_index_dates),
            "dhan_first_valid_session": dhan_index_dates[0] if dhan_index_dates else None,
            "dhan_last_valid_session": dhan_index_dates[-1] if dhan_index_dates else None,
            "dhan_sessions_added": len(dhan_set - official_set),
            "dhan_official_overlap_sessions": len(dhan_set & official_set),
            "dhan_duplicate_session_count": index_calendar.get("duplicate_session_count", 0),
            "dhan_invalid_ohlc_row_count": index_calendar.get("invalid_ohlc_row_count", 0),
            "session_calendar_union_count": len(union_session_dates),
            "raw_index_price_values_published": False,
        },
        "summary": {},
        "fatal_error": None,
        "auth_method": auth_method,
        "token_refresh_status": refresh_status,
        "dhan_profile_authorized": True,
    }

    if OUTPUT.exists():
        try:
            old = json.loads(OUTPUT.read_text(encoding="utf-8"))
            if old.get("methodology_version") == METHODOLOGY_VERSION and old.get("input_manifest") == manifest:
                report["symbol_results"] = old.get("symbol_results", {})
                report["cache_reused_symbols"] = len(report["symbol_results"])
        except (OSError, ValueError, TypeError):
            pass

    # Preserve the actual provider error and suppress repeat calls for the
    # retired HDFC legacy security. Three independent Dhan probes returned DH-905.
    pending: list[str] = []
    for symbol in symbols:
        if symbol not in resolved:
            continue
        existing = report["symbol_results"].get(symbol, {})
        dhan_status = existing.get("dhan_status", existing.get("status", "NOT_REQUESTED"))
        if symbol == "HDFC" and dhan_status in ("MISSING_DAILY_ARRAY", "KNOWN_DHAN_DH905"):
            continue
        if dhan_status != "PASS_RESPONSE":
            pending.append(symbol)

    write_report(report)
    try:
        # Re-request all equity daily series after the calendar expansion; the
        # v2 manifest forces a complete validation against the corrected dates.
        raw_dhan_for_crosscheck: dict[str, Any] = {}
        for number, symbol in enumerate(pending, 1):
            if symbol == "HDFC":
                # The old standalone HDFC security is no longer active in Dhan.
                # Prior controlled probes established DH-905, so retain that as
                # a source status and proceed to mother-source fallback.
                result = {
                    "status": "KNOWN_DHAN_DH905",
                    "dhan_status": "KNOWN_DHAN_DH905",
                    "dhan_provider_error_code": "DH-905",
                    "dhan_provider_error_type": "Input_Exception",
                    "dhan_probe_count": 3,
                    "expected_session_count": len(expected_by_symbol[symbol]),
                    "available_session_count": 0,
                    "valid_ohlc_session_count": 0,
                    "valid_volume_session_count": 0,
                    "dhan_valid_ohlc_session_count": 0,
                    "dhan_valid_volume_session_count": 0,
                    "ohlc_coverage_fraction": 0.0,
                    "volume_coverage_fraction": 0.0,
                    "missing_session_count": len(expected_by_symbol[symbol]),
                    "missing_session_sample": expected_by_symbol[symbol][:20],
                }
                report["symbol_results"][symbol] = result
                write_report(report)
                print(f"C1_DAILY_SYMBOL {number}/{len(pending)} HDFC source=KNOWN_DH905")
                continue

            response, attempts = request_daily_history(
                resolved[symbol],
                token,
                client_id,
                START_DATE,
                (date.fromisoformat(window_end) + timedelta(days=1)).isoformat(),
            )
            report["requests_this_run"] += attempts
            time.sleep(REQUEST_DELAY_SECONDS)
            item = summarise_daily_coverage(response, expected_by_symbol[symbol])
            item["dhan_status"] = item.get("status", "UNKNOWN")
            item["dhan_valid_ohlc_session_count"] = item.get("valid_ohlc_session_count", 0)
            item["dhan_valid_volume_session_count"] = item.get("valid_volume_session_count", 0)
            report["symbol_results"][symbol] = item
            if symbol == "TATAMOTORS":
                raw_dhan_for_crosscheck[symbol] = response
            report["last_symbol_completed"] = symbol
            report["symbols_completed_this_run"] = number
            report["symbols_total"] = len(pending)
            write_report(report)
            print(
                f"C1_DAILY_SYMBOL {number}/{len(pending)} {symbol} "
                f"coverage={item.get('ohlc_coverage_fraction', 0):.3f} "
                f"requests={report['requests_this_run']}"
            )

        hf_token = os.environ.get("HF_TOKEN", "").strip()
        encrypted_cache_dir = Path(
            os.environ.get(
                "TEJHQ_ENCRYPTED_CACHE_DIR",
                str(Path.home() / ".cache" / "bup01-tejhq-encrypted"),
            )
        )
        fallback_run: dict[str, Any] = {
            "status": "NOT_NEEDED",
            "dataset_repo": TEJHQ_REPO_ID,
            "dataset_revision": TEJHQ_REVISION,
            "source_tree": "nse/year=YYYY/nse_YYYY.parquet (raw NSE EQ bhavcopy; not prices_adjusted)",
            "cache_encryption": "AES-256-GCM keyed from HF_TOKEN; only encrypted files are eligible for cache",
            "raw_data_persisted_to_repo_or_artifact": False,
            "license_scope": "PERSONAL_USE_ONLY; no client/business use; no raw redistribution; exchange terms apply independently",
            "symbols": {},
            "year_partitions_used": [],
            "encrypted_cache_hits": 0,
            "year_partitions_downloaded": 0,
        }
        fallback_symbols = [
            symbol for symbol in sorted(TEJHQ_FALLBACK_SYMBOLS)
            if symbol in expected_by_symbol
            and int(report["symbol_results"].get(symbol, {}).get("missing_session_count", 0)) > 0
        ]

        personal_use_only = personal_use_fallback_authorized(
            os.environ.get("TEJHQ_PERSONAL_USE_ONLY")
        )
        if fallback_symbols and not personal_use_only:
            fallback_run["status"] = "SKIPPED_PERSONAL_USE_NOT_CONFIRMED"
        elif fallback_symbols and not hf_token:
            fallback_run["status"] = "SKIPPED_HF_TOKEN_MISSING"
        elif fallback_symbols:
            fallback_run["status"] = "IN_PROGRESS"
            partitions: dict[int, pd.DataFrame] = {}
            partition_meta: dict[int, dict[str, Any]] = {}
            for symbol in fallback_symbols:
                current = report["symbol_results"].get(symbol, {})
                expected_dates = expected_by_symbol[symbol]
                dhan_status = current.get("dhan_status", current.get("status", "UNKNOWN"))
                if dhan_status == "PASS_RESPONSE":
                    missing_count = int(current.get("missing_session_count", 0))
                    sample = set(current.get("missing_session_sample", []))
                    target_dates = (
                        [] if missing_count == 0
                        else sorted(sample) if missing_count <= len(sample)
                        else expected_dates
                    )
                else:
                    target_dates = expected_dates

                compare_dates = TEJHQ_COMPARISON_DATES.get(symbol, [])
                requested_dates = sorted(set(target_dates) | set(compare_dates))
                years = sorted({int(day[:4]) for day in requested_dates})
                for year in years:
                    if year not in partitions:
                        frame, meta = load_tejhq_nse_year(year, hf_token, encrypted_cache_dir)
                        partitions[year] = frame
                        partition_meta[year] = meta
                    if year not in fallback_run["year_partitions_used"]:
                        fallback_run["year_partitions_used"].append(year)

                selected = pd.concat([partitions[year] for year in years], ignore_index=True)
                source_summary, source_rows = inspect_tejhq_member_rows(selected, symbol, requested_dates)
                fallback_status = "PASS" if (
                    source_summary["unique_isin_count"] == 1
                    and source_summary["isin_non_null_row_count"] == source_summary["source_rows_found"]
                    and source_summary["duplicate_session_count"] == 0
                    and source_summary["invalid_ohlc_row_count"] == 0
                    and source_summary["invalid_volume_row_count"] == 0
                    and len(source_summary["valid_session_dates"]) > 0
                ) else "REJECTED_IDENTITY_OR_ROW_QA"

                crosscheck = None
                require_crosscheck = symbol == "TATAMOTORS"
                if require_crosscheck:
                    # Keep Dhan as the primary source; compare three neighbouring
                    # sessions before accepting the single missing-date fallback.
                    dhan_sample, attempts = request_daily_history(
                        resolved[symbol],
                        token,
                        client_id,
                        min(compare_dates),
                        (date.fromisoformat(max(compare_dates)) + timedelta(days=1)).isoformat(),
                    )
                    report["requests_this_run"] += attempts
                    crosscheck = compare_dhan_and_tejhq_daily(dhan_sample, source_rows, compare_dates)
                if require_crosscheck and (crosscheck is None or crosscheck.get("status") != "PASS"):
                    fallback_status = "REJECTED_CROSS_SOURCE_MISMATCH_OR_INCOMPLETE"

                merged = merge_daily_fallback_coverage(
                    current,
                    expected_dates,
                    source_summary["valid_session_dates"],
                    fallback_status,
                    source_crosscheck=crosscheck,
                    require_crosscheck=require_crosscheck,
                )
                merged["tejhq_source_rows_found"] = source_summary["source_rows_found"]
                merged["tejhq_source_unique_isin_count"] = source_summary["unique_isin_count"]
                merged["tejhq_source_duplicate_session_count"] = source_summary["duplicate_session_count"]
                merged["tejhq_source_invalid_ohlc_row_count"] = source_summary["invalid_ohlc_row_count"]
                merged["tejhq_source_invalid_volume_row_count"] = source_summary["invalid_volume_row_count"]
                merged["tejhq_source_dataset_revision"] = TEJHQ_REVISION
                merged["tejhq_source_raw_partition_sha256"] = {
                    str(year): partition_meta[year]["raw_file_sha256"] for year in years
                }
                report["symbol_results"][symbol] = merged
                fallback_run["symbols"][symbol] = {
                    "status": fallback_status,
                    "expected_session_count": len(expected_dates),
                    "candidate_sessions_checked": len(requested_dates),
                    "valid_source_sessions": len(source_summary["valid_session_dates"]),
                    "fallback_sessions_added": merged.get("fallback_valid_session_count", 0),
                    "unique_isin_count": source_summary["unique_isin_count"],
                    "duplicate_session_count": source_summary["duplicate_session_count"],
                    "invalid_ohlc_row_count": source_summary["invalid_ohlc_row_count"],
                    "invalid_volume_row_count": source_summary["invalid_volume_row_count"],
                    "source_crosscheck": crosscheck,
                }
                write_report(report)

            fallback_run["encrypted_cache_hits"] = sum(
                int(meta.get("encrypted_cache_hit", False)) for meta in partition_meta.values()
            )
            fallback_run["year_partitions_downloaded"] = sum(
                int(not meta.get("encrypted_cache_hit", False)) for meta in partition_meta.values()
            )
            fallback_run["partition_sha256"] = {
                str(year): meta["raw_file_sha256"] for year, meta in partition_meta.items()
            }
            fallback_run["status"] = (
                "COMPLETED" if all(
                    item["status"] in ("PASS", "PASS_WITH_TEJHQ_FALLBACK")
                    for item in fallback_run["symbols"].values()
                ) else "COMPLETED_WITH_GAPS"
            )

        report["tejhq_fallback"] = fallback_run
        results = report["symbol_results"]
        summary = summarise_daily_universe(symbols, expected_by_symbol, results, unresolved)
        report["summary"] = {
            "window_start": START_DATE,
            "window_end": window_end,
            "official_trading_session_count": len(official_session_dates),
            "union_trading_session_count": len(union_session_dates),
            "dhan_index_daily_calendar_status": index_calendar.get("status"),
            "dhan_index_daily_calendar_sessions_added": len(dhan_set - official_set),
            **summary,
            "daily_feature_coverage_disposition": "DESCRIPTIVE_REVIEW_REQUIRED",
            "daily_coverage_gate": "DESCRIPTIVE_ONLY_NO_UNREGISTERED_THRESHOLD",
        }
        report["status"] = daily_audit_status(summary, len(unresolved))
        report["elapsed_seconds"] = round(time.monotonic() - started, 2)
        write_report(report)
        print(
            "C1_DAILY_COVERAGE_STATUS",
            report["status"],
            "OHLCV",
            summary["weighted_ohlcv_session_coverage_fraction"],
            "TEJHQ_FALLBACK",
            fallback_run["status"],
        )
        return 0
    except FatalAccessError as exc:
        report["status"] = "BLOCKED_AUTH_OR_ENTITLEMENT"
        report["fatal_error"] = "FATAL_ACCESS_ERROR"
        trace = traceback.extract_tb(exc.__traceback__)
        if trace:
            last = trace[-1]
            report["fatal_error_location"] = {
                "file": Path(last.filename).name,
                "line": int(last.lineno),
                "function": last.name,
            }
        report["elapsed_seconds"] = round(time.monotonic() - started, 2)
        write_report(report)
        print("C1_DAILY_COVERAGE_BLOCKED", type(exc).__name__)
        return 1
    except Exception as exc:
        report["status"] = "PARTIAL_OR_BLOCKED_RUNTIME_ERROR"
        report["fatal_error"] = type(exc).__name__
        trace = traceback.extract_tb(exc.__traceback__)
        if trace:
            last = trace[-1]
            report["fatal_error_location"] = {
                "file": Path(last.filename).name,
                "line": int(last.lineno),
                "function": last.name,
            }
        report["elapsed_seconds"] = round(time.monotonic() - started, 2)
        write_report(report)
        print("C1_DAILY_COVERAGE_RUNTIME_ERROR", type(exc).__name__)
        return 1


def main() -> int:
    wrapper_started = datetime.now(timezone.utc)
    try:
        return _run_daily_audit()
    except Exception as exc:
        report: dict[str, Any] = {
            "schema_version": 2,
            "methodology_version": METHODOLOGY_VERSION,
            "created_at_utc": wrapper_started.isoformat(),
            "status": "IN_PROGRESS",
            "symbol_results": {},
            "summary": {},
        }
        try:
            if OUTPUT.exists():
                candidate = json.loads(OUTPUT.read_text(encoding="utf-8"))
                created = candidate.get("created_at_utc")
                if created and datetime.fromisoformat(created) >= wrapper_started:
                    report = candidate
        except (OSError, ValueError, TypeError):
            pass
        report["status"] = (
            "BLOCKED_AUTH_OR_ENTITLEMENT"
            if isinstance(exc, FatalAccessError)
            else "PARTIAL_OR_BLOCKED_RUNTIME_ERROR"
        )
        report["fatal_error"] = type(exc).__name__
        trace = traceback.extract_tb(exc.__traceback__)
        if trace:
            last = trace[-1]
            report["fatal_error_location"] = {
                "file": Path(last.filename).name,
                "line": int(last.lineno),
                "function": last.name,
            }
        report["elapsed_seconds"] = round(
            (datetime.now(timezone.utc) - wrapper_started).total_seconds(), 2
        )
        write_report(report)
        print("C1_DAILY_COVERAGE_EARLY_FAILURE", type(exc).__name__)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
