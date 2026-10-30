# NIFTY Options Data Audit — Research Gate 1

**Run:** GitHub Actions `41144264886`  
**Date:** 2026-10-31  
**Source:** `rissin/nse-options-intraday`, NIFTY 1-minute Parquet partitions  
**Result:** <badge>PASS</badge> basic schema/OHLC integrity; <badge>BLOCKED</badge> execution-fidelity and requested-period gates

## Coverage

| Partition | Rows | File size | Timestamp coverage (IST) | Expiry coverage |
|---|---:|---:|---|---|
| 2024 | 14,592,609 | 140,912,219 bytes | 2024-10-01 09:15 to 2024-12-31 15:29 | 2024-10-03 to 2026-06-30 |
| 2025 | 69,687,860 | 674,710,222 bytes | 2025-01-01 09:15 to 2025-12-31 15:29 | 2025-01-02 to 2026-06-30 |
| 2026 | 40,177,780 | 394,805,617 bytes | 2026-01-01 09:15 to 2026-07-21 15:29 | 2026-01-06 to 2026-07-21 |
| **Total** | **124,458,249** | **1,210,428,058 bytes** | **2024-10-01 to 2026-07-21** | **2024-10-03 to 2026-07-21** |

The audit scanned all 124,458,249 rows. The requested 2021–2026 sample is not available from this source: 2021-10 through 2024-09 is missing, and the 2026 partition ends on 2026-07-21.

## Integrity and tradability checks

| Check | Result |
|---|---:|
| Null OHLC rows | 0 |
| Non-positive OHLC rows | 0 |
| Malformed OHLC rows | 0 |
| Null OI rows | 0 |
| Null volume rows | 0 |
| Zero-volume rows | 65,768,348 (52.84%) |
| Negative-volume rows | 35 |
| Positive-volume rows | 58,689,866 (47.16%) |
| Invalid timestamps | 0 |

**Execution rule:** zero-volume and negative-volume rows are not eligible for entry or exit fills. The 35 negative-volume rows must be excluded and recorded. A valid OHLC candle does not prove a trade was executable.

**Available fields:** timestamp, expiry, strike, option_type, OHLC, volume, OI, source and granularity. There is no intraday IV field and no bid/ask quote field in the audited schema. Delta must therefore be reconstructed from option premium and synchronized spot using a documented implied-volatility solver; this is an approximation to last-traded-price IV, not a quoted mid-market Greek.

## Strategy-relevant limitations

1. **Period gap:** the free archive cannot support the requested 2021–2026 test. Its intraday window is about 22 months.
2. **No IV / bid-ask:** delta-based leg selection requires inferred IV from traded premiums; execution requires conservative next-bar fills and adverse slippage. Results would be exploratory.
3. **Sparse volume:** only 47.16% of bars have positive volume. The engine must not fill from zero-volume bars or carry stale OHLC as executable prices.
4. **VWAP:** NIFTY spot is a calculated index with no traded volume. The proposed VWAP filter requires a verified NIFTY futures price-volume series. The existing spot minute archive cannot supply it. An A-without-VWAP run is a separate ablation, not a faithful test of strategy A.
5. **Dhan:** authenticated collection has not passed. Token renewal/TOTP was inconsistent, and the rolling-options request returned DH-905 for the tested requiredData payload. No Dhan raw options data was downloaded. The Dhan workflow is retained for manual dispatch and monthly scheduled retry after credentials/request parameters are corrected.
6. **Licence:** the dataset card labels the licence as `other`. Raw Parquet is not committed or redistributed; confirm source terms before external/commercial use.

## Gate decision

- Basic schema, OHLC and timestamp checks: **PASS**.
- OI/volume field presence: **PASS**, with zero/negative volume exclusions required.
- Full 2021–2026 coverage: **FAIL**.
- Exact delta selection: **EXPLORATORY only** until IV reconstruction is validated.
- Exact VWAP rule: **BLOCKED** until a synchronized futures volume series is obtained.
- Contract-level strategy P&L: **NOT RUN**. No strategy profitability, win rate, expectancy or drawdown is claimed.

The next defensible options are (a) restore Dhan access and resolve the rolling-options request, then pursue the full five-year chain, or (b) explicitly authorize a limited 2024-10 to 2026-07 exploratory backtest with reconstructed delta and a no-VWAP ablation. The latter must not be represented as validation of the original full strategy.
