from __future__ import annotations

import hashlib, io, json, os, re, tempfile, zipfile
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "research/constituent_weekly/C1_NSE_PR_ARCHIVE_PROBE.json"
OUT_MD = ROOT / "research/constituent_weekly/C1_NSE_PR_ARCHIVE_PROBE.md"
PROBE_DATES = ["2018-04-02", "2024-04-17", "2025-10-14", "2026-04-17"]
TRANSITION = date(2025, 10, 13)
BASE = "https://nsearchives.nseindia.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; NIFTYResearchAudit/1.0)", "Accept": "application/zip,*/*", "Referer": "https://www.nseindia.com/all-reports"}
MAX_BYTES = 40 * 1024 * 1024


def candidate_urls(day: date) -> list[str]:
    stamp = day.strftime("%d%m%y")
    names = [f"PR{stamp}.zip", f"nupr{stamp}.zip"] if day >= TRANSITION else [f"nupr{stamp}.zip", f"PR{stamp}.zip"]
    paths = [f"/content/historical/EQUITIES/{day:%Y}/{day:%b}".upper(), "/archives/equities/bhavcopy/pr"]
    return [BASE + path + "/" + name for path in paths for name in names]


def parse_bundle(raw: bytes, day: date) -> dict:
    if not zipfile.is_zipfile(io.BytesIO(raw)):
        raise ValueError("Response is not a ZIP archive.")
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        members = archive.namelist()
        names = [Path(x).name.lower() for x in members]
        ca = [x for x in names if re.match(r"^(bc|bcd)\d{6,8}\.csv$", x)]
        ann = [x for x in names if re.match(r"^(an|and)\d{6,8}\.txt$", x)]
        board = [x for x in names if re.match(r"^(bm|bmd)\d{6,8}\.txt$", x)]
        if not ca:
            raise ValueError("No documented corporate-action CSV member found.")
        member = next(x for x in members if Path(x).name.lower() == ca[0])
        payload = archive.read(member)
        return {"archive_member_count": len(members), "corporate_action_member": ca[0],
                "corporate_action_header": [str(x) for x in pd.read_csv(io.BytesIO(payload), nrows=0).columns],
                "corporate_action_member_bytes": len(payload), "announcement_member_present": bool(ann),
                "board_meeting_member_present": bool(board), "schema_date": day.isoformat()}


def cache_helpers():
    from scripts.constituent_weekly.audit_c1_daily_history import decrypt_tejhq_cache_bytes, encrypt_tejhq_cache_bytes
    return decrypt_tejhq_cache_bytes, encrypt_tejhq_cache_bytes


def fetch_probe(day: date, session: requests.Session, token: str, cache_dir: Path) -> dict:
    decrypt, encrypt = cache_helpers()
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache = cache_dir / f"nse_pr_{day:%Y%m%d}.zip.aesgcm"
    aad = f"NSE-PR-PROBE:{day.isoformat()}:v1".encode()
    raw, hit, attempts = None, False, []
    if cache.is_file():
        try:
            raw, hit = decrypt(cache.read_bytes(), token, aad), True
        except Exception:
            cache.unlink(missing_ok=True)
    if raw is None:
        for url in candidate_urls(day):
            try:
                response = session.get(url, headers=HEADERS, timeout=20, stream=True)
                status = int(response.status_code)
                if status != 200:
                    attempts.append({"url_path": urlparse(url).path, "http_status": status})
                    response.close()
                    continue
                chunks, size = [], 0
                for chunk in response.iter_content(1024 * 1024):
                    if chunk:
                        size += len(chunk)
                        if size > MAX_BYTES:
                            raise ValueError("Archive exceeds 40 MiB safety limit.")
                        chunks.append(chunk)
                response.close()
                raw = b"".join(chunks)
                if not zipfile.is_zipfile(io.BytesIO(raw)):
                    attempts.append({"url_path": urlparse(url).path, "http_status": status, "valid_zip": False})
                    raw = None
                    continue
                attempts.append({"url_path": urlparse(url).path, "http_status": status, "valid_zip": True})
                cache.write_bytes(encrypt(raw, token, aad))
                break
            except requests.RequestException as exc:
                attempts.append({"url_path": urlparse(url).path, "error_type": type(exc).__name__})
    if raw is None:
        return {"date": day.isoformat(), "status": "NOT_RETRIEVED", "attempts": attempts, "encrypted_cache_hit": False}
    try:
        schema = parse_bundle(raw, day)
        return {"date": day.isoformat(), "status": "SCHEMA_CONFIRMED", "http_attempts": attempts,
                "encrypted_cache_hit": hit, "archive_bytes": len(raw), "archive_sha256": hashlib.sha256(raw).hexdigest(), "schema": schema}
    except Exception as exc:
        return {"date": day.isoformat(), "status": "SCHEMA_UNCONFIRMED", "http_attempts": attempts,
                "encrypted_cache_hit": hit, "archive_bytes": len(raw), "archive_sha256": hashlib.sha256(raw).hexdigest(),
                "error_type": type(exc).__name__, "error": str(exc)[:240]}


