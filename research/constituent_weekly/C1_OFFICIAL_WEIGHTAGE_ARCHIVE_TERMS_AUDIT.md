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


## Additional free-source candidates and technical IWF feasibility — 2026-11-01

### 1. Official IWF rule: exact exclusions, not a promoter-percentage proxy

The current NSE Indices guideline describes IWF as the fraction of company shares expected to be available for trading, based on quarterly exchange-reported shareholding patterns. It requires subtraction, where separately identifiable, of 22 categories: promoter category; promoter/promoter-group DRs; associate/group cross-holdings; promoter family; promoter-managed trusts; employee trusts; directors; public holders with board nomination/representation rights; KMP; first-refusal rights; strategic corporate holdings; direct/indirect government holdings (two cases); FDI; PE investors; PE funds; foreign VC; SWFs; public lock-in; IEPF; and persons acting in concert with promoters. Its worked example calculates (total shares − identified excluded shares) / total shares and rounds IWF to six decimals. See the [official two-page guideline](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Guideline_Investible_Weight_Factors.pdf).

The implication for this project is that `1 - promoter_pct`, `public_pct`, FII/DII ownership, or an ownership-category roll-up cannot automatically be labelled official IWF. Each exclusion must be mapped to its shareholding fact, with overlap/double-count controls and an explicit “not separately identified” state. The denominator must follow the exact share-base rule in the applicable historical taxonomy. Publication time and filing period must be stored separately; only a filing broadcast before the 10:00 forecast timestamp is admissible.

### 2. Detailed quarterly XBRL category dataset — promising, but not admitted

