# C3 Status

**Phase:** C3 pooled stock models and walk-forward evaluation  
**Workflow:** [41401986460 — attempt 2 SUCCESS](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41401986460)  
**Status:** EXPLORATORY COMPLETE — NOT CONFIRMATORY  
**C2:** PASS — 258/258 index targets and 12,807 stock-cycle rows  
**C1:** ACCEPTED WITH LIMITATIONS FOR PROGRESSION; historical action/identity review remains incomplete  
**C4 confirmatory:** GATED by C1  
**Trading:** NOT VALIDATED

## Accepted exploratory output

- 7,512 encrypted out-of-fold stock forecasts, 154 forecast cycles and 57 symbols.
- 52 untouched holdout cycles, 2,583 stock-cycle observations.
- Holdout accuracy: momentum 50.52%; logistic 48.12%; ExtraTrees 48.51%; HistGradientBoosting 46.69%.
- Logistic minus momentum cycle-macro accuracy: −2.37 percentage points; four-cycle moving-block bootstrap 95% interval: −10.04 to +4.29 percentage points.
- Mean holdout ridge return rank IC: −0.0193.
- No candidate model selected; no predictive edge established.

## Limitations

The 292 identity-flagged observations and 3 action-crossing observations were excluded from the primary experiment. C2 reports 92 missing predictor observations handled by fold-local imputation and 19 flat stock labels excluded from UP/DOWN fitting. The larger unresolved C1 corporate-action catalogue is not certified. This phase did not test options, global markets, VIX, FII/DII, news, execution, Paytm Money charges, slippage or P&L.

The separate plan-v1.4 C3-X phase already reports an exploratory NIFTY meta-model test (50.98% holdout accuracy, 53.45% balanced accuracy, ROC-AUC 48.68%, 51 cycles). Its bootstrap interval is very wide and includes zero. It remains a separate sample/method result and must not be combined with the new C3 holdout.

## Files

- [Machine-readable results](C3_RESULTS.json)
- [Results report](C3_RESULTS.md)
- [Model specification](C3_MODEL_SPEC.md)

No C3 result authorises a live signal or trading strategy.
