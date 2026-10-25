# Phase 2 Experimental Report — Bounded Completion

**Run:** [40171572720](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40171572720)  
**Generated:** 2026-10-25  
**Workflow status:** SUCCESS — PySR ran, tests passed, results persisted.  
**Research status:** EXPLORATORY ONLY; no strategy promoted.

## Research question

On the current candidate weekly-cycle dataset, do bounded evolutionary feature search, symbolic regression, a fixed-weight expiry-pressure indicator, or agent-assisted review establish better out-of-sample directional or return prediction than a simple logistic reference?

## Sample and design

- 398 candidate cycles; 318 development rows and 80 chronological held-out rows.
- Target: expiry-close return relative to the next-session 10:00 anchor.
- The candidate expiry calendar is heuristic and not verified. Independent daily close comparison failed (368/402 candidate expiry-date closes differ by more than one point).
- This is a single exploratory holdout, not independent confirmation. The feature snapshot is reused for reproducibility; evolutionary search ran 35 generations with population 80 and four chronological development folds.
- PySR was run with 25 iterations, 8 populations and max expression size 12.
- No executable instrument, contract-level fills, Paytm Money dated costs, spread, slippage, or net P&L was evaluated.

## Results

| Track | Held-out result | Interpretation |
|---|---|---|
| Logistic baseline | Accuracy 56.25%; balanced accuracy 56.29%; MCC 0.125; Brier 0.251 | Reference only; no confirmed edge |
| QuantEvolve-inspired bounded local evolution | Accuracy 53.75%; balanced accuracy 53.58%; MCC 0.072; Brier 0.294 | Underperformed logistic; no promotion |
| PySR symbolic regression | Return RMSE 0.014925; return R² −0.00124 | No out-of-sample explanatory/predictive improvement over a constant-return reference |
| Custom indicator Python mirror | Directional accuracy 38.78% on 49 signalled rows; coverage 61.25% | Poor direction on this sample; reject current weights/threshold |
| TradingAgents | No forecast score | Upstream cloned, but live multi-agent debate not run; deterministic risk-review roles only |
| AstraQuant | No forecast score | Upstream cloned/revision recorded; not evaluated as a NIFTY signal or execution model |

PySR's simple constant equation was approximately `0.0028298`; more complex expressions did not produce positive held-out R². The symbolic feature indices are runner-generated and should not be treated as a human-interpretable trading rule without the exact feature map and a new validation study.

Machine-readable details and all candidate equations are in [experimental_results.json](results/experimental/experimental_results.json). Exact upstream revisions are in [upstream_revisions.md](results/upstream_revisions.md).

## Statistical interpretation

The logistic model is the strongest of the completed directional tracks reported here, but 56.25% accuracy on 80 observations is not enough to establish a robust edge. The local evolutionary search has worse holdout accuracy and probability calibration (Brier 0.294 versus 0.251). PySR's negative held-out R² means it did not beat the held-out constant-mean benchmark for continuous returns. The indicator's signalled subset performs poorly. No result justifies profitability claims.

## Decision

**Phase 2 bounded experiment execution is complete; strategy acceptance is BLOCKED. Do not trade these signals.**

This distinction matters: the compute/test workflow completed successfully, but the research's data-quality and execution acceptance gates did not pass. Per the bounded plan, do not repeatedly tune against this same holdout.

## Corrections and audit trail

- The first run skipped PySR because of a workflow condition. The workflow was fixed to attempt installation; the latest run successfully installed PySR and completed symbolic regression.
- The workflow now reuses the committed feature snapshot by default; full data rebuild remains an explicit manual input.
- Core and experimental unit tests passed in run 40171572720.
- Failures and corrections are recorded in [ERROR_LOG.md](../logs/ERROR_LOG.md); execution status is recorded in [RESEARCH_LOG.md](../logs/RESEARCH_LOG.md).
- The Pine indicator is a prototype. TradingView Pine compilation was not verified in CI.
- TradingAgents did not run an actual LLM debate, and AstraQuant was not evaluated as a predictor.

## Strengths and limitations

**Strengths:** chronological holdout; logistic reference; balanced accuracy, MCC and Brier for classification; RMSE and R² for regression; bounded search budget; reproducible JSON and upstream revision records; automated tests and explicit no-promotion decision.

**Limitations:** small single holdout; heuristic expiry calendar; unresolved price-source disagreement and repeated-close anomalies; Dhan cross-check unavailable; no independent official-price repair; no regime-stability or multiple-testing-adjusted confirmation; no verified options/futures instrument prices, fills, date-effective Paytm Money charges, exchange/statutory fees, bid-ask spread or slippage; Pine compilation not checked; no live TradingAgents prediction.

## Future work and acceptance gates

1. Reconcile historical weekly expiry dates and all material close mismatches against official NSE/NSE Indices data or a trusted independent vendor.
2. Rebuild labels/features only after the source gate passes, then preregister a new untouched evaluation period.
3. If the clean-label baseline shows stable signal, test point-in-time global market returns, India VIX, FII/DII, breadth and options IV/OI/skew where reliable timestamps and coverage exist.
4. Define an executable futures/options instrument and run a costed fill simulation using date-specific Paytm Money brokerage, exchange charges, statutory levies, spread and slippage.
5. Require robust net expectancy, uncertainty intervals and regime stability before considering deployment.

Until these gates pass, the appropriate conclusion remains **no validated or usable trading strategy**.
