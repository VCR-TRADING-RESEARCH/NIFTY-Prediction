# Phase 9 — New Methods for NIFTY Weekly-Expiry Direction

**Branch:** research/phase-9-new-direction-methods  
**Plan version:** 1.1 addendum dated 26 October 2026  
**Status:** METHOD DESIGN COMPLETE; EMPIRICAL MODEL COMPARISON BLOCKED  
**Scope:** Preserve the existing target definition. Do not redefine the prediction horizon in this phase.

## 1. Why this extension is needed

The existing exploratory holdout contains 80 cycles. ExtraTrees reports 61.25% accuracy, 60.18% balanced accuracy, MCC 0.213, Brier score 0.246, log loss 0.686 and ROC AUC 0.574. The approximate Wilson 95% interval for accuracy is 50.3%–71.2%. These results warrant careful further investigation, but they are not confirmatory: the 10:00 anchor is not independently reconciled and the source audit reports 1,719 of 1,903 archive daily closes differ from official NSE closes by more than the pre-registered one-point tolerance.

This phase does not train more models on potentially defective labels. It records falsifiable method families, audits present input availability, and adds an automated readiness report. A blocked result is an acceptable research result; it is not evidence that a new predictor has failed or succeeded.

## 2. Research questions

- **RQ9.1 — Regime conditionality:** Does the predictive content of pre-anchor trend, gaps and cycle features change across low/medium/high realised-volatility or India VIX regimes?
- **RQ9.2 — Options information:** Do point-in-time option-implied distribution features (ATM IV, term structure, risk reversal/skew, butterfly, ATM straddle-implied move and put/call open-interest changes) add information beyond spot OHLC?
- **RQ9.3 — Overnight and global lead/lag:** Do timestamp-valid GIFT NIFTY, US/Asian market returns, USD/INR, crude, gold or rates improve the directional forecast at 10:00 IST?
- **RQ9.4 — Trend versus reversal:** Are multiscale momentum, opening-gap continuation/reversal, trend-efficiency, range position, ATR-normalised movement and asymmetric downside/upside volatility more useful than the current feature set?
- **RQ9.5 — Regime-aware estimation:** Do fold-local volatility states, change-point indicators or simple regime interactions improve walk-forward performance without increasing instability?
- **RQ9.6 — Symbolic/evolutionary discovery:** Can a complexity-constrained PySR or Quantevolve-inspired search discover a simple expression that survives nested development selection and one untouched post-repair holdout?
- **RQ9.7 — Decision uncertainty:** Can sequential probability calibration and time-series-aware conformal/EnbPI-style uncertainty support abstention on weak signals?
- **RQ9.8 — Economic relevance:** Does any verified directional improvement survive realistic contract-level Paytm Money fees, bid/ask spreads, slippage, lot sizing and conservative fills?

## 3. Aim and objectives

**Aim:** Identify a compact, replicable set of candidate methods for the defined weekly-expiry direction task while controlling data snooping and keeping data quality ahead of model complexity.

1. Independently reconcile the 10:00 anchor and explain the archive-versus-official OHLC discrepancy before empirical model comparison.
2. Add only point-in-time predictors with verified timestamps and historical coverage.
3. Prioritise interpretable, low-complexity methods suited to approximately 400 weekly observations.
4. Compare candidates against expanding-majority, unconditional UP frequency, simple direction rules, regularised logistic regression and constrained ExtraTrees using chronological splits.
5. Estimate uncertainty and calibrate probabilities only inside development folds; register abstention/model-selection rules before final holdout evaluation.
6. Maintain an experiment registry that distinguishes not-run, blocked, failed and completed experiments.
7. Only after the direction gate passes, separately evaluate executable futures/options P&L with date-specific charges, spread, slippage and fill assumptions.

## 4. Literature-informed method shortlist

