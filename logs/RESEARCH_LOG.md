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


## 2026-10-25 — Phase 3 official source reconciliation initiated
- Status: IN PROGRESS; automated validation workflow is triggered by branch changes.
- Plan: docs/PHASE_3_SOURCE_RECONCILIATION.md.
- Implementation: scripts/reconcile_official_sources.py fetches official NIFTY 50 price-index history, compares minute-archive daily closes, and checks candidate weekly expiry dates against NSE F&O bhavcopy.
- Tests: tests/test_official_reconciliation.py covers the official response parser, legacy and UDiFF bhavcopy schemas, and the Thursday-to-Tuesday weekly expiry regime.
- Caching: official daily history and F&O bhavcopy files are cached under data/cache/official; compact row-level results are written to data/reconciliation.
- Acceptance: remains blocked until the automated report verifies all expiry dates and the daily-close comparison meets the one-point tolerance. No model is promoted.


## Phase 3 official-source reconciliation — 2026-10-25T07:17:36.789826+00:00
- Status: BLOCKED
- Counts: {}
- Errors: HTTPError: 401 Client Error: Unauthorized for url: https://www.niftyindices.com/Backpage.aspx/getHistoricaldatatabletoString
- Detailed outputs: data/reconciliation/


## Automated run 40172557963 — 2026-10-25T07:28:28.068736+00:00
- Status: pipeline completed; empirical findings remain exploratory until calendar and instrument-cost gates pass.
- Source files read: 19; valid minute bars: 882839.
- Weekly labels: 398; binary rows: 398; feature-complete rows: 398.
- Development rows / held-out rows: 318 / 80.
- Development-selected model: logistic.
- Calendar gate: EXPLORATORY_ONLY — Weekly expiry dates were generated from weekday regimes and inferred from available bars; official historical expiry calendar and holiday shifts are not independently reconciled.
- Usable trading strategy: NOT VALIDATED. No verified historical futures/options fills, contract-specific price series, dated Paytm Money cost schedule and bid-ask/slippage data have been joined. Spot-direction classification is not executable P&L.
- Artifacts: data/processed/weekly_labels_features.csv, research/results/holdout_metrics.csv, research/results/summary.json and the associated plots.


## Phase 3 official-source reconciliation — 2026-10-25T07:49:08.356743+00:00
- Status: BLOCKED
- Counts: {}
- Errors: HTTPError: 401 Client Error: Unauthorized for url: https://www.niftyindices.com/Backpage.aspx/getHistoricaldatatabletoString
- Detailed outputs: data/reconciliation/


## Phase 3 bounded official-source pass — run 40174191441
- Status: BLOCKED; computation and artifact upload completed, but the final Git commit failed while rebasing shared log changes created by the parallel research workflow.
- Official NSE historical index rows: 1,913; 1,901/1,901 candidate daily sessions matched to an official close.
- Daily close comparison: 1,717/1,901 exceed the pre-registered 1-point tolerance; absolute difference median 8.25, P95 32.45, maximum 200.7 index points.
- Initial contract check: 359/402 candidate nominal dates confirmed; 43 unconfirmed; zero download exceptions. This is not a verified calendar.
- Detailed artifact: https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40174191441
- Corrections in the current commit: date-aware legacy/UDiFF URL ordering, documented nsearchives UDiFF host, schema/trade-date validation, actual-expiry-field preference, parser tests, shared workflow concurrency, and rebase-before-push for research status commits.
- Main research run 40174191439 completed calculations: 398 labels; 318 development / 80 holdout. Exploratory holdout: ExtraTrees accuracy 0.575 / balanced accuracy 0.559; logistic accuracy 0.550 / balanced accuracy 0.547. Labels remain heuristic; no strategy is validated.
- Phase gate: Phase 1 BLOCKED; Phase 2/3 exploratory only; Phase 4 blocked because no verified instrument-level P&L, dated Paytm Money costs, spread/slippage/fills; Phase 5 manuscript exists but independent audit remains pending.


## Phase 3 official-source reconciliation — 2026-10-25T08:03:49.299759+00:00
- Status: BLOCKED
- Counts: {"candidate_expiries_checked": 402, "contract_verified_expiries": 338, "daily_source_rows_compared": 1901, "daily_source_rows_expected": 1901, "daily_source_rows_missing_official_close": 0, "expiry_source_errors": 38, "minute_vs_official_mismatches_over_1_point": 1717, "official_daily_rows": 1913}
- Errors: One or more candidate expiry dates were not confirmed in official F&O data, or minute archive daily closes differ from official NIFTY 50 closes by >1 point.
- Detailed outputs: data/reconciliation/


