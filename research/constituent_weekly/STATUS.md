# BUP-01 Research Status

**Last updated:** 2026-10-31  
**Track:** Bottom-up NIFTY 50 constituent weekly-expiry prediction  
**Status:** C0 structural validation PASS; empirical stock research not yet started  
**Prediction status:** No constituent panel, trained stock model or bottom-up forecast exists  
**Trading status:** NOT VALIDATED; no strategy is approved or implied

| Phase | Status | Next action |
|---|---|---|
| C0 — Registration/governance | PASS | Actions workflow validated required files and plan structure; governance regression tests passed; report committed as 746d1b382e338e760b1cf4b3ee5ea6fa6b63bc85 |
| C1 — Point-in-time universe/data audit | PENDING | Validate original NSE circulars, historical numeric weights/IWF, IDs, corporate actions, Dhan auth and stock price coverage |
| C2 — Panel labels/features | PENDING | Build only after C1 passes; validate target construction and freeze source hashes/split |
| C3 — Stock models/baselines | PENDING | Pooled stock panel and bounded benchmarks only after C2 passes |
| C4 — Index aggregation/uncertainty | PENDING | Weighted expected return and dependence-aware probability; compare on matched cycles |
| C5 — Economic/execution gate | PENDING | Contract-level fills and date-effective Paytm Money costs required before any strategy claim |
| C6 — Manuscript/independent audit | PENDING | Complete manuscript, plots, tables, appendices and formula/repository audit |

## Initial source findings (document review only)

- NIFTY 50 methodology uses free-float market-cap weights; a majority vote of stock directions is not the primary index aggregation rule.
- NSE publishes historical index/security reports and index weightage report categories; point-in-time numeric weights and availability timestamps still require collection.
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
