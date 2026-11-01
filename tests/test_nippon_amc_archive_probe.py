from __future__ import annotations

import pandas as pd

from scripts.constituent_weekly.probe_nippon_amc_archive import (
    discover_monthly_portfolio_links,
    find_target_section,
    month_key,
)

BASE = "https://mf.nipponindiaim.com/investor-service/downloads/factsheet-portfolio-and-other-disclosures"


def test_month_key_parses_month_year_variants():
    assert month_key("Monthly portfolio for the month of Sept 2026") == "2026-09"
    assert month_key("Monthly portfolio as on 28th February 2026") == "2026-02"
    assert month_key("monthly portfolio for 30th April 2019") == "2019-04"


def test_discovery_selects_monthly_portfolio_file_not_factsheet():
    html = """
    <div>
      <span>Monthly portfolio for the month of Sept 2026</span>
      <a href="/files/portfolio-sep-2026.xls">Download</a>
      <a href="/files/factsheet-sep-2026.xls">Download</a>
    </div>
    <div>
      <span>Fundamentals E-Factsheet: February 2026</span>
      <a href="/files/factsheet-feb-2026.xls">Download</a>
    </div>
    <div>
      <span>Monthly portfolio as on 28th February 2026</span>
      <a href="/files/portfolio-feb-2026.xls">Download</a>
    </div>
    """
    found = discover_monthly_portfolio_links(html, BASE)
    assert found["2026-09"].endswith("/files/portfolio-sep-2026.xls")
    assert found["2026-02"].endswith("/files/portfolio-feb-2026.xls")
    assert "2019-04" not in found


def test_find_target_section_detects_scheme_headers_and_isin_rows_without_exposing_data():
    frame = pd.DataFrame(
        [
            ["Monthly portfolio", None, None, None, None],
            ["Nippon India ETF Nifty 50 BeES", None, None, None, None],
            ["Name", "ISIN", "Quantity", "Market Value", "% to Net Assets"],
            ["Example security", "INE000A01000", 100, 1000, 1.2],
            ["Another security", "INE000B01000", 200, 2000, 2.4],
            ["Grand Total", None, None, None, None],
        ]
    )
    result = find_target_section(frame)
    assert result["scheme_found"] is True
    assert result["header_found"] is True
    assert set(result["columns_detected"]) == {"ISIN", "quantity", "market_value", "weight_pct"}
    assert result["isin_rows"] == 2
    assert "Example security" not in str(result)
    assert "INE000A01000" not in str(result)


def test_find_target_section_fails_closed_when_scheme_or_header_missing():
    frame = pd.DataFrame([["Some unrelated scheme"], ["Name", "ISIN", "Units"]])
    result = find_target_section(frame)
    assert result["scheme_found"] is False
    assert result["header_found"] is False
