# C1 primary AMC monthly-disclosure archive audit

**Audit date:** 2026-11-01  
**Decision:** OFFICIAL ARCHIVE INDEX VERIFIED TO 2012-09; RECENT WORKBOOK SCHEMA PASSED; LEGACY URL/RIGHTS/POINT-IN-TIME GATES NOT PASSED

## Research question

Can Nippon India AMC's own historical monthly portfolio disclosures provide a dated holdings series for Nippon India ETF Nifty 50 BeES, for a separately labelled ETF-replica weight proxy without substituting ETF holdings for official NIFTY 50 IWF?

## Primary-source discovery

The Nippon India Mutual Fund disclosure page lists monthly portfolio files and exposes direct download links. Current listings run through September 2026, and the rendered archive index includes month-end portfolio entries from September 2012 through the currently listed 2026 archive, including April 2019. Listing coverage does not prove every file resolves or every month is complete. The February 2026 workbook linked by the AMC page resolves to:

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


## Additional historical archive and API discovery — 2026-11-01

- A second read of the official Nippon archive page shows month-end portfolio entries extending back to **September 2013**, not merely 2018/2019. The visible page includes a continuous monthly list across the 2019 and 2018 archive and older entries. This confirms an archive index, not that every legacy download link resolves or that each workbook remains available.
- The official archive page explicitly lists “Monthly portfolio for the month end 30th April 2019”; the guessed contemporary filename returned 404. The older entry likely uses a different attachment path. No values are inferred.
- New independent discovery route: [amcs.fund Method & sources](https://amcs.fund/methodology) states that its monthly portfolio explorer fetches each fund house's own Excel/ZIP source files, parses ISIN-bearing rows including quantity, market value and percentage to net assets, takes the disclosure month from the date printed inside the file, and links each month to the fund-house source file plus an Internet Archive copy. It also publishes a public API base at https://amcs.fund/api/v1 with /amcs, /manifest, /scheme/{id} and /month/{id} endpoints.
- This API is now a **bounded discovery/reconciliation candidate** for recovering the exact historical Nippon attachment URLs and checking monthly source coverage. The JSON API endpoint payload/schema was not retrieved by this probe, no holdings were imported, and the platform's data-reuse licence/terms have not been independently established.
- Source links: [Nippon AMC archive](https://mf.nipponindiaim.com/investor-service/downloads/factsheet-portfolio-and-other-disclosures), [amcs.fund methodology](https://amcs.fund/methodology), [amcs.fund API index](https://amcs.fund/api/v1).

**Gate impact:** This improves confidence that historical source documents are indexed and suggests a route to exact legacy source URLs. It does not prove historical file retrieval, publication timestamps, rights, point-in-time security identity, weight coverage or index-basket reconciliation. C1 remains PARTIAL / NOT ACCEPTED FOR MODELLING.


## Official archive lower bound corrected and API metadata probe added — 2026-11-01

- The rendered official Nippon archive lists monthly portfolio entries as early as **30 September 2012** (archive page lines 555–561), correcting the earlier under-report of September 2013. April 2019 remains explicitly listed. This is an index-level observation only; file-by-file availability and continuity remain unverified.
- [amcs.fund methodology](https://amcs.fund/methodology) states that its pipeline reads AMC-origin Excel/ZIP disclosures, uses the date printed inside each disclosure for the month, and links each monthly record to the original fund-house file and an Internet Archive copy. The published [API index](https://amcs.fund/api/v1) returns the advertised route list, including `/amcs` and `/manifest`.
- A new metadata-only API probe and manual/push GitHub Actions workflow have been committed: [probe script](../../scripts/constituent_weekly/probe_amcs_fund_metadata.py), [workflow](../../.github/workflows/bup01-c1-amcs-metadata-discovery.yml), [offline sanitisation tests](../../tests/test_amcs_fund_metadata.py). It requests only API index/AMC/manifest metadata, does not request a scheme holdings endpoint, and performs HEAD-only checks on whitelisted AMC/Internet Archive file URLs. Its result report will be [C1_AMCS_API_DISCOVERY_REPORT.md](C1_AMCS_API_DISCOVERY_REPORT.md).
- The probe has not yet been independently observed completing in Actions at the time of this audit update. No API JSON records or source-file URLs are claimed as retrieved. Any API-origin holdings remain excluded until reuse rights are established.
- The research browser can read the API index but cannot retrieve the `/amcs` or `/manifest` JSON endpoints directly; CI is the bounded next check. The external API's commercial/trading-research licence remains unverified.

**Gate impact:** Historical archive depth is better evidenced, but C1 remains **PARTIAL / NOT ACCEPTED FOR MODELLING**. Do not train or import third-party holdings until source rights, exact source-file lineage, publication/availability timestamps, point-in-time holdings/security identity, 98% weight coverage, 47-stock minimum and basket-to-index reconciliation all pass.

## amcs.fund metadata probe result — 2026-11-01

- Automated run [41277022940](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41277022940) completed **SUCCESS**. All four metadata-sanitisation tests passed, the API probe ran, and the sanitized report was committed.
- API index, /amcs, Nippon AMC detail and /manifest all returned HTTP 200 with valid JSON. The AMC listing resolved to nippon-india; AMC detail listed Nifty BeES schemes for the current September 2026 period.
- The manifest did **not** yield a whitelisted original-AMC or Internet Archive URL for a historical Nippon Nifty BeES monthly file. No HEAD source-link checks were available to run. The report is [C1_AMCS_API_DISCOVERY_REPORT.md](C1_AMCS_API_DISCOVERY_REPORT.md).
- No scheme-level holdings endpoint was requested. No constituent holdings, ISINs, quantities, market values, weights or source workbook bytes were downloaded.
- The API endpoint reachability is now established, but its data-reuse licence remains unverified and the exact April 2019 AMC attachment is still unresolved. Do not treat current scheme metadata as historical holdings evidence.

**Gate impact:** Discovery route partially validated (API metadata reachable); it did not resolve historical file URLs. C1 remains **PARTIAL / NOT ACCEPTED FOR MODELLING**.