## Automated run 40175103450 — 2026-10-25T08:07:29.859324+00:00
- Status: pipeline completed; empirical findings remain exploratory until calendar and instrument-cost gates pass.
- Source files read: 19; valid minute bars: 882839.
- Weekly labels: 398; binary rows: 398; feature-complete rows: 398.
- Development rows / held-out rows: 318 / 80.
- Development-selected model: logistic.
- Calendar gate: EXPLORATORY_ONLY — Weekly expiry dates were generated from weekday regimes and inferred from available bars; official historical expiry calendar and holiday shifts are not independently reconciled.
- Usable trading strategy: NOT VALIDATED. No verified historical futures/options fills, contract-specific price series, dated Paytm Money cost schedule and bid-ask/slippage data have been joined. Spot-direction classification is not executable P&L.
- Artifacts: data/processed/weekly_labels_features.csv, research/results/holdout_metrics.csv, research/results/summary.json and the associated plots.


## Phase 3 second official-source pass — run 40174991974
- Status: computation completed and automated commit succeeded; acceptance gate remains BLOCKED.
- Official daily index rows: 1,913; compared daily sessions: 1,901; 1,717 >1-point differences (median 8.25; P95 32.45; maximum 200.7).
- Expiry results: 338/402 confirmed, 26 not verified, 38 source-validation errors. Unit tests passed. Source errors were truncated to exception type, making root-cause analysis insufficient.
- Corrective step: warm each worker's NSE session against the official derivatives reports page, retain detailed sanitized validation reasons, check nearby previous sessions for expiry holiday shifts, and compare official daily open/high/low separately from close. This is diagnostic; the one-point close gate is not relaxed.
- Main research pass 40175103450 completed successfully and committed artifacts. Metrics remain exploratory only: ExtraTrees 0.575 accuracy / 0.559 balanced; logistic 0.550 / 0.547 on an 80-row holdout. No costed executable strategy exists.


## Phase 3 official-source reconciliation — 2026-10-25T08:15:03.103281+00:00
- Status: BLOCKED
- Counts: {"candidate_expiries_checked": 402, "contract_unverified_expiries": 26, "contract_verified_expiries": 338, "daily_source_rows_compared": 1901, "daily_source_rows_expected": 1901, "daily_source_rows_missing_official_close": 0, "expiry_source_errors": 38, "minute_vs_official_abs_difference_max_points": 200.7, "minute_vs_official_abs_difference_median_points": 8.25, "minute_vs_official_abs_difference_p95_points": 32.45, "minute_vs_official_mismatches_over_1_point": 1717, "minute_vs_official_within_1_point": 184, "official_daily_rows": 1913}
- Errors: 338/402 candidate dates were confirmed; 26 were not verified and 38 produced source-validation errors. Detailed failure diagnostics were not preserved by this run.; 1,717 of 1,901 daily minute-source closes differ from official NSE NIFTY 50 closes by more than the pre-registered 1-point tolerance.
- Detailed outputs: data/reconciliation/


## Test correction — run 40175798910 / 40175799013
- The first run after adding the OHLC/holiday-shift diagnostics stopped at unit tests: 14 passed, 1 failed. The only failure was a test expecting two nearby sessions, while the helper correctly returned all four sessions within the four-calendar-day window.
- Corrected the test expectation; code was not weakened. Both workflows are set to rerun from the latest branch tip.
- No official-source results were produced by these runs because test failure prevents the reconciliation step from starting.


## Automated run 40175978898 — 2026-10-25T08:20:24.495172+00:00
- Status: pipeline completed; empirical findings remain exploratory until calendar and instrument-cost gates pass.
- Source files read: 19; valid minute bars: 882839.
- Weekly labels: 398; binary rows: 398; feature-complete rows: 398.
- Development rows / held-out rows: 318 / 80.
- Development-selected model: logistic.
- Calendar gate: EXPLORATORY_ONLY — Weekly expiry dates were generated from weekday regimes and inferred from available bars; official historical expiry calendar and holiday shifts are not independently reconciled.
- Usable trading strategy: NOT VALIDATED. No verified historical futures/options fills, contract-specific price series, dated Paytm Money cost schedule and bid-ask/slippage data have been joined. Spot-direction classification is not executable P&L.
- Artifacts: data/processed/weekly_labels_features.csv, research/results/holdout_metrics.csv, research/results/summary.json and the associated plots.


