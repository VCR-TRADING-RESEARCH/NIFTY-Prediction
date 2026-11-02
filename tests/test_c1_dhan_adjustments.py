from __future__ import annotations

import pandas as pd

from scripts.constituent_weekly.audit_c1_dhan_adjustments import compute_adjustment_diagnostic


DATES = ["2024-10-21", "2024-10-22", "2024-10-23", "2024-10-24", "2024-10-25",
         "2024-10-28", "2024-10-29", "2024-10-30", "2024-11-04"]


def frames(pre_factor=0.5, post_factor=1.0, dates=DATES):
    raw_rows, dhan_rows = [], []
    for day in dates:
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
    dhan, raw = frames()
    result = compute_adjustment_diagnostic(dhan, raw, DATES, "2024-10-28", 0.5)
    assert result["status"] == "PASS_ADJUSTMENT_FACTOR"
    assert result["dates_checked"] == 9
    assert result["factor_check_passed"] and result["post_factor_check_passed"]
    assert all(value == 0.5 for value in result["relative_event_factor_by_ohlc"].values())
    assert "INE002A01018" not in str(result)
    assert "100.0" not in str(result)


def test_bajaj_finserv_split_plus_bonus_detects_tenth_factor_despite_later_adjustment():
    dates = ["2022-09-05", "2022-09-06", "2022-09-07", "2022-09-08", "2022-09-09", "2022-09-12",
             "2022-09-13", "2022-09-14", "2022-09-15", "2022-09-16", "2022-09-19"]
    raw_rows, dhan_rows = [], []
    for day in dates:
        raw_close = 1000.0 if day < "2022-09-13" else 100.0
        factor = 0.097 if day < "2022-09-13" else 0.97
        row = {"session_date": day, "isin": "INE918I01026",
               "open": raw_close, "high": raw_close + 20, "low": raw_close - 20,
               "close": raw_close + 10, "volume": 1000}
        raw_rows.append(row)
        dhan_rows.append({"session_date": day,
                          **{field: row[field] * factor for field in ("open", "high", "low", "close")},
                          "volume": row["volume"]})
    result = compute_adjustment_diagnostic(pd.DataFrame(dhan_rows), pd.DataFrame(raw_rows),
                                           dates, "2022-09-13", 0.1)
    assert result["status"] == "PASS_ADJUSTMENT_FACTOR"
    assert all(abs(value - 0.1) < 1e-6 for value in result["relative_event_factor_by_ohlc"].values())


def test_adjustment_diagnostic_fails_when_bonus_factor_is_not_applied():
    dhan, raw = frames(pre_factor=1.0, post_factor=1.0)
    result = compute_adjustment_diagnostic(dhan, raw, DATES, "2024-10-28", 0.5)
    assert result["status"] == "FAIL_OR_INCOMPLETE_FACTOR"
    assert result["factor_check_passed"] is False


def test_adjustment_diagnostic_fails_closed_on_missing_sessions():
    dhan, raw = frames()
    result = compute_adjustment_diagnostic(dhan.iloc[:-1], raw, DATES, "2024-10-28", 0.5)
    assert result["status"] == "INCOMPLETE_DATE_MATCH"
    assert result["dates_matched"] == 8


def test_adjustment_diagnostic_rejects_ambiguous_isin():
    dhan, raw = frames()
    raw.loc[0, "isin"] = "DIFFERENT"
    result = compute_adjustment_diagnostic(dhan, raw, DATES, "2024-10-28", 0.5)
    assert result["status"] == "AMBIGUOUS_OR_MISSING_ISIN"
