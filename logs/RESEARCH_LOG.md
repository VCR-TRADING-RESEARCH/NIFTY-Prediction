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


## Automated run 40675278048 — 2026-10-28T10:53:00.782564+00:00
- Status: pipeline completed; empirical findings remain exploratory until calendar and instrument-cost gates pass.
- Source files read: 19; valid minute bars: 883964.
- Weekly labels: 398; binary rows: 398; feature-complete rows: 398.
- Development rows / held-out rows: 318 / 80.
- Development-selected model: extra_trees.
- Calendar gate: OFFICIAL_EXPIRY_AND_EOD_CLOSE; ANCHOR_SOURCE_PROVISIONAL — The 10:00 anchor remains minute-archive-derived and independently unvalidated; executable contract-level performance is not tested.
- Usable trading strategy: NOT VALIDATED. No verified historical futures/options fills, contract-specific price series, dated Paytm Money cost schedule and bid-ask/slippage data have been joined. Spot-direction classification is not executable P&L.
- Artifacts: data/processed/weekly_labels_features.csv, research/results/holdout_metrics.csv, research/results/summary.json and the associated plots.


## Automated run 41145607225 — 2026-10-30T23:42:37.852823+00:00
- Status: pipeline completed; empirical findings remain exploratory until calendar and instrument-cost gates pass.
- Source files read: 19; valid minute bars: 884714.
- Weekly labels: 398; binary rows: 398; feature-complete rows: 398.
- Development rows / held-out rows: 318 / 80.
- Development-selected model: extra_trees.
- Calendar gate: OFFICIAL_EXPIRY_AND_EOD_CLOSE; ANCHOR_SOURCE_PROVISIONAL — The 10:00 anchor remains minute-archive-derived and independently unvalidated; executable contract-level performance is not tested.
- Usable trading strategy: NOT VALIDATED. No verified historical futures/options fills, contract-specific price series, dated Paytm Money cost schedule and bid-ask/slippage data have been joined. Spot-direction classification is not executable P&L.
- Artifacts: data/processed/weekly_labels_features.csv, research/results/holdout_metrics.csv, research/results/summary.json and the associated plots.


## 2026-10-31 — BUP-01 C1 resumed; offline tests pass but Dhan profile gate blocks data
- Re-read the C1 plan, status, source register, feasibility audit, README and error/research logs before resuming.
- Confirmed the offline authorised-source audit workflow [41181684637](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41181684637) passed all steps, but no authorised local official-weight archive was present.
- Confirmed the Dhan preflight workflow [41181684573](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41181684573) passed its nine mocked response tests. Live profile returned HTTP 401; no scrip-master/equity history/intraday request was reached. The workflow-level green status must not be mistaken for data-gate success.
- Confirmed shared token-refresh PR #28 has passing mocked Actions checks, but remains draft/open and unmerged. Main's scheduled helper is therefore not considered fixed.
- Re-audited the CC BY 4.0 membership candidate: 83 NIFTY50 interval rows/82 symbols; 93 sampled month-15 membership cardinalities from 2018-01 to 2025-09 equal 50. Source ends 2025-09 and has no numerical index weights. Quarterly ownership disclosures do not equal official IWF.
- C1 remains blocked; no panel, stock model, forecast or trading result has been generated. Next gate is Dhan profile/account entitlement plus separately authorised point-in-time numerical weights and current membership.

2026-10-31 — Dhan profile request aligned with v2 docs; authentication remains blocked

- Dhan v2 documentation confirms token generation uses POST with client ID, PIN and TOTP query parameters; profile validation is a GET using the access-token header only; profile returns dataPlan and tokenValidity. Data APIs require a separate subscription. Source: https://dhanhq.co/docs/v2/authentication/.
- Updated BUP-01 profile preflight to use only the documented access-token header; retained client-id for market-data calls. Added regression test. Latest run [41181948126](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41181948126): 10/10 offline tests pass.
- Live token endpoint returned HTTP 200 but no accessToken field (only message/status keys); fallback token returned HTTP 401 on profile. No security master, daily history or intraday equity calls were reached.
- C1 remains blocked on valid Dhan authentication and the independent official historical free-float weight/membership gates. No stock panel/model/forecast was built.

2026-10-31 — PR #28 review state updated

- After its mocked Actions checks passed, PR #28 was marked ready for review. GitHub reports `mergeable_state=dirty`, so it was not merged. No direct main-branch bypass was used.

2026-10-31 — Additional public NIFTY weight-source sweep

- Searched public Hugging Face, GitHub and Figshare candidates. The 216-snapshot HF weights dataset (2008-01 to 2025-08) is CC BY-NC-SA 4.0 and includes static-between-snapshot/estimated-gap assumptions; not accepted for the trading workflow without separate permission and validation.
- GitHub alternatives surfaced were binary/equal-weight membership approximations or best-effort circular/EOD reconstructions, not official numeric IWF series; NSE redistribution terms remain a blocker.
- Added the source-by-source decision to research/constituent_weekly/DATA_SOURCE_REGISTER.md. No dataset was ingested and no model work was performed.


## 2026-10-31 — Dhan authentication retry after shared-helper correction

