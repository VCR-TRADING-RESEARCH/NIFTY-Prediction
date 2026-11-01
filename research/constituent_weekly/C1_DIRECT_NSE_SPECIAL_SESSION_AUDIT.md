# C1 Direct NSE Special-session Bhavcopy Audit

Updated: 2026-11-01T19:46:28.089947+00:00
Status: PARTIAL_DIRECT_ARCHIVE_COVERAGE

Direct NSE EQ OHLCV rows validated: 0/3.

| Date | Security | Session | Result | OHLC | Volume |
|---|---|---|---|---|---|
| 2019-10-27 | HDFC | Sunday Diwali Muhurat | NO_EQ_ROW_IN_DIRECT_NSE_ARCHIVE | — | — |
| 2020-02-01 | HDFC | Saturday Union Budget special session | NO_EQ_ROW_IN_DIRECT_NSE_ARCHIVE | — | — |
| 2020-11-14 | HDFC | Saturday Diwali Muhurat | NO_EQ_ROW_IN_DIRECT_NSE_ARCHIVE | — | — |

## Method

Fetched each exact legacy NSE cash-market bhavcopy ZIP from both documented archive hosts, parsed its CSV, filtered exact SYMBOL/EQ/DATE1, validated OHLC ordering and nonnegative volume. Only source URL, archive SHA-256 and validation flags are retained; raw values are not published.

## Interpretation

A missing file or absent row is not automatically classified as a holiday/no-trade day. All three dates remain in the expected-session denominator unless exchange evidence supports a registered exclusion.

## Limitations
- Legacy CSV may omit ISIN; identity is then symbol/series/date only.
- HTTP 404 is unavailable, not proof of no trade.
- OHLCV validation does not complete the corporate-action adjustment ledger.
