# NIFTY Weekly Expiry Direction Research

**Purpose:** Predict whether the NIFTY 50 spot index at the close of a weekly options expiry is higher or lower than its value at **10:00 IST on the next trading day after the preceding weekly expiry**. This project researches a binary directional forecast, not a generic return-maximization system.

> **Research status (2026-10-25):** Repository bootstrap in progress. No live or historical out-of-sample strategy is certified yet. A strategy is accepted only after leakage checks, walk-forward evaluation, robustness tests, and date-aware costs/slippage are passed. A workflow run or model score is not proof of profitability.

<!-- AUTO_STATUS_START -->
## Latest automated research status

Last status refresh: 2026-10-25 13:19 UTC

- Run ID: 40196840830
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

## Definition of the target

For each actual weekly expiry date \(E_t\), let \(A_t\) be the first valid NIFTY 50 spot price at or after 10:00 IST on the next NSE trading day after the preceding expiry \(E_{t-1}\), and let \(C_t\) be the official/validated NIFTY 50 spot close on \(E_t\).

- Directional return: \(r_t = C_t / A_t - 1\).
- Binary label: \`1\` if \(r_t > 0\); \`0\` if \(r_t < 0\).
- Exact ties are retained as a separate \`flat\` label for data-quality reporting and excluded from binary model fitting unless a pre-registered tolerance is selected.
- All features must be available by the forecast timestamp. No expiry-day close, post-forecast data, or revised/future information may leak into features.
- Expiry dates must come from an exchange calendar/contract archive; the weekday changed from Thursday to Tuesday in September 2025, with holiday shifts. Do not infer every historical expiry from a fixed weekday.

The research target is on the spot index. Any executable strategy must separately define the instrument, order timing, position sizing, and cash-flow accounting (e.g., NIFTY futures or options) and apply date-effective Paytm Money brokerage, exchange charges, statutory levies, GST, stamp duty, bid-ask spread and slippage. Directional accuracy alone does not establish tradability.

## Research status

| Phase | Status | Acceptance gate |
|---|---|---|
| 0. Repository bootstrap and governance | In progress | Repository files, logs, workflow and test scaffolding present |
| 1. Data and label validation | Pending automated run | Reconciled timestamps, expiry calendar, data coverage and missingness report |
| 2. Baselines and leakage-safe features | Pending automated run | Majority-class and simple momentum/range baselines reproduced |
| 3. Model and indicator discovery | Pending automated run | Walk-forward performance versus baselines; nested feature/model selection |
| 4. Robustness, uncertainty and costs | Pending automated run | Regime/stability tests, calibrated probabilities, realistic cost model |
| 5. Final manuscript and independent audit | Pending automated run | Results reproducible, limitations explicit, no unsupported profitability claims |

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


## ExtraTrees as-of-date prediction page

**Current status:** The previous GitHub Issue submission flow did not meet the one-click requirement. A replacement branch, [`phase/render-one-click-prediction`](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/tree/phase/render-one-click-prediction), changes the page to call the existing secure FastAPI service directly and adds a Render deployment manifest. The public endpoint URL intentionally remains blank until the service is deployed and health-checked; until then the page fails closed and will not ask users to submit an issue.

- [One-click deployment plan](docs/PHASE_RENDER_ONE_CLICK.md)
- [Render service manifest](render.yaml)
- [Render Dockerfile](live_api/Dockerfile.render)
- [Secure API app](live_api/app.py)
- [Live inference workflow / historical result details](docs/PHASE_8_GITHUB_ACTIONS_PREDICTION.md)

**Deployment gate:** BLOCKED pending authorization to deploy a service and configure private Dhan runtime variables. No claim of one-click live inference until a browser end-to-end request succeeds.

Historical inference evidence (not a current signal): [successful GitHub Actions run](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40201653154), [published JSON record for 2024-09-20](docs/assets/predictions/2024-09-20.json), [historical result page](https://vcr-trading-research.github.io/NIFTY-Prediction/?as_of_date=2024-09-20). That result is exploratory and not cleared for trading because anchor reconciliation and executable instrument-cost validation remain blocked.

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
- NSE contract specifications: https://www.nseindia.com/static/products-services/equity-derivatives-contract-specifications
- NSE historical index/VIX reports: https://www.nseindia.com/all-reports
- Open NIFTY minute-data candidate (validate independently before use): https://github.com/technovusin/nifty50-historical-data
- Time-series momentum paper: https://doi.org/10.1016/j.jfineco.2011.11.003
- Probability of Backtest Overfitting: https://doi.org/10.21314/jcf.2016.322

Last repository status update: 2026-10-25.