- Corrected `scripts/refresh_dhan_token.py` on the C1 branch to use POST with query parameters, reject line breaks, mask the ephemeral token and export only through `GITHUB_ENV`. Added mocked regression tests and wired the helper/test paths into the C1 Dhan workflow.
- The BUP-01 preflight already used POST; its request shape was retained. This avoids conflating the shared-helper defect with the independent live-account authentication failure.
- Actions run [41182555655](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41182555655): all steps passed, including 10/10 offline tests. Live token endpoint returned HTTP 200 but only `message` and `status` keys; no access token was returned. The fallback profile request returned HTTP 401. No security master, daily bars or intraday bars were queried.
- Added safe provider-error categorisation (category only; no provider message text) and a regression test. A subsequent run is pending/in progress at the time of this log update; its result must be checked before closing this diagnostic.
- C1 remains BLOCKED. The token endpoint's HTTP 200 is not authentication success. Do not infer the token secret values or expose them. Next gate is to classify Dhan's authentication response safely, then request user-owned secret correction only if the provider confirms an invalid/mismatched credential.


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

## 2026-10-31 — BUP-01 continuation
- User approved continuation. Reviewed C1 status, preflight JSON, source register, plan, operating rules, workflow and available logs.
- Official NIFTY methodology confirms that index weights use free-float IWF and that IWF excludes specified strategic holdings beyond simple promoter/public ownership summaries.
- NSE website terms restrict automated collection and copying/reuse of site content; automated NSE collection remains disabled pending an applicable permission/licence determination.
- Dhan v2 documents up to five years of intraday history for active instruments and a maximum 90-day request window; inactive/delisted coverage is not guaranteed.
- No additional token refresh or data request was made. C1 remains blocked; C2 remains gated. Only visible decisions are logged; no private reasoning or secrets are stored.

## 2026-10-31 — BUP-01 point-in-time membership reconstruction
- Reviewed CC BY 4.0 dataset `aditya-jha/nse-historical-membership`; extracted NIFTY 50 interval subset (83 rows; upstream blob `519a9232e125cc044580ec7b90ef5c18475b4f0f`). Added attribution/provenance file and project CSV. Dataset's numeric `weightage` column is blank.
- Checked official NSE Indices press release dated 2026-02-23: no NIFTY 50 change effective 2026-03-30. Checked official 2026-08-10 release: WIPRO excluded and BSE included effective 2026-09-30 after 2026-09-29 close. Applied this correction to project interval data.
- Local check using half-open validity intervals yielded 50 unique members for all 103 month-end snapshots 2018-04-30 through 2026-10-31. Added regression tests and machine-readable audit. This does not validate every historical event independently; source docs flag pre-2018 drift, so confirmatory use starts 2018-04.
- Additional sources: Tipsheet says member-level monthly weights extend back to Jan 2008 but derive from NSE monthly weightage reports and preserve upstream terms; Hugging Face weights are CC BY-NC-SA non-commercial; other open GitHub files are binary/equal-weight approximations. No compliant free official IWF source established.
- Identified official NSE Indices data subscription (historical constituent names, identifiers, market caps, weights and prices) as the clear permissioned route; licensing enquiry at indices@nse.co.in.
- **Phase decision:** membership sub-gate PASS WITH LIMITATIONS; overall C1 BLOCKED on exact historical IWF, security IDs/corporate actions and full constituent intraday/close coverage. No model training.

## 2026-10-31 — Membership audit tests and workflow added
- Added an offline-only GitHub Actions workflow for the CC BY 4.0 NIFTY50 membership subset. It runs on membership/test changes and supports manual `workflow_dispatch`; no network market-data or Dhan auth calls are included.
- Added a test asserting machine-audit consistency and kept the overall C1 state BLOCKED pending licensed numerical IWF, security identity/corporate actions and full stock-bar coverage.
- The workflow was committed to the phase branch. Its Actions execution result is not yet independently confirmed in this log update; do not report the GitHub Actions tests as passed until the run is inspected.

## 2026-10-31 — Corrected C1 membership identity after Tata Motors demerger review
- **Error caught:** the public source had backfilled `TMPV` as the ticker for the pre-2025 Tata Motors security. NSE circular NSE/FAOP/70882 states the TATAMOTORS -> TMPV change is effective 2025-10-24; the project now models the old and new symbol intervals separately.
- NSE Indices press release 2025-10-07 includes the temporary zero-price `DUMMYTATAM` constituent in NIFTY 50 effective 2025-10-14; press release 2025-11-13 removes TMCV effective 2025-11-17. Project membership stores the dummy through 2025-11-16, marked `zero_price_dummy` and `market_data_required=FALSE`.
- The corrected 103 month-end snapshots have 50 entries on 102 dates and 51 on 2025-10-31, the sole month-end with the temporary dummy. This corrects the previous incorrect 103/103 all-50 assertion. The dummy is never included in the tradable stock panel.
- Updated the membership CSV, provenance, machine audit and six-test regression suite. Dedicated post-correction Actions run is pending; previous run 41184751617 passed the earlier four-test suite only and does not validate this correction.
- C1 remains blocked; no C2 panel/model or trading result created.

## 2026-10-31 — Membership test failure and CSV serialization correction
- Updated membership CI runs [41184902797](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41184902797) and [41184934278](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41184934278) both failed in the membership test step. Inspection showed an unquoted comma in the DUMMYTATAM notes field shifted CSV columns; the first run also checked a prior audit JSON revision (84 rows) before the 86-row audit correction landed.
- Corrected CSV serialization using valid quote escaping, kept the dummy note comma-free, and independently parsed the CSV: 86 rows, 11 columns, 85 unique symbols, all weightage fields blank, all member types/market-data flags present, and 103/103 month-end expected cardinalities pass (102×50 and 1×51).
- The post-fix membership workflow is queued as run [41185169548](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41185169548). Do not report CI PASS until this run completes and logs are checked.
