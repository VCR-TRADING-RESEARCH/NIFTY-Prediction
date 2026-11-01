# C1 Independent NSE Bhavcopy Mirror Cross-check

Updated: 2026-11-01T19:22:14.652536+00:00
Status: PARTIAL_SOURCE_COVERAGE

## Result

- Valid independent EQ OHLCV rows: 4/7.
- No EQ row in mirror: 3 (not proof that the exchange bar did not exist).
- Duplicate rows: 0; source partitions unavailable: 0.
- Raw prices and volume values are not published in this report.

| Security | Date | Session | Mirror disposition | OHLC | Volume | Identity |
|---|---|---|---|---|---|---|
| HDFC | 2018-11-07 | Diwali Muhurat | VALID_EQ_OHLCV_ROW | PASS | PASS | MATCH |
| HDFC | 2019-10-27 | Diwali Muhurat (Sunday) | NO_EQ_ROW_IN_MIRROR | - | - | NOT_CHECKED |
| HDFC | 2020-02-01 | Union Budget special session | NO_EQ_ROW_IN_MIRROR | - | - | NOT_CHECKED |
| HDFC | 2020-11-14 | Diwali Muhurat (Saturday) | NO_EQ_ROW_IN_MIRROR | - | - | NOT_CHECKED |
| HDFC | 2021-11-04 | Diwali Muhurat | VALID_EQ_OHLCV_ROW | PASS | PASS | MATCH |
| HDFC | 2022-10-24 | Diwali Muhurat | VALID_EQ_OHLCV_ROW | PASS | PASS | ISIN_NOT_PUBLISHED_IN_MIRROR |
| TATAMOTORS | 2025-10-21 | Diwali Muhurat (13:45-14:45) | VALID_EQ_OHLCV_ROW | PASS | PASS | ISIN_NOT_PUBLISHED_IN_MIRROR |

## Source and provenance

- Repository: https://github.com/floyds1995/Auto-Index-Constituents-Tracker
- Pinned revision: aa57b1050383c33e436f81844230ad2a4d52c949
- README: https://github.com/floyds1995/Auto-Index-Constituents-Tracker/blob/aa57b1050383c33e436f81844230ad2a4d52c949/README.md
- Downloader: https://github.com/floyds1995/Auto-Index-Constituents-Tracker/blob/aa57b1050383c33e436f81844230ad2a4d52c949/NSE/RawDataOHLCV/update_ohlcv.py
- Source README says NSE daily records originate from NSE bhavcopy archive endpoints. MIT licence covers repository code; no separate data licence was found. Raw data are not retained or redistributed.

## Interpretation

The mirror can corroborate rows it collected. Its downloader computes missing weekdays only; it does not systematically enumerate weekend exchange sessions. An absent row for 2019-10-27, 2020-02-01 or 2020-11-14 therefore cannot be read as evidence that no bhavcopy existed. Those dates remain unresolved pending a source with explicit special-session coverage.
No dates were removed from the denominator, no OHLCV values were inferred, and no adjustment factor was applied. Corporate-action audit remains a separate C1 blocker.

## Reproducibility

- Per-month Parquet SHA-256 hashes are recorded in the JSON report.
- C1_DAILY_COVERAGE.json remains the source of record for the original 106,385 / 106,392 coverage calculation.
