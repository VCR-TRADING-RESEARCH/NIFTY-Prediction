#!/usr/bin/env python3
"""Unit tests for official source reconciliation parsers."""
from __future__ import annotations

import io
import json
import zipfile
from datetime import date

import pandas as pd
import pytest

from scripts.reconcile_official_sources import _parse_date_values, bhavcopy_urls, candidate_verification_sessions, parse_bhavcopy_contract_expiries, parse_niftyindices_response, weekly_nominals


def test_parse_niftyindices_response_uses_official_close():
    payload = {"d": json.dumps([
        {"INDEX_NAME": "NIFTY 50", "HistoricalDate": "24 Oct 2025", "OPEN": "26000.0", "CLOSE": "26100.5"},
        {"INDEX_NAME": "NIFTY 50", "HistoricalDate": "23 Oct 2025", "OPEN": "25900.0", "CLOSE": "26000.0"},
    ])}
    frame = parse_niftyindices_response(payload)
    assert frame["session_date"].tolist() == [date(2025, 10, 23), date(2025, 10, 24)]
    assert frame["official_close"].tolist() == [26000.0, 26100.5]
    assert frame["official_open"].tolist() == [25900.0, 26000.0]


def test_parse_niftyindices_empty_data_is_not_silently_accepted():
    with pytest.raises(ValueError):
        parse_niftyindices_response({"d": "[]" })


