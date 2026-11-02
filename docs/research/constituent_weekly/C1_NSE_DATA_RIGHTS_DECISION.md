# C1 NSE Data Rights Decision and Permitted Research Route

**Decision date:** 2026-11-03  
**Status:** AUTOMATED NSE WEBSITE COLLECTION STOPPED PENDING WRITTEN PERMISSION / SUITABLE AGREEMENT

## Decision

Do not scale the existing four-date NSE PR archive/schema probe into a bulk or systematic archive crawl. The probe is retained as a historical technical-feasibility result only. Future workflows set the NSE archive probe scope to false, including manual dispatch.

## Basis

NSE's current Terms of Use prohibit systematic or automated data collection on or in relation to its website (including scraping, data mining, extraction and harvesting) without express written consent. The same terms restrict use of website data/content for gaming, virtual trading and simulation activities.

Source: https://www.nseindia.com/static/nse-terms-of-use

NSE's Data Sharing & Usage Policy defines Market Data broadly, including historical and corporate data. Subscriber handling, use and redistribution are governed by the relevant agreement; redistribution is restricted unless agreed. The policy describes separate licensing for use of market data to create a financial index or instrument. The project's prediction and future trading-simulation use is not assumed exempt; the exact scope remains a legal/licensing question.

Source: https://www.nseindia.com/static/market-data/nse-data-policy

The four-date PR archive probe passed on 2018-04-02, 2024-04-16, 2025-10-14 and 2026-04-17. It inspected archive/schema availability only. It did not collect event rows and did not grant data rights. No further automated archive download will occur absent written permission/agreement that explicitly covers the intended research and backtest use.

## Permitted work route currently used

1. **Dhan subscribed Data API:** use for daily and intraday price history under the user's current Dhan API agreement. Dhan documents daily historical OHLCV adjustment for bonus/split events; intraday-versus-daily matching has now been tested on two events only.
2. **Issuer-first-party evidence:** verify event terms and dates from issuer annual reports, corporate-action pages, investor-relations notices and official filings where the issuer's access terms permit. Do not mass-scrape exchange websites.
3. **TejHQ discovery catalogue:** personal-use-only. Use only for the user's personal research; retain raw source data in encrypted cache, do not redistribute and do not use for client/business services. The private candidate queue is encrypted to a recipient-only key and uploaded as ciphertext for one day; no cleartext event rows are published.
4. **Unresolved events:** if issuer terms, event timing or security identity cannot be independently established from permitted evidence, mark SOURCE_UNRESOLVED/IDENTITY_UNRESOLVED and exclude affected stock-cycle rows before confirmatory model fitting.

## Current sample evidence

Protected run [41510761625](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41510761625) passed the two registered daily and same-session intraday comparisons:
- RELIANCE 1:1 bonus (2024-10-28): Dhan adjusted daily OHLC factor 0.5 across 9/9 sessions; intraday full-session OHLC matched Dhan adjusted daily OHLC on the same dates.
- BAJAJFINSV 5:1 split + 1:1 bonus (2022-09-13): Dhan adjusted daily OHLC factor 0.1 across 11/11 sessions; intraday full-session OHLC matched Dhan adjusted daily OHLC on the same dates. New trading ISIN is mapped from 2022-09-13 inclusive by adjudication; the raw TejHQ identifier is retained unchanged and flagged stale.

These are two-event diagnostics, not full C1 acceptance.

## Next bounded task

Create the private recipient-encrypted queue for 37 complex point-in-time member-event candidates (19 bonus, 9 split, 6 rights, 3 merger/demerger). Use issuer-first-party evidence to verify terms where permitted. Rights issues require entitlement ratio and subscription terms; merger/demerger requires scheme ratio and effective dates. Any unresolved affected security-cycle is excluded. After that, handle 20 buybacks and 29 AGM/other candidates; dividends are kept consistent with the NIFTY price-index target and are not mechanically reinvested.

## Gate status

- NSE four-date archive technical probe: PASS 4/4; no bulk rights.
- Automated NSE website collection: STOPPED pending written permission/agreement.
- Dhan two-event adjusted scale checks: PASS on two samples only.
- Issuer-level verification of remaining candidates: NOT STARTED.
- C1 corporate-action gate: NOT PASSED.
- C1 overall: PARTIAL.
- C2 panel: previously accepted with C1 limitations.
- C4 confirmatory aggregation and C5 strategy: GATED.
