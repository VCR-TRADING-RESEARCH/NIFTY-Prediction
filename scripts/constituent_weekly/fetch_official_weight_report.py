from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import zipfile
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

REPORT_PAGE = "https://niftyindices.com/reports/monthly-reports"
FAMILIES = {
    "nifty50_weights_beta": (
        "market_capitalisation_weightage_beta_for_nifty_50_and_nifty_next_50",
        "mcwb_",
    ),
    "indices_market_cap_weightage": (
        "indices_-_market_capitalisation_and_weightage",
        "indices_data",
    ),
}
MONTH_RE = re.compile(r"mcwb_([a-z]{3})(\d{2})\.zip$", re.IGNORECASE)


class AnchorCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href is not None:
            self.links.append((self._href, " ".join(self._text).strip()))
            self._href = None
            self._text = []


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def discover_report_links(html: str, page_url: str = REPORT_PAGE) -> dict[str, str | None]:
    parser = AnchorCollector()
    parser.feed(html)
    found: dict[str, str | None] = {name: None for name in FAMILIES}
    for href, label in parser.links:
        href_l = href.lower()
        label_l = label.lower()
        for family, needles in FAMILIES.items():
            if any(needle in href_l for needle in needles) or (
                family == "nifty50_weights_beta"
                and "market capitalisation, weightage" in label_l
            ) or (
                family == "indices_market_cap_weightage"
                and "indices market capitalisation" in label_l
            ):
                found[family] = urljoin(page_url, href)
    return found


def inspect_zip(blob: bytes) -> dict:
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        bad_member = archive.testzip()
        files = []
        for item in archive.infolist():
            if item.is_dir():
                continue
            entry = {
                "name": item.filename,
                "bytes": item.file_size,
                "extension": Path(item.filename).suffix.lower(),
            }
            if entry["extension"] == ".csv" and item.file_size <= 25_000_000:
                raw = archive.read(item.filename)
                text = None
                for encoding in ("utf-8-sig", "cp1252", "latin-1"):
                    try:
                        text = raw.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                if text is not None:
                    reader = csv.reader(io.StringIO(text))
                    try:
                        rows = list(reader)
                        entry["header"] = rows[0] if rows else []
                        entry["data_rows"] = max(0, len(rows) - 1)
                        entry["preview_rows"] = rows[:12]
                    except csv.Error as exc:
                        entry["csv_parse_error"] = type(exc).__name__
            files.append(entry)
        return {
            "zip_test_error": bad_member,
            "file_count": len(files),
            "files": files,
        }


def fetch_bytes(url: str, timeout: int) -> bytes:
    request = Request(
        url,
        headers={
            "User-Agent": "NIFTY-Prediction-BUP-01-Research/1.0",
            "Accept": "application/zip,application/octet-stream,*/*",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        data = response.read()
        if response.status < 200 or response.status >= 300:
            raise RuntimeError(f"HTTP status {response.status}")
        if not data.startswith(b"PK\x03\x04"):
            raise RuntimeError("Response is not a ZIP payload")
        return data


def fetch_page(url: str, timeout: int) -> str:
    request = Request(url, headers={"User-Agent": "NIFTY-Prediction-BUP-01-Research/1.0"})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def month_from_filename(url: str) -> str | None:
    match = MONTH_RE.search(url.split("/")[-1].split("?")[0])
    if not match:
        return None
    month = match.group(1).lower()
    year = int(match.group(2))
    return f"20{year:02d}-{month}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch and inventory official NSE Indices weight report links.")
    parser.add_argument("--out-dir", default="data/cache/constituent_weekly/official")
    parser.add_argument("--manifest", default="research/constituent_weekly/C1_OFFICIAL_WEIGHT_MANIFEST.json")
    parser.add_argument("--report", default="research/constituent_weekly/C1_SOURCE_FETCH_REPORT.md")
    parser.add_argument("--timeout", type=int, default=45)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = Path(args.manifest)
    report_path = Path(args.report)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    manifest = {
        "source_page": REPORT_PAGE,
        "retrieved_at_utc": utc_now(),
        "status": "BLOCKED_DOWNLOAD",
        "families": {},
        "important_note": "Archive inventory is not proof of point-in-time historic weights or index reconciliation.",
    }

    try:
        page = fetch_page(REPORT_PAGE, args.timeout)
        links = discover_report_links(page, REPORT_PAGE)
        for family, url in links.items():
            family_result = {"url": url, "status": "LINK_NOT_FOUND"}
            if url:
                try:
                    blob = fetch_bytes(url, args.timeout)
                    filename = url.split("/")[-1].split("?")[0]
                    target = out_dir / filename
                    target.write_bytes(blob)
                    inventory = inspect_zip(blob)
                    family_result.update({
                        "status": "DOWNLOADED_AND_INVENTORIED",
                        "filename": filename,
                        "snapshot_month_hint": month_from_filename(url),
                        "bytes": len(blob),
                        "sha256": sha256_bytes(blob),
                        "inventory": inventory,
                    })
                except (HTTPError, URLError, TimeoutError, RuntimeError, zipfile.BadZipFile, OSError) as exc:
                    family_result.update({
                        "status": "DOWNLOAD_OR_PARSE_ERROR",
                        "error_type": type(exc).__name__,
                        "error": str(exc)[:300],
                    })
            manifest["families"][family] = family_result
        if any(v.get("status") == "DOWNLOADED_AND_INVENTORIED" for v in manifest["families"].values()):
            manifest["status"] = "SAMPLE_ARCHIVE_DOWNLOADED"
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        manifest["status"] = "BLOCKED_SOURCE_PAGE"
        manifest["page_error_type"] = type(exc).__name__
        manifest["page_error"] = str(exc)[:300]

    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# C1 Official Weight Report Retrieval",
        "",
        f"Retrieval time (UTC): {manifest['retrieved_at_utc']}",
        f"Overall status: **{manifest['status']}**",
        "",
        "This is a source discovery and archive inventory step. It does not certify historical effective weights, report publication time, membership, daily interpolation or basket-to-index reconciliation.",
        "",
    ]
    for family, result in manifest["families"].items():
        lines.extend([
            f"## {family}",
            f"- Status: {result.get('status')}",
            f"- URL: {result.get('url')}",
            f"- File: {result.get('filename')}",
            f"- Snapshot month hint: {result.get('snapshot_month_hint')}",
            f"- Bytes: {result.get('bytes')}",
            f"- SHA-256: {result.get('sha256')}",
            f"- Error: {result.get('error')}",
        ])
        inventory = result.get("inventory", {})
        for file_info in inventory.get("files", []):
            lines.append(f"- Member {file_info.get('name')}: {file_info.get('bytes')} bytes; rows={file_info.get('data_rows')}; columns={file_info.get('header')}")
        lines.append("")
    if not manifest["families"]:
        lines.append("The official report page could not be read; inspect the JSON manifest for sanitized diagnostics.")
    lines.extend([
        "## Gate",
        "",
        "C1 remains BLOCKED until historical monthly reports are collected, schemas and publication timestamps are confirmed, numeric weights are validated, and point-in-time membership/price reconstruction passes the registered checks.",
        "",
    ])
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Official weight report audit status: {manifest['status']}")
    print(f"Manifest: {manifest_path}")
    print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
