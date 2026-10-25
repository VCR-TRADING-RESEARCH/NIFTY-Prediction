# NIFTY Weekly Expiry Direction Research

**Purpose:** Predict whether the NIFTY 50 spot index at the close of a weekly options expiry is higher or lower than its value at **10:00 IST on the next trading day after the preceding weekly expiry**. This project researches a binary directional forecast, not a generic return-maximization system.

> **Research status (2026-10-25):** Phase 3 is **BLOCKED**. Official expiry records verify 402/402 candidate dates, but the preserved minute archive's daily close differs from official NSE close by more than one point on **1,719/1,903 sessions** (median absolute difference 8.25 points; P95 32.435; max 200.7). A prior apparent PASS was a circular comparison and is invalidated. Model metrics remain exploratory; **no usable trading strategy is validated**.

## Definition of the target

For each actual weekly expiry date \(E_t\), let \(A_t\) be the first valid NIFTY 50 spot price at or after 10:00 IST on the next NSE trading day after the preceding expiry \(E_{t-1}\), and let \(C_t\) be the official/validated NIFTY 50 spot close on \(E_t\).

- Directional return: \(r_t = C_t / A_t - 1\).
- Binary label: \`1\` if \(r_t > 0\); \`0\` if \(r_t < 0\).
- Exact ties are retained as a separate \`flat\` label for data-quality reporting and excluded from binary model fitting unless a pre-registered tolerance is selected.
- All features must be available by the forecast timestamp. No expiry-day close, post-forecast data, or revised/future information may leak into features.
- Weekly NIFTY 50 options started in February 2019; 2017–2018 minute bars may be used only for feature lookback, not weekly-option expiry labels. The first weekly expiry was 14 February 2019. Expiry weekday changed from Thursday to Tuesday in September 2025, with holiday shifts. A complete historical contract calendar is required for confirmatory inference. Official NSE circulars document Thursday weekly expiry through August 2025 and Tuesday from September 2025; see [FAOP68747](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAOP68747.pdf) and the [current NIFTY 50 contract specification](https://www.nseindia.com/static/products-services/equity-derivatives-nifty50).

The research target is on the spot index. Any executable strategy must separately define the instrument, order timing, position sizing, and cash-flow accounting (e.g., NIFTY futures or options) and apply date-effective Paytm Money brokerage, exchange charges, statutory levies, GST, stamp duty, bid-ask spread and slippage. Directional accuracy alone does not establish tradability.

## Research status

<!-- AUTO_STATUS_START -->
## Latest automated research status

Last status refresh: 2026-10-25 13:10 UTC

- Run ID: 40195799992
- Target labels: 398
- Binary rows with sufficient features: 398
- Development / final holdout rows: 318 / 80
- Model selected on development data: extra_trees
- Calendar status: **OFFICIAL_EXPIRY_AND_EOD_CLOSE; ANCHOR_SOURCE_PROVISIONAL**
- Independently validated usable trading strategy: **NO**

The 10:00 anchor remains minute-archive-derived and independently unvalidated; executable contract-level performance is not tested.

The target uses official NSE expiry dates and daily closes. The 10:00 anchor is still minute-archive-derived and independently unvalidated. No executable futures/options P&L with broker charges, spreads, slippage and fills has been validated.

- Source CSV files: 19
- Valid minute bars after checks: 882839
- Official NSE daily closes matched: 1903
- Minute-archive closes differing from official close by >1 point: 1719
- Median absolute minute-vs-official close difference: 8.25 points
- Yahoo daily-close cross-check: available; compared rows: 2352; mismatches over tolerance: 0

### Final holdout metrics (exploratory)
- extra_trees: accuracy 0.613, balanced accuracy 0.602, n=80
- logistic: accuracy 0.562, balanced accuracy 0.570, n=80
- majority: accuracy 0.463, balanced accuracy 0.500, n=80
- prior_cycle: accuracy 0.438, balanced accuracy 0.433, n=80
- prior_cycle_return: accuracy 0.438, balanced accuracy 0.433, n=80
- momentum_5d: accuracy 0.388, balanced accuracy 0.379, n=80

See the research log, error log, pre-registered plan, data-quality report, and manuscript for details.
<!-- AUTO_STATUS_END -->

| Phase | Status | Acceptance gate |
|---|---|---|
| 0. Repository bootstrap and governance | Implemented; workflow and unit tests pass | Files, logs, workflow and test scaffolding present |
| 1. Data and label validation | **BLOCKED** | 402/402 expiry records verified, but 1,719/1,903 archive close mismatches >1 point; 10:00 anchor provisional |
| 2. Baselines and leakage-safe features | Exploratory only | 398 labels; 318 development / 80 chronological holdout |
| 3. Model and indicator discovery | Exploratory only | Holdout accuracy 61.25%; no model certified; evolutionary/PySR/agent results did not beat baseline |
| 4. Robustness, uncertainty and costs | **BLOCKED** | Validated source and contract-level cost/P&L data unavailable |
| 5. Manuscript and independent audit | Draft updated; final audit blocked | False PASS corrected; findings and residual limitations documented |

### Latest Phase 3 source gate

- Official daily source: 1,913 rows collected; 1,903 sessions compared with preserved archive daily closes.
- Official expiry evidence: **402/402 candidate dates verified**, including shifted expiry dates; zero unverified and zero source errors.
- Independent preserved-archive close audit: **1,719/1,903** differences exceed one index point; median absolute difference 8.25 points; P95 32.435; maximum 200.7.
- **False PASS invalidated:** a prior comparison used a Yahoo cross-check file generated after official closes had already overwritten original archive values. That was circular and is not independent validation.
- 10:00 anchor remains provisional; model scores are exploratory. No strategy or costed P&L accepted.
- See [machine-readable report](data/reconciliation/source_reconciliation_report.json), [expiry verification](data/reconciliation/expiry_verification.csv), [close comparison](data/reconciliation/minute_vs_official_daily.csv), [yearly mismatch summary](data/reconciliation/daily_close_mismatch_summary_by_year.csv), and [Phase 3 plan](docs/PHASE_3_SOURCE_RECONCILIATION.md).
- Latest audit: [workflow run 40181901081](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40181901081); model run: [40181159630](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40181159630); [Phase 3 PR #3](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/pull/3).

## Repository map

- [Research operating rules](docs/RESEARCH_OPERATING_RULES.md)
- [Pre-registered research plan](docs/RESEARCH_PLAN.md)
- [Research questions and literature review](docs/LITERATURE_REVIEW.md)
- [Data dictionary and source register](docs/DATA_SOURCES.md)
- [Research status / step log](logs/RESEARCH_LOG.md)
- [Error and correction log](logs/ERROR_LOG.md)
- [Visible conversation log](logs/CONVERSATION_LOG.md)
- [Manuscript](research/manuscript.md)
- [Environment and methodology](research/METHODOLOGY.md)
- [Workflow entry point](scripts/run_research.py)
- [Automated test suite](tests/)
- [Research workflow](.github/workflows/nifty-research.yml)

## Research approach

1. Preserve exact target semantics and historical expiry-calendar transitions.
2. Collect free/official index and intraday data first; keep data provenance, timestamps, file hashes, and refresh metadata. Use the configured Dhan secrets only in GitHub Actions, never commit credentials.
3. Establish the majority-class, historical-frequency and simple rule baselines before ML.
4. Compare interpretable technical-feature models, regularized logistic regression, tree models and (only if data and compute justify it) symbolic-regression candidates. Use walk-forward splits; tune only inside training data.
5. Use probability metrics and confidence intervals, test class balance and temporal stability, and report all attempted candidates—including failed ones.
6. For tradability, simulate a specified instrument with date-aware Paytm Money fees, slippage/spread, exchange/statutory charges and position-sizing rules. If relevant fees or instrument prices cannot be verified, report cost-adjusted results as unavailable rather than silently assuming zero costs.
7. Stop after the pre-defined gates. Do not search endlessly or declare a winner from in-sample accuracy.

## Primary data priority

1. NSE / NSE Indices official historical index data, India VIX, expiry calendar and public market/statistical reports.
2. Free public intraday NIFTY spot OHLC sources, used with provenance and independent spot checks.
3. Dhan Data API (configured as organization/repository secrets, if available to Actions) for gaps or primary intraday capture.
4. FII/DII, global benchmarks, sector breadth, event/news, India VIX and options features only when timestamps/coverage and data rights allow. Optional feature sources must not block the core target test.
5. Public datasets from GitHub, Hugging Face, Zenodo and published papers as corroborating/alternative sources—not as a substitute for source-quality assessment.

## Reproducibility and safety

- Python pipeline is the reference research implementation; optional Rust acceleration may be added only if profiling shows it is necessary.
- Each phase is tracked on a separate branch. Summary/status artifacts are reflected on the default branch after phase completion.
- GitHub Actions should support both automatic scheduled runs and manual \`workflow_dispatch\` runs.
- Cache immutable inputs keyed by source/date/version; retain compact validated target/features and result tables in the repository. Do not commit large raw data, secret values, tokens, or private reasoning.
- Record every failure, correction, skipped test, and acceptance-gate outcome in the logs.
- The repository records visible conversation statements and research decisions; it does not store hidden private chain-of-thought. Decisions are recorded as concise rationales and reproducible methods.
- Research and backtest outputs are experimental, not financial advice and not a promise of future performance.

## Primary external references

- NSE NIFTY 50 derivatives expiry specifications: https://www.nseindia.com/static/products-services/equity-derivatives-nifty50
- NSE circular introducing weekly NIFTY 50 options and first expiry (14 February 2019): https://nsearchives.nseindia.com/content/circulars/FAOP39894.pdf
- NSE contract specifications: https://www.nseindia.com/static/products-services/equity-derivatives-contract-specifications
- NSE historical index/VIX reports: https://www.nseindia.com/all-reports
- Open NIFTY minute-data candidate (validate independently before use): https://github.com/technovusin/nifty50-historical-data
- Time-series momentum paper: https://doi.org/10.1016/j.jfineco.2011.11.003
- Probability of Backtest Overfitting: https://doi.org/10.21314/jcf.2016.322

Last repository status update: 2026-10-25.


## Phase 3: Official source reconciliation

**Status: AUTOMATED VALIDATION PENDING.** This phase attempts to replace the unverified candidate close source with official NIFTY 50 historical index data and confirm weekly expiries against NSE F&O contract bhavcopy. It does not promote any model.

- [Phase 3 plan and acceptance gates](docs/PHASE_3_SOURCE_RECONCILIATION.md)
- [Phase 3 automated workflow](.github/workflows/phase3-source-reconciliation.yml)
- [Reconciliation runner](scripts/reconcile_official_sources.py)
- [Parser and calendar tests](tests/test_official_reconciliation.py)
- [Official NIFTY Indices historical OHLC](https://www.niftyindices.com/reports/historical-data)
- [NSE F&O archives](https://www.nseindia.com/all-reports-derivatives)
- [NSE NIFTY 50 derivatives specifications](https://www.nseindia.com/static/products-services/equity-derivatives-nifty50)

<!-- PHASE3_STATUS_START -->
**Phase 3 source gate:** BLOCKED — checked 402 candidate expiry dates; official close mismatches >1 point: 1719.
See [source reconciliation report](data/reconciliation/source_reconciliation_report.json) and [Phase 3 plan](docs/PHASE_3_SOURCE_RECONCILIATION.md).
<!-- PHASE3_STATUS_END -->

The workflow is bounded, caches downloaded official source snapshots, and records errors instead of silently marking missing dates as valid. A PASS requires every candidate expiry to be confirmed in official contract data and all overlapping minute-archive daily closes to match official closes within one point. Until then, model results remain exploratory.


### Independent minute-source audit
The previous Phase 3 “alternative” dataset was not independent: the main fetch script and cross-check both read technovusin/nifty50-historical-data. The completed comparison found 1,901/1,901 exact matching daily closes, so it is marked MIRROR_NOT_INDEPENDENT and is not counted as cross-validation. A separate published dataset from sandeepkapri/Nifty50-Minute-Data is now being checked for 2019-02 through 2024-03; its underlying vendor lineage is not proven and it cannot alone pass the official-source gate.


## ExtraTrees as-of prediction page

- **Prediction page source:** [docs/prediction/index.html](docs/prediction/index.html)
- **Latest as-of forecast data:** [latest_prediction.json](docs/prediction/latest_prediction.json)
- **Historical leakage-safe walk-forward predictions:** [prediction_history.csv](docs/prediction/prediction_history.csv)
- **Generator:** [scripts/predict_asof.py](scripts/predict_asof.py)
- The NIFTY Weekly Expiry Research workflow generates the forecast after the research pipeline completes. The page shows the latest forecast as of the first available 10:00 IST anchor after the latest verified expiry, plus selectable historical walk-forward predictions.
- The future expiry date is explicitly provisional when the available official files do not verify the future holiday-adjusted date. Forecasts remain exploratory while the source gate is blocked; this page is not a trading recommendation and does not calculate options P&L.
