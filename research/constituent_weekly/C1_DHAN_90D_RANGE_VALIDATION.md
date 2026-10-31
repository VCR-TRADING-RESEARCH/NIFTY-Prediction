# C1 Dhan Full-Universe 90-Day Minute-Coverage Validation

**Date:** 2026-11-01  
**Workflow:** [41251346795](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41251346795)  
**Branch:** phase/constituent-weekly-outcomes-c1-data  
**Result:** PASS for the defined 90-day active-universe coverage probe only.

## Tested window and scope

- Request start: 2026-06-29
- Request end: 2026-09-26 (inclusive API window; 90 calendar days)
- Universe: point-in-time NIFTY 50 equity constituents active on 2026-06-29
- Security IDs resolved from the current Dhan NSE equity instrument master: 50/50
- Symbols with passing range QA: 50/50
- Dhan minute request: 1-minute bars, NSE equity segment
- API requests: one per symbol, sequential, 0.25 second spacing
- Raw OHLCV bars were not persisted to the public repository; only sanitised aggregate QA metrics were stored.

## Results

| Metric | Result |
|---|---:|
| Constituents expected | 50 |
| Security IDs resolved | 50/50 |
| Constituents passing | 50/50 |
| Bars per constituent | 23,414 |
| Total bars represented by the 50 aggregate counts | 1,170,700 |
| Regular sessions per constituent | 64 |
| Sessions with 10:00–10:03 anchor | 64/64 |
| Sessions with a valid 15:00–15:14 expiry proxy | 64/64 |
| Duplicate timestamps | 0 |
| Missing anchor sessions | 0 |
| Missing expiry-proxy sessions | 0 |
| OHLCV invariants | Pass for all 50 |
| Non-standard evening-only sessions in this date range | 0 |

The first returned bar was 09:16 IST on 2026-06-29 and the last returned bar was 15:14 IST on 2026-09-25 (the last trading session within the request window). The selected expiry proxy remains the latest valid one-minute close timestamped in the 15:00–15:14 IST window; no later bar is used.

## Related successful checks

- 2026-10-29 point-in-time current-universe daily preflight: 50/50 passed, in run [41249642409](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41249642409).
- 2022-10-03 through 2022-12-30 three-symbol history sample (RELIANCE, TCS, INFY): 3/3 passed, 61 normal sessions per symbol, 61/61 anchor and expiry-proxy coverage, no duplicates and OHLCV invariants pass, in run [41250854958](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41250854958). The evening-only Diwali Muhurat session on 2022-10-24 is separated from regular daytime sessions.
- Current run [41251346795](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41251346795): 23 offline tests passed; fresh Dhan token refresh succeeded; the 50-stock 90-day request and sanitized-result commit completed successfully.

## Interpretation and limitations

1. This establishes data availability and response quality for **one recent 90-day window** and the 50-name point-in-time universe active at the beginning of that window. It is not a full five-year point-in-time panel.
2. It does not prove coverage for constituents that were delisted, merged, renamed or inactive during earlier periods.
3. It does not establish correct corporate-action adjustment of minute bars. Dhan documents adjusted daily history for bonuses/splits; minute bars must be treated as a separate raw execution/label layer until their adjustment basis is established and any factors are applied explicitly.
4. It does not test or approve persistent storage/redistribution of raw Dhan or exchange-originated data. No raw bars were committed.
5. It does not validate the official NIFTY 50 free-float weight time series, expiry-calendar history, index reconstruction tolerance or bottom-up prediction accuracy.
6. C1 therefore remains **NOT PASSED** and C2/model training remains gated.

## Next C1 gates

- Test legacy/inactive constituent IDs over a bounded historical window, starting with HDFC Ltd pre-merger and other date-mapped identities.
- Extend 90-day coverage in controlled periods across the permitted five-year active-instrument history, while maintaining the public-repository no-raw-price rule.
- Resolve official point-in-time index weights under an authorised data-use route.
- Build and validate expiry-date alignment, corporate-action handling and constituent basket-to-NIFTY reconstruction before unlocking C2.
