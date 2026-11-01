# BUP-01 C1 developer gate report

**Report date:** 2026-11-01  
**Phase branch:** phase/constituent-weekly-outcomes-c1-data  
**Plan:** BUP-01 v1.3 (current method); earlier v1.1/v1.2 text below is historical audit material  
**Developer decision:** Under v1.3, C1 is **PARTIAL / CONTINUOUS-COVERAGE GATE IN PROGRESS**. No official/ETF weight comparison is required. Do not enable C2–C6 until the revised stock/index coverage and identity gates are evidenced.

## 1. Executive finding

The Dhan authentication and bounded 1-minute equity-data validation pipeline is operational. The latest protected preflight passed its final fail-closed gate and every tested constituent passed strict target-window QA in three separate 90-day windows plus one current session.

The remaining hard blocker is not a token/API outage. No available source has been admitted that provides a complete, point-in-time official NIFTY 50 IWF/constituent-weight history with rights for automated retrieval, private retention, model training/backtesting and the intended internal algorithmic-trading research use. The XBRL category candidate is technically promising but its explicit data-licence globs do not clearly cover the nested compressed category CSV, and aggregate categories do not establish all 22 IWF exclusions. The weighted constituent basket has therefore not been reconciled to the official NIFTY 50 index.

**No C2 constituent panel, C3 stock model, C4 weighted NIFTY forecast, C5 economic strategy or C6 final manuscript has been generated.** No usable bottom-up prediction or strategy is claimed.

## 2. Gate scoreboard

| Gate | Result | Evidence / limitation |
|---|---|---|
| C0 research registration and governance | PASS | Pre-registered BUP-01 v1.1; required phase files and governance checks exist |
| Current NIFTY 50 scrip master | PASS on tested date | 50/50 current symbols resolved |
| Historical membership alias resolution | PARTIAL | 79/84 ledger aliases resolve against today's security master; five not found in current master require dated historical identity proof |
| Dhan authentication / data plan | PASS | TOTP refresh on first attempt; active plan; protected live workflow status PASS_ACTIVE_EQUITIES |
| One-session 50-name intraday QA | PASS | 2026-10-29: 50/50 |
| 90-day 50-name intraday QA | PASS on three disjoint samples | 2021-11-01–2022-01-29: 50/50; 2022-10-03–2022-12-30: 50/50; 2026-06-29–2026-09-26: 50/50 |
| Continuous five-year one-minute coverage | NOT PROVEN | Three separate windows are not a continuous five-year backfill |
| 10:00 anchor / 15:15 expiry-proxy convention | PASS on sampled rows | Latest candle at 15:00–15:14; all late bars excluded; 15:14 used in examples |
| SHREECEM 2021 edge QA | PASS after scope correction | Only negative-volume row was 2021-12-30 15:29 IST, beyond the pre-registered 15:15 cutoff; reported separately; target scope remains strict |
| Historical ISIN/security-ID and corporate actions | PARTIAL / OPEN | Symbol ledger exists but full dated stable-ID history and corporate-action continuity not independently complete |
| Official point-in-time IWF/weights with intended-use rights | BLOCKED | Official monthly ZIP family identified; written permission/licence for automation, caching and trading-research use not obtained |
| 22 IWF exclusion evidence | PARTIAL / OPEN | Machine-readable matrix created; multiple relationship/contract categories are not provable from category aggregates alone |
| IWF mathematical implementation harness | PASS | Official NSE example reproduced as 0.608794; duplicate share-position deduction rejected; seven new tests included |
| Weighted basket-to-index reconciliation | NOT RUN | Requires authorised complete weights/IWF and identity/corporate-action mapping first |
| C2–C6 | GATED | No modelling or strategy work without C1 acceptance |

## 3. Key Actions runs

