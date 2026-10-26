# Research step log

## 2026-10-25 — Prediction page implementation
- **Phase:** Prediction interface / integration
- **Status:** Implementation scaffold committed to phase branch; live prediction remains blocked pending verified model and data artifacts.
- **Completed:** Added responsive GitHub Pages frontend, date-selectable published prediction history, JSON schema, inference script, workflow with manual dispatch and scheduled run, and documented acceptance gates.
- **Validation:** Repository was inspected before changes. Existing main branch contained README.md and scripts/fetch_dhan_recent.py only; no trained model, processed feature table, expiry calendar, or workflow was present in the inspected tree.
- **Critical limitation:** A real ExtraTrees forecast cannot be truthfully produced until compatible model/features/expiry-calendar files exist. The interface explicitly reports unavailable rather than fabricate results.
- **Next gate:** Supply/produce compatible model and data artifacts through the research pipeline; run inference and tests; verify GitHub Pages settings and workflow success.


## 2026-10-25 — Restore research-backed ExtraTrees prediction page
- **Phase:** Prediction interface / model integration
- **Status:** Integration staged on `phase-prediction-live-integration`; ready for workflow validation after merge.
- **Finding:** Existing research branch already had the proper `research_core.py` pipeline, leakage-aware `build_pages_forecasts.py`, an 80-record chronological holdout, and a latest forward forecast. The prior main-branch stub did not connect to that pipeline.
- **Correction:** Replaced the placeholder UI with the research-backed date-selectable page and copied the forecast payload, inference/export code, dependencies, processed data, official close/expiry reference files, tests, and research workflow into this integration branch.
- **Latest saved forecast:** As-of 2026-10-21 10:00 IST; target expiry 2026-10-27; direction DOWN; model p_up 0.384781. This is a previously generated record, not a new calculation on 2026-10-25.
- **Acceptance status:** UI/data contract is implemented; full automated run and GitHub Pages deployment still need to pass. Data-quality gate remains BLOCKED; anchor prices are not independently validated. No executable trading strategy is certified.
- **Next:** Merge integration PR, inspect the Actions runs, correct failures, and verify the published Pages URL.


## Automated run 40196840830 — 2026-10-25T13:19:54.501227+00:00
- Status: pipeline completed; empirical findings remain exploratory until calendar and instrument-cost gates pass.
- Source files read: 19; valid minute bars: 882839.
- Weekly labels: 398; binary rows: 398; feature-complete rows: 398.
- Development rows / held-out rows: 318 / 80.
- Development-selected model: extra_trees.
- Calendar gate: OFFICIAL_EXPIRY_AND_EOD_CLOSE; ANCHOR_SOURCE_PROVISIONAL — The 10:00 anchor remains minute-archive-derived and independently unvalidated; executable contract-level performance is not tested.
- Usable trading strategy: NOT VALIDATED. No verified historical futures/options fills, contract-specific price series, dated Paytm Money cost schedule and bid-ask/slippage data have been joined. Spot-direction classification is not executable P&L.
- Artifacts: data/processed/weekly_labels_features.csv, research/results/holdout_metrics.csv, research/results/summary.json and the associated plots.

## 2026-10-25 — Phase 7: on-demand Dhan-backed inference
- **User clarification:** Predict must refresh the Dhan token, obtain the required NIFTY data through the selected as-of date, fit ExtraTrees and return a fresh result. A saved CSV/JSON lookup does not meet the requirement.
- **Implementation:** Added a FastAPI backend for secure Dhan authentication and historical one-minute data retrieval; data requests are chunked to Dhan's documented 90-day limit and old chunks are cached on the backend. The existing `research_core.py` is reused for minute/day validation, official close reconciliation, expiry-cycle construction, features and the ExtraTrees estimator.
- **Page behavior:** Predict submits a job to the backend and polls the result. It no longer treats the saved forecasts JSON as the click-time result.
- **Security:** Dhan credentials are provisioned as runtime secrets to a Hugging Face Docker Space from GitHub Actions. The public JavaScript receives only the endpoint URL, never credentials.
- **Leakage gates:** The chosen date must be the first session after the prior verified expiry, a valid 10:00–10:03 anchor must exist, training labels must be settled strictly before the selected anchor, and at least 104 eligible training rows and both classes are required.
- **Validation status:** Automated tests and provider deployment are pending. The independent 10:00 anchor/data-quality gate remains blocked, and no options trading strategy is certified.

