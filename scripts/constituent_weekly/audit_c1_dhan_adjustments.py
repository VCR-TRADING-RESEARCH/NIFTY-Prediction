from __future__ import annotations

import io
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from live_api.app import MASTER_URL
from scripts.constituent_weekly.dhan_equity_preflight import acquire_access_token, request_profile, resolve_ids
from scripts.constituent_weekly.audit_c1_daily_history import (
    DAILY_URL, load_tejhq_nse_year, parse_daily_payload, request_daily_history,
    inspect_tejhq_member_rows, resolve_tejhq_encrypted_cache_dir,
    personal_use_fallback_authorized,
)

OUT_JSON = ROOT / "research/constituent_weekly/C1_DHAN_ADJUSTMENT_DIAGNOSTIC.json"
OUT_MD = ROOT / "research/constituent_weekly/C1_DHAN_ADJUSTMENT_DIAGNOSTIC.md"
PRICE_FIELDS = ("open", "high", "low", "close")
POST_FACTOR_TOLERANCE = (0.90, 1.05)

EVENTS = [
    {
        "symbol": "RELIANCE", "action": "BONUS_1_TO_1", "ex_date": "2024-10-28",
        "expected_pre_factor": 0.5, "expected_pre_isin": "INE002A01018", "expected_post_isin": "INE002A01018", "sample_dates": [
            "2024-10-21", "2024-10-22", "2024-10-23", "2024-10-24", "2024-10-25",
            "2024-10-28", "2024-10-29", "2024-10-30", "2024-11-04",
        ],
        "raw_year": 2024,
        "issuer_source": "https://www.ril.com/sites/default/files/2024-10/SE_16102024.pdf",
        "exchange_source": "https://nsearchives.nseindia.com/content/circulars/FAOP64621.pdf",
    },
    {
        "symbol": "BAJAJFINSV", "action": "SPLIT_5_TO_1_PLUS_BONUS_1_TO_1", "ex_date": "2022-09-13",
        "expected_pre_factor": 0.1, "expected_pre_isin": "INE918I01018", "expected_post_isin": "INE918I01026", "sample_dates": [
            "2022-09-05", "2022-09-06", "2022-09-07", "2022-09-08", "2022-09-09", "2022-09-12",
            "2022-09-13", "2022-09-14", "2022-09-15", "2022-09-16", "2022-09-19",
        ],
        "raw_year": 2022,
        "issuer_source": "https://www.bajajfinserv.in/finserv-digital-annual-report-fy23/assets/pdf/Bajaj-Finserv-AnnualReport-2022-23.pdf",
        "exchange_source": "https://archives.nseindia.com/content/circulars/FAOP53548.pdf",
        "identity_source": "https://nsearchives.nseindia.com/content/circulars/CML53597.pdf",
        "accepted_source_identity_mismatch_dates": ["2022-09-13"],
        "identity_override_note": "NSE Clearing FAOP53644 and the trade-effective clause in NSE CML53597 adjudicate the new trading ISIN from the 2022-09-13 ex-date; the TejHQ row is preserved as stale source metadata."
    },
]




def publish_ephemeral_workflow_token(token: str) -> bool:
    """Pass a validated token to the next GitHub Actions step via its private environment file."""
    env_file = os.environ.get("GITHUB_ENV", "").strip()
    if not env_file:
        return False
    if not token or "\\n" in token or "\\r" in token:
        raise ValueError("Refusing to publish an invalid ephemeral token.")
    print(f"::add-mask::{token}")
    with Path(env_file).open("a", encoding="utf-8") as handle:
        handle.write(f"DHAN_EPHEMERAL_ACCESS_TOKEN={token}\\n")
    return True


