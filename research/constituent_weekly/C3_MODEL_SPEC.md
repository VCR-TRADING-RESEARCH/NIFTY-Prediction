# C3 confirmatory stock modelling — execution specification

**Branch:** `phase/constituent-weekly-outcomes-c3-models`  
**Plan:** BUP-01 v1.3 (locked)  
**Status:** EXECUTED — exploratory stock-model result recorded; C1 remains PARTIAL and trading is NOT VALIDATED.

## Frozen C2 input and secure handoff

C2 formal acceptance is recorded in [C2_ACCEPTANCE_REPORT.md](C2_ACCEPTANCE_REPORT.md), from workflow [41398864378](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41398864378). It accepted 258 cycles, 12,807 constituent-cycle rows, 61 symbols, 100% valid index targets, 258/258 cycles meeting the 47/94% rule, and zero duplicate cycle rows. Holdout starts at cycle 206 (anchor 2025-10-29; expiry 2025-11-04).

The row-level panel is AES-GCM encrypted with the stable HF_TOKEN-derived cache key and stored in the C2 Actions cache. It must be transferred to C3 as ciphertext only. The C2 workflow attaches the encrypted frozen-panel files plus the sanitized report to its run artifact. C3 must download the artifact from the latest successful C2 run, verify the ciphertext SHA-256 values against the C2 manifest, decrypt only inside the Actions runner using HF_TOKEN, and never commit plaintext panel data.

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

C3 run [41401986460](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41401986460) initially failed before fitting on a pandas bytes/file-like parsing defect (attempt 1). The runner was corrected with `io.BytesIO`, and the encrypted AES-GCM + gzip CSV round-trip regression test was added. Attempt 2 passed every workflow step, including model execution and encrypted forecast artifact upload.


## C3 result — exploratory only (2026-11-02)

The successful second attempt of [workflow run 41401986460](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41401986460) generated 7,512 OOF stock forecasts over 154 cycles, including 52 untouched holdout cycles (2,583 observations). On the holdout, momentum accuracy was 50.52% (balanced accuracy 50.77%, ROC-AUC 50.77%); logistic was 48.12% (49.03%, 48.53%); ExtraTrees 48.51% (49.21%, 47.92%); HistGradientBoosting 46.69% (48.94%, 48.83%). Logistic minus momentum cycle-macro accuracy was −2.37 percentage points; four-cycle moving-block bootstrap 95% interval [−10.04, +4.29] percentage points. Mean holdout return rank IC was −0.0193. The evidence does not establish stock-level predictive skill; no candidate is selected.

This C3 panel was accepted for exploratory modelling after the explicit progression waiver. The 292 identity-flagged rows and 3 action-crossing rows were excluded; the wider C1 catalogue and event continuity are not certified. No holdout retuning is permitted. C4 confirmatory aggregation remains gated by C1; the separate C3-X v1.4 exploratory NIFTY aggregation result is reported in its own phase record. No trading P&L, Paytm Money costs, options, FII/DII, global-market or news input was tested here.
