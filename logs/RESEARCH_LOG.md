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
- The post-fix membership workflow [41185169548](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41185169548) completed SUCCESS; the job log confirms 6 passed in 0.02s. This closes the CSV/test correction; C1 remains blocked on unrelated data/rights gates.

## 2026-10-31 — Corrected membership integrity workflow passed
- Post-correction GitHub Actions run [41185169548](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41185169548) completed SUCCESS; job log confirms **6 passed in 0.02s**.
- The run checked the final 86-row / 85-symbol dataset and updated audit file. It validates membership-file integrity only; it does not pass numerical IWF, full security identity/corporate-action coverage, constituent historical data or basket reconstruction.
- E0030 is resolved for the membership CSV/test sequencing defect. Overall C1 remains BLOCKED and C2 stays gated.


## 2026-11-01 — Five-year QA correction and live Dhan gate verification

- Inspected the complete job logs for run [41252703953](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41252703953). Its offline suite failed 1/26 because the post-market counter included a deliberately excluded 2021 Muhurat-session row. The implementation now reports special-session exclusions separately from true outside-hours bars.
- Verified run [41263593605](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41263593605): 26/26 offline tests passed. Weight cache integrity also passed, but the cached CC BY-NC-SA series remains non-commercial, estimated in some reconstitution intervals and ends 2025-08-31; it is not accepted as official point-in-time IWF.
- The live Dhan section of run 41263593605 was blocked: two token attempts returned HTTP 200 without an access token, diagnostics categorised the response as TOTP rejected/invalid, and fallback profile authentication returned HTTP 401. No market-data endpoint was reached. A stale/provided token is not an acceptable workaround.
- Confirmed earlier bounded live evidence: full current-universe 50/50 for one session (41249642409), full 50/50 for the 2026Q3 90-day slice (41251346795), and full 50/50 for the 2022Q4 90-day slice (41251808946). These separated slices do not establish uninterrupted coverage between them or across all five years.
- Added a fail-closed workflow status gate after the sanitized diagnostics commit so future live authentication/data failures cannot be mistaken for green research runs. No new token attempt was made after the blocked result.
- C1 remains NOT PASSED; C2–C6 remain pending/gated. No constituent panel, forecast, or strategy is claimed.


## 2026-11-01 — Workflow gate ordering review

- Review caught that the first fail-closed Dhan status-gate patch was positioned before the diagnostics commit. It was moved after the commit step before any further live run. The updated YAML was fetched back from GitHub and confirmed to commit sanitized status first, then enforce `PASS_ACTIVE_EQUITIES`.
- Error E0033 is closed for the ordering defect. Runtime behaviour remains to be verified on the next authorized protected Dhan preflight; no additional run was triggered while authentication remains blocked.

## 2026-11-01 — Resume: validator fix verified; live Dhan authentication blocked

- Re-read the C1 status, latest preflight JSON, previous successful preflight, research plan, operating rules, and research/error/conversation logs before continuing.
- Inspected the failure from run [41252703953](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41252703953). The Muhurat-session row was being counted in the ordinary outside-hours counter as well as in the separate special-session count. The correction makes those classifications disjoint. Offline regression suite passed **26/26** in [run 41263593605](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41263593605).
- Inspected all steps of run 41263593605 and its sanitized JSON. Live authentication failed: two TOTP token-generation attempts returned HTTP 200 without an access token; provider diagnostics classified the response as `TOTP_REJECTED_OR_INVALID`; the fallback access token returned profile HTTP 401. No security master, daily history, or intraday history call was made.
- The job conclusion was SUCCESS because the final fail-closed workflow step was not in the executed run. Read-back of the current C1 branch workflow confirms the enforcement step now follows the diagnostics commit; runtime verification is still pending.
- Previous successes remain valid only for their tested scopes: one session 50/50; 2026-06-29–2026-09-26 50/50; 2022-10-03–2022-12-30 50/50. The 2021-11-01–2022-01-29 edge range remains untested.
- Decision: stop automated token retries. Require corrected Dhan organization secrets or a configured API-key/secret OAuth flow before another protected live data run. C1 remains NOT PASSED; C2 stays gated. No stock model, index aggregation, forecast or strategy was produced.
- User-facing checkpoint: user asked to resume after a screenshot showing the 2021-edge QA investigation. The visible response explains the distinct offline-test and live-authentication blockers. Hidden private reasoning and secrets are not recorded.


