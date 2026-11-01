# NIFTY Weekly Expiry Direction Research

## Current research status (BUP-01 — plan v1.3)

**As of 2026-11-01:** C0 PASS; C1 PARTIAL / CONTINUOUS-COVERAGE GATE IN PROGRESS. The user directed that no ETF holdings versus official NIFTY index-weight comparison is needed. The active method does not require official IWF, ETF portfolio holdings or reconstructed weight data. It forecasts point-in-time constituent stocks and uses strictly out-of-fold stock probabilities/returns, unweighted predicted breadth, cross-sectional dispersion, sector breadth and member coverage to predict the **observed NIFTY 50 index direction**. Equal-weight constituent-basket measures are diagnostics only, not the actual NIFTY return.

C1 evidence includes a 50/50 current-universe security-master check, 103 monthly membership reconciliations and separate 90-day Dhan stock-minute QA samples across 2021, 2022 and 2026. These are bounded samples, **not continuous five-year coverage**. The remaining C1 gates are continuous stock and NIFTY index 90-day-chunk coverage, verified weekly expiry dates, and complete dated ISIN/security-ID/corporate-action continuity. Accepted cycles need at least 47 valid constituent forecasts and at least 94% member coverage; at least 98% of scheduled eligible cycles must have valid observed NIFTY labels. No constituent panel, trained model, bottom-up forecast or cost-validated strategy exists.

**Active plan:** [BUP-01 pre-registered plan v1.3](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/RESEARCH_PLAN.md) · [C1 status](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/STATUS.md) · [developer gate report](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_DEVELOPER_GATE_REPORT.md)

**Historical (superseded) weight-source assessment:** [C1 historical weights alternatives](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_WEIGHT_ALTERNATIVES_ASSESSMENT.md) — source ranking, licensing constraints, reconstruction formula and C1 acceptance gates.


The archive/API follow-up is tracked in the [C1 archive audit](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_AMC_DISCLOSURE_ARCHIVE_AUDIT.md), [metadata probe script](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/scripts/constituent_weekly/probe_amcs_fund_metadata.py), [manual/push workflow](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/.github/workflows/bup01-c1-amcs-metadata-discovery.yml), and [API discovery report](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_AMCS_API_DISCOVERY_REPORT.md).

See the [C1 status](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/STATUS.md), [AMC probe report](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_AMC_ARCHIVE_PROBE_REPORT.md), [AMC archive audit](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_AMC_DISCLOSURE_ARCHIVE_AUDIT.md), [locked plan v1.3](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/RESEARCH_PLAN.md), and [developer gate report](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_DEVELOPER_GATE_REPORT.md).


## Latest automated research status

Last status refresh: 2026-10-30 23:42 UTC

- Run ID: 41145607225
- Target labels: 398
- Binary rows with sufficient features: 398
- Development / final holdout rows: 318 / 80
- Model selected on development data: extra_trees
- Calendar status: **OFFICIAL_EXPIRY_AND_EOD_CLOSE; ANCHOR_SOURCE_PROVISIONAL**
- Independently validated usable trading strategy: **NO**

The 10:00 anchor remains minute-archive-derived and independently unvalidated; executable contract-level performance is not tested.

The target uses official NSE expiry dates and daily closes. The 10:00 anchor is still minute-archive-derived and independently unvalidated. No executable futures/options P&L with broker charges, spreads, slippage and fills has been validated.

- Source CSV files: 19
- Valid minute bars after checks: 884714
- Official NSE daily closes matched: 1903
- Minute-archive closes differing from official close by >1 point: 1719
- Median absolute minute-vs-official close difference: 8.25 points
- Yahoo daily-close cross-check: available; compared rows: 2357; mismatches over tolerance: 0

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

Last repository status update: 2026-11-01.


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

## NIFTY options dual-sleeve backtest research

