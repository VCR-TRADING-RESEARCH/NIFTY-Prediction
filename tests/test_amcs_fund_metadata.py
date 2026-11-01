from __future__ import annotations

from scripts.constituent_weekly.probe_amcs_fund_metadata import (
    _extract_html_metadata,
    _mfdata_family_summaries,
    _mfdata_months,
    _mfdata_month_coverage,
    _first_identifier,
    _matching_records,
    _metadata_records,
    _month_identifiers,
    _record_summary,
    _scheme_slug,
    _source_links,
    _tipsheet_weight_candidates,
)


def test_matching_records_extracts_only_nippon_bees_metadata():
    amc_payload = {
        "data": [
            {"id": 12, "name": "Nippon India Mutual Fund", "slug": "nippon-india"},
            {"id": 13, "name": "Other AMC", "slug": "other"},
        ]
    }
    scheme_payload = {
        "data": [
            {
                "scheme_id": 501,
                "scheme_name": "Nippon India ETF Nifty 50 BeES",
                "published_at": "2019-05-08",
                "secret_holdings_field": "must-not-be-retained",
            },
            {"scheme_id": 502, "scheme_name": "Nippon India Other ETF"},
        ]
    }
    amcs = _matching_records(amc_payload, ("nippon",))
    schemes = _matching_records(scheme_payload, ("nifty", "bees"))
    assert amcs == [{"id": 12, "name": "Nippon India Mutual Fund", "slug": "nippon-india"}]
    assert schemes == [{
        "scheme_id": 501,
        "scheme_name": "Nippon India ETF Nifty 50 BeES",
        "published_at": "2019-05-08",
    }]
    assert "secret_holdings_field" not in str(schemes)


def test_first_identifier_accepts_only_safe_identifier_characters():
    assert _first_identifier([{"name": "Nippon", "id": "nippon-india"}]) == "nippon-india"
    assert _first_identifier([{"id": "../unsafe"}]) is None


def test_record_summary_whitelists_official_and_archive_urls_only():
    record = {
        "name": "Nippon India",
        "source_url": "https://mf.nipponindiaim.com/archive/portfolio.xls",
        "archive_url": "https://web.archive.org/web/20190401id_/https://example.com/file.xls",
        "external_url": "https://unknown.example/file.xls",
        "weights": [1, 2, 3],
    }
    summary = _record_summary(record)
    assert summary["source_url"].endswith("/archive/portfolio.xls")
    assert summary["archive_url"].startswith("https://web.archive.org/")
    assert "external_url" not in summary
    assert "weights" not in summary


def test_source_links_only_whitelisted_hosts():
    records = [
        {"source_url": "https://mf.nipponindiaim.com/file.xls"},
        {"archive_url": "https://web.archive.org/record"},
        {"source_url": "https://evil.example/file.xls"},
    ]
    links = _source_links(records)
    assert len(links) == 2
    assert {item["field"] for item in links} == {"source_url", "archive_url"}


def test_scheme_history_drops_isin_holding_rows():
    payload = {
        'data': [
            {'id': '2026-09', 'month': '2026-09', 'disclosure_date': '2026-09-30'},
            {'isin': 'INE000000001', 'name': 'Example constituent', 'quantity': 123, 'weight': 8.7},
        ]
    }
    records = _metadata_records(payload)
    assert records == [{'id': '2026-09', 'month': '2026-09', 'disclosure_date': '2026-09-30'}]
    assert 'isin' not in str(records)
    assert 'quantity' not in str(records)


def test_scheme_slug_and_month_identifiers_are_selected_safely():
    assert _scheme_slug([
        {'name': 'Nippon India ETF Nifty Bank BeES', 'slug': 'bank-bees'},
        {'name': 'Nippon India ETF Nifty 50 BeES', 'slug': 'nifty-50-bees'},
    ]) == 'nifty-50-bees'
    assert _month_identifiers([
        {'id': '2026-09'}, {'id': '2026-08'}, {'id': '../bad'},
        {'id': '2026-07'}, {'id': '2026-06'}, {'id': '2026-05'},
    ]) == ['2026-09', '2026-08', '2026-07', '2026-06']



