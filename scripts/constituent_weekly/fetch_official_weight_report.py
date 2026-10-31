from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_weight_csv(raw: bytes) -> dict:
    text = None
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        return {"status": "UNDECODABLE"}

    rows = list(csv.reader(io.StringIO(text)))
    header_index = next(
        (
            i for i, row in enumerate(rows)
            if "Security Symbol" in row and "Weightage (%)" in row
        ),
        None,
    )
    if header_index is None:
        return {
            "status": "SCHEMA_NOT_RECOGNISED",
            "preview_rows": rows[:5],
        }

    header = rows[header_index]
    symbol_col = header.index("Security Symbol")
    weight_col = header.index("Weightage (%)")
    serial_col = header.index("Sr. No") if "Sr. No" in header else None

    symbols: list[str] = []
    weights: list[float] = []
    malformed_rows = 0
    for row in rows[header_index + 1:]:
        if serial_col is not None:
            if serial_col >= len(row) or not row[serial_col].strip().isdigit():
                if symbols:
                    break
                continue
        if max(symbol_col, weight_col) >= len(row):
            malformed_rows += 1
            continue
        symbol = row[symbol_col].strip()
        raw_weight = row[weight_col].strip().replace(",", "")
        if not symbol or not raw_weight:
            malformed_rows += 1
            continue
        try:
            weight = float(raw_weight)
        except ValueError:
            malformed_rows += 1
            continue
        symbols.append(symbol)
        weights.append(weight)

    return {
        "status": "STRUCTURE_PARSED",
        "header_row_index_zero_based": header_index,
        "column_names": header,
        "constituent_rows": len(symbols),
        "unique_symbols": len(set(symbols)),
        "duplicate_symbol_rows": len(symbols) - len(set(symbols)),
        "malformed_rows_before_table_end": malformed_rows,
        "weight_sum_percent": round(sum(weights), 6),
        "weights_sum_to_100_within_0_01": abs(sum(weights) - 100.0) <= 0.01,
        "symbol_values_omitted": True,
        "individual_weight_values_omitted": True,
    }


def inspect_zip(path: Path) -> dict:
    blob = path.read_bytes()
    result = {
        "filename": path.name,
        "bytes": len(blob),
        "sha256": sha256_bytes(blob),
    }
    try:
        with zipfile.ZipFile(io.BytesIO(blob)) as archive:
            bad_member = archive.testzip()
            members = []
            for item in archive.infolist():
                if item.is_dir():
                    continue
                entry = {
                    "name": item.filename,
                    "bytes": item.file_size,
                    "extension": Path(item.filename).suffix.lower(),
                }
                if entry["extension"] == ".csv" and item.file_size <= 25_000_000:
                    entry["weight_table_audit"] = parse_weight_csv(archive.read(item.filename))
                members.append(entry)
            result.update({
                "status": "ZIP_INTEGRITY_PASS" if bad_member is None else "ZIP_INTEGRITY_FAIL",
                "zip_test_error": bad_member,
                "file_count": len(members),
                "members": members,
            })
    except (zipfile.BadZipFile, OSError) as exc:
        result.update({
            "status": "ZIP_READ_ERROR",
            "error_type": type(exc).__name__,
        })
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Offline inventory of user-authorised, pre-provisioned source archives; performs no network collection."
    )
    parser.add_argument("--input-dir", default="data/authorized/constituent_weekly")
    parser.add_argument("--manifest", default="research/constituent_weekly/C1_OFFICIAL_WEIGHT_MANIFEST.json")
    parser.add_argument("--report", default="research/constituent_weekly/C1_SOURCE_FETCH_REPORT.md")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    manifest_path = Path(args.manifest)
    report_path = Path(args.report)
    input_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    archives = sorted(input_dir.glob("*.zip"))
    manifest = {
        "audit_type": "OFFLINE_ARCHIVE_INVENTORY",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_directory": str(input_dir),
        "network_access_performed": False,
        "status": "NO_AUTHORISED_ARCHIVE" if not archives else "ARCHIVES_INSPECTED",
        "archives": [inspect_zip(path) for path in archives],
        "important_note": (
            "This script does not fetch, scrape or redistribute market data. "
            "Only archives separately supplied with documented usage rights should be placed in the input directory."
        ),
    }

    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# C1 Offline Source Archive Audit",
        "",
        f"Audit time (UTC): {manifest['retrieved_at_utc']}",
        f"Status: **{manifest['status']}**",
        "- Network collection: **not performed**",
        "- Raw archive contents and individual constituent values are not written to this report.",
        "",
    ]
    if not archives:
        lines.append(
            "No separately authorised source archives were present. C1 remains blocked; do not download from a website or redistribute data unless the source terms and permission have been cleared."
        )
    for archive in manifest["archives"]:
        lines.extend([
            f"## {archive['filename']}",
            f"- Status: {archive['status']}",
            f"- Bytes: {archive['bytes']}",
            f"- SHA-256: {archive['sha256']}",
            f"- ZIP members: {archive.get('file_count')}",
        ])
        for member in archive.get("members", []):
            audit = member.get("weight_table_audit")
            if audit:
                lines.extend([
                    f"- CSV member {member['name']}: {audit.get('status')}",
                    f"  - Header row: {audit.get('header_row_index_zero_based')}",
                    f"  - Constituent rows: {audit.get('constituent_rows')}",
                    f"  - Unique symbols: {audit.get('unique_symbols')}",
                    f"  - Duplicate symbol rows: {audit.get('duplicate_symbol_rows')}",
                    f"  - Weight total is 100% within 0.01: {audit.get('weights_sum_to_100_within_0_01')}",
                    "  - Individual symbols/weights omitted from report.",
                ])
            else:
                lines.append(f"- Member {member['name']}: {member['extension']}, {member['bytes']} bytes")
        lines.append("")
    lines.extend([
        "## Gate",
        "",
        "An archive integrity/schema pass is not permission to use the data and is not proof of point-in-time publication, membership, historical weight coverage, basket reconciliation or model validity. C1 remains blocked until source rights, point-in-time data and price/weight reconciliation pass.",
        "",
    ])
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Offline source audit status: {manifest['status']}")
    print(f"Manifest: {manifest_path}")
    print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
