from datetime import date
import pytest

from live_api.app import PublicPredictionError, parse_as_of_date, find_nifty50_security, _first_official_session_after


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


def test_refresh_dhan_token_uses_post(monkeypatch):
    import live_api.app as live_app

    class Response:
        ok = True
        status_code = 200

        @staticmethod
        def json():
            return {"accessToken": "x" * 40}

    captured = {}

    def fake_post(url, *, params, timeout):
        captured.update(url=url, params=params, timeout=timeout)
        return Response()

    monkeypatch.setenv("DHAN_CLIENT_ID", "test-client")
    monkeypatch.setenv("DHAN_PIN", "123456")
    monkeypatch.setenv("DHAN_TOTP_SECRET", "JBSWY3DPEHPK3PXP")
    monkeypatch.setattr(live_app.requests, "post", fake_post)
    token, client_id = live_app.refresh_dhan_token()
    assert token == "x" * 40
    assert client_id == "test-client"
    assert captured["url"] == live_app.AUTH_URL
    assert set(captured["params"]) == {"dhanClientId", "pin", "totp"}


def test_next_session_uses_official_calendar_not_minute_coverage(tmp_path):
    # May 5, 2026 is a verified expiry; May 6 is the next official session.
    # Dhan minute coverage is deliberately irrelevant to this calendar helper.
    import pandas as pd

    official = tmp_path / "official.csv"
    pd.DataFrame({
        "session_date": ["2026-05-05", "2026-05-06", "2026-05-07"],
        "official_close": [24000.0, 24100.0, 24200.0],
    }).to_csv(official, index=False)

    assert _first_official_session_after(pd.Timestamp("2026-05-05"), official) == pd.Timestamp("2026-05-06")


def test_next_session_helper_rejects_missing_official_calendar(tmp_path):
    import pandas as pd

    official = tmp_path / "official.csv"
    pd.DataFrame({"session_date": ["not-a-date"], "official_close": [1.0]}).to_csv(official, index=False)
    with pytest.raises(PublicPredictionError, match="no session after"):
        _first_official_session_after(pd.Timestamp("2026-05-05"), official)
