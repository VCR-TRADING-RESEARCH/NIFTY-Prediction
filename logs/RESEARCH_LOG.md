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


## 2026-11-01 — AMC recent-month schema gate passed

- Corrected probe [run 41275178244](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41275178244) passed all seven offline tests and both required source-schema checks.
- September 2026 AMC workbook: HTTP 200, XLSX container, 108 sheets, Nifty BeES target found, ISIN/quantity/weight fields detected, 50 ISIN-bearing rows.
- February 2026 AMC workbook: HTTP 200, XLSX container, 111 sheets, target found, same fields detected, 50 ISIN-bearing rows.
- The older April 2019 archive record is shown on the AMC page but the guessed direct URL returned 404; this is recorded as link-discovery failure and not as missing historical data.
- Exact hashes, sizes, HTTP status and file signatures are in the sanitised probe report. No raw holdings, names, quantities, values or workbooks were committed.
- The automated report push raced with an independent C1 update. The report is now committed by the research controller and the workflow publisher uses bounded non-forced retries.
- Overall C1 remains PARTIAL / NOT ACCEPTED FOR MODELLING. Rights, publication dates, complete historical series, identity/actions, 98%/47-stock coverage and basket reconciliation remain open.


## 2026-11-01 — AMC metadata workflow and report publisher verified

- Follow-up workflow [41275487989](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41275487989) completed SUCCESS. The 7-test parser suite, three-month source probe, job-summary publication and sanitised report publication all completed.
- The bounded fetch/rebase/push loop resolved the prior concurrent-ref race without force-pushing. The current committed probe report is generated by the successful run.
- The two recent AMC workbook schema checks remain PASS_SCHEMA (Sep-2026 and Feb-2026, 50 ISIN-bearing holdings rows each); the guessed Apr-2019 direct URL remains 404 pending exact historical path discovery.
- C1 remains PARTIAL / NOT ACCEPTED FOR MODELLING because source-use rights, actual availability timestamps, full historical coverage, security/action alignment, 98%/47-stock coverage and basket reconciliation remain open.


## 2026-11-01 — Historical Nippon archive and amcs.fund discovery route

- Rechecked the official Nippon AMC page with its older archive sections. The visible month-end portfolio index extends back to September 2013, with an explicit April 2019 record. The previously tested Apr-2019 direct URL was only a modern filename guess and returned 404; it is not evidence of missing historical holdings.
- Read amcs.fund's published methodology: it claims to fetch fund houses' own Excel/ZIP disclosures, extract ISIN/quantity/market-value/%NAV fields, use the printed disclosure month, and link each monthly record to the original AMC file plus Internet Archive copy. The API index advertises /amcs, /manifest, /scheme/{id} and /month/{id} routes.
- Attempted to open the advertised API index successfully; it lists those route names. The /amcs JSON endpoint itself was inaccessible through the present browser fetch path, so no API payload, scheme id or historical URL was obtained. This is a source-discovery lead only, not an admitted dataset.
- The public-use/reuse licence of amcs.fund data is not verified. No holdings values or raw source workbook have been copied.
- C1 remains PARTIAL / NOT ACCEPTED FOR MODELLING. Rights, exact attachment links, availability timestamps, historical ISIN/action continuity, weight coverage and weighted basket-index reconciliation remain gates.


## 2026-11-01 — Official archive lower bound corrected; API metadata-only probe committed

- **Phase:** C1 — point-in-time universe and data-source feasibility.
- **Step/status:** Historical archive source discovery advanced; API metadata probe implementation committed; runtime API result pending.
- **Finding:** The rendered official Nippon India archive shows monthly portfolio index entries back to 30 September 2012, not just September 2013, and explicitly lists April 2019. The previously guessed April 2019 modern filename returned 404; this remains a wrong/unresolved link, not a missing-data finding.
- **Independent method/source lead:** amcs.fund's published methodology says it links each monthly row to the AMC's original source file and an Internet Archive copy, and takes the period from the date printed in the disclosure. Its API index lists /amcs and /manifest among the metadata routes. No API records or holdings were imported.
- **Implementation:** Added a metadata-only probe that requests the API index, AMC listing/detail and manifest only; it does not call a scheme holdings endpoint or download portfolio files. It filters output to whitelisted metadata fields/hosts and HEAD-checks only whitelisted original-AMC/Internet Archive links. Added offline sanitisation tests and a push/manual Actions workflow with bounded report publication retries.
- **Rights rule:** amcs.fund reuse rights for commercial/trading-research extraction, caching and redistribution remain unverified. Treat it only as a source locator pending licence review. Do not import holdings or train.
- **Plan:** Locked BUP-01 plan v1.2 unchanged.
- **Next gate:** Inspect the automated API metadata report; if it resolves a specific original Nippon disclosure link, test link availability via HEAD only, record disclosure date separately from first-publication date, and review source rights before any file body is downloaded.


## 2026-11-01 — AMC metadata probe regression fixture corrected

- **Phase:** C1 source-discovery automation.
- **Run:** [41276748532](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41276748532) failed in the offline tests: 3 passed, 1 failed; the network probe was skipped.
- **Diagnosis:** A single test fixture mixed AMC-list and scheme-detail records. The recursive matcher correctly included both Nippon-related objects, but the test expected only the AMC record.
- **Correction:** Separated the test fixture into the two distinct endpoint shapes. The metadata extraction code was not changed.
- **Next action:** Push-triggered workflow rerun; inspect API metadata and only original-source HEAD results. Rights remain unverified and C1 remains blocked.

 
## 2026-11-01 — amcs.fund metadata workflow passed; no source URLs surfaced

- **Phase:** C1 source discovery.
- **Run:** [41277022940](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41277022940), **SUCCESS**; 4/4 metadata sanitisation tests passed.
- **Observed:** API index, /amcs, Nippon AMC detail and /manifest all returned HTTP 200 / valid JSON. AMC record resolved to Nippon India; detail returned current Nifty BeES scheme metadata.
- **Limitation:** The /manifest response did not yield any whitelisted original-AMC or Internet Archive source URL for historical Nifty BeES files. No HEAD checks could be made. The exact April 2019 attachment remains unresolved.
- **Data/rights:** No scheme holdings route or source-file body was downloaded; no portfolio values were admitted. amcs.fund data-reuse rights for trading research remain unverified.
- **Correction:** E0062 closed after the successful follow-up run; it was an incorrectly mixed offline test fixture, not an API/data error.
- **Plan:** BUP-01 v1.2 remains locked. C1 remains PARTIAL / NOT ACCEPTED FOR MODELLING.


## 2026-11-01 — Alternative historical membership/weight routes assessed

- **Phase:** C1 — source feasibility and rights audit.
- **User request:** “Can you find alternatives?”
- **Primary alternative:** NSE Indices official historical reports page has an Archives of Daily/Monthly Reports selector; official monthly report page lists market-capitalisation and weightage ZIP reports. NSE All Reports lists a NIFTY 50/NIFTY Next 50 market-cap/weightage/beta report and a broader index market-cap/weightage report. The archive looks like the strongest exact-weight source, but month-by-month coverage, publication times and permitted research use remain unverified.
- **Rights check:** current NSE Indices Terms of Use prohibit systematic/automated collection absent express written consent and describe site use as personal/non-commercial. No scraper/cache will be enabled without consent or a subscription licence.
- **Membership alternative:** inspected aditya-jha/nse-historical-membership. Derived data are CC BY 4.0 with attribution; NIFTY 50 membership intervals begin 2014-01-01, README states high confidence from 2018 onward and best-effort earlier, and coverage lists last NIFTY 50 event as 2025-09-30. Historical weight values are null. Accept only as a membership comparator after reconciliation and update.
- **XBRL route:** NSE/BSE quarterly SHP filings offer independent ownership inputs. NSE IWF methodology has 22 exclusion classes; current promoter/FII/DII aggregates do not calculate IWF. A detailed classification and timestamp-aware parser must be built and tested against an official index-weight snapshot.
- **ETF proxy route:** HDFC, UTI and Nippon index-fund/ETF monthly portfolios can be compared by ISIN but remain proxies, subject to source-use rights and cash/derivative residuals. Do not substitute ETF weights for official index weights.
- **Rejected for current use:** AMP4010 Hugging Face historical NIFTY weight series is CC BY-NC-SA 4.0 and requires a separate commercial licence; it also uses monthly/event snapshots and between-snapshot assumptions.
- **Paid fallback:** NSE Indices data subscription describes historical constituent identifiers, market capitalisation, weights and prices and names quantitative research as a data-use category. Check only after free routes and rights/permission possibilities.
- **Implementation:** full assessment saved at research/constituent_weekly/C1_WEIGHT_ALTERNATIVES_ASSESSMENT.md. No model training or raw data ingestion occurred. Plan v1.2 remains unchanged.
- **Decision:** C1 remains PARTIAL / NOT ACCEPTED FOR MODELLING. The preferred next path is permissioned NSE weight reports + CC BY 4.0 PIT membership comparator + Dhan price-drift reconstruction with event resets and official basket reconciliation.

 
## 2026-11-01 — CC BY 4.0 membership alternative reconciled over 103 months

- **Phase:** C1 point-in-time universe source validation.
- **Source:** `aditya-jha/nse-historical-membership`, data licence CC BY 4.0. Copied the NIFTY 50-only subset with attribution and added the 2026-09-30 BSE/WIPRO transition supported by an independent reprint plus fund-portfolio cross-check.
- **Comparison:** Matched the alternative effective-dated table to the project’s C1 membership ledger for all 103 calendar month-ends from 2018-04 to 2026-10. The exact member sets match after restoring upstream canonical TMPV to pre-rename TATAMOTORS before 2025-10-24 and excluding the temporary DUMMYTATAM zero-price placeholder from the tradable-stock set.
- **Counts:** 50 members at 102 month-ends; 51 on 2025-10-31 only when the temporary dummy is included in the index ledger. This is not a mismatch.
- **CI:** Corrected membership regression run [41289992040](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41289992040) SUCCESS. C1 authorised-source audit [41289991986](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41289991986) SUCCESS. Dhan preflight run [41289992028](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41289992028) SUCCESS for offline/cache steps; live Dhan steps were skipped because it was a pull-request event.
- **Limitation:** All weights are blank in the imported CC BY source. Membership is now independently cross-checked, but historical numerical weights/IWF are not resolved.
- **Error correction:** E0063 logs that the test originally expected 79 rather than 103 months; the corrected test and suite passed.



## 2026-11-01 — mfdata.in historical-month endpoint probe (bounded attempt)

