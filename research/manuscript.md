# NIFTY Weekly Expiry Direction Prediction: Initial Empirical Study

**Run:** 40167611476  
**Status:** Initial pipeline completed; confirmatory research is BLOCKED. No usable trading strategy is validated.

## Abstract

This study tests whether NIFTY 50 spot direction from the 10:00 IST anchor on the first trading session after a prior weekly options expiry to the next weekly expiry close can be predicted from lagged returns, volatility/range features, gaps, simple rules and machine-learning models. The pipeline processed 882,839 in-session minute bars across 2,356 sessions and created 398 candidate labels. In an 80-row chronological holdout, ExtraTrees achieved 57.5% accuracy and 55.9% balanced accuracy; logistic regression achieved 55.0% accuracy and 54.7% balanced accuracy. These are exploratory only: 368 of 402 expiry-date daily closes differ from Yahoo's independent daily close by more than one point; 63 sessions have repeated-close runs longer than 10 minutes, with a maximum run of 239; and the weekly expiry calendar remains a weekday heuristic. Dhan data did not provide a usable intraday cross-check. No contract-level execution prices or date-specific Paytm Money costs were evaluated. The conclusion is that no usable strategy has been established.

## 1. Introduction and research questions

The sole target is the sign of the NIFTY 50 spot return between the 10:00 IST anchor on the first session after the previous weekly expiry and the close of the next weekly expiry. NSE introduced weekly NIFTY 50 options in February 2019, with first expiry on 14 February 2019. Earlier bars are lookback history only. The pre-registered research questions, hypotheses, and gates are in ../docs/RESEARCH_PLAN.md.

## 2. Data and labels

The workflow fetched 19 CSV files from the technovusin/nifty50-historical-data public archive. Basic parsing and OHLC validation produced:

| Quality item | Result |
|---|---:|
| Raw rows | 884,673 |
| Valid in-session minute bars | 882,839 |
| Daily sessions | 2,356 |
| Coverage | 2017-04-03 to 2026-10-23 |
| Duplicate timestamp rows | 0 |
| Invalid OHLC rows removed | 0 |
| Sessions with fewer than 250 bars | 2 |
| Sessions with repeated-close run longer than 10 bars | 63 |
| Maximum repeated-close run | 239 bars |
| Independent daily-close matches | 2,352 |
| Expiry-date closes differing from Yahoo by >1 point | 368 / 402 |

The candidate calendar generated 402 expiry events and 398 labelled cycles: 223 UP and 175 DOWN. Thirty-four cycles involve an inferred calendar/data-gap shift; two were flagged for uncertain low coverage. Zero rows are confirmatory-eligible because the official historical expiry calendar has not been reconciled.

The target is return = expiry close / anchor open - 1. Anchor is the first bar open at or after 10:00 IST, allowing a maximum three-minute delay. Expiry close is the last available close from 15:25–15:29 IST. UP means return > 0; DOWN means return < 0; exact ties are FLAT and excluded from binary fitting.

## 3. Methods

Features were lagged 1/5/10/20-session returns, realised volatility and ranges over 5/10/20 sessions, overnight gap, pre-anchor movement, anchor jump, prior-cycle outcome, prior range position, session gap, month encodings and an expiry-regime flag. Models were expanding-majority, prior-cycle direction, prior-cycle return sign, 5-session momentum sign, regularised logistic regression and constrained ExtraTrees. Development comprised 318 rows and the chronological holdout 80 rows, beginning 2025-04-09. Minimum training history was 104 rows. Logistic regression was selected using development balanced accuracy, with Brier score as tie-breaker. The final holdout was not used for model selection.

## 4. Results

| Candidate | Accuracy | Balanced accuracy | MCC | Brier score |
|---|---:|---:|---:|---:|
| ExtraTrees | 0.575 | 0.559 | 0.131 | 0.249 |
| Logistic regression | 0.550 | 0.547 | 0.095 | 0.256 |
| Expanding majority | 0.463 | 0.500 | 0.000 | 0.261 |
| Prior-cycle direction | 0.450 | 0.447 | -0.106 | Not defined |
| Prior-cycle return sign | 0.450 | 0.447 | -0.106 | Not defined |
| 5-session momentum sign | 0.363 | 0.352 | -0.304 | Not defined |

UP prevalence in the holdout was 46.25%. Logistic regression accuracy was 55.0% (95% Wilson interval approximately 44.1%–65.4%); ExtraTrees accuracy was 57.5% (approximately 46.6%–67.7%). Intervals are broad and overlap. ExtraTrees was strongest on this holdout but was not the development-selected model. Since source and calendar validation failed, all these metrics are descriptive, not confirmatory evidence of predictive edge.

## 5. Independent data validation and discussion

The independent daily close comparison found 368 of 402 expiry-date values differed from Yahoo by more than one index point. Across all matched days, median absolute difference was approximately 7.20 points and the 95th percentile approximately 30.52 points. This may reflect source defects, close-definition alignment, or both; discrepancies must be inspected date by date. Sixty-three sessions have repeated-close runs over ten bars and the maximum is 239 bars. Dhan bars were not available for comparison.

