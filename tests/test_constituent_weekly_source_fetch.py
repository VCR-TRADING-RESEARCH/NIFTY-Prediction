from __future__ import annotations

import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "constituent_weekly"))

import fetch_official_weight_report as audit


class OfflineArchiveAuditTests(unittest.TestCase):
    def test_parses_preamble_and_weight_table(self):
        raw = (
            "Report title,,,,\n"
            ",,,\n"
            "Sr. No,Security Symbol,Security Name,Weightage (%)\n"
            "1,AAA,Company A,60.0\n"
            "2,BBB,Company B,40.0\n"
            "* Last trading day was month end,,,,\n"
        ).encode("utf-8")
        result = audit.parse_weight_csv(raw)
        self.assertEqual(result["status"], "STRUCTURE_PARSED")
        self.assertEqual(result["header_row_index_zero_based"], 2)
        self.assertEqual(result["constituent_rows"], 2)
        self.assertEqual(result["unique_symbols"], 2)
        self.assertEqual(result["weight_sum_percent"], 100.0)
        self.assertTrue(result["weights_sum_to_100_within_0_01"])
        self.assertTrue(result["symbol_values_omitted"])
        self.assertTrue(result["individual_weight_values_omitted"])

    def test_detects_duplicate_symbol_and_bad_weight_total(self):
        raw = (
            "Sr. No,Security Symbol,Weightage (%)\n"
            "1,AAA,30\n"
            "2,AAA,20\n"
            "3,BBB,40\n"
        ).encode("utf-8")
        result = audit.parse_weight_csv(raw)
        self.assertEqual(result["constituent_rows"], 3)
        self.assertEqual(result["unique_symbols"], 2)
        self.assertEqual(result["duplicate_symbol_rows"], 1)
        self.assertFalse(result["weights_sum_to_100_within_0_01"])

    def test_inspects_zip_and_csv_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.zip"
            memory = io.BytesIO()
            with zipfile.ZipFile(memory, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr(
                    "nifty50_mcwb.csv",
                    "title,,,,\n,,,\nSr. No,Security Symbol,Weightage (%)\n1,AAA,100\n",
                )
            path.write_bytes(memory.getvalue())
            result = audit.inspect_zip(path)
        self.assertEqual(result["status"], "ZIP_INTEGRITY_PASS")
        self.assertEqual(result["file_count"], 1)
        self.assertEqual(result["members"][0]["weight_table_audit"]["constituent_rows"], 1)

    def test_empty_authorised_input_directory_is_handled(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_dir = root / "empty"
            input_dir.mkdir()
            manifest = root / "manifest.json"
            report = root / "report.md"
            old_argv = sys.argv
            try:
                sys.argv = [
                    "fetch_official_weight_report.py",
                    "--input-dir", str(input_dir),
                    "--manifest", str(manifest),
                    "--report", str(report),
                ]
                self.assertEqual(audit.main(), 0)
            finally:
                sys.argv = old_argv
            import json
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "NO_AUTHORISED_ARCHIVE")
            self.assertFalse(payload["network_access_performed"])
            self.assertIn("C1 remains blocked", report.read_text(encoding="utf-8"))

    def test_sha256_is_deterministic(self):
        self.assertEqual(
            audit.sha256_bytes(b"test"),
            "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
        )


if __name__ == "__main__":
    unittest.main()
