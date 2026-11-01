# C1 Alternative Historical Membership and Weight Sources — Assessment

**Assessment date:** 2026-11-01  
**Track:** BUP-01 / C1 point-in-time universe and data feasibility  
**Disposition:** ALTERNATIVE ROUTES FOUND; PRIMARY WEIGHTS STILL BLOCKED; NO MODELLING AUTHORISED  
**Pre-registered plan:** v1.2 unchanged

## Executive finding

There is a credible way forward without depending on Nippon BeES historical files:

1. Use NSE Indices historical monthly weightage reports as the preferred source of actual NIFTY 50 constituent weights.
2. Use a separately licensed CC BY 4.0 point-in-time membership dataset to fill and cross-check constituent entry/exit dates, with an explicit 2018+ high-confidence core and a refresh beyond its current NIFTY 50 event history.
3. Reconstruct weekly/daily weights between valid official snapshots using price drift from Dhan, but reset on reconstitution, IWF/float changes, corporate actions, index-share changes and other official adjustments.
4. Use exchange-filed quarterly XBRL shareholding data as an independent audit/reconstruction route, not as a shortcut from aggregate promoter/FII/DII values.
5. Use multiple AMC NIFTY 50 ETF/index-fund portfolios only as a secondary cross-check or a separately labelled proxy.

The Hugging Face 20-year weights dataset is not admitted for this trading research under its published non-commercial licence unless its creator grants separate written commercial-use permission.

No alternative currently closes C1 by itself. The most promising path is official NSE Index weight snapshots plus a point-in-time membership calendar and licensed/user-entitled constituent price data.

## Source alternatives

### A1 — NSE Indices historical monthly reports (preferred primary weight source)

**Sources**
- Historical reports and archive selector: https://www.niftyindices.com/reports
- Monthly reports: https://niftyindices.com/reports/monthly-reports
- NIFTY 50 / NIFTY Next 50 report family listed by NSE: https://www.nseindia.com/all-reports

The official Historical Data page exposes “Archives of Daily/Monthly Reports”. The official monthly reports page lists “Indices Market Capitalisation & Weightage (zip)” and “Market Capitalisation, Weightage, Beta (Zip)”. NSE's All Reports archive separately lists “Market Capitalisation, Weightage, Beta for NIFTY 50 & NIFTY Next 50” and “Indices - Market Capitalisation & Weightage”. A secondary public explanation of the archive workflow reports that selecting the NIFTY 50/NIFTY Next 50 report and a month yields detailed CSVs; the broader indices report yields a PDF. Treat that as a discovery pointer, not proof of complete date coverage.

**Why it is best:** These are reports published by the index provider and intended to describe index constituents, market capitalisation and weights. They avoid substituting an ETF portfolio for the actual index basket.

**Known blockers:** The report archive's month-by-month history, exact fields, first-publication timestamps, export consistency and licensing for automated trading research still need to be verified. The current website Terms of Use prohibit systematic/automated collection without express written consent and describe use as personal/non-commercial, including restrictions on aggregation/copying. Do not add an automated crawler or commit/copy report contents until NSE Indices provides written permission or a suitable data subscription/licence.

**Bounded next test after permission:** Verify a contiguous monthly sample from 2018-04 through the latest available month, including all major index reconstitution dates and at least one corporate-action month. Record report date, actual public-availability timestamp, URL, file hash, format, row count, symbol/ISIN, weight and market-cap fields. No raw report should be committed unless the licence explicitly permits repository storage/publication.

**Decision:** PRIMARY candidate; permission and coverage gate open.

### A2 — CC BY 4.0 point-in-time NSE membership dataset (adopt for membership audit)

**Source:** https://github.com/aditya-jha/nse-historical-membership  
**Data licence:** CC BY 4.0 (LICENSE-DATA); code licence MIT. Attribution is required. Raw NSE source PDFs remain the publishers' property and are not redistributed by the project.

The repository publishes a point-in-time membership history for 42 indices. The NIFTY 50 table has membership intervals from 2014-01-01, with the README describing high confidence from 2018 onward and best-effort earlier history. Its published coverage table lists the NIFTY 50 most recent membership event as 2025-09-30; it therefore requires a current-date refresh and a C1 reconciliation. The dataset's historical weightage field is NULL for historical rows; it is a membership source, not a historical numerical weight source. The repository describes pre-2018 cardinality drift in some index histories and has separate validation gates; these caveats must be carried into our audit.

**Use:** Compare the source membership intervals to our C1 candidate, use it as an independently attributed validation layer for the 2018-04 confirmatory start, and update the membership timeline from official event publications through the latest effective date. Preserve distinct security identity/ISIN across mergers, demergers and symbol changes; do not accept ticker aliases alone.

**Decision:** ADOPT AS A MEMBERSHIP VALIDATION CANDIDATE after local reconciliation; not a weight substitute.