def run_probe(token: str, cache_dir: Path) -> dict:
    session = requests.Session()
    try:
        session.get("https://www.nseindia.com/all-reports", headers=HEADERS, timeout=20)
    except requests.RequestException:
        pass
    rows = [fetch_probe(date.fromisoformat(x), session, token, cache_dir) for x in PROBE_DATES]
    confirmed = [x for x in rows if x["status"] == "SCHEMA_CONFIRMED"]
    before = any(date.fromisoformat(x["date"]) < TRANSITION for x in confirmed)
    after = any(date.fromisoformat(x["date"]) >= TRANSITION for x in confirmed)
    return {"updated_at_utc": datetime.now(timezone.utc).isoformat(), "probe_dates": PROBE_DATES,
            "confirmed_archives": len(confirmed), "pre_transition_schema_confirmed": before,
            "post_transition_schema_confirmed": after, "overall_status": "PASS_FIXED_PROBE" if before and after else "PARTIAL_OR_BLOCKED",
            "raw_archives_published": False, "results": rows,
            "limitations": ["Four-date probe only; not complete daily archive coverage.",
                            "Only CSV headers and member presence are inspected; no event rows are published.",
                            "Retrieval does not establish licence for bulk extraction or redistribution.",
                            "No issuer verification or adjustment-factor calculation/application is performed."]}


def write_report(result: dict) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = ["# C1 Official NSE PR Bundle Fixed-Date Probe", "", f"Updated: {result['updated_at_utc']}",
             f"Result: {result['overall_status']}", f"Schema-confirmed archives: {result['confirmed_archives']}/4",
             f"Pre-13-Oct-2025 schema: {result['pre_transition_schema_confirmed']}",
             f"Post-13-Oct-2025 schema: {result['post_transition_schema_confirmed']}", "",
             "| Date | Status | Bytes | SHA-256 | Encrypted cache hit |", "|---|---|---:|---|---|"]
    for item in result["results"]:
        lines.append(f"| {item['date']} | {item['status']} | {item.get('archive_bytes', '')} | {item.get('archive_sha256', '')} | {item.get('encrypted_cache_hit', False)} |")
        schema = item.get("schema")
        if schema:
            lines += ["", f"### Schema: {item['date']}", "", f"- Corporate-action member: {schema['corporate_action_member']}",
                      f"- Header fields: {', '.join(schema['corporate_action_header'])}",
                      f"- Announcement member present: {schema['announcement_member_present']}",
                      f"- Board-meeting member present: {schema['board_meeting_member_present']}", ""]
    lines += ["", "## Limitations", ""] + [f"- {x}" for x in result["limitations"]]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    token = os.environ.get("HF_TOKEN", "").strip()
    if not token:
        raise SystemExit("HF_TOKEN is required for encrypted temporary caching.")
    cache = Path(os.environ.get("NSE_PR_ENCRYPTED_CACHE_DIR", tempfile.gettempdir() + "/nse-pr-encrypted"))
    result = run_probe(token, cache)
    write_report(result)
    print("C1_NSE_PR_PROBE", result["overall_status"], "CONFIRMED", result["confirmed_archives"])
    return 0 if result["confirmed_archives"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
