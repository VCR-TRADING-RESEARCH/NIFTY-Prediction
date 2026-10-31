# BUP-01 Research Status

**Last updated:** 2026-11-01  
**Track:** Bottom-up NIFTY 50 constituent weekly-expiry prediction  
**Status:** C0 PASS; C1 data feasibility IN PROGRESS / RIGHTS-BLOCKED  
**Prediction status:** No constituent panel, trained stock model or bottom-up forecast exists  
**Trading status:** NOT VALIDATED; no strategy is approved or implied

| Phase | Status | Next action |
|---|---|---|
| C0 — Registration/governance | PASS | Actions workflow validated required files and plan structure; governance regression tests passed; report committed as 746d1b382e338e760b1cf4b3ee5ea6fa6b63bc85 |
| C1 — Point-in-time universe/data audit | IN PROGRESS / BLOCKED | 15:15 expiry proxy accepted and sample validation passed; historical-weight candidate cached; close 2025-09 onward weight gap, historical corporate-action identity, full stock OHLCV coverage and basket reconciliation under review |
| C2 — Panel labels/features | PENDING | Build only after C1 passes; validate target construction and freeze source hashes/split |
| C3 — Stock models/baselines | PENDING | Pooled stock panel and bounded benchmarks only after C2 passes |
| C4 — Index aggregation/uncertainty | PENDING | Weighted expected return and dependence-aware probability; compare on matched cycles |
| C5 — Economic/execution gate | PENDING | Contract-level fills and date-effective Paytm Money costs required before any strategy claim |
| C6 — Manuscript/independent audit | PENDING | Complete manuscript, plots, tables, appendices and formula/repository audit |


## Latest gate update — 2026-11-01

- **Expiry proxy gate: PASS on the tested sample.** By user instruction, the expiry observation is the close of the latest one-minute candle timestamped 15:00 through 15:14 IST, treated as a 15:15 proxy and not mislabeled as the 15:30 exchange close. Protected run [41247509692](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41247509692) passed all 10 five-symbol/two-date anchor and expiry-proxy checks; all selected the 15:14 candle.
- **Current universe: 50/50. Historical symbol master match: 79/84.** A separate legacy HDFC Ltd ID test passed on 2022-10-31 and 2023-06-30 (2/2). JPASSOCIAT, RANBAXY and MCDOWELL-N only appear in the ledger in 2014, before the confirmatory 2018-04 start. TATAMOTORS/TMPV remains a dated demerger/symbol boundary; pre/post prices must not be joined unadjusted.
- **Historical weight candidate: acquired and validated.** 216 dated rows, 100 ticker columns, 2008-01-31 to 2025-08-31; row sums within 4.3e-14 of 100%. Cache: data/constituent_weekly/nifty50_weights_monthly.csv; audit: [C1_NIFTY50_WEIGHT_AUDIT.json](C1_NIFTY50_WEIGHT_AUDIT.json). Licence is CC BY-NC-SA 4.0 and commercial use is not permitted; the source has estimated/extrapolated event weights and is not accepted as official daily IWF.
- **Official source search:** NSE All Reports lists historical “Market Capitalisation, Weightage, Beta for NIFTY 50 & NIFTY Next 50” and “Indices - Market Capitalisation & Weightage” reports. NSE Market Pulse gives some recent sector-level weights but not a full stock-level point-in-time series. Automated NSE collection remains disabled pending rights/licence clearance. The candidate file does not cover 2025-09 onward.
- Latest offline workflow regression validation: [run 41247674443](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41247674443), **18 passed**. The status renderer now reports the user's expiry rule, HDFC legacy sample, and weight-cache result.
- **Overall C1 remains NOT PASSED.** The five-symbol sample is not a 50-stock data panel. Required next gates: authorised/official stock weights after 2025-08 and historical reconciliation, dated ISIN/security identities/corporate actions, full anchor/expiry-proxy OHLCV coverage, and constituent basket reconstruction against the official NIFTY 50 index.
## Initial source findings (document review only)