- **Phase / step:** BUP-01 C1 — independent mutual-fund source discovery and archive-history coverage.
- **Documentation reviewed:** [mfdata.in API docs](https://mfdata.in/docs) describe the no-auth /api/v1/search, /api/v1/families, and /api/v1/families/{family_id}/holdings/history routes. The history route returns available YYYY-MM labels; actual month-specific portfolio contents require a separate /holdings?month=YYYY-MM request, which was deliberately not called.
- **Implementation:** Updated scripts/constituent_weekly/probe_amcs_fund_metadata.py with documented search + family-catalogue + legacy-schemes bounded fallbacks; limited family-ID detail resolution and history probes; recursive month parsing; month-gap/continuity metrics. No per-security holdings values or source workbooks are retained.
- **Tests:** [Actions run 41297143071](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41297143071) passed 13/13 metadata parser/sanitisation tests and published the report.
- **Live result:** /search, /families and /schemes discovery requests all returned HTTP 522. The run never discovered a family ID, so the monthly history endpoint was not reached. No historical coverage result can be reported; the route remains **INCONCLUSIVE**, not zero coverage.
- **Rights/provenance:** Documentation says the API is free/no-auth and is rate limited; this does not establish a licence to extract, cache, redistribute or use aggregated upstream holdings in commercial trading research. No clear underlying financial-data licence, source-per-snapshot citation, or first-publication timestamp was established.
- **Phase outcome:** This route is retained as a documented fallback candidate, but it is not an admitted data source. No holdings downloaded, no model training, no forecast. BUP-01 plan v1.2 unchanged; C1 remains NOT PASSED / RIGHTS-BLOCKED.
- **Next bounded action:** No immediate network retry loop. Continue to an independently accessible AMC mother-source route only where access and data-use terms allow; reopen mfdata only when provider access is available.




## 2026-11-01 — Original AMC disclosure locator assessed as mfdata fallback

- **Source:** [amcs.fund monthly archive](https://amcs.fund/month) and [methodology](https://amcs.fund/methodology).
- **Source claim:** the site states it builds from each fund house's own monthly portfolio spreadsheet/ZIP, reads the month from the date printed in the disclosure, links source files and Internet Archive copies, and flags incomplete months where accessible files cover less than 70% of average fund-house AUM. These are provider methodology claims, not an independent reproduction yet.
- **Existing technical evidence:** the C1 metadata workflow returned valid JSON (HTTP 200) from the API index, AMC/scheme metadata and sampled month endpoints including 2019-04. The sanitizer kept metadata/schema only; it did not store security-level holdings or raw source files. The scheme snapshots also showed only a 13-month hold_hist cache, which is not accepted as complete historical coverage.
- **Research use:** retain amcs.fund as a route to discover the original AMC disclosure files and archived copies. For each scheme-month, the actual printed disclosure date, original URL, archive URL, ISIN identity, 50-stock presence, portfolio weight sum and source reuse rights must be checked.
- **Limitation:** ETF/index-fund weights are not NIFTY free-float IWF. They may include cash/derivatives or tracking residuals and may differ by scheme. Use only as a proxy/cross-check after a direct comparison with independently published index weights.
- **Rights:** no blanket licence to download/cache/re-publish the underlying AMC files was established. Public page availability does not override AMC source terms.
- **Disposition:** useful provenance path; not yet an admitted model input. C1 remains NOT PASSED / RIGHTS-BLOCKED; no C2 or trading backtest triggered.




## 2026-11-01 — v1.3 user-directed weight-free bottom-up index aggregation

- **User direction:** “No comparison needed. Proceed.” Applied narrowly to mean no ETF-holdings-versus-official-NIFTY-weight comparison; no ETF weight series or historical free-float IWF reconstruction is required for this active method.
- **Plan amendment:** registered BUP-01 v1.3. Stock targets remain the 10:00-to-15:15-proxy constituent price outcomes. For each expiry cycle, generate strictly out-of-fold stock probabilities/expected returns, summarize them with unweighted predicted breadth, probability/return means and medians, dispersion, sector breadth, concentration and valid-member coverage, then fit a chronological NIFTY-direction meta-model to the observed NIFTY index label.
- **Mathematical safeguard:** the actual NIFTY target is still the observed index series. An equal-weighted constituent mean is a diagnostic only, not the actual index return. The meta-model must not use in-sample stock predictions or predictions trained on the same expiry cycle.
- **C1 gates preserved/revised:** maintain point-in-time membership, stable ISIN/security IDs, corporate-action continuity, verified expiry/session calendar and continuous stock plus NIFTY index candles. Accepted cycles require at least 47 and at least 94% of eligible tradable constituents with valid forecasts; at least 98% of scheduled eligible cycles must have valid NIFTY targets; first confirmatory forecast requires 104 prior eligible cycles.
- **Rights control:** Nippon AMC bulk workbook automation is paused; no holdings values were admitted. Existing weights/ETF files and calibration reports remain historical audit material only and are not used or refreshed. The v1.3 C1 gate no longer requires weights or basket-to-index weight reconciliation.
- **Automation:** Dhan C1 workflow no longer refreshes the historical weight cache; AMC archive workflow now runs offline parser tests only. The v1.3 plan validator, member-count/OOF tests and manual/push offline workflow are updated.
- **Validation:** the preceding mother-source metadata workflow [41298336318](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41298336318) completed SUCCESS, including offline tests and metadata probe. The v1.3 plan/offline workflow is running on the amended branch; record its final result when complete.
- **Current phase decision:** C0 PASS; C1 PARTIAL / CONTINUOUS-COVERAGE GATE IN PROGRESS. No C2 panel, stock model, forecast, strategy or final manuscript exists. Locked plan v1.3; no weight comparison is to be performed.



## 2026-11-01 — C1 effective-dated security identity review

- **Finding:** the membership ledger uses canonical LTM for the 2023-07-13 to 2024-09-30 LTIMindtree interval. Exchange records show actual ticker LTIM throughout that interval, with LTIM→LTM effective 2026-02-27. The C2 identity resolver now distinguishes point-in-time ticker from current/canonical security key.
- **Additional aliases:** ZOMATO→ETERNAL from 2025-04-09; TATAGLOBAL→TATACONSUM from 2020-02-27; TATAMOTORS→TMPV from 2025-10-24. These are recorded as symbol history; scheme and demerger price discontinuities are not assumed adjusted.
- **Security safeguards:** HDFC Ltd (legacy Dhan ID 1330) remains a distinct security from HDFCBANK. Tata Motors demerger ex-date 2025-10-14 is retained as an event where raw return continuity is invalid. The placeholder DUMMYTATAM remains non-tradable.
- **Artifacts:** security_alias_history.csv, security_corporate_action_events.csv, security_identity.py, tests/test_c1_security_alias_history.py.
- **Limitation:** this is a major identity/event ledger, not a complete dividend/split/bonus/rights adjustment series. C1 stays partial; no model or stock return label is built from these mappings yet.
- **Workflow:** alias/identity regression run [41302695594](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41302695594) pending; continuous Dhan run [41301447865](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41301447865) was still processing at this log point.


## 2026-11-01 — Live C1 Dhan intraday target coverage completed; publication conflict recorded

- **Run:** [41301447865](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41301447865).
- **Result:** 258/258 weekly expiry cycles had valid observed NIFTY anchor/expiry-proxy target pairs; 258/258 met the stock input rule (at least 47 and at least 94%); 154 confirmatory cycles remain after 104 prior accepted cycles; zero unresolved active symbols; 1,083 Dhan requests across 21 windows.
- **Window:** first anchor 2021-11-12 through final expiry 2026-10-27. The 2024-01-31 to 2024-04-29 index window was PARTIAL_TARGET_DATES, despite the final 258/258 cycle-level target count. Exact partial-date detail is not recoverable.
- **Publication:** runner generated sanitized report; git pull --rebase conflicted on STATUS.md and RESEARCH_LOG.md. Final target-coverage gate printed PASS. Detailed per-cycle QA was not retained as an Actions artifact.
- **Next:** artifact upload before branch update, clean-reset/re-generate status publication, separate daily OHLCV audit and exhaustive action-aware return review before C2.


## 2026-11-01 — C1 Dhan daily OHLCV coverage

- **Auditor status:** COMPLETED_WITH_GAPS.
- **Window:** 2018-04-01 to 2026-10-30.
- **Coverage:** 68/69 parseable symbols; 94799/95900 valid OHLC member sessions; weighted OHLCV coverage 98.85%.
- **API/cache:** 69 requests; 0 symbols reused from the sanitized QA cache.
- **Interpretation:** daily OHLCV coverage is reported independently from intraday target coverage, historical identity and action-adjusted return integrity. No model is trained and C2 remains gated.
- **Artifacts:** C1_DAILY_COVERAGE.json and C1_DAILY_COVERAGE_REPORT.md.


## 2026-11-01 — C1 continuous stock/index target coverage

- **Auditor status:** PARTIAL_OR_BLOCKED_TARGET_COVERAGE; data-coverage gate: FAIL; identity/action gate: SYMBOL_MAPPING_RESOLVED_KNOWN_AND_UNIVERSAL_CORPORATE_ACTION_REVIEW_PENDING.
- **Window:** 2021-11-12 to 2026-10-27.
- **Coverage:** 77/258 valid NIFTY targets; 64 cycles meet the stock and index data rules; 0 confirmatory cycles after the 104-cycle warm-up.
- **API/cache:** 1083 requests this run; reused 0 index and 0 stock-symbol chunks.
- **Interpretation:** data coverage is assessed independently of security identity/corporate-action treatment. This audit does not train or evaluate a model and does not unlock C2.
- **Artifacts:** C1_CONTINUOUS_COVERAGE.json and C1_CONTINUOUS_COVERAGE_REPORT.md.


## 2026-11-01 — Full C1 intraday artifact retrieved; target coverage reconciliation

- **Authoritative run:** [41309632317](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41309632317), artifact 13086220727. The complete sanitized JSON with all per-cycle and index-chunk date QA was downloaded and inspected.
- **Result:** intraday target gate PASS; 258/258 weekly expiry cycles valid; 258/258 stock-input cycles meet 47 members and at least 94% coverage; 154 confirmatory cycles after 104 prior accepted cycles; 98% minimum member coverage; median 50 valid members; zero unresolved active symbols; 1,083 requests over 21 windows.
- **Partial-window explanation:** the only partial date is 2024-04-26 at 15:14, while the 10:00 anchor passes. This was not an expiry day. The cycle anchored 2024-04-26 expires 2024-05-02; its actual expiry proxy, stock coverage and index target all pass.
- **Reconciliation:** earlier 77/258 and 64 accepted-cycle values are from an earlier incomplete run and remain historical; they are superseded as current gate evidence by the later full artifact.
- **C1 remains partial overall:** the first daily run found 98.85% OHLCV member-session coverage but HDFC legacy history and one TATAMOTORS date missing. The corrected TejHQ personal-use fallback is awaiting its live run. Full action-aware return validation remains open.


## 2026-11-01 — C1 daily fallback safeguards and regression validation

- Added an explicit TEJHQ_PERSONAL_USE_ONLY=1 runtime guard before any TejHQ fallback download. Without the flag, fallback is skipped; without HF_TOKEN, it is skipped.
- Changed encrypted cache publication to a run-unique key plus a dataset/revision restore prefix. This avoids immutable GitHub cache-key collisions preventing the addition of year partitions on later runs.
- The common C1 offline regression workflow passed **88 tests** in Actions run [41315241386](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41315241386). This includes AES-GCM cache, personal-use guard, HDFC boundary, TejHQ EQ/ISIN/row QA and Tata cross-source check tests.
- Live TejHQ fallback has not yet run; no fallback sessions are counted in coverage. Dhan daily coverage remains at the last measured first-pass result until the next serialized live daily job completes.
- Overall C1 remains PARTIAL; daily feature gaps and full action-aware return integrity remain open.


## 2026-11-01T14:34:44.970940+00:00 — C1 Dhan daily OHLCV coverage

- **Auditor status:** COMPLETED_WITH_GAPS.
- **Window:** 2018-04-01 to 2026-10-30.
- **Calendar:** 1918 official NIFTY sessions plus 210 validated Dhan index sessions; combined sessions 2128.
- **Coverage:** 69/70 parseable Dhan symbols; 106385/106392 valid OHLC member sessions; weighted OHLCV coverage 99.9934%.
- **Fallback:** COMPLETED_WITH_GAPS; 1295 validated member sessions added from the pinned encrypted-cache source.
- **Residual gaps:** HDFC: 6 (2018-11-07, 2019-10-27, 2020-02-01, 2020-11-14, 2021-11-04, 2022-10-24; sample complete); TATAMOTORS: 1 (2025-10-21; sample complete).
- **API/cache:** 2 requests; 70 symbols reused from the sanitized QA cache.
- **Interpretation:** daily OHLCV coverage is reported independently from intraday target coverage, historical identity and action-adjusted return integrity. No model is trained and C2 remains gated.
- **Artifacts:** C1_DAILY_COVERAGE.json and C1_DAILY_COVERAGE_REPORT.md.


## 2026-11-01T14:42:05.550037+00:00 — C1 Dhan daily OHLCV coverage

- **Auditor status:** COMPLETED_WITH_GAPS.
- **Window:** 2018-04-01 to 2026-10-30.
- **Calendar:** 1918 official NIFTY sessions plus 210 validated Dhan index sessions; combined sessions 2128.
- **Coverage:** 69/70 parseable Dhan symbols; 106385/106392 valid OHLC member sessions; weighted OHLCV coverage 99.9934%.
- **Fallback:** COMPLETED_WITH_GAPS; 1295 validated member sessions added from the pinned encrypted-cache source.
- **Residual gaps:** HDFC: 6 (2018-11-07, 2019-10-27, 2020-02-01, 2020-11-14, 2021-11-04, 2022-10-24; sample complete); TATAMOTORS: 1 (2025-10-21; sample complete).
- **API/cache:** 2 requests; 70 symbols reused from the sanitized QA cache.
- **Interpretation:** daily OHLCV coverage is reported independently from intraday target coverage, historical identity and action-adjusted return integrity. No model is trained and C2 remains gated.
- **Artifacts:** C1_DAILY_COVERAGE.json and C1_DAILY_COVERAGE_REPORT.md.


## 2026-11-01T14:42:05.550037+00:00 — C1 encrypted cache path correction

- **Code correction:** The encrypted TejHQ cache path now expands `~` before resolving to an absolute path; regression coverage added for tilde and explicit paths.
- **Actions:** Offline suite [41317402493](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41317402493) passed; live daily workflow [41317402483](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41317402483) completed successfully.
- **Cache:** First run after the correction had no valid prior cache and therefore downloaded seven pinned yearly partitions. The encrypted cache save step then stored 87,911,829 bytes under the new shared key. The next compatible workflow must verify cache hits; reuse is not yet claimed.
- **Coverage:** No change to the last audited 106,385/106,392 (99.9934%) member-session coverage or seven residual dates. C1 remains PARTIAL; action-adjusted return audit remains open; no model trained.


## 2026-11-01 — C1 corporate-action candidate catalogue

- Live workflow [41318287855](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41318287855) completed successfully, including offline action/identity tests, pinned-source download, encrypted-cache save and sanitized artifact publication.
- Candidate catalogue: 18,393 NSE rows, 18,361 deduplicated events, 32 duplicates, 711 point-in-time constituent matches. Matched events: dividends 625, bonus 19, splits 9, rights 6, buybacks 20, merger/demerger 3, other 29.
- No factor was calculated or applied. Official NSE derivatives adjustment methodology is documented separately and explicitly not treated as a blanket cash-equity adjustment method.
- Cache directory mismatch was identified in both workflows and aligned to the absolute runner temporary directory. New workflow tests guard this path; live cache-hit verification remains pending.
- Next C1 task: verify each matched member event against official NSE/BSE corporate-action records and issuer filings; build an event-specific adjustment/exclusion ledger with source links, formula inputs and reproducible checks. Only then re-audit daily/expiry return continuity.
- C1 remains PARTIAL/NOT PASSED; no model trained and no C2 entry.


## 2026-11-01T15:01:28.039610+00:00 — C1 Dhan daily OHLCV coverage

- **Auditor status:** COMPLETED_WITH_GAPS.
- **Window:** 2018-04-01 to 2026-10-30.
- **Calendar:** 1918 official NIFTY sessions plus 210 validated Dhan index sessions; combined sessions 2128.
- **Coverage:** 69/70 parseable Dhan symbols; 106385/106392 valid OHLC member sessions; weighted OHLCV coverage 99.9934%.
- **Fallback:** COMPLETED_WITH_GAPS; 1295 validated member sessions added from the pinned encrypted-cache source.
- **Residual gaps:** HDFC: 6 (2018-11-07, 2019-10-27, 2020-02-01, 2020-11-14, 2021-11-04, 2022-10-24; sample complete); TATAMOTORS: 1 (2025-10-21; sample complete).
- **API/cache:** 2 requests; 70 symbols reused from the sanitized QA cache.
- **Interpretation:** daily OHLCV coverage is reported independently from intraday target coverage, historical identity and action-adjusted return integrity. No model is trained and C2 remains gated.
- **Artifacts:** C1_DAILY_COVERAGE.json and C1_DAILY_COVERAGE_REPORT.md.


## 2026-11-01 — C1 shared-cache workflow regression validation

- The daily and corporate-action workflow YAML files now use the same explicit `${{ runner.temp }}/bup01-tejhq-encrypted` path for restore, Python runtime and save.
- Added static regression assertions for both workflows and a shared-helper test for the corporate-action cache path.
- Pull-request CI [41319075705](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41319075705) passed; Dhan preflight [41319075672](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41319075672) passed its offline checks; continuous coverage [41319075683](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41319075683) passed its offline validation. Live Dhan steps were correctly skipped on pull-request events.
- The live corporate-action run [41318287855](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41318287855) predates the absolute-path correction; it reported 0 action-partition cache hits. A post-correction live run is still required to prove cache reuse.


## 2026-11-01 — C1 corporate-action official-source and cache verification checkpoint

- Latest offline regression workflow [41319197109](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41319197109) passed 93 tests.
- Latest daily coverage workflow [41318960344](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41318960344) passed; 106,385/106,392 daily member sessions (99.9934%) and seven residual sessions remain unchanged.
- Latest corporate-action workflow [41318960367](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41318960367) passed; 18,393 raw candidates, 18,361 deduplicated, 711 PIT member matches. Zero action-cache hits were expected because the restored cache was populated by the daily workflow and did not contain the action parquet namespace. Nine action partitions were saved for subsequent reuse.
- Official NSE sources located: [Corporate Filings—Corporate Actions](https://www.nseindia.com/companies-listing/corporate-filings-actions), with symbol/company, purpose, ex-date, record-date and CSV controls; [NSE All Reports data description](https://www.nseindia.com/static/products-services/equity-market-data-reports-download), which describes the daily symbol/series corporate-action report; [NSE derivative adjustment methodology](https://www.nseindia.com/static/products-services/equity-derivatives-corporate-actions-adjustments). The latter applies to derivative contract adjustment and is not adopted as a blanket equity-price adjustment formula.
- Added a test that verifies encrypted action partition cache round-trip, with the first call downloading and the second reusing cached ciphertext.
- Next: run the action workflow to verify cache hits; then build the official NSE event cross-check adapter, match by symbol/series/ISIN and ex-date, and manually classify the 711 constituent events. Do not use unverified events or factors in target construction.
- C1 remains PARTIAL/NOT PASSED; no C2 model training or trading strategy.


## 2026-11-01 — Corporate-action encrypted cache reuse verified

- The new encrypted partition round-trip test passed within the corporate-action workflow: 13/13 action and identity tests passed.
- Live corporate-action run [41319736877](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41319736877) restored the prior encrypted cache created by run 41318960367.
- All nine action-year partitions (2018–2026) were decrypted from cache: 9/9 cache hits; zero downloads. Cache reuse is now verified, not merely inferred from cache step success.
- Candidate event count and matching remained unchanged at 18,361 deduplicated events and 711 PIT member matches.
- Official NSE Market Activity Report documentation describes `Bcddmmyy.csv` within daily `nuprddmmyy.zip` as the daily corporate-action detail file. It is the next candidate primary-source cross-check route; archive URL/date coverage/schema still require live validation.
- No factor was calculated/applied; C1 corporate-action gate remains NOT PASSED; C2 remains locked.


## 2026-11-02 — C1 special-session calendar reconciliation

- Reviewed all seven residual daily OHLCV security/date gaps against NSE circulars and NSE Market Pulse. Six dates are Diwali Muhurat sessions; 2020-02-01 was a full 09:15–15:30 Union Budget trading session.
- The special-session dates remain genuine exchange trading dates and remain in the coverage denominator. This corrects the risk of misclassifying them as ordinary holidays or assuming all sessions use normal daytime hours.
- No prices were imputed and no gaps were waived. Targeted independent daily-bar reconciliation is still required for all seven security/date pairs.
- Audit: `research/constituent_weekly/C1_SPECIAL_SESSION_CALENDAR_RECONCILIATION.md`. Evidence includes NSE circulars NSE/CMTR/39216, NSE/CMTR/43290, NSE/CMTR/50050, NSE/FAOP/54024, NSE/CMTR/70319 and NSE Market Pulse November 2024.
- C1 remains PARTIAL / NOT PASSED; C2 remains locked.

## 2026-11-02 — C1 special-session source cross-check setup
- Added a dedicated, bounded audit for the seven residual security/session pairs. It checks a pinned daily NSE bhavcopy mirror and queries the exact NSE archive URLs; it does not download the full security universe.
- The mirror maintainer documents the OHLCV files as sourced from NSE archive endpoints. Its collector enumerates weekdays, so absent weekend sessions are not classified as exchange closures.
- Raw exchange bars are temporary-only. The committed output will contain row status, validity flags and hashes, not numerical prices or volumes. The mirror's MIT software licence is not treated as a market-data licence.
- First preflight run 41340624209 stopped before network data retrieval: five tests passed and one ISO-date parser test failed. Logged as E0086; corrected the parser and success-gated result publication.
- **Status:** targeted source audit implementation committed; live rerun pending. Existing C1 daily coverage remains 99.9934% with seven unresolved bars; C1 remains PARTIAL and C2/confirmatory modelling remain LOCKED.

## 2026-11-02 — Independent NSE bhavcopy mirror cross-check

- Audited seven exact security/date pairs using the pinned public NSE bhavcopy mirror.
- Valid EQ OHLCV rows: 4/7; mirror no-row: 3; duplicate rows: 0; unavailable source partitions: 0.
- The mirror collector enumerates weekdays only, so no-row on 2019-10-27, 2020-02-01 and 2020-11-14 is inconclusive for those special sessions.
- No raw prices/volumes were copied, no bar was fabricated, and the daily coverage denominator was unchanged. Corporate-action review remains open.
- Evidence: C1_INDEPENDENT_BHAVCOPY_AUDIT.md and C1_INDEPENDENT_BHAVCOPY_AUDIT.json.

## 2026-11-02 — Direct NSE special-session archive cross-check

- Direct NSE legacy cash-market archives validate all three remaining HDFC special-session EQ rows: 2019-10-27, 2020-02-01 and 2020-11-14.
- Combined with four valid independent-mirror rows, all seven residual security/date pairs have source-level OHLCV evidence.
- Cache enhancement now persists the three raw direct-NSE rows in the existing AES-GCM GitHub Actions cache using the HF_TOKEN-derived key. Cache SHA-256 is recorded in the direct audit JSON; no raw values are committed or uploaded.
- Base daily coverage JSON remains 106,385/106,392 until the encrypted supplemental rows are merged into the feature panel and the daily auditor is rerun. Corporate-action gate remains NOT PASSED; C2 remains locked.

## 2026-11-02 — Direct NSE encrypted-cache dependency correction

## 2026-11-02 — Direct NSE encrypted-cache dependency correction

- The direct NSE archive audit validates 3/3 special-session rows. A follow-up attempt to persist the raw rows into the encrypted cache exposed a missing runtime dependency (`pyotp`) from the shared cache-encryption module.
- Updated the workflow dependency installation to use the project's runtime requirements plus cache dependencies. No raw values were committed; encrypted cache persistence remains pending rerun.


## 2026-11-01T19:56:40.493291+00:00 — C1 Dhan daily OHLCV coverage

- **Auditor status:** COMPLETE.
- **Window:** 2018-04-01 to 2026-10-30.
- **Calendar:** 1918 official NIFTY sessions plus 210 validated Dhan index sessions; combined sessions 2128.
- **Coverage:** 69/70 parseable Dhan symbols; 106392/106392 valid OHLC member sessions; weighted OHLCV coverage 100.0000%.
- **Fallback:** COMPLETED; 1302 validated member sessions added from the pinned encrypted-cache source.
- **Residual gaps:** none.
- **API/cache:** 1 requests; 70 symbols reused from the sanitized QA cache.
- **Interpretation:** daily OHLCV coverage is reported independently from intraday target coverage, historical identity and action-adjusted return integrity. No model is trained and C2 remains gated.
- **Artifacts:** C1_DAILY_COVERAGE.json and C1_DAILY_COVERAGE_REPORT.md.

## 2026-11-02 — Direct NSE residual archive integration and daily coverage completion

- Direct NSE legacy/UDiFF bhavcopy archives independently validated all seven residual member/date pairs: six HDFC sessions and TATAMOTORS 2025-10-21. Each had one EQ row, valid OHLC/volume and matching ISIN.
- Raw residual rows were encrypted with the existing HF_TOKEN-derived AES-GCM cache key; the cache was restored with seven TejHQ year partitions and zero partition downloads.
- The daily coverage auditor now decrypts and merges the supplemental rows with the pinned TejHQ fallback. Successful run [41344197015](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41344197015) reports COMPLETE: 106,392/106,392 OHLCV member sessions, zero symbol gaps, 100% minimum per-symbol coverage, and no unresolved security IDs.
- Daily data coverage is complete. C1 overall remains gated by the separate corporate-action adjustment/issuer verification and other registered C1 checks; C2 remains locked.


## 2026-11-02 — Official NSE corporate-action source route identified

- Reviewed NSE's official Description of Market Activity Reports, the 1-Oct-2025 NSE/CMTR/70563 nomenclature circular, the live Corporate Actions CSV interface and NSE Clearing report documentation.
- Identified the daily PR/legacy archive corporate-action member as a plausible official mother-source cross-check for the 711 point-in-time member-event candidates; announcement and board-meeting files may provide additional event context.
- Recorded a bounded archive/schema probe and event-matching protocol in C1_OFFICIAL_CORPORATE_ACTION_SOURCE_FEASIBILITY.md.
- This was source discovery only: no raw source downloaded, no event adjudicated, no price factor applied. C1 remains PARTIAL / NOT PASSED; C2 remains gated.


## 2026-11-02 — Official NSE PR archive probe implementation

- Implemented a bounded fixed-date archive probe covering 2018-04-02, 2024-04-17, 2025-10-14 and 2026-04-17 to test both sides of NSE Circular NSE/CMTR/70563's 13-Oct-2025 naming transition.
- Added URL candidate handling for the legacy `nuprDDMMYY.zip` and current `PRDDMMYY.zip` names, ZIP validation, corporate-action member detection, CSV-header-only schema inspection, and announcement/board-meeting member checks.
- Raw archives are AES-GCM encrypted in the Actions cache; public report outputs contain hashes and schema metadata only.
- Added three offline regression tests and integrated the probe into the C1 corporate-action workflow's push-path and manual-dispatch paths.
- **Runtime execution:** Actions run [41422655123](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41422655123) started automatically on the matching branch push. Offline validation and cache restore passed; the catalogue step was still running at this log update. Static review caught and corrected a case-sensitive URL-path bug before trusting the source result; see E0109 in ERROR_LOG.md. The first run checked out the pre-fix revision and is not accepted as source evidence. The corrected script/test commits trigger a fresh run.
- C1 remains PARTIAL / NOT PASSED; C2 remains gated; no holdout tuning or strategy test was started.


## 2026-11-02 — Official NSE PR archive fixed-date probe PASS

- Corrected probe-only Actions run [41423606062](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41423606062) passed the offline tests, restored the encrypted archive cache, ran the probe, uploaded the sanitised artifact and published the reports to the C1 branch.
- **4/4** selected trading dates passed: 2018-04-02, 2024-04-16, 2025-10-14 and 2026-04-17. The previously selected 17-Apr-2024 was an official market holiday (NSE CMTR/59722) and was correctly replaced by 16-Apr-2024.
- Empirically confirmed website archive URL pattern: `https://nsearchives.nseindia.com/archives/equities/bhavcopy/pr/PRDDMMYY.zip`.
- Each archive contained a corporate-action CSV, announcement text and board-meeting text. The corporate-action CSV schema was consistent across all four dates (10 columns: SERIES, SYMBOL, SECURITY, RECORD_DT, BC_STRT_DT, BC_END_DT, EX_DT, ND_STRT_DT, ND_END_DT, PURPOSE).
- The final retest reused 4/4 encrypted archive cache entries. Raw bytes remain AES-GCM encrypted in Actions cache; public artifacts contain only metadata, hashes and headers.
- Corrected publisher now preserves generated reports across branch synchronisation; read-back verified the new 4/4 report and machine result.
- This is a bounded source/schema feasibility pass only—not proof of complete historical coverage or licence for bulk extraction. No candidate events were matched/adjudicated, no price factors calculated, and C1 remains PARTIAL / NOT PASSED; C2 remains gated.


## 2026-11-02 — NSE data-rights review and alternate source decision

- Reviewed NSE Terms of Use, Data Sharing & Usage Policy, Non-Display Usage Policy and NSE Research Initiative. NSE terms prohibit systematic/automated collection from the website without express written consent; non-display policy covers automated trading-decision algorithms and derived data. Research access is described as academic/non-commercial.
- Decision: do not expand the successful four-date technical probe into a 711-event automated NSE archive crawl without an applicable written permission/agreement.
- Evaluated the existing Dhan subscription as the next route. Dhan documents daily historical OHLCV from instrument inception and says daily history is adjusted for bonuses and splits; no claim is made that it covers dividends, rights, mergers or all contract adjustments.
- Added [C1_DATA_RIGHTS_AND_ALTERNATIVES.md](research/constituent_weekly/C1_DATA_RIGHTS_AND_ALTERNATIVES.md) and updated the feasibility report.
- Next: controlled Dhan adjusted-price diagnostic against the encrypted candidate event catalogue; targeted issuer-first-party verification only where access terms permit. C1 remains PARTIAL / NOT PASSED; C2 remains gated.


## 2026-11-02 — Dhan adjusted-price diagnostics (two event classes)

- Run [41426184727](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41426184727) successfully refreshed a Dhan token through TOTP (HTTP 200, one attempt; profile and data plan active). Two encrypted TejHQ year partitions were restored from cache; zero new partition downloads.
- Reliance 1:1 bonus (28-Oct-2024): 9/9 sessions; relative Dhan-adjusted/raw OHLC factor = 0.5 across open/high/low/close; post-event ratios = 1.0. PASS.
- Bajaj Finserv 5:1 split plus 1:1 bonus (13-Sep-2022): 11/11 sessions; relative Dhan-adjusted/raw OHLC factor = 0.1 across all four OHLC fields. Price-factor check PASS.
- **Identity warning:** NSE Circular CML53597 is internally inconsistent: its first sentence says w.e.f. 14-Sep-2022, while the next says trades from the 13-Sep ex-date. A MarketScreener reproduction of BSE Notice 20220908-17 also says 13-Sep, but the original BSE notice was not independently retrieved. TejHQ rows transition on 14-Sep. Logged as E0118; no date was silently selected or corrected. The factor pass is not an identity pass.
- Overall diagnostic PARTIAL_OR_BLOCKED. No raw prices/ISINs published; no factor applied to the full panel. Dividends, rights, mergers/demergers and buybacks remain outside this two-event test. C1 remains PARTIAL / NOT PASSED; C2 remains gated.
- Direct NSE bulk scraping remains prohibited absent written consent/agreement. See C1_DATA_RIGHTS_AND_ALTERNATIVES.md.

## GitHub Pages publication — 2026-11-02

- Sanitised C1 status, source-feasibility reports, data-rights notes and machine-readable NSE/Dhan diagnostics were copied to `docs/research/constituent_weekly/` on main.
- Pages deployment [41427840788](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41427840788) completed successfully.
- Live C1 research page: https://vcr-trading-research.github.io/NIFTY-Prediction/research/constituent_weekly/
- The page publishes only metadata, ratios, hashes, status and source links; no raw prices, event rows, ISIN values, tokens or credentials.


- The Pages deployment was refreshed after clarifying the conflicting BAJAJFINSV ISIN date wording in NSE CML53597; latest deployment run [41427840788](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41427840788) succeeded.


## 2026-11-03 — C1 event-level review protocol

- Reviewed the current C1 status, data-rights assessment, corporate-action catalogue, Dhan adjustment diagnostic, continuous coverage report, C4 gate and relevant project conversation history.
- Confirmed the C1 catalogue contains 711 point-in-time member-event candidates: 625 dividends, 20 buybacks, 19 bonuses, 9 splits, 6 rights, 3 merger/demerger and 29 AGM/other events.
- Added `research/constituent_weekly/C1_EVENT_REVIEW_PROTOCOL.md` on the C1 phase branch. The protocol preserves price-index dividend semantics, prevents double application of Dhan split/bonus adjustments, separates price-factor validation from security-identity validation, and defines event-window exclusion rules.
- No new event was verified and no adjustment factor was applied. C1 remains PARTIAL; C2/C4 confirmatory remain gated. This is a bounded process deliverable, not an empirical pass.


## 2026-11-03 — BAJAJFINSV identity-date discrepancy resolved

- Re-examined E0118 using the original NSE listing circular, the NSE Clearing contract-adjustment circular FAOP53644 and the BSE Notice 20220908-17 reproduction.
- NSE Clearing confirms ex-date 2022-09-13 and the combined 10x adjustment factor; both the explicit trade-effective clause in NSE CML53597 and the BSE notice reproduction state that the new ISIN applies to trades from 13-Sep.
- Decision: derived security mapping uses the new ISIN from 2022-09-13 inclusive. The old ISIN retained in the TejHQ row on that date is flagged as stale source metadata and is not rewritten.
- Added [C1_BAJAJFINSV_ISIN_ADJUDICATION.md](research/constituent_weekly/C1_BAJAJFINSV_ISIN_ADJUDICATION.md); E0118 closed with adjudication. This does not close the remaining C1 event review.


## 2026-11-03 — CI efficiency review

- The C1 protocol and adjudication files were committed in multiple sequential branch writes. The open C1 PR consequently launched multiple path-filtered validation workflows. This did not affect research data, but was unnecessary CI churn.
- Corrective rule: batch related branch-file changes into one Git tree/commit per logical step, then monitor the single resulting PR validation set. Recorded as E0120.


## 2026-11-03 — First protected intraday adjustment attempt

- Run [41507896770](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41507896770) successfully refreshed Dhan credentials and revalidated daily adjustment factors: RELIANCE 0.5 (9/9 sessions), BAJAJFINSV 0.1 (11/11 sessions). No intraday result was produced.
- Intraday script failed before the API request due to missing repository-root Python path (E0121). The workflow's daily gate also expected an obsolete status string (E0122).
- Correction batch adds the repository-root import bootstrap, a unit test for the adjudicated BAJAJFINSV date, and fail-closed gate checks against the actual machine result schemas. C1 remains PARTIAL.


## 2026-11-03 — Daily corporate-action sub-gate passed; intraday token handoff correction

- Run [41508838557](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41508838557) passed all 14 offline math/diagnostic tests and the protected daily adjusted-price diagnostic. Dhan authentication succeeded; RELIANCE bonus factor was 0.5 across OHLC (9/9 sessions) and BAJAJFINSV split+bonus factor was 0.1 across OHLC (11/11 sessions). The 13-Sep identity discrepancy was handled with the documented derived override while the raw source row remained unchanged.
- The intraday step made no price request: it attempted a second TOTP refresh in the same workflow, which returned no token, and the fallback profile check returned HTTP 401. Logged as E0123.
- Correction: hand off the first profile/data-plan validated token only through private Actions `GITHUB_ENV`, masked, and reuse it for the intraday request; no token is retained in the repository or artifact. The same run also exposed that the previous workflow file still contained the stale gate status string; its check is now being replaced with the actual machine status contract.


## 2026-11-03 — Ephemeral token handoff newline defect found

- Run [41509666199](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41509666199) completed the daily adjustment step and invoked the intraday diagnostic, but produced no minute-bar result. Artifact status: `BLOCKED_RUNTIME_ERROR`.
- Root cause found in code inspection: the private `GITHUB_ENV` writer used a double-escaped newline and appended literal backslash+n characters to the access token, corrupting the value passed to the next step.
- Fixed the environment writer and added/updated regression coverage to ensure it writes one actual token line and rejects actual line breaks. No token was logged or stored in the repo.


## 2026-11-03 — Preliminary intraday scale result and stronger same-session control

- Protected run [41510216099](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41510216099) passed offline tests, daily event adjustment checks and the token handoff. The minute-data script returned preliminary close-to-close ratios of 1.002562 for RELIANCE and 1.047470 for BAJAJFINSV, both classified near adjusted scale.
- The preliminary comparison crossed an overnight interval and therefore includes the market return. It is not strong enough for C1 acceptance by itself.
- Added a stronger same-session test: aggregate Dhan intraday OHLC on the cum date and ex-date and compare each field with Dhan daily adjusted OHLC for the exact same dates. This can distinguish pre-event 1.0-scale matching from the expected 2x/10x raw intraday scale without using an overnight return. E0125 records the methodology improvement.


## 2026-11-03 — Same-session intraday corporate-action scale comparison passed

- Protected Actions run [41510761625](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41510761625) passed all steps, including offline tests, daily adjustment checks, intraday diagnostic, report publication and both acceptance gates.
- RELIANCE 1:1 bonus (2024-10-28): same-session intraday/daily adjusted OHLC ratios for pre-date 2024-10-25 were open 0.994008, high 0.997211, low 1.000000, close 1.000226; ex-date ratios 1.000000, 1.000000, 1.000000, 1.000300. Result: `INTRADAY_MATCHES_DHAN_DAILY_ADJUSTED_SCALE`.
- BAJAJFINSV 5:1 split + 1:1 bonus (2022-09-13): pre-date ratios 0.996548, 0.997072, 1.000164, 1.006179; ex-date ratios 1.000000, 0.999756, 1.000000, 0.997899. Result: `INTRADAY_MATCHES_DHAN_DAILY_ADJUSTED_SCALE`.
- The same-session cross-endpoint test removes the overnight move in the earlier exploratory check. It indicates minute bars match Dhan's adjusted daily scale for these two events. It does not establish all-symbol/all-event coverage. No raw prices or intraday bars were published.
- E0125 closed for the two registered samples. E0126 closed (corrected report method description). Overall C1 remains PARTIAL because the remaining point-in-time event catalogue and identity review are open.


## 2026-11-03 — Intraday report-method wording corrected

- The same-session intraday-versus-daily scale comparison passed both sampled events on run [41510761625](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41510761625).
- A review found the Markdown explanation still described the earlier overnight pre-close-to-ex-open comparison even though the JSON and acceptance gate used same-session comparisons. Corrected the report generator and saved report so the documentation now matches the executed calculation.


## 2026-11-03 — C1 rights-compliant continuation

- Rechecked official NSE Terms of Use and Data Sharing & Usage Policy. The four-date PR archive probe is retained as technical feasibility only; it is not permission for systematic automated extraction or use in trading simulation. Disabled the PR archive-probe path, including manual dispatch.
- Dhan daily and same-session intraday scale checks passed for RELIANCE and BAJAJFINSV in protected run [41510761625](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41510761625). BAJAJFINSV's trading-ISIN date is adjudicated to 2022-09-13 inclusive; raw TejHQ value remains preserved and flagged stale.
- Added a new recipient-encrypted private queue workflow for the 37 complex member-event candidates. It reads the TejHQ personal-use-only source within Actions and uploads only ciphertext for one day; the private key is held outside GitHub and no cleartext event rows are logged or published.
- Next: decrypt only in the intended private runtime, verify issuer-first-party terms where permitted, and exclude cycles for unresolved event terms/identity. C1 remains PARTIAL; C2 panel accepted with limitations, C4/C5 gated.


## 2026-11-03 — First private issuer queue attempt failed before extraction

- Workflow [41513029040](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41513029040) passed two offline encryption tests and restored the encrypted TejHQ cache, but the queue script stopped before loading candidate rows because the repository root was missing from `sys.path` (E0128).
- No cleartext candidate data was generated, written, logged, or uploaded. Added the root-path bootstrap before project imports; retry required.


## 2026-11-03 — Recipient key rotation for private issuer-event queue

- The successful private queue workflow [41513398732](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41513398732) emitted a recipient-encrypted ciphertext artifact, but the matching private key was not available in the active research runtime. The candidate queue therefore could not be reviewed event by event.
- Generated an RSA-3072 recipient keypair outside GitHub. Only the public key and fingerprint are committed; the private key remains in the current local runtime with restrictive file permissions. No private-key bytes are logged, committed or uploaded.
- Next step: run the encrypted queue builder again against the current public key, decrypt the one-day artifact locally, and proceed with issuer-first-party evidence collection. No TejHQ raw rows will be persisted to the repository or Pages.


## 2026-11-03 — Bounded issuer-source review of 37 complex event candidates

- Protected workflow [41514027613](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41514027613) successfully built a recipient-encrypted queue; 37 candidates joined unambiguously to point-in-time member keys. The private event-level decision ledger and source-to-row map are retained outside GitHub because the source queue is personal-use-only.
- Issuer and official exchange source review established 17 equity bonus-share actions, 9 splits, 6 rights offers and 3 merger/demerger schemes. Two of the 19 bonus-labelled candidates are non-equity NCD distributions, not equity bonuses. Terms/record-date evidence was found for all 37 candidates: 35 with issuer-first-party source evidence and 2 with official exchange-primary evidence where an issuer notice was not located in this bounded search.
- Important corrections include the debenture classification, a later issuer corrigendum revising a bonus record date to 4 June 2026, POWERGRID's 1:3 bonus with 12-Sep-2023 record date, and source-adjudicated BAJAJFINSV trading identity from 13-Sep-2022.
- No manual corporate-action factor or rights TERP was applied. No merger/demerger generic price factor was applied. Full historical security identity/price continuity remains open; Dhan same-session adjusted-scale evidence still covers only two samples.
- The remaining 674 catalogue candidates comprise 625 dividends, 20 buybacks and 29 AGM/other events. Their review remains a separate bounded block. The 625 dividend candidates are not mechanically added back to the NIFTY price-index target.
- Public aggregate report: [C1_ISSUER_EVENT_REVIEW_AGGREGATE.md](research/constituent_weekly/C1_ISSUER_EVENT_REVIEW_AGGREGATE.md). Sanitised machine summary: [C1_ISSUER_EVENT_REVIEW_AGGREGATE.json](research/constituent_weekly/C1_ISSUER_EVENT_REVIEW_AGGREGATE.json).
- **Disposition:** 37-candidate source review complete; C1 overall **PARTIAL / NOT PASSED**; C2 panel remains PASS WITH C1 LIMITATIONS; C3 exploratory complete with no confirmed stock-model edge; confirmatory C4/C5 remain gated.


## 2026-11-03 — Next bounded queue for 49 buyback and AGM/other candidates

- The 37-candidate bonus/split/rights/merger-demerger queue is complete and published as aggregate results.
- Added a separate protected encrypted queue for the remaining 20 buybacks and 29 AGM/other candidates. It reuses the pinned TejHQ encrypted cache and existing recipient public key; it emits only aggregate counts and a one-day ciphertext artifact.
- Dividend events (625) are not bundled into this queue because the locked protocol preserves NIFTY price-index semantics and does not mechanically reinvest cash dividends. They remain subject to forecast-time and affected-window review where relevant.


## 2026-11-03 — Secondary 49-event review and corrected 711-candidate catalogue

- Protected queue [41517328794](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41517328794) completed SUCCESS; 49 unique candidates joined to 49 point-in-time member keys with zero ambiguity.
- Source review corrected the feed classes: 21 buybacks (one originally under “other”), 3 dividends (also under “other”) and 25 AGM/governance. Primary issuer/SEBI/exchange offer/record-date evidence was found for all 21 buybacks; issuer/exchange amount/date evidence for the 3 dividend corrections.
- HCLTech ₹2/record 2018-08-06; TCS ₹4/record 2018-10-24; Nestlé India ₹135/record 2020-11-02; NTPC buyback ₹115/record 2020-11-13.
- All AGM records remain excluded from predictive features until actual issuer/exchange notice timestamps are verified before the 10:00 IST forecast cutoff. No price factor is applied to buybacks, dividends or AGMs.
- Corrected final 711 classification: 17 equity bonuses, 2 NCD distributions, 9 splits, 6 rights, 3 merger/demerger, 21 buybacks, 628 dividends and 25 AGM/governance. Full identity, adjusted-price continuity and affected-cycle exclusions remain open.
- Reports: [C1_BUYBACK_AGM_REVIEW_AGGREGATE.md](research/constituent_weekly/C1_BUYBACK_AGM_REVIEW_AGGREGATE.md), [complex event aggregate](research/constituent_weekly/C1_ISSUER_EVENT_REVIEW_AGGREGATE.md).


## 2026-11-03 — Workflow template correction for complex-event cycle sensitivity

- The initial cycle-exclusion workflow run [41523805932](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41523805932) started, but review found GitHub Actions expression markers had been over-escaped in the committed YAML. Token and artifact/cache inputs would not resolve.
- Corrected the workflow expressions in one batched commit. The first run is not a research result; the corrected run must validate artifact download, checksum verification, decryption, event joins and 47/94 sensitivity.

## 2026-11-03 — Weekly expiry calendar correction discovered

- The expiry parser filtered only regular weekly expiries and dropped contract-present rows explicitly marked as holiday-shifted weekly expiries.
- Reconstruction from the official daily-session calendar changes the registered sample from 258 to 260 cycles. It restores the 2021-11-08 to 2021-11-11 cycle and splits the October 2025 window at the actual 2025-10-20 expiry.
- The prior 258-cycle C2 panel, 37-event cycle-exclusion sensitivity and dependent C3 metrics are quarantined as historical artifacts, not current acceptance evidence.
- C1 and C2 parsers now accept the two explicit verified status values only when the contract-expiry flag is true. Regression tests cover both shifted dates and the cycle split.
- C3's holdout boundary is calculated as floor(80% of eligible cycles): 206 for 258 and 208 for 260.
- Next: cached C1 coverage refresh, C2 panel-only rebuild, automatic C3 rerun, then recalculate event-cycle sensitivity against the new C2 manifest. No strategy or cost claim is authorised by this correction.


## 2026-11-02 — C1 continuous stock/index target coverage

- **Auditor status:** PARTIAL_OR_BLOCKED_TARGET_COVERAGE; data-coverage gate: FAIL; identity/action gate: SYMBOL_MAPPING_RESOLVED_KNOWN_AND_UNIVERSAL_CORPORATE_ACTION_REVIEW_PENDING.
- **Window:** 2021-11-08 to 2026-10-27.
- **Coverage:** 26/260 valid NIFTY targets; 13 cycles meet the stock and index data rules; 0 confirmatory cycles after the 104-cycle warm-up.
- **API/cache:** 1083 requests this run; reused 0 index and 0 stock-symbol chunks.
- **Interpretation:** data coverage is assessed independently of security identity/corporate-action treatment. This audit does not train or evaluate a model and does not unlock C2.
- **Artifacts:** C1_CONTINUOUS_COVERAGE.json and C1_CONTINUOUS_COVERAGE_REPORT.md.
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


## 2026-11-01 — AMC recent-month schema gate passed

- Corrected probe [run 41275178244](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41275178244) passed all seven offline tests and both required source-schema checks.
- September 2026 AMC workbook: HTTP 200, XLSX container, 108 sheets, Nifty BeES target found, ISIN/quantity/weight fields detected, 50 ISIN-bearing rows.
- February 2026 AMC workbook: HTTP 200, XLSX container, 111 sheets, target found, same fields detected, 50 ISIN-bearing rows.
- The older April 2019 archive record is shown on the AMC page but the guessed direct URL returned 404; this is recorded as link-discovery failure and not as missing historical data.
- Exact hashes, sizes, HTTP status and file signatures are in the sanitised probe report. No raw holdings, names, quantities, values or workbooks were committed.
- The automated report push raced with an independent C1 update. The report is now committed by the research controller and the workflow publisher uses bounded non-forced retries.
- Overall C1 remains PARTIAL / NOT ACCEPTED FOR MODELLING. Rights, publication dates, complete historical series, identity/actions, 98%/47-stock coverage and basket reconciliation remain open.


## 2026-11-01 — AMC metadata workflow and report publisher verified

- Follow-up workflow [41275487989](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41275487989) completed SUCCESS. The 7-test parser suite, three-month source probe, job-summary publication and sanitised report publication all completed.
- The bounded fetch/rebase/push loop resolved the prior concurrent-ref race without force-pushing. The current committed probe report is generated by the successful run.
- The two recent AMC workbook schema checks remain PASS_SCHEMA (Sep-2026 and Feb-2026, 50 ISIN-bearing holdings rows each); the guessed Apr-2019 direct URL remains 404 pending exact historical path discovery.
- C1 remains PARTIAL / NOT ACCEPTED FOR MODELLING because source-use rights, actual availability timestamps, full historical coverage, security/action alignment, 98%/47-stock coverage and basket reconciliation remain open.


## 2026-11-01 — Historical Nippon archive and amcs.fund discovery route

- Rechecked the official Nippon AMC page with its older archive sections. The visible month-end portfolio index extends back to September 2013, with an explicit April 2019 record. The previously tested Apr-2019 direct URL was only a modern filename guess and returned 404; it is not evidence of missing historical holdings.
- Read amcs.fund's published methodology: it claims to fetch fund houses' own Excel/ZIP disclosures, extract ISIN/quantity/market-value/%NAV fields, use the printed disclosure month, and link each monthly record to the original AMC file plus Internet Archive copy. The API index advertises /amcs, /manifest, /scheme/{id} and /month/{id} routes.
- Attempted to open the advertised API index successfully; it lists those route names. The /amcs JSON endpoint itself was inaccessible through the present browser fetch path, so no API payload, scheme id or historical URL was obtained. This is a source-discovery lead only, not an admitted dataset.
- The public-use/reuse licence of amcs.fund data is not verified. No holdings values or raw source workbook have been copied.
- C1 remains PARTIAL / NOT ACCEPTED FOR MODELLING. Rights, exact attachment links, availability timestamps, historical ISIN/action continuity, weight coverage and weighted basket-index reconciliation remain gates.


## 2026-11-01 — Official archive lower bound corrected; API metadata-only probe committed

- **Phase:** C1 — point-in-time universe and data-source feasibility.
- **Step/status:** Historical archive source discovery advanced; API metadata probe implementation committed; runtime API result pending.
- **Finding:** The rendered official Nippon India archive shows monthly portfolio index entries back to 30 September 2012, not just September 2013, and explicitly lists April 2019. The previously guessed April 2019 modern filename returned 404; this remains a wrong/unresolved link, not a missing-data finding.
- **Independent method/source lead:** amcs.fund's published methodology says it links each monthly row to the AMC's original source file and an Internet Archive copy, and takes the period from the date printed in the disclosure. Its API index lists /amcs and /manifest among the metadata routes. No API records or holdings were imported.
- **Implementation:** Added a metadata-only probe that requests the API index, AMC listing/detail and manifest only; it does not call a scheme holdings endpoint or download portfolio files. It filters output to whitelisted metadata fields/hosts and HEAD-checks only whitelisted original-AMC/Internet Archive links. Added offline sanitisation tests and a push/manual Actions workflow with bounded report publication retries.
- **Rights rule:** amcs.fund reuse rights for commercial/trading-research extraction, caching and redistribution remain unverified. Treat it only as a source locator pending licence review. Do not import holdings or train.
- **Plan:** Locked BUP-01 plan v1.2 unchanged.
- **Next gate:** Inspect the automated API metadata report; if it resolves a specific original Nippon disclosure link, test link availability via HEAD only, record disclosure date separately from first-publication date, and review source rights before any file body is downloaded.


## 2026-11-01 — AMC metadata probe regression fixture corrected

- **Phase:** C1 source-discovery automation.
- **Run:** [41276748532](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41276748532) failed in the offline tests: 3 passed, 1 failed; the network probe was skipped.
- **Diagnosis:** A single test fixture mixed AMC-list and scheme-detail records. The recursive matcher correctly included both Nippon-related objects, but the test expected only the AMC record.
- **Correction:** Separated the test fixture into the two distinct endpoint shapes. The metadata extraction code was not changed.
- **Next action:** Push-triggered workflow rerun; inspect API metadata and only original-source HEAD results. Rights remain unverified and C1 remains blocked.

 
## 2026-11-01 — amcs.fund metadata workflow passed; no source URLs surfaced

- **Phase:** C1 source discovery.
- **Run:** [41277022940](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41277022940), **SUCCESS**; 4/4 metadata sanitisation tests passed.
- **Observed:** API index, /amcs, Nippon AMC detail and /manifest all returned HTTP 200 / valid JSON. AMC record resolved to Nippon India; detail returned current Nifty BeES scheme metadata.
- **Limitation:** The /manifest response did not yield any whitelisted original-AMC or Internet Archive source URL for historical Nifty BeES files. No HEAD checks could be made. The exact April 2019 attachment remains unresolved.
- **Data/rights:** No scheme holdings route or source-file body was downloaded; no portfolio values were admitted. amcs.fund data-reuse rights for trading research remain unverified.
- **Correction:** E0062 closed after the successful follow-up run; it was an incorrectly mixed offline test fixture, not an API/data error.
- **Plan:** BUP-01 v1.2 remains locked. C1 remains PARTIAL / NOT ACCEPTED FOR MODELLING.


## 2026-11-01 — Alternative historical membership/weight routes assessed

- **Phase:** C1 — source feasibility and rights audit.
- **User request:** “Can you find alternatives?”
- **Primary alternative:** NSE Indices official historical reports page has an Archives of Daily/Monthly Reports selector; official monthly report page lists market-capitalisation and weightage ZIP reports. NSE All Reports lists a NIFTY 50/NIFTY Next 50 market-cap/weightage/beta report and a broader index market-cap/weightage report. The archive looks like the strongest exact-weight source, but month-by-month coverage, publication times and permitted research use remain unverified.
- **Rights check:** current NSE Indices Terms of Use prohibit systematic/automated collection absent express written consent and describe site use as personal/non-commercial. No scraper/cache will be enabled without consent or a subscription licence.
- **Membership alternative:** inspected aditya-jha/nse-historical-membership. Derived data are CC BY 4.0 with attribution; NIFTY 50 membership intervals begin 2014-01-01, README states high confidence from 2018 onward and best-effort earlier, and coverage lists last NIFTY 50 event as 2025-09-30. Historical weight values are null. Accept only as a membership comparator after reconciliation and update.
- **XBRL route:** NSE/BSE quarterly SHP filings offer independent ownership inputs. NSE IWF methodology has 22 exclusion classes; current promoter/FII/DII aggregates do not calculate IWF. A detailed classification and timestamp-aware parser must be built and tested against an official index-weight snapshot.
- **ETF proxy route:** HDFC, UTI and Nippon index-fund/ETF monthly portfolios can be compared by ISIN but remain proxies, subject to source-use rights and cash/derivative residuals. Do not substitute ETF weights for official index weights.
- **Rejected for current use:** AMP4010 Hugging Face historical NIFTY weight series is CC BY-NC-SA 4.0 and requires a separate commercial licence; it also uses monthly/event snapshots and between-snapshot assumptions.
- **Paid fallback:** NSE Indices data subscription describes historical constituent identifiers, market capitalisation, weights and prices and names quantitative research as a data-use category. Check only after free routes and rights/permission possibilities.
- **Implementation:** full assessment saved at research/constituent_weekly/C1_WEIGHT_ALTERNATIVES_ASSESSMENT.md. No model training or raw data ingestion occurred. Plan v1.2 remains unchanged.
- **Decision:** C1 remains PARTIAL / NOT ACCEPTED FOR MODELLING. The preferred next path is permissioned NSE weight reports + CC BY 4.0 PIT membership comparator + Dhan price-drift reconstruction with event resets and official basket reconciliation.

 
## 2026-11-01 — CC BY 4.0 membership alternative reconciled over 103 months

- **Phase:** C1 point-in-time universe source validation.
- **Source:** `aditya-jha/nse-historical-membership`, data licence CC BY 4.0. Copied the NIFTY 50-only subset with attribution and added the 2026-09-30 BSE/WIPRO transition supported by an independent reprint plus fund-portfolio cross-check.
- **Comparison:** Matched the alternative effective-dated table to the project’s C1 membership ledger for all 103 calendar month-ends from 2018-04 to 2026-10. The exact member sets match after restoring upstream canonical TMPV to pre-rename TATAMOTORS before 2025-10-24 and excluding the temporary DUMMYTATAM zero-price placeholder from the tradable-stock set.
- **Counts:** 50 members at 102 month-ends; 51 on 2025-10-31 only when the temporary dummy is included in the index ledger. This is not a mismatch.
- **CI:** Corrected membership regression run [41289992040](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41289992040) SUCCESS. C1 authorised-source audit [41289991986](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41289991986) SUCCESS. Dhan preflight run [41289992028](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41289992028) SUCCESS for offline/cache steps; live Dhan steps were skipped because it was a pull-request event.
- **Limitation:** All weights are blank in the imported CC BY source. Membership is now independently cross-checked, but historical numerical weights/IWF are not resolved.
- **Error correction:** E0063 logs that the test originally expected 79 rather than 103 months; the corrected test and suite passed.



## 2026-11-01 — mfdata.in historical-month endpoint probe (bounded attempt)

- **Phase / step:** BUP-01 C1 — independent mutual-fund source discovery and archive-history coverage.
- **Documentation reviewed:** [mfdata.in API docs](https://mfdata.in/docs) describe the no-auth /api/v1/search, /api/v1/families, and /api/v1/families/{family_id}/holdings/history routes. The history route returns available YYYY-MM labels; actual month-specific portfolio contents require a separate /holdings?month=YYYY-MM request, which was deliberately not called.
- **Implementation:** Updated scripts/constituent_weekly/probe_amcs_fund_metadata.py with documented search + family-catalogue + legacy-schemes bounded fallbacks; limited family-ID detail resolution and history probes; recursive month parsing; month-gap/continuity metrics. No per-security holdings values or source workbooks are retained.
- **Tests:** [Actions run 41297143071](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41297143071) passed 13/13 metadata parser/sanitisation tests and published the report.
- **Live result:** /search, /families and /schemes discovery requests all returned HTTP 522. The run never discovered a family ID, so the monthly history endpoint was not reached. No historical coverage result can be reported; the route remains **INCONCLUSIVE**, not zero coverage.
- **Rights/provenance:** Documentation says the API is free/no-auth and is rate limited; this does not establish a licence to extract, cache, redistribute or use aggregated upstream holdings in commercial trading research. No clear underlying financial-data licence, source-per-snapshot citation, or first-publication timestamp was established.
- **Phase outcome:** This route is retained as a documented fallback candidate, but it is not an admitted data source. No holdings downloaded, no model training, no forecast. BUP-01 plan v1.2 unchanged; C1 remains NOT PASSED / RIGHTS-BLOCKED.
- **Next bounded action:** No immediate network retry loop. Continue to an independently accessible AMC mother-source route only where access and data-use terms allow; reopen mfdata only when provider access is available.




## 2026-11-01 — Original AMC disclosure locator assessed as mfdata fallback

- **Source:** [amcs.fund monthly archive](https://amcs.fund/month) and [methodology](https://amcs.fund/methodology).
- **Source claim:** the site states it builds from each fund house's own monthly portfolio spreadsheet/ZIP, reads the month from the date printed in the disclosure, links source files and Internet Archive copies, and flags incomplete months where accessible files cover less than 70% of average fund-house AUM. These are provider methodology claims, not an independent reproduction yet.
- **Existing technical evidence:** the C1 metadata workflow returned valid JSON (HTTP 200) from the API index, AMC/scheme metadata and sampled month endpoints including 2019-04. The sanitizer kept metadata/schema only; it did not store security-level holdings or raw source files. The scheme snapshots also showed only a 13-month hold_hist cache, which is not accepted as complete historical coverage.
- **Research use:** retain amcs.fund as a route to discover the original AMC disclosure files and archived copies. For each scheme-month, the actual printed disclosure date, original URL, archive URL, ISIN identity, 50-stock presence, portfolio weight sum and source reuse rights must be checked.
- **Limitation:** ETF/index-fund weights are not NIFTY free-float IWF. They may include cash/derivatives or tracking residuals and may differ by scheme. Use only as a proxy/cross-check after a direct comparison with independently published index weights.
- **Rights:** no blanket licence to download/cache/re-publish the underlying AMC files was established. Public page availability does not override AMC source terms.
- **Disposition:** useful provenance path; not yet an admitted model input. C1 remains NOT PASSED / RIGHTS-BLOCKED; no C2 or trading backtest triggered.




## 2026-11-01 — v1.3 user-directed weight-free bottom-up index aggregation

- **User direction:** “No comparison needed. Proceed.” Applied narrowly to mean no ETF-holdings-versus-official-NIFTY-weight comparison; no ETF weight series or historical free-float IWF reconstruction is required for this active method.
- **Plan amendment:** registered BUP-01 v1.3. Stock targets remain the 10:00-to-15:15-proxy constituent price outcomes. For each expiry cycle, generate strictly out-of-fold stock probabilities/expected returns, summarize them with unweighted predicted breadth, probability/return means and medians, dispersion, sector breadth, concentration and valid-member coverage, then fit a chronological NIFTY-direction meta-model to the observed NIFTY index label.
- **Mathematical safeguard:** the actual NIFTY target is still the observed index series. An equal-weighted constituent mean is a diagnostic only, not the actual index return. The meta-model must not use in-sample stock predictions or predictions trained on the same expiry cycle.
- **C1 gates preserved/revised:** maintain point-in-time membership, stable ISIN/security IDs, corporate-action continuity, verified expiry/session calendar and continuous stock plus NIFTY index candles. Accepted cycles require at least 47 and at least 94% of eligible tradable constituents with valid forecasts; at least 98% of scheduled eligible cycles must have valid NIFTY targets; first confirmatory forecast requires 104 prior eligible cycles.
- **Rights control:** Nippon AMC bulk workbook automation is paused; no holdings values were admitted. Existing weights/ETF files and calibration reports remain historical audit material only and are not used or refreshed. The v1.3 C1 gate no longer requires weights or basket-to-index weight reconciliation.
- **Automation:** Dhan C1 workflow no longer refreshes the historical weight cache; AMC archive workflow now runs offline parser tests only. The v1.3 plan validator, member-count/OOF tests and manual/push offline workflow are updated.
- **Validation:** the preceding mother-source metadata workflow [41298336318](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41298336318) completed SUCCESS, including offline tests and metadata probe. The v1.3 plan/offline workflow is running on the amended branch; record its final result when complete.
- **Current phase decision:** C0 PASS; C1 PARTIAL / CONTINUOUS-COVERAGE GATE IN PROGRESS. No C2 panel, stock model, forecast, strategy or final manuscript exists. Locked plan v1.3; no weight comparison is to be performed.



## 2026-11-01 — C1 effective-dated security identity review

- **Finding:** the membership ledger uses canonical LTM for the 2023-07-13 to 2024-09-30 LTIMindtree interval. Exchange records show actual ticker LTIM throughout that interval, with LTIM→LTM effective 2026-02-27. The C2 identity resolver now distinguishes point-in-time ticker from current/canonical security key.
- **Additional aliases:** ZOMATO→ETERNAL from 2025-04-09; TATAGLOBAL→TATACONSUM from 2020-02-27; TATAMOTORS→TMPV from 2025-10-24. These are recorded as symbol history; scheme and demerger price discontinuities are not assumed adjusted.
- **Security safeguards:** HDFC Ltd (legacy Dhan ID 1330) remains a distinct security from HDFCBANK. Tata Motors demerger ex-date 2025-10-14 is retained as an event where raw return continuity is invalid. The placeholder DUMMYTATAM remains non-tradable.
- **Artifacts:** security_alias_history.csv, security_corporate_action_events.csv, security_identity.py, tests/test_c1_security_alias_history.py.
- **Limitation:** this is a major identity/event ledger, not a complete dividend/split/bonus/rights adjustment series. C1 stays partial; no model or stock return label is built from these mappings yet.
- **Workflow:** alias/identity regression run [41302695594](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41302695594) pending; continuous Dhan run [41301447865](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41301447865) was still processing at this log point.


## 2026-11-01 — Live C1 Dhan intraday target coverage completed; publication conflict recorded

- **Run:** [41301447865](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41301447865).
- **Result:** 258/258 weekly expiry cycles had valid observed NIFTY anchor/expiry-proxy target pairs; 258/258 met the stock input rule (at least 47 and at least 94%); 154 confirmatory cycles remain after 104 prior accepted cycles; zero unresolved active symbols; 1,083 Dhan requests across 21 windows.
- **Window:** first anchor 2021-11-12 through final expiry 2026-10-27. The 2024-01-31 to 2024-04-29 index window was PARTIAL_TARGET_DATES, despite the final 258/258 cycle-level target count. Exact partial-date detail is not recoverable.
- **Publication:** runner generated sanitized report; git pull --rebase conflicted on STATUS.md and RESEARCH_LOG.md. Final target-coverage gate printed PASS. Detailed per-cycle QA was not retained as an Actions artifact.
- **Next:** artifact upload before branch update, clean-reset/re-generate status publication, separate daily OHLCV audit and exhaustive action-aware return review before C2.


## 2026-11-01 — C1 Dhan daily OHLCV coverage

- **Auditor status:** COMPLETED_WITH_GAPS.
- **Window:** 2018-04-01 to 2026-10-30.
- **Coverage:** 68/69 parseable symbols; 94799/95900 valid OHLC member sessions; weighted OHLCV coverage 98.85%.
- **API/cache:** 69 requests; 0 symbols reused from the sanitized QA cache.
- **Interpretation:** daily OHLCV coverage is reported independently from intraday target coverage, historical identity and action-adjusted return integrity. No model is trained and C2 remains gated.
- **Artifacts:** C1_DAILY_COVERAGE.json and C1_DAILY_COVERAGE_REPORT.md.


## 2026-11-01 — C1 continuous stock/index target coverage

- **Auditor status:** PARTIAL_OR_BLOCKED_TARGET_COVERAGE; data-coverage gate: FAIL; identity/action gate: SYMBOL_MAPPING_RESOLVED_KNOWN_AND_UNIVERSAL_CORPORATE_ACTION_REVIEW_PENDING.
- **Window:** 2021-11-12 to 2026-10-27.
- **Coverage:** 77/258 valid NIFTY targets; 64 cycles meet the stock and index data rules; 0 confirmatory cycles after the 104-cycle warm-up.
- **API/cache:** 1083 requests this run; reused 0 index and 0 stock-symbol chunks.
- **Interpretation:** data coverage is assessed independently of security identity/corporate-action treatment. This audit does not train or evaluate a model and does not unlock C2.
- **Artifacts:** C1_CONTINUOUS_COVERAGE.json and C1_CONTINUOUS_COVERAGE_REPORT.md.


## 2026-11-01 — Full C1 intraday artifact retrieved; target coverage reconciliation

- **Authoritative run:** [41309632317](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41309632317), artifact 13086220727. The complete sanitized JSON with all per-cycle and index-chunk date QA was downloaded and inspected.
- **Result:** intraday target gate PASS; 258/258 weekly expiry cycles valid; 258/258 stock-input cycles meet 47 members and at least 94% coverage; 154 confirmatory cycles after 104 prior accepted cycles; 98% minimum member coverage; median 50 valid members; zero unresolved active symbols; 1,083 requests over 21 windows.
- **Partial-window explanation:** the only partial date is 2024-04-26 at 15:14, while the 10:00 anchor passes. This was not an expiry day. The cycle anchored 2024-04-26 expires 2024-05-02; its actual expiry proxy, stock coverage and index target all pass.
- **Reconciliation:** earlier 77/258 and 64 accepted-cycle values are from an earlier incomplete run and remain historical; they are superseded as current gate evidence by the later full artifact.
- **C1 remains partial overall:** the first daily run found 98.85% OHLCV member-session coverage but HDFC legacy history and one TATAMOTORS date missing. The corrected TejHQ personal-use fallback is awaiting its live run. Full action-aware return validation remains open.


## 2026-11-01 — C1 daily fallback safeguards and regression validation

- Added an explicit TEJHQ_PERSONAL_USE_ONLY=1 runtime guard before any TejHQ fallback download. Without the flag, fallback is skipped; without HF_TOKEN, it is skipped.
- Changed encrypted cache publication to a run-unique key plus a dataset/revision restore prefix. This avoids immutable GitHub cache-key collisions preventing the addition of year partitions on later runs.
- The common C1 offline regression workflow passed **88 tests** in Actions run [41315241386](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41315241386). This includes AES-GCM cache, personal-use guard, HDFC boundary, TejHQ EQ/ISIN/row QA and Tata cross-source check tests.
- Live TejHQ fallback has not yet run; no fallback sessions are counted in coverage. Dhan daily coverage remains at the last measured first-pass result until the next serialized live daily job completes.
- Overall C1 remains PARTIAL; daily feature gaps and full action-aware return integrity remain open.


## 2026-11-01T14:34:44.970940+00:00 — C1 Dhan daily OHLCV coverage

- **Auditor status:** COMPLETED_WITH_GAPS.
- **Window:** 2018-04-01 to 2026-10-30.
- **Calendar:** 1918 official NIFTY sessions plus 210 validated Dhan index sessions; combined sessions 2128.
- **Coverage:** 69/70 parseable Dhan symbols; 106385/106392 valid OHLC member sessions; weighted OHLCV coverage 99.9934%.
- **Fallback:** COMPLETED_WITH_GAPS; 1295 validated member sessions added from the pinned encrypted-cache source.
- **Residual gaps:** HDFC: 6 (2018-11-07, 2019-10-27, 2020-02-01, 2020-11-14, 2021-11-04, 2022-10-24; sample complete); TATAMOTORS: 1 (2025-10-21; sample complete).
- **API/cache:** 2 requests; 70 symbols reused from the sanitized QA cache.
- **Interpretation:** daily OHLCV coverage is reported independently from intraday target coverage, historical identity and action-adjusted return integrity. No model is trained and C2 remains gated.
- **Artifacts:** C1_DAILY_COVERAGE.json and C1_DAILY_COVERAGE_REPORT.md.


## 2026-11-01T14:42:05.550037+00:00 — C1 Dhan daily OHLCV coverage

- **Auditor status:** COMPLETED_WITH_GAPS.
- **Window:** 2018-04-01 to 2026-10-30.
- **Calendar:** 1918 official NIFTY sessions plus 210 validated Dhan index sessions; combined sessions 2128.
- **Coverage:** 69/70 parseable Dhan symbols; 106385/106392 valid OHLC member sessions; weighted OHLCV coverage 99.9934%.
- **Fallback:** COMPLETED_WITH_GAPS; 1295 validated member sessions added from the pinned encrypted-cache source.
- **Residual gaps:** HDFC: 6 (2018-11-07, 2019-10-27, 2020-02-01, 2020-11-14, 2021-11-04, 2022-10-24; sample complete); TATAMOTORS: 1 (2025-10-21; sample complete).
- **API/cache:** 2 requests; 70 symbols reused from the sanitized QA cache.
- **Interpretation:** daily OHLCV coverage is reported independently from intraday target coverage, historical identity and action-adjusted return integrity. No model is trained and C2 remains gated.
- **Artifacts:** C1_DAILY_COVERAGE.json and C1_DAILY_COVERAGE_REPORT.md.


## 2026-11-01T14:42:05.550037+00:00 — C1 encrypted cache path correction

- **Code correction:** The encrypted TejHQ cache path now expands `~` before resolving to an absolute path; regression coverage added for tilde and explicit paths.
- **Actions:** Offline suite [41317402493](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41317402493) passed; live daily workflow [41317402483](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41317402483) completed successfully.
- **Cache:** First run after the correction had no valid prior cache and therefore downloaded seven pinned yearly partitions. The encrypted cache save step then stored 87,911,829 bytes under the new shared key. The next compatible workflow must verify cache hits; reuse is not yet claimed.
- **Coverage:** No change to the last audited 106,385/106,392 (99.9934%) member-session coverage or seven residual dates. C1 remains PARTIAL; action-adjusted return audit remains open; no model trained.


## 2026-11-01 — C1 corporate-action candidate catalogue

- Live workflow [41318287855](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41318287855) completed successfully, including offline action/identity tests, pinned-source download, encrypted-cache save and sanitized artifact publication.
- Candidate catalogue: 18,393 NSE rows, 18,361 deduplicated events, 32 duplicates, 711 point-in-time constituent matches. Matched events: dividends 625, bonus 19, splits 9, rights 6, buybacks 20, merger/demerger 3, other 29.
- No factor was calculated or applied. Official NSE derivatives adjustment methodology is documented separately and explicitly not treated as a blanket cash-equity adjustment method.
- Cache directory mismatch was identified in both workflows and aligned to the absolute runner temporary directory. New workflow tests guard this path; live cache-hit verification remains pending.
- Next C1 task: verify each matched member event against official NSE/BSE corporate-action records and issuer filings; build an event-specific adjustment/exclusion ledger with source links, formula inputs and reproducible checks. Only then re-audit daily/expiry return continuity.
- C1 remains PARTIAL/NOT PASSED; no model trained and no C2 entry.


## 2026-11-01T15:01:28.039610+00:00 — C1 Dhan daily OHLCV coverage

- **Auditor status:** COMPLETED_WITH_GAPS.
- **Window:** 2018-04-01 to 2026-10-30.
- **Calendar:** 1918 official NIFTY sessions plus 210 validated Dhan index sessions; combined sessions 2128.
- **Coverage:** 69/70 parseable Dhan symbols; 106385/106392 valid OHLC member sessions; weighted OHLCV coverage 99.9934%.
- **Fallback:** COMPLETED_WITH_GAPS; 1295 validated member sessions added from the pinned encrypted-cache source.
- **Residual gaps:** HDFC: 6 (2018-11-07, 2019-10-27, 2020-02-01, 2020-11-14, 2021-11-04, 2022-10-24; sample complete); TATAMOTORS: 1 (2025-10-21; sample complete).
- **API/cache:** 2 requests; 70 symbols reused from the sanitized QA cache.
- **Interpretation:** daily OHLCV coverage is reported independently from intraday target coverage, historical identity and action-adjusted return integrity. No model is trained and C2 remains gated.
- **Artifacts:** C1_DAILY_COVERAGE.json and C1_DAILY_COVERAGE_REPORT.md.


## 2026-11-01 — C1 shared-cache workflow regression validation

- The daily and corporate-action workflow YAML files now use the same explicit `${{ runner.temp }}/bup01-tejhq-encrypted` path for restore, Python runtime and save.
- Added static regression assertions for both workflows and a shared-helper test for the corporate-action cache path.
- Pull-request CI [41319075705](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41319075705) passed; Dhan preflight [41319075672](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41319075672) passed its offline checks; continuous coverage [41319075683](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41319075683) passed its offline validation. Live Dhan steps were correctly skipped on pull-request events.
- The live corporate-action run [41318287855](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41318287855) predates the absolute-path correction; it reported 0 action-partition cache hits. A post-correction live run is still required to prove cache reuse.


## 2026-11-01 — C1 corporate-action official-source and cache verification checkpoint

- Latest offline regression workflow [41319197109](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41319197109) passed 93 tests.
- Latest daily coverage workflow [41318960344](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41318960344) passed; 106,385/106,392 daily member sessions (99.9934%) and seven residual sessions remain unchanged.
- Latest corporate-action workflow [41318960367](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41318960367) passed; 18,393 raw candidates, 18,361 deduplicated, 711 PIT member matches. Zero action-cache hits were expected because the restored cache was populated by the daily workflow and did not contain the action parquet namespace. Nine action partitions were saved for subsequent reuse.
- Official NSE sources located: [Corporate Filings—Corporate Actions](https://www.nseindia.com/companies-listing/corporate-filings-actions), with symbol/company, purpose, ex-date, record-date and CSV controls; [NSE All Reports data description](https://www.nseindia.com/static/products-services/equity-market-data-reports-download), which describes the daily symbol/series corporate-action report; [NSE derivative adjustment methodology](https://www.nseindia.com/static/products-services/equity-derivatives-corporate-actions-adjustments). The latter applies to derivative contract adjustment and is not adopted as a blanket equity-price adjustment formula.
- Added a test that verifies encrypted action partition cache round-trip, with the first call downloading and the second reusing cached ciphertext.
- Next: run the action workflow to verify cache hits; then build the official NSE event cross-check adapter, match by symbol/series/ISIN and ex-date, and manually classify the 711 constituent events. Do not use unverified events or factors in target construction.
- C1 remains PARTIAL/NOT PASSED; no C2 model training or trading strategy.


## 2026-11-01 — Corporate-action encrypted cache reuse verified

- The new encrypted partition round-trip test passed within the corporate-action workflow: 13/13 action and identity tests passed.
- Live corporate-action run [41319736877](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41319736877) restored the prior encrypted cache created by run 41318960367.
- All nine action-year partitions (2018–2026) were decrypted from cache: 9/9 cache hits; zero downloads. Cache reuse is now verified, not merely inferred from cache step success.
- Candidate event count and matching remained unchanged at 18,361 deduplicated events and 711 PIT member matches.
- Official NSE Market Activity Report documentation describes `Bcddmmyy.csv` within daily `nuprddmmyy.zip` as the daily corporate-action detail file. It is the next candidate primary-source cross-check route; archive URL/date coverage/schema still require live validation.
- No factor was calculated/applied; C1 corporate-action gate remains NOT PASSED; C2 remains locked.


## 2026-11-02 — C1 special-session calendar reconciliation

- Reviewed all seven residual daily OHLCV security/date gaps against NSE circulars and NSE Market Pulse. Six dates are Diwali Muhurat sessions; 2020-02-01 was a full 09:15–15:30 Union Budget trading session.
- The special-session dates remain genuine exchange trading dates and remain in the coverage denominator. This corrects the risk of misclassifying them as ordinary holidays or assuming all sessions use normal daytime hours.
- No prices were imputed and no gaps were waived. Targeted independent daily-bar reconciliation is still required for all seven security/date pairs.
- Audit: `research/constituent_weekly/C1_SPECIAL_SESSION_CALENDAR_RECONCILIATION.md`. Evidence includes NSE circulars NSE/CMTR/39216, NSE/CMTR/43290, NSE/CMTR/50050, NSE/FAOP/54024, NSE/CMTR/70319 and NSE Market Pulse November 2024.
- C1 remains PARTIAL / NOT PASSED; C2 remains locked.

## 2026-11-02 — C1 special-session source cross-check setup
- Added a dedicated, bounded audit for the seven residual security/session pairs. It checks a pinned daily NSE bhavcopy mirror and queries the exact NSE archive URLs; it does not download the full security universe.
- The mirror maintainer documents the OHLCV files as sourced from NSE archive endpoints. Its collector enumerates weekdays, so absent weekend sessions are not classified as exchange closures.
- Raw exchange bars are temporary-only. The committed output will contain row status, validity flags and hashes, not numerical prices or volumes. The mirror's MIT software licence is not treated as a market-data licence.
- First preflight run 41340624209 stopped before network data retrieval: five tests passed and one ISO-date parser test failed. Logged as E0086; corrected the parser and success-gated result publication.
- **Status:** targeted source audit implementation committed; live rerun pending. Existing C1 daily coverage remains 99.9934% with seven unresolved bars; C1 remains PARTIAL and C2/confirmatory modelling remain LOCKED.

## 2026-11-02 — Independent NSE bhavcopy mirror cross-check

- Audited seven exact security/date pairs using the pinned public NSE bhavcopy mirror.
- Valid EQ OHLCV rows: 4/7; mirror no-row: 3; duplicate rows: 0; unavailable source partitions: 0.
- The mirror collector enumerates weekdays only, so no-row on 2019-10-27, 2020-02-01 and 2020-11-14 is inconclusive for those special sessions.
- No raw prices/volumes were copied, no bar was fabricated, and the daily coverage denominator was unchanged. Corporate-action review remains open.
- Evidence: C1_INDEPENDENT_BHAVCOPY_AUDIT.md and C1_INDEPENDENT_BHAVCOPY_AUDIT.json.

## 2026-11-02 — Direct NSE special-session archive cross-check

- Direct NSE legacy cash-market archives validate all three remaining HDFC special-session EQ rows: 2019-10-27, 2020-02-01 and 2020-11-14.
- Combined with four valid independent-mirror rows, all seven residual security/date pairs have source-level OHLCV evidence.
- Cache enhancement now persists the three raw direct-NSE rows in the existing AES-GCM GitHub Actions cache using the HF_TOKEN-derived key. Cache SHA-256 is recorded in the direct audit JSON; no raw values are committed or uploaded.
- Base daily coverage JSON remains 106,385/106,392 until the encrypted supplemental rows are merged into the feature panel and the daily auditor is rerun. Corporate-action gate remains NOT PASSED; C2 remains locked.

## 2026-11-02 — Direct NSE encrypted-cache dependency correction

## 2026-11-02 — Direct NSE encrypted-cache dependency correction

- The direct NSE archive audit validates 3/3 special-session rows. A follow-up attempt to persist the raw rows into the encrypted cache exposed a missing runtime dependency (`pyotp`) from the shared cache-encryption module.
- Updated the workflow dependency installation to use the project's runtime requirements plus cache dependencies. No raw values were committed; encrypted cache persistence remains pending rerun.


## 2026-11-01T19:56:40.493291+00:00 — C1 Dhan daily OHLCV coverage

- **Auditor status:** COMPLETE.
- **Window:** 2018-04-01 to 2026-10-30.
- **Calendar:** 1918 official NIFTY sessions plus 210 validated Dhan index sessions; combined sessions 2128.
- **Coverage:** 69/70 parseable Dhan symbols; 106392/106392 valid OHLC member sessions; weighted OHLCV coverage 100.0000%.
- **Fallback:** COMPLETED; 1302 validated member sessions added from the pinned encrypted-cache source.
- **Residual gaps:** none.
- **API/cache:** 1 requests; 70 symbols reused from the sanitized QA cache.
- **Interpretation:** daily OHLCV coverage is reported independently from intraday target coverage, historical identity and action-adjusted return integrity. No model is trained and C2 remains gated.
- **Artifacts:** C1_DAILY_COVERAGE.json and C1_DAILY_COVERAGE_REPORT.md.

## 2026-11-02 — Direct NSE residual archive integration and daily coverage completion

- Direct NSE legacy/UDiFF bhavcopy archives independently validated all seven residual member/date pairs: six HDFC sessions and TATAMOTORS 2025-10-21. Each had one EQ row, valid OHLC/volume and matching ISIN.
- Raw residual rows were encrypted with the existing HF_TOKEN-derived AES-GCM cache key; the cache was restored with seven TejHQ year partitions and zero partition downloads.
- The daily coverage auditor now decrypts and merges the supplemental rows with the pinned TejHQ fallback. Successful run [41344197015](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41344197015) reports COMPLETE: 106,392/106,392 OHLCV member sessions, zero symbol gaps, 100% minimum per-symbol coverage, and no unresolved security IDs.
- Daily data coverage is complete. C1 overall remains gated by the separate corporate-action adjustment/issuer verification and other registered C1 checks; C2 remains locked.


## 2026-11-02 — Official NSE corporate-action source route identified

- Reviewed NSE's official Description of Market Activity Reports, the 1-Oct-2025 NSE/CMTR/70563 nomenclature circular, the live Corporate Actions CSV interface and NSE Clearing report documentation.
- Identified the daily PR/legacy archive corporate-action member as a plausible official mother-source cross-check for the 711 point-in-time member-event candidates; announcement and board-meeting files may provide additional event context.
- Recorded a bounded archive/schema probe and event-matching protocol in C1_OFFICIAL_CORPORATE_ACTION_SOURCE_FEASIBILITY.md.
- This was source discovery only: no raw source downloaded, no event adjudicated, no price factor applied. C1 remains PARTIAL / NOT PASSED; C2 remains gated.


## 2026-11-02 — Official NSE PR archive probe implementation

- Implemented a bounded fixed-date archive probe covering 2018-04-02, 2024-04-17, 2025-10-14 and 2026-04-17 to test both sides of NSE Circular NSE/CMTR/70563's 13-Oct-2025 naming transition.
- Added URL candidate handling for the legacy `nuprDDMMYY.zip` and current `PRDDMMYY.zip` names, ZIP validation, corporate-action member detection, CSV-header-only schema inspection, and announcement/board-meeting member checks.
- Raw archives are AES-GCM encrypted in the Actions cache; public report outputs contain hashes and schema metadata only.
- Added three offline regression tests and integrated the probe into the C1 corporate-action workflow's push-path and manual-dispatch paths.
- **Runtime execution:** Actions run [41422655123](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41422655123) started automatically on the matching branch push. Offline validation and cache restore passed; the catalogue step was still running at this log update. Static review caught and corrected a case-sensitive URL-path bug before trusting the source result; see E0109 in ERROR_LOG.md. The first run checked out the pre-fix revision and is not accepted as source evidence. The corrected script/test commits trigger a fresh run.
- C1 remains PARTIAL / NOT PASSED; C2 remains gated; no holdout tuning or strategy test was started.


## 2026-11-02 — Official NSE PR archive fixed-date probe PASS

- Corrected probe-only Actions run [41423606062](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41423606062) passed the offline tests, restored the encrypted archive cache, ran the probe, uploaded the sanitised artifact and published the reports to the C1 branch.
- **4/4** selected trading dates passed: 2018-04-02, 2024-04-16, 2025-10-14 and 2026-04-17. The previously selected 17-Apr-2024 was an official market holiday (NSE CMTR/59722) and was correctly replaced by 16-Apr-2024.
- Empirically confirmed website archive URL pattern: `https://nsearchives.nseindia.com/archives/equities/bhavcopy/pr/PRDDMMYY.zip`.
- Each archive contained a corporate-action CSV, announcement text and board-meeting text. The corporate-action CSV schema was consistent across all four dates (10 columns: SERIES, SYMBOL, SECURITY, RECORD_DT, BC_STRT_DT, BC_END_DT, EX_DT, ND_STRT_DT, ND_END_DT, PURPOSE).
- The final retest reused 4/4 encrypted archive cache entries. Raw bytes remain AES-GCM encrypted in Actions cache; public artifacts contain only metadata, hashes and headers.
- Corrected publisher now preserves generated reports across branch synchronisation; read-back verified the new 4/4 report and machine result.
- This is a bounded source/schema feasibility pass only—not proof of complete historical coverage or licence for bulk extraction. No candidate events were matched/adjudicated, no price factors calculated, and C1 remains PARTIAL / NOT PASSED; C2 remains gated.


## 2026-11-02 — NSE data-rights review and alternate source decision

- Reviewed NSE Terms of Use, Data Sharing & Usage Policy, Non-Display Usage Policy and NSE Research Initiative. NSE terms prohibit systematic/automated collection from the website without express written consent; non-display policy covers automated trading-decision algorithms and derived data. Research access is described as academic/non-commercial.
- Decision: do not expand the successful four-date technical probe into a 711-event automated NSE archive crawl without an applicable written permission/agreement.
- Evaluated the existing Dhan subscription as the next route. Dhan documents daily historical OHLCV from instrument inception and says daily history is adjusted for bonuses and splits; no claim is made that it covers dividends, rights, mergers or all contract adjustments.
- Added [C1_DATA_RIGHTS_AND_ALTERNATIVES.md](research/constituent_weekly/C1_DATA_RIGHTS_AND_ALTERNATIVES.md) and updated the feasibility report.
- Next: controlled Dhan adjusted-price diagnostic against the encrypted candidate event catalogue; targeted issuer-first-party verification only where access terms permit. C1 remains PARTIAL / NOT PASSED; C2 remains gated.


## 2026-11-02 — Dhan adjusted-price diagnostics (two event classes)

- Run [41426184727](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41426184727) successfully refreshed a Dhan token through TOTP (HTTP 200, one attempt; profile and data plan active). Two encrypted TejHQ year partitions were restored from cache; zero new partition downloads.
- Reliance 1:1 bonus (28-Oct-2024): 9/9 sessions; relative Dhan-adjusted/raw OHLC factor = 0.5 across open/high/low/close; post-event ratios = 1.0. PASS.
- Bajaj Finserv 5:1 split plus 1:1 bonus (13-Sep-2022): 11/11 sessions; relative Dhan-adjusted/raw OHLC factor = 0.1 across all four OHLC fields. Price-factor check PASS.
- **Identity warning:** NSE Circular CML53597 is internally inconsistent: its first sentence says w.e.f. 14-Sep-2022, while the next says trades from the 13-Sep ex-date. A MarketScreener reproduction of BSE Notice 20220908-17 also says 13-Sep, but the original BSE notice was not independently retrieved. TejHQ rows transition on 14-Sep. Logged as E0118; no date was silently selected or corrected. The factor pass is not an identity pass.
- Overall diagnostic PARTIAL_OR_BLOCKED. No raw prices/ISINs published; no factor applied to the full panel. Dividends, rights, mergers/demergers and buybacks remain outside this two-event test. C1 remains PARTIAL / NOT PASSED; C2 remains gated.
- Direct NSE bulk scraping remains prohibited absent written consent/agreement. See C1_DATA_RIGHTS_AND_ALTERNATIVES.md.

## GitHub Pages publication — 2026-11-02

- Sanitised C1 status, source-feasibility reports, data-rights notes and machine-readable NSE/Dhan diagnostics were copied to `docs/research/constituent_weekly/` on main.
- Pages deployment [41427840788](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41427840788) completed successfully.
- Live C1 research page: https://vcr-trading-research.github.io/NIFTY-Prediction/research/constituent_weekly/
- The page publishes only metadata, ratios, hashes, status and source links; no raw prices, event rows, ISIN values, tokens or credentials.


- The Pages deployment was refreshed after clarifying the conflicting BAJAJFINSV ISIN date wording in NSE CML53597; latest deployment run [41427840788](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41427840788) succeeded.


## 2026-11-03 — C1 event-level review protocol

- Reviewed the current C1 status, data-rights assessment, corporate-action catalogue, Dhan adjustment diagnostic, continuous coverage report, C4 gate and relevant project conversation history.
- Confirmed the C1 catalogue contains 711 point-in-time member-event candidates: 625 dividends, 20 buybacks, 19 bonuses, 9 splits, 6 rights, 3 merger/demerger and 29 AGM/other events.
- Added `research/constituent_weekly/C1_EVENT_REVIEW_PROTOCOL.md` on the C1 phase branch. The protocol preserves price-index dividend semantics, prevents double application of Dhan split/bonus adjustments, separates price-factor validation from security-identity validation, and defines event-window exclusion rules.
- No new event was verified and no adjustment factor was applied. C1 remains PARTIAL; C2/C4 confirmatory remain gated. This is a bounded process deliverable, not an empirical pass.


## 2026-11-03 — BAJAJFINSV identity-date discrepancy resolved

- Re-examined E0118 using the original NSE listing circular, the NSE Clearing contract-adjustment circular FAOP53644 and the BSE Notice 20220908-17 reproduction.
- NSE Clearing confirms ex-date 2022-09-13 and the combined 10x adjustment factor; both the explicit trade-effective clause in NSE CML53597 and the BSE notice reproduction state that the new ISIN applies to trades from 13-Sep.
- Decision: derived security mapping uses the new ISIN from 2022-09-13 inclusive. The old ISIN retained in the TejHQ row on that date is flagged as stale source metadata and is not rewritten.
- Added [C1_BAJAJFINSV_ISIN_ADJUDICATION.md](research/constituent_weekly/C1_BAJAJFINSV_ISIN_ADJUDICATION.md); E0118 closed with adjudication. This does not close the remaining C1 event review.


## 2026-11-03 — CI efficiency review

- The C1 protocol and adjudication files were committed in multiple sequential branch writes. The open C1 PR consequently launched multiple path-filtered validation workflows. This did not affect research data, but was unnecessary CI churn.
- Corrective rule: batch related branch-file changes into one Git tree/commit per logical step, then monitor the single resulting PR validation set. Recorded as E0120.


## 2026-11-03 — First protected intraday adjustment attempt

- Run [41507896770](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41507896770) successfully refreshed Dhan credentials and revalidated daily adjustment factors: RELIANCE 0.5 (9/9 sessions), BAJAJFINSV 0.1 (11/11 sessions). No intraday result was produced.
- Intraday script failed before the API request due to missing repository-root Python path (E0121). The workflow's daily gate also expected an obsolete status string (E0122).
- Correction batch adds the repository-root import bootstrap, a unit test for the adjudicated BAJAJFINSV date, and fail-closed gate checks against the actual machine result schemas. C1 remains PARTIAL.


## 2026-11-03 — Daily corporate-action sub-gate passed; intraday token handoff correction

- Run [41508838557](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41508838557) passed all 14 offline math/diagnostic tests and the protected daily adjusted-price diagnostic. Dhan authentication succeeded; RELIANCE bonus factor was 0.5 across OHLC (9/9 sessions) and BAJAJFINSV split+bonus factor was 0.1 across OHLC (11/11 sessions). The 13-Sep identity discrepancy was handled with the documented derived override while the raw source row remained unchanged.
- The intraday step made no price request: it attempted a second TOTP refresh in the same workflow, which returned no token, and the fallback profile check returned HTTP 401. Logged as E0123.
- Correction: hand off the first profile/data-plan validated token only through private Actions `GITHUB_ENV`, masked, and reuse it for the intraday request; no token is retained in the repository or artifact. The same run also exposed that the previous workflow file still contained the stale gate status string; its check is now being replaced with the actual machine status contract.


## 2026-11-03 — Ephemeral token handoff newline defect found

- Run [41509666199](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41509666199) completed the daily adjustment step and invoked the intraday diagnostic, but produced no minute-bar result. Artifact status: `BLOCKED_RUNTIME_ERROR`.
- Root cause found in code inspection: the private `GITHUB_ENV` writer used a double-escaped newline and appended literal backslash+n characters to the access token, corrupting the value passed to the next step.
- Fixed the environment writer and added/updated regression coverage to ensure it writes one actual token line and rejects actual line breaks. No token was logged or stored in the repo.


## 2026-11-03 — Preliminary intraday scale result and stronger same-session control

- Protected run [41510216099](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41510216099) passed offline tests, daily event adjustment checks and the token handoff. The minute-data script returned preliminary close-to-close ratios of 1.002562 for RELIANCE and 1.047470 for BAJAJFINSV, both classified near adjusted scale.
- The preliminary comparison crossed an overnight interval and therefore includes the market return. It is not strong enough for C1 acceptance by itself.
- Added a stronger same-session test: aggregate Dhan intraday OHLC on the cum date and ex-date and compare each field with Dhan daily adjusted OHLC for the exact same dates. This can distinguish pre-event 1.0-scale matching from the expected 2x/10x raw intraday scale without using an overnight return. E0125 records the methodology improvement.


## 2026-11-03 — Same-session intraday corporate-action scale comparison passed

- Protected Actions run [41510761625](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41510761625) passed all steps, including offline tests, daily adjustment checks, intraday diagnostic, report publication and both acceptance gates.
- RELIANCE 1:1 bonus (2024-10-28): same-session intraday/daily adjusted OHLC ratios for pre-date 2024-10-25 were open 0.994008, high 0.997211, low 1.000000, close 1.000226; ex-date ratios 1.000000, 1.000000, 1.000000, 1.000300. Result: `INTRADAY_MATCHES_DHAN_DAILY_ADJUSTED_SCALE`.
- BAJAJFINSV 5:1 split + 1:1 bonus (2022-09-13): pre-date ratios 0.996548, 0.997072, 1.000164, 1.006179; ex-date ratios 1.000000, 0.999756, 1.000000, 0.997899. Result: `INTRADAY_MATCHES_DHAN_DAILY_ADJUSTED_SCALE`.
- The same-session cross-endpoint test removes the overnight move in the earlier exploratory check. It indicates minute bars match Dhan's adjusted daily scale for these two events. It does not establish all-symbol/all-event coverage. No raw prices or intraday bars were published.
- E0125 closed for the two registered samples. E0126 closed (corrected report method description). Overall C1 remains PARTIAL because the remaining point-in-time event catalogue and identity review are open.


## 2026-11-03 — Intraday report-method wording corrected

- The same-session intraday-versus-daily scale comparison passed both sampled events on run [41510761625](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41510761625).
- A review found the Markdown explanation still described the earlier overnight pre-close-to-ex-open comparison even though the JSON and acceptance gate used same-session comparisons. Corrected the report generator and saved report so the documentation now matches the executed calculation.


## 2026-11-03 — C1 rights-compliant continuation

- Rechecked official NSE Terms of Use and Data Sharing & Usage Policy. The four-date PR archive probe is retained as technical feasibility only; it is not permission for systematic automated extraction or use in trading simulation. Disabled the PR archive-probe path, including manual dispatch.
- Dhan daily and same-session intraday scale checks passed for RELIANCE and BAJAJFINSV in protected run [41510761625](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41510761625). BAJAJFINSV's trading-ISIN date is adjudicated to 2022-09-13 inclusive; raw TejHQ value remains preserved and flagged stale.
- Added a new recipient-encrypted private queue workflow for the 37 complex member-event candidates. It reads the TejHQ personal-use-only source within Actions and uploads only ciphertext for one day; the private key is held outside GitHub and no cleartext event rows are logged or published.
- Next: decrypt only in the intended private runtime, verify issuer-first-party terms where permitted, and exclude cycles for unresolved event terms/identity. C1 remains PARTIAL; C2 panel accepted with limitations, C4/C5 gated.


## 2026-11-03 — First private issuer queue attempt failed before extraction

- Workflow [41513029040](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41513029040) passed two offline encryption tests and restored the encrypted TejHQ cache, but the queue script stopped before loading candidate rows because the repository root was missing from `sys.path` (E0128).
- No cleartext candidate data was generated, written, logged, or uploaded. Added the root-path bootstrap before project imports; retry required.


## 2026-11-03 — Recipient key rotation for private issuer-event queue

- The successful private queue workflow [41513398732](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41513398732) emitted a recipient-encrypted ciphertext artifact, but the matching private key was not available in the active research runtime. The candidate queue therefore could not be reviewed event by event.
- Generated an RSA-3072 recipient keypair outside GitHub. Only the public key and fingerprint are committed; the private key remains in the current local runtime with restrictive file permissions. No private-key bytes are logged, committed or uploaded.
- Next step: run the encrypted queue builder again against the current public key, decrypt the one-day artifact locally, and proceed with issuer-first-party evidence collection. No TejHQ raw rows will be persisted to the repository or Pages.


## 2026-11-03 — Bounded issuer-source review of 37 complex event candidates

- Protected workflow [41514027613](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41514027613) successfully built a recipient-encrypted queue; 37 candidates joined unambiguously to point-in-time member keys. The private event-level decision ledger and source-to-row map are retained outside GitHub because the source queue is personal-use-only.
- Issuer and official exchange source review established 17 equity bonus-share actions, 9 splits, 6 rights offers and 3 merger/demerger schemes. Two of the 19 bonus-labelled candidates are non-equity NCD distributions, not equity bonuses. Terms/record-date evidence was found for all 37 candidates: 35 with issuer-first-party source evidence and 2 with official exchange-primary evidence where an issuer notice was not located in this bounded search.
- Important corrections include the debenture classification, a later issuer corrigendum revising a bonus record date to 4 June 2026, POWERGRID's 1:3 bonus with 12-Sep-2023 record date, and source-adjudicated BAJAJFINSV trading identity from 13-Sep-2022.
- No manual corporate-action factor or rights TERP was applied. No merger/demerger generic price factor was applied. Full historical security identity/price continuity remains open; Dhan same-session adjusted-scale evidence still covers only two samples.
- The remaining 674 catalogue candidates comprise 625 dividends, 20 buybacks and 29 AGM/other events. Their review remains a separate bounded block. The 625 dividend candidates are not mechanically added back to the NIFTY price-index target.
- Public aggregate report: [C1_ISSUER_EVENT_REVIEW_AGGREGATE.md](research/constituent_weekly/C1_ISSUER_EVENT_REVIEW_AGGREGATE.md). Sanitised machine summary: [C1_ISSUER_EVENT_REVIEW_AGGREGATE.json](research/constituent_weekly/C1_ISSUER_EVENT_REVIEW_AGGREGATE.json).
- **Disposition:** 37-candidate source review complete; C1 overall **PARTIAL / NOT PASSED**; C2 panel remains PASS WITH C1 LIMITATIONS; C3 exploratory complete with no confirmed stock-model edge; confirmatory C4/C5 remain gated.


## 2026-11-03 — Next bounded queue for 49 buyback and AGM/other candidates

- The 37-candidate bonus/split/rights/merger-demerger queue is complete and published as aggregate results.
- Added a separate protected encrypted queue for the remaining 20 buybacks and 29 AGM/other candidates. It reuses the pinned TejHQ encrypted cache and existing recipient public key; it emits only aggregate counts and a one-day ciphertext artifact.
- Dividend events (625) are not bundled into this queue because the locked protocol preserves NIFTY price-index semantics and does not mechanically reinvest cash dividends. They remain subject to forecast-time and affected-window review where relevant.


## 2026-11-03 — Secondary 49-event review and corrected 711-candidate catalogue

- Protected queue [41517328794](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41517328794) completed SUCCESS; 49 unique candidates joined to 49 point-in-time member keys with zero ambiguity.
- Source review corrected the feed classes: 21 buybacks (one originally under “other”), 3 dividends (also under “other”) and 25 AGM/governance. Primary issuer/SEBI/exchange offer/record-date evidence was found for all 21 buybacks; issuer/exchange amount/date evidence for the 3 dividend corrections.
- HCLTech ₹2/record 2018-08-06; TCS ₹4/record 2018-10-24; Nestlé India ₹135/record 2020-11-02; NTPC buyback ₹115/record 2020-11-13.
- All AGM records remain excluded from predictive features until actual issuer/exchange notice timestamps are verified before the 10:00 IST forecast cutoff. No price factor is applied to buybacks, dividends or AGMs.
- Corrected final 711 classification: 17 equity bonuses, 2 NCD distributions, 9 splits, 6 rights, 3 merger/demerger, 21 buybacks, 628 dividends and 25 AGM/governance. Full identity, adjusted-price continuity and affected-cycle exclusions remain open.
- Reports: [C1_BUYBACK_AGM_REVIEW_AGGREGATE.md](research/constituent_weekly/C1_BUYBACK_AGM_REVIEW_AGGREGATE.md), [complex event aggregate](research/constituent_weekly/C1_ISSUER_EVENT_REVIEW_AGGREGATE.md).


## 2026-11-03 — Workflow template correction for complex-event cycle sensitivity

- The initial cycle-exclusion workflow run [41523805932](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41523805932) started, but review found GitHub Actions expression markers had been over-escaped in the committed YAML. Token and artifact/cache inputs would not resolve.
- Corrected the workflow expressions in one batched commit. The first run is not a research result; the corrected run must validate artifact download, checksum verification, decryption, event joins and 47/94 sensitivity.

## 2026-11-03 — Weekly expiry calendar correction discovered

- The expiry parser filtered only regular weekly expiries and dropped contract-present rows explicitly marked as holiday-shifted weekly expiries.
- Reconstruction from the official daily-session calendar changes the registered sample from 258 to 260 cycles. It restores the 2021-11-08 to 2021-11-11 cycle and splits the October 2025 window at the actual 2025-10-20 expiry.
- The prior 258-cycle C2 panel, 37-event cycle-exclusion sensitivity and dependent C3 metrics are quarantined as historical artifacts, not current acceptance evidence.
- C1 and C2 parsers now accept the two explicit verified status values only when the contract-expiry flag is true. Regression tests cover both shifted dates and the cycle split.
- C3's holdout boundary is calculated as floor(80% of eligible cycles): 206 for 258 and 208 for 260.
- Next: cached C1 coverage refresh, C2 panel-only rebuild, automatic C3 rerun, then recalculate event-cycle sensitivity against the new C2 manifest. No strategy or cost claim is authorised by this correction.


## 2026-11-02 — C1 continuous stock/index target coverage

- **Auditor status:** PARTIAL_OR_BLOCKED_TARGET_COVERAGE; data-coverage gate: FAIL; identity/action gate: SYMBOL_MAPPING_RESOLVED_KNOWN_AND_UNIVERSAL_CORPORATE_ACTION_REVIEW_PENDING.
- **Window:** 2021-11-08 to 2026-10-27.
- **Coverage:** 26/260 valid NIFTY targets; 13 cycles meet the stock and index data rules; 0 confirmatory cycles after the 104-cycle warm-up.
- **API/cache:** 1083 requests this run; reused 0 index and 0 stock-symbol chunks.
- **Interpretation:** data coverage is assessed independently of security identity/corporate-action treatment. This audit does not train or evaluate a model and does not unlock C2.
- **Artifacts:** C1_CONTINUOUS_COVERAGE.json and C1_CONTINUOUS_COVERAGE_REPORT.md.


## 2026-11-03 — C1 HTTP 400 diagnostic and hold
- C1 run [41529572895](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41529572895) completed its audit and published a sanitized artifact, but failed its registered coverage gate.
- Dhan profile returned HTTP 200 and the data plan was active. Of 1,083 requests, 70 stock chunks and 2 index chunks produced usable responses; 992 stock chunks and 19 index chunks returned HTTP 400.
- The current request wrapper discarded non-2xx response bodies, so the exact provider rejection cause remains unknown. No speculative fix or broad retry is authorized. Next action is to add sanitized error-code/message diagnostics and test one known failing request before any full rebuild.
- C2 remains independently in progress; C3 stays gated until the corrected C2 panel and all upstream data acceptance criteria pass.


## 2026-11-03 — C1 failure diagnostic and regression correction
- C1 continuous coverage run [41529572895](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41529572895) failed its formal gate: 26/260 index target cycles and 13/260 stock-plus-index cycles passed. Dhan profile auth returned HTTP 200 and the data plan was active. The audit recorded HTTP 400 for 19/21 index chunks and 992/1,062 stock-symbol chunks, but discarded provider error details.
- The bounded response-shape probe [41533187708](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41533187708) returned usable payloads in 23/26 cases, including full 90-day stock/index calls and a 16-symbol burst. Its three failures were all legacy HDFC daily-history tests returning DH-905. This does not explain the 1,011 historical intraday request failures. Exact windows from the failed C1 chunks were added to the next bounded probe.
- The expanded offline tests exposed E0138: the expected DH-905 category label differed from the emitted label. The code now maps DH-905 / DH-907 to explicit sanitised categories.
- C2 corrected panel-only build [41530483274](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41530483274) remains in the panel-construction step; no formal C2 result exists. C3 remains gated.


## 2026-11-03 — Follow-up to E0138: align all classifier assertions
- Offline run [41534173076](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41534173076) produced 95 passed and 1 failed because a second nested-remarks test still expected `DHAN_DH_905`. The response classifier correctly emitted the explicit `DHAN_INPUT_EXCEPTION_DH905` category.
- Updated the remaining stale expectation. The associated live exact-window probe was skipped by the workflow's test-success gate; no new provider result is inferred from this failed run.


## 2026-11-03 — E0140: controlled Dhan recovery preparation
- The exact-window Dhan diagnostic [41534685957](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41534685957) passed 7/7 requests for NIFTY and active-stock 90-day chunks that had failed in the continuous C1 audit. It passed 30/33 diagnostic requests overall; the three failures were legacy HDFC daily-history calls returning DH-905.
- Since the previous C1 HTTP 400 response body was discarded, its root cause cannot be recovered. Concurrent C1/C2 acquisition was a possible contributor, not a confirmed cause; the API docs distinguish DH-904 rate-limit errors, DH-905 input errors and Data API 805 too-many-requests blocking warning. The documentation has separate statements for overall Data API request quotas and minute/hourly requests, so no claim is made that the original HTTP 400s were definitely rate-limit responses.
- Updated C1 intraday requests to use one-second pacing, preserve only whitelisted provider error codes/types/categories, retry only explicit DH-904 with bounded backoff, and avoid retrying input/data/805 errors. C1/C2 live intraday workflows share a concurrency group to prevent overlap.
- The formal acceptance thresholds are unchanged. Rebuild and C2 panel acceptance are pending; C3 remains gated.
