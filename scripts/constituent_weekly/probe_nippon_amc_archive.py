from __future__ import annotations

import argparse
import hashlib
import re
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

PAGE_URL = (
    "https://mf.nipponindiaim.com/investor-service/downloads/"
    "factsheet-portfolio-and-other-disclosures"
)
SCHEME = "nippon india etf nifty 50 bees"
MONTHS = {
    "jan": "01", "january": "01", "feb": "02", "february": "02",
    "mar": "03", "march": "03", "apr": "04", "april": "04",
    "may": "05", "jun": "06", "june": "06", "jul": "07",
    "july": "07", "aug": "08", "august": "08", "sep": "09",
    "sept": "09", "september": "09", "oct": "10", "october": "10",
    "nov": "11", "november": "11", "dec": "12", "december": "12",
}
TARGET_MONTHS = ("2026-09", "2026-02", "2019-04")
ISIN_RE = re.compile(r"\bINE[A-Z0-9]{9}\b", re.I)
MAX_FILE_BYTES = 35 * 1024 * 1024
TIMEOUT = (15, 60)


def month_key(text: str) -> str | None:
    value = re.sub(r"\s+", " ", text.lower())
    for name, number in MONTHS.items():
        match = re.search(rf"\b{name}\b\D{{0,20}}\b(20\d{{2}})\b", value)
        if match:
            return f"{match.group(1)}-{number}"
    return None


def discover_monthly_portfolio_links(html: str, base_url: str = PAGE_URL) -> dict[str, str]:
    """Return {YYYY-MM: URL} for AMC monthly-portfolio disclosure links."""
    soup = BeautifulSoup(html, "html.parser")
    discovered: dict[str, str] = {}
    for anchor in soup.find_all("a", href=True):
        href = str(anchor.get("href", "")).strip()
        if not href or not re.search(r"\.(?:xls|xlsx|zip)(?:$|\?)", href, re.I):
            continue
        if "factsheet" in href.lower():
            continue
        context = ""
        for ancestor in list(anchor.parents)[:8]:
            if getattr(ancestor, "name", None) in {"li", "tr", "div", "td"}:
                candidate = ancestor.get_text(" ", strip=True)
                if "monthly portfolio" in candidate.lower():
                    context = candidate
                    break
        if not context:
            context = anchor.get_text(" ", strip=True)
        key = month_key(context) or month_key(urlparse(href).path.replace("-", " "))
        if not key:
            continue
        absolute = urljoin(base_url, href)
        # Prefer a workbook over a zip only when a duplicate month is discovered.
        existing = discovered.get(key)
        if existing is None or absolute.lower().endswith((".xls", ".xlsx")):
            discovered[key] = absolute
    return discovered


def cell_text(value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value).strip()


def find_target_section(frame: pd.DataFrame) -> dict[str, object]:
    """Find scheme and generic column headers without returning holdings values."""
    rows = [
        " ".join(cell_text(v) for v in frame.iloc[i].tolist()).lower()
        for i in range(len(frame))
    ]
    scheme_rows = [
        i for i, row in enumerate(rows)
        if SCHEME in re.sub(r"\s+", " ", row)
    ]
    if not scheme_rows:
        return {"scheme_found": False, "header_found": False, "isin_rows": 0}

    header_candidates: list[tuple[int, int, list[str]]] = []
    for i, row in enumerate(rows):
        compact = re.sub(r"\s+", " ", row)
        fields = []
        if "isin" in compact:
            fields.append("ISIN")
        if "quantity" in compact or "no. of units" in compact or "units held" in compact:
            fields.append("quantity")
        if "market value" in compact or "marketvalue" in compact:
            fields.append("market_value")
        if "% to net assets" in compact or "% to nav" in compact or "% of nav" in compact:
            fields.append("weight_pct")
        if len(fields) >= 3:
            distance = min(abs(i - s) for s in scheme_rows)
            header_candidates.append((distance, i, fields))
    if not header_candidates:
        return {"scheme_found": True, "header_found": False, "isin_rows": 0}

    _, header_idx, fields = sorted(header_candidates)[0]
    scheme_idx = min(scheme_rows, key=lambda s: abs(s - header_idx))
    start = max(header_idx, scheme_idx) + 1
    end = min(len(rows), start + 100)
    isin_rows = 0
    for row in rows[start:end]:
        if re.search(r"\bnippon india (?!etf nifty 50 bees)", row) or re.search(r"\bgrand total\b|\bnet assets\b", row):
            break
        isin_rows += len(ISIN_RE.findall(row.upper()))
    return {
        "scheme_found": True,
        "header_found": True,
        "columns_detected": fields,
        "isin_rows": isin_rows,
    }