- Protected Dhan preflight, final status PASS: [41266897788](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266897788).
- Baseline regression suite before IWF arithmetic tests: [41266922851](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266922851), 43 passed.
- Corrected full offline suite including IWF tests: [41269516064](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41269516064), 50 passed.
- Pull-request validation of the same full suite: [41269519499](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41269519499), 50 passed.
- C1 authorised-source audit workflow: [41269430549](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41269430549), successful.

The offline regression workflow initially omitted the newly added IWF test module despite its path filter. This was recorded as E0049, corrected in commit 12d997bf51c12a5780abcd6a9836d69853327bd0, and verified by the 50-test runs above.

## 4. Methodological controls and outstanding risks

### 4.1 IWF denominator and double counting

The official NSE IWF guideline's worked example uses:

IWF = (Total Shares - sum of separately identified excluded shares) / Total Shares

and rounds the result to six decimals. The third-party XBRL parser also reports shareholding percentages on an A+B+C2 base (total less C1/DR shares). That percentage base must not be substituted for the IWF denominator. Reconstruct from absolute share counts and reconcile the correct full share-capital base and DR treatment to official historical files.

A single holding may satisfy more than one exclusion description (e.g. promoter-related and DR-related). Deduplicate holding positions before subtracting. Never sum 22 overlapping category aggregates blindly.

### 4.2 Category mapping

The matrix in C1_IWF_EXCLUSION_MAPPING.csv covers all 22 official IWF exclusions. Promoter, government, FDI, FVCI, SWF, IEPF and locked-in data have plausible category-level candidates; promoter family, group/associate ownership, director/KMP roles, board nomination rights, right-of-first-refusal, strategic purpose and PAC status require dated relationship or contractual evidence. These statuses are candidates only until actual authorised XBRL rows and official weights are audited.

### 4.3 Data rights and storage

The upstream detailed shareholding candidate's LICENSE-DATA globs do not unambiguously include the nested parsed compressed CSV. Do not copy or import that file without written path-specific licence confirmation. Its named-shareholder file is excluded from scope.

The NIFTY-Prediction repository is public. Do not commit raw Dhan minute bars, NSE/XBRL source rows, named shareholder records or private-license datasets to public branches, workflow artifacts or public Actions caches. The user's preference for repo caching does not override source terms. A separately authorised private store is required for raw restricted data.

## 5. Required next developer actions

1. Obtain a written NSE Indices/NSE Data agreement (or equivalent explicit permission) covering historical NIFTY 50 constituent weights/IWF, machine retrieval, private cache retention, model training, quantitative backtesting, own-capital algorithmic-trading research and the permitted publication of non-reconstructive derived outputs.
2. If the XBRL category dataset is proposed instead, obtain an explicit licence statement covering the exact nested path shareholding_history/data/parsed/_categories.csv.gz; validate representative filings from every taxonomy generation; and complete the 22-exclusion mapping with overlap resolution and date-effective evidence.
3. Arrange an access-controlled private data store before any raw Dhan/NSE/XBRL data is retained. Public repo should keep only code, permitted provenance/hashes and non-reconstructive QA reports.
4. Complete the continuous weekly-cycle one-minute data coverage across the intended confirmatory history in bounded <=90-day chunks, with dated historical security ID/ISIN/symbol mapping and corporate-action continuity. Preserve source-native values and QA.
5. Reconstruct daily free-float weights using the latest authorised IWF known at each 10:00 forecast timestamp and dated prices/share capital. Confirm official methodology, capping, rounding and divisor treatment.
6. Reconcile weighted constituent basket return to the official NIFTY 50 price-return move on matched cycles. Enforce at least 98% point-in-time weight and at least 47 valid names. Lock the numerical tolerance before model results are viewed.
7. Only after all gates above pass, move to C2 and follow the locked walk-forward, untouched holdout and uncertainty plan.

## 6. Repository integrity review

