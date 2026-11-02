# BUP-01 C3 Stock Model Results

**Status:** EXPLORATORY COMPLETE — NOT CONFIRMATORY

- C2 manifest: `693365a0981d3354a87d8639c1e0ee74022c530b017024d8d3712e91b9014c19`
- Eligible cycles: 260; OOF forecast cycles: 156; holdout starts at cycle 208 (the final 20% of eligible cycles).
- OOF stock rows: 7609 across 57 symbols.
- 104-cycle warm-up; model refit every four cycles; complete cycles remain indivisible.
- Per-stock OOF forecasts encrypted; raw prices and feature values not published.

## Stock direction metrics

| Split | Model | Rows | Accuracy | Balanced accuracy | MCC | ROC-AUC | Brier | Log loss |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| development | momentum | 5026 | 0.4739 | 0.4714 | -0.0573 | 0.4714 | 0.2551 | 0.7034 |
| development | symbol_frequency | 5026 | 0.5143 | 0.4950 | -0.0143 | 0.4945 | 0.2510 | 0.6952 |
| development | logistic | 5026 | 0.5092 | 0.5066 | 0.0132 | 0.5121 | 0.2511 | 0.6956 |
| development | extra_trees | 5026 | 0.5034 | 0.5021 | 0.0042 | 0.5002 | 0.2514 | 0.6960 |
| development | hist_gradient_boosting | 5026 | 0.4986 | 0.4888 | -0.0240 | 0.4925 | 0.2557 | 0.7051 |
| untouched_holdout | momentum | 2583 | 0.5052 | 0.5077 | 0.0153 | 0.5077 | 0.2520 | 0.6971 |
| untouched_holdout | symbol_frequency | 2583 | 0.4638 | 0.5096 | 0.0275 | 0.5213 | 0.2559 | 0.7052 |
| untouched_holdout | logistic | 2583 | 0.4812 | 0.4897 | -0.0206 | 0.4853 | 0.2529 | 0.6991 |
| untouched_holdout | extra_trees | 2583 | 0.4812 | 0.4849 | -0.0300 | 0.4801 | 0.2519 | 0.6970 |
| untouched_holdout | hist_gradient_boosting | 2583 | 0.4526 | 0.4817 | -0.0410 | 0.4770 | 0.2582 | 0.7097 |

## Cycle-macro performance

| Split | Cycles | Momentum accuracy | Logistic accuracy | ExtraTrees accuracy | HistGradientBoosting accuracy | Ridge return rank IC |
|---|---:|---:|---:|---:|---:|---:|
| development | 104 | 0.4739 | 0.5093 | 0.5034 | 0.4989 | 0.0202 |
| untouched_holdout | 52 | 0.5052 | 0.4815 | 0.4814 | 0.4527 | -0.0184 |

## Paired holdout uncertainty

- Logistic minus momentum mean cycle-accuracy difference: -0.023709772370486652
- Four-cycle moving-block bootstrap 95% interval: [-0.10381129807692308, 0.04507520604395596]
- Replicates: 2,000; seed: 20261031.

Stock-level results are exploratory. C4 must test whether OOF stock forecasts improve NIFTY direction on the same holdout. No trading profitability is inferred.
