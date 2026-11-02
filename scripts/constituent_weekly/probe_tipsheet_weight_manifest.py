from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests

BASE = "https://tipsheet.markets"
MANIFEST_URL = f"{BASE}/data/v1/manifest.json"
TIMEOUT = (15, 45)
MAX_BYTES = 40 * 1024 * 1024
OUTPUT = Path("research/constituent_weekly/C1_TIPSHEET_WEIGHT_SOURCE_REPORT.md")
URL_KEYS = {"url", "uri", "href", "file", "path", "address", "data_url", "download_url"}
SAFE_KEYS = {
    "name", "title", "slug", "id", "dataset", "description", "source",
    "resolution", "frequency", "unit", "date_start", "date_end",
    "start", "end", "first_date", "last_date", "updated_at",
    "file", "path", "url", "href", "data_url", "download_url",
    "sha256", "hash", "rows", "row_count", "columns,
}
TERMS_NOTE = (
    "Tipsheet says the dataset files are free to fetch and asks users to cite "
    "Tipsheet and the original source named in each dataset's meta. Its page "
    "also states that upstream sources keep their own terms. No blanket licence "
    "to redistribute underlying source data is assumed by this probe."
)


def _walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _safe_url(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    url = urljoin(BASE, value.strip())
    parsed = urlparse(url)
    if parsed.scheme == "https" and parsed.hostname == "tipsheet.markets":
        return url
    return None


def _candidate_records(payload: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in _walk(payload):
        text = " ".join([str(k) for k in item.keys()] + [str(v) for v in item.values() if isinstance(v, (str, int, float))]).lower()
        if "weight" not in text:
            continue
        if not ("nifty 50" in text or "nifty-50" in text or "nifty50" in text):
            continue
        summary: dict[str, Any] = {}
        for key, value in item.items():
            key_l = str(key).lower()
            if key_l not in SAFE_KEYS:
                continue
            if key_l in URL_KEYS:
                safe = _safe_url(value)
                if safe:
                    summary[key_l] = safe
            elif isinstance(value, (str, int, float, bool)) or value is None:
                summary[key_l] = value
            elif isinstance(value, list) and value and all(isinstance(x, (str, int, float)) for x in value[:20]):
                summary[key_l] = value[:20]
        fp = json.dumps(summary, sort_keys=True, default=str)
        if summary and fp not in seen:
            found.append(summary)
            seen.add(fp)
    return found[:100]


def _load() -> tuple[Any | None, dict[str, Any]]:
    response = None
    meta: dict[str, Any] = {"url": MANIFEST_URL, "status": "NOT_STARTED"}
    chunks: list[bytes] = []
    total = 0
    try:
        response = requests.get(
            MANIFEST_URL,
            headers={"User-Agent": "NIFTY-Prediction research data-source audit/1.0", "Accept": "application/json"},
            timeout=TIMEOUT,
            stream=True,
        )
        meta["http_status"] = response.status_code
        meta["content_type"] = response.headers.get("Content-Type", "")
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=256 * 1024):
            if not chunk:
                continue
            total += len(chunk)
            if total > MAX_BYTES:
                raise ValueError("Tipsheet manifest exceeds configured byte limit")
            chunks.append(chunk)
        raw = b"".join(chunks)
        payload = json.loads(raw.decode("utf-8-sig"))
        meta.update({
            "status": "PASS_JSON",
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "root_type": type(payload).__name__,
            "root_keys": sorted(payload.keys())[:50] if isinstance(payload, dict) else [],
            "records": len(payload) if isinstance(payload, (dict, list)) else None,
        })
        return payload, meta
    except Exception as exc:
        meta.update({"status": "ERROR", "error_type": type(exc).__name__, "error": str(exc)[:220], "bytes": total})
        return None, meta
    finally:
        if response is not None:
            response.close()


def build_report() -> str:
    payload, meta = _load()
    candidates = _candidate_records(payload) if payload is not None else []
    lines = [
        "# Tipsheet NIFTY 50 historical weight-data discovery",
        "",
        f"- Probed at (UTC): {datetime.now(timezone.utc).isoformat()}",
        f"- Manifest status: **{meta.get('status')}**; HTTP {meta.get('http_status', '')}; bytes {meta.get('bytes', '')}; SHA-256 {meta.get('sha256', '')}",
        f"- Manifest URL: {MANIFEST_URL}",
        f"- {TERMS_NOTE}",
        "",
        "## Manifest metadata",
        "",
        json.dumps(meta, indent=2, sort_keys=True),
        "",
        f"## NIFTY 50 weight-related candidate entries ({len(candidates)})",
        "",
    ]
    if candidates:
        for candidate in candidates:
            lines.append("- " + json.dumps(candidate, sort_keys=True, ensure_ascii=False))
    else:
        lines.append("- No manifest candidate matched NIFTY 50 plus weight.")
    lines += [
        "",
        "This probe stores only manifest metadata and does not download or store monthly stock-weight values.",
        "A dataset is not admitted until date range, resolution, ISIN/symbol schema, availability timing, upstream source attribution, reuse terms and independent reconstruction error have been reviewed.",
        "Do not redistribute raw or derived weights until the published terms and upstream source terms are clear.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