def test_tipsheet_manifest_finds_nifty50_weight_series_without_values():
    payload = {
        "datasets": [
            {
                "name": "indices/nifty-50/weightage",
                "title": "Nifty 50 historical constituent weights",
                "url": "/data/v1/indices/nifty50/weightage.abcd.json",
                "date_start": "2008-01-31",
                "date_end": "2026-09-30",
                "resolution": "monthly",
                "source": "monthly weightage files",
            },
            {"name": "indices/nifty-bank/weightage", "url": "/data/v1/bank.json"},
        ]
    }
    records = _tipsheet_weight_candidates(payload)
    assert len(records) == 1
    assert records[0]["date_start"] == "2008-01-31"
    assert records[0]["resolution"] == "monthly"
    assert records[0]["url"].startswith("https://tipsheet.markets/")


def test_tipsheet_manifest_rejects_off_host_urls():
    payload = {
        "datasets": [
            {
                "name": "Nifty 50 weight history",
                "url": "https://evil.example/weights.json",
            }
        ]
    }
    records = _tipsheet_weight_candidates(payload)
    assert len(records) == 1
    assert "url" not in records[0]



def test_amcs_html_extractor_keeps_only_same_site_scripts_and_whitelisted_sources():
    html = '''
    <html>
      <script src="/assets/app.js"></script>
      <script src="https://evil.example/track.js"></script>
      <a href="https://mf.nipponindiaim.com/portfolios/abc.xlsx">Original portfolio</a>
      <a href="https://web.archive.org/web/abcid_/https://hdfcfund.com/file.xlsx">Archive copy</a>
      <a href="https://evil.example/file.xlsx">Unknown file</a>
    </html>
    '''
    meta = _extract_html_metadata(html, "https://amcs.fund/month")
    assert meta["script_srcs"] == ["https://amcs.fund/assets/app.js"]
    assert len(meta["source_links"]) == 2
    assert {x["host"] for x in meta["source_links"]} == {
        "mf.nipponindiaim.com", "web.archive.org"
    }
    assert "html_bytes" in meta and "sha256" in meta



def test_mfdata_family_search_keeps_only_nifty50_scheme_metadata():
    payload = {
        "status": "success",
        "data": [
            {
                "family_id": 8721,
                "family_name": "UTI Nifty 50 Index Fund",
                "amc": "UTI Mutual Fund",
                "category": "Index Funds",
                "has_holdings": True,
                "variants": [{"scheme_code": 120716}],
            },
            {
                "family_id": 8722,
                "family_name": "UTI Nifty Next 50 Index Fund",
                "amc": "UTI Mutual Fund",
                "has_holdings": True,
            },
            {
                "family_id": 8723,
                "family_name": "UTI Nifty 50 Fund",
                "amc": "UTI Mutual Fund",
                "has_holdings": False,
            },
        ],
    }
    records = _mfdata_family_summaries(payload)
    assert len(records) == 2
    assert records[0]["family_id"] == 8721
    assert records[0]["has_holdings"] is True
    assert "variants" not in str(records)


def test_mfdata_month_parser_only_keeps_valid_year_month_labels():
    payload = {
        "status": "success",
        "data": ["2019-04", "2022-09", "2026-09", "2019-13", "not-a-month"],
    }
    assert _mfdata_months(payload) == ["2019-04", "2022-09", "2026-09"]



def test_mfdata_month_coverage_reports_internal_gaps():
    result = _mfdata_month_coverage(["2020-01", "2020-03", "2020-04"])
    assert result["month_count"] == 3
    assert result["first_month"] == "2020-01"
    assert result["last_month"] == "2020-04"
    assert result["expected_month_count"] == 4
    assert result["missing_month_count"] == 1
    assert result["missing_months_sample"] == ["2020-02"]
    assert result["continuous"] is False
    assert result["coverage_ratio"] == 0.75


def test_mfdata_month_coverage_handles_empty_history():
    result = _mfdata_month_coverage([])
    assert result["month_count"] == 0
    assert result["continuous"] is False
    assert result["coverage_ratio"] is None



def test_payload_shape_keeps_stable_whitelisted_top_level_mother_source_url():
    payload = {
        "source": "https://mf.nipponindiaim.com/InvestorServices/FactsheetsDocuments/portfolio.xls",
        "data": {"month": "2019-04"},
    }
    shape = _payload_shape(payload)
    assert shape["source_host"] == "mf.nipponindiaim.com"
    assert shape["source_url"].endswith("/portfolio.xls")


def test_payload_shape_drops_untrusted_or_signed_top_level_source_url():
    external = _payload_shape({
        "source": "https://evil.example/private.xls",
        "data": {"month": "2019-04"},
    })
    signed = _payload_shape({
        "source": "https://mf.nipponindiaim.com/portfolio.xls?token=secret",
        "data": {"month": "2019-04"},
    })
    assert "source_url" not in external
    assert "source_url" not in signed
