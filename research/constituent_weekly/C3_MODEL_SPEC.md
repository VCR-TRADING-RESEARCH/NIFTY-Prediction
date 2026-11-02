# C3 confirmatory stock modelling — execution specification

**Branch:** `phase/constituent-weekly-outcomes-c3-models`  
**Plan:** BUP-01 v1.3 (locked)  
**Status:** READY — secure panel handoff is being enabled; no C3 model run is claimed.

## Frozen C2 input and secure handoff

C2 formal acceptance is recorded in [C2_ACCEPTANCE_REPORT.md](C2_ACCEPTANCE_REPORT.md), from workflow [41398864378](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41398864378)(https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41353406358). It accepted 258 cycles, 12,807 constituent-cycle rows, 61 symbols, 100% valid index targets, 258/258 cycles meeting the 47/94% rule, and zero duplicate cycle rows. Holdout starts at cycle 206 (anchor 2025-10-29; expiry 2025-11-04).

The row-level panel is AES-GCM encrypted with the stable HF_TOKEN-derived cache key and stored in the C2 Actions cache. It must be transferred to C3 as ciphertext only. The C2 workflow is being amended to attach only the encrypted frozen-panel files plus the sanitized report to its run artifact. C3 must download the artifact from the latest successful C2 run, verify the ciphertext SHA-256 values against the C2 manifest, decrypt only inside the Actions runner using HF_TOKEN, and never commit plaintext panel data.

## Registered C3 methods

- Unit of time split: complete expiry cycle. Every constituent row for a cycle remains in the same fold.
- Eligible training rows: C2 `primary_flag == true`, non-flat `stock_label`, valid causal features, and no missing target.
- Primary candidate: pooled regularised logistic regression for UP/DOWN.
- Secondary candidates: expanding UP-frequency / prior-cycle sign and own-stock momentum baselines; constrained ExtraTrees classifier; pooled regularised continuous-return regression; one constrained HistGradientBoosting candidate.
- All imputers, scalers and estimators fit inside each chronological training fold.
- First confirmatory forecast requires at least 104 earlier eligible cycles. C2 provides 258 eligible cycles; final 20% holdout is sealed from cycle 206. Do not use holdout cycles for feature selection, tuning or calibration.
- Fit/refit on prior cycles only. Generate strictly out-of-fold stock predictions; no stock row from the same expiry cycle may appear in training.
- Evaluate balanced accuracy, MCC, ROC-AUC where defined, Brier score, log loss, precision/recall, calibration, and per-cycle cross-sectional Spearman rank IC. Report all registered candidates and failures.
- Quantify uncertainty by four-cycle moving-block bootstrap over expiry cycles (2,000 replicates; seed 20261031); retain whole cycles.
- Keep the 292 identity-flagged rows and 3 action-crossing rows out of the primary model; report a separate sensitivity only if event treatment is defensible. Do not claim unresolved event/identity checks passed.
- Export per-stock OOF forecasts only in encrypted form for C4. Publish aggregate metrics and cycle-level summaries without raw prices or per-stock raw features.

## Acceptance and stop rules

C3 is accepted only if the full chronological pipeline, fold isolation, leakage tests, coverage, duplicate checks, and untouched holdout reporting all pass. Prediction success does not imply trading profitability. C5 remains separate and requires executable instrument fills, date-effective Paytm Money brokerage/levies/taxes, spread, slippage, lot size and conservative fill assumptions.

No additional model families, tuning loops or holdout retuning are permitted beyond the locked plan.


## Automated execution trigger

C3 runs automatically when a successful C2 panel workflow completes, and also on a material C3 code/spec push or manual `workflow_dispatch`. A manual run resolves the latest successful C2 run and downloads its artifact. Model outputs are committed only in aggregate/sanitized form; the per-stock OOF forecast remains AES-GCM encrypted.


## Latest execution checkpoint — 2026-11-02

C2 run [41398864378](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41398864378) passed all 15 steps and formal acceptance, including 258 scheduled cycles, 12,807 constituent-cycle rows, 61 symbols and 258/258 valid index targets. The holdout starts at cycle 206. The manifest records 292 identity-flagged rows, 3 known action-crossing rows, 92 feature-missing observations and 19 flat stock labels; these limitations remain explicit.

C3 run [41401986460](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41401986460) downloaded and authenticated the artifact and passed compilation/offline tests, then failed before model fitting because pandas received raw bytes rather than a file-like buffer. The parser fix and encrypted CSV round-trip test are recorded as E0106.
