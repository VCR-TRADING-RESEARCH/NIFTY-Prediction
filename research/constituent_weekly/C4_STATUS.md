# C4 — NIFTY Index Aggregation and Uncertainty

**Status:** GATED — CONFIRMATORY C4 NOT STARTED  
**C1 gate:** PARTIAL; not accepted  
**C2:** Panel run passed with C1 limitations  
**C3:** Exploratory stock-model run complete; no constituent model selected  
**C3-X:** Separate exploratory NIFTY meta-model complete but inconclusive  
**Gate workflow:** [41411507365 — SUCCESS](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41411507365) — fail-closed C1-before-C4 check passed.\n**Trading:** NOT VALIDATED

## Why C4 remains gated

The registered plan v1.4 allows C3-X as a bounded exploratory exception; it does not waive C1 or C2 acceptance and does not unlock confirmatory C4. The C1 developer gate report still lists incomplete dated security alias resolution and 711 point-in-time member-event candidates requiring independent corporate-action review. User-authorised progression to exploratory modelling is not a C1 pass.

The C3 stock-model holdout shows no reliable constituent-direction edge. The separate C3-X NIFTY meta-model produced 50.98% accuracy, 53.45% balanced accuracy and 48.68% ROC-AUC on 51 cycles; its paired advantage over lag direction was 1.96 percentage points with a four-cycle bootstrap 95% interval of −25.49 to +25.49 percentage points. This is exploratory and inconclusive, not a C4 result.

## Requirements before C4 can start

1. Close C1 point-in-time security/ISIN aliases and event-level corporate-action validation, with an audited exclusion ledger and independent source evidence.
2. Accept a single frozen C2 panel whose stock and NIFTY targets share the same eligible cycle identifiers and whose membership/action status passes the locked acceptance thresholds.
3. Regenerate all stock probabilities and predicted returns on that same frozen panel using strictly out-of-fold predictions; all stock rows from one expiry cycle must remain in the same fold.
4. Build cycle-level summaries only from those OOF outputs: mean/median probability, unweighted predicted breadth, predicted-return summaries, dispersion, sector summaries where point-in-time sector labels exist, forecast concentration and valid-member coverage.
5. Compare regularised logistic meta-model against the pre-registered breadth/history baselines and a matched direct-index benchmark on identical cycles.
6. Keep the final chronological holdout sealed; use cycle-block uncertainty and disclose calibration, class balance, regime drift and missing-member coverage.
7. Do not call any constituent summary an official NIFTY return. The observed NIFTY index target remains the label.

## Decision

No confirmatory C4 model is fitted in this branch. Do not reuse the C3-X or later C3 holdout to select features, tune models or claim significance. C4 will reopen only after the C1 gate is independently accepted and the complete matched sample is frozen.
