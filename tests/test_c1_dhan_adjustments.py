from __future__ import annotations

import pandas as pd

from scripts.constituent_weekly.audit_c1_dhan_adjustments import EVENTS, compute_adjustment_diagnostic, public_event_metadata

DATES = ["2024-10-21", "2024-10-22", "2024-10-23", "2024-10-24", "2024-10-25",
         "2024-10-28", "2024-10-29", "2024-10-30", "2024-11-04"]


def reliance_frames(pre_factor=0.5, post_factor=1.0):
    raw_rows, dhan_rows = [], []
    for day in DATES:
        raw_close = 100.0 if day < "2024-10-28" else 50.0
        factor = pre_factor if day < "2024-10-28" else post_factor
        row = {"session_date": day, "isin": "INE002A01018",
               "open": raw_close, "high": raw_close + 2, "low": raw_close - 2,
               "close": raw_close + 1, "volume": 1000}
        raw_rows.append(row)
        dhan_rows.append({"session_date": day,
                          **{field: row[field] * factor for field in ("open", "high", "low", "close")},
                          "volume": row["volume"]})
    return pd.DataFrame(dhan_rows), pd.DataFrame(raw_rows)


def test_reliance_1_to_1_bonus_adjustment_detects_half_relative_factor():
    dhan, raw = reliance_frames()
    result = compute_adjustment_diagnostic(dhan, raw, DATES, "2024-10-28", 0.5,
                                           "INE002A01018", "INE002A01018")
    assert result["status"] == "PASS_ADJUSTMENT_FACTOR"
    assert result["dates_checked"] == 9
    assert result["factor_check_passed"] and result["post_factor_check_passed"]
    assert result["isin_transition_verified"] is True
    assert all(value == 0.5 for value in result["relative_event_factor_by_ohlc"].values())
    assert "INE002A01018" not in str(result)
    assert "100.0" not in str(result)


def test_bajaj_finserv_split_plus_bonus_detects_tenth_factor_and_known_isin_change():
    dates = ["2022-09-05", "2022-09-06", "2022-09-07", "2022-09-08", "2022-09-09", "2022-09-12",
             "2022-09-13", "2022-09-14", "2022-09-15", "2022-09-16", "2022-09-19"]
    raw_rows, dhan_rows = [], []
    for day in dates:
        raw_close = 1000.0 if day < "2022-09-13" else 100.0
        factor = 0.097 if day < "2022-09-13" else 0.97
        row = {"session_date": day, "isin": "INE918I01018" if day < "2022-09-13" else "INE918I01026",
               "open": raw_close, "high": raw_close + 20, "low": raw_close - 20,
               "close": raw_close + 10, "volume": 1000}
        raw_rows.append(row)
        dhan_rows.append({"session_date": day,
                          **{field: row[field] * factor for field in ("open", "high", "low", "close")},
                          "volume": row["volume"]})
    result = compute_adjustment_diagnostic(pd.DataFrame(dhan_rows), pd.DataFrame(raw_rows),
                                           dates, "2022-09-13", 0.1,
                                           "INE918I01018", "INE918I01026")
    assert result["status"] == "PASS_ADJUSTMENT_FACTOR"
    assert result["isin_transition_verified"] is True
    assert all(abs(value - 0.1) < 1e-6 for value in result["relative_event_factor_by_ohlc"].values())
    assert "INE918I01018" not in str(result) and "INE918I01026" not in str(result)


def test_adjustment_diagnostic_fails_when_bonus_factor_is_not_applied():
    dhan, raw = reliance_frames(pre_factor=1.0, post_factor=1.0)
    result = compute_adjustment_diagnostic(dhan, raw, DATES, "2024-10-28", 0.5,
                                           "INE002A01018", "INE002A01018")
    assert result["status"] == "FAIL_OR_INCOMPLETE_FACTOR"
    assert result["factor_check_passed"] is False


def test_adjustment_diagnostic_fails_closed_on_missing_sessions():
    dhan, raw = reliance_frames()
    result = compute_adjustment_diagnostic(dhan.iloc[:-1], raw, DATES, "2024-10-28", 0.5,
                                           "INE002A01018", "INE002A01018")
    assert result["status"] == "INCOMPLETE_DATE_MATCH"
    assert result["dates_matched"] == 8


def test_adjustment_diagnostic_rejects_unexpected_isin_transition():
    dhan, raw = reliance_frames()
    raw.loc[0, "isin"] = "DIFFERENT"
    result = compute_adjustment_diagnostic(dhan, raw, DATES, "2024-10-28", 0.5,
                                           "INE002A01018", "INE002A01018")
    assert result["status"] == "ISIN_SET_MISMATCH"


def test_bajaj_finserv_isin_transition_must_occur_on_ex_date():
    dates = ["2022-09-08", "2022-09-09", "2022-09-12", "2022-09-13", "2022-09-14", "2022-09-15"]
    raw_rows, dhan_rows = [], []
    for day in dates:
        value = 100.0 if day < "2022-09-13" else 10.0
        isin = "INE918I01018" if day < "2022-09-13" else "INE918I01026"
        raw_rows.append({"session_date": day, "isin": isin, "open": value, "high": value + 1,
                         "low": value - 1, "close": value, "volume": 100})
        dhan_rows.append({"session_date": day, "open": value * 0.1 if day < "2022-09-13" else value,
                          "high": (value + 1) * 0.1 if day < "2022-09-13" else value + 1,
                          "low": (value - 1) * 0.1 if day < "2022-09-13" else value - 1,
                          "close": value * 0.1 if day < "2022-09-13" else value, "volume": 100})
    raw_rows[3]["isin"] = "INE918I01018"
    result = compute_adjustment_diagnostic(pd.DataFrame(dhan_rows), pd.DataFrame(raw_rows),
                                           dates, "2022-09-13", 0.1,
                                           "INE918I01018", "INE918I01026")
    assert result["status"] == "FACTOR_PASS_IDENTITY_WARNING"
    assert result["factor_check_passed"] is True
    assert result["isin_transition_verified"] is False
    assert result["identity_mismatch_dates"] == ["2022-09-13"]
    assert result["observed_post_isin_first_date"] == "2022-09-14"


def test_public_event_metadata_allows_missing_identity_source():
    reliance = next(event for event in EVENTS if event["symbol"] == "RELIANCE")
    bajaj = next(event for event in EVENTS if event["symbol"] == "BAJAJFINSV")
    assert public_event_metadata(reliance)["identity_source"] is None
    assert public_event_metadata(bajaj)["identity_source"].endswith("CML53597.pdf")