def workbook_probe(payload: bytes) -> dict[str, object]:
    if len(payload) > MAX_FILE_BYTES:
        raise ValueError("Workbook exceeds configured size ceiling")
    excel = pd.ExcelFile(BytesIO(payload), engine="xlrd")
    best: dict[str, object] = {"scheme_found": False, "header_found": False, "isin_rows": 0}
    found_sheet_count = 0
    for sheet in excel.sheet_names:
        frame = pd.read_excel(excel, sheet_name=sheet, header=None, dtype=object)
        result = find_target_section(frame)
        if result["scheme_found"]:
            found_sheet_count += 1
            if result["header_found"]:
                best = result
                break
            best = result
    best["sheet_count"] = len(excel.sheet_names)
    best["target_sheet_count"] = found_sheet_count
    return best


def probe_file(session: requests.Session, month: str, url: str) -> dict[str, object]:
    result: dict[str, object] = {"month": month, "url": url, "status": "NOT_STARTED"}
    try:
        response = session.get(url, timeout=TIMEOUT, stream=True)
        response.raise_for_status()
        chunks = []
        total = 0
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if not chunk:
                continue
            total += len(chunk)
            if total > MAX_FILE_BYTES:
                raise ValueError("Downloaded workbook exceeds configured size ceiling")
            chunks.append(chunk)
        payload = b"".join(chunks)
        if not payload:
            raise ValueError("Empty workbook response")
        meta = workbook_probe(payload)
        result.update(
            {
                "http_status": response.status_code,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                **meta,
            }
        )
        result["status"] = (
            "PASS_SCHEMA"
            if meta.get("scheme_found") and meta.get("header_found") and meta.get("isin_rows", 0) > 0
            else "SCHEMA_UNRECOGNISED"
        )
    except Exception as exc:
        result.update({"status": "ERROR", "error_type": type(exc).__name__, "error": str(exc)[:240]})
    return result


def render_report(results: list[dict[str, object]]) -> str:
    required = {"2026-09", "2026-02"}
    passed = {str(r["month"]) for r in results if r.get("status") == "PASS_SCHEMA"}
    overall = "PASS_SCHEMA_ONLY" if required.issubset(passed) else "PARTIAL_OR_BLOCKED"
    lines = [
        "# C1 AMC disclosure metadata probe",
        "",
        f"- Run time (UTC): {datetime.now(timezone.utc).isoformat()}",
        f"- Overall: **{overall}**",
        "- Scope: metadata/schema validation only; no raw holdings are published.",
        "",
        "| Month | Status | HTTP | Bytes | SHA-256 | Sheets | Scheme | Headers | ISIN rows |",
        "|---|---:|---:|---:|---|---:|---|---|---:|",
    ]
    for r in results:
        lines.append(
            "| {month} | {status} | {http} | {size} | {digest} | {sheets} | {scheme} | {headers} | {rows} |".format(
                month=r.get("month", ""),
                status=r.get("status", ""),
                http=r.get("http_status", ""),
                size=r.get("bytes", ""),
                digest=r.get("sha256", ""),
                sheets=r.get("sheet_count", ""),
                scheme=r.get("scheme_found", ""),
                headers=",".join(r.get("columns_detected", [])),
                rows=r.get("isin_rows", ""),
            )
        )
        if r.get("error"):
            lines.append(f"- {r.get('month')}: {r.get('error_type')}: {r.get('error')}")
    lines.extend(
        [
            "",
            "No constituent names, ISINs, quantities, market values, portfolio weights or raw workbook rows are stored in this report.",
            "A schema pass does not establish publication-time availability, source-use rights, historical security continuity, index-weight equivalence or permission to trade.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default="research/constituent_weekly/C1_AMC_ARCHIVE_PROBE_REPORT.md",
    )
    args = parser.parse_args()
    session = requests.Session()
    session.headers.update({"User-Agent": "BUP-01 research metadata probe/1.0"})
    response = session.get(PAGE_URL, timeout=TIMEOUT)
    response.raise_for_status()
    links = discover_monthly_portfolio_links(response.text)
    results = []
    for month in TARGET_MONTHS:
        url = links.get(month)
        if url:
            results.append(probe_file(session, month, url))
        else:
            results.append({"month": month, "status": "ARCHIVE_LINK_NOT_FOUND"})
    report = render_report(results)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")
    print(report)
    required = {"2026-09", "2026-02"}
    passed = {str(r["month"]) for r in results if r.get("status") == "PASS_SCHEMA"}
    return 0 if required.issubset(passed) else 2


if __name__ == "__main__":
    raise SystemExit(main())
