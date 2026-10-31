# C1 Source Feasibility Audit — BUP-01

**Date:** 2026-10-31  
**Branch:** phase/constituent-weekly-outcomes-c1-data  
**Status:** IN PROGRESS — source discovery completed, empirical weight/price validation not yet passed.

## 1. Executive finding

There is a credible official route for constituent weight data: NSE Indices publishes monthly report categories including “Indices Market Capitalisation & Weightage” and “Market Capitalisation, Weightage, Beta”. The NSE India all-reports archive also lists “Market Capitalisation, Weightage, Beta for NIFTY 50 & NIFTY Next 50”, equity UDiFF bhavcopies and other historical reports. The actual monthly ZIP payload has not yet been retrieved or parsed in this runtime. This is a **network retrieval limitation in this run**, not a finding that the source is unavailable.

Official sources:
- NSE Indices monthly reports: https://niftyindices.com/reports/monthly-reports
- NSE India all reports: https://www.nseindia.com/all-reports
- NSE NIFTY 50 page/methodology: https://www.nseindia.com/static/products-services/indices-nifty50-index
- NSE IWF: https://www.nseindia.com/static/products-services/indices-investible-weight-factors
- Dhan v2 historical data: https://dhanhq.co/docs/v2/historical-data/

The next automated task is to download the latest available official monthly ZIP from GitHub Actions, inventory the archive contents, record file hashes and identify the actual data schema. This first sample will not by itself establish historical point-in-time weights back to 2019.

## 2. Source-by-source status

| Data requirement | Preferred source | What is confirmed | What remains unverified | C1 status |
|---|---|---|---|---|
| NIFTY 50 methodology | NSE Indices | NSE describes NIFTY 50 as a 50-stock index and says free-float methodology applies from 26-Jun-2009 | Full historical constituent/weight observations and publication timestamp per report | PARTIAL |
| Historical weight reports | NSE Indices monthly reports | Official page lists “Indices Market Capitalisation & Weightage (zip)” and “Market Capitalisation, Weightage, Beta (Zip)” | Archive coverage, report dates, raw ZIP schema, complete NIFTY50 stock columns, weight precision, availability date | PENDING_DOWNLOAD |
| Historical daily index/stock reports | NSE India all-reports | Official archive lists historical index data, security-wise price/volume, daily and monthly equity/indices reports, UDiFF bhavcopy category | Exact downloadable coverage, raw schema and timestamp semantics need automated tests | PARTIAL |
| Point-in-time membership | Original NSE Indices press releases and NSE circulars | Official pages link index reconstitution/calendar resources | Full change ledger, effective date vs announcement date, stable ISIN/security-ID links and missing circulars | PENDING |
| Third-party historical membership reconstruction | BKKB20/nse-index-history | Public project supplies reconstruction scripts and current-member CSV; README describes 2004–2026 coverage | Original circular audit, parser correctness, effective-date semantics, alias/ISIN integrity | DIAGNOSTIC_ONLY |
| Independent binary membership cross-check | vishalvx/nifty-indices-datasets | README describes monthly binary membership from 2008 onward | It does not provide numeric free-float weights and discloses reconstructed/approximate data | NOT_WEIGHT_SOURCE |
| Stock intraday prices | DhanHQ v2; official/free archives first | Current Dhan documentation describes 1-minute history up to five years for active instruments and max 90-day request windows | Whether subscription/auth works; security-ID coverage for historical inactive/removed stocks; actual bar quality and adjustment semantics | PENDING_API_TEST |
| Stock daily prices | NSE equity archive / Dhan daily history | Dhan docs state daily history from instrument inception; NSE publishes security price/volume archives | Full point-in-time adjusted/unadjusted definitions, old/delisted security continuity, corporate actions | PENDING |
| Options/flows/global/news | NSE reports and public historical sources | Source categories exist | Timestamped historical archive, rights, completeness and point-in-time availability | OPTIONAL_PENDING |

## 3. Official monthly weight archive: discovered link, payload retrieval blocked in this runtime

The NSE Indices Monthly Reports page lists the two monthly ZIP report families above. The web page exposes the “Market Capitalisation, Weightage, Beta” report as an official download. A latest observed link in the page extract was:
https://niftyindices.com/Market_Capitalisation_Weightage_Beta_for_NIFTY_50_And_NIFTY_Next_50/mcwb_jul26.zip

A second report family uses the “Indices - Market Capitalisation and Weightage” archive. The direct ZIP fetch from this chat/container runtime failed, and the browser viewer rejects ZIP content as unsupported. No ZIP contents, row counts or exact period are claimed at this point. The GitHub Actions runner will retry from the official page and save the downloaded archive as a workflow artifact plus a compact manifest, without committing raw data until redistribution and size restrictions are checked.

The monthly report is a snapshot, not automatically the precise weight known at every weekly 10:00 forecast. Report period and report publication timestamp must be tracked separately. A report published after a forecast cannot be used as if known before that forecast.

## 4. Third-party weight dataset investigated but not accepted as primary