At handoff:
- Main README contains the latest C1 data result, remaining rights gate and links to phase files.
- C1 STATUS.md records current gate outcomes; C1 RESEARCH_PLAN.md remains version 1.1 and unchanged.
- RESEARCH_LOG.md and CONVERSATION_LOG.md record visible research actions/results; hidden reasoning and secrets are not stored.
- ERROR_LOG.md records E0049 as closed and E0050 as an open denominator/source-reconciliation risk.
- The IWF matrix, mathematical audit, code helper, unit tests and offline workflow changes are committed on the C1 phase branch.
- The source-audit and offline workflows passed; the protected Dhan run passed its final fail-closed check.
- No raw market data or unlicensed shareholding records were imported during this continuation.

## 7. Final C1 decision

**C1 is not accepted.** The market-data acquisition component passed on the bounded Dhan samples, and the IWF arithmetic harness is tested, but source rights, complete exclusion evidence, continuous historical coverage, stable historical identity and weighted basket reconstruction are unresolved. The next gating event is a documented data-rights resolution and secure data-access/storage arrangement—not another unbounded search or model-training attempt.

BUP-01 v1.1 remains locked. C2–C6 remain pending. No trading recommendation is implied.



## Addendum — public ETF-replica weight path (2026-11-01; supersedes rights-only next step)

User direction is to proceed with available public web sources and not wait for a separate NSE permission request before doing exploratory work. The data-source strategy has therefore been broadened without changing the official-weight confirmatory standard.

### New evidence

- Nippon India ETF Nifty 50 BeES publicly discloses a portfolio intended to replicate NIFTY 50 constituent weights.
- February 2026 AMC portfolio (28-Feb-2026 portfolio; NAV date 27-Feb-2026) has 50 equity constituents plus 0.08% cash.
- Compared with NSE Indices' official white-paper weight snapshot dated 2026-02-27: 50/50 constituents matched; equity-only normalized MAE 0.002214 percentage points; RMSE 0.003204 pp; max absolute difference 0.008967 pp; Pearson correlation 0.99999895.
- This is one-date calibration evidence only. The underlying official and ETF inputs are rounded to 0.01 pp, and a single observation cannot validate a multi-year historical proxy.

### Method and guardrails

- Plan amended to v1.2: a separate exploratory ETF-replica proxy track is now permitted.
- The new utility implements equity-only normalization, fixed-share price drift and normalized cross-source comparison. Drift is valid only on unchanged membership/share-capital/IWF/corporate-action intervals.
- A published holdings snapshot cannot be used before its actual publication time. Where actual timestamp cannot be verified, period-end +15 calendar days is explicitly imputed for exploratory analysis, with +10/+20 day sensitivities. SEBI's post-16-Mar-2025 rule is quarterly disclosure within 10 days after quarter; it does not support assuming monthly disclosure automatically.
- At each NIFTY reconstitution, IWF/float change, share-capital event or corporate action, reseed from dated evidence or exclude affected cycles. Keep minimum 98% weight and 47 valid-name thresholds.
- The AMC holdings are proxy weights, never "official weights" or official IWF. Official, ETF and reconstructed weights remain separately stored/reported.
- Raw market bars and individual shareholder details are not committed to this public repository.

### Updated gate status

C1 remains **PARTIAL / NOT YET ACCEPTED**. The proxy source passes a one-date calibration test, but the historical full holdings series, actual publication timestamps, historical constituent identity/corporate-action reseeding and weighted basket-to-index reconstruction are still outstanding. C2 model training has not started. No bottom-up prediction, strategy or full manuscript is claimed.

### New artifacts

- [ETF proxy calibration and data rules](C1_ETF_PROXY_CALIBRATION.md)
- [Aggregate calibration metrics](../../data/constituent_weekly/etf_proxy_calibration_2026-02-27.csv)
- [Weight-proxy utilities](../../scripts/constituent_weekly/weight_proxy.py)
- [Eight regression tests](../../tests/test_constituent_weekly_weight_proxy.py)
- [Plan v1.2](RESEARCH_PLAN.md)


## Addendum — recent Nippon AMC source-schema validation (2026-11-01)

