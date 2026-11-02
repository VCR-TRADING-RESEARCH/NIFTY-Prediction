from __future__ import annotations

import io
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from live_api.app import MASTER_URL
from scripts.constituent_weekly.dhan_equity_preflight import (
    acquire_access_token, request_profile, resolve_ids,
)
from scripts.constituent_weekly.audit_c1_daily_history import (
    DAILY_URL, load_tejhq_nse_year, parse_daily_payload, request_daily_history,
    inspect_tejhq_member_rows, resolve_tejhq_encrypted_cache_dir,
    personal_use_fallback_authorized,
)

OUT_JSON = ROOT / "research/constituent_weekly/C1_DHAN_ADJUSTMENT_DIAGNOSTIC.json"
OUT_MD = ROOT / "research/constituent_weekly/C1_DHAN_ADJUSTMENT_DIAGNOSTIC.md"
SYMBOL = "RELIANCE"
EX_DATE = "2024-10-28"
EXPECTED_PRE_FACTOR = 0.5
SAMPLE_DATES = [
    "2024-10-21", "2024-10-22", "2024-10-23", "2024-10-24", "2024-10-25",
    "2024-10-28", "2024-10-29", "2024-10-30", "2024-11-04",
]
PRICE_FIELDS = ("open", "high", "low", "close")
RIL_SOURCE = "https://www.ril.com/sites/default/files/2024-10/SE_16102024.pdf"
NSE_SOURCE = "https://nsearchives.nseindia.com/content/circulars/FAOP64621.pdf"


def compute_adjustment_diagnostic(
    dhan_frame: pd.DataFrame,
    raw_frame: pd.DataFrame,
    sample_dates: list[str] = SAMPLE_DATES,
    ex_date: str = EX_DATE,
) -> dict:
    """Compare Dhan's adjusted OHLC against raw NSE bhavcopy OHLC without exposing prices."""
    required = {"session_date", *PRICE_FIELDS}
    if required - set(dhan_frame.columns) or required - set(raw_frame.columns):
        return {"status": "INVALID_INPUT_SCHEMA", "dates_checked": 0, "dates_matched": 0}
    if "isin" not in raw_frame.columns:
        return {"status": "RAW_IDENTITY_FIELD_MISSING", "dates_checked": 0, "dates_matched": 0}

    left = dhan_frame.loc[dhan_frame["session_date"].astype(str).isin(sample_dates)].copy()
    right = raw_frame.loc[raw_frame["session_date"].astype(str).isin(sample_dates)].copy()
    left["session_date"] = left["session_date"].astype(str)
    right["session_date"] = right["session_date"].astype(str)
    if left["session_date"].duplicated().any() or right["session_date"].duplicated().any():
        return {"status": "DUPLICATE_SESSION_ROWS", "dates_checked": 0, "dates_matched": 0}
    isin_values = sorted(set(right["isin"].dropna().astype(str).str.strip()) - {""})
    if len(isin_values) != 1:
        return {"status": "AMBIGUOUS_OR_MISSING_ISIN", "dates_checked": 0, "dates_matched": 0,
                "raw_unique_isin_count": len(isin_values)}

    joined = left.merge(right, on="session_date", suffixes=("_dhan", "_raw"), validate="one_to_one")
    expected_dates = set(sample_dates)
    present_dates = set(joined["session_date"].astype(str))
    missing = sorted(expected_dates - present_dates)
    if len(joined) != len(sample_dates):
        return {"status": "INCOMPLETE_DATE_MATCH", "dates_checked": int(len(joined)),
                "dates_matched": int(len(joined)), "missing_dates": missing,
                "raw_unique_isin_count": 1}

    ratios = {field: [] for field in PRICE_FIELDS}
    pre_ratios = {field: [] for field in PRICE_FIELDS}
    post_ratios = {field: [] for field in PRICE_FIELDS}
    for _, row in joined.iterrows():
        day = str(row["session_date"])
        for field in PRICE_FIELDS:
            dhan_value = pd.to_numeric(row[f"{field}_dhan"], errors="coerce")
            raw_value = pd.to_numeric(row[f"{field}_raw"], errors="coerce")
            if not np.isfinite(dhan_value) or not np.isfinite(raw_value) or dhan_value <= 0 or raw_value <= 0:
                return {"status": "INVALID_PRICE_OBSERVATION", "dates_checked": int(len(joined)),
                        "dates_matched": int(len(joined)), "raw_unique_isin_count": 1}
            ratio = float(dhan_value / raw_value)
            ratios[field].append(ratio)
            (pre_ratios if day < ex_date else post_ratios)[field].append(ratio)

    pre_median = {field: round(float(np.median(values)), 6) for field, values in pre_ratios.items()}
    post_median = {field: round(float(np.median(values)), 6) for field, values in post_ratios.items()}
    pre_ok = all(0.48 <= value <= 0.52 for value in pre_median.values())
    post_ok = all(0.97 <= value <= 1.03 for value in post_median.values())
    return {
        "status": "PASS_BONUS_ADJUSTMENT_FACTOR" if pre_ok and post_ok else "FAIL_OR_INCOMPLETE_FACTOR",
        "dates_checked": int(len(joined)),
        "dates_matched": int(len(joined)),
        "pre_ex_date_session_count": int((joined["session_date"].astype(str) < ex_date).sum()),
        "post_ex_date_session_count": int((joined["session_date"].astype(str) >= ex_date).sum()),
        "raw_unique_isin_count": 1,
        "expected_pre_ex_date_factor": EXPECTED_PRE_FACTOR,
        "expected_post_ex_date_factor": 1.0,
        "pre_ex_date_median_factor_by_ohlc": pre_median,
        "post_ex_date_median_factor_by_ohlc": post_median,
        "pre_factor_tolerance": [0.48, 0.52],
        "post_factor_tolerance": [0.97, 1.03],
        "pre_factor_check_passed": pre_ok,
        "post_factor_check_passed": post_ok,
        "raw_prices_published": False,
        "isin_published": False,
    }


