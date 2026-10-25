from datetime import date
import pytest

from live_api.app import PublicPredictionError, parse_as_of_date, find_nifty50_security


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2024-05-10", date(2024, 5, 10)),
        ("10/05/2024", date(2024, 5, 10)),
        ("10-05-2024", date(2024, 5, 10)),
        ("10.05.2024", date(2024, 5, 10)),
    ],
)
def test_parse_as_of_date_accepts_iso_and_indian_formats(value, expected):
    assert parse_as_of_date(value) == expected


def test_parse_as_of_date_rejects_invalid_calendar_date():
    with pytest.raises(PublicPredictionError):
        parse_as_of_date("31/02/2024")


def test_nifty_security_id_requires_unique_match():
    import pandas as pd

    master = pd.DataFrame({
        "SEM_SMST_SECURITY_ID": ["13", "14"],
        "SEM_SEGMENT": ["I", "I"],
        "SEM_EXM_EXCH_ID": ["NSE", "NSE"],
        "SEM_TRADING_SYMBOL": ["NIFTY 50", "OTHER"],
    })
    assert find_nifty50_security(master) == "13"
