from __future__ import annotations

import pandas as pd

from scripts.constituent_weekly.audit_c1_dhan_adjustments import compute_adjustment_diagnostic


DATES = ["2024-10-21", "2024-10-22", "2024-10-23", "2024-10-24", "2024-10-25",
         "2024-10-28", "2024-10-29", "2024-10-30", "2024-11-04"]


def frames(pre_factor=0.5, post_factor=1.0):
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


def test_reliance_1_to_1_bonus_adjustment_detects_half_factor_before_ex_date():
    dhan, raw = frames()
    result = compute_adjustment_diagnostic(dhan, raw)
    assert result["status"] == "PASS_BONUS_ADJUSTMENT_FACTOR"
    assert result["dates_checked"] == 9
    assert result["pre_factor_check_passed"] is True
    assert result["post_factor_check_passed"] is True
    assert all(value == 0.5 for value in result["pre_ex_date_median_factor_by_ohlc"].values())
    assert all(value == 1.0 for value in result["post_ex_date_median_factor_by_ohlc"].values())
    assert "INE002A01018" not in str(result)
    assert "100.0" not in str(result)


def test_adjustment_diagnostic_fails_when_bonus_factor_is_not_applied():
    dhan, raw = frames(pre_factor=1.0, post_factor=1.0)
    result = compute_adjustment_diagnostic(dhan, raw)
    assert result["status"] == "FAIL_OR_INCOMPLETE_FACTOR"
    assert result["pre_factor_check_passed"] is False


def test_adjustment_diagnostic_fails_closed_on_missing_sessions():
    dhan, raw = frames()
    result = compute_adjustment_diagnostic(dhan.iloc[:-1], raw)
    assert result["status"] == "INCOMPLETE_DATE_MATCH"
    assert result["dates_matched"] == 8


def test_adjustment_diagnostic_rejects_ambiguous_isin():
    dhan, raw = frames()
    raw.loc[0, "isin"] = "DIFFERENT"
    result = compute_adjustment_diagnostic(dhan, raw)
    assert result["status"] == "AMBIGUOUS_OR_MISSING_ISIN"