## 2026-10-25 — Live inference deployment status
- Live inference code merged to `main` in commit `35ebee7d1cd621047d3cf2113803c79f93b36a13`.
- Validation passed before merge and the first main-branch deployment run installed dependencies and passed the backend tests (12 passed).
- First provider deployment attempt failed with `HfHubHTTPError` and HTTP 402 before publishing endpoint config. Current Hugging Face documentation confirms Docker Space CPU-basic requires Pro for individual accounts or Team/Enterprise for organizations.
- Added sanitized stage/status diagnostics and corrected a shadowed stage variable. No secret values or response bodies are logged.
- **Status: BLOCKED awaiting eligible Hugging Face compute or an existing eligible writable Space ID.** The page does not fall back to static records.

## 2026-10-25 — Deployment gate resolved to external service entitlement
- The corrected deployment diagnostic identifies the failing stage as “creating or opening the Hugging Face Docker Space”, HTTP 402; see [Actions run 40199234322](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40199234322).
- Dhan inference logic, existing research-core tests, frontend JavaScript syntax and endpoint-config JSON passed CI. The live service itself was not created, so no end-to-end Dhan request can be run yet.
- **Stop condition:** No further autonomous retries against the same Hugging Face account/plan. Waiting on a writable existing Docker Space or an eligible compute plan is a real external prerequisite.


## 2026-10-25 — Alternative backend assessment
- User approved continuing with a secure alternative backend while retaining GitHub Pages for the UI.
- Current configured Hugging Face deployment was retried after correcting the diagnostic code; run https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40199234322 confirms HTTP 402 at Space creation. Code checks pass, but no server exists to handle a live request.
- Available repository secrets include HF_TOKEN, GOOGLE_API_KEY, and Dhan credentials. No alternate hosting-provider deployment token is configured in the workflow. Google API key alone is not an infrastructure deployment credential.
- **Stop condition:** Do not loop deployments against the same rejected provider. Wait for an existing eligible Space ID or alternate host credentials; then deploy and run a real Dhan end-to-end smoke test.


## 2026-10-25 — Phase 8: GitHub Actions on-demand prediction
- User direction: keep the Pages UI and run Python inference in GitHub Actions when Predict is used; Dhan may be used but credentials must remain protected.
- Architecture: replaced dependency on provisioning a separate API host with a secured GitHub issue request. Pages prepares a prefilled issue link for the chosen date; the user submits it while authenticated. A default-branch Actions workflow admits only OWNER/MEMBER issue authors, validates a strict ISO date title, refreshes Dhan authentication from GitHub Secrets, runs the existing ExtraTrees inference function, and publishes a date-specific JSON result.
- Manual fallback: workflow_dispatch with an as-of date on main.
- Cache: Actions cache restores and saves Dhan minute chunks so old history need not be downloaded on every run. The access token is refreshed for each inference.
- Frontend: Predict prepares the request link and polls the public result file, accepting only a result generated after the click. Failed inference is shown as a failure; stale forecasts are not substituted.
- Files: [Phase 8 plan](../docs/PHASE_8_GITHUB_ACTIONS_PREDICTION.md), [workflow](../.github/workflows/on-demand-prediction.yml), [runner](../scripts/run_live_prediction.py).
- Status: implementation committed on phase/github-actions-on-demand-prediction; automated CI, merge, Actions permissions, Pages publication and live Dhan end-to-end request remain to be verified. No live prediction is claimed yet.
- Research gate: independent 10:00 anchor validation and options/futures P&L including Paytm Money charges, spread and slippage remain BLOCKED.