def _zip_csv(text: str) -> bytes:
    buff = io.BytesIO()
    with zipfile.ZipFile(buff, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("sample.csv", text)
    return buff.getvalue()


def test_parse_legacy_bhavcopy_finds_nifty_option_expiry():
    csv = (
        "INSTRUMENT,SYMBOL,EXPIRY_DT,OPTION_TYP,STRIKE_PR\n"
        "OPTIDX,NIFTY,30-Oct-2025,CE,25000\n"
        "OPTIDX,NIFTY,30-Oct-2025,PE,25000\n"
        "FUTIDX,NIFTY,27-Nov-2025,,25000\n"
        "OPTIDX,BANKNIFTY,30-Oct-2025,CE,55000\n"
    )
    assert parse_bhavcopy_contract_expiries(_zip_csv(csv), date(2025, 10, 30)) == {date(2025, 10, 30)}


def test_parse_udiff_bhavcopy_finds_nifty_option_expiry():
    csv = (
        "FinInstrmTp,TckrSymb,XpryDt,OptnTp,StrkPric\n"
        "OPTIDX,NIFTY,2025-10-28,CE,25000\n"
        "OPTIDX,NIFTY,2025-10-28,PE,25000\n"
        "FUTIDX,NIFTY,2025-11-25,,25000\n"
    )
    assert parse_bhavcopy_contract_expiries(csv.encode(), date(2025, 10, 28)) == {date(2025, 10, 28)}


def test_weekly_nominal_schedule_changes_to_tuesday_in_sep_2025():
    dates = weekly_nominals(date(2025, 8, 25), date(2025, 9, 10))
    assert date(2025, 8, 28) in dates
    assert date(2025, 9, 2) in dates
    assert all(d.weekday() == 3 for d in dates if d < date(2025, 9, 1))
    assert all(d.weekday() == 1 for d in dates if d >= date(2025, 9, 1))



def test_parse_udiff_index_derivative_option_code_ido():
    csv = (
        "FinInstrmTp,TckrSymb,XpryDt,OptnTp,StrkPric\n"
        "IDO,NIFTY,2025-10-28,CE,25000\n"
        "IDO,NIFTY,2025-10-28,PE,25000\n"
        "IDF,NIFTY,2025-11-25,,25000\n"
    )
    assert parse_bhavcopy_contract_expiries(csv.encode(), date(2025, 10, 28)) == {date(2025, 10, 28)}


def test_bhavcopy_url_order_matches_nse_format_transition():
    legacy = bhavcopy_urls(date(2024, 7, 5))
    udiff = bhavcopy_urls(date(2024, 7, 8))
    assert "/content/historical/DERIVATIVES/" in legacy[0]
    assert "nsearchives.nseindia.com/content/fo/" in udiff[0]
    assert "/content/historical/DERIVATIVES/" in udiff[-1]


def test_parse_udiff_prefers_actual_expiry_and_validates_trade_date():
    csv = (
        "BizDt,FinInstrmTp,TckrSymb,XpryDt,FinInstrmActlXpryDt,OptnTp,StrkPric\n"
        "2025-10-21,IDO,NIFTY,2025-10-23,2025-10-21,CE,25000\n"
        "2025-10-21,IDO,NIFTY,2025-10-23,2025-10-21,PE,25000\n"
    )
    assert parse_bhavcopy_contract_expiries(csv.encode(), date(2025, 10, 21)) == {date(2025, 10, 21)}


def test_parse_bhavcopy_rejects_wrong_trade_date():
    csv = (
        "TIMESTAMP,INSTRUMENT,SYMBOL,EXPIRY_DT,OPTION_TYP\n"
        "03-JAN-2024,OPTIDX,NIFTY,04-Jan-2024,CE\n"
        "03-JAN-2024,OPTIDX,NIFTY,04-Jan-2024,PE\n"
    )
    with pytest.raises(ValueError, match="trade-date mismatch"):
        parse_bhavcopy_contract_expiries(_zip_csv(csv), date(2024, 1, 4))



def test_candidate_verification_checks_nearby_previous_sessions_for_holiday_shift():
    sessions = [date(2021, 11, 1), date(2021, 11, 2), date(2021, 11, 3), date(2021, 11, 4)]
    assert candidate_verification_sessions(date(2021, 11, 4), sessions) == [date(2021, 11, 4), date(2021, 11, 3), date(2021, 11, 2), date(2021, 11, 1)]


def test_alternative_minute_aggregate_uses_chronological_last_bar_and_session_filter():
    from scripts.compare_alternative_minute_source import aggregate_minute_frame

    frame = pd.DataFrame({
        "Timestamp": ["2025-01-02T15:29:00", "2025-01-02T09:15:00", "2025-01-02T18:00:00", "2025-01-02T15:28:00"],
        "Open": [100.0, 99.0, 999.0, 100.0],
        "High": [101.0, 100.0, 999.0, 102.0],
        "Low": [99.5, 98.0, 999.0, 99.0],
        "Close": [100.5, 99.5, 999.0, 101.0],
    })
    daily = aggregate_minute_frame(frame)
    assert len(daily) == 1
    row = daily.iloc[0]
    assert row["alternative_open"] == 99.0
    assert row["alternative_high"] == 102.0
    assert row["alternative_low"] == 98.0
    assert row["alternative_close"] == 100.5
    assert row["alternative_bars"] == 3


def test_official_bhavcopy_trade_date_prefers_traddt_over_bizdt():
    csv = (
        "TradDt,BizDt,FinInstrmTp,TckrSymb,XpryDt,OptnTp,StrkPric\n"
        "2025-10-21,2025-10-22,IDO,NIFTY,2025-10-23,CE,25000\n"
        "2025-10-21,2025-10-22,IDO,NIFTY,2025-10-23,PE,25000\n"
    )
    assert parse_bhavcopy_contract_expiries(csv.encode(), date(2025, 10, 21)) == {date(2025, 10, 23)}


def test_parse_date_values_preserves_iso_calendar_date_and_legacy_formats():
    values = pd.Series(["2024-12-04", "2025-01-02", "20240711", "11-Jul-2024", "04-12-2024"])
    parsed = _parse_date_values(values)
    assert parsed.dt.date.tolist() == [
        date(2024, 12, 4),
        date(2025, 1, 2),
        date(2024, 7, 11),
        date(2024, 7, 11),
        date(2024, 12, 4),
    ]


def test_sandeep_minute_aggregate_parses_day_first_date_and_filters_session():
    from scripts.compare_sandeep_minute_source import aggregate_sandeep_frame

    frame = pd.DataFrame({
        "Date": ["02-01-25", "02-01-25", "02-01-25", "02-01-25"],
        "Time": ["15:29:00", "09:15:00", "18:00:00", "15:28:00"],
        "Open": [100.0, 99.0, 999.0, 100.0],
        "High": [101.0, 100.0, 999.0, 102.0],
        "Low": [99.5, 98.0, 999.0, 99.0],
        "Close": [100.5, 99.5, 999.0, 101.0],
    })
    daily, quality = aggregate_sandeep_frame(frame)
    assert len(daily) == 1
    row = daily.iloc[0]
    assert row["session_date"] == date(2025, 1, 2)
    assert row["alternative_open"] == 99.0
    assert row["alternative_high"] == 102.0
    assert row["alternative_low"] == 98.0
    assert row["alternative_close"] == 100.5
    assert row["alternative_bars"] == 3
    assert quality["daily_sessions"] == 1
