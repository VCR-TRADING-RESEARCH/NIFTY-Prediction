# C1 Continuous Dhan Stock and NIFTY Target Coverage Report

**Result: INTRADAY DATA-COVERAGE SUB-GATE PASS**
**Actions run:** https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41301447865
**Run completed:** 2026-11-01 11:46:24 UTC

## Registered scope and outcome

The live Dhan auditor requested up to 90 calendar days at a time for the point-in-time tradable stock universe and the actual NIFTY 50 index. It retained the stock 10:00–10:03 anchor and latest valid 15:00–15:14 IST expiry proxy, and the corresponding observed NIFTY index target. It did not use ETF weights or index IWF.

| Metric | Result |
|---|---:|
| Weekly expiry cycles scheduled | 258 |
| Valid observed NIFTY anchor/expiry target pairs | 258 / 258 (100%) |
| Cycles meeting at least 47 stock and at least 94% coverage | 258 / 258 |
| Cycles meeting both stock and index target rules | 258 / 258 |
| Confirmatory cycles after 104 prior accepted cycles | 154 |
| Unresolved active security symbols | 0 |
| Dhan historical-data requests | 1,083 |
| Non-overlapping request windows | 21 |

**Data-coverage disposition:** PASS. The workflow's final gate step explicitly emitted C1_CONTINUOUS_COVERAGE_GATE_PASSED.

## 90-day window request log

The table below transcribes the sanitized C1_COVERAGE_CHUNK job output. The cumulative-requests column is the job's printed total after each window.

| # | From | To | Index response | Stock symbols requested | Cumulative requests |
|---|---|---|---|---:|---:|
| 1 | 2021-11-12 | 2022-02-09 | PASS_RESPONSE | 50 | 51 |
| 2 | 2022-02-10 | 2022-05-10 | PASS_RESPONSE | 51 | 103 |
| 3 | 2022-05-11 | 2022-08-08 | PASS_RESPONSE | 50 | 154 |
| 4 | 2022-08-09 | 2022-11-06 | PASS_RESPONSE | 51 | 206 |
| 5 | 2022-11-07 | 2023-02-04 | PASS_RESPONSE | 50 | 257 |
| 6 | 2023-02-05 | 2023-05-05 | PASS_RESPONSE | 50 | 308 |
| 7 | 2023-05-06 | 2023-08-03 | PASS_RESPONSE | 51 | 360 |
| 8 | 2023-08-04 | 2023-11-01 | PASS_RESPONSE | 50 | 411 |
| 9 | 2023-11-02 | 2024-01-30 | PASS_RESPONSE | 50 | 462 |
| 10 | 2024-01-31 | 2024-04-29 | PARTIAL_TARGET_DATES | 51 | 514 |
| 11 | 2024-04-30 | 2024-07-28 | PASS_RESPONSE | 50 | 565 |
| 12 | 2024-07-29 | 2024-10-26 | PASS_RESPONSE | 52 | 618 |
| 13 | 2024-10-27 | 2025-01-24 | PASS_RESPONSE | 50 | 669 |
| 14 | 2025-01-25 | 2025-04-24 | PASS_RESPONSE | 52 | 722 |
| 15 | 2025-04-25 | 2025-07-23 | PASS_RESPONSE | 50 | 773 |
| 16 | 2025-07-24 | 2025-10-21 | PASS_RESPONSE | 52 | 826 |
| 17 | 2025-10-22 | 2026-01-19 | PASS_RESPONSE | 51 | 878 |
| 18 | 2026-01-20 | 2026-04-19 | PASS_RESPONSE | 50 | 929 |
| 19 | 2026-04-20 | 2026-07-18 | PASS_RESPONSE | 50 | 980 |
| 20 | 2026-07-19 | 2026-10-16 | PASS_RESPONSE | 51 | 1032 |
| 21 | 2026-10-17 | 2026-10-27 | PASS_RESPONSE | 50 | 1083 |

There were 20 fully successful index-window responses and one window-level PARTIAL_TARGET_DATES response (2024-01-31 to 2024-04-29). The final aggregate nevertheless reports all 258 expiry-cycle target pairs valid. The exact target date responsible for the partial window was not retained in the failed publication; this is disclosed rather than explained by inference.

## Publication incident and evidence limits

The auditor completed and wrote its sanitized JSON and Markdown outputs in the Actions runner. The later repository commit step attempted to rebase after concurrent edits. Git reported conflicts in research/constituent_weekly/STATUS.md and logs/RESEARCH_LOG.md. The separate target-coverage gate still passed.

The Actions workflow did not upload the detailed generated JSON as an artifact, so per-symbol and per-cycle QA detail is not available from this run. This report therefore preserves only aggregate counts and per-window lines present in the logs. It does not recreate or invent per-cycle/per-stock detail. Error E0070 records the publication failure.

## Remaining C1 gates

This result passes only the intraday stock/index target-data coverage sub-gate. It does not pass C1 overall:
- Daily OHLCV history used by causal features remains under a separate coverage audit.
- The dated symbol alias ledger exists, but exhaustive split, bonus, dividend, rights and merger/demerger adjustment review remains incomplete.
- Raw market bars and prices were not committed.
- C2 model construction remains gated until daily feature history and complete action-aware data integrity checks are accepted.

[Plan v1.3](RESEARCH_PLAN.md) · [C1 status](STATUS.md) · [error log E0070](../../logs/ERROR_LOG.md)
