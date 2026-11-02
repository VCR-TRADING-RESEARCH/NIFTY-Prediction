> **Superseded on 2026-11-03:** The following metrics were generated from a 258-cycle C2 panel that omitted two verified shifted expiries. Keep them as historical evidence only; do not use them as current performance estimates. A corrected C2 panel and C3 rerun are required.

# BUP-01 C3 Stock Model Results

**Status:** SUPERSEDED — EXPIRY-CALENDAR CORRECTION REQUIRES RERUN

- C2 manifest: `9d263e441f09c70693e30f1541440ac6b249c5293da61faceb0af729d699c305`
- Eligible cycles: 258; OOF forecast cycles: 154; holdout starts at cycle 206.
- OOF stock rows: 7512 across 57 symbols.
- 104-cycle warm-up; model refit every four cycles; complete cycles remain indivisible.
- Per-stock OOF forecasts encrypted; raw prices and feature values not published.

## Stock direction metrics

| Split | Model | Rows | Accuracy | Balanced accuracy | MCC | ROC-AUC | Brier | Log loss |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| development | momentum | 4929 | 0.4753 | 0.4732 | -0.0536 | 0.4732 | 0.2550 | 0.7031 |
| development | symbol_frequency | 4929 | 0.5141 | 0.4950 | -0.0144 | 0.4946 | 0.2512 | 0.6957 |
| development | logistic | 4929 | 0.5104 | 0.5079 | 0.0159 | 0.5121 | 0.2511 | 0.6957 |
| development | extra_trees | 4929 | 0.4971 | 0.4958 | -0.0084 | 0.4973 | 0.2515 | 0.6961 |
| development | hist_gradient_boosting | 4929 | 0.4971 | 0.4873 | -0.0273 | 0.4875 | 0.2567 | 0.7072 |
| untouched_holdout | momentum | 2583 | 0.5052 | 0.5077 | 0.0153 | 0.5077 | 0.2520 | 0.6971 |
| untouched_holdout | symbol_frequency | 2583 | 0.4592 | 0.5075 | 0.0229 | 0.5199 | 0.2590 | 0.7133 |
| untouched_holdout | logistic | 2583 | 0.4812 | 0.4903 | -0.0194 | 0.4853 | 0.2528 | 0.6989 |
| untouched_holdout | extra_trees | 2583 | 0.4851 | 0.4921 | -0.0157 | 0.4792 | 0.2520 | 0.6971 |
| untouched_holdout | hist_gradient_boosting | 2583 | 0.4669 | 0.4894 | -0.0224 | 0.4883 | 0.2604 | 0.7147 |

## Cycle-macro performance

| Split | Cycles | Momentum accuracy | Logistic accuracy | ExtraTrees accuracy | HistGradientBoosting accuracy | Ridge return rank IC |
|---|---:|---:|---:|---:|---:|---:|
| development | 102 | 0.4752 | 0.5106 | 0.4971 | 0.4973 | 0.0261 |
| untouched_holdout | 52 | 0.5052 | 0.4815 | 0.4852 | 0.4668 | -0.0193 |

## Paired holdout uncertainty

- Logistic minus momentum mean cycle-accuracy difference: -0.023725470957613806
- Four-cycle moving-block bootstrap 95% interval: [-0.10037786989795919, 0.04285640698587118]
- Replicates: 2,000; seed: 20261031.

Stock-level results are exploratory. C4 must test whether OOF stock forecasts improve NIFTY direction on the same holdout. No trading profitability is inferred.
