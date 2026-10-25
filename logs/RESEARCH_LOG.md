# Research Step Log

Every major action, including failure and blockage, is recorded here. Update statuses after each phase step.

## 2026-10-25 — Run R0001 / repository bootstrap
- Status: IN PROGRESS.
- Confirmed VCR-TRADING-RESEARCH/NIFTY-Prediction was an empty public repository; README had no prior research plan/logs/artifacts to read.
- Read the available current project conversation context: a prior project thread requested organization/GitHub setup and described the same NIFTY weekly direction target. A screenshot-based organization-connection troubleshooting discussion is listed in the project summary, but full past messages/images are not accessible as plain text in this run.
- Initialized README and research/phase-0-foundation branch. Defined the target, initial pre-registration, source register, status/error/conversation logs, manuscript and method plan.
- Public source review: NSE currently describes NIFTY weekly expiries on Tuesday with shift to previous trading day for holidays; historical Thursday-to-Tuesday shift must be modelled. Public minute-data repository describes 1-minute NIFTY OHLC from 2017 and documents known quirks. See docs/LITERATURE_REVIEW.md and docs/DATA_SOURCES.md.
- Paytm Money F&O FAQ says ₹10 per unique executed order; cost schedule must be date-aware. NSE current STT page lists rates effective 2026-04-01, so present-day rates cannot be copied into older backtests.
- Dhan authentication documentation says access tokens expire after 24 hours and supports secure API-based token generation when TOTP is configured. Token implementation is deferred until the Actions environment can test it; never emit token fields in logs.
- Code/data validation: automated workflow has not yet executed. No market-data computation or empirical backtest result is claimed. Pending workflow/test run.
- Phase gate at bootstrap: Phase 0 = IN PROGRESS; Phase 1 = NOT STARTED.

## 2026-10-25 — Run R0002 / first automated empirical pass
- Status: pipeline completed successfully; Phase 1 acceptance gate BLOCKED; Phase 2/3 metrics are exploratory only; Phase 4/5 acceptance blocked.
- GitHub Actions run: https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40167611476
- Unit tests passed. One feature-builder field-reference defect was caught by the first run, corrected, and covered by a follow-up test before the successful run.
- Source: 19 CSV files, 882,839 valid in-session bars, 2,356 sessions. Basic OHLC/timestamp checks passed but are not enough to certify data correctness.
- Target construction: 398 candidate labels (223 UP, 175 DOWN); 34 calendar/data-gap shifts inferred; 2 low-coverage rows flagged; 0 confirmatory-eligible rows.
- Independent Yahoo daily-close check: 2,352 overlapping dates; 368 of 402 candidate expiry dates differ by more than 1 index point. Overall median absolute difference ~7.20 points; 95th percentile ~30.52 points. Repeated-close run >10 bars on 63 sessions; maximum 239 bars.
- Dhan token/data cross-check unavailable. No Dhan intraday overlap was compared.
- Exploratory final holdout: 80 rows from 2025-04-09 onward; ExtraTrees accuracy 0.575 / balanced accuracy 0.559; development-selected logistic accuracy 0.550 / balanced accuracy 0.547. Not a validated edge.
- Conclusion: BLOCKED / NO USABLE STRATEGY VALIDATED. Do not trade. First reconcile the official expiry calendar and all source discrepancies; then rerun.
- Manuscript populated with results, tables, caveats and future steps at research/manuscript.md.
- Phase status: Phase 0 = scaffold/workflow/tests implemented; Phase 1 = BLOCKED on independent source and official calendar validation; Phase 2/3 = exploratory baseline/model pass only; Phase 4 = BLOCKED (no validated labels/instrument P&L); Phase 5 = manuscript complete as a blocked/inconclusive report, independent audit pending.
- Next step: add data fetch, label/feature/prediction pipeline, unit tests and manual/scheduled GitHub Actions workflow; run and inspect logs.


## Automated run 40167611476 — 2026-10-25T06:05:13.210148+00:00
- Status: pipeline completed; empirical findings remain exploratory until calendar and instrument-cost gates pass.
- Source files read: 19; valid minute bars: 882839.
- Weekly labels: 398; binary rows: 398; feature-complete rows: 398.
- Development rows / held-out rows: 318 / 80.
- Development-selected model: logistic.
- Calendar gate: EXPLORATORY_ONLY — Weekly expiry dates were generated from weekday regimes and inferred from available bars; official historical expiry calendar and holiday shifts are not independently reconciled.
- Usable trading strategy: NOT VALIDATED. No verified historical futures/options fills, contract-specific price series, dated Paytm Money cost schedule and bid-ask/slippage data have been joined. Spot-direction classification is not executable P&L.
- Artifacts: data/processed/weekly_labels_features.csv, research/results/holdout_metrics.csv, research/results/summary.json and the associated plots.


## Automated run 40169213949 — 2026-10-25T06:35:51.040915+00:00
- Status: pipeline completed; empirical findings remain exploratory until calendar and instrument-cost gates pass.
- Source files read: 19; valid minute bars: 882839.
- Weekly labels: 398; binary rows: 398; feature-complete rows: 398.
- Development rows / held-out rows: 318 / 80.
- Development-selected model: logistic.
- Calendar gate: EXPLORATORY_ONLY — Weekly expiry dates were generated from weekday regimes and inferred from available bars; official historical expiry calendar and holiday shifts are not independently reconciled.
- Usable trading strategy: NOT VALIDATED. No verified historical futures/options fills, contract-specific price series, dated Paytm Money cost schedule and bid-ask/slippage data have been joined. Spot-direction classification is not executable P&L.
- Artifacts: data/processed/weekly_labels_features.csv, research/results/holdout_metrics.csv, research/results/summary.json and the associated plots.