### A3 — NSE/BSE quarterly shareholding XBRL (free reconstruction/audit path)

**Sources**
- NSE shareholding-pattern filings: https://www.nseindia.com/companies-listing/corporate-filings-shareholding-pattern
- BSE shareholding-pattern filings: https://www.bseindia.com/corporates/Sharehold_Searchnew.aspx
- NSE XBRL methodology and IWF page: https://archives.nseindia.com/content/indices/Method_NIFTY_Equity_Indices.pdf

NSE's methodology states that IWF is determined from public shareholding disclosed in quarterly company filings and specifies 22 classes to exclude where separately identifiable (including promoter-related holdings, cross-holdings, promoter trusts/family, directors/KMP, strategic corporate holdings, government holdings, FDI, PE/VC, sovereign wealth funds, locked-in shares, IEPF and persons acting in concert).

The public repository aditya-jha/nse-historical-membership also publishes quarterly shareholding aggregates and an XBRL filing index for thousands of symbols under CC BY 4.0 for its derived outputs. Its current aggregate output/parser does not by itself implement all 22 IWF exclusions. The aggregate 100% - promoter%, or FII + DII, is not a valid IWF calculation. A detailed parser and a separately validated shareholder-category-to-IWF exclusion mapping would be required.

**Use:** Build an independent PIT estimate and cross-check against official NSE weight snapshots. Use both NSE and BSE filing metadata when available; distinguish reporting period, initial submission/broadcast timestamp and later revision timestamp. Only information published before the forecast cutoff may be used. Preserve source filing IDs, ISIN, issuer identity and taxonomy/revision version.

**Decision:** SECONDARY reconstruction/audit route; not admitted as primary weights until all exclusion classes, publication timestamps and snapshot reconciliation pass.

### A4 — Other AMC NIFTY 50 ETF / index-fund portfolios (proxy and cross-check only)

Potential direct source routes include:
- Nippon India: https://mf.nipponindiaim.com/investor-service/downloads/factsheet-portfolio-and-other-disclosures
- HDFC Mutual Fund: https://www.hdfcfund.com/statutory-disclosure/portfolio/monthly-portfolio
- UTI / other AMC monthly scheme disclosures (scheme and archive depth to be verified from each AMC).

The HDFC page currently lists NIFTY 50 ETF and NIFTY 50 Index Fund monthly portfolio workbooks. Public secondary aggregators currently expose 24 months for some HDFC/UTI NIFTY 50 ETF schemes through September 2026. This proves a possible recent cross-check route, not a licensed long historical series.

**Use:** For the same disclosure month, compare ISIN-aligned weights across several independent NIFTY 50 index funds/ETFs and to one authorised official NSE report. Quantify cash/receivable/derivative residuals, missing/extra securities, weight rank correlation, top-10 absolute differences and total absolute weight error. If any series is used without official equivalence and rights clearance, label it an ETF replication proxy only.

**Limitations:** ETF holdings may include cash, receivables, derivatives or operational residuals; fund timing and replication may differ from the exact index portfolio. Public availability alone does not grant bulk extraction, commercial research or redistribution rights.

**Decision:** CROSS-CHECK / PROXY; not primary weights.

### A5 — Hugging Face 20-year historical constituent-weight dataset (excluded pending separate licence)

**Source:** https://huggingface.co/datasets/AMP4010/Historical_Nifty_50_Constituent_Weights_20Y  
**DOI:** https://doi.org/10.6084/m9.figshare.30217915  
**Published licence:** CC BY-NC-SA 4.0.

The dataset card reports 216 dated observations, 101 columns, 100 tickers and dates 2008-01-31 through 2025-08-31, with normalized row weights summing to 100%. It describes monthly/event snapshots, static-between-observation assumptions and other reconstruction/extrapolation. Its stated licence does not permit commercial use; the author asks commercial users to negotiate a separate licence.

**Decision:** DO NOT download/use in the trading-research dataset under the present licence. May contact the creator for explicit separate written commercial-use permission. If permission is granted, it remains an exploratory comparator and still needs independent snapshot/basket validation.

### A6 — Licensed index-constituent data (last resort, or if permission is denied)

NSE Indices' data-subscription page explicitly offers ongoing and historical constituent data including company identifiers, market capitalisation, weights and prices, and lists quantitative research among its applications. It provides the contact indices@nseids.co.in for EOD index constituent data and lists Bloomberg, FactSet, IHS Markit, MSCI, Rimes and Thomson Reuters as distribution channels.

**Decision:** Ask for scope, historical depth, timestamp semantics, allowed internal trading-research and automated storage rights, and pricing only after the official report route and lawful XBRL reconstruction have been assessed. Do not purchase until free/permissioned sources have been ruled out.

## Proposed reconstruction method

For the period between two authorised monthly/official weight snapshots, a daily weight can be estimated under fixed constituents, fixed index shares and fixed IWF:

