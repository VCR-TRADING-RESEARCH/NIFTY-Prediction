from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests

BASE = "https://amcs.fund"
API_BASE = f"{BASE}/api/v1"
TIMEOUT = (15, 45)
MAX_RESPONSE_BYTES = 20 * 1024 * 1024
TARGET_SCHEME_TOKENS = ("nifty", "bees")
SAFE_FIELDS = {
    "id", "amc_id", "scheme_id", "slug", "code", "name", "title",
    "amc", "fund_house", "scheme_name", "display_name", "month",
    "period", "date", "disclosure_date", "published_at", "publication_date",
    "url", "source_url", "original_url", "file_url", "download_url",
    "archive_url", "internet_archive_url", "archived_url",
}
URL_FIELDS = {
    "url", "source_url", "original_url", "file_url", "download_url",
    "archive_url", "internet_archive_url", "archived_url",
}
ALLOWED_HOSTS = {"amcs.fund", "mf.nipponindiaim.com", "web.archive.org", "archive.org"}
OUTPUT = Path("research/constituent_weekly/C1_AMCS_API_DISCOVERY_REPORT.md")


def _safe_scalar(value: Any) -> str | int | float | bool | None:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return None


def _record_summary(record: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in record.items():
        key_l = str(key).lower()
        if key_l not in SAFE_FIELDS:
            continue
        scalar = _safe_scalar(value)
        if scalar is None or scalar == "":
            continue
        if key_l in URL_FIELDS and isinstance(scalar, str):
            absolute = urljoin(BASE, scalar)
            parsed = urlparse(absolute)
            if parsed.scheme == "https" and parsed.hostname in ALLOWED_HOSTS:
                result[key_l] = absolute
        else:
            result[key_l] = scalar
    return result


def _walk_dicts(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_dicts(child)


def _record_text(record: dict[str, Any]) -> str:
    parts = []
    for key, value in record.items():
        if isinstance(value, (str, int, float)):
            parts.append(str(value))
    return " ".join(parts).lower()


def _fetch_json(session: requests.Session, url: str) -> tuple[Any | None, dict[str, Any]]:
    meta: dict[str, Any] = {"url": url, "status": "NOT_STARTED"}
    response = None
    chunks: list[bytes] = []
    total = 0
    try:
        response = session.get(url, timeout=TIMEOUT, stream=True)
        meta["http_status"] = response.status_code
        meta["content_type"] = response.headers.get("Content-Type", "")
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=256 * 1024):
            if not chunk:
                continue
            total += len(chunk)
            if total > MAX_RESPONSE_BYTES:
                raise ValueError("JSON response exceeds configured size limit")
            chunks.append(chunk)
        payload = b"".join(chunks)
        parsed = json.loads(payload.decode("utf-8-sig"))
        meta.update({
            "status": "PASS_JSON",
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "top_level_type": type(parsed).__name__,
            "top_level_keys": sorted(list(parsed.keys()))[:30] if isinstance(parsed, dict) else [],
            "top_level_records": len(parsed) if isinstance(parsed, (list, dict)) else None,
        })
        return parsed, meta
    except Exception as exc:
        meta.update({
            "status": "ERROR",
            "error_type": type(exc).__name__,
            "error": str(exc)[:180],
            "bytes": total,
        })
        return None, meta
    finally:
        if response is not None:
            response.close()


def _matching_records(payload: Any, contains: tuple[str, ...]) -> list[dict[str, Any]]:
    matches = []
    seen = set()
    for record in _walk_dicts(payload):
        text = _record_text(record)
        if all(token in text for token in contains):
            summary = _record_summary(record)
            fingerprint = json.dumps(summary, sort_keys=True, default=str)
            if summary and fingerprint not in seen:
                matches.append(summary)
                seen.add(fingerprint)
    return matches[:50]


def _first_identifier(records: list[dict[str, Any]]) -> str | None:
    for record in records:
        for key in ("id", "amc_id", "slug", "code"):
            value = record.get(key)
            if value is not None and re.fullmatch(r"[A-Za-z0-9_-]{1,100}", str(value)):
                return str(value)
    return None


def _source_links(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    links = []
    seen = set()
    for record in records:
        for key in URL_FIELDS:
            url = record.get(key)
            if not isinstance(url, str):
                continue
            parsed = urlparse(url)
            if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
                continue
            if url not in seen:
                links.append({"field": key, "url": url})
                seen.add(url)
    return links[:30]


def run_probe() -> dict[str, Any]:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "NIFTY-Prediction research metadata source audit/1.0",
        "Accept": "application/json",
    })
    report: dict[str, Any] = {
        "run_time_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Metadata-only source discovery. No holdings endpoint is requested and no holdings values are stored.",
        "api_index": None,
        "amcs": None,
        "amc_detail": None,
        "manifest": None,
        "nippon_amc_matches": [],
        "nifty_bees_scheme_matches": [],
        "historical_source_matches": [],
        "source_links": [],
        "rights_status": "UNVERIFIED — API discovery does not grant reuse, extraction, caching, or redistribution rights.",
    }

    index, index_meta = _fetch_json(session, API_BASE)
    report["api_index"] = index_meta

    amcs, amcs_meta = _fetch_json(session, f"{API_BASE}/amcs")
    report["amcs"] = amcs_meta
    amc_matches = _matching_records(amcs, ("nippon",)) if amcs is not None else []
    report["nippon_amc_matches"] = amc_matches

    amc_id = _first_identifier(amc_matches)
    amc_records: list[dict[str, Any]] = []
    if amc_id:
        detail, detail_meta = _fetch_json(session, f"{API_BASE}/amc/{amc_id}")
        report["amc_detail"] = detail_meta
        if detail is not None:
            amc_records = _matching_records(detail, ("nifty", "bees"))
            report["nifty_bees_scheme_matches"] = amc_records

    manifest, manifest_meta = _fetch_json(session, f"{API_BASE}/manifest")
    report["manifest"] = manifest_meta
    if manifest is not None:
        report["historical_source_matches"] = _matching_records(manifest, ("nippon",))
        report["historical_source_matches"] += _matching_records(manifest, ("nifty", "bees"))
        report["historical_source_matches"] = report["historical_source_matches"][:50]

    report["source_links"] = _source_links(
        report["historical_source_matches"] + report["nifty_bees_scheme_matches"]
    )

    # Only HEAD links on the original AMC or Internet Archive hosts; never download a file.
    head_results = []
    for item in report["source_links"][:20]:
        host = urlparse(item["url"]).hostname
        if host not in {"mf.nipponindiaim.com", "web.archive.org", "archive.org"}:
            continue
        try:
            response = session.head(item["url"], timeout=TIMEOUT, allow_redirects=True)
            head_results.append({
                "field": item["field"],
                "host": urlparse(item["url"]).hostname,
                "http_status": response.status_code,
                "content_type": response.headers.get("Content-Type", ""),
                "content_length": response.headers.get("Content-Length", ""),
            })
            response.close()
        except Exception as exc:
            head_results.append({
                "field": item["field"],
                "host": host or "",
                "error_type": type(exc).__name__,
                "error": str(exc)[:120],
            })
    report["source_link_head_checks"] = head_results
    return report