## 2026-11-01 — Dhan TOTP parsing and clock diagnostics
- Resumed from the authenticated-data blocker without asking the user to reconfigure credentials. The previous evidence established only that Dhan's generated-token response lacked an access-token field and the fallback profile call returned HTTP 401; it did not prove the supplied setup was wrong.
- Merged PR #29 (commit cb7d304831f039bb994d819d5570a71f2bec0116): shared TOTP parser accepts raw Base32 and standard otpauth TOTP URIs; whitespace-only normalization for raw secrets; HTTP Date-based runner clock-skew diagnostic records integer seconds only.
- Regression coverage added for URI/raw equivalence, invalid HOTP/empty values and positive/negative clock skew. Workflow trigger paths include the new shared helper.
- Post-merge C1 research and source-audit workflows passed (41266155248, 41266155292). Dhan live workflow 41266155250 was still in dependency installation at last observation; no new auth/data result claimed.
- C1 remains blocked; no stock panel/model/forecast or strategy authorised.


## 2026-11-01 — Dhan auth helper regression suite verified

- First offline CI attempt [41266339150](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266339150) failed at collection because the minimal membership workflow installed pytest but omitted the Dhan helper's `pyotp` and `requests` dependencies. Logged as E0044.
- Added the dependencies explicitly. Follow-up [41266377005](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266377005) passed **12/12**: 6 existing membership tests plus 6 Dhan token/helper tests (including raw/otpauth TOTP parity, HOTP rejection and clock-skew sign tests).
- The live preflight [41266155250](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266155250) was still executing its protected Dhan preflight at last check. Do not claim authentication or coverage until its final sanitized JSON and fail-closed job conclusion are inspected.
- Current follow-up PR Dhan validation runs are pull-request/offline-only and cannot prove live-secret authentication.


## 2026-11-01 — Protected Dhan preflight recovered and five-year edge narrowed

- Protected Actions run [41266155250](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266155250) completed its live data step. Fresh TOTP token generation succeeded on attempt 1 (HTTP 200; access-token field present); profile confirmed Data API active; server-minus-runner UTC clock skew was **0 seconds**.
- Current NIFTY 50 universe resolved **50/50**; historical aliases resolved against the current master **79/84**. A single day (2026-10-29) had **50/50** anchor/15:14-expiry-proxy results.
- 3-stock 2022Q4 90-day test passed **3/3**; full 50-stock range tests passed **50/50** for 2026Q3 and **50/50** for 2022Q4. Reliance daily history returned 22 bars for Jan 2018 (existence check only).
- 2021-11-01–2022-01-29 full-universe range: 50/50 IDs resolved; 49/50 passed strict OHLCV checks. The 50 stocks all had 61 sessions, 61 anchor sessions and 61 expiry-proxy sessions with no missing days, duplicate timestamps, invalid numeric rows or OHLC violations. SHREECEM had one negative volume row, the only strict invariant failure.
- The new final workflow gate ran after the sanitized report was committed and deliberately failed the job on PARTIAL_OR_BLOCKED; no further false-green conclusion. E0032 (live token/profile auth blocker) and E0033 (status gate ordering/runtime) are now closed; E0045 tracks the single SHREECEM volume anomaly.
- Added a bounded single-stock SHREECEM diagnostic (one 90-day API request) to get the bad row timestamp, not its price or volume. Initial offline test exposed unsupported pandas .dt.isoformat; fixed to call Timestamp.isoformat() on row objects. Corrected diagnostic run is pending.
- **Gate outcome:** authentication and most sampled price-history gates pass, but C1 remains NOT PASSED due to the SHREECEM strict QA item, incomplete continuous five-year backfill, and the decisive unresolved official/licensed point-in-time IWF series and basket reconciliation. C2 remains gated. No stock model or forecast run.


## 2026-11-01 — SHREECEM diagnostic runner import-path correction

