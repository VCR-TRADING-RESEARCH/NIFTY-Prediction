# C1 primary AMC monthly-disclosure archive audit

**Audit date:** 2026-11-01  
**Decision:** SOURCE FOUND; METADATA PROBE PENDING; RIGHTS/POINT-IN-TIME GATES NOT PASSED

## Research question

Can Nippon India AMC's own historical monthly portfolio disclosures provide a dated holdings series for Nippon India ETF Nifty 50 BeES, for a separately labelled ETF-replica weight proxy without substituting ETF holdings for official NIFTY 50 IWF?

## Primary-source discovery

The Nippon India Mutual Fund disclosure page lists monthly portfolio files and exposes direct download links. Current listings run through September 2026, and older monthly portfolios extend into 2018/2019. The February 2026 workbook linked by the AMC page resolves to:

https://mf.nipponindiaim.com/InvestorServices/FactsheetsDocuments/NIMF-MONTHLY-PORTFOLIO-28-Feb-26.xls

Archive index: https://mf.nipponindiaim.com/investor-service/downloads/factsheet-portfolio-and-other-disclosures

AMFI's separate monthly archive exposes PDF and Excel reports from April 2018. Its terms grant a personal, non-transferable, non-sublicensable, limited and revocable right for personal non-commercial use only. As this research supports trading, AMFI-hosted files are not admitted to automated bulk extraction, reuse, caching or publication without separate rights clearance.

The AMC page is a distinct primary publication route. The AMC disclaimer/privacy page reviewed did not establish an affirmative licence for bulk extraction or redistribution. Public availability is not treated as a blanket data licence.

## Independent discovery / cross-check sources

- FundTracker India reports 90 monthly Nifty BeES portfolio observations from April 2019 through September 2026, sourced from AMC monthly disclosures. This is a secondary completeness check, not primary model input or an independently licensed download.
- DecryptMutualFunds indexes 24 months and is a secondary check only.
- amcs.fund documents use of AMC-origin disclosures and says month-level records link to fund-house files and Internet Archive copies. Its API is a discovery/reconciliation candidate until schema, source-file lineage, use terms and historical publication timing are verified.

## Not yet established

- Complete direct-AMC file list and successful download coverage.
- Stable workbook layout for scheme, ISIN, quantity, market value and percentage of NAV.
- Actual publication timestamps (portfolio month-end is not a publication timestamp).
- Historical scheme/security continuity and corporate-action adjustments.
- Permission for automated extraction and internal trading-research use.
- Historical basket reconstruction against the official index.

## BUP-01 gate decision

A metadata-only probe checks September 2026, February 2026 (the existing official-weight calibration month), and April 2019 where available. It reports URLs, HTTP status, bytes, SHA-256, sheet count, generic header detection and ISIN-row count only. It does not print or commit constituent names, security IDs, quantities, market values, weights or raw workbook rows; no raw-file cache or artifact is created.

The one-date ETF/NSE calibration remains calibration only. Plan v1.2 is unchanged. C1 remains **PARTIAL / NOT ACCEPTED FOR MODELLING** pending source-use rights, point-in-time availability, membership/security-action alignment, 98% weight coverage, at least 47 constituents and frozen weighted basket-to-index reconciliation.

## Source links

- [Nippon India AMC disclosure archive](https://mf.nipponindiaim.com/investor-service/downloads/factsheet-portfolio-and-other-disclosures)
- [AMFI Monthly archive](https://www.amfiindia.com/research-information/amfi-monthly)
- [AMFI terms of use](https://www.amfiindia.com/terms-of-use)
- [FundTracker India Nifty BeES history](https://fundtrackerindia.com/scheme/nippon-india-etf-nifty-50-bees)
- [amcs.fund method and source description](https://amcs.fund/month)


## Metadata probe outcome — 2026-11-01

The bounded probe passed on the two required recent dates:
- September 2026: HTTP 200; 1,352,141 bytes; XLSX ZIP signature; 108 sheets; target scheme found; ISIN, quantity and weight columns detected; 50 ISIN-bearing target rows.
- February 2026: HTTP 200; 1,206,358 bytes; XLSX ZIP signature; 111 sheets; target scheme found; ISIN, quantity and weight columns detected; 50 ISIN-bearing target rows.
- Offline parser tests: 7 passed. See [sanitised probe report](C1_AMC_ARCHIVE_PROBE_REPORT.md) and [Actions run 41275178244](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41275178244).

The direct URL candidate for April 2019 returned HTTP 404. The AMC archive page does show a portfolio entry for that month; the modern filename pattern was not confirmed for older years. This is a link-discovery issue, not evidence of source absence. The April file has not been replaced with an inferred or third-party record.

**Interpretation:** Recent source schema is verified, not the full historical series. No individual holding values or raw workbook files have been committed. Publication-time availability, use rights, historical security identity/actions, weight coverage and weighted basket reconciliation remain open. C1 stays PARTIAL / NOT ACCEPTED FOR MODELLING.