## 2026-10-25 — Post-merge trigger smoke test
- PR #8 merged in commit db3edc113037ff16f7d21d28a69bcc0e975bae7e; validation run [40200568709](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40200568709) passed research/Dhan tests, Python compilation, JavaScript syntax and workflow YAML parsing.
- PR #10 merged in commit faa2b1291abfee6f6b4a92bd4a902fc204dd5776; validation run [40200737861](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40200737861) passed the same checks. The issue-trigger authorization gate includes OWNER, MEMBER and COLLABORATOR associations and allows reopened requests.
- Created/reopened [test request #9](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/issues/9) for 2026-10-21. At latest inspection, no completion comment or result file was visible. The live Dhan event path is not yet certified; no forecast is claimed.


## 2026-10-25 — Dhan authentication correction and live retry
- Controlled run [40201297978](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40201297978) successfully executed workflow/publish mechanics but correctly produced a failed prediction record because Dhan token refresh returned HTTP 405; no forecast was fabricated.
- Root cause found in code: token generation used GET, while official DhanHQ documentation specifies POST with query parameters. Corrected in `live_api/app.py` commit `ad14c138c91f75ec801bf201e1770271bb2deb6e` and added a mocked regression test in `tests/test_live_api.py` commit `5a5789c9cf8569f7890a2e7e42b5c941641f81dd`.
- The inference runner now exits non-zero when a prediction fails, rather than letting a failed inference appear as a successful Actions step (commit `8a1c1c3659e6c1e37cfca5ffc41fd668094f196f`).
- Retry run [40201653154](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40201653154) is in progress at the latest inspection. Live forecast remains unverified until a successful JSON record appears.
- Cache warning: GitHub Actions cache save denied writable scope. Data cache persistence must be corrected or explicitly marked unavailable; no claim that cache save succeeded.


## 2026-10-25 — First successful fresh Dhan-backed ExtraTrees inference
- Retry run [40201653154](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40201653154) completed successfully after fixing Dhan token generation to POST. It refreshed credentials, fetched 268,510 valid in-session minute bars from 2021-10-26 through 2024-09-20, fit ExtraTrees using 147 completed weekly labels through 2024-09-19, and published `docs/assets/predictions/2024-09-20.json`.
- Result: UP direction; raw ExtraTrees UP score 0.5131; target expiry 2024-09-26; Dhan 10:00 anchor 25,586.7. This is a historical point-in-time research output, not a current signal.
- Temporal checks: training labels stop at 2024-09-19 (before the 2024-09-20 anchor); all 20 model features were available; official close sessions matched 717; verified expiry calendar status is official.
- Gate remains BLOCKED: the Dhan-derived 10:00 anchor has not been independently reconciled, score is not calibrated, and no executable options P&L including Paytm Money charges/spreads/slippage has been validated. Do not treat as a trading recommendation.
- Cache: an earlier run logged a cache-save writable-scope warning. Workflow permissions were amended to include `actions: write` in commit `04f55a01c7ce65b086aa73d82b6bad955b065e05`; persistence must be confirmed on a later run.


## 2026-10-25 — Free GitHub Actions + Pages design selected

- User approved removing Render and using GitHub Actions with Pages.
- Added branch `phase/github-actions-pages-free` with a scheduled weekday 10:30 IST inference workflow, manual dispatch, date-specific/latest JSON publication and UI-only result loading.
- Pages does not hold credentials and no longer asks the user to submit a GitHub Issue in this proposed flow.
- Known platform constraint documented: browser click loads the published result; a fresh private Actions run cannot be securely initiated directly from static Pages without authentication.
- **Phase status:** implementation prepared; validation/merge and live scheduled inference pending.
- **Research status:** not trading-ready; independent anchor reconciliation and executable cost/slippage validation remain open.


## 2026-10-25 — Free Actions + Pages merged and CI checked

- Merged PR #13 (commit `ca5ad434ed0a919495b4897b6e1034a82da257b2`).
- Branch CI and workflow integration checks passed.
- Pages deployment was still in progress at the latest check.
- First fresh Dhan inference/publication/browser acceptance remains pending; the scheduled workflow runs weekdays at 10:30 IST and has a manual dispatch control.
- No trading-readiness upgrade: anchor reconciliation and option-level transaction cost/slippage checks remain BLOCKED.


## 2026-10-25 — Date dispatch and stale-result correction
- **Phase:** Free GitHub Actions + Pages integration
- **Status:** Staged on `fix/date-dispatch-and-failure-publication`; validation pending.
- **Observed run:** Screenshot shows the 2024-06-07 date rejected by the “first session after prior verified expiry” gate; prior expiry reported as 2024-06-06. Gate remains intact pending calendar audit.
- **Changes:** Date form opens Actions workflow for the selected date; publication writes explicit failure status after failed inference to prevent stale predictions appearing fresh.
- **Limit:** User must confirm Run workflow in GitHub; no token is exposed to the static page. Research-only, not trading-cleared.
- **Next:** CI and review of date-specific workflow behavior.


## 2026-10-25 — Historical cutoff 2024-06-07 successfully inferred
- **Phase:** GitHub Actions + Pages historical date inference
- **Run:** [40204498793](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40204498793), successful retry; all inference, cache-save, and publication steps passed.
- **Published artifact:** [2024-06-07.json](../docs/assets/predictions/2024-06-07.json).
- **Output:** UP; raw ExtraTrees UP score 0.547499; target expiry 2024-06-13; anchor 22,978.3; 132 eligible training rows, last expiry label 2024-06-06; 20/20 features; 241,516 Dhan minute bars through 15:29 IST on the historical date.
- **Date validation:** The date passed the strict first-session-after-prior-expiry check on the successful retry. The earlier failure was not reproduced; its precise cause is unresolved.
- **Interpretation:** Features are constructed using the 10:00 anchor and pre-anchor data; data_through records overall retrieval coverage, not the feature cutoff. Nevertheless, the 10:00 anchor is not independently reconciled, and the model score is not calibrated probability or options profit.
- **Status:** Inference/publication gate PASSED for this historical date. Research/trading-readiness gate remains BLOCKED pending anchor reconciliation, walk-forward validation and instrument-level costs/slippage.


## 2026-10-25 — Pages redirect loop correction
- **Finding:** The live page redirected to GitHub Actions because its submit handler was hardcoded to navigate to the workflow URL, even though a successful date-specific JSON existed.
- **Fix:** Restore intended behavior: load published JSON in-page; do not redirect on date selection. Only show a manual workflow hint if the result is unavailable. Add JS cache-busting.
- **Date result:** 2024-06-07 published record is status=succeeded, direction UP, raw score 0.547499, target expiry 2024-06-13. Data-quality status remains BLOCKED.
- **Status:** Correction committed directly to main; deployment validation pending.


## 2026-10-25 — All-date calendar/session validation fix
- **Issue:** Calendar validation used Dhan-derived daily sessions, coupling exchange-calendar truth to provider data coverage and potentially falsely rejecting dates across the historical range.
- **Method change:** Resolve the next NSE session from official daily-session dates after the preceding verified expiry. Keep Dhan minute-bar requirements separate: missing 10:00 anchor or expiry bars must still fail safely with a data-coverage error.
- **Regression tests:** Add tests that 2026-05-06 is the next official session after 2026-05-05, independent of Dhan bar presence, and that an empty official calendar fails closed.
- **Status:** Fix staged on `fix/official-session-calendar-validation`; CI and review pending. Trading gate remains blocked for anchor/cost validation.


## 2026-10-25 — Selected-date Dhan cache refresh
- **Trigger:** Manual inference for 2026-08-05 failed because no valid 10:00–10:03 IST anchor bar was found.
- **Hypothesis:** A previously cached 90-day chunk may be incomplete and cache-first logic would preserve that gap. Not yet confirmed; the rerun will distinguish cache staleness from provider absence.
- **Change:** Refresh the 90-day chunk containing the requested cutoff on every inference; all other chunks remain cached. Add regression test to ensure the selected date's chunk bypasses cache.
- **Research integrity:** Do not substitute daily close or fabricated price for the 10:00 anchor. Missing bar remains a hard gate.
- **Status:** Staged on `fix/refresh-selected-date-data-cache`; CI pending.


## 2026-10-25 — PR #16 merged; post-merge prediction still pending
- PR #16 merged as `c81a3c5e1bc9a6021c530ebdf691313acbd8c80a`; automated `test` and `validate` checks passed.
- Selected date 2026-08-05 currently has only a failed-status JSON; there is no fresh prediction generated after the cache-refresh change yet.
- A separate legacy `Deploy Live Dhan ExtraTrees API` workflow failed at the external Docker Space deploy step. It is outside the selected static Pages architecture and does not prove the Pages predictor failed.
- Status: code-level test PASSED; end-to-end selected-date cache refresh and anchor acquisition PENDING; no trading inference claim.


## 2026-10-25 — Targeted one-day retry for selected-session data
- **Question:** Does Dhan omit the 2026-08-05 anchor because of large-chunk response coverage, or is the data genuinely unavailable/invalid?
- **Method:** Alongside the normal cached/chunked history fetch, request only the selected session once; normalize/validate and deduplicate the combined bars. If anchor remains missing, report aggregate timestamp diagnostics only.
- **Hypothesis test:** Targeted request returns bars absent from broad request => broad response/cache coverage problem. Targeted request also lacks bars => investigate Dhan response/instrument/time conversion and free-source cross-checks. No inference from fabricated or silently substituted anchors.
- **Status:** Staged on `fix/target-date-intraday-diagnostic-retry`; CI pending.


## Phase 9 historical anchor source audit — run 40278945700 — 2026-10-26T06:18:22.022003+00:00
- Status: DIAGNOSTIC_ONLY (diagnostic only).
- Counts: {"anchor_open_mismatches_over_1_point": 62, "exact_timestamp_matches": 0, "overlap_sessions": 1269, "primary_anchors": 1269, "secondary_anchors": 1271}.
- Difference summary: {"max": 6.700000000000728, "median": 0.049999999999272404, "p95": 1.0}.
- Caveat: secondary archive provider lineage is unverified; this comparison cannot pass the official independent-anchor gate.
- Output: data/reconciliation/anchor_source_comparison.csv and anchor_source_comparison_report.json.


## Phase 9 historical anchor source audit — run 40279153471 — 2026-10-26T06:20:21.519357+00:00
- Status: DIAGNOSTIC_ONLY (diagnostic only).
- Counts: {"anchor_open_mismatches_over_1_point": 62, "exact_timestamp_matches": 1269, "overlap_sessions": 1269, "primary_anchors": 1269, "secondary_anchors": 1271}.
- Difference summary: {"max": 6.700000000000728, "median": 0.049999999999272404, "p95": 1.0}.
- Caveat: secondary archive provider lineage is unverified; this comparison cannot pass the official independent-anchor gate.
- Output: data/reconciliation/anchor_source_comparison.csv and anchor_source_comparison_report.json.


## Phase 9 historical anchor source audit — run 40279215364 — 2026-10-26T06:21:15.328262+00:00
- Status: DIAGNOSTIC_ONLY (diagnostic only).
- Counts: {"anchor_open_mismatches_over_1_point": 62, "exact_timestamp_matches": 1269, "overlap_sessions": 1269, "primary_anchors": 1269, "secondary_anchors": 1271}.
- Difference summary: {"max": 6.700000000000728, "median": 0.049999999999272404, "p95": 1.0}.
- Caveat: secondary archive provider lineage is unverified; this comparison cannot pass the official independent-anchor gate.
- Output: data/reconciliation/anchor_source_comparison.csv and anchor_source_comparison_report.json.


## 2026-10-26 — Historical 10:00 anchor cross-check, corrected timestamp handling
- Workflow run [40278945700](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40278945700) completed the first public-archive comparison. A timestamp metric defect was then identified: the primary timestamps were timezone-aware IST and the secondary archive timestamps were naive local timestamps. As a result, the first run's "zero exact timestamp matches" was invalid and must not be used.
- Corrected code localizes source-specified naive secondary times to Asia/Kolkata before comparing. New run [40279215364](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40279215364) passed the new timestamp and label-sensitivity unit tests and the comparison workflow.
- Corrected result over 1 February 2019–27 March 2024: primary anchors 1,269; secondary anchors 1,271; overlap 1,269; exact timestamp matches 1,269 / 1,269. Absolute open-price difference: median 0.05 index points, 95th percentile 1.00, maximum 6.70. 62 sessions exceed a one-point price mismatch.
- On the 265 overlapping weekly cycles, holding the recorded expiry close constant and substituting the secondary 10:00 anchor produced zero UP/DOWN label switches; all 265 resulting labels matched the original published labels.
- Interpretation remains DIAGNOSTIC_ONLY: the secondary repository's underlying data-provider lineage is not independently verified. This result indicates low label sensitivity in the overlapping weekly sample, but does not certify anchor-source provenance, other OHLC features, or out-of-overlap dates.
- Next source check: use the authenticated Dhan historical intraday endpoint over its advertised last-five-year window, cache raw chunks privately in Actions cache, publish only compact comparison statistics and label sensitivity.
