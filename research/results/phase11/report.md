# Phase 11 — Diverse Model-Family Benchmark

- Status: **EXPLORATORY_ONLY_NOT_CONFIRMATORY**
- Source-gated rows: 256
- Expanding-window predictions per candidate: 152
- Evaluation dates: 2023-11-16 to 2026-10-19
- Candidates: expanding majority, prior-cycle direction, 5-session momentum, logistic regression, ExtraTrees, Random Forest, Gradient Boosting, Histogram Gradient Boosting, RBF SVC.

## Results

| Candidate | N | Accuracy | Balanced accuracy | MCC | Brier | Log loss | ROC AUC |
|---|---:|---:|---:|---:|---:|---:|---:|
| extra_trees | 152 | 0.579 | 0.578 | 0.157 | 0.245 | 0.684 | 0.595 |
| random_forest | 152 | 0.572 | 0.573 | 0.146 | 0.247 | 0.688 | 0.585 |
| hist_gradient_boosting | 152 | 0.553 | 0.554 | 0.111 | 0.262 | 0.725 | 0.559 |
| logistic | 152 | 0.546 | 0.546 | 0.092 | 0.260 | 0.718 | 0.531 |
| rbf_svc | 152 | 0.526 | 0.532 | 0.106 | 0.254 | 0.702 | 0.504 |
| gradient_boosting | 152 | 0.500 | 0.503 | 0.006 | 0.254 | 0.703 | 0.555 |
| expanding_majority | 152 | 0.493 | 0.500 | 0.000 | 0.254 | 0.702 | 0.507 |
| prior_cycle | 152 | 0.474 | 0.474 | -0.053 | 0.526 | 7.271 | 0.474 |
| momentum_5d | 152 | 0.467 | 0.467 | -0.067 | 0.533 | 7.362 | 0.467 |

## Interpretation

This is exploratory screening, not confirmatory evidence. The Phase 10 holdout has already been inspected; these results must not be described as a fresh holdout or used for repeated tuning. A top rank does not establish significance or profitability.

## Trading gate

BLOCKED: no contract-level options/futures fills, date-effective Paytm Money costs, spreads and slippage stress.

## Reproducibility

See summary.json, metrics.csv, predictions_expanding_window.csv and balanced_accuracy.png. Preprocessing is fitted inside each expanding training fold.
