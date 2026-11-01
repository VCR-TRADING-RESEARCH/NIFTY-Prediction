# BUP-01 — IWF exclusion mapping and mathematical acceptance audit

**Date:** 2026-11-01  
**Plan:** BUP-01 v1.1 (unchanged)  
**Status:** Design audit complete; source data not licensed/imported; no official IWF reconstruction admitted.

## Purpose

Translate the official NSE Indices IWF guidance into an explicit 22-item evidence matrix before considering any category-level shareholding dataset. The row-by-row machine-readable matrix is [C1_IWF_EXCLUSION_MAPPING.csv](C1_IWF_EXCLUSION_MAPPING.csv).

The official two-page [IWF guideline](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Guideline_Investible_Weight_Factors_0.pdf) says IWF is based on quarterly public shareholding-pattern disclosures and excludes the 22 listed categories **where identifiable separately**. Its worked example uses total shares as the denominator, subtracts identified excluded share blocks, and rounds IWF to six decimal places. See PDF page 1 for the list and page 2 for the formula/example.

## Key mathematical distinction discovered

The third-party XBRL parser describes "pct_base_shares" as "total_shares - CustodianOrDRHolder shares" (the SEBI shareholding-pattern percentage base, A+B+C2). It separately preserves "total_shares" and the raw category share counts.

The official IWF guideline's numerical example instead shows:

"IWF = (Total Shares − sum of identified excluded shares) / Total Shares"

Therefore:
- Do **not** calculate IWF as "1 - promoter_pct", "public_pct", or from the parser's pre-computed percentages.
- Reconstruct exclusions from integer share counts and a fully reconciled issuer share-capital denominator.
- Do not assume "pct_base_shares" is the denominator for IWF. The official example uses total shares. Confirm the applicable historical share-capital denominator, C1/DR treatment and share class treatment against official files before accepting any reconstruction.
- The same position may satisfy several exclusion descriptions (e.g., promoter-related and DR-related). Count the underlying share position only once. A sum of 22 category aggregates is unsafe unless overlaps have been resolved at position/holding level.
- Missing or masked facts are not zero. A zero exclusion requires explicit evidence of zero or confirmation by the source/methodology.
- Use only filings whose NSE broadcast/publication timestamp is at or before the forecast timestamp. Quarter-end period and company submission date are not substitutes for public availability time.

## Calculation primitives to be tested after rights clearance

For issuer i, at the latest point-in-time IWF determination known by forecast time t:

"IWF(i,t) = round to 6 decimals of [S(i,t) - sum over unique excluded positions p of s(p,i,t)] / S(i,t)"

where S(i,t) is the correctly defined total eligible share capital, and the exclusion set contains unique, separately identifiable excluded share positions. The position set—not the list of exclusion labels—is the object that must be deduplicated.

The free-float market-cap index weight would then be:

"w(i,t) = [P(i,t) × S(i,t) × IWF(i,t)] / sum over j in the point-in-time universe [P(j,t) × S(j,t) × IWF(j,t)]"

subject to the official index methodology's market-cap price convention, share capital basis, investible-weight effective date, capping rules, divisor treatment and rounding. This expression is a mathematical design target, not a claim that all inputs or rules have been obtained.

## What the detailed XBRL candidate appears able to support

The upstream parser generically retains each explicit XBRL member name and share count and documents "dr_shares", "locked_in_shares", category totals, FDI, foreign venture-capital investor and sovereign wealth fund category candidates. It also preserves "broadcast_date" and taxonomy version.

This is potentially useful for some categories, but the code/README alone do not prove:
1. the category exists in every taxonomy vintage;
2. the category is uniquely classifiable under the IWF guideline;
3. aggregate category rows are mutually exclusive;
4. the issuer total denominator exactly matches the IWF denominator;
5. holder relationships and contractual rights are known;
6. the nested "shareholding_history/data/parsed/_categories.csv.gz" file is licensed for copying/reuse.

The upstream "LICENSE-DATA" lists particular data-file globs that do not clearly cover the nested compressed CSV in question. No XBRL data files or named-shareholder rows have been downloaded, copied or imported. The detailed candidate remains **not admitted** pending written path-specific licence confirmation and sample XBRL validation.

## Public-repository data handling

The main NIFTY-Prediction repository is currently **public**. Do not commit Dhan intraday bars, NSE/XBRL raw records, named shareholder data, or private-license data to this repository merely to satisfy a cache requirement. A public GitHub branch, artifact or Actions cache must not be treated as a private data vault. Until applicable rights are documented, retain only code, source hashes/metadata permitted by the relevant terms, and non-reconstructive aggregate QA summaries. Raw vendor data would require a separately authorised private store.

## Acceptance gates for an eventual IWF source

1. Written rights explicitly cover machine-readable acquisition, private retention/cache, model training, quantitative backtesting and internal algorithmic-trading use.
2. Every source file has a source URL/identifier, retrieved timestamp, SHA-256, schema/version and licence/terms snapshot.
3. For every IWF exclusion (1–22), there is a date-effective status: quantified share positions, evidence-backed zero, or an explicitly accepted "not separately identifiable" case under the official rule. No unlabelled gaps.
4. Every excluded share position is uniquely identified/deduplicated so it is never subtracted twice.
5. Total share denominator and DR treatment are reconciled to the official IWF example and historical published IWF/weight snapshots.
6. IWF is publication-time point-in-time safe and rounded to six decimals exactly as the guideline states.
7. Derived daily free-float market-cap weights use only membership, IWF and price/market-cap information available as of the forecast timestamp; they sum to 1 within a pre-registered tolerance.
8. A matched historical constituent basket reconstructs the official NIFTY 50 price-return move within a tolerance locked before model results are inspected, with at least 98% weight represented and at least 47 valid names.

## Current decision

- Dhan bounded intraday QA has passed in three separate 90-day windows and one session; this is not a continuous five-year history.
- The 22-exclusion mapping is now explicit, but the candidate XBRL dataset is **not legally admitted** and does not prove several relationship/agreement categories.
- The denominator distinction is a new mathematical hard check; it must be addressed before any IWF reconstruction.
- **C1 overall stays NOT PASSED / RIGHTS-BLOCKED.** Do not train C2, create a weighted aggregate forecast, or backtest a strategy with equal weights, promoter complements or estimated weights.
- No amendment to the locked BUP-01 v1.1 plan is required; this file refines the source acceptance criteria, not the scientific scope.

## References

- NSE Indices, [Guideline on calculation of IWF](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Guideline_Investible_Weight_Factors_0.pdf)
- NSE Indices, [IWF explanation page](https://www.nseindia.com/static/products-services/indices-investible-weight-factors)
- NSE Indices, [monthly reports](https://www.niftyindices.com/reports/monthly-reports)
- NSE, [Data Sharing & Usage Policy](https://www.nseindia.com/static/market-data/nse-data-policy)
- Third-party parser code and schema documentation: [yurukatsu/nse-historical-membership](https://github.com/yurukatsu/nse-historical-membership)