def compute_adjustment_diagnostic(
    dhan_frame: pd.DataFrame,
    raw_frame: pd.DataFrame,
    sample_dates: list[str],
    ex_date: str,
    expected_pre_factor: float,
    expected_pre_isin: str,
    expected_post_isin: str,
    accepted_source_identity_mismatch_dates: list[str] | None = None,
) -> dict:
    """Compare adjusted OHLC with raw NSE bhavcopy; output ratios only, never prices."""
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
    isin_values = sorted(set(right["isin"].dropna().astype(str).str.strip().str.upper()) - {""})
    expected_isins = {expected_pre_isin.upper(), expected_post_isin.upper()}
    if set(isin_values) != expected_isins:
        return {"status": "ISIN_SET_MISMATCH", "dates_checked": 0, "dates_matched": 0,
                "raw_unique_isin_count": len(isin_values)}

    joined = left.merge(right, on="session_date", suffixes=("_dhan", "_raw"), validate="one_to_one")
    identity_mismatch_dates = []
    identity_mismatch_types = {}
    observed_post_isin_dates = []
    for _, identity_row in joined.iterrows():
        identity_day = str(identity_row["session_date"])
        expected_isin = expected_pre_isin.upper() if identity_day < ex_date else expected_post_isin.upper()
        actual_isin = str(identity_row["isin"]).strip().upper()
        if actual_isin == expected_post_isin.upper():
            observed_post_isin_dates.append(identity_day)
        if actual_isin != expected_isin:
            identity_mismatch_dates.append(identity_day)
            if actual_isin == expected_pre_isin.upper() and identity_day >= ex_date:
                identity_mismatch_types[identity_day] = "OLD_ISIN_ON_OR_AFTER_EX_DATE"
            elif actual_isin == expected_post_isin.upper() and identity_day < ex_date:
                identity_mismatch_types[identity_day] = "NEW_ISIN_BEFORE_EX_DATE"
            else:
                identity_mismatch_types[identity_day] = "UNEXPECTED_ISIN"
    present_dates = set(joined["session_date"].astype(str))
    missing = sorted(set(sample_dates) - present_dates)
    if len(joined) != len(sample_dates):
        return {"status": "INCOMPLETE_DATE_MATCH", "dates_checked": int(len(joined)),
                "dates_matched": int(len(joined)), "missing_dates": missing,
                "raw_unique_isin_count": 1}

    pre_ratios = {field: [] for field in PRICE_FIELDS}
    post_ratios = {field: [] for field in PRICE_FIELDS}
    for _, row in joined.iterrows():
        day = str(row["session_date"])
        for field in PRICE_FIELDS:
            try:
                dhan_value = float(row[f"{field}_dhan"])
                raw_value = float(row[f"{field}_raw"])
            except (TypeError, ValueError):
                return {"status": "INVALID_PRICE_OBSERVATION", "dates_checked": int(len(joined)),
                        "dates_matched": int(len(joined)), "raw_unique_isin_count": 1}
            if not np.isfinite(dhan_value) or not np.isfinite(raw_value) or dhan_value <= 0 or raw_value <= 0:
                return {"status": "INVALID_PRICE_OBSERVATION", "dates_checked": int(len(joined)),
                        "dates_matched": int(len(joined)), "raw_unique_isin_count": 1}
            ratio = dhan_value / raw_value
            (pre_ratios if day < ex_date else post_ratios)[field].append(ratio)

    if min((len(x) for x in pre_ratios.values()), default=0) < 3 or min((len(x) for x in post_ratios.values()), default=0) < 3:
        return {"status": "INSUFFICIENT_PRE_POST_SESSIONS", "dates_checked": int(len(joined)),
                "dates_matched": int(len(joined)), "raw_unique_isin_count": 1}

    pre_median = {field: float(np.median(values)) for field, values in pre_ratios.items()}
    post_median = {field: float(np.median(values)) for field, values in post_ratios.items()}
    relative_factor = {field: pre_median[field] / post_median[field] for field in PRICE_FIELDS}
    lower, upper = expected_pre_factor * 0.95, expected_pre_factor * 1.05
    factor_ok = all(lower <= value <= upper for value in relative_factor.values())
    post_ok = all(POST_FACTOR_TOLERANCE[0] <= value <= POST_FACTOR_TOLERANCE[1] for value in post_median.values())
    accepted_identity_dates = set(accepted_source_identity_mismatch_dates or [])
    identity_override_applied_dates = sorted(set(identity_mismatch_dates) & accepted_identity_dates)
    identity_unresolved_dates = sorted(set(identity_mismatch_dates) - accepted_identity_dates)
    identity_ok = not identity_unresolved_dates
    if factor_ok and post_ok and identity_ok:
        diagnostic_status = "PASS_ADJUSTMENT_FACTOR"
    elif factor_ok and post_ok and not identity_ok:
        diagnostic_status = "FACTOR_PASS_IDENTITY_WARNING"
    else:
        diagnostic_status = "FAIL_OR_INCOMPLETE_FACTOR"
    return {
        "status": diagnostic_status,
        "dates_checked": int(len(joined)), "dates_matched": int(len(joined)),
        "pre_ex_date_session_count": int((joined["session_date"].astype(str) < ex_date).sum()),
        "post_ex_date_session_count": int((joined["session_date"].astype(str) >= ex_date).sum()),
        "raw_unique_isin_count": len(isin_values), "isin_transition_verified": identity_ok,
        "identity_mismatch_dates": identity_mismatch_dates,
        "identity_mismatch_type_by_date": identity_mismatch_types,
        "identity_override_applied_dates": identity_override_applied_dates,
        "identity_unresolved_dates": identity_unresolved_dates,
        "observed_post_isin_first_date": (min(observed_post_isin_dates) if observed_post_isin_dates else None) if expected_pre_isin.upper() != expected_post_isin.upper() else None,
        "expected_pre_ex_date_factor": float(expected_pre_factor),
        "pre_ex_date_median_dhan_to_raw_by_ohlc": {k: round(v, 6) for k, v in pre_median.items()},
        "post_ex_date_median_dhan_to_raw_by_ohlc": {k: round(v, 6) for k, v in post_median.items()},
        "relative_event_factor_by_ohlc": {k: round(v, 6) for k, v in relative_factor.items()},
        "pre_factor_tolerance": [round(lower, 6), round(upper, 6)],
        "post_factor_tolerance": list(POST_FACTOR_TOLERANCE),
        "factor_check_passed": factor_ok, "post_factor_check_passed": post_ok,
        "raw_prices_published": False, "isin_published": False,
    }