w_hat_i(t) = [w_i(t0) × P_i(t) / P_i(t0)] / sum_j [w_j(t0) × P_j(t) / P_j(t0)]

where t0 is the most recent weight snapshot known to be public by forecast time, U(t0) is the point-in-time index universe, and P_i is a consistently adjusted price series. This is a reconstruction hypothesis, not an official published daily weight.

Reset the basket when an official index change, IWF/float change, index-share/divisor change, split, bonus, rights issue, merger, demerger, spin-off, delisting or security-identity event affects a constituent. Apply the documented official index treatment. Do not connect predecessor and successor security prices without an event-aware adjustment.

At each official snapshot t1, compare estimated w_hat_i(t1-) with the newly reported w_i(t1). Report:
- weight-sum deviation and missing/extra constituents;
- per-stock absolute error, top-10 error and total absolute error;
- weight rank correlation;
- reconstructed basket return versus official NIFTY 50 price-return index;
- error by period, index review event and corporate-action class.

Use the actual report publication timestamp, not just the report's as-of month. At a forecast timestamp, select only a report already publicly available at that time. If publication time cannot be established, exclude that report from confirmatory inputs or use a pre-registered conservative availability lag.

## C1 acceptance gates for any alternative

1. **Rights:** explicit licence/permission supports automated retrieval, internal trading research, caching, derivative calculation and any planned publication.
2. **Coverage:** contiguous accepted point-in-time membership and weight snapshots from 2018-04 through the latest research cutoff; all missing months disclosed and resolved or excluded under the registered rules.
3. **Identity:** stable ISIN/security IDs, valid-from/to and explicit symbol-change/merger/demerger/corporate-action mapping.
4. **Timestamp:** source as-of date and first public availability timestamp recorded separately; all feature values known by the relevant forecast cutoff.
5. **Weight integrity:** 50 valid constituents or a justified date-specific set; weight sum reconciles to 100% within a frozen numeric tolerance; no duplicates or ticker-only joins.
6. **Coverage:** ≥98% of index weight and at least 47 valid constituents at both anchor and expiry endpoints.
7. **Basket reconciliation:** reconstructed weighted constituent return reconciles to the official NIFTY 50 price-return movement within a tolerance specified before modelling; report residual distribution, not only mean error.
8. **Independent validation:** at least two independent snapshots/source routes agree within the registered tolerance (e.g. official report vs XBRL reconstruction/ETF proxy, with proxy differences explicitly measured).
9. **Reproducibility:** raw input only where licensed; otherwise retain URL, source ID, hash, parsing version, timestamps, sanitized diagnostics and derived output only where permission permits.

Do not start C2 panel construction or model training until these gates pass. The current plan v1.2 thresholds remain unchanged.

## Recommended implementation order

1. **Immediately:** use the CC BY 4.0 membership dataset as an independent C1 membership comparator; reconcile its 2018-04 onward NIFTY 50 intervals against our current PIT data and refresh the 2025-09 onward events.
2. **In parallel, permission-first:** contact NSE Indices for written permission to use the monthly weight reports in an automated internal trading-research workflow, or request a sample/licence quote for historical EOD constituent weights.
3. **After permission:** manually inspect a small set of authorized historical monthly reports, then add a bounded CI ingestion workflow with source hashes, month coverage checks and caching.
4. **Independent audit:** extend the exchange-filed XBRL category parser to the 22 methodology exclusion buckets and compare the resulting float/IWF estimates to the official snapshots.
5. **Proxy audit:** compare HDFC/UTI/Nippon ETF and index-fund portfolios for recent months to quantify how closely each tracks the official index weights.
6. **Only if these routes fail:** evaluate licensed constituent data from NSE Indices or an authorized vendor; otherwise stop C1 and report the remaining limitation rather than inventing weights.

## Primary references

- NSE Indices historical reports: https://www.niftyindices.com/reports
- NSE Indices monthly reports: https://niftyindices.com/reports/monthly-reports
- NSE All Reports: https://www.nseindia.com/all-reports
- NSE Indices Terms of Use: https://www.niftyindices.com/terms-of-use
- NSE Indices data subscription: https://niftyindices.com/offerings/data-subscription
- NSE IWF / free-float methodology: https://archives.nseindia.com/content/indices/Method_NIFTY_Equity_Indices.pdf
- CC BY 4.0 membership dataset: https://github.com/aditya-jha/nse-historical-membership
- Exchange shareholding filings: https://www.nseindia.com/companies-listing/corporate-filings-shareholding-pattern and https://www.bseindia.com/corporates/Sharehold_Searchnew.aspx
- Restricted historical-weights candidate (excluded): https://huggingface.co/datasets/AMP4010/Historical_Nifty_50_Constituent_Weights_20Y
- HDFC AMC monthly portfolios: https://www.hdfcfund.com/statutory-disclosure/portfolio/monthly-portfolio
- User's primary NIFTY research repo: https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction
