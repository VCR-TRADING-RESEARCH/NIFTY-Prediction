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


## Preliminary second-published-dataset comparison (25 October 2026)

The separately published sandeepkapri/Nifty50-Minute-Data dataset was successfully downloaded and aggregated for the overlapping period 1 February 2019 through 27 March 2024. Using the last minute bar in the 09:15-15:29 IST window, 1,271 sessions overlapped the latest available official daily snapshot. Its closing value differed from the official daily close by more than one point on 1,182 sessions; median absolute difference was 7.55 points, P95 27.20 and maximum 161.55 points. The primary candidate series on the same overlapping sessions differed on 1,176 sessions, median 7.65 and P95 26.985. 574 of 1,267 compared daily closes matched exactly between the two published minute datasets.

These comparisons are preliminary diagnostic evidence only. The official-source reconciliation did not run in that particular job because unit tests failed first, so the comparison used the last committed official daily snapshot. The separate dataset is a different repository, but its underlying provider lineage is not independently established, and its coverage ends in March 2024. It does not validate the full 2019-2026 range and does not resolve the source gate.


## Updated source reconciliation and target construction (25 October 2026)
NSE derivatives bhavcopy reconciliation verified all 402 candidate weekly-expiry records with no source errors. The primary public minute archive's daily close differs from official NSE daily close by more than one index point in 1,717 of 1,901 sessions (median absolute difference 8.25 points; 95th percentile 32.45; maximum 200.7). A separately published minute dataset overlaps for 1,271 sessions through 27 March 2024 and has 1,182 close mismatches over one point; its underlying provider lineage is not independently verified.

Target construction now uses the official NSE daily close on the verified expiry trade date. Lagged daily closes also use official NSE values where available, while the archive close is retained for audit. The 10:00 anchor still uses the first eligible minute-bar open from the primary public archive and is not independently validated. Results remain exploratory until the anchor source and instrument-level execution costs are validated.


## 9. Corrected official-source audit and final interpretation (25 October 2026)

### Research question and methods
The final bounded audit tested whether original minute-archive daily closes match official NSE NIFTY 50 daily closes within the pre-specified one-point tolerance, and whether candidate expiry dates have official derivatives evidence. To avoid circular validation, the audit compared preserved `session_close_archive` values from the original minute bars directly with official `official_close`, not a cross-check table whose close values had already been replaced by official closes.

### Results
| Audit measure | Result |
|---|---:|
| Candidate expiry dates checked | 402 |
| Candidate expiry dates officially verified | 402 / 402 |
| Unverified expiry dates / source errors | 0 / 0 |
| Official daily records retrieved | 1,913 |
| Preserved archive sessions compared | 1,903 |
| Close differences above one point | 1,719 / 1,903 (90.3%) |
| Median absolute close difference | 8.25 points |
| 95th percentile absolute close difference | 32.435 points |
| Maximum absolute close difference | 200.7 points |

The corrected audit invalidates an earlier apparent PASS that reported zero close mismatches. That result was circular because the comparison table used official-close-overridden values. The separate audit's non-zero discrepancy result is authoritative. The cause of the differences is not fully identified; source integrity, session aggregation, timestamp alignment or other processing issues remain possible.

### Updated model result (exploratory only)
The official-close/verified-expiry pipeline (run 40181159630) produced 398 labelled cycles, with 318 development observations and 80 chronological holdout observations. ExtraTrees was selected on development data. Holdout accuracy was 61.25%, balanced accuracy 60.18%, MCC 0.213, Brier score 0.246, log loss 0.686 and ROC AUC 0.574. The approximate 95% Wilson interval for accuracy is 50.3%–71.2%. This is not confirmatory evidence: the 10:00 anchor still comes from the unvalidated minute archive, and the preserved archive daily closes fail independent comparison. These metrics must not be interpreted as a proven predictive edge.

### Statistical interpretation
The holdout has only 80 observations and a wide uncertainty interval. Accuracy modestly exceeds 50%, while ROC AUC is 0.574 and probability scores are weak. Evidence is insufficient to distinguish a stable economic edge from sampling variability, regime effects or residual label/source errors. Recorded evolutionary and symbolic-regression experiments did not improve on the simpler baseline. Further searching now would compound multiple-testing risk without fixing the data defect.

