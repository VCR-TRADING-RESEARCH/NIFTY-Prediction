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


## Phase 3 official-source reconciliation update (25 October 2026)

### Methods and source-audit outcome
The third phase attempted to reconcile the candidate minute archive against the official NSE NIFTY 50 daily index history and NSE derivative contract bhavcopies. The completed run returned 1,913 official daily records and matched 1,901 of 1,901 comparison sessions. The daily-close comparison exceeded the pre-registered one-index-point tolerance on 1,717 sessions; the median absolute difference was 8.25 points, the 95th percentile was 32.45 points, and the maximum was 200.7 points. The independent audit therefore remains blocked. These differences are not silently corrected and the tolerance has not been widened.

| Phase 3 metric | Result | Interpretation |
|---|---:|---|
| Official daily close rows | 1,913 | Official series retrieved |
| Sessions compared | 1,901 / 1,901 | No missing official close in the matched comparison |
| Minute/session close differences >1 index point | 1,717 / 1,901 (90.3%) | Fails the registered close-agreement gate |
| Median absolute close difference | 8.25 points | Material discrepancy |
| 95th percentile absolute close difference | 32.45 points | Large upper-tail errors |
| Maximum absolute close difference | 200.7 points | The candidate close series needs investigation |
| Candidate weekly expiries checked | 402 | Calendar remains provisional |
| Confirmations in run 40174991974 | 338 / 402 (84.1%) | 26 unverified and 38 source-validation errors |

### Interpretation and limitations
The current minute archive is not accepted as ground truth merely because basic OHLC/timestamp validation passes. Its publisher documents missing bars, frozen-price stretches and partial/special sessions. The largest observed close mismatch includes a day with a 239-bar unchanged-close run, but high close differences also occur on sessions without such a long run; freezing alone is insufficient to explain the pattern. Official closing-index methodology and underlying minute source quality therefore remain competing explanations that require direct open/high/low and alternative-source comparison.

The expiry result is also inconclusive. The first strict-parser run used a source downloader whose diagnostics preserved only exception types, which is not adequate for a defensible audit. The next bounded pass warms the NSE archive session, captures sanitized validation reasons, checks the nearby prior session only when no expiry is found on the nominal day, and writes yearly status summaries. These corrections do not convert a source error into a confirmed expiry.

### Decision
Phase 1 remains **BLOCKED**. All previously reported model metrics remain exploratory; 398 heuristic labels and the 318/80 chronological split are not confirmatory evidence. No executable strategy is selected. The next stage compares official daily open/high/low to diagnose the mismatch and validates a second independent intraday archive for the 10:00 anchor, while preserving the existing close-tolerance gate. Only after the label/source gates pass should a specified futures/options instrument be backtested with date-effective Paytm Money costs, spread, slippage and conservative fills.


## Second-source diagnostics added (25 October 2026)

The source gate is still blocked. The current official-vs-primary report compared 1,901 sessions; 1,717 close differences exceeded one point, with median absolute difference 8.25, P95 32.45 and maximum 200.7. Official open/high/low mismatches above one point were 587, 197 and 185. The distribution warrants a separate timestamp/aggregation examination rather than changing the one-point tolerance.

An independent public 1-minute NIFTY 50 dataset is now included as a diagnostic comparator. It publishes annual files for 2019-2025 and monthly files in 2026, states timestamps are IST, and describes known remaining missing/frozen/special-session bars. Each session is aggregated from bars timestamped 09:15-15:29 IST and compared to official daily OHLC and the current archive. This third-party archive is not official ground truth; the audit is intended to test whether the discrepancy is specific to the current candidate source. Results await the latest automated run.


## Audit correction and additional source plan (25 October 2026)

The previous Phase 3 “alternative” minute dataset is not independent. The main data-fetch script reads technovusin/nifty50-historical-data, and the purported cross-check reads the same repository. Across 1,901 overlapping daily closes, the values matched exactly; this documents consistency of a duplicate read, not independent source validation. No inference about reliability may be drawn from that match.

Inspection of the Phase 3 expiry artifact also identified a date-parsing error. On UDiFF records with ISO strings, applying a generic day-first fallback interpreted dates such as 2024-12-04 as 2024-04-12. A parser that handles YYYYMMDD and ISO year-first dates before legacy day-first strings has been added with regression tests. The previous 340/402 expiry confirmation remains the latest valid result until the corrected full workflow finishes.

A second published dataset from sandeepkapri/Nifty50-Minute-Data is being compared with official NSE daily OHLC for the overlapping period 2019-02-01 to 2024-03-27. It is hosted in a separate repository, but the underlying data provider is not established by its README; therefore agreement will be diagnostic evidence only, not proof of independent vendor lineage. It cannot validate dates after March 2024. Phase 1 remains blocked and all model results remain exploratory.
