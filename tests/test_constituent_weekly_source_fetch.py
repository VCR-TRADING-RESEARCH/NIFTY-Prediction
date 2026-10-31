from __future__ import annotations

import io
import sys
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "constituent_weekly"))

import fetch_official_weight_report as audit


class OfficialWeightFetcherTests(unittest.TestCase):
    def test_discovers_official_weight_links(self):
        html = """
        <a href="/Market_Capitalisation_Weightage_Beta_for_NIFTY_50_And_NIFTY_Next_50/mcwb_jul26.zip">
          Market Capitalisation, Weightage, Beta (Zip)
        </a>
        <a href="/Indices_-_Market_Capitalisation_and_Weightage/indices_dataJul2026.zip">
          Indices Market Capitalisation &amp; Weightage (zip)
        </a>
        """
        links = audit.discover_report_links(html)
        self.assertTrue(links["nifty50_weights_beta"].endswith("mcwb_jul26.zip"))
        self.assertTrue(links["indices_market_cap_weightage"].endswith("indices_dataJul2026.zip"))

    def test_month_hint_parses_weight_archive_name(self):
        self.assertEqual(
            audit.month_from_filename("https://niftyindices.com/path/mcwb_jul26.zip?download=1"),
            "2026-jul",
        )

    def test_zip_inventory_reads_csv_header_and_row_count(self):
        memory = io.BytesIO()
        with zipfile.ZipFile(memory, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(
                "weights.csv",
                "Symbol,ISIN,Weightage\nABC,INE000A01000,25.5\nXYZ,INE000B01000,74.5\n",
            )
        result = audit.inspect_zip(memory.getvalue())
        self.assertIsNone(result["zip_test_error"])
        self.assertEqual(result["file_count"], 1)
        self.assertEqual(result["files"][0]["header"], ["Symbol", "ISIN", "Weightage"])
        self.assertEqual(result["files"][0]["data_rows"], 2)
        self.assertEqual(result["files"][0]["preview_rows"][0], ["Symbol", "ISIN", "Weightage"])
        self.assertEqual(len(result["files"][0]["preview_rows"]), 3)

    def test_sha256_is_deterministic(self):
        self.assertEqual(
            audit.sha256_bytes(b"test"),
            "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
        )


if __name__ == "__main__":
    unittest.main()
