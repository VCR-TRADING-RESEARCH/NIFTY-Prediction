# BUP-01 Research Status

**Last updated:** 2026-10-31  
**Track:** Bottom-up NIFTY 50 constituent weekly-expiry prediction  
**Status:** C0 PASS; C1 source feasibility audit IN PROGRESS  
**Prediction status:** No constituent panel, trained stock model or bottom-up forecast exists  
**Trading status:** NOT VALIDATED; no strategy is approved or implied

| Phase | Status | Next action |
|---|---|---|
| C0 — Registration/governance | PASS | Actions workflow validated required files and plan structure; governance regression tests passed; report committed as 746d1b382e338e760b1cf4b3ee5ea6fa6b63bc85 |
| C1 — Point-in-time universe/data audit | IN PROGRESS | Fetch official monthly weight-report sample; audit historical membership, point-in-time weights, IDs, corporate actions and stock intraday coverage |
| C2 — Panel labels/features | PENDING | Build only after C1 passes; validate target construction and freeze source hashes/split |
| C3 — Stock models/baselines | PENDING | Pooled stock panel and bounded benchmarks only after C2 passes |
| C4 — Index aggregation/uncertainty | PENDING | Weighted expected return and dependence-aware probability; compare on matched cycles |
| C5 — Economic/execution gate | PENDING | Contract-level fills and date-effective Paytm Money costs required before any strategy claim |
| C6 — Manuscript/independent audit | PENDING | Complete manuscript, plots, tables, appendices and formula/repository audit |

## Initial source findings (document review only)

- NIFTY 50 methodology uses free-float market-cap weights; a majority vote of stock directions is not the primary index aggregation rule.
- NSE Indices' monthly report page publishes two official ZIP families: Indices Market Capitalisation & Weightage, and Market Capitalisation, Weightage, Beta. Raw files, coverage dates and publication timestamps still require ingestion and audit.
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
- Automated retrieval: added an Actions-side link discovery, ZIP validation, archive inventory and SHA-256 manifest workflow; raw archives are intended for Actions cache/artifacts, not automatic raw-data commits.
- Third-party data: the HF historical weight dataset is restricted to CC-BY-NC-SA non-commercial use and documents extrapolation/static-between-snapshot assumptions; not accepted as primary weights.
- Membership: the public circular reconstruction is only a candidate. Ticker-only aliases can collapse distinct predecessor/successor securities; ISIN and effective-date reconstruction is required.
- C1 acceptance remains BLOCKED until raw official archives are parsed, historic weights and membership are validated, stock price coverage is measured, and the realised basket reconciles to NIFTY.

<!-- C1_FETCH_STATUS_START -->
## Latest automated C1 source-fetch result

- Recorded at (UTC): 2026-10-31T06:43:25.304581+00:00
- Official report retrieval status: SAMPLE_ARCHIVE_DOWNLOADED
- This result is source-fetch/inventory only; it is not a historical weight, membership, or trading-data validation.
- nifty50_weights_beta: DOWNLOADED_AND_INVENTORIED; file=mcwb_sep26.zip; sha256=eb6336b8e0c55a0b2cfd1a29d0c79e2b962e091d8d3a3d724e2245320ec0799b; error=None
- indices_market_cap_weightage: DOWNLOADED_AND_INVENTORIED; file=indices_dataOct2026.zip; sha256=7f1ba20b04ef45f0e061a00b4a8937145d8e9f8f277891ab20fe935826fe995f; error=None
- C1 acceptance: NOT PASSED; historical reports, point-in-time availability, membership and basket reconciliation remain required.
<!-- C1_FETCH_STATUS_END -->
