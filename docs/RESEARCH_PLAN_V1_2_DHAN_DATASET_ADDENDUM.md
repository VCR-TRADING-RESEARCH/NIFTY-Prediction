# Research Plan Version 1.2 Addendum — Authenticated Dhan Dataset Rebuild

**Date:** 26 October 2026  
**Branch:** research/phase-10-verified-dataset-rebuild  
**User authorisation:** Proceed with the next bounded research phase following the Phase 9 source-audit checkpoint.

## Change control

This amendment preserves the original weekly-expiry target semantics, chronological evaluation principles, baseline comparisons, and transaction-cost separation. It changes the execution dataset, not the economic question: official NSE daily OHLC and the official verified expiry table will be used for the full daily feature history; authenticated DhanHQ 1-minute bars will provide the 10:00 anchor and pre-anchor intraday features where the five-year Dhan window has coverage.

The historical public minute archive is no longer the label/feature source for this rebuild. Its disagreement with official daily OHLC remains documented in prior logs, but rebuilt daily values use official NSE values directly. This does not retroactively repair older public minute records or supply pre-Dhan historical anchor labels.

## Fixed experiment design

- Historical Dhan window: request dates from the five-year boundary through the latest completed date, split into requests no longer than 90 days. Cache date-range chunks; do not commit raw Dhan bars or credentials.
- Official calendar: use every official NSE daily session as the session calendar, then left-join Dhan bar coverage. Never derive the next exchange session solely from dates where a Dhan candle happens to exist.
- Targets: only consecutive verified actual expiry pairs; first true NSE trading session after the previous expiry; valid Dhan 10:00–10:03 anchor; official NSE daily close on the target expiry date; sufficient Dhan session completeness at anchor and expiry.
- Feature clock: lagged official daily OHLC only before the anchor date plus Dhan bars available before the 10:00 anchor. Use the selected anchor candle's open only; never use its later high/low/close/volume.
- Six fixed causal augmentations: 5-vs-20-session momentum spread, realised-volatility ratio, 20-session trend efficiency, downside semivolatility, upside semivolatility, and downside/upside semivolatility ratio.
- Fixed candidate list: expanding majority, prior-cycle direction, 5-session momentum sign, prior-cycle return sign, base Logistic Regression, base ExtraTrees, augmented Logistic Regression and augmented ExtraTrees. No unrestricted search.
- Minimum training history: 104 earlier labelled cycles. If the dataset cannot support the registered development/holdout counts, the evaluation stops as blocked/underpowered.
- Split: sort by actual expiry date; the earliest 80% is development and the latest contiguous 20% is held out. Write the split manifest before fitting. Select one baseline and one augmented challenger on development predictions only. Evaluate the holdout once.
- Statistics: accuracy/Wilson interval, balanced accuracy, MCC, class-level precision/recall, ROC-AUC where valid, Brier/log loss for probability forecasts, and paired four-week moving-block bootstrap interval for balanced-accuracy difference.
- Acceptance screen: challenger balanced-accuracy improvement at least +0.03, paired bootstrap 95% interval lower bound above zero, Brier degradation no worse than 0.01, log-loss degradation no worse than 0.02, and no sign reversal in either half of the holdout. Failure means no new method validated, not permission to continue tuning the same holdout.
- Trading performance is a separate gate. Do not infer option/futures profitability from spot direction metrics. Paytm Money date-effective brokerage, exchange/statutory levies, GST, stamp duty, spreads, slippage, lot sizes, realistic fills and expiry settlement must be included before any strategy is called usable.

## Interpretation and limitations

The corrected source audit showed exact timestamps for 1,229/1,229 overlapping Dhan/public session anchors and maximum anchor-open discrepancy of 0.0008 index points. All 257 overlapping weekly labels remained unchanged when the alternate anchor was substituted while holding official expiry close constant. That cross-check is diagnostic; it is not the sole acceptance evidence. The rebuilt target rows will rely on authenticated Dhan data, verified expiry dates and official NSE daily closing values.

The final output remains an exploratory Dhan-window study because the sample is limited to the available five years and no executable futures/options cost-adjusted P&L is included. The bounded Phase 10 attempt ends after one registered run, regardless of whether a candidate passes.
