# BUP-01 C3-X Exploratory Prediction Results

**Status:** EXPLORATORY COMPLETE — NOT CONFIRMATORY  
**Generated:** 2026-11-01T18:25:20.048525+00:00  
**Plan:** v1.4

## Sample and safeguards

- C1 target-coverage cycles: 258
- Cycles after features, available structural-event exclusions and registered 47/94% coverage: 252
- Stock-cycle rows: 12560; member symbols: 62
- First holdout anchor: 2025-11-06; holdout cycles: 51
- Stock models use 104 prior eligible cycles and refit every 4 cycles.
- Dhan requests this run: 1095; encrypted cache hit: False.
- Raw bars and plaintext constituent panel were not published.

## Stock models — chronological holdout

| Model | Rows | Accuracy | Balanced accuracy | MCC | ROC-AUC | Brier (uncalibrated) |
|---|---:|---:|---:|---:|---:|---:|
| ExtraTreesClassifier | 2543 | 0.4829 | 0.4910 | -0.0181 | 0.4850 | 0.2514 |
| LogisticRegression | 2543 | 0.4959 | 0.5055 | 0.0112 | 0.5099 | 0.2511 |
| five_session_momentum_sign | 2543 | 0.5151 | 0.5097 | 0.0193 | 0.5097 | 0.4849 |

## NIFTY direction from OOF constituent signals — chronological holdout

| Model | Cycles | Accuracy | Balanced accuracy | MCC | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| OOF constituent-signal logistic meta-model | 51 | 0.5098 | 0.5345 | 0.0679 | 0.4868 |
| Constituent breadth baseline | 51 | 0.4314 | 0.4827 | -0.0366 | 0.4457 |
| Previous eligible-cycle direction | 51 | 0.4902 | 0.4548 | -0.0905 | 0.4548 |

## Paired uncertainty

- Meta minus lag-direction accuracy: 0.019607843137254888
- Four-cycle moving-block bootstrap 95% interval: [-0.25490196078431376, 0.2549019607843137]
- Replicates: 2000; seed: 20261031.

## Interpretation and limitations

These findings are exploratory only. They do not pass C1 corporate-action review, C2 confirmatory panel validation or C5 trading execution. The broad candidate event catalogue is not fully reconciled. Model scores are uncalibrated. Do not treat the forecasts as live trading signals or a profitability claim.

Machine-readable metrics: EXPLORATORY_RESULTS.json. Cycle-level NIFTY holdout predictions: EXPLORATORY_NIFTY_HOLDOUT.csv.
