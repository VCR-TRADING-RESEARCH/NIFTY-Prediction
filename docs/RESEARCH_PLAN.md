# Pre-registered Research Plan

Current version: 1.2 (26 October 2026; versioned addenda preserve earlier plan history)
Original baseline: Version 1.0 registered 2026-10-25.
Version 1.1 method-design amendment is documented on the Phase 9 method branch; Version 1.2 registers an authenticated-Dhan dataset rebuild with a fixed method comparison and one locked chronological holdout. The public minute-archive mismatch remains documented, but Phase 10 uses official NSE daily OHLC plus Dhan intraday anchors in the available five-year window. The model result remains exploratory and trading acceptance is separate. See [Version 1.2 addendum](RESEARCH_PLAN_V1_2_DHAN_DATASET_ADDENDUM.md), [Phase 10 plan](PHASE_10_VERIFIED_DATASET.md), research/manuscript.md and logs/RESEARCH_LOG.md.

## 1. Title and scope
NIFTY Weekly Expiry Direction Prediction: estimate whether the NIFTY 50 spot-index close at weekly options expiry is greater than or less than its value at 10:00 IST on the next trading day after the preceding weekly expiry. This is a binary direction task; magnitude forecasting is secondary and only used for risk/cost analysis.

## 2. Formal target
Weekly NIFTY 50 options were introduced for trading from 11 February 2019, with the first weekly expiry on 14 February 2019 (NSE circular FAOP39894). Therefore 2017–2018 minute history is eligible only as a pre-sample feature-lookback window; it must not be used to fabricate weekly-option expiry labels.

For each consecutive pair of actual weekly expiry dates E(t-1), E(t):
- Anchor date D(t): the first NSE trading session after E(t-1).
- Anchor price A(t): first valid 1-minute candle open stamped at or after 10:00 IST on D(t), allowing at most a 3-minute delay. If no valid bar exists, exclude the row and log it.
- Expiry price C(t): close of the last valid NIFTY spot 1-minute candle representing the cash-session close on E(t) (normally bar start 15:29 IST; use a validated 15:25–15:29 last-bar rule).
- Return r(t)=C(t)/A(t)-1, in decimal units.
- Binary label is UP=1 for r(t)>0, DOWN=0 for r(t)<0; exact equality is FLAT and excluded from primary binary fitting, but counted and listed separately. No arbitrary deadband in v1.0.
- Forecast time is 10:00 IST as the anchor is observed; features may use the 10:00 bar open and preceding information, but must not use that bar's eventual high/low/close or any later timestamp.

The actual expiry list must be sourced from official contract/expiry data where possible. A calendar heuristic is allowed only as a discovery aid, each inferred holiday shift must be flagged, and rows with uncertain expiry dates are excluded from confirmatory statistics. Current NSE specs indicate Tuesday expiry; historical Thursday-to-Tuesday transition is accounted for.

## 3. Aim
Find a reproducible and statistically defensible model/rule with out-of-sample edge for this exact weekly binary label. If no model beats conservative baselines robustly, establish that result and identify data/design constraints blocking further inference.

## 4. Objectives
1. Build an auditable weekly expiry/anchor/close dataset and validate it independently.
2. Measure prevalence, stability and performance of naive baselines.
3. Test pre-registered price/volatility/market-structure features and a small set of model families.
4. Test newly designed expiry-cycle indicators and bounded evolutionary/symbolic searches without data leakage.
5. Quantify uncertainty and robustness across volatility regimes, calendar periods and the expiry weekday change.
6. Translate directional calls into a separately specified hypothetical instrument strategy only when contract prices and complete transaction-cost inputs are available.
7. Publish complete results, errors, reproducibility information and future research directions in a structured manuscript.