### Strengths and limitations
Strengths include chronological holdout evaluation, explicit target semantics, official expiry-date verification, preservation of original archive closes, a fixed one-point mismatch tolerance, automated tests, and correction logs that invalidate the false PASS rather than conceal it.

Limitations include 1,719/1,903 close discrepancies above tolerance; an unvalidated 10:00 anchor; no verified contract-level fills; no historical bid-ask spread/slippage series; no date-effective Paytm Money brokerage, exchange fees, statutory levies or GST accounting; no net-of-cost futures/options backtest; a small holdout; and incomplete point-in-time coverage for options IV/OI, FII/DII, global-market, news and regime features. A spot-index classification score is not an executable trading return.

### Conclusion and stopping decision
**Final bounded result: BLOCKED — NO USABLE TRADING STRATEGY VALIDATED.** The official expiry calendar is verified for all 402 candidate dates, but the price-source gate fails and the anchor remains provisional. Do not trade these model outputs. Pause at the pre-defined data-quality gate rather than run further model searches on potentially incorrect labels. No profitability or cost-adjusted expectancy claim is made.

### Future direction
If resumed, the next justified step is a bounded source-diagnosis phase: inspect date-level/year-level mismatch patterns; test session aggregation, timezone and close selection; independently validate 10:00 minute prices using a reliable free source first and Dhan if access can be repaired; preserve immutable raw-source values; rebuild labels and re-register the holdout. Only after source and anchor gates pass should contract-level simulation include historical futures/options prices, date-effective Paytm Money charges, bid-ask spread, slippage, lot sizing and conservative fills.


## Additional historical anchor audit (26 October 2026)

### Data and timestamp audit

A corrected comparison between the primary public NIFTY minute archive and a separately published minute dataset covered 1 February 2019 through 27 March 2024. The first attempt reported no exact timestamp matches; review found a comparison bug because the primary timestamps were timezone-aware while the secondary timestamps were timezone-naive local IST. That match-count statistic was invalidated. Both sources were normalized to Asia/Kolkata before rerunning and regression tests were added.

| Anchor diagnostic | Result |
|---|---:|
| Primary-source anchor sessions | 1,269 |
| Secondary-source anchor sessions | 1,271 |
| Sessions with both anchors | 1,269 |
| Exact timestamps after IST normalization | 1,269 / 1,269 |
| Median absolute anchor-open difference | 0.05 points |
| 95th percentile absolute difference | 1.00 point |
| Maximum absolute difference | 6.70 points |
| Sessions with difference over 1 point | 62 / 1,269 |
| Weekly cycles with overlapping alternate anchor | 265 |
| Weekly UP/DOWN labels changed after alternate-anchor substitution | 0 / 265 |

### Interpretation

The alternate-anchor test holds the recorded expiry closing price constant and recalculates the cycle return using the other archive's 10:00 open. No direction label changed in the 265 overlapping weekly cycles. This reduces concern that small anchor-price discrepancies alone are driving the direction labels within this overlap. It does not establish that either minute archive is a reliable ground-truth source: the secondary data's original provider lineage is not independently verified, the comparison ends in March 2024, and 62 daily anchor opens differ by more than one index point. Other intraday OHLC features may remain affected.

The daily-close source mismatch gate therefore remains **BLOCKED**. No model selection or trading acceptance is inferred from this diagnostic. A Dhan historical anchor-source audit is the next evidence-gathering step; it can corroborate only its available five-year window and does not remove the requirement for complete source provenance, re-built labels and a new locked holdout.

<!-- PHASE10_RESULTS_START -->
## Phase 10 execution status

**Status:** BLOCKED_WORKFLOW_FAILURE. The automated Dhan-backed rebuild did not produce a successful summary in run 40283691388. This is a blocked execution result, not model performance evidence. See logs/ERROR_LOG.md and docs/PHASE_10_VERIFIED_DATASET.md.
<!-- PHASE10_RESULTS_END -->
