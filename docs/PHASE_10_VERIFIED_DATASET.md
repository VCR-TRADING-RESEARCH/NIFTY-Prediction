# Phase 10 — Dhan-Backed Weekly Dataset Rebuild and Bounded Method Test

**Branch:** research/phase-10-verified-dataset-rebuild  
**Plan version:** 1.2 addendum, 26 October 2026  
**Status:** PLAN LOCKED; AUTOMATED REBUILD/EVALUATION PENDING  
**Research budget:** One source rebuild and one pre-registered development/holdout evaluation pass. No unrestricted hyperparameter or evolutionary search.

## 1. Research questions

- Does the existing weekly NIFTY UP/DOWN target remain stable when historical 10:00 anchor prices are obtained directly from the authenticated DhanHQ intraday API and expiry closes / lagged daily OHLC are sourced from the repository's official NSE snapshot?
- Do simple multiscale trend and volatility-asymmetry features add useful out-of-sample directional information over the established simple rules, regularised logistic regression and constrained ExtraTrees?
- Does any augmented model beat the strongest pre-registered development-selected baseline on a fresh, chronological holdout with useful uncertainty evidence?
- If a candidate fails the screening criteria, is the correct outcome no validated edge rather than more unbounded searching?

## 2. Data reconstruction rule

1. Load the official NIFTY 50 daily OHLC reference table at data/reconciliation/nifty50_official_daily.csv and the official F&O expiry verification table at data/reconciliation/expiry_verification.csv. Preserve one row per official trading session and one row per verified actual expiry.
2. Obtain DhanHQ authenticated 1-minute bars for its advertised historical window (up to five years, requests no longer than 90 days). Cache source chunks by date. Do not commit raw Dhan bars or any credential, access token, PIN, TOTP value or provider response body.
3. Build a **complete official session calendar** from NSE daily records, then left-join the available Dhan intraday session counts. This is essential: missing Dhan bars must not cause a later observed day to be mistaken for the first NSE session after an expiry.
4. Use official NSE daily open/high/low/close for daily historical features and official NSE expiry closes for targets. Use Dhan intraday bars for the 10:00–10:03 anchor and causal pre-anchor features. Preserve Dhan-derived aggregates separately for diagnostics; never overwrite original values silently.
5. Exclude any cycle without a verified actual expiry pair, a true next official trading-session anchor, a valid 10:00–10:03 Dhan anchor, a complete enough Dhan session at anchor/expiry, or an official closing price. Record every exclusion and reason.
6. The labelled sample is limited by Dhan history. Earlier official daily history is used only for lagged features, not to fabricate pre-Dhan 10:00 anchor labels.

## 3. Fixed feature and model budget

Base feature family: the existing registered features in scripts/research_core.py (lagged daily returns, realised volatility/ranges, overnight gap, pre-anchor return/jump, prior completed cycle, range position and calendar terms).

One bounded augmentation family adds six causal features calculated from official daily returns strictly before the anchor date:
- five-session versus 20-session momentum spread;
- 5-day/20-day realised-volatility ratio;
- trend-efficiency ratio (absolute 20-session net return divided by the sum of absolute daily returns);
- downside semivolatility over 20 daily returns;
- upside semivolatility over 20 daily returns;
- downside/upside semivolatility ratio.

No feature may use the selected anchor candle's eventual high/low/close or information after the 10:00 anchor.

Fixed candidates: expanding-majority, prior-cycle direction, five-session momentum sign, prior-cycle-return sign, base logistic regression, base ExtraTrees, augmented logistic regression, augmented ExtraTrees. Default model hyperparameters stay fixed; no grid/random/LLM/evolutionary search.

## 4. Pre-registered evaluation

- Sort rows by actual expiry date, ascending. Primary target: official expiry close divided by Dhan 10:00 anchor open minus one, labelled UP for positive return and DOWN for negative return; exact FLAT rows are retained in the audit table and excluded from binary model fitting.
- Generate a split manifest **before model fitting**. The final contiguous 20% of feature-complete rows is the untouched holdout; the earlier 80% is development. Model/feature selection uses only expanding walk-forward development predictions.
- Minimum training history is 104 earlier labelled weekly cycles. If the usable sample cannot support this, publish a blocked/underpowered result; do not lower the threshold silently.
- Select the strongest baseline among the pre-registered rules and base estimators using development balanced accuracy (tie-break with Brier score where defined). Select the strongest augmented candidate the same way. Freeze both choices before evaluating the holdout.
- Metrics: accuracy with Wilson 95% interval, balanced accuracy, MCC, precision/recall by class, ROC-AUC where valid, Brier and log loss for probabilistic models, class prevalence, confusion matrix, and a paired four-week moving-block bootstrap interval for the holdout balanced-accuracy difference.
- Screening requirement: augmented candidate must improve balanced accuracy by at least 0.03 over the development-selected baseline on the holdout, the paired 95% block-bootstrap interval must be above zero, Brier/log loss must not materially worsen, and direction of effect must not reverse across principal subperiods. With the small sample, report uncertainty and do not claim an edge if the tests are inconclusive.
- Run the locked holdout once. The report may include fixed candidate metrics, but do not use their holdout rankings to run another tuning loop.

## 5. Data gate and interpretation

This phase replaces the suspect public minute archive as the source of selected 10:00 anchors and intraday features for the available Dhan window. It does not retroactively repair pre-Dhan minute bars or prove that an executable options strategy is profitable. The existing public-vs-official archive close discrepancy remains in the historical error log; rebuilt daily features and target closes come from official NSE daily OHLC instead of that archive.

If the Dhan history manifest, verified expiry data or official daily source is incomplete, stop evaluation and publish the reason. Otherwise the resulting predictive experiment is a **Dhan-backed, source-identified exploratory walk-forward study**. Do not call the model confirmatory solely because the data pipeline passed.

## 6. Trading gate remains separate

A directional model is not a trading strategy. No positive net-P&L statement is allowed until contract-level NIFTY futures/options prices, actual entry/exit rules, lot size, realistic fills, Paytm Money brokerage effective for each trade date, exchange/statutory charges, GST, bid/ask spread and slippage stress are joined and tested. If those data are not available, report trading acceptance as BLOCKED, not zero-cost.

## 7. Stop rule and deliverables

Stop after this rebuild/evaluation run. Publish compact machine-readable data-quality summary, labelled feature table, exclusion table, split manifest, model metrics and predictions, pre-registered comparison/uncertainty table, charts, manuscript addendum, updated README and structured logs. If no augmented model passes the gate, stop with the result “no new directional method validated in this bounded run.”

## 8. Status ledger

- Official expiry calendar available: 402 candidate expiry rows in the current repository snapshot; the build will validate every row before use.
- Official daily OHLC snapshot: through 23 October 2026.
- Dhan anchor audit: five-year window 26 October 2021–25 October 2026; 1,229 overlapping session anchors compared, all timestamps matched exactly, maximum anchor-open discrepancy 0.0008 points; 257 overlapping cycle labels showed no direction switches. This is strong diagnostic agreement, not a claim that trading P&L has been validated.
- Prior model results: older 2019–2026 public-archive-derived 80-row holdout remains exploratory and is not reused for model choice.
- Future Dhan-backed dataset, new split and model results are produced by this Phase 10 workflow.