## 5. Research questions
- RQ1: Is the UP/DOWN label materially imbalanced or stable over time and across the Thursday-to-Tuesday expiry regime?
- RQ2: Do simple persistence, prior-cycle return, multi-day momentum, overnight gap, opening-range, realised-volatility and price-range features beat expanding-majority and unconditional-probability baselines out of sample?
- RQ3: Do regularised logistic models and shallow tree/ensemble models improve balanced accuracy and probability quality over simple rules?
- RQ4: Do interpretable custom indicators or symbolic regression deliver incremental performance after nested selection and correction for multiple comparisons?
- RQ5: Does adding India VIX, global benchmark returns, options-implied variables, breadth, and FII/DII activity improve results using only values available at forecast time?
- RQ6: Are probability estimates calibrated enough to support abstention on low-confidence calls?
- RQ7: Does any candidate preserve an edge across regimes and a held-out period, and does its edge survive a defensible date-specific trading-cost/slippage model?
- RQ8: Which failures are caused by data quality, sample size, regime change, look-ahead, or overfitting?

## 6. Hypotheses
- H0-1: No candidate has better out-of-sample balanced accuracy than the baseline by a practically meaningful margin.
- H1-1: At least one pre-registered candidate improves on the baseline in a locked time holdout with uncertainty bounds and robustness evidence.
- H0-2: Selected strategy gains do not survive realistic costs and conservative fill assumptions.
- H1-2: A fully specified instrument strategy remains net positive after all date-appropriate costs, with uncertainty and risk reported.
These hypotheses are evaluated separately; H1-1 does not imply H1-2.

## 7. Data and predictors
Primary: 1-minute NIFTY 50 spot OHLC with IST timestamps, actual weekly expiry calendar and exchange session dates. Candidate secondary sources: India VIX, NIFTY option chain/expired options, futures, official FII/DII reports, global index/FX/rates/commodity returns, sector/advance-decline breadth and timestamped news. All non-core sources are optional unless coverage, timestamps and rights pass inspection.

Feature set is fixed initially to: prior 1/5/10/20-session returns; realised volatility over 5/10/20 sessions; prior high-low range and ATR-like range; overnight gap; morning return from 09:15 up to the last fully closed bar before 10:00; change from prior expiry close to anchor; anchor opening gap versus 09:59 close; prior-cycle label; calendar regime and month. No feature may use information after the forecast cutoff.

## 8. Models and candidate discovery
- Baselines: expanding majority class; expanding UP probability; prior-cycle direction; sign of pre-anchor 5-session return; sign of prior expiry-cycle return.
- Confirmatory models: regularised logistic regression; shallow Random Forest / ExtraTrees or HistGradientBoosting with constrained settings.
- Optional models: calibrated linear margin model, volatility/regime-conditioned models, PySR symbolic expressions, and bounded genetic/evolutionary search inspired by Quantevolve. Optional model inclusion must be recorded before inspecting holdout performance.
- TradingView/Pine indicators are research candidates only; Python-generated labels are ground truth. Pine weekday logic does not replace the official historical expiry calendar.
- LLM multi-agent research tools may propose hypotheses and summarize sources; all claims and outputs must be independently validated by deterministic code.

## 9. Validation and statistical analysis
- Chronological expanding walk-forward; at each prediction, train only on earlier observations. A minimum 104 prior non-flat expiry rows is targeted; if sample size or class balance prevents this, report the deviation and lower power.
- Final untouched time holdout: most recent 20% of eligible rows; model choices and feature selection are frozen before using it. For an honest final holdout, walk-forward development may use the older 80% only. Results from any repeated tuning on that holdout are exploratory.
- Metrics: accuracy, balanced accuracy, precision/recall for both labels, Matthews correlation, ROC-AUC when both classes present, Brier score, log loss, calibration summary, coverage/abstention rate, Wilson interval for accuracy and block-bootstrap interval for differences.
- Baseline comparisons: paired prediction comparison where applicable; bootstrap by contiguous weeks/months to respect serial dependence. Report effect sizes, confidence intervals and p-values only when assumptions are justified.
- Multiple testing: retain an experiment registry; distinguish pre-registered and exploratory strategies; adjust exploratory model-comparison p-values (e.g., Holm or Benjamini–Hochberg) and/or use a locked holdout/backtest-overfitting diagnostic if sample size supports it.
- Robustness: pre/post expiry transition, VIX/realised-volatility regimes, calendar subperiods, missing-data exclusions, parameter stability, delayed execution and cost stress tests.
- Avoid random shuffle cross-validation. Never compute scalers, feature selection or hyperparameters across future folds.