### Passed evidence
- The AMC primary monthly portfolio archive exposes a recent Nifty BeES portfolio workbook.
- September 2026 and February 2026 direct workbooks both returned HTTP 200. Although URLs end in .xls, file signatures identify XLSX containers; the probe reads them with the correct engine.
- Target scheme was located in both workbooks. ISIN, quantity and portfolio-weight headers were detected; each scheme section contained 50 ISIN-bearing rows.
- Seven offline regression tests passed. The metadata-only results, byte sizes and SHA-256 hashes are recorded in [C1_AMC_ARCHIVE_PROBE_REPORT.md](C1_AMC_ARCHIVE_PROBE_REPORT.md), linked to Actions run [41275178244](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41275178244).

### Still blocked
- The April 2019 archive item is visible, but the guessed modern-format download URL returned 404. Its correct historical direct link remains unresolved.
- The actual publication timestamps for each portfolio month have not been independently established.
- AMC site/data terms do not yet affirmatively establish automated extraction and trading-research use rights. AMFI composite data remain excluded absent separate clearance.
- No historical holdings series has yet been reconstructed, no point-in-time weight coverage has been measured, and no weighted basket-to-index reconciliation has run.

### Gate disposition
This raises source feasibility from discovery-only to **recent-schema PASS**, but does not pass C1 overall. C1 is **PARTIAL / NOT ACCEPTED FOR MODELLING**; C2–C6 remain gated. Do not present these holdings as official NIFTY IWF or as a validated historical proxy series.



## Superseding developer addendum — BUP-01 plan v1.3 (2026-11-01)

This addendum supersedes the earlier weight-rights recommendations and the v1.2 ETF proxy exploration as **active requirements**. The older material above is preserved as the dated historical C1 audit trail only.

### User-directed method

The user said: “No comparison needed. Proceed.” BUP-01 v1.3 removes official free-float/IWF weights, ETF holdings, weight reconstruction and weighted basket-to-index reconciliation from its active method. It uses point-in-time stock forecasts and strictly out-of-fold cycle summaries (unweighted predicted breadth, mean/median probabilities and returns, dispersion, sector breadth, concentration and member coverage) to predict the observed NIFTY 50 10:00-to-15:15-proxy direction label. Equal-weight stock averages are diagnostics only and are never presented as the actual index return.

### Revised gate scoreboard

| Gate | Result | Evidence / limitation |
|---|---|---|
| C0 governance / registered protocol | PASS; v1.3 amendment committed | Plan, plan validator and unit tests updated |
| PIT membership / effective-date ledger | PASS WITH LIMITATIONS | CC BY 4.0 membership subset; 103 month-end reconciliations; source confidence and symbol/action caveats retained |
| Current active NIFTY 50 security-master resolution | PASS on checked date | 50/50 current constituents resolved in prior protected Dhan run |
| Bounded stock candle coverage | PASS on separate samples only | Three 90-day samples across 2021/2022/2026 and recent single-day universe checks; not continuous five-year coverage |
| Continuous stock and NIFTY intraday coverage | NOT YET PROVEN | Need <=90-day chunks across the intended confirmatory period and explicit gap accounting |
| Historical ISIN/security-ID and corporate actions | PARTIAL / OPEN | HDFC legacy ID passed selected dates; dated TATAMOTORS/TMPV action and all interval mappings must remain explicit |
| Expiry calendar and index target | PARTIAL / OPEN | Need a verified actual-expiry/session list and same 10:00/15:15-proxy NIFTY index target observations |
| C1 acceptance | NOT PASSED | >=47 and >=94% valid constituents per accepted cycle; >=98% scheduled cycles with valid observed NIFTY targets; continuous window and identity gates |
| C2 panel / C3 models / C4 meta-model | PENDING | Must remain gated until C1 passes; no model/forecast exists |
| C5 trading economics | PENDING | Paytm Money brokerage, taxes/levies, spread, slippage, lots and fills still required |
| C6 manuscript / independent audit | PENDING | Must include complete manuscript, figures, tables, appendices, supplements and independent error audit |

