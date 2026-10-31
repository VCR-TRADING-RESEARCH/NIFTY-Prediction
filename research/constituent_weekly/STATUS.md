# BUP-01 Research Status

**Last updated:** 2026-10-31  
**Track:** Bottom-up NIFTY 50 constituent weekly-expiry prediction  
**Status:** C0 PASS; C1 data feasibility IN PROGRESS / RIGHTS-BLOCKED  
**Prediction status:** No constituent panel, trained stock model or bottom-up forecast exists  
**Trading status:** NOT VALIDATED; no strategy is approved or implied

| Phase | Status | Next action |
|---|---|---|
| C0 — Registration/governance | PASS | Actions workflow validated required files and plan structure; governance regression tests passed; report committed as 746d1b382e338e760b1cf4b3ee5ea6fa6b63bc85 |
| C1 — Point-in-time universe/data audit | IN PROGRESS / BLOCKED | One-time report sample structurally parsed; automated NSE collection stopped pending permission; audit licensed/authorised weights, historical membership, security IDs, corporate actions and Dhan stock price coverage |
| C2 — Panel labels/features | PENDING | Build only after C1 passes; validate target construction and freeze source hashes/split |
| C3 — Stock models/baselines | PENDING | Pooled stock panel and bounded benchmarks only after C2 passes |
| C4 — Index aggregation/uncertainty | PENDING | Weighted expected return and dependence-aware probability; compare on matched cycles |
| C5 — Economic/execution gate | PENDING | Contract-level fills and date-effective Paytm Money costs required before any strategy claim |
| C6 — Manuscript/independent audit | PENDING | Complete manuscript, plots, tables, appendices and formula/repository audit |

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

- Successful authentication/data probe: Actions run [41182679514](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41182679514).
- Offline response-validation tests: **11 passed**.
- Fresh TOTP token: generated successfully; profile HTTP 200; Data API plan active.
- Current scrip master: **5/5** probe symbols resolved.
- Historical daily: **PASS**, 22 bars for 2018-01-01 to 2018-02-01.
- Historical one-minute: **5/5 PASS** on 2022-10-31; 374 bars per symbol, including the 10:00 anchor and 15:25–15:29 close window.
- Recent one-minute: 2026-10-30 returned 359 bars per symbol and valid 10:00 anchors, but no 15:25–15:29 bars; targeted close-window requests returned empty arrays (**0/5**).
- Follow-up 2026-10-29 probe: inconclusive because a subsequent TOTP call returned HTTP 200 without an access-token field; the fallback token failed profile authentication (HTTP 401). No price requests were made in that retry: [run 41182764467](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41182764467).
- Workflow hardened: pull-request checks now run offline tests only; live Dhan authentication is serialized and not triggered by workflow-file-only edits. This avoids needless TOTP requests during code review.
- No raw bars, prices, security IDs, credentials, tokens or provider message text are stored.
- C1 remains **NOT PASSED**: recent close coverage, inactive/delisted security history, point-in-time membership, official numerical free-float weights and basket reconciliation remain open.
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
- Regression/cardinality check: 103/103 month-end dates from 2018-04-30 through 2026-10-31 have exactly 50 unique NIFTY 50 members. This tests cardinality, not every member transition independently; pre-2018 data remains excluded from confirmatory modelling due known source drift.
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