The Hugging Face dataset AMP4010/Historical_Nifty_50_Constituent_Weights_20Y has a public data card that describes 216 observations and 100 ticker columns from 2008-01-31 to 2025-08-31. The card states that it is derived from NSE Indices monthly reports, but also says:
- Some missing/event weights are estimated or extrapolated.
- Weight observations may be treated as static between snapshots.
- Rows are normalised to 100%.
- The dataset uses a CC-BY-NC-SA 4.0 non-commercial licence.

Decision: do not use it as a primary numerical weight series for this research or any commercial strategy workflow. It may only be used as a non-commercial diagnostic/cross-check if terms are compatible and attribution/share-alike requirements are respected. No raw download was successfully obtained in this run. The data card is useful for source discovery, but not sufficient evidence of exact daily point-in-time weights.

## 5. Daily weight reconstruction hypothesis — not yet accepted

If an official point-in-time snapshot at time t0 provides weights w[i,t0], and constituent membership, index shares and IWF are unchanged between t0 and t, a mechanically implied daily weight estimate is:

w[i,t] = (w[i,t0] * P[i,t] / P[i,t0]) / sum_j(w[j,t0] * P[j,t] / P[j,t0])

This is an algebraic drift of free-float market-cap weights under fixed shares/IWF and universe. It is not a substitute for official weights when there is a constituent rebalance, IWF change, split/bonus/rights issue, merger/demerger, spin-off, divisor/index-share change or other corporate action. Such events must reset or invalidate the reconstruction until the official index treatment is replayed.

Acceptance tests before using this estimate:
1. Snapshot publication time precedes the forecast timestamp.
2. Every security is matched by stable ISIN/security ID and effective-date mapping, not ticker-only alias.
3. Daily prices use the correct corporate-action basis relative to the snapshot date.
4. Membership, index shares and IWF changes are applied on the exact effective dates.
5. Reconstructed weights sum to 100% within tolerance without hiding missing constituents.
6. Reconstructed weights are compared against the next official snapshot, reporting per-security absolute error, top-weight error and total absolute deviation.
7. The realised weighted constituent basket is compared with official NIFTY price-return index movement on the same windows.
8. A maximum reconstruction error/tolerance is frozen before any predictive model or holdout results are inspected.

Until those tests pass, the estimate is an exploratory diagnostic only and C1 remains BLOCKED.

## 6. Historical membership reconstruction audit findings

The candidate BKKB20/nse-index-history project may speed up circular discovery, but its README discloses three unprocessed scanned circular PDFs from 2018–2019 and pre-2010 mapping limitations. Code inspection shows:
- The database stores membership snapshots keyed by date and ticker, plus parsed circulars/audit warnings; the inspected schema does not contain numerical free-float weights.
- The query script uses a local hard-coded Windows base path, so it is not an immediately portable pipeline.
- The inspected query script keys reconstructed snapshots using the parsed circular record date. The source must be checked to prove this date is the index-effective date, not announcement/publication date.
- Its alias maps collapse some corporate-action predecessors and successors to one ticker (for example HDFC/HDFCBANK, MINDTREE/LTIM and PVR/PVRINOX). Such collapsing can incorrectly rewrite historical security identity. It is not acceptable for this study without ISIN/effective-date reconstruction and event-level audit.
- Its current-member file lists 50 rows, but the README describes the current list as March 2026. That file is not a verified constituent snapshot for 31-Oct-2026 and does not validate historical membership.

The second vishalvx dataset is explicitly binary membership. It is a secondary membership cross-check only, not a weight source.

## 7. Data coverage implications

Dhan v2 currently documents 1-minute candles for the last five years for active instruments and says a maximum 90 days can be requested per intraday call. Its daily endpoint is documented from instrument inception. This means:
- Minute-price tests may be feasible for active constituents across approximately the last five years, subject to actual entitlement/security-ID coverage.
- Historical constituents that have since been removed, merged, renamed or delisted are a separate critical coverage problem; the “active instruments” qualifier must not be ignored.
- For older minute observations, test official/free NSE and independent public archives first. Dhan does not prove five-year minute access for all historical securities.
- Requests should be cached by stable security ID, timeframe, date window and source schema. Do not download the same immutable history repeatedly.
- The C1 automated workflow will start with the official current weight report sample; full historical archive coverage and old security intraday coverage remain explicit open items.

## 8. C1 acceptance decision

**Current gate: BLOCKED / IN PROGRESS.**

Passed: official source families are identified; a plausible monthly all-constituent report exists; membership reconstruction candidates were reviewed; Dhan's current history-window constraints are documented.

Not passed: no official monthly ZIP payload has been parsed; historical point-in-time membership is not certified; numerical weights are not yet reconciled; no daily weight reconstruction has passed; no stock intraday coverage or inactive-security test has completed; no weighted constituent basket has been reconciled to official NIFTY.

**Next action:** automated official report retrieval and schema audit, then exact historical membership/security mapping and a Dhan/free-source spot-price coverage audit. No stock model training is authorised before the C1 acceptance gates in RESEARCH_PLAN.md pass.