| Priority | Candidate family | Candidate variables / model | Rationale | Main restriction |
|---|---|---|---|---|
| P0 | Source and anchor integrity | Official sessions, independently sourced 10:00 OHLC, official close, row-level provenance | Prevents incorrect labels from masquerading as model error | Must pass before any new model search |
| P1 | Multiscale trend, gap and range | 1/5/10/20-session return, trend efficiency, overnight gap, pre-anchor move, range position, ATR-normalised movement and rolling z-scores | Extends current features with interpretable trend strength and reversal structure | No anchor-bar high/low/close or post-10:00 information |
| P1 | Volatility conditionality | Realised-volatility ratios, upside/downside semivariance, India VIX level/change/rolling percentile, trend × volatility interactions; optional GARCH/HAR-derived features | Tests whether direction is conditional on market state rather than assuming volatility predicts direction alone | Fit thresholds and estimates on past data inside each fold |
| P1 | Point-in-time options surface | ATM IV, term structure, 25-delta risk reversal/skew, butterfly, ATM straddle-implied move, expiry-specific PCR, strike/moneyness OI and volume changes | Options can encode forward-looking risk-neutral distribution and positioning information not in spot OHLC | Historical 10:00 snapshots must be available no later than 09:59:59 IST; EOD open interest cannot be backdated |
| P1 | Global overnight and cross-market leads | Available GIFT NIFTY/futures, prior US close and overnight futures, Asian benchmarks, USD/INR, crude, gold and rates | Tests global price discovery and overnight information transmission | Explicit market timezone, holiday, close and publication-time handling |
| P2 | Flows and breadth | Properly lagged FII/DII cash activity, participant futures/options OI and volume, advance/decline breadth and sector returns | Adds positioning and market-participation state | Report publication time is required; do not use same-day reports released after 10:00 |
| P2 | Fold-local regime models | Rolling realised-volatility quantiles, simple state labels, change-point flags, regularised regime-interaction terms; optional Markov switching | Tests whether conditional effects survive temporal regime changes | Never fit states on the entire sample; inspect small-regime counts |
| P2 | Calibrated prediction and abstention | Fold-local calibration; sequential conformal or EnbPI-style uncertainty diagnostics | Could improve selective decision quality by abstaining on ambiguous weeks | Coverage under non-stationarity must be measured, not assumed |
| P3, bounded | Symbolic/evolutionary discovery | PySR expressions and Quantevolve-inspired candidate rules | May suggest compact, interpretable interactions | Only after source gate passes; cap at 100 candidate expressions/rules and at most 3 development-only generations; log every trial |
| Deferred | News agents and deep sequence models | Timestamped event features; TradingAgents-style hypothesis generation; LSTM/TCN/Transformer | Potential value requires much richer sequence/event data | About 398 weekly rows are insufficient for unrestricted neural/model search; LLM output is not ground truth |

The research order deliberately prioritises source quality, causal low-complexity features, volatility interactions and options data. Bigger models are not inherently better.

## 5. Data acquisition and point-in-time rules

1. **Free and official first:** NSE Indices NIFTY 50 OHLC and India VIX history; NSE F&O UDiFF bhavcopy, contract expiry and contract-wise reports; historical participant-wise OI/trading volumes and FII derivatives statistics; official trading-session calendar. Relevant catalogue: https://www.nseindia.com/all-reports-derivatives.
2. **Independent intraday inputs:** compare the current archive with a genuinely different source. The technovusin/nifty50-historical-data comparison is a mirror test because it is also the main pipeline's input. It cannot count as independent validation. Another published dataset with unknown underlying provider lineage is diagnostic, not ground truth. A recent Dhan overlap may validate recent observations but cannot validate the complete historical window alone.
3. **Public option research data:** inspect Zenodo record 10899828 (reported spot/futures/options minute data for 2017–2020): https://zenodo.org/records/10899828, and Hugging Face rissin/nse-options-intraday (source page describes historical daily options and intraday data from 2024 onward): https://huggingface.co/datasets/rissin/nse-options-intraday. Fetch only relevant partitions and validate schemas, timestamps, contract mapping, provider lineage and rights.
4. **Global/flow/news inputs:** retain a source manifest with URL, licence/rights, coverage, timestamp convention, actual publication time, missingness, checksum and transformation. Use only data that existed by the forecast cutoff.
5. **Composite datasets:** combine sources only after row-level date/time alignment and conflict reports. Preserve original source values and provenance. Never silently average conflicting prices or substitute a source without recording it.
6. **Caching and security:** cache immutable public downloads keyed by source/date/schema version. Store compact derived rows, manifests and reports. Do not commit secrets or large raw market files unless data rights and repository size permit.

## 6. Scientific methodology and statistical analysis

### Target and feature clock

Keep the existing target unchanged: for each actual expiry E(t), compare the official/validated spot close C(t) with the first valid one-minute bar open at or after 10:00 IST on the first NSE session after the preceding expiry E(t-1). Return equals C(t) / A(t) - 1; UP is a strictly positive return, DOWN strictly negative and exact ties remain FLAT/excluded from primary binary fitting unless the registered protocol changes. The anchor bar's eventual high/low/close and later timestamps are not permissible predictors.

### Splits and model selection

- After data repair, rebuild labels and write a dated split manifest before viewing the new holdout results. The existing holdout must not be recycled for method choice while the source gate remains blocked.
- Use expanding walk-forward evaluation; aim for at least 104 earlier non-flat cycles where feasible and explicitly report when sample size prevents it.
- Use nested development-only feature selection, probability calibration and tuning. Do not shuffle weeks randomly.
- Keep the final contiguous 20% of rebuilt eligible cycles untouched. Evaluate it once after methods are frozen.
- Compare the current baselines first, then add one method family at a time. Use ablation tests to determine whether new data adds value beyond spot features.

### Metrics and uncertainty

Primary predictive metric: balanced accuracy. Secondary metrics: accuracy with Wilson interval, Matthews correlation, per-class precision/recall, ROC-AUC when both classes exist, Brier score, log loss, calibration and abstention coverage. Compare paired weekly predictions using contiguous-block bootstrap intervals and apply Holm correction for the bounded primary model comparisons. Do not report unsupported p-values.

