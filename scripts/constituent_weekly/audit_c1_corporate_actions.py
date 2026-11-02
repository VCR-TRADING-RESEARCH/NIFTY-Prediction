from __future__ import annotations

import hashlib
import io
import json
import os
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))

from scripts.constituent_weekly.audit_c1_daily_history import (
    TEJHQ_REPO_ID, TEJHQ_REVISION, decrypt_tejhq_cache_bytes,
    encrypt_tejhq_cache_bytes, personal_use_fallback_authorized,
    resolve_tejhq_encrypted_cache_dir,
)
from scripts.constituent_weekly.security_identity import point_in_time_symbol

MEMBERSHIP = ROOT / "data/constituent_weekly/nifty50_membership_intervals.csv"
ALIASES = ROOT / "data/constituent_weekly/security_alias_history.csv"
OUT_JSON = ROOT / "research/constituent_weekly/C1_CORPORATE_ACTION_AUDIT.json"
OUT_MD = ROOT / "research/constituent_weekly/C1_CORPORATE_ACTION_AUDIT_REPORT.md"
START, END = "2018-04-01", "2026-10-30"
REQUIRED = {
    "exchange", "symbol", "isin", "company", "ex_date", "record_date", "type",
    "ratio_num", "ratio_den", "cash_amount", "face_value_from", "face_value_to", "raw_subject",
}
TYPE_MAP = {
    "dividend": "dividend", "split": "split", "bonus": "bonus", "rights": "rights",
    "buyback": "buyback", "merger": "merger_demerger", "demerger": "merger_demerger",
    "agm": "agm_or_other", "other": "agm_or_other",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalise_type(value: object) -> str:
    return TYPE_MAP.get(str(value or "").strip().lower(), "unclassified")


def load_member_intervals(path: Path = MEMBERSHIP) -> pd.DataFrame:
    data = pd.read_csv(path, dtype=str, keep_default_na=False)
    required = {"symbol", "valid_from", "valid_to", "member_type", "market_data_required"}
    if required - set(data.columns):
        raise ValueError("Point-in-time membership schema is incomplete.")
    data = data.loc[
        data["member_type"].eq("equity_security")
        & data["market_data_required"].str.upper().eq("TRUE")
    ].copy()
    return data


def load_action_year(year: int, token: str, cache_dir: Path) -> tuple[pd.DataFrame, dict]:
    # The cache directory is resolved by the shared C1 helper used by daily OHLCV.
    from cryptography.exceptions import InvalidTag

    filename = f"actions/nse_{year}.parquet"
    target = cache_dir / f"actions_nse_{year}.parquet.aesgcm"
    aad = f"{TEJHQ_REPO_ID}@{TEJHQ_REVISION}:{filename}".encode()
    cache_dir.mkdir(parents=True, exist_ok=True)
    raw = None
    hit = False
    if target.is_file():
        try:
            raw = decrypt_tejhq_cache_bytes(target.read_bytes(), token, aad)
            hit = True
        except (InvalidTag, ValueError):
            target.unlink(missing_ok=True)
    if raw is None:
        with tempfile.TemporaryDirectory(prefix="bup01-action-") as tmp:
            path = hf_hub_download(
                repo_id=TEJHQ_REPO_ID, filename=filename, repo_type="dataset",
                revision=TEJHQ_REVISION, token=token, cache_dir=str(Path(tmp) / "hf"),
            )
            raw = Path(path).read_bytes()
        temp = target.with_suffix(".tmp")
        temp.write_bytes(encrypt_tejhq_cache_bytes(raw, token, aad))
        temp.replace(target)
    frame = pd.read_parquet(io.BytesIO(raw))
    missing = REQUIRED - set(frame.columns)
    if missing:
        raise ValueError(f"Action partition {year} is missing columns: {sorted(missing)}")
    return frame, {
        "year": year, "sha256": sha256(raw), "encrypted_cache_hit": hit,
        "raw_bytes": len(raw), "rows": len(frame),
    }


def match_member_keys(symbol: str, ex_date: str, intervals: pd.DataFrame) -> list[str]:
    matches = []
    for row in intervals.itertuples(index=False):
        if ex_date < row.valid_from or (row.valid_to and ex_date >= row.valid_to):
            continue
        if point_in_time_symbol(row.symbol, ex_date, ALIASES) == symbol:
            matches.append(row.symbol)
    return sorted(set(matches))


def catalogue(partitions: list[pd.DataFrame], intervals: pd.DataFrame) -> dict:
    if not partitions:
        raise ValueError("No action partitions supplied.")
    frame = pd.concat(partitions, ignore_index=True)
    frame["exchange"] = frame["exchange"].astype("string").str.upper().str.strip()
    frame["symbol"] = frame["symbol"].astype("string").str.upper().str.strip()
    frame["ex_date"] = pd.to_datetime(frame["ex_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    frame["event_class"] = frame["type"].map(normalise_type)
    frame = frame.loc[
        frame["exchange"].eq("NSE") & frame["ex_date"].between(START, END, inclusive="both")
    ].copy()
    raw_count = len(frame)
    duplicate_key = ["exchange", "symbol", "isin", "ex_date", "type"]
    duplicates = int(frame.duplicated(duplicate_key).sum())
    frame = frame.drop_duplicates(duplicate_key)
    all_types, matched_types, unresolved_types = Counter(), Counter(), Counter()
    matched = unmatched = ambiguous = missing_isin = 0
    fingerprints = set()
    yearly = Counter()
    for row in frame.itertuples(index=False):
        kind = row.event_class
        all_types[kind] += 1
        yearly[str(row.ex_date)[:4]] += 1
        missing_isin += int(not str(row.isin or "").strip())
        member_matches = match_member_keys(str(row.symbol), str(row.ex_date), intervals)
        if len(member_matches) == 1:
            matched += 1
            matched_types[kind] += 1
        elif len(member_matches) > 1:
            ambiguous += 1
            unresolved_types[kind] += 1
        else:
            unmatched += 1
            unresolved_types[kind] += 1
        key = "|".join([str(row.symbol), str(row.isin or ""), str(row.ex_date), str(row.type)])
        fingerprints.add(sha256(key.encode()))
    methods = {
        "dividend": "Needs previous raw close and confirmed cash amount; candidate factor (previous_close-cash)/previous_close; not calculated.",
        "split": "Check face_value_to/face_value_from against issuer/exchange notice; not applied.",
        "bonus": "Verify source ratio semantics and issuer notice before calculating a factor; not applied.",
        "rights": "TERP requires entitlement ratio and subscription price; manual review required.",
        "buyback": "No mechanical price factor; keep as a separately dated event feature.",
        "merger_demerger": "No generic scaling or cross-security stitching; exclude affected cycles until scheme terms are verified.",
        "agm_or_other": "Review source subject and issuer filing before classification.",
        "unclassified": "Unknown event class; affected windows remain unresolved.",
    }
    return {
        "status": "COMPLETED_WITH_REVIEW_REQUIRED",
        "corporate_action_gate": "NOT_PASSED",
        "start_date": START, "end_date": END,
        "raw_rows_in_window": raw_count,
        "deduplicated_events": len(frame),
        "duplicate_rows": duplicates,
        "matched_pit_member_events": matched,
        "unmatched_or_non_member_events": unmatched,
        "ambiguous_member_events": ambiguous,
        "missing_isin_events": missing_isin,
        "unique_event_fingerprints": len(fingerprints),
        "events_by_type": dict(sorted(all_types.items())),
        "matched_events_by_type": dict(sorted(matched_types.items())),
        "unresolved_events_by_type": dict(sorted(unresolved_types.items())),
        "events_by_year": dict(sorted(yearly.items())),
        "adjustment_method_disposition": methods,
        "independent_exchange_or_issuer_verification": "NOT_COMPLETED",
        "raw_event_rows_published": False,
        "limitations": [
            "Discovery catalogue only; no adjustment factors calculated or applied.",
            "Source-reported ISIN may be stale across restructurings; symbol/date matching is not proof of identity.",
            "Rights, mergers, demergers, buybacks and unclassified actions need event-specific handling.",
            "Independent exchange/issuer circular review is still required.",
            "TejHQ terms do not grant exchange-data rights; exchange terms apply independently.",
        ],
    }


def write_outputs(result: dict, metadata: list[dict]) -> None:
    result["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    result["source"] = {
        "dataset": TEJHQ_REPO_ID, "revision": TEJHQ_REVISION,
        "years": [m["year"] for m in metadata],
        "partition_sha256": {str(m["year"]): m["sha256"] for m in metadata},
        "encrypted_cache_hits": sum(int(m["encrypted_cache_hit"]) for m in metadata),
        "partitions_downloaded": sum(int(not m["encrypted_cache_hit"]) for m in metadata),
        "raw_data_persisted_to_repo_or_artifact": False,
        "license_scope": "PERSONAL_USE_ONLY; no client/business use; no raw redistribution; exchange terms apply independently",
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# C1 Corporate-Action Candidate Catalogue", "",
        f"**Updated:** {result['updated_at_utc']}",
        f"**Status:** {result['status']}; corporate-action gate NOT PASSED",
        f"**Window:** {START} to {END}", "",
        "## Aggregate counts", "",
        f"- Candidate NSE action rows: {result['raw_rows_in_window']}",
        f"- Deduplicated event rows: {result['deduplicated_events']}",
        f"- Duplicate rows: {result['duplicate_rows']}",
        f"- Matched to point-in-time members by effective symbol alias: {result['matched_pit_member_events']}",
        f"- Unmatched/non-member: {result['unmatched_or_non_member_events']}",
        f"- Ambiguous member events: {result['ambiguous_member_events']}",
        f"- Missing ISIN: {result['missing_isin_events']}", "",
        "| Action class | All | Matched member | Unresolved |",
        "|---|---:|---:|---:|",
    ]
    for kind, n in result["events_by_type"].items():
        lines.append(f"| {kind} | {n} | {result['matched_events_by_type'].get(kind,0)} | {result['unresolved_events_by_type'].get(kind,0)} |")
    lines += ["", "## Adjustment handling", ""]
    lines += [f"- **{kind}:** {method}" for kind, method in result["adjustment_method_disposition"].items()]
    lines += [
        "", "## Cache and source controls", "",
        f"- Pinned revision: {TEJHQ_REVISION}",
        f"- Encrypted cache hits: {result['source']['encrypted_cache_hits']}",
        f"- New partitions downloaded: {result['source']['partitions_downloaded']}",
        "- Only AES-256-GCM ciphertext is retained in Actions cache.",
        "- Raw action rows, ISINs, cash values, ratios and source subjects are not published.",
        "", "**Conclusion:** candidate events are catalogued, but no return adjustment or C1 corporate-action pass is claimed.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if not personal_use_fallback_authorized(os.environ.get("TEJHQ_PERSONAL_USE_ONLY")):
        raise SystemExit("Explicit personal-use source guard is required.")
    token = os.environ.get("HF_TOKEN", "").strip()
    if not token:
        raise SystemExit("HF_TOKEN is missing.")
    cache_dir = resolve_tejhq_encrypted_cache_dir(os.environ.get("TEJHQ_ENCRYPTED_CACHE_DIR"))
    intervals = load_member_intervals()
    frames, metadata = [], []
    for year in range(2018, 2027):
        frame, meta = load_action_year(year, token, cache_dir)
        frames.append(frame)
        metadata.append(meta)
        print(f"C1_ACTION_PARTITION year={year} rows={meta['rows']} cache_hit={meta['encrypted_cache_hit']}")
    result = catalogue(frames, intervals)
    write_outputs(result, metadata)
    print("C1_CORPORATE_ACTION_STATUS", result["status"], "MATCHED", result["matched_pit_member_events"],
          "CACHE_HITS", sum(int(m["encrypted_cache_hit"]) for m in metadata))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