def render_report(report: dict[str, Any]) -> str:
    def endpoint_row(name: str, meta: dict[str, Any] | None) -> str:
        meta = meta or {}
        return "| {name} | {status} | {http} | {ctype} | {bytes} | {records} |".format(
            name=name,
            status=meta.get("status", "NOT_RUN"),
            http=meta.get("http_status", ""),
            ctype=meta.get("content_type", ""),
            bytes=meta.get("bytes", ""),
            records=meta.get("top_level_records", ""),
        )

    lines = [
        "# C1 amcs.fund API metadata discovery",
        "",
        f"- Run time (UTC): {report['run_time_utc']}",
        "- Scope: **metadata only**; this probe does not request a scheme holdings endpoint, download workbooks, or store constituent values.",
        "- Rights: **UNVERIFIED**. Public API access is not treated as permission for commercial/trading-research extraction, caching, or redistribution.",
        "",
        "| Endpoint | Result | HTTP | Content type | Bytes | Top-level records |",
        "|---|---|---:|---|---:|---:|",
        endpoint_row("API index", report.get("api_index")),
        endpoint_row("/amcs", report.get("amcs")),
        endpoint_row("Nippon AMC detail", report.get("amc_detail")),
        endpoint_row("/manifest", report.get("manifest")),
        "",
        "## Nippon AMC metadata matches",
        "",
    ]
    if report.get("nippon_amc_matches"):
        for item in report["nippon_amc_matches"][:10]:
            lines.append("- " + json.dumps(item, sort_keys=True, ensure_ascii=False))
    else:
        lines.append("- No Nippon AMC metadata match was returned.")
    lines += ["", "## Nifty BeES scheme metadata matches", ""]
    if report.get("nifty_bees_scheme_matches"):
        for item in report["nifty_bees_scheme_matches"][:20]:
            lines.append("- " + json.dumps(item, sort_keys=True, ensure_ascii=False))
    else:
        lines.append("- No scheme metadata match was returned from the AMC detail endpoint.")
    lines += ["", "## Historical source-file metadata matches", ""]
    if report.get("historical_source_matches"):
        for item in report["historical_source_matches"][:30]:
            lines.append("- " + json.dumps(item, sort_keys=True, ensure_ascii=False))
    else:
        lines.append("- No matching historical source metadata was returned by /manifest.")
    lines += ["", "## Whitelisted source-link checks", ""]
    if report.get("source_link_head_checks"):
        for item in report["source_link_head_checks"]:
            lines.append("- " + json.dumps(item, sort_keys=True, ensure_ascii=False))
    else:
        lines.append("- No whitelisted official-AMC or Internet Archive source URL was found to check.")
    lines += [
        "",
        "No portfolio holdings, ISINs, quantities, market values, weights, or source-file bytes were downloaded or stored by this probe.",
        "A source URL or successful HEAD response is not proof of disclosure publication time, point-in-time availability, or permission to use the data.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    report = run_probe()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rendered = render_report(report)
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
