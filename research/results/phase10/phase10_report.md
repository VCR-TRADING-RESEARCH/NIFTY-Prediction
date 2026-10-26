# Phase 10 Results — Dhan-Backed Weekly NIFTY Direction

Generated (UTC): 2026-10-26T06:59:45.545138+00:00

## Executive result

- **Dataset status:** SOURCE_GATE_PASS_FOR_DHAN_WINDOW.
- **Model result:** NO_NEW_DIRECTIONAL_METHOD_VALIDATED.
- **Usable trading strategy:** NOT VALIDATED. No contract-level options/futures P&L with complete date-specific Paytm Money charges, spreads, slippage and fills was performed in this bounded model phase.
- **Selected baseline from development:** extra_trees_base.
- **Selected augmented challenger from development:** extra_trees_augmented.
- **Pre-registered screening result:** NOT PASSED — holdout balanced-accuracy improvement is below +0.03; paired four-week bootstrap 95% interval does not establish improvement above zero; one or both holdout subperiods are underpowered or show direction reversal.

## Data and target construction

The target uses the verified actual weekly expiry calendar and official NSE daily OHLC. The anchor and pre-anchor intraday features use authenticated DhanHQ 1-minute bars. The official NSE session list, not the set of observed Dhan sessions, determines the first trading session after the previous expiry. This avoids shifting the anchor when Dhan has a coverage gap.

- Official NSE daily sessions: n/a (n/a to n/a).
- Official sessions with Dhan intraday bars: n/a.
- Weekly cycles built / source-gate rows: n/a / n/a.
- Dhan anchor cross-check: {"absolute_difference_points": {"max": 0.000800000001618173, "median": 0.0, "p95": 0.000800000001618173}, "counts": {"anchor_open_mismatches_over_1_point": 0, "dhan_anchors": 1235, "exact_timestamp_matches": 1229, "overlap_sessions": 1229, "primary_anchors": 1229}, "interpretation": "Cross-check covers the overlapping sessions only; the Dhan source is authenticated, but the public comparison is diagnostic rather than exchange-official ground truth.", "report_status": "DIAGNOSTIC_ONLY", "weekly_label_sensitivity": {"anchor_difference_max_points": 0.000800000001618173, "anchor_difference_median_points": 0.0, "anchor_difference_p95_points": 0.000800000001618173, "caveat": "Same official expiry closes are used for both returns. This only measures label sensitivity to the secondary anchor; secondary provider lineage is unverified and labels remain exploratory.", "label_agreement_rate": 1.0, "label_switch_rate": 0.0, "labels_agreeing_with_original_published_label": 257, "primary_vs_secondary_direction_switches": 0, "status": "DIAGNOSTIC_ONLY", "weekly_cycles_with_secondary_anchor": 257}}.
- Fresh holdout: n/a to n/a (52 rows); development predictions start only after 104 earlier labelled rows.
- All feature engineering is causal to the 10:00 cutoff; the selected candle's later high/low/close is not used.

## Development walk-forward metrics

| candidate | n | accuracy | balanced_accuracy | mcc | brier | log_loss | roc_auc |
|---|---|---|---|---|---|---|---|
| majority | 100 | 0.530 | 0.500 | 0.000 | 0.252 | 0.697 | 0.448 |
| prior_cycle | 100 | 0.480 | 0.477 | -0.046 | n/a | n/a | n/a |
| momentum_5d | 100 | 0.510 | 0.509 | 0.018 | n/a | n/a | n/a |
| prior_cycle_return | 100 | 0.480 | 0.477 | -0.046 | n/a | n/a | n/a |
| logistic_base | 100 | 0.510 | 0.496 | -0.010 | 0.273 | 0.751 | 0.490 |
| extra_trees_base | 100 | 0.620 | 0.620 | 0.239 | 0.245 | 0.682 | 0.597 |
| logistic_augmented | 100 | 0.480 | 0.465 | -0.081 | 0.278 | 0.764 | 0.475 |
| extra_trees_augmented | 100 | 0.610 | 0.609 | 0.218 | 0.245 | 0.683 | 0.598 |

## Locked chronological holdout metrics

| candidate | n | accuracy | balanced_accuracy | mcc | brier | log_loss | roc_auc |
|---|---|---|---|---|---|---|---|
| majority | 52 | 0.423 | 0.500 | 0.000 | 0.259 | 0.711 | 0.374 |
| prior_cycle | 52 | 0.442 | 0.426 | -0.150 | n/a | n/a | n/a |
| momentum_5d | 52 | 0.385 | 0.364 | -0.277 | n/a | n/a | n/a |
| prior_cycle_return | 52 | 0.442 | 0.426 | -0.150 | n/a | n/a | n/a |
| logistic_base | 52 | 0.538 | 0.509 | 0.019 | 0.259 | 0.715 | 0.527 |
| extra_trees_base | 52 | 0.577 | 0.548 | 0.104 | 0.256 | 0.705 | 0.479 |
| logistic_augmented | 52 | 0.519 | 0.486 | -0.030 | 0.265 | 0.731 | 0.523 |
| extra_trees_augmented | 52 | 0.558 | 0.538 | 0.078 | 0.254 | 0.702 | 0.497 |

## Pre-registered primary comparison

- Baseline: extra_trees_base; challenger: extra_trees_augmented.
- Holdout balanced-accuracy difference: -0.011.
- Paired four-week moving-block bootstrap: {"block_length": 4, "difference_ci_95_high": 0.0343836805555555, "difference_ci_95_low": -0.050000000000000044, "difference_mean": -0.007351808676011449, "n": 52, "replicates_requested": 2000, "replicates_valid": 2000, "status": "COMPLETED"}.
- Brier baseline / challenger: 0.256 / 0.254.
- Log-loss baseline / challenger: 0.705 / 0.702.
- Subperiod balanced-accuracy differences (first half / second half): 0.019 / -0.036.

## Interpretation

No new directional method is validated by the pre-registered screen in this bounded run. Do not continue searching on this holdout; use a new, independently registered sample if further research is justified.

The data rebuild is source-identified for the Dhan coverage window and uses official daily prices/calendars. The earlier public minute archive remains in the error history for its mismatch with official daily OHLC; it was not used for the rebuilt labels or lagged daily features. The secondary-public-source anchor comparison is diagnostic rather than official ground truth.

## Limitations and next steps

The sample is limited to the available Dhan historical window. The holdout is small, and a single positive metric does not establish a repeatable trading edge. Options IV/OI/skew, timestamp-valid global inputs and lagged flow data have not been added in this experiment. No futures/options instrument-level backtest or costs were computed. The correct stopping outcome if the augmented method does not pass the pre-registered screening rule is **no new directional method validated in this bounded run**.

Reproducibility files: phase10_split_manifest.json; data_quality_report.json; development_metrics.csv; holdout_metrics.csv; holdout_predictions.csv; source and exclusion tables; plots.