## 10. Trading and transaction-cost rules
Classification results are reported separately from a trading P&L. A trade simulation must name an instrument and use price data for that instrument or transparently label a spot-return proxy as non-executable. For Paytm Money use the official fee schedule effective on each trade date: brokerage per executed order (current public FAQ says ₹10 per unique executed order), exchange transaction charges, STT as date-effective, GST, stamp duty, SEBI/regulatory charges, bid-ask spread, slippage, lot/contract multipliers and realistic order fills. Include entry/exit fees, turnover, worst-case stress assumptions, drawdown, turnover and Sharpe only where mathematically appropriate. Never set missing fees to zero.

## 11. Phases and acceptance gates
### Phase 0 — Bootstrap and governance
Deliverables: instructions, locked plan, source register, structured logs, script, tests, workflow, manuscript skeleton. Gate: files verified in repo; workflow syntax and unit tests pass.

### Phase 1 — Data and label validation
Deliverables: raw source metadata/checksums, quality report, expiry list, weekly labels. Gate: timestamps are IST-consistent, duplicate/conflict counts known, anchor and close rows individually auditable, uncertain expiry shifts are excluded or independently confirmed.

### Phase 2 — Baselines and feature construction
Deliverables: feature table with availability constraints; baseline performance. Gate: no duplicate weeks, missingness reported, all features are temporally causal.

### Phase 3 — Model and strategy discovery
Deliverables: walk-forward predictions; candidate registry; new indicators; any bounded evolutionary/symbolic candidates. Gate: results strictly compare against baseline and untouched holdout is not used for tuning.

### Phase 4 — Robustness, uncertainty, costs
Deliverables: calibration and confidence intervals, regime tests, leakage audit, date-aware cost stress tests. Gate: strategy passes robustness and (where executable data exists) net-performance requirements.

### Phase 5 — Manuscript and independent audit
Deliverables: complete manuscript, charts/tables, appendices, data/code citations, limitations, future work, final error-log review. Gate: independent check of formulas, signs, joins, timestamps, multiple-testing, costs and repository compliance.

## 12. Stop rules
The initial cycle ends after Phase 5 or is explicitly marked BLOCKED when essential data/permissions are unavailable. Do not launch unlimited strategy search. A candidate is called a validated directional model only if it improves on the best pre-registered simple baseline on the locked holdout with uncertainty evidence and stable robustness. A usable trading strategy additionally requires instrument-specific fills and positive net results after verified costs. Otherwise publish a negative, inconclusive or blocked result honestly.


## 13. Version 1.2 amendment — Dhan-backed dataset rebuild

The registered data reconstruction, six causal feature additions, fixed candidate list, 104-row minimum training history, chronological 80/20 split, four-week moving-block bootstrap and stop rules are in [RESEARCH_PLAN_V1_2_DHAN_DATASET_ADDENDUM.md](RESEARCH_PLAN_V1_2_DHAN_DATASET_ADDENDUM.md) and [Phase 10](PHASE_10_VERIFIED_DATASET.md). The previous plan remains an auditable record; changes apply only to the Phase 10 source-identifiable sample. No trading strategy is validated by this amendment.


## Phase 10 outcome — bounded method screen (26 October 2026)

The version 1.2 Dhan-backed reconstruction and fixed-candidate evaluation completed. The source-gated dataset contains 256 weekly cycles, with a 204-row development partition and 52-row chronological holdout. The development-scored portion begins after the registered 104-cycle minimum training history.

The development-selected baseline was base ExtraTrees; the selected challenger was ExtraTrees with six additional causal trend/volatility features. Holdout balanced accuracy was 54.85% for the baseline and 53.79% for the challenger, a −1.06 percentage-point difference. The paired four-week moving-block bootstrap 95% interval for the difference was −5.00 to +3.44 points. The preregistered screen did not pass. **Conclusion: no new directional method validated in this bounded run.**

This is a prediction experiment, not a profitable trading strategy. Historical contract-level futures/options fills, Paytm Money date-effective costs, spreads and slippage were not validated. The current phase stops here; do not retune against this holdout. See [Phase 10 plan](PHASE_10_VERIFIED_DATASET.md), [results summary](../research/results/phase10/summary.json), and [full report](../research/results/phase10/phase10_report.md).
