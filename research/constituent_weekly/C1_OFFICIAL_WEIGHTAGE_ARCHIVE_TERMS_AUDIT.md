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


## Additional official-source and free-alternative review — 2026-11-01

### Official monthly report family now confirmed on the current publisher page

The current NSE Indices [Monthly Reports page](https://www.niftyindices.com/reports/monthly-reports) lists both **"Indices Market Capitalisation & Weightage (zip)"** and **"Market Capitalisation, Weightage, Beta (Zip)"**. This confirms a real official route for monthly weight records, not merely the previously inferred filename pattern. No ZIP was downloaded or parsed in this review.

The current [Nifty Indices Terms of Use](https://www.niftyindices.com/terms-of-use) prohibit systematic or automated data collection without express written consent, prohibit copying/reproducing/redistributing site content without prior written permission, and limit general website use to personal non-commercial use. Therefore this public report listing is not permission for the project's automated download, repository caching or public redistribution. NSE's own [Index Data Subscription page](https://www.nseindia.com/static/nse-indices/index-data-subscription) explicitly describes licensed constituent products including identifiers, market capitalisation, weights and prices, and gives `indices@nse.co.in` for licensing enquiries.

### IWF methodology makes a simple public-float proxy insufficient

The official [Guideline on Investible Weight Factors](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Guideline_Investible_Weight_Factors.pdf) states that IWF is derived from quarterly shareholding-pattern disclosures. It lists 22 categories to exclude where identifiable separately, including promoter/DR and associate cross-holdings, family and promoter trusts, employee trusts, directors/KMP, strategic holdings, government, FDI, private equity/funds, sovereign wealth funds, locked-in shares, IEPF and persons acting in concert. The guideline's example rounds IWF to six decimals. Thus `1 - promoter_pct`, `public_pct`, FII/DII flows, or total market capitalisation cannot be substituted for IWF.

### Additional open data candidate assessed

The GitHub project [aditya-jha/nse-historical-membership](https://github.com/aditya-jha/nse-historical-membership) publishes a point-in-time quarterly shareholding output for 2,261 symbols and 108 quarters (2001-03 to 2026-04), under a stated CC BY 4.0 data licence. Its shipped flat table is aggregated to ticker/period/promoter/FII/DII/public/pledge percentages. It does **not** publish the detailed 22-category exclusions needed to calculate official IWF. Its data-licence attribution note also describes NSE press releases/circulars, while this shareholding module is described as parsed from NSE XBRL filings; provenance/redistribution scope for this particular module therefore needs confirmation before bulk import. It is a candidate source for a future ownership/sentiment feature audit, not an accepted weight source.

The [AMP4010 historical weight candidate](https://huggingface.co/datasets/AMP4010/Historical_Nifty_50_Constituent_Weights_20Y) remains CC BY-NC-SA 4.0, ends 2025-08-31, and documents extrapolated weights around rebalances. It is not admitted for the primary or commercial trading track. Binary/equal-weight membership files are not numerical IWF.

### Updated decision

- Free-source search has identified: (a) official monthly weight archives that require a permission/licence decision for automated extraction and use; and (b) reusable public membership/shareholding datasets that do not supply the complete IWF exclusion data.
- No legally cleared, complete, point-in-time numerical IWF series with effective/publication dates and the full 22-category treatment has been identified for BUP-01.
- Do not scrape the monthly archive, store its ZIPs, or use third-party approximations as a primary weight series.
- Next permitted route is a written permission/licence covering machine retrieval, cache retention, research/backtesting, internal trading use and any intended publication, or a separately licensed vendor data feed. The permission scope must be recorded before automation.

Additional references:
- Nifty Indices official IWF guidance: https://www.niftyindices.com/resources/investible-weight-factors
- NSE official shareholding-pattern filings page: https://www.nseindia.com/companies-listing/corporate-filings-shareholding-pattern
- NSE IWF guideline PDF: https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Guideline_Investible_Weight_Factors.pdf
- Quarterly shareholding candidate dataset: https://github.com/aditya-jha/nse-historical-membership
