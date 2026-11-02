# C1 Dhan Historical Point-in-Time 50-Stock 90-Day Validation

**Date:** 2026-11-01  
**Workflow:** [41251808946](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41251808946)  
**Branch:** phase/constituent-weekly-outcomes-c1-data  
**Result:** PASS for the defined 2022 historical point-in-time universe and one 90-day period.

## Tested universe and period

- Membership date: 2022-10-03
- Request window: 2022-10-03 through 2022-12-30 (90 calendar days)
- Source of membership: project point-in-time NIFTY 50 membership interval ledger
- Expected equity constituents: 50
- Security IDs resolved: 50/50
- Bar-quality checks passed: 50/50
- Interval: 1-minute Dhan NSE_EQ candles
- Data stored in the public repo: sanitized metadata only; raw OHLCV bars are not committed.

## Legacy identity handling

- HDFC Ltd: Dhan legacy security ID **1330**, previously sampled on 2022-10-31 and 2023-06-30; 2022Q4 range check passes.
- TATAMOTORS: for this pre-2025-10-24 window, mapped to the continuing TMPV security ID found in the current Dhan instrument master. This is a period-specific alias only. The price series is not stitched across the later Tata Motors demerger/rename event.
- All other point-in-time symbols resolved through the current Dhan NSE equity security master for this checked period.
- This successful 90-day sample does not prove every other inactive or delisted historical ID is available.

## Results

| Metric | Result |
|---|---:|
| Point-in-time NIFTY 50 members | 50 |
| Security IDs resolved | 50/50 |
| Stocks passing QA | 50/50 |
| Regular sessions per constituent | 61 |
| Anchor sessions present | 61/61 |
| Expiry-proxy sessions present | 61/61 |
| Duplicate timestamps | 0 |
| Missing anchor sessions | 0 |
| Missing expiry-proxy sessions | 0 |
| OHLCV invariants | Pass for all 50 |
| Total bars represented by sanitized counts | 1,146,180 |

Per-stock bar counts differ (22,918 to 22,998) due to the returned session/bar structure; all 50 passed the date-level anchor/expiry and numeric OHLCV checks.

## Workflow and regression validation

- The complete Dhan workflow succeeded.
- 24 offline tests passed in 1.89 seconds.
- Fresh TOTP authentication and Dhan profile/data-plan checks succeeded.
- The run also reran the recent 2026Q3 full-universe range and single-day current universe checks, all 50/50 passing.

## Interpretation

This demonstrates full point-in-time basket availability for one historical 2022 quarter, including the HDFC legacy ID and the dated TATAMOTORS/TMPV alias. Combined with the separate 2026Q3 full-universe pass, it provides two useful time-separated coverage anchors. It does **not** establish uninterrupted coverage between these samples, full five-year coverage for all constituents, or minute data for every inactive/delisted constituent.

It also does not validate corporate-action adjustment of minute bars, official historical free-float weights, the weekly expiry calendar, basket-to-NIFTY reconstruction tolerance or model predictive skill. No prediction model or trading strategy has been trained or approved.

**C1 remains NOT PASSED; C2 remains gated.**
