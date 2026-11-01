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
    "scheme_name", "scheme_id", "family_id", "family_name", "scheme_code",
    "amc_slug", "category", "has_holdings", "variant_count", "plan_type",
    "period", "date", "disclosure_date", "published_at", "publication_date",
    "url", "source_url", "original_url", "file_url", "download_url",
    "archive_url", "internet_archive_url", "archived_url", "original_file_url",
    "archive_file_url", "report_url", "source_file", "source_file_url",
    "report_date", "disclosure_month", "published_date", "publication_date",
    "publication_timestamp", "disclosure_timestamp", "first_seen",
}
URL_FIELDS = {
    "url", "source_url", "original_url", "file_url", "download_url",
    "archive_url", "internet_archive_url", "archived_url", "original_file_url",
    "archive_file_url", "report_url", "source_file_url",
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



def _payload_shape(payload: Any) -> dict[str, Any]:
    """Report JSON schema shape only, never any portfolio/security values."""
    if not isinstance(payload, dict):
        return {"root_type": type(payload).__name__}
    shape: dict[str, Any] = {"root_type": "object", "root_keys": sorted(str(k) for k in payload.keys())[:50]}
    data = payload.get("data")
    shape["data_type"] = type(data).__name__ if data is not None else "null"
    source = payload.get("source")
    shape["source_type"] = type(source).__name__ if source is not None else "null"
    if isinstance(source, dict):
        shape["source_metadata_keys"] = sorted(str(k) for k in source.keys())[:40]
        allowed_hosts = {
            "mf.nipponindiaim.com", "hdfcfund.com", "www.hdfcfund.com",
            "sbimf.com", "www.sbimf.com", "icicipruamc.com", "www.icicipruamc.com",
            "utimf.com", "www.utimf.com", "doc.utimf.com", "archive.org", "web.archive.org",
            "amcs.fund",
        }
        source_urls = {}
        for key, value in source.items():
            if isinstance(value, str):
                parsed = urlparse(value)
                if parsed.scheme == "https" and parsed.hostname in allowed_hosts:
                    source_urls[str(key)] = value
        if source_urls:
            shape["source_urls"] = source_urls
    elif isinstance(source, str):
        parsed = urlparse(source)
        if parsed.scheme == "https" and parsed.hostname:
            shape["source_host"] = parsed.hostname
    if isinstance(data, list):
        shape["data_length"] = len(data)
        if data and isinstance(data[0], dict):
            shape["first_item_keys"] = sorted(str(k) for k in data[0].keys())[:50]
            shape["first_item_nested_types"] = {
                str(k): type(v).__name__ for k, v in list(data[0].items())[:30]
            }
    elif isinstance(data, dict):
        shape["data_keys"] = sorted(str(k) for k in data.keys())[:50]
        shape["data_nested_types"] = {
            str(k): type(v).__name__ for k, v in list(data.items())[:30]
        }
        for field in ("first_month", "prev_month", "unit"):
            value = data.get(field)
            if isinstance(value, (str, int, float, bool)):
                shape[field] = value
        history = data.get("history")
        if isinstance(history, list):
            shape["history_count"] = len(history)
            if history:
                first = history[0]
                last = history[-1]
                shape["history_item_type"] = type(first).__name__
                if isinstance(first, dict):
                    shape["history_item_keys"] = sorted(str(k) for k in first.keys())[:40]
                    for key in ("m", "month", "date", "period"):
                        if isinstance(first.get(key), str):
                            shape["history_first_period"] = first[key]
                            break
                    if isinstance(last, dict):
                        for key in ("m", "month", "date", "period"):
                            if isinstance(last.get(key), str):
                                shape["history_last_period"] = last[key]
                                break
                elif isinstance(first, str) and isinstance(last, str):
                    shape["history_first_period"] = first
                    shape["history_last_period"] = last
        hold_hist = data.get("hold_hist")
        if isinstance(hold_hist, dict):
            shape["hold_hist_type"] = "object"
            shape["hold_hist_entry_count"] = len(hold_hist)
            shape["hold_hist_value_types"] = sorted({type(v).__name__ for v in hold_hist.values()})
            hist_counts = {}
            hist_list_lengths = []
            hist_object_key_sets = []
            hist_month_keys = []
            for key, value in hold_hist.items():
                if isinstance(key, str) and re.fullmatch(r"20\d{2}-\\d{2}", key):
                    hist_month_keys.append(key)
                if isinstance(value, list):
                    hist_counts["list"] = hist_counts.get("list", 0) + 1
                    hist_list_lengths.append(len(value))
                    if value and isinstance(value[0], dict):
                        hist_object_key_sets.append(sorted(str(k) for k in value[0].keys())[:40])
                elif isinstance(value, dict):
                    hist_counts["dict"] = hist_counts.get("dict", 0) + 1
                    for nested_key in value:
                        if isinstance(nested_key, str) and re.fullmatch(r"20\d{2}-\\d{2}", nested_key):
                            hist_month_keys.append(nested_key)
            shape["hold_hist_container_counts"] = hist_counts
            shape["hold_hist_key_count"] = len(hold_hist)
            shape["hold_hist_key_names"] = [
                str(key) for key in list(hold_hist.keys())[:10]
                if re.fullmatch(r"[A-Za-z_]{1,40}", str(key))
                or re.fullmatch(r"20\d{2}-\\d{2}", str(key))
            ]
            if hist_list_lengths:
                shape["hold_hist_list_lengths"] = hist_list_lengths[:20]
            if hist_object_key_sets:
                shape["hold_hist_list_item_keys"] = hist_object_key_sets[:3]
            months = hold_hist.get("months")
            if isinstance(months, list):
                month_values = [x for x in months if isinstance(x, str) and re.fullmatch(r"20\d{2}-\\d{2}", x)]
                shape["hold_hist_month_count"] = len(month_values)
                shape["hold_hist_months"] = months[:20]
                shape["hold_hist_months_normalized"] = month_values[:20]
                shape["hold_hist_month_labels_type"] = sorted({type(x).__name__ for x in months})
                if month_values:
                    shape["hold_hist_first_month"] = min(month_values)
                    shape["hold_hist_last_month"] = max(month_values)
                    shape["hold_hist_months_unique"] = len(set(month_values))
            h = hold_hist.get("h")
            if isinstance(h, dict):
                shape["hold_hist_series_count"] = len(h)
                value_types = sorted({type(value).__name__ for value in h.values()})
                shape["hold_hist_series_value_types"] = value_types
                series_lengths = [len(value) for value in h.values() if isinstance(value, list)]
                if series_lengths:
                    shape["hold_hist_series_length_min"] = min(series_lengths)
                    shape["hold_hist_series_length_max"] = max(series_lengths)
                    shape["hold_hist_series_length_unique"] = sorted(set(series_lengths))
                numeric_series = [
                    value for value in h.values()
                    if isinstance(value, list) and all(isinstance(v, (int, float)) or v is None for v in value)
                ]
                shape["hold_hist_numeric_series_count"] = len(numeric_series)
            for key, value in hold_hist.items():
                if isinstance(value, dict):
                    shape["hold_hist_dict_value_key_count"] = len(value)
                    shape["hold_hist_dict_value_types"] = sorted({type(v).__name__ for v in value.values()})
                    shape["hold_hist_dict_value_key_samples"] = [
                        str(k) for k in list(value.keys())[:10]
                        if re.fullmatch(r"[A-Za-z_]{1,40}", str(k))
                        or re.fullmatch(r"20\d{2}-\\d{2}", str(k))
                    ]
                    break
                if isinstance(value, list) and value:
                    shape["hold_hist_list_item_type"] = type(value[0]).__name__
                    if isinstance(value[0], dict):
                        shape["hold_hist_list_item_keys_detail"] = sorted(str(k) for k in value[0].keys())[:40]
                    break
            if hist_month_keys:
                shape["hold_hist_month_key_count"] = len(set(hist_month_keys))
                shape["hold_hist_first_month_key"] = min(hist_month_keys)
                shape["hold_hist_last_month_key"] = max(hist_month_keys)
        for field in ("history", "holdings", "events", "amcs", "groups", "buys", "sells", "sector_flows"):
            items = data.get(field)
            if isinstance(items, list):
                shape[field + "_count"] = len(items)
                if items and isinstance(items[0], dict):
                    shape[field + "_item_keys"] = sorted(str(k) for k in items[0].keys())[:40]
                    item_url_fields = {}
                    for key, value in items[0].items():
                        if isinstance(value, str) and ("url" in str(key).lower() or "file" in str(key).lower()):
                            parsed = urlparse(value)
                            if parsed.scheme == "https" and parsed.hostname:
                                item_url_fields[str(key)] = parsed.hostname
                    if item_url_fields:
                        shape[field + "_url_hosts"] = item_url_fields
        history = data.get("history")
        if isinstance(history, list):
            dates = []
            for row in history:
                if isinstance(row, dict):
                    for key in ("month", "date", "period", "disclosure_date"):
                        value = row.get(key)
                        if isinstance(value, str) and len(value) >= 7:
                            dates.append(value[:10])
                            break
            if dates:
                shape["history_first_date"] = min(dates)
                shape["history_last_date"] = max(dates)
    return shape


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


def _metadata_records(payload: Any) -> list[dict[str, Any]]:
    """Keep month/source metadata only; exclude individual ISIN holdings rows."""
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    metadata_keys = {
        "id", "month", "period", "date", "disclosure_date", "report_date",
        "published_at", "published_date", "publication_date", "source_url",
        "original_url", "file_url", "download_url", "archive_url",
        "internet_archive_url", "archived_url", "original_file_url",
        "archive_file_url", "report_url", "source_file_url",
    }
    for record in _walk_dicts(payload):
        if any(str(k).lower() == "isin" for k in record):
            continue
        summary = _record_summary(record)
        if not (set(summary) & metadata_keys):
            continue
        fingerprint = json.dumps(summary, sort_keys=True, default=str)
        if summary and fingerprint not in seen:
            records.append(summary)
            seen.add(fingerprint)
    return records[:100]


def _scheme_slug(records: list[dict[str, Any]]) -> str | None:
    for record in records:
        name = str(record.get("name") or record.get("scheme_name") or "").lower()
        slug = record.get("slug") or record.get("scheme_id") or record.get("id")
        if "nifty 50" in name and "bees" in name and isinstance(slug, str):
            if re.fullmatch(r"[A-Za-z0-9_-]{1,120}", slug):
                return slug
    return None


def _month_identifiers(records: list[dict[str, Any]]) -> list[str]:
    ids: list[str] = []
    for record in records:
        value = record.get("id") or record.get("month_id") or record.get("month") or record.get("period")
        if value is not None and re.fullmatch(r"[A-Za-z0-9_-]{1,100}", str(value)):
            candidate = str(value)
            if candidate not in ids:
                ids.append(candidate)
    return ids[:4]


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



TIPSHEET_MANIFEST_URL = "https://tipsheet.markets/data/v1/manifest.json"
TIPSHEET_HOST = "tipsheet.markets"


def _tipsheet_weight_candidates(payload: Any) -> list[dict[str, Any]]:
    """Extract dataset catalog metadata only; do not read any series values."""
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    safe_keys = {
        "name", "title", "slug", "id", "dataset", "description",
        "resolution", "frequency", "unit", "date_start", "date_end",
        "start", "end", "first_date", "last_date", "updated_at",
        "file", "path", "url", "href", "data_url", "download_url",
        "sha256", "hash", "rows", "row_count", "columns",
    }
    url_keys = {"file", "path", "url", "href", "data_url", "download_url"}
    for record in _walk_dicts(payload):
        text = " ".join(
            [str(key) for key in record.keys()]
            + [str(value) for value in record.values() if isinstance(value, (str, int, float))]
        ).lower()
        if "weight" not in text:
            continue
        if not ("nifty 50" in text or "nifty-50" in text or "nifty50" in text):
            continue
        summary: dict[str, Any] = {}
        for key, value in record.items():
            key_l = str(key).lower()
            if key_l not in safe_keys:
                continue
            if key_l in url_keys and isinstance(value, str):
                absolute = urljoin("https://tipsheet.markets", value)
                parsed = urlparse(absolute)
                if parsed.scheme == "https" and parsed.hostname == TIPSHEET_HOST:
                    summary[key_l] = absolute
            elif isinstance(value, (str, int, float, bool)) or value is None:
                summary[key_l] = value
            elif isinstance(value, list) and value and all(isinstance(x, (str, int, float)) for x in value[:20]):
                summary[key_l] = value[:20]
        fingerprint = json.dumps(summary, sort_keys=True, default=str)
        if summary and fingerprint not in seen:
            candidates.append(summary)
            seen.add(fingerprint)
    return candidates[:100]



HTML_PAGES = [
    f"{BASE}/month",
    f"{BASE}/methodology",
    f"{BASE}/scheme/nippon-india-etf-nifty-50-bees",
    "https://www.utimf.com/downloads/scheme-wise-portfolio-disclosure",
    "https://www.utimf.com/downloads/consolidate-all-portfolio-disclosure",
    "https://www.hdfcfund.com/statutory-disclosure/portfolio/monthly-portfolio",
]
ALLOWED_SOURCE_HOSTS = {
    "mf.nipponindiaim.com", "hdfcfund.com", "www.hdfcfund.com",
    "sbimf.com", "www.sbimf.com", "icicipruamc.com", "www.icicipruamc.com",
    "utimf.com", "www.utimf.com", "archive.org", "web.archive.org",
    "amcs.fund", "www.amcs.fund",
}


def _extract_html_metadata(html: str, page_url: str) -> dict[str, Any]:
    """Extract only page/script/source links, not HTML text or portfolio values."""
    script_srcs: list[str] = []
    hrefs: list[str] = []
    page_host = (urlparse(page_url).hostname or "").lower()
    def same_site(host: str) -> bool:
        host = (host or "").lower()
        return host == page_host or (page_host and host.endswith("." + page_host))
    for match in re.findall(r"""<script\b[^>]*\bsrc\s*=\s*["']([^"']+)["'][^>]*>""", html, flags=re.I):
        absolute = urljoin(page_url, match)
        parsed = urlparse(absolute)
        if parsed.scheme == "https" and same_site(parsed.hostname or ""):
            script_srcs.append(absolute)
    for match in re.findall(r"""<a\b[^>]*href\s*=\s*["']([^"']+)["'][^>]*>(.*?)</a>""", html, flags=re.I | re.S):
        target, label = match
        absolute = urljoin(page_url, target)
        parsed = urlparse(absolute)
        label_text = re.sub(r"<[^>]+>", " ", label)
        label_text = re.sub(r"\s+", " ", label_text).strip()[:120]
        if parsed.scheme != "https":
            continue
        if parsed.hostname in ALLOWED_SOURCE_HOSTS:
            hrefs.append({
                "host": parsed.hostname,
                "url": absolute,
                "label": label_text,
            })
    form_actions = []
    for match in re.findall(r"""<form\b[^>]*action\s*=\s*["']([^"']+)["'][^>]*>""", html, flags=re.I):
        target = urljoin(page_url, match)
        parsed = urlparse(target)
        if parsed.scheme == "https" and parsed.hostname in ALLOWED_SOURCE_HOSTS:
            form_actions.append(target)
    select_fields = []
    for match in re.findall(r"""<select\b([^>]*)>(.*?)</select>""", html, flags=re.I | re.S):
        attrs, body = match
        name = re.search(r"""\bname\s*=\s*["']([^"']+)["']""", attrs, flags=re.I)
        ident = re.search(r"""\bid\s*=\s*["']([^"']+)["']""", attrs, flags=re.I)
        options = []
        for value, label in re.findall(r"""<option\b[^>]*value\s*=\s*["']([^"']*)["'][^>]*>(.*?)</option>""", body, flags=re.I | re.S):
            clean = re.sub(r"<[^>]+>", " ", label)
            clean = re.sub(r"\s+", " ", clean).strip()[:80]
            options.append({"value": value[:80], "label": clean})
        select_fields.append({
            "name": name.group(1) if name else "",
            "id": ident.group(1) if ident else "",
            "options_sample": options[:40],
            "options_count": len(options),
        })
    input_fields = []
    for attrs in re.findall(r"""<input\b([^>]*)>""", html, flags=re.I):
        name = re.search(r"""\bname\s*=\s*["']([^"']+)["']""", attrs, flags=re.I)
        ident = re.search(r"""\bid\s*=\s*["']([^"']+)["']""", attrs, flags=re.I)
        kind = re.search(r"""\btype\s*=\s*["']([^"']+)["']""", attrs, flags=re.I)
        if name or ident:
            input_fields.append({
                "name": name.group(1) if name else "",
                "id": ident.group(1) if ident else "",
                "type": kind.group(1) if kind else "",
            })
    inline_patterns = []
    for needle in ("source", "archive", "portfolio", "holdings", "internetarchive", "wayback", "getportfolio", "year", "month"):
        count = len(re.findall(needle, html, flags=re.I))
        if count:
            inline_patterns.append({"term": needle, "count": count})
    return {
        "page_url": page_url,
        "html_bytes": len(html.encode("utf-8")),
        "sha256": hashlib.sha256(html.encode("utf-8")).hexdigest(),
        "script_srcs": list(dict.fromkeys(script_srcs))[:30],
        "source_links": hrefs[:50],
        "form_actions": list(dict.fromkeys(form_actions))[:20],
        "select_fields": select_fields[:20],
        "input_fields": input_fields[:40],
        "pattern_counts": inline_patterns,
    }


def _fetch_html_metadata(session: requests.Session, url: str) -> dict[str, Any]:
    response = None
    try:
        response = session.get(url, timeout=TIMEOUT, allow_redirects=True)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        html = response.text
        meta = _extract_html_metadata(html, response.url)
        meta.update({
            "status": "PASS_HTML",
            "http_status": response.status_code,
            "content_type": content_type,
        })
        return meta
    except Exception as exc:
        return {
            "page_url": url,
            "status": "ERROR",
            "error_type": type(exc).__name__,
            "error": str(exc)[:180],
        }
    finally:
        if response is not None:
            response.close()


def _scan_amcs_script_metadata(session: requests.Session, script_urls: list[str]) -> list[dict[str, Any]]:
    """Fetch bounded same-origin AMC UI scripts and retain route/schema metadata only."""
    results = []
    for url in list(dict.fromkeys(script_urls))[:8]:
        response = None
        try:
            response = session.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            body = response.text
            endpoint_hits = sorted(set(re.findall(
                r"""(?:/api/v1/|/api/|/month/|/scheme/|/source/|/file/|/downloads/|/portfolio/|/documents/)[A-Za-z0-9_./{}?=&<>-]{1,160}""",
                body, flags=re.I
            )))[:100]
            function_hits = sorted(set(re.findall(
                r"""(?:GetPortfolio|GetSchemePortfolio|portfolioDisclosure|schemePortfolio|DownloadPortfolio|fetchPortfolio)[A-Za-z0-9_.$]{0,80}""",
                body, flags=re.I
            )))[:60]
            api_hosts = sorted(set(
                (urlparse(u if "://" in u else "https://" + u).hostname or "")
                for u in re.findall(r"""https?://[^"'\\s<>]{1,240}""", body, flags=re.I)
                if urlparse(u if "://" in u else "https://" + u).hostname
                and (
                    urlparse(u if "://" in u else "https://" + u).hostname in ALLOWED_SOURCE_HOSTS
                    or urlparse(u if "://" in u else "https://" + u).hostname.endswith(".cloudfront.net")
                )
            ))[:30]
            source_hosts = sorted(set(re.findall(
                r"""https?://(?:www\.)?(?:mf\.nipponindiaim\.com|hdfcfund\.com|sbimf\.com|icicipruamc\.com|utimf\.com|archive\.org|web\.archive\.org)[^"'\\s<>]{0,200}""",
                body, flags=re.I
            )))[:50]
            keyword_counts = {
                term: len(re.findall(term, body, flags=re.I))
                for term in ("originalUrl", "archiveUrl", "sourceUrl", "source_file", "archive.org", "wayback")
                if re.search(term, body, flags=re.I)
            }
            results.append({
                "script_url": url,
                "status": "PASS_JS" if response.status_code == 200 else "HTTP_ERROR",
                "http_status": response.status_code,
                "bytes": len(body.encode("utf-8")),
                "sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
                "endpoint_patterns": endpoint_hits,
                "function_patterns": function_hits,
                "api_hosts": api_hosts,
                "whitelisted_url_patterns": source_hosts,
                "source_keyword_counts": keyword_counts,
            })
        except Exception as exc:
            results.append({
                "script_url": url,
                "status": "ERROR",
                "error_type": type(exc).__name__,
                "error": str(exc)[:150],
            })
        finally:
            if response is not None:
                response.close()
    return results



def _mfdata_family_summaries(payload: Any) -> list[dict[str, Any]]:
    """Retain only scheme family identifiers/labels from mfdata search metadata."""
    allowed = {
        "family_id", "family_name", "scheme_code", "scheme_name",
        "amc", "amc_name", "category", "has_holdings", "variant_count",
    }
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in _walk_dicts(payload):
        name = str(record.get("family_name") or record.get("scheme_name") or record.get("name") or "")
        if "nifty 50" not in name.lower():
            continue
        row = {str(k).lower(): v for k, v in record.items()
               if str(k).lower() in allowed and isinstance(v, (str, int, float, bool))}
        if not any(k in row for k in ("family_id", "scheme_code")):
            continue
        fingerprint = json.dumps(row, sort_keys=True, default=str)
        if fingerprint not in seen:
            out.append(row)
            seen.add(fingerprint)
    return out[:100]


def _mfdata_months(payload: Any) -> list[str]:
    """Extract YYYY-MM month labels only; never serialize holdings records."""
    candidates: list[str] = []
    for node in _walk_dicts(payload):
        for value in node.values():
            if isinstance(value, str) and re.fullmatch(r"20\\d{2}-(0[1-9]|1[0-2])", value):
                candidates.append(value)
    if isinstance(payload, list):
        candidates.extend(
            x for x in payload if isinstance(x, str)
            and re.fullmatch(r"20\\d{2}-(0[1-9]|1[0-2])", x)
        )
    return sorted(set(candidates))


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
        "amcs_html_pages": [],
        "amcs_ui_scripts": [],
        "amc_archive_ui_pages": [],
        "amc_archive_ui_scripts": [],
        "amcs": None,
        "amc_detail": None,
        "scheme_detail": None,
        "scheme_detail_shape": None,
        "month_details": [],
        "historical_month_samples": [],
        "manifest": None,
        "tipsheet_manifest": None,
        "tipsheet_weight_candidates": [],
        "mfdata_schemes": None,
        "mfdata_scheme_families": [],
        "mfdata_family_histories": [],
        "nippon_amc_matches": [],
        "amc_catalog_records": [],
        "amc_nifty50_schemes": [],
        "amc_scheme_shapes": [],
        "nifty_bees_scheme_matches": [],
        "scheme_history_metadata": [],
        "month_source_metadata": [],
        "historical_source_matches": [],
        "source_links": [],
        "rights_status": "UNVERIFIED — API discovery does not grant reuse, extraction, caching, or redistribution rights.",
    }

    index, index_meta = _fetch_json(session, API_BASE)
    report["api_index"] = index_meta
    if index is not None:
        if isinstance(index, dict):
            report["api_index_schema"] = {
                "keys": sorted(str(k) for k in index.keys())[:40],
                "endpoint_names": sorted(str(k) for k in index.get("endpoints", {}).keys())[:80]
                    if isinstance(index.get("endpoints"), dict) else [],
                "endpoint_count": len(index.get("endpoints", []))
                    if isinstance(index.get("endpoints"), list) else None,
                "endpoint_item_keys": sorted(str(k) for k in index["endpoints"][0].keys())[:30]
                    if isinstance(index.get("endpoints"), list) and index["endpoints"] and isinstance(index["endpoints"][0], dict) else [],
                "endpoint_paths": (
                    [item for item in index.get("endpoints", []) if isinstance(item, str)][:80]
                    if isinstance(index.get("endpoints"), list) and all(isinstance(item, str) for item in index.get("endpoints", []))
                    else [
                        item.get("path") or item.get("url") or item.get("route")
                        for item in index.get("endpoints", [])
                        if isinstance(item, dict) and isinstance(item.get("path") or item.get("url") or item.get("route"), str)
                    ][:80] if isinstance(index.get("endpoints"), list) else []
                ),
                "docs_type": type(index.get("docs")).__name__,
                "docs_excerpt": index.get("docs", "")[:700] if isinstance(index.get("docs"), str) else None,
                "endpoints_type": type(index.get("endpoints")).__name__,
            }

    for page_url in HTML_PAGES:
        report["amcs_html_pages"].append(_fetch_html_metadata(session, page_url))
    scripts = []
    for page in report["amcs_html_pages"][:3]:
        scripts.extend(page.get("script_srcs", []))
    report["amcs_ui_scripts"] = _scan_amcs_script_metadata(session, scripts)

    # Inspect the primary AMC archive interfaces for year/month selectors and
    # their first-party download routes. This metadata-only probe never submits
    # a portfolio request and never downloads holdings.
    for page in report["amcs_html_pages"][3:]:
        report["amc_archive_ui_pages"].append({
            "page_url": page.get("page_url"),
            "status": page.get("status"),
            "http_status": page.get("http_status"),
            "html_bytes": page.get("html_bytes"),
            "script_src_count": len(page.get("script_srcs", [])),
            "script_srcs_sample": page.get("script_srcs", [])[:30],
            "source_links": page.get("source_links", [])[:20],
            "form_actions": page.get("form_actions", []),
            "select_fields": page.get("select_fields", []),
            "input_fields": page.get("input_fields", []),
            "pattern_counts": page.get("pattern_counts", []),
        })
    archive_scripts = []
    for page in report["amcs_html_pages"][3:]:
        archive_scripts.extend(page.get("script_srcs", []))
    report["amc_archive_ui_scripts"] = _scan_amcs_script_metadata(session, archive_scripts)

    amcs, amcs_meta = _fetch_json(session, f"{API_BASE}/amcs")
    report["amcs"] = amcs_meta
    amc_matches = _matching_records(amcs, ("nippon",)) if amcs is not None else []
    report["nippon_amc_matches"] = amc_matches
    report["amc_catalog_records"] = _metadata_records(amcs) if amcs is not None else []

    amc_id = _first_identifier(amc_matches)
    amc_records: list[dict[str, Any]] = []
    if amc_id:
        detail, detail_meta = _fetch_json(session, f"{API_BASE}/amc/{amc_id}")
        report["amc_detail"] = detail_meta
        if detail is not None:
            amc_records = _matching_records(detail, ("nifty", "bees"))
            report["nifty_bees_scheme_matches"] = amc_records

    # The published API catalog explicitly advertises /scheme/{id} and /month/{id}.
    # Query the scheme-history route with the Nifty 50 BeES slug, but retain only
    # source/month metadata and discard any per-ISIN holdings payload fields.
    scheme_slug = _scheme_slug(report["nifty_bees_scheme_matches"])
    scheme_records: list[dict[str, Any]] = []
    if scheme_slug:
        scheme_payload, scheme_meta = _fetch_json(session, f"{API_BASE}/scheme/{scheme_slug}")
        report["scheme_detail"] = scheme_meta
        if scheme_payload is not None:
            report["scheme_detail_shape"] = _payload_shape(scheme_payload)
            scheme_records = _metadata_records(scheme_payload)
            report["scheme_history_metadata"] = scheme_records

    month_ids = list(dict.fromkeys(_month_identifiers(scheme_records) + ["2019-04", "2022-09", "2025-09", "2026-09"]))[:6]
    for month_id in month_ids:
        month_payload, month_meta = _fetch_json(session, f"{API_BASE}/month/{month_id}")
        month_meta["month_id"] = month_id
        if month_payload is not None:
            month_meta["payload_shape"] = _payload_shape(month_payload)
            report["month_source_metadata"].extend(_metadata_records(month_payload))
        report["month_details"].append(month_meta)
    report["month_source_metadata"] = report["month_source_metadata"][:100]

    tipsheet_payload, tipsheet_meta = _fetch_json(session, TIPSHEET_MANIFEST_URL)
    report["tipsheet_manifest"] = tipsheet_meta
    if tipsheet_payload is not None:
        report["tipsheet_weight_candidates"] = _tipsheet_weight_candidates(tipsheet_payload)

    # Independent free-source check: mfdata.in documents a no-key schemes search
    # and a separate monthly holdings-history endpoint. Only IDs, fund labels and
    # YYYY-MM availability are retained; per-stock holdings responses are never called.
    mfdata_payload, mfdata_meta = _fetch_json(
        session,
        "https://mfdata.in/api/v1/schemes?search=nifty%2050&has_holdings=true&limit=1000",
    )
    report["mfdata_schemes"] = mfdata_meta
    family_summaries = _mfdata_family_summaries(mfdata_payload) if mfdata_payload is not None else []
    report["mfdata_scheme_families"] = family_summaries
    seen_family_ids: set[str] = set()
    for family in family_summaries:
        family_id = family.get("family_id")
        if family_id is None:
            continue
        family_id_s = str(family_id)
        if not re.fullmatch(r"[0-9]{1,12}", family_id_s) or family_id_s in seen_family_ids:
            continue
        seen_family_ids.add(family_id_s)
        if len(seen_family_ids) > 15:
            break
        hist_payload, hist_meta = _fetch_json(
            session,
            f"https://mfdata.in/api/v1/families/{family_id_s}/holdings/history",
        )
        months = _mfdata_months(hist_payload) if hist_payload is not None else []
        report["mfdata_family_histories"].append({
            "family": family,
            "status": hist_meta.get("status"),
            "http_status": hist_meta.get("http_status"),
            "bytes": hist_meta.get("bytes"),
            "month_count": len(months),
            "first_month": months[0] if months else None,
            "last_month": months[-1] if months else None,
            "months_sample": months[:3] + (months[-3:] if len(months) > 3 else []),
            "month_list_sha256": hashlib.sha256("\\n".join(months).encode("utf-8")).hexdigest(),
        })

    # Discover other fund houses' NIFTY 50 index ETFs/funds. Retain only scheme
    # identifiers and schema/date counts, never individual holdings values.
    amc_probe_slugs = []
    for rec in report["amc_catalog_records"]:
        slug = rec.get("slug") or rec.get("id")
        name = str(rec.get("name", "")).lower()
        if isinstance(slug, str) and any(token in name for token in ("hdfc", "uti", "sbi", "icici", "nippon")):
            amc_probe_slugs.append(slug)
    for amc_slug in list(dict.fromkeys(amc_probe_slugs))[:8]:
        amc_payload, amc_meta = _fetch_json(session, f"{API_BASE}/amc/{amc_slug}")
        if amc_payload is None:
            continue
        schemes = _matching_records(amc_payload, ("nifty", "50"))
        for scheme_rec in schemes[:8]:
            scheme_slug = scheme_rec.get("slug") or scheme_rec.get("scheme_id")
            if not isinstance(scheme_slug, str):
                continue
            scheme_payload, scheme_meta = _fetch_json(session, f"{API_BASE}/scheme/{scheme_slug}")
            item = {
                "amc_slug": amc_slug,
                "scheme": scheme_rec,
                "http_status": scheme_meta.get("http_status"),
                "status": scheme_meta.get("status"),
            }
            if scheme_payload is not None:
                item["shape"] = _payload_shape(scheme_payload)
            report["amc_nifty50_schemes"].append(scheme_rec)
            report["amc_scheme_shapes"].append(item)

    manifest, manifest_meta = _fetch_json(session, f"{API_BASE}/manifest")
    report["manifest"] = manifest_meta
    if manifest is not None:
        report["historical_source_matches"] = _matching_records(manifest, ("nippon",))
        report["historical_source_matches"] += _matching_records(manifest, ("nifty", "bees"))
        report["historical_source_matches"] = report["historical_source_matches"][:50]

    report["source_links"] = _source_links(
        report["historical_source_matches"] + report["nifty_bees_scheme_matches"]
        + report["scheme_history_metadata"] + report["month_source_metadata"]
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
        "- Scope: **metadata only**; the probe inspects AMC archive UI and mfdata.in family/month-history metadata. It does not submit AMC archive forms, call fund-family holdings endpoints, download portfolio workbooks, or store holdings values.",
        "- Rights: **UNVERIFIED**. Public API access is not treated as permission for commercial/trading-research extraction, caching, or redistribution.",
        "",
        "| Endpoint | Result | HTTP | Content type | Bytes | Top-level records |",
        "|---|---|---:|---|---:|---:|",
        endpoint_row("API index", report.get("api_index")),
        endpoint_row("/amcs", report.get("amcs")),
        endpoint_row("Nippon AMC detail", report.get("amc_detail")),
        endpoint_row("/scheme/{slug}", report.get("scheme_detail")),
        endpoint_row("/manifest", report.get("manifest")),
        endpoint_row("Tipsheet /data/v1/manifest.json", report.get("tipsheet_manifest")),
        *[endpoint_row("/month/" + str(x.get("month_id", "{id}")), x) for x in report.get("month_details", [])],
        "",
        "## Nippon AMC metadata matches",
        "",
    ]
    if report.get("api_index_schema"):
        lines.append("- API index schema: " + json.dumps(report["api_index_schema"], sort_keys=True))
    if report.get("nippon_amc_matches"):
        for item in report["nippon_amc_matches"][:10]:
            lines.append("- " + json.dumps(item, sort_keys=True, ensure_ascii=False))
    else:
        lines.append("- No Nippon AMC metadata match was returned.")
    lines += ["", "## AMC catalogue records", ""]
    if report.get("amc_catalog_records"):
        for item in report["amc_catalog_records"][:30]:
            lines.append("- " + json.dumps(item, sort_keys=True, ensure_ascii=False))
    else:
        lines.append("- No AMC catalogue records found.")
    lines += ["", "## Nifty 50 index schemes across fund houses", ""]
    if report.get("amc_scheme_shapes"):
        for item in report["amc_scheme_shapes"][:40]:
            lines.append("- " + json.dumps(item, sort_keys=True, ensure_ascii=False))
    else:
        lines.append("- No cross-AMC NIFTY 50 scheme history was discovered.")
    lines += ["", "## Mother AMC archive interface discovery (metadata only)", ""]
    if report.get("amc_archive_ui_pages"):
        for item in report["amc_archive_ui_pages"]:
            lines.append("- " + json.dumps(item, sort_keys=True, ensure_ascii=False))
    else:
        lines.append("- No mother-AMC archive page metadata was retrieved.")
    lines += ["", "## Mother AMC archive UI script patterns", ""]
    if report.get("amc_archive_ui_scripts"):
        for item in report["amc_archive_ui_scripts"]:
            lines.append("- " + json.dumps(item, sort_keys=True, ensure_ascii=False))
    else:
        lines.append("- No first-party archive UI scripts were found to inspect.")
    lines += ["", "## Nifty BeES scheme metadata matches", ""]
    if report.get("nifty_bees_scheme_matches"):
        for item in report["nifty_bees_scheme_matches"][:20]:
            lines.append("- " + json.dumps(item, sort_keys=True, ensure_ascii=False))
    else:
        lines.append("- No scheme metadata match was returned from the AMC detail endpoint.")
    for endpoint_name, meta_key in [
        ("API index", "api_index"), ("/amcs", "amcs"),
        ("AMC detail", "amc_detail"), ("/scheme/{slug}", "scheme_detail"),
        ("/manifest", "manifest")
    ]:
        meta = report.get(meta_key) or {}
        if meta.get("top_level_keys"):
            lines.append(f"- {endpoint_name} top-level JSON keys: " + ", ".join(meta["top_level_keys"]))
    if report.get("scheme_detail_shape"):
        lines.append("- /scheme/{slug} JSON shape: " + json.dumps(report["scheme_detail_shape"], sort_keys=True))
    for meta in report.get("month_details", []):
        if meta.get("payload_shape"):
            lines.append("- /month/" + str(meta.get("month_id")) + " JSON shape: " + json.dumps(meta["payload_shape"], sort_keys=True))
    lines += ["", "## Scheme-history metadata (source URLs and dates only)", ""]
    if report.get("scheme_history_metadata"):
        for item in report["scheme_history_metadata"][:50]:
            lines.append("- " + json.dumps(item, sort_keys=True, ensure_ascii=False))
    else:
        lines.append("- No scheme-history metadata was returned by /scheme/{slug}.")
    lines += ["", "## Month-level source metadata", ""]
    if report.get("month_source_metadata"):
        for item in report["month_source_metadata"][:50]:
            lines.append("- " + json.dumps(item, sort_keys=True, ensure_ascii=False))
    else:
        lines.append("- No source metadata was returned by /month/{id}.")

    lines += ["", "## mfdata.in independent portfolio-history availability audit", ""]
    lines.append("- Scope: scheme/family labels and month availability metadata only; no per-stock holdings endpoint was requested.")
    lines.append(endpoint_row("mfdata.in /api/v1/schemes?search=nifty 50", report.get("mfdata_schemes")))
    if report.get("mfdata_scheme_families"):
        for item in report["mfdata_scheme_families"][:50]:
            lines.append("- Scheme family: " + json.dumps(item, sort_keys=True, ensure_ascii=False))
    else:
        lines.append("- No matching family records were returned by the documented mfdata scheme search.")
    if report.get("mfdata_family_histories"):
        for item in report["mfdata_family_histories"]:
            lines.append("- Holdings-history availability: " + json.dumps(item, sort_keys=True, ensure_ascii=False))
    else:
        lines.append("- No family_id values were available to query the documented holdings-history endpoint.")
    lines += ["", "## Tipsheet NIFTY 50 weight-data catalogue entries", ""]
    if report.get("tipsheet_weight_candidates"):
        for item in report["tipsheet_weight_candidates"][:50]:
            lines.append("- " + json.dumps(item, sort_keys=True, ensure_ascii=False))
    else:
        lines.append("- No NIFTY 50 weight dataset entry was found in the Tipsheet manifest.")
    lines.append("- Tipsheet says its files are free to fetch with attribution, but upstream sources retain their own terms; this report does not establish a blanket redistribution licence.")
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
