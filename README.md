# NIFTY Weekly Expiry Direction Research

**Purpose:** Predict whether the NIFTY 50 spot index at the close of a weekly options expiry is higher or lower than its value at **10:00 IST on the next trading day after the preceding weekly expiry**. This project researches a binary directional forecast, not a generic return-maximization system.

> **Research status (2026-10-25):** Research and deployment remain in progress; no strategy is certified for live trading. No live or historical out-of-sample strategy is certified yet. A strategy is accepted only after leakage checks, walk-forward evaluation, robustness tests, and date-aware costs/slippage are passed. A workflow run or model score is not proof of profitability.

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

**Current implementation status:** The GitHub Actions Python route has completed its first fresh Dhan-backed ExtraTrees inference. Test record for 2024-09-20: **UP**, raw UP score 51.3%, target expiry 2024-09-26, 147 eligible training labels through 2024-09-19, 268,510 minute bars, 20/20 features. [View the result JSON](docs/assets/predictions/2024-09-20.json) and [successful Actions run](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40201653154). This is a historical result and **not trading-ready**: independent 10:00 anchor validation and executable costs/slippage are still blocked. From Pages, selecting a date opens the GitHub Actions workflow page so you can manually dispatch that date; GitHub Pages cannot securely start a private workflow itself. Failed inference attempts publish an explicit failed status instead of reusing a prior same-date result.

- **Prediction page:** [Open the GitHub Pages source](docs/index.html) (deployment status is tracked in [Actions](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions)).
- **Forecast records and selectable history:** [docs/data/extra_trees_forecasts.json](docs/data/extra_trees_forecasts.json).
- **Leakage-aware forecast exporter:** [scripts/build_pages_forecasts.py](scripts/build_pages_forecasts.py).
- **Model/feature pipeline:** [scripts/research_core.py](scripts/research_core.py), [scripts/run_research.py](scripts/run_research.py).
- **Previous page specification:** [docs/PHASE_6_PREDICTION_PAGES.md](docs/PHASE_6_PREDICTION_PAGES.md).
- **Live Dhan API plan (superseded hosting path):** [docs/PHASE_7_LIVE_DHAN_INFERENCE.md](docs/PHASE_7_LIVE_DHAN_INFERENCE.md).
- **Current on-demand Actions flow:** [Phase 8 — GitHub Actions prediction](docs/PHASE_8_GITHUB_ACTIONS_PREDICTION.md), [workflow](.github/workflows/on-demand-prediction.yml), [runner](scripts/run_live_prediction.py), [request template](.github/ISSUE_TEMPLATE/prediction_request.yml).
- **Published live-result directory:** [docs/assets/predictions/](docs/assets/predictions/). A result is only fresh when its generation timestamp follows the request.
- **Backend service:** [live_api/app.py](live_api/app.py).
- **Automated backend deployment:** [.github/workflows/deploy-live-api.yml](.github/workflows/deploy-live-api.yml).
- **Deployment script:** [scripts/deploy_live_api_space.py](scripts/deploy_live_api_space.py).
- **Page API endpoint config (URL only):** [docs/assets/live-api-config.json](docs/assets/live-api-config.json).
- **Research manuscript:** [research/manuscript.md](research/manuscript.md).
- **Deployment workflow:** [.github/workflows/deploy-pages.yml](.github/workflows/deploy-pages.yml).
- **Research workflow:** [.github/workflows/nifty-research.yml](.github/workflows/nifty-research.yml).

**Current forecast record (last generated 2026-10-25 UTC):** as-of 2026-10-21 10:00 IST; target expiry 2026-10-27; model direction DOWN; model score for UP 0.3848. This is a previously generated exploratory forecast, not a new forecast for 2026-10-25. The data-quality gate remains **BLOCKED** because the 10:00 anchor is not independently validated. The page must show this warning and must not present the score as a probability of profit. No options strategy is certified.

**Live behavior (Phase 7):** Clicking Predict is wired to a secure backend that refreshes Dhan authentication, fetches or reuses DhanHQ one-minute NIFTY 50 bars through the selected date, rebuilds the research features and fits ExtraTrees on settled historical labels. Backend deployment is currently **BLOCKED by Hugging Face HTTP 402**: current Hugging Face docs say Docker Spaces on CPU-basic require an eligible Pro/Team/Enterprise plan. To enable live requests, either provide eligible Hugging Face compute or set HF_SPACE_ID to an existing writable Docker Space, or provide deployment credentials for an alternative host such as Render or Cloudflare. GOOGLE_API_KEY alone does not authorize deployment of a Google Cloud service. The page stays disabled until the secure endpoint is configured and passes `/health`; it never falls back to saved forecasts. See [Phase 7 plan](docs/PHASE_7_LIVE_DHAN_INFERENCE.md) and [deployment Actions](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions).