- NIFTY 50 methodology uses free-float market-cap weights; a majority vote of stock directions is not the primary index aggregation rule.
- One-time September 2026 report sample: NIFTY50 table parsed as 50 unique constituents with displayed weights summing to 100.0%; this is schema integrity only, not permission or historical point-in-time validation.
- BKKB20/nse-index-history is a promising historical membership reconstruction candidate, but its README discloses unprocessed scanned circulars and pre-2010 mapping limitations.
- vishalvx/nifty-indices-datasets provides binary membership rather than numerical free-float weights; it cannot be used as a primary weight series.
- Dhan v2 documentation describes up to five years of intraday history for active instruments and 90-day request windows; historical inactive constituents remain unverified.
- Parent repo's latest index-only run 41145607225 (2026-10-30) reports 398 weekly labels, 318 development and 80 holdout rows, but the anchor remains provisional and no executable strategy is certified. This is benchmark context only.

## Gate decision

No model training until point-in-time membership, numeric free-float weights, security mappings, corporate actions, stock anchor/close coverage and basket-to-index reconstruction all pass C1. If these inputs cannot be sourced reliably, stop at C1 and publish the exact data limitation rather than fabricate approximations.


## C0 acceptance evidence

- Automated Actions commit: [746d1b3](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/commit/746d1b382e338e760b1cf4b3ee5ea6fa6b63bc85).
- Validation artifact: C0_VALIDATION_REPORT.md — PASS.
- Scope: structural governance validation and the BUP-01 plan regression tests only.
- C1 remains IN PROGRESS / RIGHTS-BLOCKED: the one-time September 2026 CSV passed only a structural check; no licensed historic weights, certified membership history, constituent stock data or basket reconstruction has passed empirical validation.


## C1 source-audit work started

- Official report discovery: identified the NSE Indices monthly weightage ZIP families and the corresponding NSE India all-reports category.
- Automated retrieval: initial one-time Actions test downloaded a sample before terms review. All subsequent remote retrieval and raw artifact uploads have been disabled; the workflow now inspects only separately authorised local archives.
- Third-party data: the HF historical weight dataset is restricted to CC-BY-NC-SA non-commercial use and documents extrapolation/static-between-snapshot assumptions; not accepted as primary weights.
- Membership: the public circular reconstruction is only a candidate. Ticker-only aliases can collapse distinct predecessor/successor securities; ISIN and effective-date reconstruction is required.
- NSE Indices Terms of Use were reviewed; automated collection without express written consent and redistribution/copying without prior written permission are restricted. Issue #27 requests deletion of the earlier raw Actions artifact and associated cache if possible.

<!-- C1_FETCH_STATUS_START -->
## Latest automated C1 offline-source audit

- Recorded at (UTC): 2026-10-31T06:57:43.460536+00:00
- Audit status: NO_AUTHORISED_ARCHIVE
- Network collection performed: False
- This is file-integrity/schema evidence only; it is not point-in-time membership, source permission, weight validity or trading-data validation.
- C1 acceptance: NOT PASSED until licensed/authorised point-in-time weights, membership, identifiers, corporate actions, equity bar coverage and basket reconciliation pass.
<!-- C1_FETCH_STATUS_END -->

## C1 decision update — 2026-10-31