This is a material data-validation failure. A model cannot repair inaccurate prices or incorrect expiry dates; performance rankings can change when labels are corrected. The provisional ExtraTrees score is a hypothesis to retest only after data repair, not a winning signal. No Quantevolve, PySR, TradingAgents, options-IV/OI, FII/DII, global-market model, or contract P&L simulator was run; the experiment registry records these as deferred until the target-data gate passes.

## 6. Strengths and limitations

Strengths: explicit target semantics and timezone; chronological expanding predictions; simple baselines; probability metrics and Wilson intervals; regression tests for timestamps, duplicate handling, anchor-open selection, return sign and frozen-price runs; logs and automated workflow.

Limitations: inferred expiry calendar; material daily-close mismatch; repeated-close anomalies; Dhan cross-check unavailable; no complete official expiry list; no joined historical options/futures prices, India VIX, FII/DII, global-market or point-in-time news features; small regime-dependent sample; no dated brokerage, exchange fees, STT, GST, stamp duty, spread, slippage, lot-size or fill simulation; Pine prototype has not been validated in TradingView.

## 7. Conclusion

**BLOCKED — NO USABLE STRATEGY VALIDATED.** The pipeline completed, but its source data and expiry calendar failed acceptance gates. The apparent 57.5% ExtraTrees holdout accuracy is not evidence of a tradable edge. Do not trade this result. The next required step is to reconcile all expiry dates with official contract history and resolve the 368 daily-close mismatches, then rebuild labels and repeat the analysis. Only after this gate passes should further model discovery proceed. Any future strategy must also pass an untouched holdout, robustness analysis, and contract-level net P&L after verified Paytm Money costs and realistic spread/slippage.

## 8. Future work

1. Obtain official NSE/NSE Indices historical daily closes and a canonical expiry/holiday calendar.
2. Audit each mismatched date and repeated-close run; repair Dhan authentication and compare recent minute bars.
3. Rebuild labels and exclude unresolved expiries.
4. After data validation passes, test India VIX, global overnight returns, breadth, timestamped FII/DII reports and historical option-implied IV/skew/OI when point-in-time coverage exists.
5. Run bounded Quantevolve/PySR searches and TradingAgents-assisted hypothesis generation only after a clean label gate, with multiple-testing controls.
6. Build a contract-aware simulator using date-specific Paytm Money charges, exchange fees, statutory levies, spread, slippage and conservative fill assumptions.
7. Keep an untouched final period and conduct an independent formula/calendar audit before any deployment decision.

## Appendices

- Research plan: ../docs/RESEARCH_PLAN.md
- Data source register: ../docs/DATA_SOURCES.md
- Methodology: METHODOLOGY.md
- Data-quality report: ../data/processed/data_quality_report.json
- Holdout metrics and predictions: results/holdout_metrics.csv and results/holdout_predictions.csv
- Experiment registry: results/experiment_registry.json
- Logs: ../logs/RESEARCH_LOG.md, ../logs/ERROR_LOG.md and ../logs/CONVERSATION_LOG.md


---

# Supplementary Study: Bounded Evolution, Symbolic Regression and Custom Indicator

**Supplement status:** Phase 2 completed computationally on 2026-10-25. This supplement updates the original manuscript's earlier statement that these tracks were deferred. It does not alter the original data-quality acceptance decision.

## Supplementary methods

Using the committed candidate weekly-cycle feature snapshot (398 rows; 318 development and 80 chronological holdout), we ran a bounded local evolutionary feature-rule search (35 generations, population 80, four chronological development folds), PySR symbolic regression (25 iterations, 8 populations, maximum expression size 12), and a fixed-weight custom indicator mirrored in Python. A deterministic role-based review considered quantitative validity, data provenance and execution costs. No live LLM debate, broker integration or orders were run. Exact results and upstream SHAs are preserved in the Phase 2 machine-readable artifacts.

## Supplementary results

| Track | Holdout result | Interpretation |
|---|---|---|
| Logistic reference | Accuracy 56.25%; balanced accuracy 56.29%; MCC 0.125; Brier 0.2506 | Weak exploratory reference |
| QuantEvolve-inspired local evolution | Accuracy 53.75%; balanced accuracy 53.58%; MCC 0.072; Brier 0.2944 | Worse than logistic |
| PySR | Return RMSE 0.014925; R² −0.00124 | Does not improve over constant-mean return prediction on holdout |
| Custom indicator | 38.78% directional accuracy on 49 signalled rows; 61.25% coverage | Rejected in current form |
| TradingAgents | No forecast score | No actual agent debate/forecast executed |
| AstraQuant | No forecast score | No NIFTY signal evaluation performed |

The complete equation table is in [Phase 2 results](results/experimental/experimental_results.json), and the detailed discussion is in [Phase 2 report](phase2_report.md).

## Supplementary conclusion

The evolutionary search underperformed the logistic reference. PySR's negative held-out R² and the custom indicator's poor directional accuracy do not support promotion. The experiment workflow and unit tests completed successfully, but this is a computational completion only. The original critical blockers remain: heuristic expiry dates, 368 of 402 candidate expiry closes differing from the independent daily-close source by more than one point, unavailable Dhan cross-check, and no contract-level net P&L including date-effective Paytm Money charges, spread and slippage. Therefore, **no usable or validated trading strategy is established**.