## 2026-10-25 — Phase 2 experimental track started
- Status: IN PROGRESS; bounded experiment branch created from the Phase 1 evidence branch.
- User explicitly requested bypassing the earlier validation phases and proceeding with QuantEvolve, PySR, TradingAgents/testing agents, and the custom indicator.
- Added a bounded evolutionary feature-rule search, a PySR symbolic-return experiment, upstream repository smoke-test/provenance, deterministic role-based risk review, and Python mirror of the Pine indicator.
- Added scheduled/manual GitHub Actions workflow, tests, and phase-specific plan. Outcomes will be recorded per track; dependency and runtime failures are non-blocking and must be logged.
- Scientific caveat: this is a user-directed bypass, not a passing validation gate. The historical expiry calendar and independent price discrepancies remain unresolved; no strategy is approved for trading.


## Automated run 40171160326 — 2026-10-25T07:03:48.638685+00:00
- Status: pipeline completed; empirical findings remain exploratory until calendar and instrument-cost gates pass.
- Source files read: 19; valid minute bars: 882839.
- Weekly labels: 398; binary rows: 398; feature-complete rows: 398.
- Development rows / held-out rows: 318 / 80.
- Development-selected model: logistic.
- Calendar gate: EXPLORATORY_ONLY — Weekly expiry dates were generated from weekday regimes and inferred from available bars; official historical expiry calendar and holiday shifts are not independently reconciled.
- Usable trading strategy: NOT VALIDATED. No verified historical futures/options fills, contract-specific price series, dated Paytm Money cost schedule and bid-ask/slippage data have been joined. Spot-direction classification is not executable P&L.
- Artifacts: data/processed/weekly_labels_features.csv, research/results/holdout_metrics.csv, research/results/summary.json and the associated plots.


## Phase 2 automated run — 2026-10-25T07:03:58.307284+00:00
- Status: experimental tracks executed; individual outcomes are in research/results/experimental/experimental_results.json.
- Upstream projects cloned with exact revisions in research/results/upstream_revisions.md.
- Data/calendar quality gate remains bypassed at user request; all scores are exploratory and no strategy is certified.


## 2026-10-25 — Phase 2 first bounded results
- Status: PARTIAL; first experimental run completed successfully, but PySR did not execute because the install step was skipped by a workflow condition.
- Sample: 398 candidate weekly cycles; 318 development / 80 held-out rows.
- Logistic baseline: 56.25% accuracy, 56.29% balanced accuracy, MCC 0.125, Brier 0.251.
- QuantEvolve-inspired bounded evolutionary search: 53.75% accuracy, 53.58% balanced accuracy, MCC 0.072, Brier 0.294; worse than baseline.
- Custom indicator Python mirror: 38.78% directional accuracy on 49 signalled held-out rows, coverage 61.25%.
- TradingAgents: repository cloned; no live multi-agent forecast was run. Deterministic risk-review roles were recorded only.
- AstraQuant: repository cloned and revision recorded; no signal model or order execution evaluated.
- Repair: PySR installation is now attempted on push; committed features are reused unless a manual run sets refresh_features=true.
- Decision: no strategy promoted; all results remain exploratory because source/calendar gates and contract-level costed P&L are unresolved.


## Phase 2 automated run — 2026-10-25T07:11:07.022954+00:00
- Status: experimental tracks executed; individual outcomes are in research/results/experimental/experimental_results.json.
- Upstream projects cloned with exact revisions in research/results/upstream_revisions.md.
- Data/calendar quality gate remains bypassed at user request; all scores are exploratory and no strategy is certified.


## 2026-10-25 — Phase 2 bounded execution complete
- Status: COMPUTE COMPLETE / RESEARCH ACCEPTANCE BLOCKED.
- Workflow: [40171572720](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40171572720), success; core and experimental unit tests passed; results and artifacts persisted.
- Sample: 398 candidate cycles, 318 development / 80 holdout; calendar quality remains heuristic/unverified.
- Logistic baseline: accuracy 56.25%, balanced accuracy 56.29%, MCC 0.125, Brier 0.2506.
- QuantEvolve-inspired local bounded search: accuracy 53.75%, balanced accuracy 53.58%, MCC 0.072, Brier 0.2944; underperformed logistic.
- PySR: completed 25 iterations / 8 populations / max expression size 12; holdout return RMSE 0.014925, R² -0.00124. No out-of-sample improvement over constant mean.
- Custom indicator: 38.78% directional accuracy on 49 signalled rows; 61.25% coverage.
- TradingAgents: no actual LLM debate/forecast; deterministic risk review only. AstraQuant: cloned/revision recorded, no NIFTY signal evaluation.
- Decision: no model promoted; no usable trading strategy validated. Do not iterate on the same holdout.
- Remaining blocking gates: official expiry-calendar reconciliation, 368/402 candidate expiry-close mismatches >1 point, unavailable Dhan cross-check, no instrument-level fills or dated Paytm Money brokerage/taxes/spread/slippage/net P&L.
- Full summary: research/phase2_report.md. Machine-readable outcomes: research/results/experimental/experimental_results.json.