- Technical sample result: September 2026 NIFTY50 CSV has a title preamble, table header at row index 2, 50 unique symbol rows and displayed weight total 100.0%. No individual symbol/weight values are reproduced.
- A third-party current-members CSV (project README dates it March 2026) differs from the September sample by one name each: candidate-only WIPRO, report-only BSE. Treat it as stale/date-mismatched, not ground truth.
- The official October report archive includes a NIFTY50 PDF; it has not been analysed.
- Rights correction: remote NSE scraping and raw archive artifact publication have been disabled. C1 workflow is now offline-only for separately authorised input files.
- Cleanup issue: [#27 remove the prior raw NSE sample artifact/cache](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/issues/27).
- The existing Dhan auth path and data pipeline are under audit. Prior parent logs report inconsistent TOTP renewal and a separate options DH-905 error; no stock-equity API call has yet been verified.
- C1 is NOT PASSED. No panel, feature table, stock prediction or trading result exists.


## Workflow validation record — 2026-10-31

- Initial one-time source retrieval workflow run 41177903446 completed successfully before the data-rights restriction was discovered. Its raw output artifact is under cleanup issue #27.
- Offline workflow run 41178553686 (run #28) failed during checkout because a literal backslash was prepended to the GitHub branch-ref expression. The test and inspection steps were skipped. The expression was corrected in commit 0b430118c003e2f626b70097756e641fea55067c.
- Subsequent run 41178676032 (run #35) is reported as action_required and exposes no job steps. It has not demonstrated a test pass. The workflow was then changed to read-only permissions and no longer uploads artifacts or commits data.
- Current workflow revision: a2dd17c865250a068ffb60ee94d3cc4fe19bbcd0. The read-only test has not yet been observed executing successfully.

**Validation status:** C0 PASS. C1 offline workflow tests are NOT YET VERIFIED by GitHub Actions. C1 data gate remains RIGHTS-BLOCKED / IN PROGRESS. No model or constituent forecast exists.


## Licensed open-source data candidate — audit completed 2026-10-31

- CC BY 4.0 NIFTY50 membership subset cached at `data/derived/constituent_weekly/nifty50_membership_intervals.csv`, with attribution file `C1_MEMBERSHIP_DATA_ATTRIBUTION.md`.
- Membership audit: 83 intervals, 82 symbols; 50 snapshot_floor / 33 press_release; all 93 month-15 cardinality checks from 2018-01 to 2025-09 returned 50 active intervals. Latest event 2025-09-30. No numeric weights.
- Shareholding dataset audit: 2,584 records / 78 NIFTY50-related tickers in all years; quarterly coverage 37/50 in 2018-03, 47/50 in 2018-06, 41/50 in 2020-06, 43/50 in 2022-03, 49/50 in 2023-06, and 50/50 from 2023-09 through 2025-09.
- Ownership records are not official IWF. Roll-ups lack detailed strategic exclusions; `100%-promoter` is rejected as an IWF calculation. Filing-index manifests contain broadcast timestamps, which must be joined by XBRL filename before causal feature use.
- AMFI ETF portfolio data are not used because its Terms of Use restrict public redistribution/derivative works and storage without permission.
- C1 stays BLOCKED: no point-in-time numerical free-float weights, no NIFTY50 membership update after 2025-09-30 in this candidate, and no Dhan stock intraday coverage result yet.


## C1 automation / workflow validation update — 2026-10-31

- Offline authorised-source workflow run [41180457400](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41180457400) completed **SUCCESS**. Checkout, offline source-audit tests, local archive inspection, status update and job-summary publication all passed.
- This is only code/structure and offline archive validation. No separately authorised archive was present in the runner; the result remains `NO_AUTHORISED_ARCHIVE`. The earlier one-time September 2026 sample is documented separately and does not provide historical weekly IWF.
- Dhan equity preflight script, response-validation tests and a separate manual/read-only same-repository PR workflow are now committed. The workflow uses the existing POST-based `live_api.app.refresh_dhan_token()` function and never writes raw bars or tokens.
- No Actions run for the Dhan equity preflight is visible as of this status update. Therefore no Dhan profile, equity security-ID resolution, 2018 daily history or 1-minute stock-bar request has passed yet.
- Shared scheduled Dhan token script defect is separately staged in [PR #28](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/pull/28): GET was corrected to POST. That PR's mocked Actions check also has no visible run yet.
- Current C1 workflow source revisions: offline audit workflow has read-only permissions; Dhan preflight workflow is read-only and only runs for same-repository C1 PRs/push/manual runs. No raw report scraping or artifact upload is configured.

**Phase decision:** C0 PASS. C1 offline workflow PASS. C1 market-data/weights gate remains BLOCKED. Do not create C2 panel or fit stock models until numeric point-in-time free-float weights, the post-2025-09-30 current membership, security identity/corporate actions, and constituent 1-minute price coverage are validated.

<!-- C1_DHAN_STATUS_START -->
## Latest Dhan equity preflight

- Recorded at (UTC): 2026-10-31T22:20:24.242099+00:00
- Dhan auth method/status: totp_refresh / SUCCESS
- Profile HTTP status: NOT_RECORDED
- Status: PASS_ACTIVE_EQUITIES
- Data plan active: True
- Current NIFTY 50 universe resolved in current Dhan master: 50/50
- Historical membership symbol aliases matched in current Dhan master: 79/84
- Five-symbol one-minute anchor/expiry-proxy checks: 10/10
- Accepted expiry proxy: last returned one-minute candle at/before 15:15:00 IST; sample proxy timestamp(s): 2022-10-31T15:14:00+05:30, 2026-10-29T15:14:00+05:30
- Historic HDFC Ltd legacy-security-ID probes: 2/2 passed
- Deep daily-history probe: PASS
- Historical-weight candidate cache: CACHE_VALIDATED; 216 rows, 100 ticker columns, 2008-01-31 to 2025-08-31
- Weight candidate licence: CC BY-NC-SA 4.0; commercial use permitted: False
- This is a five-symbol/two-date market-data sample, not full-universe OHLCV certification.
- Raw bars, prices, security IDs, credentials and tokens are not stored in this report.
- C1 remains gated by official/authorised point-in-time weights, the 2025-09 onward weight gap, full historical security identity and coverage, and index-basket reconciliation.
<!-- C1_DHAN_STATUS_END -->

## C1 resume checkpoint — 2026-10-31

- Offline authorised-source audit workflow [41181684637](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41181684637): SUCCESS; checkout, offline tests, local archive inventory and summary publication all passed. Result remains NO_AUTHORISED_ARCHIVE.
- Dhan equity preflight workflow [41181684573](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41181684573): workflow SUCCESS, offline tests 9/9 PASS, but live profile check returned HTTP 401. No equity price coverage was tested.
- Shared token refresh PR [#28](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/pull/28): mocked regression and Actions integration checks both SUCCESS. PR #28 has passing checks and was marked ready for review, but GitHub reports a merge conflict (`mergeable_state=dirty`); it remains open/unmerged. The main scheduled helper is not yet fixed.
- Open data candidate audit: CC BY 4.0 project ledger now has 86 NIFTY 50 intervals/85 symbols after 2026 WIPRO-to-BSE and Tata Motors demerger corrections. The corrected April 2018–October 2026 month-end test expects 50 entries on 102 dates and 51 on 2025-10-31 due the official zero-price DUMMYTATAM placeholder. There are no numeric weights; quarterly ownership disclosures are not official IWF.
- C1 remains BLOCKED. C2 panel construction and model training remain prohibited until rights, point-in-time official/free-float weights, current membership, ISIN/security identity, corporate actions, Dhan profile/data entitlement, historical equity bars and weighted basket reconciliation all pass.


## Dhan API documentation reconciliation — 2026-10-31

- Dhan v2 documentation specifies POST to `/app/generateAccessToken` with `dhanClientId`, `pin`, and `totp`; tokens are valid for 24 hours. The profile endpoint example sends only the `access-token` header and returns token validity plus `dataPlan` status. Data APIs require a separately subscribed plan. Source: https://dhanhq.co/docs/v2/authentication/.
- The preflight now tests the profile endpoint with only the documented access-token header, while retaining client-id for subsequent market-data requests. Regression tests pass 10/10. The latest live run still receives HTTP 200 without an accessToken from token generation and HTTP 401 from profile; account secret validation is now the blocking dependency.


## 2026-10-31 — Dhan authentication retry after shared-helper correction

- Corrected `scripts/refresh_dhan_token.py` on the C1 branch to use POST with query parameters, reject line breaks, mask the ephemeral token and export only through `GITHUB_ENV`. Added mocked regression tests and wired the helper/test paths into the C1 Dhan workflow.
- The BUP-01 preflight already used POST; its request shape was retained. This avoids conflating the shared-helper defect with the independent live-account authentication failure.
- Actions run [41182555655](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41182555655): all steps passed, including 10/10 offline tests. Live token endpoint returned HTTP 200 but only `message` and `status` keys; no access token was returned. The fallback profile request returned HTTP 401. No security master, daily bars or intraday bars were queried.
- Added safe provider-error categorisation (category only; no provider message text) and a regression test. A subsequent run is pending/in progress at the time of this log update; its result must be checked before closing this diagnostic.
- C1 remains BLOCKED. The token endpoint's HTTP 200 is not authentication success. Do not infer the token secret values or expose them. Next gate is to classify Dhan's authentication response safely, then request user-owned secret correction only if the provider confirms an invalid/mismatched credential.

## C1 source/rights audit update — 2026-10-31

- Official NIFTY methodology confirms free-float index capitalisation uses shares outstanding × IWF × capping factor × price; the IWF process excludes a broader set of strategic holdings than promoter/public/FII/DII roll-ups. Quarterly ownership data is not a substitute for official IWF.
- NSE website Terms of Use expressly restrict systematic/automated collection and restrict copying/storage/redistribution and virtual-trading/simulation use without permission. The project therefore keeps remote NSE scraping and raw report caching disabled pending an applicable written licence/permission determination.
- Dhan v2 documents five-year intraday coverage only for active instruments and a maximum 90-day request window. This does not establish coverage for delisted/inactive historic constituents. The successful five-symbol historical probe is a limited sample, not universe-wide evidence.
- No additional TOTP attempt was made. Existing 2026-10-30 close-window gap and 2026-10-29 inconclusive auth retry remain unchanged.
- **Decision:** C1 remains BLOCKED / RIGHTS-DEPENDENT. C2 remains prohibited. Next permitted work: review the exact Dhan subscription terms/covered inactive instruments and identify a licensed or explicitly authorised historical constituent-weight source; do not scrape NSE pages or ingest non-commercial weights into a trading workflow.

## C1 membership sub-gate — 2026-10-31

**MEMBERSHIP PASS WITH LIMITATIONS**

- Added the NIFTY 50-only CC BY 4.0 point-in-time membership subset at `data/constituent_weekly/nifty50_membership_intervals.csv`, with attribution/provenance in [MEMBERSHIP_DATA_PROVENANCE.md](MEMBERSHIP_DATA_PROVENANCE.md).
- Upstream data has 83 NIFTY 50 intervals, with no weights, and last reconstitution at 2025-09-30. The project snapshot adds the official 2026-09-30 one-for-one change WIPRO → BSE using the 2026-08-10 NSE Indices press release.
- Corrected regression/cardinality check: 103/103 month-end dates from 2018-04-30 through 2026-10-31 match expected counts: 102 dates have 50 entries and 2025-10-31 has 51 because DUMMYTATAM was temporarily included at zero price. This tests cardinality, not every member transition independently; pre-2018 data remains excluded from confirmatory modelling due known source drift.
- Added [machine-readable audit](C1_MEMBERSHIP_AUDIT.json) and `tests/test_bup01_membership_intervals.py`.

**Overall C1 remains BLOCKED.** The membership sub-gate is improved, but the dataset has no numerical free-float weights, ISIN/security-id history or corporate-action mapping. Dhan constituent-bar coverage still lacks a full-universe test and recent expiry-close completion. No C2 panel/model is permitted.

**Best official exact-weight route identified:** NSE Indices data subscription includes historical constituent identifiers, market caps, weights and prices; licensing enquiry: `indices@nse.co.in`. Free alternatives reviewed are insufficient or carry upstream/non-commercial restrictions. Automated NSE web scraping remains disabled.

## C1 membership identity correction — 2026-10-31

A second corporate-action audit refined the membership ledger. The upstream file's `TMPV` symbol was incorrectly carried backwards into dates before the NSE symbol change. It is now corrected to `TATAMOTORS` through 2025-10-23 and `TMPV` from 2025-10-24, as per NSE circular NSE/FAOP/70882.

The ledger also now captures the temporary `DUMMYTATAM` zero-price placeholder from 2025-10-14 through 2025-11-16, explicitly flagged `market_data_required=FALSE`. Thus the corrected 103 month-end snapshots contain 50 unique entries on 102 dates and 51 entries on 2025-10-31. The earlier all-50 count is superseded. The placeholder is for index-ledger completeness only; it is never a stock prediction input.

The revised six-test suite and machine audit are committed. **Post-correction Actions validation passed:** run [41185169548](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41185169548), 6 tests passed. Overall C1 remains BLOCKED on exact licensed IWF, ISIN/security identity history, other corporate actions and constituent price coverage; no C2 panel/model may be built yet.

## Membership CI acceptance — 2026-10-31

- Corrected membership integrity workflow [41185169548](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41185169548): **SUCCESS; 6 tests passed**.
- The passing suite checks half-open effective-date intervals, the 2025-10-24 TATAMOTORS/TMPV symbol transition, DUMMYTATAM zero-price placeholder inclusion/removal and its non-tradable flag, corrected 103 month-end cardinality (102×50, 1×51), no fabricated index weights, and machine-audit consistency.
- This passes the membership-file integrity sub-gate only. It does not certify every upstream membership event, official IWF, ISIN mapping, corporate actions other than those explicitly patched, stock OHLCV coverage or basket/index reconstruction.


## Recovery continuation — bounded public-source audit (2026-10-31)

- Verified the membership Actions run 41185169548 as SUCCESS (six tests passed); corrected stale log wording on main.
- Rechecked official NSE Indices data subscription, NSE free-float methodology page, Dhan v2 historical-data documentation, a CC BY-NC-SA Hugging Face weights dataset and a GitHub approximate-weight dataset.
- The official exact-weight/identifier data route is licensed/subscription. The Hugging Face dataset is non-commercial; the GitHub dataset explicitly uses equal-weighted/binary approximations. Dhan documents five-year minute history for active instruments and 90-day request windows, not guaranteed inactive/delisted history.
- No source found in this bounded pass clears rights + exact historical IWF + security/corporate-action identity + full constituent intraday/expiry-close coverage together.
- **Gate decision unchanged:** membership sub-gate PASS WITH LIMITATIONS; overall C1 BLOCKED; C2 not authorised. Do not fabricate weights, scrape NSE without permission, or fit stock models on an incomplete universe.
- References: https://www.nseindia.com/static/nse-indices/index-data-subscription ; https://www.nseindia.com/static/products-services/indices-nifty50-index ; https://dhanhq.co/docs/v2/historical-data/ ; https://huggingface.co/datasets/AMP4010/Historical_Nifty_50_Constituent_Weights_20Y ; https://github.com/vishalvx/nifty-indices-datasets.


## User data-source direction — 2026-10-31

User confirmed “Dhan” as the available data route. Treat the existing Dhan Data API subscription and GitHub Actions secrets as the primary permitted market-data source for constituent prices. Next C1 data work must use Dhan-first, cache-first acquisition: resolve the point-in-time constituent universe to Dhan security IDs, inventory historical daily/intraday coverage by symbol and date, test delisted/inactive coverage, and capture both forecast-time anchors and expiry-close bars. Reuse cached successful responses; make bounded date/security batches; serialize authentication and avoid unnecessary TOTP refresh loops. Never expose secrets or raw credentials.

Dhan price data does not itself establish official historical NIFTY free-float IWF or index methodology membership. Keep those as separate gates and do not infer weights from equal weights, market cap, or promoter/FII/DII ownership. Overall C1 remains BLOCKED until weights/identity and full price coverage are verified. C2 remains gated.

## Full-universe Dhan scrip-master audit — 2026-10-31

- Extended the C1 preflight to read the licensed point-in-time membership ledger and construct (a) the 2026-10-31 active tradable NIFTY 50 symbol set and (b) the distinct historical tradable symbol/alias set. The zero-price DUMMYTATAM placeholder is excluded from both tradable sets.
- The preflight now resolves both sets against the current Dhan scrip master, recording counts and unresolved symbol names only; security IDs and raw data are never written. The report explicitly warns that a current-master match does not prove historical security-ID validity for an inactive/delisted instrument.
- Five-symbol price probes remain separately bounded; no bulk 50-stock candle download was initiated by this code change.
- PR validation run [41223379333](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41223379333): SUCCESS; 13 offline tests passed. The live Dhan step was intentionally skipped because this was a pull-request event; workflow guard prevents exposing credentials to PR code.
- Live data status unchanged: latest successful live Dhan evidence remains the five-symbol partial preflight [41182679514](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41182679514). Full-universe security-ID resolution has not yet been run. Use the workflow's manual workflow_dispatch on the C1 branch for the live secret-backed step.
- C1 remains BLOCKED; C2 remains gated. No constituent panel/model/forecast or strategy is claimed.


## Live Dhan full-universe result — 2026-10-31

Protected Actions run [41224048773](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41224048773) completed successfully. The Dhan TOTP refresh returned an access token, profile authentication succeeded, and the Data API plan was active.

- Current active NIFTY 50: **50/50** symbols resolved against the current Dhan scrip master.
- Historical tradable membership ledger: **79/84** distinct symbols/aliases found in the current scrip master. Five absent from the current master: HDFC, JPASSOCIAT, MCDOWELL-N, RANBAXY, TATAMOTORS. These require dated corporate-action/successor/security-ID mapping; absence from today's master does not prove historical data unavailable.
- Five-stock candle sample: daily history returned 22 bars for Jan 2018. All five stocks passed the 2022-10-31 one-minute probe (374 bars each, including 10:00 anchor and 15:25–15:29 expiry close).
- Recent sample 2026-10-29: 359 bars per stock, valid 10:00 anchor, but feed stopped at 15:14 IST; expiry-close window missing for all five. Targeted 15:20–15:30 requests returned empty arrays (**0/5**).
- No raw price bars, security IDs or credentials were committed. Sanitized output is in [C1_DHAN_PREFLIGHT.json](C1_DHAN_PREFLIGHT.json).
- C1 remains BLOCKED: historical security mapping for five aliases, recent close-bar coverage, full constituent OHLCV history, official numerical IWF/weights and basket reconciliation remain open. C2 is not authorised.


## Public minute-data source audit — 2026-11-01

- Updated pre-registered plan to v1.1 to apply the user-approved 15:15 expiry proxy consistently to both constituent and NIFTY index outcomes; 15:30 official close is a separate sensitivity only.
- Discovered historical public minute archive gsidhu/nse-intraday-data: 47/50 point-in-time NIFTY 50 member files on both 2022-11-03 and 2022-11-04. Missing: DIVISLAB, SBILIFE, APOLLOHOSP. Five sample stocks plus NIFTY had 10:00–10:03 anchor rows and 15:14 bars on 2022-11-03.
- The archive README claims MIT but neither the fork nor upstream root had a LICENSE file. It is diagnostic only; no bars were imported. Another 2024–2026 stock dataset is limited to research/education and excludes commercial redistribution; a large HF candidate has no verified licence; DataPointX downloads are not open yet.
- Dhan docs confirm five years of minute history for active instruments and 90-day query chunks, but no guarantee for inactive/delisted instruments. Daily history extends to instrument inception.
- **C1 remains NOT PASSED / RIGHTS + COVERAGE BLOCKED.** We do not have licensed full-universe 1-minute history, point-in-time official weights or 98% basket coverage. C2 remains gated.
- Details: [C1_PUBLIC_INTRADAY_SOURCE_AUDIT.md](C1_PUBLIC_INTRADAY_SOURCE_AUDIT.md).


## Workflow mistake and correction — 2026-11-01

- Push run [41249370561](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41249370561) failed at `validate_plan.py` because its registration check hard-coded plan version 1.0 after the user-approved plan amendment to v1.1.
- This was a validator defect, not a research-data failure. The separate C1 authorised-source audit passed in run [41249370606](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41249370606).
- Corrective change: validator now parses the declared plan version, requires the same version in the version history, and verifies the 15:15-proxy definition and separate 15:30 sensitivity. A regression test covers the v1.1 amendment.
- Re-run status will be added after the next Actions result is observed. C1 remains NOT PASSED; C2 stays gated.
