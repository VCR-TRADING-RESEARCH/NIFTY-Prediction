# Phase 11 — Diverse Model-Family Benchmark

**Branch:** research/phase-11-diverse-model-benchmark  
**Status:** COMPLETED — corrected CI run passed; results exploratory only  
**Plan version:** 1.3 addendum to the pre-registered plan  
**Budget:** One fixed expanding-window benchmark; no hyperparameter sweep or recursive feature search.

## Why this phase exists
Phase 10 compared simple rules, logistic regression, and ExtraTrees with one six-feature augmentation. It did not test diverse model families. This phase broadens the comparison while preserving the same target and source-gated weekly dataset.

## Research question
Across a fixed expanding-window evaluation, do distinct model families—regularized logistic regression, Random Forest, ExtraTrees, gradient boosting, histogram gradient boosting, and RBF SVM—provide materially different or consistently better predictions than simple baselines?

## Aim and objectives
1. Run a fixed, reproducible family-level benchmark on source-gated Phase 10 rows.
2. Compare direction and probability quality using identical prediction timestamps.
3. Report stability without treating weekly observations as independent.
4. Explicitly prevent the already inspected Phase 10 holdout from being represented as fresh confirmatory evidence.
5. Produce tables, charts, a machine-readable manifest and a manuscript section.
6. Preserve the separate trading gate: no strategy claim without dated instrument prices, fills, spreads/slippage and Paytm Money charges.

## Methods
- Input: data/processed/phase10_dhan_weekly_labels_features.csv; use only source-gate-passing rows with binary UP/DOWN labels and numeric features available at the 10:00 IST forecast cutoff.
- Features: registered base features plus six causal Phase 10 features. Exclude labels, future expiry closes/returns, calendar outcomes, source-gate metadata and target-derived fields.
- Prediction protocol: expanding chronological evaluation with a minimum of 104 prior labelled rows; predict one next row at a time, refitting only on prior rows. Use identical evaluation timestamps for all candidates. Median imputation and scaling are fitted within each training fold.
- Fixed candidates: expanding majority; prior-cycle direction; five-session momentum; regularized logistic regression; ExtraTrees; Random Forest; Gradient Boosting; HistGradientBoosting; RBF SVC. Fixed seeds and conservative defaults; no tuning.
- Metrics: accuracy, balanced accuracy, MCC, Brier score, log loss and ROC AUC where defined.
- Outputs: predictions CSV, metrics CSV, JSON summary, chart PNG and Markdown report.
- Reproducibility: fixed random seed, model parameters and feature list written to the summary manifest.

## Critical inference boundary
This is an exploratory family benchmark on the existing 256-cycle sample. The Phase 10 final holdout has already been examined; it is not fresh confirmatory evidence and must not be retuned or relabelled as untouched. The benchmark can shortlist candidates for future prospective evaluation, but cannot certify an edge. A future confirmatory window must accrue after this protocol is frozen.

## Acceptance criteria
- All candidate predictions share the same chronological evaluation rows.
- Every fitted preprocessing step is trained only on prior rows.
- Tests verify source gating, reproducibility and identical prediction counts.
- Report labels results exploratory and keeps the trading gate blocked unless costs and instrument-level fills are independently validated.

## Bounded phases
1. Implement fixed candidates, tests, workflow and artifacts.
2. Run one benchmark on the cached, source-gated dataset.
3. Correct implementation defects only, not model selection based on scores.
4. Publish findings and audit compliance. Stop; no additional tuning or evolutionary search in this phase.

## Known limitations
Small sample, weekly serial dependence, limited Dhan window, missing point-in-time options IV/OI/skew and complete flow/sentiment covariates, and no contract-level P&L/cost validation. Results do not constitute investment advice.


## First benchmark outcome (2026-10-26)

The first successful fixed run evaluated 152 identical expanding-window dates from 2023-11-16 through 2026-10-19, using 256 source-gated weekly cycles and 104 prior labelled rows for each initial fit. The first-run results are available in [report.md](../research/results/phase11/report.md) and [summary.json](../research/results/phase11/summary.json).

| Candidate | Balanced accuracy | Brier | ROC AUC |
|---|---:|---:|---:|
| ExtraTrees | 0.578 | 0.245 | 0.595 |
| Random Forest | 0.573 | 0.247 | 0.585 |
| Histogram Gradient Boosting | 0.554 | 0.262 | 0.559 |
| Logistic regression | 0.546 | 0.260 | 0.531 |
| RBF SVC | 0.532 | 0.254 | 0.504 |
| Gradient Boosting | 0.503 | 0.254 | 0.555 |
| Expanding majority | 0.500 | 0.254 | 0.507 |

These are descriptive exploratory metrics, not evidence of an independent edge. ExtraTrees ranked first, but this is the same reused historical sample and must not be treated as fresh confirmation. The fixed protocol did not include hyperparameter tuning.

A plan-compliance review found that the original plan promised dependence-aware uncertainty reporting but the first implementation omitted it. A paired four-week moving-block bootstrap comparison (ExtraTrees versus majority and Random Forest) has now been added as a bounded reporting correction; it will be validated by CI and is not a new model-selection loop.

**Trading gate remains BLOCKED.** No contract-level historical fills, date-effective Paytm Money charges, bid/ask spread or slippage stress were evaluated. No trading strategy is validated.


## Final CI status (2026-10-26)

Corrected workflow run [40311220819](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40311220819) passed tests, benchmark, artifact upload and persistence. The ExtraTrees–Random Forest balanced-accuracy difference is +0.55 percentage points (paired four-week block-bootstrap 95% interval −6.9 to +8.0 points). This interval crosses zero. Stop Phase 11; no additional tuning is authorized by this phase.
