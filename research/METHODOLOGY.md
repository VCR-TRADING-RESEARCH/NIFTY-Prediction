# Methodology and Statistical Analysis Plan

Version: 1.0. All changes should be logged and versioned.

## 1. Data engineering and calendar
Load minute OHLC from the source folders. Keep source timestamp semantics as candle-start IST. Consolidate identical duplicates; conflicting duplicates are logged and resolved by a deterministic source-priority rule. Validate each bar's OHLC consistency and exclude malformed rows.

Generate candidate weekly expiry dates using historical weekday regimes only as a discovery fallback (Thursday before the September 2025 transition, Tuesday afterwards, shifted back only with official holiday evidence). A confirmed actual contract calendar outranks a weekday heuristic. Label every expiry as official, verified_shift, inferred or uncertain; confirmatory analysis uses official/verified_shift only. If no official calendar is available, publish a clearly marked exploratory analysis and do not claim a validated final result.

## 2. Anchor and label alignment
For an expiry pair, select the first session after the previous expiry, then the first valid 1m bar at/after 10:00 IST and within 3 minutes. Use the bar's Open as the reference value. The prediction cutoff is the anchor bar's opening time; do not use that bar's high/low/close. The expiry outcome uses the final valid cash-session bar in a validated closing window, and its timestamp is retained. Return is close/reference minus one. Sign is UP for positive, DOWN for negative, FLAT if exactly equal.

Version 1.0 defines “at 10 am” as the 10:00 bar open (or first valid open by 10:03); it must not be silently replaced with that bar's close.

## 3. Causal features
For the anchor timestamp:
- Lagged session returns: 1, 5, 10 and 20 completed sessions.
- Realised standard deviation of daily returns: 5, 10 and 20 sessions.
- Lagged rolling high-low range, normalized by previous close.
- Previous close-to-close trend and prior expiry-cycle return/direction.
- Previous close to anchor overnight gap.
- Current-session 09:15 to last completed bar before 10:00 return.
- 09:59 close to 10:00 open jump.
- Prior close relative to recent range.
- Calendar regime (historical expiry weekday era), month and session-gap length.
- Optional official India VIX, global overnight moves, breadth, FII/DII and options inputs only with point-in-time availability.

When calculating a rolling window, sort by timestamp, shift daily closes so the current-day close is never included, and ensure anchor-date features use data strictly preceding the forecast timestamp except the anchor Open itself. Standardization, imputation and model fitting occur within training folds.

## 4. Baselines
- Expanding historical majority class.
- Expanding UP prevalence as probability baseline.
- Prior expiry-cycle direction.
- Sign of 5-session return available before forecast.
- Sign of prior-cycle return.
A machine model must beat the strongest relevant baseline, not only 50% accuracy.

## 5. Model suite
Initial library: scikit-learn LogisticRegression with StandardScaler in a Pipeline; a shallow ExtraTrees or RandomForest candidate with bounded depth/leaves. Small sample sizes mean deep trees, neural networks and LLM-as-predictor are excluded from confirmatory v1.0. Hyperparameter search is modest and confined to training data. PySR/Quantevolve are optional later-stage candidate generators with a strict expression/search budget and a locked holdout; they do not bypass the same testing rules.

## 6. Validation
Primary estimator is an expanding walk-forward sequence: for each prediction, use only older observations, train after a minimum history when feasible, then record out-of-sample prediction probability. A final contiguous 20% holdout remains untouched during feature/model selection; if eligible observations are too few for a 104-row training history, report the restriction and avoid overclaiming. Report results separately by historical expiry weekday regime.

Metrics: count, UP prevalence, accuracy, balanced accuracy, class precision/recall/F1, Matthews correlation, ROC-AUC when valid, Brier score, log loss, confusion matrix, calibration and coverage for abstention rules. Include Wilson confidence intervals for accuracy and a contiguous-block bootstrap for metric differences if sample size supports it. Compare candidate versus baseline with paired methods and correct exploratory comparisons for multiplicity. P-values are supportive, not the sole decision criterion.

## 7. Costs and executable strategy
A directional label is not an instrument P&L. To claim a usable strategy, specify a futures/options contract and actual price series, order timestamps, contract multipliers/lot size and fill assumptions. Model entry/exit brokerage and all taxes/fees at the schedule in force on each trade date. Apply slippage/spread on both sides; test conservative 2x/3x slippage scenarios. An index-return proxy may be presented as such but must not be called executable. Paytm Money's currently published F&O FAQ states ₹10 per unique executed order; historical schedules and other levy rates need verification. STT changed effective 1 April 2026 per NSE, so current rates must not be back-applied historically.

## 8. Uncertainty, regimes and robustness
- Split pre/post September 2025 expiry rule; do not let a learned calendar shift masquerade as alpha.
- Evaluate low/medium/high volatility using only information available by forecast time.
- Use rolling/expanding class-rate baseline, not hindsight full-sample prevalence.
- Test missing-data sensitivity and alternate valid close/anchor definitions as labelled exploratory sensitivity analysis.
- Assess signal stability to a small parameter neighbourhood and remove fragile features.
- Optional conformal sets/abstention must be calibrated on a separate prior period and measured for coverage; no guarantee under market regime shift.
- If many candidates are searched, record all candidates and include multiple-testing/backtest-overfit checks where sample size allows.

## 9. Quality and mathematical audit
Before accepting results, verify:
1. Return sign: close/reference minus one; UP if strictly positive.
2. Positive prices, sane OHLC invariants, ordered timestamp and timezone.
3. Expiry rows are unique and aligned to actual contract dates, including holidays.
4. No duplicate weeks, no inconsistent timezone joins, no forward fill of target prices.
5. Training timestamp is strictly before each prediction; feature computation does not use future candle closes.
6. Costs deducted on both entry and exit using correct turnover basis; taxes apply to appropriate transaction side.
7. Metrics computed from saved out-of-sample predictions only; uncertainty uses valid sample definitions.
8. Output files and logs match run ID/config hash; failures and exclusions are reported.

## 10. Reproducibility
Save environment versions, commit SHA, source manifest/hashes, run date, model seeds, configuration, split indices, prediction rows and aggregate metric tables. Do not save raw credentials or hidden private reasoning. Workflow runs deterministic baselines first; optional expensive tools run only when data size and runtime justify them.