A separate options strategy study is underway on [research branch](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/tree/research/nifty-options-dual-sleeve-backtest) and [draft PR #22](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/pull/22). The limited B1 execution is tracked in [PR #24](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/pull/24).

- [Phase plan](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/research/nifty-options-dual-sleeve-backtest/research/options_backtest/PHASE_PLAN.md)
- [Data audit report](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/research/nifty-options-dual-sleeve-backtest/research/options_backtest/DATA_AUDIT_REPORT.md)
- [Machine-readable audit](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/research/nifty-options-dual-sleeve-backtest/research/options_backtest/data_audit_summary.json)
- [Historical NIFTY lot sizes](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/research/nifty-options-dual-sleeve-backtest/research/options_backtest/LOT_SIZE_SCHEDULE.md)
- [Paytm Money cost schedule](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/research/nifty-options-dual-sleeve-backtest/research/options_backtest/PAYTM_MONEY_COST_SCHEDULE.md)
- [B1 exploratory simulator](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/research/nifty-options-dual-sleeve-backtest/scripts/exploratory_positional_backtest.py)
- [Dhan data pipeline and current blocker](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/research/nifty-options-dual-sleeve-backtest/research/options_backtest/DHAN_DATA_PIPELINE.md)

**Current gate:** the public archive audit scanned 124,458,249 one-minute NIFTY option rows from 2024-10-01 to 2026-07-21. OHLC/timestamps and OI/volume completeness passed; 52.84% of rows have zero volume and 35 have negative volume. Only positive-volume bars are eligible for fills. The archive has no IV or bid/ask and does not cover 2021–2024. Dhan authenticated collection remains blocked. NIFTY spot has no traded volume, so the original VWAP condition needs verified NIFTY futures volume. The first B1 positional credit-spread exploratory simulator, unit tests and cached Actions workflow are now implemented on the research branch. Its automated run is pending. The proxy directional filter, reconstructed delta and no-VWAP treatment are explicitly exploratory; no profitability or risk metrics are claimed until execution completes.


### BUP-01 C1 data-feasibility update (2026-10-31)

**C0 governance:** PASS — the registered plan and structural regression tests passed.  
**C1 data gate:** IN PROGRESS / BLOCKED — no point-in-time constituent panel or stock model exists.

- [C1 source feasibility audit](research/constituent_weekly/C1_SOURCE_FEASIBILITY.md)
- [One-time sample integrity audit](research/constituent_weekly/C1_INITIAL_SAMPLE_AUDIT.md)
- [C1 source/rights register](research/constituent_weekly/DATA_SOURCE_REGISTER.md)
- [C1 status](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/STATUS.md)
- [C1 draft PR #26](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/pull/26)

The September 2026 official weight-report sample was parsed once for file/schema integrity: 50 unique NIFTY50 rows and a displayed weight sum of 100.0%. The report publication timestamp, historical coverage and basket reconciliation were not validated. The October archive's PDF was inventoried but not analysed. A third-party March 2026 current-members file differs from the September sample (WIPRO appears only in the candidate, BSE only in the sample), so it is not accepted as the current or historical truth.

**Data-rights safeguard:** NSE Indices Terms of Use restrict systematic/automated collection without express written consent and copying/distribution without prior written permission. Repeated NSE scraping and raw artifact uploads have been disabled. [Issue #27](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/issues/27) asks the repository maintainer to delete the earlier raw sample Actions artifact/cache. The C1 workflow is now offline-only for separately authorised archives.

The existing Dhan implementation refreshes a 24-hour access token and retrieves NIFTY index intraday bars; it does not yet prove stock-equity coverage. Dhan's published documentation states daily data are available from instrument inception, while intraday history is limited to five years for active instruments and requests to 90-day windows. A constituent-level API preflight and point-in-time weight/identity audit remain pending. **No constituent model, index prediction or strategy result is available.**


## C1 candidate source addition

The licensed CC BY 4.0 NIFTY 50 interval subset is now cached at [data/derived/constituent_weekly/nifty50_membership_intervals.csv](data/derived/constituent_weekly/nifty50_membership_intervals.csv); full attribution, coverage and quality caveats are in [C1_MEMBERSHIP_DATA_ATTRIBUTION.md](research/constituent_weekly/C1_MEMBERSHIP_DATA_ATTRIBUTION.md). The related ownership facts are a possible causal feature source after manifest broadcast-time joining, but they do not establish the official NIFTY free-float IWF. C1 remains blocked on exact weights, the post-Sep-2025 universe and Dhan stock intraday bars.


### Latest C1 execution note

- Offline C1 source-audit workflow: [run 41180457400](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41180457400) — SUCCESS, including offline parser tests. No authorised local weight archive was present; this is not a historical IWF pass.
- Dhan equity preflight workflow and mocked response tests are staged; no Dhan preflight run/result is visible yet. No stock bars or access-token data are claimed.
- The cached CC BY 4.0 membership subset and attribution are now linked above. It does not contain numeric weights and stops at 2025-09-30.

### Latest BUP-01 C1 checkpoint — 2026-10-31

- [Offline authorised-source audit](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41181684637): SUCCESS; no authorised local official-weight archive was present.
- [Dhan equity preflight](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41181684573): workflow SUCCESS and offline tests 9/9 PASS, but live Dhan profile authentication returned HTTP 401. No equity security IDs, 2018 daily bars or 1-minute stock bars were tested.
- [Dhan token-refresh PR #28](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/pull/28): mocked regression and integration Actions checks passed; PR #28 is ready for review with passing checks, but GitHub reports merge conflicts (`dirty`); it remains open/unmerged, so the main scheduled helper is not yet updated.
- C1 remains **BLOCKED** on Dhan profile/data entitlement, authorised point-in-time numerical free-float weights, post-2025-09 membership, security identity/corporate actions and basket reconciliation. No stock panel/model/forecast exists.
- Detailed gate record: [BUP-01 STATUS](research/constituent_weekly/STATUS.md), [C1 source feasibility](research/constituent_weekly/C1_SOURCE_FEASIBILITY.md), [data source register](research/constituent_weekly/DATA_SOURCE_REGISTER.md), [error log](logs/ERROR_LOG.md).

### Latest C1 Dhan diagnostic — 31 October 2026

- [Latest preflight run 41181948126](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41181948126): workflow passed; 10/10 offline tests passed. Live token-generation endpoint returned HTTP 200 but no `accessToken`; fallback token then failed profile authentication with HTTP 401.
- The profile request now matches Dhan's documented header shape (access-token only). No stock equity endpoint was reached and no bars were collected.
- **Actionable blocker:** verify the Dhan client ID, six-digit PIN, TOTP secret/TOTP enablement, and fallback token in organisation secrets. Dhan token validity is 24 hours and Data APIs require an active plan. See [Dhan authentication docs](https://dhanhq.co/docs/v2/authentication/).
- C1 remains BLOCKED on authentication, authorised point-in-time numeric free-float weights, current membership, corporate-action/security identity history and basket reconciliation. No constituent model/forecast exists.

- Additional public-source sweep: no permissively reusable official historical IWF series found. The HF 2008–2025 weights candidate is CC BY-NC-SA 4.0 and documents static/extrapolated intervals; GitHub alternatives are binary membership or best-effort reconstructions. See [C1 data-source register](research/constituent_weekly/DATA_SOURCE_REGISTER.md).


## BUP-01 Dhan authentication checkpoint — 2026-10-31

- Shared Dhan refresh helper corrected to POST on the C1 branch; token values are masked and exported only within the Actions job. BUP-01 preflight already used POST.
- Run [41182555655](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41182555655): 10/10 offline tests passed; live token endpoint returned HTTP 200 without an access-token field; fallback profile returned HTTP 401. No equity data calls were reached.
- Safe error-category diagnostics and a regression test have been added; the follow-up run is pending/in progress. C1 remains blocked; no constituent model or strategy result exists.


## 2026-10-31 — Dhan authentication succeeded; constituent coverage partially verified

- Follow-up Actions run [41182679514](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41182679514) completed successfully. The fresh TOTP request returned a valid access token; the profile authenticated (HTTP 200); the Data API plan is active; all 5/5 current scrip-master probe symbols resolved.
- Historical daily probe passed with 22 bars for 2018-01-01 to 2018-02-01. Historical one-minute probes passed for all 5 symbols on 2022-10-31 (374 bars each, including the 10:00 anchor and 15:25–15:29 close window).
- Recent-session probe on 2026-10-30 returned 359 bars per symbol and 10:00 anchors, but no 15:25–15:29 bars; targeted close-window requests returned empty arrays (0/5). Overall status remains PARTIAL_OR_BLOCKED; do not treat the recent session as complete.
- Offline Dhan tests: 11 passed. No credentials, token values, raw bars, prices or security IDs were stored.
- A one-date follow-up probe for 2026-10-29 has been committed and its Actions run is pending/in progress; this will distinguish a date-specific gap from a recent-history limitation. C1 remains blocked pending point-in-time weights, current membership, identifier/corporate-action history and full coverage validation.


## 2026-10-31 — Follow-up date probe inconclusive; Dhan workflow hardened

- The 2026-10-30 preflight result remains the verified successful run: fresh TOTP token, profile HTTP 200, active Data API plan, 5/5 current symbols resolved, 22 historical daily bars, and 5/5 historical intraday windows on 2022-10-31. The 2026-10-30 recent-session sample had 10:00 anchors but no 15:25–15:29 close bars (0/5).
- Follow-up run [41182764467](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41182764467) attempted the 2026-10-29 probe but could not obtain a fresh token (HTTP 200 without accessToken); fallback profile returned HTTP 401. No price endpoints were called. This run is INCONCLUSIVE, not evidence that 2026-10-29 bars are unavailable.
- Hardened workflow so pull-request checks run offline tests only, Dhan calls are serialized, and editing the workflow file alone does not consume another TOTP token. Offline tests passed 11/11 on the last live preflight.
- Dhan official guidance states access tokens are valid for 24 hours, API-key/secret authentication is the intended automation route, and at most five active tokens may be retained simultaneously. Avoid repeated token-generation loops. Sources: https://dhanhq.co/docs/v2/authentication/ and https://dhan.co/support/platforms/dhanhq-api/how-many-access-tokens-can-i-generate-for-my-dhan-account/.
- C1 remains BLOCKED: recent-session close coverage and point-in-time index data/rights gates remain unresolved. No constituent model or trading result exists.

## BUP-01 constituent-level weekly expiry research

**Current status (2026-10-31): C0 PASS; C1 BLOCKED / RIGHTS-DEPENDENT.** No constituent panel, stock model, bottom-up forecast or trading strategy has been validated. C2 model work remains gated until point-in-time membership, official numerical free-float weights, security/corporate-action mappings and full stock-bar coverage pass.

- [BUP-01 status](research/constituent_weekly/STATUS.md)
- [BUP-01 source register](research/constituent_weekly/DATA_SOURCE_REGISTER.md)
- [BUP-01 research log](logs/RESEARCH_LOG.md)
- [BUP-01 error log](logs/ERROR_LOG.md)
- [BUP-01 visible conversation log](logs/CONVERSATION_LOG.md)

Official methodology requires free-float IWF and specified strategic-holding exclusions. NSE website terms restrict automated collection and reuse, so automated website scraping remains disabled pending permission/licence confirmation. Dhan intraday documentation covers active instruments only; inactive/delisted coverage still requires proof. No additional Dhan token refresh was attempted during this update.

## BUP-01 constituent-level weekly expiry research — membership audit update (2026-10-31)

**Membership sub-gate:** PASS WITH LIMITATIONS. **Overall C1:** BLOCKED. No bottom-up model or trading strategy is authorised yet.

- [Point-in-time NIFTY 50 membership intervals (CC BY 4.0)](data/constituent_weekly/nifty50_membership_intervals.csv)
- [Membership data provenance and attribution](research/constituent_weekly/MEMBERSHIP_DATA_PROVENANCE.md)
- [Machine-readable membership audit](research/constituent_weekly/C1_MEMBERSHIP_AUDIT.json)
- [Membership integrity regression tests](tests/test_bup01_membership_intervals.py)
- [Automatic/manual GitHub Actions workflow](.github/workflows/bup01-c1-membership-tests.yml)

The corrected 86-row project ledger contains 85 distinct symbols. It validates 50 unique entries on 102/103 month-end snapshots and 51 on 2025-10-31 because the official temporary zero-price DUMMYTATAM placeholder was active. Tata Motors is mapped as TATAMOTORS through 2025-10-23 and TMPV from 2025-10-24; DUMMYTATAM is explicitly flagged non-tradable. The 2026 WIPRO-to-BSE reconstitution is also applied. The source contains no numerical weights. Exact historical free-float IWF, legacy ISIN/security identity, remaining corporate actions and full constituent intraday/expiry-close coverage remain open; Phase C2 stays gated. The membership workflow uses offline tests only and makes no market-data or authentication calls. The final corrected workflow run [41185169548](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41185169548) succeeded with 6 tests passed.


## 2026-10-31 — Conversation recovery checkpoint

The ChatGPT conversation encountered a send/response transport error during a sequence of audit/provenance update messages. Repository state was independently checked before continuing; no duplicate data run or Dhan token refresh was triggered.

- Membership integrity Actions run [41185169548](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41185169548): **SUCCESS; six tests passed** (verified from job status).
- Membership sub-gate: **PASS WITH LIMITATIONS**.
- Overall constituent research gate C1: **BLOCKED** pending licensed exact historical free-float IWF, security identity/ISIN and corporate-action mapping, and complete constituent intraday/expiry-close coverage.
- C2 model construction remains prohibited until all C1 gates pass. No bottom-up prediction or trading strategy is validated.
- See [research log](logs/RESEARCH_LOG.md), [error log](logs/ERROR_LOG.md), [conversation log](logs/CONVERSATION_LOG.md), and [BUP-01 status](research/constituent_weekly/STATUS.md).


## C1 source audit — recovery continuation (2026-10-31)

The bounded free-source review did not clear the remaining C1 gates. Official NSE Indices historical constituent identifiers, market capitalisation, weights and prices are offered through a licensing/subscription route ([NSE Indices data subscription](https://www.nseindia.com/static/nse-indices/index-data-subscription)). The discovered Hugging Face historical-weight series is CC BY-NC-SA 4.0 and the public GitHub alternative uses equal-weighted/binary approximations; neither is accepted as an exact, rights-cleared trading input. [Dhan's v2 documentation](https://dhanhq.co/docs/v2/historical-data/) describes five-year minute history for active instruments with 90-day request windows, not guaranteed inactive/delisted coverage.

**Decision unchanged:** membership integrity sub-gate PASS WITH LIMITATIONS; overall C1 BLOCKED; C2 remains gated. No bottom-up model or strategy is claimed. See [research log](logs/RESEARCH_LOG.md) and [error log](logs/ERROR_LOG.md).


## Dhan-first constituent data plan — 2026-10-31

User confirmed Dhan as the available data source. The next constituent data gate will prioritize the existing Dhan Data API subscription for historical daily/intraday OHLCV and security-ID resolution, using cache-first bounded batches and coverage checks for active and delisted/inactive constituents. Required observations include forecast-time anchor bars and expiry-close bars. Authentication is serialized and credentials remain in GitHub Actions secrets.

Dhan price data must not be misrepresented as official historical NIFTY free-float IWF. Exact point-in-time weights, membership/security identity/corporate actions and full constituent price coverage remain separate gates. C1 is still BLOCKED; no C2 model or strategy is claimed. See [BUP-01 status](research/constituent_weekly/STATUS.md) and [research log](logs/RESEARCH_LOG.md).

## BUP-01 — Dhan full-universe audit code update (2026-10-31)

The C1 Dhan preflight now derives the active 2026-10-31 tradable NIFTY 50 universe and the full historical tradable symbol/alias set from the point-in-time membership ledger, then resolves both against the current Dhan scrip master. It excludes the non-tradable DUMMYTATAM placeholder and reports resolution counts separately from the five-symbol candle probe. Security IDs and raw bars are not committed. A current scrip-master match is not proof of historical ID coverage for inactive/delisted securities.

- Code commit: 05b71dc111779ef40da748319f7d109a012c4451.
- Offline validation: [Actions run 41223379333](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41223379333), SUCCESS; 13 tests passed.
- The live Dhan step was skipped because this run was a pull-request event; this is an intentional secret-safety guard. Full-universe ID counts have not yet been measured. The protected live test must be started using the [C1 Dhan workflow](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/workflows/constituent-weekly-c1-dhan.yml) with workflow_dispatch on the C1 branch.
- Latest successful live probe [41182679514](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41182679514) still covers only five sample stocks and remains partial for recent expiry-close bars.

Status: C1 BLOCKED; C2 not authorised. No bottom-up stock model, index aggregation or trading strategy exists yet. See [BUP-01 status](research/constituent_weekly/STATUS.md), [research log](logs/RESEARCH_LOG.md), and [error log](logs/ERROR_LOG.md).

## BUP-01 — Live Dhan full-universe result (2026-10-31)

Protected live run [41224048773](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41224048773) succeeded: fresh TOTP token/profile authentication succeeded and the Dhan Data API plan was active.

| Gate | Result |
|---|---:|
| Current active NIFTY 50 scrip-master resolution | **50/50** |
| Historical membership symbols found in current master | **79/84** |
| Five-stock 2022-10-31 one-minute history | **5/5 PASS** |
| Five-stock 2026-10-29 expiry-close window | **0/5** |

The five historical symbols/aliases absent from today's Dhan master are HDFC, JPASSOCIAT, MCDOWELL-N, RANBAXY, and TATAMOTORS. This is a current-master lookup limitation, not proof that historical prices cannot be retrieved; dated successor/security-ID mappings must be established before acquisition. The recent sample feed returned 359 one-minute bars per symbol through 15:14 IST, with 10:00 anchors but no 15:25–15:29 expiry-close bars; separate 15:20–15:30 requests were empty for all five symbols.

The workflow committed sanitized diagnostics to the C1 branch. No raw OHLCV bars, security IDs, access tokens, PINs or TOTP secrets were stored. **C1 remains BLOCKED; C2 remains gated.** See [C1 phase status](research/constituent_weekly/STATUS.md), [sanitized Dhan preflight](research/constituent_weekly/C1_DHAN_PREFLIGHT.json), [research log](logs/RESEARCH_LOG.md), and [error log](logs/ERROR_LOG.md).

## BUP-01 latest Dhan preflight — 2026-10-31

The protected live Dhan run [41223795394](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41223795394) authenticated successfully, confirmed an active Data API plan, and resolved **50/50 current NIFTY 50 symbols** against the current Dhan scrip master. **79/84 historical membership aliases** were present in that current master; this is not proof of historic security-ID continuity for inactive/delisted securities.

The bounded five-stock price probes found 22 daily bars for January 2018, and all five stocks passed the 31 October 2022 one-minute anchor/expiry-close checks. The recent 29 October 2026 sample had 10:00 anchors but no 15:25–15:29 close bars for any of the five; targeted close-window requests were empty (0/5). A later authentication-only retry returned HTTP 200 without an access token and the fallback profile check returned HTTP 401; no data requests were made in that retry.

The first workflow revision did not persist generated diagnostics after an autostash/rebase. The commit step was corrected, and the sanitized successful-run report plus the subsequent auth-only failure are now preserved in the C1 branch:
- [C1 status](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/STATUS.md)
- [Successful-run sanitized report](research/constituent_weekly/C1_DHAN_PREFLIGHT.json)
- [Latest auth-only attempt](research/constituent_weekly/C1_DHAN_LAST_ATTEMPT.json)

**Gate decision:** C1 remains BLOCKED. No constituent price panel, stock model, NIFTY aggregation, or trading strategy is approved. The remaining blockers include five unresolved historical aliases, actual historic IDs for inactive/delisted securities, recent expiry-close coverage, point-in-time numerical free-float weights, and basket-to-index reconstruction.

### BUP-01 correction — successful persistence run

A subsequent fresh-token live run [41224048773](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41224048773) also passed the protected workflow and successfully committed its sanitized result as branch commit d5a82d8. It reproduced the 50/50 current-universe and 79/84 historical-alias counts, plus the same bounded price-coverage findings. This is the latest successful live Dhan report; the earlier auth-only failure was transient and is retained separately for audit. C1 remains BLOCKED by missing recent expiry-close bars and the unresolved historical/weight gates.



## 2026-11-01 — Bottom-up C1 expiry proxy and historical-weight data acquisition

Latest C1 research branch commit: [9eac677](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/commit/9eac677b26ebcc682f9d90060d3ceabff7f0c73e). Live evidence: [Dhan preflight run 41247509692](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41247509692), successful.

- **Expiry definition updated by user direction:** use the close of the last available 1-minute candle timestamped from 15:00 through 15:14 IST as the 15:15 expiry proxy. This is explicitly a proxy, not an exchange 15:30 close. The five-stock/two-date live sample passed 10/10 with the recorded proxy timestamp 15:14 IST. The obsolete 15:25–15:29 requirement and targeted late-window requests have been removed.
- **Current universe:** 50/50 active NIFTY 50 symbols resolve in Dhan's current scrip master. **Historical identities:** 79/84 historical membership symbols match the current master. This count is not proof of complete historical OHLCV. HDFC Ltd's documented legacy security identifier returned valid intraday samples for 2022-10-31 and 2023-06-30 (2/2). JPASSOCIAT, RANBAXY and MCDOWELL-N occur only in the project's 2014 ledger and are outside the confirmatory period beginning 2018-04. TATAMOTORS/TMPV remains a dated corporate-action identity transition; do not concatenate pre/post-demerger prices without adjustment.
- **Weights acquired and cached:** [nifty50_weights_monthly.csv](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/data/constituent_weekly/nifty50_weights_monthly.csv) — 216 date rows, 100 ticker columns, 2008-01-31 to 2025-08-31, row sums within 4.3e-14 of 100. SHA-256: `3a3441a997b64a54363b38ebc02807e82cc0e0affd2efda147d1b7758a0b10cb`. Source: Sukrit Bera (2025), Figshare DOI 10.6084/m9.figshare.30217915, pinned Hugging Face revision; licence **CC BY-NC-SA 4.0** (commercial use not permitted). Source compiles official index reports but includes estimated/extrapolated event weights and author corporate-action handling; it is provisional research data, not an official daily IWF series.
- **Official cross-check source found:** NSE All Reports contains the report family “Market Capitalisation, Weightage, Beta for NIFTY 50 & NIFTY Next 50” and an “Indices - Market Capitalisation & Weightage” archive. NSE index-data subscription includes constituent identifiers, market cap, weights and prices. Automated scraping is not enabled pending terms/licence review. The candidate weight file ends 2025-08-31; 2025-09 onward still needs an authorized source.
- Dhan authentication and the active Data API plan passed. The bounded test includes five symbols, not a bulk historical constituent panel. No full-universe OHLCV coverage or basket-to-index reconstruction is certified.

Research artifacts: [phase status](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/STATUS.md), [Dhan diagnostics](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_DHAN_PREFLIGHT.json), [weight-source audit](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_WEIGHT_SOURCE_AUDIT.md), [weight audit JSON](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_NIFTY50_WEIGHT_AUDIT.json), [historic symbol identity review](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_HISTORICAL_SYMBOL_IDENTITY.md), [user decisions](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_USER_DECISIONS.md), [licence notice](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/data/constituent_weekly/NIFTY50_WEIGHTS_SOURCE_LICENSE.md).

**Gate decision:** C1 remains NOT PASSED until the 2025-09 onward weight gap and official/source reconciliation, full historical security identity/corporate actions, all required constituent price coverage and basket reconstruction pass. C2/model training remains gated. Do not use this CC BY-NC-SA cache commercially.

### Follow-up validation — 2026-11-01

The subsequent status/validator correction was also pushed and validated: [run 41247674443](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41247674443) completed SUCCESS with **18 tests passed**. The report renderer now records 10/10 expiry-proxy checks, HDFC legacy samples 2/2, 216-row historical weights cache and the CC BY-NC-SA non-commercial restriction. The warning from the first validator version was removed using NumPy finite/range checks. Current phase report: [C1 status](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/STATUS.md). Overall C1 remains NOT PASSED; no C2 model or trading strategy is claimed.


## BUP-01 latest C1 source-audit update — 2026-11-01

- Plan v1.1 now applies the user's 15:15 expiry proxy consistently to both constituent and index targets; the 15:30 official close is a separate sensitivity.
- Free-source minute-data search found a public 2012–2023 GitHub archive with 47/50 NIFTY 50 member files on 2022-11-03 and 2022-11-04; DIVISLAB, SBILIFE and APOLLOHOSP are absent. Five sampled stocks and the NIFTY index file had 10:00–10:03 anchor rows and a 15:14 bar on 2022-11-03.
- The archive's README claims MIT but the fork and inspected upstream root have no LICENSE file; it is not imported. Other candidates are either non-commercial/research-only, lack verified licence, or are not downloadable yet.
- Dhan's current documentation confirms minute history up to five years for active instruments and 90-day request windows, and daily history from inception; it does not guarantee intraday data for inactive/delisted symbols.
- C1 is still NOT PASSED. No canonical constituent panel, bottom-up model, index forecast or strategy exists. [C1 source audit](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_PUBLIC_INTRADAY_SOURCE_AUDIT.md) · [Research plan v1.1](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/RESEARCH_PLAN.md) · [C1 status](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/STATUS.md)


## BUP-01 new evidence — Dhan full-universe check and official weight snapshot

- The protected Dhan run [41249642409](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41249642409) resolved and passed **50/50** point-in-time current NIFTY 50 symbols on 2026-10-29 for one-minute bar coverage/quality. All passing symbols had four 10:00–10:03 bars and a 15:14 proxy bar. This is one session only; it does not imply full historical coverage or index reconstruction.
- The NSE Indices March 2026 white paper publishes the full NIFTY 50 weights on 2026-02-27. A 50-row transcription is cached as [official 2026-02-27 snapshot](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/data/constituent_weekly/nifty50_official_weights_2026-02-27.csv) with a source note. Rounded weights total 100.02%; published values are not normalised. This is one-date evidence only, not a historic series.
- A Hugging Face 1-minute dataset (2022–2026) declares MIT and describes daily data to 2000, but explicit feed provenance is missing and the card warns against use as a primary live-trading source. It remains exploratory/not admitted.
- C0 governance run [41249521876](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41249521876) and source-audit run [41249642494](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41249642494) passed. C1 remains NOT PASSED; no bottom-up model or strategy is certified.


## Official monthly weights archive — permission gate (2026-11-01)

- Located the official NSE Indices monthly "Market Capitalisation, Weightage, Beta" ZIP family. Independent documentation reports 159 monthly files from June 2013 onward; a public code example shows the `mcwb_{mon}{yy}.zip` naming convention. This project has not retrieved or parsed the ZIPs in this review.
- The NSE research-data policy lists historical reports/index data for research/analysis, but Nifty Indices site terms separately restrict systematic/automated collection without express written consent. Permission for automated recurring retrieval, caching and this research-to-personal-trading workflow is not unambiguous.
- Automated retrieval stays disabled until written permission or a suitable licence is confirmed. No scrape or ZIP download was performed. [C1 archive terms audit](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_OFFICIAL_WEIGHTAGE_ARCHIVE_TERMS_AUDIT.md).
- Current evidence remains: Dhan full-universe 50/50 one-session pass [run 41249642409](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41249642409); C0 validator pass [run 41249521876](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41249521876); C1 offline source audit pass [run 41249967298](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41249967298). C1 is NOT PASSED; C2 remains gated.


## Latest C1 Dhan evidence (2026-11-01)

- One-day full-universe Dhan preflight: **50/50** current NIFTY 50 symbols passed bar QA on 2026-10-29 in run [41249642409](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41249642409).
- 90-day sample: **3/3** (RELIANCE, TCS, INFY) passed on 2022-10-03–2022-12-30 in run [41250854958](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41250854958), with 61 normal sessions, valid anchor/expiry-proxy coverage, no duplicate timestamps and OHLCV invariants passing. The evening-only Diwali Muhurat session is tracked separately.
- A larger 50-stock/90-day run was attempted but blocked by a transient Dhan token-refresh response and expired fallback token in run [41251079084](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41251079084). A bounded retry and last-success preservation were added; current validation is run [41251346795](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41251346795).
- No full five-year panel or point-in-time weights series is yet validated. C1 remains NOT PASSED; C2/model training remains gated.


## C1 milestone — complete 50-stock 90-day minute coverage check (2026-11-01)

- Dhan preflight run [41251346795](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41251346795) passed fresh authentication, 23 offline tests and the complete 50-stock 90-day panel slice (2026-06-29–2026-09-26).
- 50/50 point-in-time security IDs resolved; 50/50 stocks passed. Each symbol returned 23,414 bars over 64 regular sessions, with 64/64 10:00 anchors and 64/64 15:14 expiry-proxy sessions, zero missing bars, zero duplicates and OHLCV invariants passing (1,170,700 aggregate rows).
- The three-stock older 2022 90-day sample passed 3/3 in [run 41250854958](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41250854958); the one-day current universe passed 50/50 in [run 41249642409](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41249642409).
- Full result: [C1 Dhan 90-day validation report](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_DHAN_90D_RANGE_VALIDATION.md).
- C1 remains NOT PASSED: this is one recent quarter, not a five-year panel. Legacy/inactive constituent history, corporate-action treatment for minute data, official authorised weights and basket-to-NIFTY reconstruction remain unresolved. No model or strategy has been trained or claimed.


## C1 milestone — historical 2022 full-basket coverage passed (2026-11-01)

- Run [41251808946](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41251808946) passed the full point-in-time NIFTY 50 basket for 2022-10-03–2022-12-30: **50/50 security IDs resolved and 50/50 passed**.
- Each member had 61 regular sessions, 61/61 10:00 anchor coverage and 61/61 15:14 expiry-proxy coverage. No duplicate timestamps or OHLCV invariant failures. Aggregate per-symbol bar count: **1,146,180**.
- This includes HDFC Ltd legacy security ID 1330 and the period-specific TATAMOTORS→TMPV mapping. The later demerger/rename prices are not stitched.
- Together with the 2026Q3 full-basket result [41251346795](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41251346795), two separated quarter-slices are now validated. This is not proof of continuous five-year coverage.
- Details: [2022 historical validation report](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_DHAN_HISTORICAL_2022_90D_VALIDATION.md). C1 remains NOT PASSED; official weight series, continuous coverage, corporate actions and NIFTY reconstruction remain open.


## Five-year-edge validation — investigation in progress (2026-11-01)

- The 2021-11-01–2022-01-29 Dhan check resolved all 50 security IDs and returned 1,233,597 bars, but strict QA initially failed due to one shared anchor-session gap and after-hours OHLCV flags.
- NSE confirms 4 November 2021 was an evening-only Muhurat session (18:15–19:15). The validator also included rows after 15:30 in OHLCV checks. Both issues have been corrected and regression tests added.
- Corrected run: [41252703953](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41252703953), pending final outcome. Do not treat the oldest edge as passed until the corrected report is published.


## BUP-01 latest verified state — 2026-11-01

The screenshot's earlier handoff predates the latest C1 evidence. The full 50-stock/90-day check is no longer a single pending run: two separated full-universe windows have passed, but this does **not** establish uninterrupted five-year coverage.

- **2026Q3 window:** [Actions run 41251346795](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41251346795) passed 50/50 point-in-time constituents for 2026-06-29–2026-09-26 (64 regular sessions per symbol, 64/64 anchors and 15:14 expiry proxies, no duplicate timestamps or OHLCV invariant failures).
- **2022Q4 window:** [Actions run 41251808946](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41251808946) passed 50/50 constituents for 2022-10-03–2022-12-30 (61 regular sessions per symbol, 61/61 anchors and expiry proxies, no duplicate timestamps or OHLCV invariant failures).
- **One-session current universe:** [Actions run 41249642409](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41249642409) passed 50/50 for 2026-10-29. These independent samples must not be presented as complete continuous five-year coverage.
- **Latest workflow [41263593605](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41263593605):** offline tests passed 26/26, but the live Dhan preflight was **BLOCKED_PROFILE_HTTP_401**. Dhan's token endpoint returned HTTP 200 twice without an access token; the sanitized diagnostic category was TOTP rejected/invalid, and the provided-token fallback failed the profile check with HTTP 401. No market-data endpoints ran. The green workflow conclusion was therefore not a live data pass. The current C1 workflow source now contains a final fail-closed status gate after the diagnostics commit, but run 41263593605 did not execute that step; runtime enforcement remains unverified.
- **2021 five-year edge:** [run 41252703953](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41252703953) originally stopped at an offline counter assertion (Muhurat exclusion miscounted as post-market). The code/test correction is now covered by the 26/26 passing suite, but the 2021 live data request is still untested because authentication is blocked.
- **Weights:** the cached third-party 216-row monthly candidate ends 2025-08-31, is CC BY-NC-SA 4.0 (non-commercial), and includes estimated/extrapolated event weights. It is not accepted as official point-in-time IWF for a trading workflow. Automated NSE Indices scraping remains disabled pending written permission/licensing.
- **Gate decision:** C0 PASS; **C1 NOT PASSED / RIGHTS + DATA BLOCKED**; C2–C6 remain gated. No constituent panel, stock model, bottom-up NIFTY forecast, or executable strategy is certified.

**Next dependency:** verify/correct the organization GitHub Actions Dhan credentials (do not post secret values in chat), then perform one bounded protected retry. Do not repeat TOTP attempts while credentials remain rejected. After authentication succeeds, first finish the 2021 edge window and historical identity checks, then test continuous intervals; only after authorized point-in-time weights, complete coverage and basket-to-index reconciliation pass may C2 begin.

- [Detailed C1 status](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/STATUS.md)
- [C1 research log](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/logs/RESEARCH_LOG.md)
- [C1 error log](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/logs/ERROR_LOG.md)
- [C1 continuation / workflow correction commit](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/commit/45714d20000c307684bca06efa46c09458689475)


## Bottom-up C1 continuation — 2026-11-01

**Dhan bounded data QA: PASS. Overall C1: NOT PASSED / RIGHTS-BLOCKED.** The bottom-up index prediction track is separate from the index-only ExtraTrees results above; there is no bottom-up stock panel, model, forecast or approved strategy yet.

- Protected Dhan preflight [run 41266897788](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266897788) passed its final fail-closed gate. TOTP refreshed on attempt one, the Data API plan was active, and the server/runner clock difference was -1 second.
- Full 50-stock 90-day QA passed **50/50** for each of three separated windows: 2021-11-01–2022-01-29, 2022-10-03–2022-12-30 and 2026-06-29–2026-09-26. The 2026-10-29 one-session probe also passed 50/50. These windows do **not** establish continuous five-year coverage.
- The SHREECEM negative-volume record was timestamped 15:29 on 2021-12-30, after the registered 15:15 expiry-proxy cutoff. The target checker validates through 15:14 and separately records post-cutoff anomalies. Baseline offline regression suite [run 41266922851](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266922851): **43 passed**. After adding IWF formula tests, corrected offline suite [run 41269516064](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41269516064): **50 passed**.
- C1 remains blocked by the absence of an admissible, complete point-in-time official IWF series and a verified mapping of the 22 official free-float exclusions, followed by weighted basket-to-index reconciliation. The detailed XBRL category candidate's specific compressed-CSV licence scope is unclear; official monthly weight downloads remain permission-gated. No approximate/equal weights are substituted.
- The 22-exclusion matrix and mathematical audit are now committed. The official worked example reproduces IWF **0.608794** using total shares as denominator and six-decimal rounding. The third-party parser uses a different A+B+C2 percentage base; its percentages cannot be substituted for IWF. Unit tests reject duplicate share-position deductions and unresolved exclusion coverage. No historical IWF values have been reconstructed.
- TejHQ daily EOD and corporate-action data is a secondary research cross-check candidate only. Its publisher permits personal research and private storage, but prohibits raw redistribution; this public repository will not cache its raw data. It supplies neither intraday target bars nor official NIFTY IWF weights.
- **C2–C6 remain gated under the locked BUP-01 v1.1 plan.** No options/stock trading strategy is certified. Any eventual execution study must use date-effective Paytm Money costs, spreads, slippage and realistic fills.

Detailed phase files (C1 branch): [status](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/STATUS.md), [registered plan v1.1](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/RESEARCH_PLAN.md), [Dhan 90-day validation report](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_DHAN_90D_VALIDATION_REPORT.md), [IWF/rights audit](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_OFFICIAL_WEIGHTAGE_ARCHIVE_TERMS_AUDIT.md), [22-exclusion mapping](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_IWF_EXCLUSION_MAPPING.csv), [IWF math audit](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_IWF_MAPPING_AUDIT.md), [C1 developer gate report](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_DEVELOPER_GATE_REPORT.md), [NSE data-rights request template — not sent](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/NSE_DATA_RIGHTS_REQUEST.md), [toolchain evaluation](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/TOOLING_EVALUATION.md), [research log](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/logs/RESEARCH_LOG.md), [error log](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/logs/ERROR_LOG.md), [visible conversation log](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/logs/CONVERSATION_LOG.md).

The remaining C1 blockers are permissioned access to complete point-in-time official IWF/constituent weights for the intended algorithmic-trading research use; continuous five-year constituent coverage and dated security/corporate-action identity mapping; and subsequent 98%-coverage weighted basket-to-index reconciliation. NSE's academic research-data route is explicitly non-commercial and not for trading/profit; a commercial-use agreement or explicit written authorization is required before automated retrieval/cache and model training for this intended use. No request has been sent.


## mfdata.in independent history-source check — 2026-11-01

The [mfdata.in documentation](https://mfdata.in/docs) describes a no-key search and a family-level history endpoint that returns available month labels. The C1 probe [run 41297143071](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41297143071) passed 13/13 parser tests, but its three bounded discovery routes returned HTTP 522. No family ID was found and the history endpoint was not reached. Coverage is therefore **inconclusive**, not zero. The API is not yet an admitted source: underlying-data rights, original-source lineage and publication timing remain unverified. No holdings values were downloaded. See the [sanitised report](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_AMCS_API_DISCOVERY_REPORT.md), [C1 status](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/STATUS.md), and [research/error logs](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/tree/phase/constituent-weekly-outcomes-c1-data/logs).



## Original AMC disclosure locator — 2026-11-01

A complementary source path is [amcs.fund's monthly archive](https://amcs.fund/month) and [methodology](https://amcs.fund/methodology). The provider says it reads each AMC's original monthly file, takes the date printed inside the disclosure, links the original file and an Internet Archive copy, and flags partial months. Existing C1 probes reached amcs.fund metadata/month routes, but did not admit holdings values or prove continuous NIFTY 50 ETF history. Treat this as an original-source locator and cross-check, not official NIFTY IWF: ETF weights differ from the index and source-use rights remain to be checked. More detail is recorded in the [C1 phase status](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/STATUS.md) and [research log](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/logs/RESEARCH_LOG.md).



<!-- PHASE3_STATUS_START -->
**Phase 3 source gate:** BLOCKED — checked 402 candidate expiry dates; official close mismatches >1 point: 1719.
See [source reconciliation report](data/reconciliation/source_reconciliation_report.json) and [Phase 3 plan](docs/PHASE_3_SOURCE_RECONCILIATION.md).
<!-- PHASE3_STATUS_END -->



## BUP-01 v1.3 aggregation and source-use policy — 2026-11-01

No ETF-holdings-versus-index-weight comparison will be performed. The new index prediction uses strictly out-of-fold constituent stock forecasts and unweighted cycle-level breadth, probability/return summaries, dispersion and sector signals to predict the observed NIFTY 50 index label. An equal-weighted constituent basket is not an index-return reconstruction. The older IWF/ETF work products remain historical audit records only and are not active model inputs.

The Dhan C1 workflow no longer refreshes the historical weight cache. The Nippon AMC workflow is now offline parser tests only; bulk workbook downloads are paused because explicit reuse permission for the intended trading research was not established. C1 remains in progress on continuous stock/index candle coverage, expiry dates and historical security/action identity. See [plan v1.3](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/RESEARCH_PLAN.md), [status](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/STATUS.md), [user decisions](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_USER_DECISIONS.md), and [research log](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/logs/RESEARCH_LOG.md).


## C1 identity audit update — 2026-11-01

A dated security-alias layer now translates canonical membership symbols to the exchange ticker actually traded at each date. This corrects LTIMindtree's 2023–2024 NIFTY membership interval to the actual symbol LTIM (not later symbol LTM), and captures the ZOMATO/ETERNAL, TATAGLOBAL/TATACONSUM and TATAMOTORS/TMPV transitions. HDFC Ltd remains distinct from HDFCBANK, and the Tata Motors demerger ex-date is not treated as a continuous raw-price interval. See [security alias history](data/constituent_weekly/security_alias_history.csv), [major corporate-action events](data/constituent_weekly/security_corporate_action_events.csv), [identity resolver](scripts/constituent_weekly/security_identity.py), and [C1 identity review](research/constituent_weekly/C1_HISTORICAL_SYMBOL_IDENTITY.md).

This is a major-identity correction, not the exhaustive adjustment ledger for dividends/splits/bonus/rights actions; C1 remains PARTIAL. [Latest C1 status](research/constituent_weekly/STATUS.md).


## C1 data-gate update — 2026-11-01

The live Dhan intraday target-data sub-gate has passed: **258/258 weekly expiry cycles** had valid observed NIFTY anchor/expiry target pairs, all 258 met the registered >=47 stock / >=94% point-in-time constituent coverage rule, 154 confirmatory cycles remained after the 104-cycle warm-up, zero active symbols were unresolved, and 1,083 requests ran across 21 windows. One index window was labelled PARTIAL_TARGET_DATES. The full artifact later showed the only partial check was the extra 15:14 check on 26-Apr-2024, an anchor-only date (10:00 anchor passed); the actual expiry proxy on 02-May-2024 passed. See the [durable result JSON](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_CONTINUOUS_COVERAGE_RESULT.json), [window report](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_CONTINUOUS_COVERAGE_REPORT.md), and [error log E0070](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/logs/ERROR_LOG.md).

The separate [Dhan daily OHLCV audit](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41316751830) completed successfully with **106,385/106,392 valid point-in-time member-sessions (99.9934%)**. A guarded TejHQ fallback added 1,295 HDFC sessions; six HDFC sessions and one TATAMOTORS session remain unresolved and are listed by date in the [daily report](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_DAILY_COVERAGE_REPORT.md). The action-adjusted return/identity review remains partial. **C1 overall is still NOT PASSED and C2 modelling remains locked.**


## Intraday QA artifact reconciliation — 2026-11-01

The complete per-cycle/date QA was recovered from [Actions run 41309632317, artifact 13086220727](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41309632317). It confirms 258/258 weekly expiry target cycles and stock coverage cycles passed, 154 confirmatory cycles after the 104-cycle warm-up, 98% minimum member coverage, zero unresolved active symbols and 1,083 requests across 21 windows. The lone partial flag is 2024-04-26 at 15:14, a non-expiry session used for the cycle's 10:00 anchor; the actual 2024-05-02 expiry proxy passed. An earlier 77/258 report was from an incomplete run and is superseded by this full artifact. [Corrected result](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_CONTINUOUS_COVERAGE_RESULT.json).

Overall C1 remains NOT PASSED: the daily history audit is 99.9934% with seven residual member-sessions, and exhaustive corporate-action/adjusted-return validation remains open. C2 is still locked.


## Latest C1 daily-history audit — 2026-11-01

The patched Dhan daily workflow [run 41316751830](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41316751830) completed successfully and retained sanitized [JSON](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_DAILY_COVERAGE.json) and [per-symbol report](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_DAILY_COVERAGE_REPORT.md). The 2018-04-01 to 2026-10-30 point-in-time member panel contains **106,385 valid OHLCV member-sessions out of 106,392 (99.9934%)**, across 70 security/member symbols and 2,128 combined index sessions. 210 Dhan index sessions extended the official cached calendar.

The restricted personal-use TejHQ raw NSE EQ bhavcopy fallback added 1,295 HDFC Ltd sessions after three Dhan legacy-security probes returned DH-905. Six HDFC dates remain absent: 2018-11-07, 2019-10-27, 2020-02-01, 2020-11-14, 2021-11-04 and 2022-10-24. One TATAMOTORS member-session remains absent on 2025-10-21. Its fallback was rejected because the source cross-check was incomplete; no unverified bar was inserted. Raw prices and parquet remain excluded from public artifacts.

The residual-date/reporting correction passed **91 regressions** in [run 41316751630](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41316751630). A separate cache-path expansion defect was identified and logged as E0075; cache reuse is not claimed until a subsequent run verifies encrypted-cache hits. The intraday target sub-gate remains **258/258 passed**, but overall C1 is still PARTIAL pending the seven feature gaps and full corporate-action/adjusted-return review. C2 remains locked.

See [C1 phase status](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/STATUS.md), [research log](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/logs/RESEARCH_LOG.md), and [error log](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/logs/ERROR_LOG.md).
