# Official NIFTY 50 Monthly Weight Archive: Access and Terms Audit

Recorded: 2026-11-01  
Decision: archive located; no automated retrieval until express written permission or an applicable licence is confirmed.

## Source and archive structure

NSE Indices' monthly reports page lists the monthly "Market Capitalisation, Weightage, Beta" ZIP family. Independent project documentation reports monthly archives from June 2013 onward (159 files in its inventory). A public code example documents this apparent filename pattern:

`https://www.niftyindices.com/Market_Capitalisation_Weightage_Beta_for_NIFTY_50_And_NIFTY_Next_50/mcwb_{mon}{yy}.zip`

Here `mon` is the three-letter lowercase month and `yy` the two-digit year. This is a discovery lead, not an archive retrieval performed by this project. No ZIP payload was fetched or parsed in this audit.

Expected month-end fields, subject to later authorised schema validation, include constituent symbol/name, industry, closing price, index market capitalisation and index weight percentage. A month-end report cannot automatically be treated as an exact daily or intramonth weight series. Snapshot date and report publication/availability date must remain separate.

## Policy and terms

The NSE Research and Analysis Data Sharing Policy dated 2025-07-28 lists historical reports and historical index data in its first research/analysis data basket.

Separately, Nifty Indices' Terms of Use prohibit systematic or automated data collection (including scraping, data mining, extraction and harvesting) without express written consent. The terms also restrict copying/reproduction/distribution without prior written permission and describe site use as personal and non-commercial.

Public wording does not settle whether the first-basket policy grants automated retrieval rights for this specific ZIP archive, or whether the full intended workflow (recurring automation, caching and research leading to personal trading) is covered. We must not assume that "free for research" overrides the specific automated-collection restriction.

The NSE Indices data subscription page describes licensed products containing constituents, identifiers, market capitalisation, weights and prices.

## Decision

1. Do not automate archive requests, scrape the reports page, or reverse engineer browser/API calls without express written consent or a licence covering the proposed access.
2. Do not mirror or redistribute monthly ZIP files or extracted rows in this public repository unless written permission expressly allows it.
3. Keep the existing CC BY-NC-SA third-party monthly weights clearly separated and not for commercial use.
4. Keep the official 2026-02-27 white-paper snapshot as a one-date reference only.
5. Before enabling a fetch workflow, record the permission scope for automated access, caching, analysis, attribution and personal trading/research; then implement cache-first retrieval, hashes and strict schema/missing-month validation.
6. Until authorised monthly weights and historic price coverage are validated, C1 remains NOT PASSED and C2 stays gated.

## References

- NSE Indices monthly reports: https://www.niftyindices.com/reports/monthly-reports
- NSE Indices historical reports: https://www.niftyindices.com/reports/historical-data
- NSE Research and Analysis Data Sharing Policy: https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Research_and_Analysis_Data_Sharing_Policy.pdf
- Nifty Indices Terms of Use: https://www.niftyindices.com/terms-of-use
- NSE index data subscription: https://www.nseindia.com/static/nse-indices/index-data-subscription
- Independent monthly archive inventory: TradeEntry documentation.
- Independent filename-pattern example: FarzanBhalara/Discretized-Neural-SDE-for-Risk-Return-and-Market-regimes, step0_fetch_nifty50_panel.py.

Audit scope: source discovery and public-terms review only. No monthly ZIP was downloaded, opened or processed in this step.