Repository: [yurukatsu/nse-historical-membership](https://github.com/yurukatsu/nse-historical-membership), folder `shareholding_history/`. Its README describes 2,316 symbols and 62,850 filings from 2001-03 through 2026-08, with a `_categories.csv.gz` table containing approximately 70 filing-by-category observations. The documented columns include category shares, voting rights, demat shares, locked-in shares, pledged/encumbered shares, DR shares, warrants and sub-category share counts. The filing keys include `filing_date`, `submission_date` and `broadcast_date`; its documentation reports broadcast time at 100% coverage and says it differs from submission date on 18% of filings (90th percentile 79 days). The separate `_shareholders.csv.gz` contains named shareholder rows.

This is materially richer than the simpler 47-column promoter/FII/DII/public roll-up and is a candidate for a category-to-IWF reconstruction experiment. However:
- The upstream `LICENSE-DATA` text explicitly lists `*/data/*.csv`, `*/data/parsed/*.json` and `*/data/manual_overrides/*.json`. The detailed output is `shareholding_history/data/parsed/_categories.csv.gz`; the advertised licence path patterns do not unambiguously include that nested compressed CSV, nor the nested `_flat.csv`. The README's general “Data: CC BY 4.0” statement and the detailed licence globs are not perfectly aligned. Do not copy/cache/import these files until the maintainer confirms that the specific compressed and parsed CSV paths are CC BY 4.0 (or supplies a corrected explicit licence).
- The 70 categories can potentially identify several IWF exclusions (promoter, government, FDI, PE/FPI/SWF categories, directors/KMP, IEPF, lock-in, DR), but aggregate category rows cannot by themselves prove holder relationships or agreements such as group cross-holdings, promoter family/PAC status, board representation, first-refusal rights and strategic control. A mapping completeness matrix and independent spot-check against official XBRL examples are required.
- Point-in-time use must use `broadcast_date`, not merely quarter-end `period` or `submission_date`; revisions must be ordered by publication timestamp. Use the latest revision broadcast before each forecast time, retaining the as-of period and source filing identity.
- Do **not** ingest or publish `_shareholders.csv.gz` as part of this project. It contains named individual shareholders. The intended research dataset is category aggregates only; no names, PANs or personal identifiers are needed.
- No file from this repository was downloaded, imported or copied into this project during this audit.

**Decision:** retain as a high-priority candidate, but **not admitted** pending written path-specific licence confirmation and a 22-category mapping/completeness test. Even after those checks, any missing relationship/agreement categories must remain explicitly unresolved and be tested against official monthly weights; do not silently treat them as zero.

### 3. TejHQ daily EOD and corporate-action data — useful secondary cross-check

The [TejHQ Indian Markets dataset](https://huggingface.co/datasets/tejhq/indian-markets) documents NSE daily OHLCV from 2010-01-04 onward and includes raw bhavcopy, adjusted-price, corporate-action and ISIN/symbol-history trees. Its publisher's [data terms, updated 2026-10-30](https://tejhq.dev/data-terms), explicitly permit personal research, backtesting, model training, personal trading decisions and private local storage; they prohibit redistribution/public mirroring of raw data and say the publisher holds no NSE/BSE licence, so exchange terms independently apply. The code's MIT licence does not cover the market data. Keyless OHLCV, snapshots and corporate actions are offered by its API; the terms document a 120-request/minute keyless rate limit.

This is admitted as a **candidate secondary EOD/corporate-action/symbol-history cross-check only**, subject to source provenance and exchange-term review. It is not 1-minute data, an official NIFTY 50 membership ledger, or a numerical IWF series. Its top-500 liquidity universe must not be mistaken for official NIFTY 50 membership. Because this repository is public and GitHub cache contents can be extracted by people able to open a pull request, raw TejHQ data must not be committed or put in a public Actions cache; retain only non-reconstructive QA summaries/manifests in this public repo. A secure private store would be required to retain its raw files here without redistribution risk.

### 4. Official exchange public shareholding/XBRL access

NSE's current shareholding-pattern page displays quarter-end date, submission date, revision date, XBRL link and broadcast date/time. The XBRL filing-information page publishes the Regulation 31 Shareholding Pattern taxonomy and sample. This supports the existence of a structured primary filing route, but does not override the Nifty Indices restriction on automated collection of its website. The current Nifty Indices Terms of Use prohibit systematic/automated collection without express written consent; the monthly ZIP listing is therefore discovery, not permission to scrape, cache or republish. NSE Indices offers licensed constituent products with identifiers, market cap, weights and prices and lists `indices@nse.co.in` for licensing enquiries.

SEBI's 2024 market-data sharing policy also establishes a research-data sharing framework, including a first-basket of mandated public disclosures; the enhanced MII data-access route is directed to accredited academic institutions. This project has not established accredited-institution status or a data-sharing arrangement, so that policy is not treated as blanket authorization for this repo to automate XBRL extraction.

### 5. Current source-gate decision

| Candidate | What it can supply | Rights / quality decision | BUP-01 use |
|---|---|---|---|
| Official NSE Indices monthly weight ZIPs | Official monthly weightage / market-cap snapshots | Exact automated access, caching and intended use require permission/licence decision | Preferred IWF reconciliation source after permission |
| `yurukatsu/nse-historical-membership` category-level XBRL parse | ~70 category aggregates, broadcast timestamps and 2001–2026-08 history | Specific nested `.csv.gz` licence scope unclear; some of 22 exclusions need holder/agreement context | High-priority candidate, not admitted |
| TejHQ daily EOD/corporate-actions/symbol history | Daily prices from 2010, event and ISIN-symbol history | Publisher allows personal research and private storage; no raw redistribution and exchange rights remain independently applicable | Secondary daily/corporate-action QA; no IWF or intraday target |
| AMP4010 HF historical weights | Monthly approximate weights to 2025-08 | CC BY-NC-SA 4.0, estimated/extrapolated rebalance values | Not admitted for primary/commercial track |
| Binary/equal-weight membership projects | Member/non-member only | Not numerical IWF | Membership cross-check only |

**Gate remains:** no admissible official point-in-time IWF series is yet present. Do not begin confirmatory stock-panel modelling, weighted aggregation, or trading validation until the rights issue and weight reconstruction/reconciliation gates pass. The BUP-01 v1.1 plan remains locked; no research-plan amendment has been made.
