from __future__ import annotations

from scripts.constituent_weekly.probe_amcs_fund_metadata import (
    _first_identifier,
    _matching_records,
    _metadata_records,
    _month_identifiers,
    _record_summary,
    _scheme_slug,
    _source_links,
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