### Retired data path and rights control

The historic ETF/IWF files and reports remain only as audit history; they are not active inputs and must not be refreshed or compared. The Nippon AMC bulk-workbook automation is paused because its terms restrict aggregation/copying and require prior written permission for reuse of proprietary content. No holdings values were admitted. mfdata.in returned HTTP 522 on three discovery routes; that is inconclusive and does not block the v1.3 no-weight design.

### Next bounded developer action

Implement and test a rate-limited, cache-aware Dhan <=90-day chunk coverage runner for the point-in-time stock universe **and the NIFTY index target**, with separate source IDs, security identity/action manifests, missing-session diagnostics and sanitized output only. Validate a manageable date slice and request-count/runtime guards first, then continue across the registered confirmatory window without repeated token-generation loops. No C2 fitting until the C1 coverage panel and target calendar are accepted.


## Developer addendum — dated symbol identity correction (2026-11-01)

- Found that project membership rows use canonical symbol LTM for the 2023-07-13 to 2024-09-30 LTIMindtree interval. Exchange records show actual ticker LTIM throughout that interval, with LTIM→LTM effective 2026-02-27; the company entered NIFTY 50 on 2023-07-13 and exited effective 2024-09-30. The C2 identity resolver correctly returns LTIM for the membership interval and resolves it to the current LTM security identity.
- Added point-in-time mapping rows for ZOMATO→ETERNAL, TATAGLOBAL→TATACONSUM, and TATAMOTORS→TMPV, plus major issuer-event rules. HDFC Ltd remains separate from HDFCBANK. DUMMYTATAM remains excluded.
- Offline tests now cover point-in-time symbol resolution and event dates.
- **Gate:** identity mapping is improved but remains PARTIAL; the new ledger does not replace the exhaustive corporate-action/adjusted-return review. C1 is not passed; C2 remains pending.


## Developer gate addendum — 2026-11-01 intraday target coverage

The live Dhan audit [41301447865](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41301447865) printed C1_CONTINUOUS_COVERAGE_GATE_PASSED:
- 258 scheduled expiry cycles; 258 valid observed NIFTY anchor/expiry target pairs.
- 258 cycles met the at least 47 and at least 94% point-in-time constituent input rule.
- 154 confirmatory cycles remain after the 104-cycle warm-up.
- Zero unresolved active symbols; 1,083 Dhan requests across 21 windows.
- One index chunk (2024-01-31 to 2024-04-29) was marked PARTIAL_TARGET_DATES, while cycle-level count remained 258/258. The date-level flag was not retained due publication conflict.

**Gate scope:** intraday target coverage sub-gate PASS. C1 overall remains NOT PASSED: daily feature history and exhaustive action-adjusted return validation remain open. C2 remains PENDING.


## Corrected developer gate addendum — full intraday QA artifact inspected (2026-11-01)

The later full artifact from [run 41309632317](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41309632317), artifact 13086220727, is the authoritative current intraday evidence: 258/258 weekly expiry cycles pass NIFTY anchor/expiry target validation; 258/258 cycles meet the 47-stock / 94% constituent-input rule; 154 confirmatory cycles remain after 104 prior accepted cycles; minimum member coverage is 98%; zero unresolved active symbols; 1,083 requests across 21 windows.

The only window-level partial is the extra 15:14 check on 2024-04-26. The 10:00 anchor on that date passes; the date was not a weekly expiry. The cycle's actual expiry proxy on 2024-05-02 passes. The earlier 77/258 result is retained as an earlier incomplete run and is superseded by this full artifact.

**Remaining C1 gates:** the daily first-pass result has 98.85% OHLCV member-session coverage, but the legacy HDFC daily series and one TATAMOTORS member session remain unresolved before the corrected personal-use fallback; exhaustive corporate-action/adjusted-return review is also open. Overall C1 NOT PASSED; C2 PENDING.
