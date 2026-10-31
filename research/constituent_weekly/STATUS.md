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

- Recorded at (UTC): 2026-10-31T07:31:29.719420+00:00
- Status: BLOCKED_DHAN_AUTH
- Data plan active: None
- Current symbols resolved: 0
- Missing symbols from current scrip master: 0
- One-minute probe windows passing: 0/0
- Deep daily-history probe: NOT_RUN
- Raw bars, prices, security IDs, credentials and tokens are not stored in this report.
- This probe does not establish inactive/delisted instrument history, point-in-time membership or index weights.
<!-- C1_DHAN_STATUS_END -->
