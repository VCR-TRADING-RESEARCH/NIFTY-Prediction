#!/usr/bin/env python3
"""Unit tests for official source reconciliation parsers."""
from __future__ import annotations

import io
import json
import zipfile
from datetime import date

import pandas as pd
import pytest

from scripts.reconcile_official_sources import parse_bhavcopy_contract_expiries, parse_niftyindices_response, weekly_nominals


def test_parse_niftyindices_response_uses_official_close():
    payload = {"d": json.dumps([
        {"INDEX_NAME": "NIFTY 50", "HistoricalDate": "24 Oct 2025", "OPEN": "26000.0", "CLOSE": "26100.5"},
        {"INDEX_NAME": "NIFTY 50", "HistoricalDate": "23 Oct 2025", "OPEN": "25900.0", "CLOSE": "26000.0"},
    ])}
    frame = parse_niftyindices_response(payload)
    assert frame["session_date"].tolist() == [date(2025, 10, 23), date(2025, 10, 24)]
    assert frame["official_close"].tolist() == [26000.0, 26100.5]


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