**Proposed screening rule to preregister before examining the repaired holdout:** require at least +0.03 balanced-accuracy improvement over the strongest preregistered baseline; a paired 95% contiguous-block bootstrap interval for the improvement above zero; no material degradation in Brier score/log loss; and effect direction that is not reversed across key time/volatility regimes. This is only a model-screening rule, not proof of profitability. Record exact bootstrap block construction and multiple-comparison correction before evaluation.

### Trading validation is a separate gate

A spot-direction score is not a trade. A later strategy must use verified futures/options contract prices and fills; Paytm Money brokerage effective for each trade date; exchange transaction fees, STT, GST, stamp duty and SEBI/regulatory charges; lot size; bid/ask spread; slippage; and conservative fill stress. If historical rates/quotes/fills are unavailable, cost-adjusted P&L remains BLOCKED rather than assuming zero cost. Spot return proxies must be labelled non-executable.

## 7. Current evidence and gate outcome

| Item | Current evidence | Phase-9 implication |
|---|---|---|
| Labelled weekly cycles | 398 binary rows in the latest pipeline | Small sample; keep models compact |
| Existing ExtraTrees holdout | Accuracy 0.6125; balanced accuracy 0.6018; MCC 0.2129; Brier 0.2465; ROC-AUC 0.5745 on n=80 | Exploratory only; not a licence to optimise on the old holdout |
| Expiry calendar | 402/402 candidate expiry dates were marked verified in the official-source audit | Calendar evidence exists, but data gate still fails |
| Minute-source close check | 1,719/1,903 closes differ from official by >1 point; median absolute difference 8.25 points | Source gate remains blocked |
| Independent historical 10:00 anchor | Not established across the full period | No new empirical model search |
| Options, global, flows | No audited point-in-time table joined to the current labels | Candidate families are designed, not tested |
| Executable contract P&L | Historical fills, complete dated costs, spreads and slippage not validated | No strategy claim |

The readiness script must emit BLOCKED_EMPIRICAL_METHOD_SEARCH until the data/anchor gate is repaired. It may report readiness and candidate inputs; it must not train candidates or call anything a winner.

## 8. Acceptance gates and bounded stop rules

- **Gate A — method design:** research questions, candidate families, source mapping, search budgets and stop rules documented; readiness audit and regression tests pass. This is the present deliverable.
- **Gate B — target repair:** independently validate 10:00 prices and explain official OHLC discrepancies; retain row provenance and true expiry contracts. If blocked, document the exact source gap.
- **Gate C — preregistered evaluation:** rebuild features/labels, freeze split manifest, run expanding development comparisons and evaluate the final holdout once; register all attempted methods.
- **Gate D — robustness:** uncertainty, regime/subperiod, leakage, calibration and multiple-testing audits pass.
- **Gate E — trading:** contract-level net results remain positive under verified charges, spreads, slippage and conservative fills. Otherwise conclude no usable strategy is validated.
- Stop after these gates. Symbolic/evolutionary work is bounded and optional. Do not add more model families simply because earlier results disappoint.

## 9. Strengths and limitations

**Strengths:** exact target preserved; recent literature and official report sources mapped; hypotheses are falsifiable; point-in-time rules explicit; search budget bounded; prediction and trading profitability clearly separated; data gate not bypassed.

**Limitations:** no new predictive model has been empirically tested in this phase; anchor/source gate remains blocked; public derivative archives may only provide EOD values rather than 10:00 snapshots; input data rights/coverage require checks; weekly sample size limits complexity and statistical power.

## 10. References

- Sajjan (2026), “Variance Risk Premium in Nifty 50 Weekly Expiry Cycles: VIX Calibration Bias and Regime Dependence,” SSRN preprint: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6918100. Preliminary working-paper evidence; reproduce independently.
- Preethi S. R. (2026), “Intraday Volatility Regimes via Unsupervised Machine Learning: Evidence from the NIFTY Index,” SSRN preprint: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6316139. Regime discovery does not by itself imply directional alpha.
- Xu and Xie (2023), “Conformal Prediction for Time Series,” IEEE TPAMI, DOI: https://doi.org/10.1109/TPAMI.2023.3272339.
- Dotsis (2024), “A New Index of Option Implied Absolute Deviation,” Journal of Futures Markets, DOI: https://doi.org/10.1002/fut.22537. The S&P 500 result motivates a testable distribution-shape hypothesis, not established NIFTY validity.
- NSE derivatives reports: https://www.nseindia.com/all-reports-derivatives.
- SEBI equity-derivatives source directory: https://www.sebi.gov.in/curation/equity_derivatives.html.
- Existing source gate: [Phase 3 reconciliation](PHASE_3_SOURCE_RECONCILIATION.md); current experiment registry: [experiment_registry.json](../research/results/experiment_registry.json); manuscript: [manuscript.md](../research/manuscript.md).