- Corrected diagnostic timestamp formatting; offline test run [41266604463](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266604463) then passed 2/2.
- The same run failed before network access because direct execution from the script subdirectory did not place repository root on sys.path (E0046). Added explicit repository-root insertion before project imports in commit 34e067d.
- The corrected push-triggered one-symbol run is pending. No extra full-universe data request is scheduled by this diagnostic workflow.


## 2026-11-01 — C1 bounded Dhan market-data gate passed; official IWF remains blocking

### Market-data and validation result
- Protected Dhan preflight [41266897788](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266897788) completed **SUCCESS** with final machine status `PASS_ACTIVE_EQUITIES`. The workflow committed its sanitized result and then passed its final fail-closed status gate.
- Dhan token refresh succeeded on attempt one; profile confirmed active Data API. HTTP Date minus runner UTC was **-1 second** (Date header second precision; immaterial).
- Current NIFTY 50 security master resolved 50/50. Historical membership aliases resolved against the current master 79/84.
- One-session all-constituent probe (2026-10-29): 50/50. Full 50-name 90-day tests: 2026-06-29–2026-09-26, 50/50; 2022-10-03–2022-12-30, 50/50; 2021-11-01–2022-01-29, 50/50. Each of the 61 regular sessions in the 2021 edge window had a valid 10:00–10:03 anchor and a 15:00–15:14 expiry proxy. These are three disjoint 90-day windows plus one session, not continuous five-year coverage.
- SHREECEM diagnostic [41266690449](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266690449) located the one negative-volume row at 2021-12-30 15:29 IST. It is after the locked 15:15 cutoff. QA now applies strict OHLCV validation only through 15:14 and separately reports 15:15–15:30 records. The corrected 50-stock edge sample passed 50/50; negative volume within the target interval still fails.
- Offline tests [41266922851](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266922851) passed **43/43**. E0045–E0048 have been resolved/closed in the error log.

