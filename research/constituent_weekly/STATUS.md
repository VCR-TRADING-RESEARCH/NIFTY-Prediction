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
- C1 remains PENDING: no stock data, historical weights, constituent membership or index reconstruction has yet passed an empirical audit.


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