def write_report(result: dict) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    diag = result.get("diagnostic", {})
    lines = [
        "# Dhan Daily Adjusted-Price Corporate-Action Diagnostic", "",
        f"**Updated:** {result.get('updated_at_utc')}",
        f"**Overall status:** {result.get('status')}",
        f"**Instrument:** {SYMBOL}",
        f"**Event:** 1:1 bonus; ex-date {EX_DATE}",
        f"**Dhan daily endpoint:** {DAILY_URL}",
        f"**Matched sessions:** {diag.get('dates_matched', 0)}/{len(SAMPLE_DATES)}",
        f"**Pre-ex median factors (OHLC):** {diag.get('pre_ex_date_median_factor_by_ohlc')}",
        f"**Post-ex median factors (OHLC):** {diag.get('post_ex_date_median_factor_by_ohlc')}",
        f"**Pre/post checks:** {diag.get('pre_factor_check_passed')} / {diag.get('post_factor_check_passed')}", "",
        "## Primary-source event terms", "",
        f"- Issuer record-date notice: {RIL_SOURCE}",
        f"- NSE F&O adjustment circular (factor 2, revised market lot 500): {NSE_SOURCE}", "",
        "## Data and privacy", "",
        "- Raw Dhan/TejHQ prices and ISIN are not written to reports or artifacts.",
        "- The raw TejHQ NSE partition is used only under the personal-use-only workflow opt-in and retained only as AES-GCM encrypted Actions cache.",
        "- Dhan API credentials and tokens are runtime-only; no token values are logged.",
        "- This single bonus-event diagnostic does not validate dividends, rights, mergers, demergers or buybacks.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run() -> dict:
    result = {
        "status": "BLOCKED",
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "event": {"symbol": SYMBOL, "type": "BONUS", "ratio": "1:1", "ex_date": EX_DATE},
        "sample_dates": SAMPLE_DATES,
        "raw_prices_published": False,
        "raw_event_rows_published": False,
        "credentials_or_tokens_recorded": False,
        "sources": {"issuer": RIL_SOURCE, "nse_contract_adjustment": NSE_SOURCE},
    }
    if not personal_use_fallback_authorized(os.environ.get("TEJHQ_PERSONAL_USE_ONLY")):
        result["status"] = "BLOCKED_PERSONAL_USE_NOT_CONFIRMED"
        return result
    hf_token = os.environ.get("HF_TOKEN", "").strip()
    if not hf_token:
        result["status"] = "BLOCKED_HF_TOKEN_MISSING"
        return result
    try:
        token, client_id, auth_method, refresh_status, _ = acquire_access_token()
        result["auth_method"] = auth_method
        result["token_refresh_status"] = refresh_status
        profile = request_profile(token)
        if not profile.ok:
            result["status"] = f"BLOCKED_PROFILE_HTTP_{profile.status_code}"
            return result
        if str(profile.json().get("dataPlan", "")).strip().casefold() != "active":
            result["status"] = "BLOCKED_DATA_PLAN_NOT_ACTIVE"
            return result
        result["data_plan_active"] = True

        master_response = requests.get(MASTER_URL, timeout=45)
        master_response.raise_for_status()
        master = pd.read_csv(io.BytesIO(master_response.content), low_memory=False)
        resolved = resolve_ids(master, [SYMBOL])
        if SYMBOL not in resolved:
            result["status"] = "BLOCKED_SECURITY_ID_UNRESOLVED"
            return result

        dhan_body, attempts = request_daily_history(
            resolved[SYMBOL], token, client_id, min(SAMPLE_DATES),
            "2024-11-05",
        )
        result["dhan_daily_request_attempts"] = attempts
        dhan_frame, parse_error = parse_daily_payload(dhan_body)
        if dhan_frame is None or dhan_frame.empty:
            result["status"] = "BLOCKED_DHAN_DAILY_" + str(parse_error or "NO_BARS")
            return result

        cache_dir = resolve_tejhq_encrypted_cache_dir(os.environ.get("TEJHQ_ENCRYPTED_CACHE_DIR"))
        raw_year, cache_meta = load_tejhq_nse_year(2024, hf_token, cache_dir)
        source_summary, raw_rows = inspect_tejhq_member_rows(raw_year, SYMBOL, SAMPLE_DATES)
        result["tejhq_cache"] = {
            "encrypted_cache_hit": bool(cache_meta.get("encrypted_cache_hit")),
            "raw_partition_sha256": cache_meta.get("raw_file_sha256"),
            "dataset_revision": cache_meta.get("dataset_revision"),
            "valid_sample_sessions": len(source_summary.get("valid_session_dates", [])),
            "unique_isin_count": source_summary.get("unique_isin_count"),
            "raw_values_persisted": False,
        }
        if source_summary.get("valid_session_dates") != sorted(SAMPLE_DATES):
            result["status"] = "BLOCKED_RAW_REFERENCE_QA"
            result["raw_reference_qa"] = {
                "valid_session_count": len(source_summary.get("valid_session_dates", [])),
                "duplicate_session_count": source_summary.get("duplicate_session_count"),
                "invalid_ohlc_row_count": source_summary.get("invalid_ohlc_row_count"),
                "invalid_volume_row_count": source_summary.get("invalid_volume_row_count"),
                "unique_isin_count": source_summary.get("unique_isin_count"),
            }
            return result

        diagnostic = compute_adjustment_diagnostic(dhan_frame, raw_rows)
        result["diagnostic"] = diagnostic
        result["status"] = diagnostic["status"]
        return result
    except Exception as exc:
        result["status"] = "BLOCKED_RUNTIME_ERROR"
        result["error_type"] = type(exc).__name__
        return result


def main() -> int:
    result = run()
    write_report(result)
    print("C1_DHAN_ADJUSTMENT_DIAGNOSTIC", result["status"])
    print("Dhan bonus adjustment factor diagnostic complete; raw price values withheld.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
