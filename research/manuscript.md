# NIFTY Weekly Expiry Direction Prediction: A Leakage-Safe, Cost-Aware Research Protocol

**Status:** Protocol and repository scaffold; final empirical results pending automated data and test run.

## Abstract
This study aims to predict the sign of the NIFTY 50 spot-index return from 10:00 IST on the next trading day after a prior weekly options expiry to the close of the subsequent weekly expiry. The primary contribution is an auditable label/calendar specification and a bounded walk-forward research design that compares simple rules and machine-learning candidates without look-ahead, while reporting uncertainty and distinguishing directional accuracy from executable net returns. No empirical performance claim is made in this protocol manuscript; result tables will be populated only from reproducible workflow artifacts.

## 1. Introduction
Weekly expiry outcomes are influenced by accumulated market trend, overnight repricing, volatility, event risk and the changing expiry calendar. High flexibility in technical-indicator and model search can overfit a small number of weekly observations. Therefore this research fixes the target, uses a historical expiry calendar, establishes simple baselines, and reserves a time-ordered holdout.

## 2. Research questions and hypotheses
See docs/RESEARCH_PLAN.md. The central null is that no tested candidate has a meaningful out-of-sample improvement over the best simple baseline. An additional and stricter null is that predictive advantage does not translate into a net-positive executable strategy after verified costs.

## 3. Data
Primary candidate: NIFTY 50 1-minute spot OHLC from a public GitHub data archive, subject to source validation. Official NSE index prices, expiry dates, holiday shifts and India VIX are preferred validation sources. Options, futures, global benchmark, breadth, FII/DII and timestamped news are secondary and may be included only if quality and point-in-time availability pass. Source completeness, licences and known quirks are reported in docs/DATA_SOURCES.md.

## 4. Methods
The label is UP when the final expiry close is greater than the 10:00 IST anchor open after the preceding expiry, DOWN when lower, and FLAT when equal. Features include lagged returns, realised volatility, ranges, overnight gap, pre-10:00 morning return, prior-cycle return and calendar regime. All features and model fitting are causal. Evaluation uses expanding walk-forward predictions and a locked contiguous holdout; baseline performance, probability quality, confidence intervals, regime splits, multiple-testing discipline and a deterministic audit are mandatory. Any trade simulation requires contract-level prices, time-sensitive charges and slippage.

## 5. Results
**Pending.** This section must be replaced or extended by saved workflow outputs. No backtest has yet been run by this repository scaffold. Do not invent sample sizes, accuracy, p-values, profitability or a winning strategy.

Planned tables:
- Table 1: target/feature coverage and exclusions by year/expiry regime.
- Table 2: prevalence and simple baseline metrics.
- Table 3: walk-forward and final-holdout metrics with confidence intervals.
- Table 4: paired baseline comparison, calibration and abstention.
- Table 5: robustness by volatility regime, calendar regime and costs.
- Table 6: cost components and net strategy performance when executable inputs exist.

Planned figures: yearly label prevalence, weekly return distribution, model-versus-baseline balanced accuracy and Brier score, calibration plot, regime performance and after-cost equity/drawdown curves only if actual instrument results exist.

## 6. Inferences and discussion
To be written from saved results. Predictive significance, probability calibration, regime stability and tradability are separate claims. Any performance not exceeding the best baseline on unseen data must be described as no demonstrated edge. Failure to obtain a complete expiry calendar or verified instrument-cost data will be reported as a limitation, not evidence for profitability.

## 7. Strengths and limitations
Strengths include explicit event/time semantics, causal features, chronological validation, comparison to simple baselines, an experiment registry, data-quality logs and costs separated from direction classification. Limitations include a relatively small weekly sample, regime changes, source/licensing dependence on third-party minute data, possible gaps in FII/DII/options features, ambiguity around execution timing, and data-mining risk when many indicators are tried.

## 8. Conclusion
No usable strategy is certified at protocol-writing time. The final conclusion will be based on pre-registered acceptance gates and will state validated evidence, a negative finding, or a clear data/access blocker.

## 9. Future work
After the primary gate, consider (1) verified options-implied volatility/skew and expiry gamma exposure, (2) point-in-time global overnight and event-risk features, (3) regime-conditional calibration and abstention, (4) bounded symbolic strategy discovery, and (5) a real-instrument, contract-aware simulator. Do not proceed to deployment solely because classification accuracy appears high.

## Appendices
- A. Data dictionary and source lineage: docs/DATA_SOURCES.md.
- B. Mathematical and leakage audit checklist: research/METHODOLOGY.md.
- C. Experiment/error/status/conversation logs: logs/.
- D. Software and external-source review: docs/LITERATURE_REVIEW.md.