## Phase 3 official-source reconciliation — 2026-10-25T08:23:11.400151+00:00
- Status: BLOCKED
- Counts: {"candidate_expiries_checked": 402, "contract_unverified_expiries": 22, "contract_verified_expiries": 340, "daily_source_rows_compared": 1901, "daily_source_rows_expected": 1901, "daily_source_rows_missing_official_close": 0, "expiry_source_errors": 40, "minute_vs_official_abs_difference_max_points": 200.70000000000073, "minute_vs_official_abs_difference_median_points": 8.25, "minute_vs_official_abs_difference_p95_points": 32.44999999999709, "minute_vs_official_high_abs_difference_median_points": 0.049999999999272404, "minute_vs_official_high_mismatches_over_1_point": 197, "minute_vs_official_high_rows_compared": 1901, "minute_vs_official_low_abs_difference_median_points": 0.049999999999272404, "minute_vs_official_low_mismatches_over_1_point": 185, "minute_vs_official_low_rows_compared": 1901, "minute_vs_official_mismatches_over_1_point": 1717, "minute_vs_official_open_abs_difference_median_points": 0.0, "minute_vs_official_open_mismatches_over_1_point": 587, "minute_vs_official_open_rows_compared": 1901, "minute_vs_official_within_1_point": 184, "official_daily_rows": 1913}
- Errors: One or more candidate expiry dates were not confirmed in official F&O data, or minute archive daily closes differ from official NIFTY 50 closes by >1 point.
- Detailed outputs: data/reconciliation/


## Resume — independent minute-source cross-check added
- Added a bounded data audit for the independent public NIFTY 50 1-minute repository https://github.com/technovusin/nifty50-historical-data.
- Cache policy: reuse yearly 2019-2025 files and monthly 2026 files in data/cache/alternative-minute rather than downloading each run.
- Aggregation: chronologically sorted rows, ordinary 09:15-15:29 IST session, daily open/high/low/close and bar count; compare to official NSE daily OHLC and primary candidate archive.
- Phase 3 run 40175978915: 1,913 official daily rows, 1,901 sessions; 1,717 close mismatches >1 point; median 8.25, P95 32.45, max 200.7. Official open/high/low mismatches were 587/197/185.
- Expiry check: 340/402 confirmed including two shifted dates, 22 not verified, 40 source-validation errors. The new parser prioritizes TradDt ahead of BizDt and retains longer sanitized diagnostics.
- Phase 1 stays BLOCKED; model metrics exploratory only.


## Automated run 40177007671 — 2026-10-25T08:36:04.616087+00:00
- Status: pipeline completed; empirical findings remain exploratory until calendar and instrument-cost gates pass.
- Source files read: 19; valid minute bars: 882839.
- Weekly labels: 398; binary rows: 398; feature-complete rows: 398.
- Development rows / held-out rows: 318 / 80.
- Development-selected model: logistic.
- Calendar gate: EXPLORATORY_ONLY — Weekly expiry dates were generated from weekday regimes and inferred from available bars; official historical expiry calendar and holiday shifts are not independently reconciled.
- Usable trading strategy: NOT VALIDATED. No verified historical futures/options fills, contract-specific price series, dated Paytm Money cost schedule and bid-ask/slippage data have been joined. Spot-direction classification is not executable P&L.
- Artifacts: data/processed/weekly_labels_features.csv, research/results/holdout_metrics.csv, research/results/summary.json and the associated plots.


## Phase 3 official-source reconciliation — 2026-10-25T08:39:38.674792+00:00
- Status: BLOCKED
- Counts: {"candidate_expiries_checked": 402, "contract_unverified_expiries": 22, "contract_verified_expiries": 340, "daily_source_rows_compared": 1901, "daily_source_rows_expected": 1901, "daily_source_rows_missing_official_close": 0, "expiry_source_errors": 40, "minute_vs_official_abs_difference_max_points": 200.70000000000073, "minute_vs_official_abs_difference_median_points": 8.25, "minute_vs_official_abs_difference_p95_points": 32.44999999999709, "minute_vs_official_high_abs_difference_median_points": 0.049999999999272404, "minute_vs_official_high_mismatches_over_1_point": 197, "minute_vs_official_high_rows_compared": 1901, "minute_vs_official_low_abs_difference_median_points": 0.049999999999272404, "minute_vs_official_low_mismatches_over_1_point": 185, "minute_vs_official_low_rows_compared": 1901, "minute_vs_official_mismatches_over_1_point": 1717, "minute_vs_official_open_abs_difference_median_points": 0.0, "minute_vs_official_open_mismatches_over_1_point": 587, "minute_vs_official_open_rows_compared": 1901, "minute_vs_official_within_1_point": 184, "official_daily_rows": 1913}
- Errors: One or more candidate expiry dates were not confirmed in official F&O data, or minute archive daily closes differ from official NIFTY 50 closes by >1 point.
- Detailed outputs: data/reconciliation/
