# C1 Independent NSE Bhavcopy Mirror — Method Note

**Purpose:** Independently check the seven residual daily OHLCV member-session keys without repeating the full Dhan history request or treating special-session dates as holidays.

## Frozen scope

| Symbol | Date | Session |
|---|---|---|
| HDFC | 2018-11-07 | Diwali Muhurat |
| HDFC | 2019-10-27 | Diwali Muhurat (Sunday) |
| HDFC | 2020-02-01 | Union Budget special session |
| HDFC | 2020-11-14 | Diwali Muhurat (Saturday) |
| HDFC | 2021-11-04 | Diwali Muhurat |
| HDFC | 2022-10-24 | Diwali Muhurat |
| TATAMOTORS | 2025-10-21 | Diwali Muhurat (13:45–14:45) |

## Source

The check uses a pinned revision of floyds1995/Auto-Index-Constituents-Tracker, specifically its monthly NSE equity OHLCV Parquet archive and updater. Its README says it stores daily NSE bhavcopy data and describes the source endpoints as NSE archives. The exact source revision is fixed in the audit script.

The repository's MIT licence is for code. A separate market-data licence was not identified. Therefore the audit processes Parquet files in runner temporary storage, records SHA-256 fingerprints and validity flags only, and does not commit raw values or upload raw data as an artifact.

## Validation

For each exact symbol/date, the script filters the EQ series, requires exactly one row, validates positive finite OHLC, checks low/open/close/high ordering, and checks finite nonnegative volume. If the source publishes ISIN, it is checked against the dated security identity; if the source omits ISIN, that limitation is explicit.

No raw price, OHLC or volume values are written to the repository. Results contain source hashes, row counts, field-validity flags and identity status only.

## Known source-calendar limitation

The source updater enumerates weekdays when discovering missing dates. It does not systematically enumerate weekend exchange sessions. Thus an absent Sunday or Saturday row cannot establish that the exchange did not trade. These three target dates require another source with explicit special-session coverage:

- 2019-10-27 (Sunday Muhurat session)
- 2020-02-01 (Saturday Budget session)
- 2020-11-14 (Saturday Muhurat session)

A row absent from this mirror is reported as NO_EQ_ROW_IN_MIRROR, not as a waived or invalid market session. All seven dates remain in the original coverage denominator.

## Gate and downstream impact

This cross-check can corroborate rows for dates the mirror actually contains. It does not validate the full corporate-action ledger and does not unlock C2. No prices are imputed, no returns are adjusted, and no trading strategy is approved by this step.
