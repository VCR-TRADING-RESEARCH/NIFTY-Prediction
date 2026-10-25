# NIFTY Weekly Expiry Direction Research

**Purpose:** Predict whether the NIFTY 50 spot index at the close of a weekly options expiry is higher or lower than its value at **10:00 IST on the next trading day after the preceding weekly expiry**. This project researches a binary directional forecast, not a generic return-maximization system.

> **Research status (2026-10-25):** First automated empirical run completed, but Phase 1 is BLOCKED: 368/402 expiry-date closes mismatch an independent daily-close source by >1 point and the historical expiry calendar remains heuristic. Provisional holdout model scores are exploratory only. No usable trading strategy is validated. Do not trade this result.

## Definition of the target

For each actual weekly expiry date \(E_t\), let \(A_t\) be the first valid NIFTY 50 spot price at or after 10:00 IST on the next NSE trading day after the preceding expiry \(E_{t-1}\), and let \(C_t\) be the official/validated NIFTY 50 spot close on \(E_t\).

- Directional return: \(r_t = C_t / A_t - 1\).
- Binary label: \`1\` if \(r_t > 0\); \`0\` if \(r_t < 0\).
- Exact ties are retained as a separate \`flat\` label for data-quality reporting and excluded from binary model fitting unless a pre-registered tolerance is selected.
- All features must be available by the forecast timestamp. No expiry-day close, post-forecast data, or revised/future information may leak into features.
- Weekly NIFTY 50 options started in February 2019; 2017–2018 minute bars may be used only for feature lookback, not weekly-option expiry labels. The first weekly expiry was 14 February 2019. Expiry weekday changed from Thursday to Tuesday in September 2025, with holiday shifts. A complete historical contract calendar is required for confirmatory inference.

The research target is on the spot index. Any executable strategy must separately define the instrument, order timing, position sizing, and cash-flow accounting (e.g., NIFTY futures or options) and apply date-effective Paytm Money brokerage, exchange charges, statutory levies, GST, stamp duty, bid-ask spread and slippage. Directional accuracy alone does not establish tradability.

## Research status

<!-- AUTO_STATUS_START -->
## Latest automated research status

Last status refresh: 2026-10-25 06:05 UTC

- Run ID: 40167611476
- Target labels: 398
- Binary rows with sufficient features: 398
- Development / final holdout rows: 318 / 80
- Model selected on development data: logistic
- Calendar status: **EXPLORATORY_ONLY**
- Independently validated usable trading strategy: **NO**

The current pipeline labels the weekday-derived expiry calendar as exploratory; performance metrics are not a verified trading edge. The spot index is not a directly executable instrument, and contract-level quotes, dated costs, spread/slippage and fills are not yet joined.

- Source CSV files: 19
- Valid minute bars after checks: 882839
- Yahoo daily-close check: available; compared rows: 2352; expiry-date mismatches over tolerance: 368

### Final holdout metrics (exploratory)
- extra_trees: accuracy 0.575, balanced accuracy 0.559, n=80
- logistic: accuracy 0.550, balanced accuracy 0.547, n=80
- majority: accuracy 0.463, balanced accuracy 0.500, n=80
- prior_cycle: accuracy 0.450, balanced accuracy 0.447, n=80
- prior_cycle_return: accuracy 0.450, balanced accuracy 0.447, n=80
- momentum_5d: accuracy 0.362, balanced accuracy 0.352, n=80

See the research log, error log, pre-registered plan, data-quality report, and manuscript for details.
<!-- AUTO_STATUS_END -->

| Phase | Status | Acceptance gate |
|---|---|---|
| 0. Repository bootstrap and governance | Implemented; workflow and unit tests pass | Files, logs, workflow and test scaffolding present |
| 1. Data and label validation | **BLOCKED** | 368/402 expiry-date close mismatches >1 point; official expiry calendar not reconciled; Dhan cross-check unavailable |
| 2. Baselines and leakage-safe features | Exploratory pass only | Provisional labels/features and baseline outputs generated; cannot accept while Phase 1 fails |
| 3. Model and indicator discovery | Exploratory pass only | 80-row holdout evaluated; no model certified; Quantevolve/PySR/TradingAgents deferred |
| 4. Robustness, uncertainty and costs | **BLOCKED** | Validated source and contract-level cost/P&L data unavailable |
| 5. Manuscript and independent audit | Manuscript drafted; independent audit pending | Exploratory results and blockers documented; no unsupported profitability claim |

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