### Point-in-time weight / data-rights source audit
- Read the current two-page official IWF guideline. It defines IWF from quarterly public shareholding and lists 22 exclusions. Some are simple categories (promoter, FDI, government, PE, SWF, locked-in, IEPF), while others need relationship or agreement context (cross-holdings, family, board rights, first-refusal, strategic control, PAC). An aggregate roll-up cannot be presumed to cover all of them.
- The official Nifty Indices monthly page lists two monthly weight ZIP families. The current Terms of Use prohibit systematic/automated collection without express written consent; no scraping or ZIP ingestion was attempted. NSE Index Data Subscription is the preferred licensed route and publishes a licensing contact.
- New category-level candidate assessed: [yurukatsu/nse-historical-membership](https://github.com/yurukatsu/nse-historical-membership), documenting 2,316 symbols, 62,850 filings, 2001-03 to 2026-08 and ~70 filing-by-category rows with broadcast timestamps, share counts, lock-in, DR, pledge and related fields. However the explicit `LICENSE-DATA` globs do not unambiguously include the nested parsed `_categories.csv.gz` or `_flat.csv` files. Several IWF exclusions also require holder/relationship/agreement evidence that category totals alone may not provide. No dataset file was copied/imported; no named-shareholder file will be used.
- TejHQ daily EOD/corporate-action/symbol-history data (NSE from 2010) has publisher terms updated 2026-10-30 allowing personal research, backtesting, model training and private local storage, but prohibits raw redistribution and says exchange terms apply independently. It is useful only as a secondary daily/identity/corporate-action cross-check, not intraday or IWF. Because this repo is public and Actions caches are extractable by people able to open PRs, no raw TejHQ dataset is committed/cached in this repo. Store only non-reconstructive QA summaries.
- The AMP4010 approximate weights remain non-commercial CC BY-NC-SA 4.0, estimated at rebalance transitions, ending 2025-08; not admitted.

### Gate decision
- **Dhan bounded intraday data QA: PASS.** Do not misstate this as full continuous five-year coverage.
- **C1 overall: NOT PASSED / RIGHTS-BLOCKED.** No admissible complete point-in-time official IWF series, verified mapping of all 22 exclusions, and weighted basket-to-index reconciliation exist yet.
- C2–C6 remain gated by the locked BUP-01 v1.1 plan. No constituent panel/model/forecast/strategy was created. No change was made to the locked plan.
- Remaining external path: written rights for official monthly weights, or explicit path-specific CC BY confirmation for the category dataset plus an independently passing 22-exclusion mapping/reconciliation. Do not replace missing IWF with equal weights, promoter complement or majority vote.


## 2026-11-01 — Final free-source sweep and official commercial-use route

- Added machine-readable detail as a reproducible [C1 Dhan 90-day validation report](../research/constituent_weekly/C1_DHAN_90D_VALIDATION_REPORT.md), reporting 50/50 pass on 2021 edge, 2022Q4 and 2026Q3 90-day windows and the 2026-10-29 full basket probe. These are non-contiguous samples, not continuous five-year coverage.
- Reviewed [NSE's first-basket data list](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Data%20list%20under%20NSE%20Data%20Sharing%20Policy%20for%20Research%20and%20Analysis_20250728.pdf): quarterly shareholding pattern appears as regulatory disclosure/research data; voluminous (>2 GB) corporate data including shareholding pattern can be chargeable.
- Reviewed the NSE Research Initiatives page and consolidated NSE Data Sharing & Usage Policy. Research Initiative access is explicitly academic/non-commercial; the policy defines Research Activity as research for purposes other than trading/profit. Commercial market data requires a relevant agreement; data use and caching/republication must be defined in that agreement. Therefore the free academic data route is not assumed to license this trading-research project.
- Further free-source candidates assessed: NSE/BSE filing access, detailed XBRL category dataset, TejHQ daily EOD/corporate actions, floyds1995 NSE historical-EOD GitHub repository, Nifty Chronicles top-10 official weights plus equally-split estimated residual and the NSE factsheet/whitepaper snapshots. No candidate clears the required complete point-in-time IWF, 22 exclusions, historic identity, data rights and internal algorithmic trading use gates.
- Added unsent [NSE_DATA_RIGHTS_REQUEST.md](../research/constituent_weekly/NSE_DATA_RIGHTS_REQUEST.md) to request the actual historical IWF/weight product plus licensed commercial use, automated access, private cache rights, identifier history and derivative-output rules. No request has been sent.
- **Gate outcome:** C1 market-data sampling passes, but C1 overall is still NOT PASSED / RIGHTS-BLOCKED. No stock panel or model is built. BUP-01 v1.1 remains locked; C2-C6 remain gated.


## 2026-11-01 — Requested external quant toolchain reviewed

- Recorded repository-level README and licence review for QuantEvolve, TradingAgents, AstraQuant, PySR, arch, tick and MAPIE in [TOOLING_EVALUATION.md](../research/constituent_weekly/TOOLING_EVALUATION.md).
- Decided not to import modelling/tooling dependencies in C1 because the registered plan requires C1 data/rights and C2 panel acceptance first. This avoids unnecessary dependencies and model/search leakage while no stock panel exists.
- Phase allocation: arch/PySR in bounded C3; MAPIE in C4 only after sequential coverage checks; TradingAgents as sandboxed hypothesis reviewer; QuantEvolve in limited C5 search only; tick deferred until validated event/tick data exists. AstraQuant excluded from integration due to custom AGPL/Commons Clause/addenda and OKX-specific execution path.
- No third-party source code was cloned or copied. No external exchange collectors or trading agents were run. BUP-01 v1.1 unchanged; overall C1 remains NOT PASSED / RIGHTS-BLOCKED.


## 2026-11-01 — IWF 22-exclusion and denominator audit completed

- Opened and visually reviewed the official NSE two-page IWF guideline PDF from the current NSE Indices IWF page. It enumerates 22 exclusions, says they are excluded where separately identifiable, and its worked example uses total shares as denominator and rounds IWF to six decimals.
- Added a row-by-row 22-item mapping matrix and a narrative audit. Several items are potentially present as XBRL categories; promoter family, group/associate ownership, director/KMP, board rights, first refusal, strategic purpose and PAC status require additional dated relationship/contract evidence. The candidate README/code does not prove every row.
- Mathematical hard check: the third-party parser's A+B+C2 percentage denominator is distinct from the total-share denominator shown in the IWF example. A reconstruction must use absolute share counts, total-share reconciliation, and position-level overlap removal; no percentage-complement shortcut is valid.
- Added pure arithmetic helpers and seven tests for the official example (0.608794), deduplication, denominator validity, 22-category evidence coverage and free-float weight normalization.
- The first CI run omitted the new test module from the pytest command (E0049) despite its path filter; corrected before acceptance. Corrected run [41269516064](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41269516064) and PR run [41269519499](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41269519499) each passed **50/50**. Source-audit run [41269430549](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41269430549) also passed.
- No category dataset, named-holder data, official monthly ZIP, or raw Dhan market bars were imported. The upstream parsed compressed CSV licence remains unclear for that nested file; official automated collection requires written data rights for intended use.
- The main repo is public; raw source data or personal shareholder records cannot be stored there as a cache. Only permitted metadata and aggregate QA summaries may be published pending rights review.
- **Gate result:** technical IWF calculation harness passes; data-source rights/completeness and official basket reconstruction remain NOT PASSED. BUP-01 v1.1 remains locked and C2–C6 remain gated.


## 2026-11-01 — C1 developer handoff issued

- Created [C1_DEVELOPER_GATE_REPORT.md](../research/constituent_weekly/C1_DEVELOPER_GATE_REPORT.md) after the final independent C1 repository review.
- Developer disposition: C1 PARTIAL PASS / RIGHTS-BLOCKED. Dhan bounded data QA and IWF arithmetic harness pass. Official point-in-time IWF rights/completeness, continuous five-year stock coverage, historical security identity/corporate-action mapping and weighted basket-to-index reconstruction remain open.
- C1 status file and main README now link the handoff. Plan v1.1 remains locked. No model, forecast, strategy or manuscript is claimed.


## 2026-11-01 — Public ETF portfolio holdings proxy discovery and calibration

- User approved use of available public web sources rather than making a separate NSE data-rights request a prerequisite.
- Located Nippon India ETF Nifty 50 BeES portfolio disclosures. AMC strategy statement says it invests in NIFTY 50 securities in the same proportion as the index; the February 2026 holdings PDF contains all 50 stock positions and 0.08% cash, with portfolio date 2026-02-28 and NAV date 2026-02-27.
- Compared those 50 stock holdings with the NSE Indices official white-paper weight snapshot dated 2026-02-27. After separately normalizing the 50 equity rows to 100%: 50/50 matched; MAE 0.002214 percentage points; RMSE 0.003204 pp; maximum absolute difference 0.008967 pp; Pearson correlation 0.99999895. This confirms a very close one-date calibration, not a historical time-series result.
- Reviewed the NSE FAQ describing self-weighting between events and the SEBI passive-scheme disclosure circular. The circular changes equity passive portfolio disclosure to within 10 days after each quarter, effective 2025-03-16. Actual publication dates remain necessary for strict look-ahead control; a +15-day imputed availability convention is included only as an explicitly flagged exploratory fallback with +10/+20-day sensitivity.
- Added public-source proxy audit, aggregate calibration summary, fixed-share weight-drift and comparison helper, 8 unit tests, and wired those tests into the C1 offline source-audit workflow.
- Updated BUP-01 plan to v1.2. Official index weights and ETF proxy weights remain separate. The original confirmatory standard is not silently relaxed; a proxy-only model, if later run, must be labelled exploratory and pass point-in-time membership, corporate-action, 98% weight coverage and basket/index reconciliation.
- No public raw intraday bars, named shareholder records or third-party licensed dataset have been imported. The proxy calibration is a small derived QA summary.
- Current result: C1 PARTIAL; ETF proxy source has passed one-date calibration but a historical series and point-in-time validation are not complete. C2 is not started; no bottom-up forecast or strategy has been produced.


## 2026-11-01 — AMC primary-disclosure archive audit and bounded probe

- Located the Nippon India AMC monthly portfolio archive, which lists monthly workbooks through Sep-2026 and older records back to 2018/2019; confirmed a direct Feb-2026 .xls link.
- AMFI also publishes monthly Excel composite reports, but its current terms limit usage to personal/non-commercial purposes. Because this project supports trading research, AMFI-hosted bulk data is not admitted without separate rights clearance.
- Independent source coverage points to 90 Nifty BeES monthly observations from Apr-2019 to Sep-2026. This is secondary corroboration only.
- Added a metadata-only AMC probe for Sep-2026, Feb-2026 and Apr-2019, including schema/header checks and SHA-256. It deliberately does not store holdings values or raw files.
- **Result at commit time:** workflow not yet executed; no historical weight series or C2 panel is claimed.
- Streamlined Actions: C0 governance now triggers only on the C0 branch; C1 offline regression and source-audit workflows use PR/manual triggers to avoid duplicate push+PR execution; duplicate IWF test command removed.
- C1 remains PARTIAL / NOT ACCEPTED FOR MODELLING.


## 2026-11-01 — AMC metadata probe dependency correction

- The initial workflow run [41274822097](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41274822097) installed the parser dependencies but omitted pytest, so the regression step failed before the workbook probe. No AMC workbook was downloaded in that attempt.
- Added pytest explicitly to the dedicated workflow's install command. Corrected run and archive/schema evidence are pending.
- This is a workflow setup failure only; the C1 source/rights and basket reconciliation gates remain unchanged.


## 2026-11-01 — AMC rendered-page link discovery correction

- The first corrected probe run [41274888924](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41274888924) passed all four offline parser tests, but found zero workbook hrefs because the runner's raw page response did not expose the rendered monthly-file links as standard .xls anchors.
- The official rendered page shows September 2026 and February 2026 monthly portfolio download controls; the resolved direct links use an AMC month-end workbook filename convention.
- Added a deterministic URL fallback using the calendar month-end and abbreviated month/year in the filename, while preserving HTML link discovery as the first choice. Added regression tests for September 2026, February 2026 and April 2019 candidate paths.
- Next bounded run will verify HTTP response and workbook schema; the April 2019 path and workbook availability are not yet confirmed.


## 2026-11-01 — AMC workbook container and concurrent report-push correction

- Run [41274969265](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41274969265) passed the five parser tests, and both recent AMC workbooks returned HTTP 200. The workbook bytes were XLSX, despite the .xls URL suffix; the previous fixed xlrd reader therefore failed. The guessed 2019 link returned 404.
- Updated the probe to detect Excel container signatures and choose openpyxl for XLSX and xlrd for legacy XLS. Added signature regression tests and removed an unrelated pandas fixture warning.
- The same Actions run created the sanitized report but its push raced with other C1 commits and was rejected. The workflow now rebases the report commit onto the latest C1 head before pushing.
- No holdings were extracted successfully in the failed run, and no raw data were stored. C1 remains PARTIAL / NOT ACCEPTED FOR MODELLING.


## 2026-11-01 — AMC workbook response-type diagnostic

- Run [41275027813](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41275027813) passed seven tests, but HTTP 200 responses for the Sep-2026 and Feb-2026 URLs did not begin with recognised XLSX or XLS file signatures; guessed Apr-2019 URL returned 404.
- Updated the probe to use browser-like headers and report only content type, bytes, SHA-256 and a 12-byte hexadecimal magic prefix. No body text or holdings data are logged. A 200 response will not pass until its payload is a real parseable workbook.
- Current result remains PARTIAL / BLOCKED; investigate the response type and exact archive download mechanism before admitting any holdings.


## 2026-11-01 — XLSX signature predicate corrected

- Run [41275096839](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41275096839) returned recent workbook metadata with XLSX ZIP signature 504b0304 and content type application/vnd.ms-excel. The code's byte-signature literal was double escaped, so it incorrectly rejected valid XLSX containers.
- Replaced escaped literals with bytes.fromhex signature constants and added matching tests. The next run will assess whether the real workbook schema contains the expected Nifty BeES holdings table.
- The previous report push raced with concurrent branch updates; the workflow now explicitly pulls/rebases before pushing. April 2019 guessed URL remains a 404 and is not used as source evidence.
- C1 remains PARTIAL / NOT ACCEPTED FOR MODELLING.