def public_event_metadata(event: dict) -> dict:
    keys = ("symbol", "action", "ex_date", "expected_pre_factor", "sample_dates",
            "issuer_source", "exchange_source", "identity_source",
            "accepted_source_identity_mismatch_dates", "identity_override_note")
    return {key: event.get(key) for key in keys}


def write_report(result: dict) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Dhan Daily Adjusted-Price Corporate-Action Diagnostics", "",
        f"**Updated:** {result.get('updated_at_utc')}",
        f"**Overall status:** {result.get('status')}",
        f"**Dhan daily endpoint:** {DAILY_URL}", "",
        "| Symbol | Event | Ex-date | Expected pre factor | Matched dates | Relative OHLC factors | Status |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for item in result.get("events", []):
        d = item.get("diagnostic", {})
        lines.append(
            f"| {item.get('symbol')} | {item.get('action')} | {item.get('ex_date')} | "
            f"{item.get('expected_pre_factor')} | {d.get('dates_matched', 0)}/{len(item.get('sample_dates', []))} | "
            f"{d.get('relative_event_factor_by_ohlc', {})} | {item.get('status')} |"
        )
        lines += ["", f"### {item.get('symbol')} — {item.get('action')}", "",
                  f"- Issuer source: {item.get('issuer_source')}",
                  f"- Exchange adjustment source: {item.get('exchange_source')}",
                  f"- Security identity transition source: {item.get('identity_source')}",
                  f"- ISIN transition verified after adjudication: {d.get('isin_transition_verified')}",
                  f"- Source identity override dates: {d.get('identity_override_applied_dates', [])}",
                  f"- Override note: {item.get('identity_override_note')}",
                  f"- Pre-event Dhan/raw median ratios: {d.get('pre_ex_date_median_dhan_to_raw_by_ohlc')}",
                  f"- Post-event Dhan/raw median ratios: {d.get('post_ex_date_median_dhan_to_raw_by_ohlc')}",
                  f"- Relative event factors: {d.get('relative_event_factor_by_ohlc')}",
                  f"- Encrypted TejHQ cache hit: {item.get('tejhq_cache', {}).get('encrypted_cache_hit')}", ""]
    lines += [
        "## Data and privacy", "",
        "- Raw Dhan/TejHQ prices and ISINs are not written to reports or artifacts.",
        "- TejHQ raw partitions are used only under the personal-use-only workflow opt-in and retained only as AES-GCM encrypted Actions cache.",
        "- Dhan API credentials and tokens are runtime-only; no token values are logged.",
        "- These two event diagnostics do not validate dividends, rights, mergers, demergers or buybacks.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run() -> dict:
    result = {
        "status": "BLOCKED", "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "events": [], "raw_prices_published": False, "raw_event_rows_published": False,
        "credentials_or_tokens_recorded": False,
    }
    if not personal_use_fallback_authorized(os.environ.get("TEJHQ_PERSONAL_USE_ONLY")):
        result["status"] = "BLOCKED_PERSONAL_USE_NOT_CONFIRMED"
        return result
    hf_token = os.environ.get("HF_TOKEN", "").strip()
    if not hf_token:
        result["status"] = "BLOCKED_HF_TOKEN_MISSING"
        return result
    try:
        token, client_id, auth_method, refresh_status, auth_diagnostics = acquire_access_token()
        result["auth_method"] = auth_method
        result["token_refresh_status"] = refresh_status
        result["token_refresh_diagnostics"] = auth_diagnostics
        profile = request_profile(token)
        if not profile.ok:
            result["status"] = f"BLOCKED_PROFILE_HTTP_{profile.status_code}"
            return result
        if str(profile.json().get("dataPlan", "")).strip().casefold() != "active":
            result["status"] = "BLOCKED_DATA_PLAN_NOT_ACTIVE"
            return result
        result["data_plan_active"] = True
        result["ephemeral_token_handoff"] = (
            "PUBLISHED_TO_PRIVATE_GITHUB_ENV" if publish_ephemeral_workflow_token(token)
            else "NOT_RUNNING_IN_GITHUB_ACTIONS"
        )

        master_response = requests.get(MASTER_URL, timeout=45)
        master_response.raise_for_status()
        master = pd.read_csv(io.BytesIO(master_response.content), low_memory=False)
        all_symbols = [event["symbol"] for event in EVENTS]
        resolved = resolve_ids(master, all_symbols)
        result["resolved_event_symbols"] = len(resolved)
        if len(resolved) != len(all_symbols):
            result["status"] = "BLOCKED_SECURITY_ID_UNRESOLVED"
            return result

        cache_dir = resolve_tejhq_encrypted_cache_dir(os.environ.get("TEJHQ_ENCRYPTED_CACHE_DIR"))
        partitions: dict[int, pd.DataFrame] = {}
        partition_meta: dict[int, dict] = {}
        for event in EVENTS:
            symbol = event["symbol"]
            sample_dates = event["sample_dates"]
            year = int(event["raw_year"])
            if year not in partitions:
                partitions[year], partition_meta[year] = load_tejhq_nse_year(year, hf_token, cache_dir)
            summary, raw_rows = inspect_tejhq_member_rows(partitions[year], symbol, sample_dates)
            event_result = public_event_metadata(event)
            event_result["tejhq_cache"] = {
                "encrypted_cache_hit": bool(partition_meta[year].get("encrypted_cache_hit")),
                "raw_partition_sha256": partition_meta[year].get("raw_file_sha256"),
                "dataset_revision": partition_meta[year].get("dataset_revision"),
                "valid_sample_sessions": len(summary.get("valid_session_dates", [])),
                "unique_isin_count": summary.get("unique_isin_count"),
                "raw_values_persisted": False,
            }
            expected_isin_count = len({event["expected_pre_isin"], event["expected_post_isin"]})
            if summary.get("valid_session_dates") != sorted(sample_dates) or summary.get("unique_isin_count") != expected_isin_count:
                event_result["status"] = "BLOCKED_RAW_REFERENCE_QA"
                event_result["raw_reference_qa"] = {
                    "valid_session_count": len(summary.get("valid_session_dates", [])),
                    "duplicate_session_count": summary.get("duplicate_session_count"),
                    "invalid_ohlc_row_count": summary.get("invalid_ohlc_row_count"),
                    "invalid_volume_row_count": summary.get("invalid_volume_row_count"),
                    "unique_isin_count": summary.get("unique_isin_count"),
                }
                result["events"].append(event_result)
                continue

            body, attempts = request_daily_history(
                resolved[symbol], token, client_id, min(sample_dates),
                (date.fromisoformat(max(sample_dates)) + timedelta(days=1)).isoformat(),
            )
            event_result["dhan_daily_request_attempts"] = attempts
            dhan_frame, parse_error = parse_daily_payload(body)
            if dhan_frame is None or dhan_frame.empty:
                event_result["status"] = "BLOCKED_DHAN_DAILY_" + str(parse_error or "NO_BARS")
                result["events"].append(event_result)
                continue

            diagnostic = compute_adjustment_diagnostic(
                dhan_frame, raw_rows, sample_dates, event["ex_date"], event["expected_pre_factor"],
                event["expected_pre_isin"], event["expected_post_isin"],
                event.get("accepted_source_identity_mismatch_dates", []),
            )
            event_result["diagnostic"] = diagnostic
            event_result["status"] = diagnostic["status"]
            result["events"].append(event_result)

        result["encrypted_partition_cache_hits"] = sum(
            int(meta.get("encrypted_cache_hit", False)) for meta in partition_meta.values()
        )
        result["encrypted_partition_downloads"] = sum(
            int(not meta.get("encrypted_cache_hit", False)) for meta in partition_meta.values()
        )
        result["status"] = (
            "PASS_ALL_EVENT_ADJUSTMENTS"
            if len(result["events"]) == len(EVENTS)
            and all(item.get("status") == "PASS_ADJUSTMENT_FACTOR" for item in result["events"])
            else "PARTIAL_OR_BLOCKED"
        )
        return result
    except Exception as exc:
        result["status"] = "BLOCKED_RUNTIME_ERROR"
        result["error_type"] = type(exc).__name__
        return result


def main() -> int:
    result = run()
    write_report(result)
    print("C1_DHAN_ADJUSTMENT_DIAGNOSTIC", result["status"])
    for item in result.get("events", []):
        diagnostic = item.get("diagnostic", {})
        print("C1_DHAN_ADJUSTMENT_EVENT", item.get("symbol"), item.get("status"),
              "dates=", diagnostic.get("dates_matched", 0),
              "relative_factor=", diagnostic.get("relative_event_factor_by_ohlc", {}))
    print("Dhan adjusted-price diagnostics complete; raw price values withheld.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