<!-- PHASE9_ANCHOR_AUDIT_STATUS_START -->
## Phase 9 — Historical anchor-source audit
- **Corrected public-archive comparison:** 1,269/1,269 overlapping 10:00–10:03 anchor timestamps match after timezone normalization.
- **Anchor-open differences:** median 0.05 points; P95 1.00 point; maximum 6.70 points; 62/1,269 sessions differ by over 1 point.
- **Weekly direction sensitivity:** 0/265 overlapping weekly labels changed when the secondary archive's anchor was substituted while preserving the recorded expiry close.
- **Interpretation:** diagnostic only. The secondary archive's underlying provider lineage is unverified; these results do not pass the independent-anchor gate.
- **Dhan cross-check:** [automated five-year audit workflow](.github/workflows/phase9-dhan-anchor-source-audit.yml); [script](scripts/audit_dhan_anchor_source.py); report will be committed after the workflow completes.
- **Logs and raw comparison:** [research log](logs/RESEARCH_LOG.md), [error log](logs/ERROR_LOG.md), [daily anchor comparison](data/reconciliation/anchor_source_comparison.csv), [weekly label sensitivity](data/reconciliation/weekly_anchor_label_sensitivity.csv), [summary report](data/reconciliation/anchor_source_comparison_report.json).
<!-- PHASE9_ANCHOR_AUDIT_STATUS_END -->

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


## Free GitHub Actions + Pages prediction flow

**Current implementation branch:** [`phase/github-actions-pages-free`](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/tree/phase/github-actions-pages-free)  
**Plan:** [Free Actions + Pages phase plan](docs/PHASE_GITHUB_ACTIONS_PAGES_FREE.md)  
**Workflow:** [Free scheduled prediction](.github/workflows/free-pages-prediction.yml)

- The scheduled workflow runs on weekdays at 10:30 IST and can also be started manually from GitHub Actions.
- Dhan credentials remain in GitHub Actions secrets. The workflow publishes a date-specific JSON record and `latest.json` for GitHub Pages.
- The Pages button only loads published records; it no longer creates a GitHub Issue or calls an external API. GitHub Pages cannot securely launch a private Actions run directly without an authenticated trigger.
- A missing/failed latest result is shown as unavailable rather than silently substituting a stale forecast.
- The workflow is merged to `main`; date-specific inference and publication have been verified for historical cutoff `2024-06-07` (Actions run [40204498793](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40204498793)).
- Trading readiness remains **BLOCKED** pending independent 10:00 anchor reconciliation, leakage-safe walk-forward evaluation, and executable option-level P&L including Paytm Money brokerage/fees, bid-ask spreads and slippage.


**Validation update (2026-10-25):** PR [#14](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/pull/14) was merged to prevent stale result publication and add selected-date workflow navigation. The historical inference run [40204498793](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40204498793) succeeded on rerun and published [the 2024-06-07 result](docs/assets/predictions/2024-06-07.json): direction UP, raw ExtraTrees UP score 0.5475, target expiry 2024-06-13, anchor 22,978.3, 132 training rows through 2024-06-06. This remains exploratory: anchor reconciliation and executable option costs/slippage are not validated.


**Pages navigation correction (2026-10-25):** The date form now loads the already-published date-specific JSON in place and does not redirect to GitHub Actions on submit. If that date has no published successful result, the page reports it as unavailable and the user can open Actions manually. Script cache-busting was added to reduce stale browser JavaScript. See the latest research/error logs for this correction.


**All-date session validation correction (2026-10-25):** The live inference gate now determines the first trading session after each verified weekly expiry from the official NSE daily-session reference, not from the dates that happen to be present in Dhan minute bars. Minute bars are still independently required for the 10:00 anchor and training/expiry features; missing market data will fail that explicit data gate instead of producing a false calendar rejection. Regression tests cover the 2026-05-05 → 2026-05-06 session transition.


**Selected-date data refresh (2026-10-25):** The workflow now refreshes the cached 90-day Dhan chunk containing the requested cutoff date before inference, while retaining cache-first behavior for all other historical chunks. This addresses stale/incomplete cache risk for the selected date. It does not fabricate a missing bar: if Dhan still returns no valid 10:00–10:03 bar, the date remains unavailable and logs should be inspected for provider/session coverage.


**Selected-date cache refresh status (2026-10-25):** PR [#16](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/pull/16) is merged and CI passed. The selected-date rerun has not yet occurred after merge; `2026-08-05.json` currently contains a safe failed status, not a fresh prediction. A separate legacy Docker Space/API deployment workflow failed at its external deployment step and is not part of the selected free GitHub Actions + Pages architecture. Do not treat that unrelated failure as a Pages deployment failure.


**Target-session retry and diagnostics (2026-10-25):** Inference now makes one targeted, one-day Dhan request for the selected session in addition to the normal chunked history request. This can recover bars omitted from a large response and helps distinguish session-level data gaps from broad-request truncation. If the required anchor is still unavailable, the failure explains whether the whole session had no valid bars or reports the returned session's timestamp range and nearby-bar count. The anchor is never silently substituted.

<!-- PHASE9_DHAN_ANCHOR_STATUS_START -->
## Phase 9 Dhan anchor audit
- Status: DIAGNOSTIC_ONLY. See [report](data/reconciliation/dhan_anchor_comparison_report.json) and [audit script](scripts/audit_dhan_anchor_source.py).
- Even a close recent match is diagnostic; provider/official source validation and the daily OHLC reconciliation gate remain mandatory.
<!-- PHASE9_DHAN_ANCHOR_STATUS_END -->
