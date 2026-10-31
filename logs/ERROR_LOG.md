# Error and correction log

## 2026-10-25 — Prediction page prerequisite audit
- **Finding:** The repository README described planned research artifacts/workflows that were not present in the inspected main-branch tree.
- **Impact:** No verifiable trained ExtraTrees artifact, feature matrix, or expiry calendar was available to the prediction page implementation. Producing a numerical forecast would be fabricated.
- **Correction:** Page uses a visible unavailable state; inference script requires exact trained feature names, an exact as-of-date feature row, and a verified calendar. It never silently substitutes a nearby date.
- **Status:** Open until the model/data pipeline produces compatible artifacts and a successful forecast is validated.
- **Security:** No secret values or private chain-of-thought are written to repository logs.


## E0006 — 2026-10-25 — Initial prediction page workflow failed
- Severity: High / deployment blocker.
- Symptom: GitHub Actions run 40196235090 failed at `actions/setup-python@v5`; inference and deployment steps were skipped.
- Root cause: The minimal main branch lacked the requirements file expected by pip caching, and its standalone inference script expected model artifacts that were not present. The branch also duplicated an existing research-backed forecast pipeline.
- Correction: Reuse the existing ExtraTrees pipeline and published forecast schema from the research branch; add the dependencies and pipeline assets; replace the placeholder page; use the dedicated Pages deployment workflow.
- Residual risk: The integration workflow has not yet been run on main; verify after merge. The model/source gate remains blocked for research reasons, independent of page deployment.
- Security: No secrets or private reasoning recorded.


## GitHub Actions failure — run 40196725878
- Status: BLOCKED. One or more workflow steps failed; inspect the Actions run for the exact failing step.
- The workflow is configured to continue with public data when the optional Dhan branch fails.
- No secrets, access tokens, PINs or TOTP values should be copied from runner diagnostics into repository logs.


## Dhan authentication attempt — run 40196840830
- Status: FAILED or incomplete. The public archive route will still be attempted.
- Sensitive response fields and secrets were withheld. Inspect the Dhan-auth step status in Actions.

## E0007 — 2026-10-25 — Static prediction behavior did not meet the requested workflow
- **Severity:** High — functional requirement gap.
- **Symptom:** Predict looked up precomputed JSON/CSV records and returned "No saved forecast exists for this date" rather than querying Dhan and fitting ExtraTrees.
- **Root cause:** The page had been implemented as a static report UI. GitHub Pages cannot securely read GitHub Actions secrets or run Python server-side, so an authenticated backend is needed.
- **Correction in progress:** Added `live_api/app.py`, the secure Dhan-to-ExtraTrees inference path, a Hugging Face Docker Space deployment script/workflow, server-side minute-chunk caching, a browser job/polling flow, and a Phase 7 acceptance plan. The backend refreshes the Dhan token on each request and fits the model on request; it never returns credentials.
- **Additional correction:** An earlier manual-date-input edit left literal newline escape characters in a JavaScript statement. The live browser script has since been replaced with a complete parser/polling implementation to remove that syntax error.
- **Remaining gates:** CI test run; HF_TOKEN write/Space deployment; Dhan authentication and intraday-data verification; browser smoke test. If deployment credentials or permissions are missing, the service stays disabled rather than exposing secrets.

## E0008 — 2026-10-25 — Live inference backend blocked by Hugging Face compute-plan gate
- **Severity:** High — deployment acceptance gate.
- **Runs:** [40198909189](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40198909189), [40199001881](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40199001881), [40199234322](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40199234322).
- **Symptom:** Live API logic tests passed (12 passed), but Hugging Face Docker Space provisioning failed with HTTP 402. The endpoint config was not published.
- **Root cause:** Hugging Face's current Space management documentation states that Docker/Gradio Spaces on CPU-basic require a Pro subscription for individual accounts or Team/Enterprise for organizations; without an eligible plan, creating or moving a Docker Space can return HTTP 402. See https://huggingface.co/docs/huggingface_hub/guides/manage-spaces.
- **Correction:** Added sanitized stage/HTTP diagnostics and fixed stage tracking in `scripts/deploy_live_api_space.py`. No credentials or response bodies are logged.
- **Blocker / intervention needed:** The existing HF token can access the Hub sufficiently to reach the provisioning operation, but the current account/plan cannot provision this Docker backend. To continue, enable the applicable Hugging Face plan/compute entitlement or set the repo variable `HF_SPACE_ID` to an already writable, eligible Docker Space that can be updated by this token. Until then, the public page safely keeps live inference disabled and does not fall back to saved CSV/JSON records.

## E0009 — 2026-10-25 — Follow-up deployment diagnostic staging bug
- **Severity:** Medium — delayed root-cause confirmation.
- **Run:** [40199152655](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40199152655).
- **Symptom:** A diagnostics-only follow-up failed with `NameError` while handling the temporary staging directory.
- **Root cause:** The directory context variable reused the `stage` name used for the human-readable deploy-stage diagnostic. The attempted correction also left a reference to `stage_dir` before initializing it.
- **Correction:** Replaced the path variable with `stage_dir`, retained `stage` as a string, and reran deployment. The corrected run [40199234322](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40199234322) now identifies the actual failure stage as Docker Space creation with HTTP 402.
- **Status:** Code correction validated; external Hugging Face compute entitlement remains the blocker. Do not repeat deployments until an eligible Space/plan is available, except for an explicit user-approved provider change.


## E0010 — 2026-10-25 — No safe alternate backend credentials available
- **Severity:** High — external deployment prerequisite.
- **User direction:** Continue with a secure alternative backend while keeping the UI on GitHub Pages.
- **Checks:** The repository has Dhan credentials, HF_TOKEN, and GOOGLE_API_KEY configured as GitHub organization secrets. The Hugging Face token reaches Space creation but the provider returns HTTP 402 because the current account/plan cannot provision the required Docker compute. A Google API key is not a Cloud Run/Functions deployment identity; it cannot safely create and configure a private server-side service on its own.
- **Security decision:** Do not move Dhan PIN/TOTP into Pages JavaScript, expose GitHub Actions credentials in a URL, or create an unauthenticated workflow trigger.
- **Remaining external input:** Either an eligible existing Hugging Face Docker Space (HF_SPACE_ID repository variable) or a deployment credential for an alternative backend (e.g. Render API key or Cloudflare account/API token). Until one exists, live inference cannot be deployed safely; the UI must remain fail-closed.


## E0011 — 2026-10-25 — Separate API host blocked; move inference into GitHub Actions
- Severity: High — on-demand deployment blocker.
- Observed: Hugging Face Docker Space provisioning returned HTTP 402; the Pages endpoint config remained empty and click-to-predict could not run end-to-end.
- Correction: added a GitHub Actions inference runner and default-branch workflow triggered by authenticated prediction-request issues. The workflow restricts secret-bearing execution to repository OWNER/MEMBER issue authors, validates the date title, keeps Dhan secrets in Actions, caches historical chunks, and publishes sanitized result JSON to Pages. Added a manual workflow_dispatch path.
- Security decision: Pages cannot securely invoke authenticated GitHub Actions REST APIs without a browser-exposed token. The UI therefore provides a prefilled issue link for the user to submit; no PAT, Dhan token, PIN, or TOTP is embedded in JavaScript.
- Current status: implementation is not yet verified by a live Dhan request. If issue permissions or Actions write permissions prevent publishing, record the failure and do not expose credentials or fall back to an old forecast.


## E0012 — 2026-10-25 — Issue-triggered runtime smoke test not yet observable
- Severity: Medium — end-to-end acceptance pending.
- Evidence: CI passed in runs 40200568709 and 40200737861. Controlled request issue [#9](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/issues/9) was opened and reopened after workflow changes, but no completion comment or date-specific JSON result was visible at the latest check.
- Correction already merged: the workflow author gate includes OWNER, MEMBER and COLLABORATOR; reopened issues are accepted for retries.
- Remaining diagnosis: determine whether GitHub skipped the issue event, the job was skipped by authorization, repository Actions settings/permissions blocked it, or Dhan retrieval is still running. Do not embed credentials in Pages or infer a forecast from a missing output.


## E0013 — 2026-10-25 — Dhan token refresh used wrong HTTP method
- Severity: High — live prediction blocked before data retrieval.
- Evidence: Actions run [40201297978](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40201297978) completed the workflow and published a failure record for 2024-09-20: `Dhan token refresh failed (HTTP 405)`. Inspection found `refresh_dhan_token()` used `requests.get()` against Dhan's token-generation endpoint.
- Root cause: official DhanHQ authentication docs specify `POST https://auth.dhan.co/app/generateAccessToken` with `dhanClientId`, `pin`, and `totp` query parameters. Source: https://dhanhq.co/docs/v2/authentication/ and https://github.com/dhan-oss/DhanHQ-py/blob/main/src/dhanhq/auth.py.
- Fix: changed GET to POST in `live_api/app.py` (commit `ad14c138c91f75ec801bf201e1770271bb2deb6e`) and changed `scripts/run_live_prediction.py` to exit non-zero if inference fails (commit `8a1c1c3659e6c1e37cfca5ffc41fd668094f196f`). Added a mocked regression test in `tests/test_live_api.py` (commit `5a5789c9cf8569f7890a2e7e42b5c941641f81dd`).
- Retry: issue #11 was edited to trigger a fresh run [40201653154](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40201653154). Final Dhan/model outcome pending.
- Secondary issue: Actions cache save reported `cache write denied: token has no writable scopes`; historical minute cache persistence is not verified and needs a separate correction.


## E0014 — 2026-10-25 — Corrected Dhan token HTTP method; first live inference succeeded
- Severity: Resolved for token method; separate research gates remain blocked.
- Root cause E0013 was confirmed and fixed: Dhan token generation requires POST. Retry run [40201653154](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40201653154) completed successfully and published a fresh record for 2024-09-20.
- Result record: UP, raw UP score 0.5131, target expiry 2024-09-26, 147 training labels, 268,510 valid minute bars, 20/20 features present, training labels through 2024-09-19.
- No leakage was detected by the existing cutoff check. Independent anchor reconciliation and transaction-cost backtest remain BLOCKED, so this is not cleared for trading.
- Separate cache warning observed on earlier run: `cache write denied: token has no writable scopes`. Added `actions: write` to workflow permissions in commit `04f55a01c7ce65b086aa73d82b6bad955b065e05`; confirm with next run before marking persistent caching resolved.


## E0016 — 2026-10-25 — Remove external-host dependency from Pages prediction

- **Severity:** High — deployment architecture requirement.
- **User decision:** Use GitHub Actions + GitHub Pages only; avoid Render or another separately hosted API.
- **Root cause:** The previous branch still depended on a separately deployed FastAPI endpoint and therefore did not satisfy the free-hosting requirement.
- **Correction prepared on `phase/github-actions-pages-free`:** add a weekday 10:30 IST scheduled workflow and manual dispatch; run the existing Dhan-backed ExtraTrees script in Actions; publish date-specific and latest JSON records; update the Pages UI to read published records without issue submission or external API calls.
- **Security:** Dhan credentials remain in GitHub Actions secrets. No GitHub token or Dhan credential is embedded in Pages.
- **Limitation:** Pages cannot securely trigger a private workflow immediately on button click without an authenticated mechanism. The button loads the latest scheduled/published result.
- **Status:** Implementation branch prepared; CI, merge, scheduled Dhan run and Pages browser verification are pending. Trading gate remains BLOCKED.


## E0017 — 2026-10-25 — Free Actions + Pages implementation merged; live run pending

- **Status:** Implementation merged to `main` in PR [#13](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/pull/13), merge commit `ca5ad434ed0a919495b4897b6e1034a82da257b2`.
- **Validation:** GitHub Actions regression run [40203509499](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40203509499) passed; integration/workflow validation run [40203521024](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40203521024) passed; final live API regression run [40203521052](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40203521052) passed.
- **Pages deployment:** Run [40203599397](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40203599397) was in progress at the last status check.
- **Remaining acceptance gate:** No fresh scheduled/manual Dhan inference or live browser result has been verified yet. The next scheduled weekday run is expected at 10:30 IST. If it fails, inspect the workflow and published failure JSON; do not use an old forecast as fresh.
- **Research gate:** Trading remains blocked pending independent anchor reconciliation and executable option-level costs/slippage.


## Scheduled prediction failure — run 40204327333
- Date: 2026-10-02
- Status: FAILED; inspect the linked Actions run for the failing step.
- No secrets or provider response bodies are copied into logs.


## Scheduled prediction — run 40204498793 (retry outcome)
- Date: 2024-06-07
- First attempt: FAILED at inference with the reported prior-expiry/session validation error.
- Retry: SUCCEEDED; current published record is `docs/assets/predictions/2024-06-07.json` and the workflow run is green.
- The successful retry shows the earlier failure was not a deterministic rejection of this date. The exact transient cause of the first attempt is not proven; preserve this history rather than claiming a confirmed root cause.
- Data-quality status remains BLOCKED for independent anchor reconciliation and executable costs/slippage.
- No secrets or provider response bodies are copied into logs.


## E0011 — 2026-10-25 — Date dispatch and stale-result publication safety
- **Finding:** The supplied screenshot shows a run for 2024-06-07 rejected by the calendar gate: it was not recognized as the first NSE session after the reported prior verified expiry, 2024-06-06. This does not prove whether the calendar data or session construction is wrong; do not bypass the gate without auditing source rows.
- **Additional defect:** The Pages publish step could preserve an existing date JSON after failed inference and copy it to latest.json, risking stale output being shown as fresh.
- **Correction staged:** Failed inference now overwrites same-date output with an explicit failed record. The Pages date form opens the workflow page with the selected date encoded in the URL; user must confirm Run workflow because static Pages cannot securely dispatch authenticated Actions.
- **Validation:** Pending branch CI and workflow run.
- **Security:** No credentials or private reasoning logged.


## E0012 — 2026-10-25 — Historical date inference succeeds on rerun
- **Run:** [40204498793](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40204498793), successful retry.
- **Date:** 2024-06-07, first NSE session after verified NIFTY weekly expiry 2024-06-06.
- **Result:** UP; raw ExtraTrees UP score 0.547499; target expiry 2024-06-13; anchor 22,978.3; 132 completed training rows through 2024-06-06; 20/20 features; 241,516 minute bars.
- **Interpretation:** The successful retry disproves the earlier assumption that the date is consistently rejected by the current workflow. The exact cause of the initial failed attempt remains unverified and may have been transient/data-dependent. Do not label the score as a calibrated probability or profitability estimate.
- **Remaining gate:** Independent 10:00 anchor validation and executable options P&L including Paytm Money costs, spreads and slippage are still BLOCKED.
- **Security:** No secrets logged.


## E0013 — 2026-10-25 — Pages form redirected instead of loading published result
- **Observed:** User showed Pages form selecting 07-06-2024 but displaying an old expiry validation error, while the GitHub Actions rerun and docs/assets/predictions/2024-06-07.json were successful.
- **Root cause confirmed in code:** The form submit handler was explicitly navigating to the Actions workflow URL instead of calling the existing fetchPrediction(asOfDate) function. This contradicted the page's published-result UX and caused unnecessary workflow redirects. Browser caching may also have contributed to the displayed stale error.
- **Correction:** Form now fetches and renders the already-published JSON in place; no automatic redirect. If no successful result is available, show a clear error and tell the user where to run Actions manually. Added cache-busting query to predictor.js script URL.
- **Validation:** Pending syntax/deploy checks. No tokens exposed. Research gate remains BLOCKED for independent anchor validation and executable option costs/slippage.


## Scheduled prediction failure — run 40212055994
- Date: 2026-05-06
- Status: FAILED; inspect the linked Actions run for the failing step.
- No secrets or provider response bodies are copied into logs.


## E0014 — 2026-10-25 — Session validation incorrectly coupled to Dhan bar coverage
- **Observed:** Workflow run screenshot rejected 2026-05-06 after verified expiry 2026-05-05 with a message claiming it was not the next NSE session. This pattern can affect any date where Dhan minute coverage differs from official sessions.
- **Root cause:** `_do_prediction` built `next_session_dates` from `daily`, which is derived exclusively from available Dhan minute bars. A missing Dhan session could therefore be misreported as a calendar violation.
- **Fix staged:** Introduced `_first_official_session_after` using the official NSE daily-session reference. Date validity is checked against official sessions; Dhan anchor/label coverage remains a separate required gate. Added regression tests for the 2026-05-05 → 2026-05-06 transition and empty calendar handling.
- **Status:** PR/CI pending. Do not bypass missing-bar or leakage checks.


## Scheduled prediction failure — run 40214389317
- Date: 2026-08-05
- Status: FAILED; inspect the linked Actions run for the failing step.
- No secrets or provider response bodies are copied into logs.


## E0015 — 2026-10-25 — Selected date missing anchor bar
- **Run:** [40214389317](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40214389317)
- **Date:** 2026-08-05
- **Observed error:** Dhan returned no valid 10:00–10:03 IST NIFTY 50 minute bar.
- **Potential cause:** The selected date falls inside an old cached 90-day chunk; current cache logic trusted completed chunks indefinitely. This is a testable hypothesis, not yet confirmed as root cause.
- **Fix staged:** Always refresh only the 90-day chunk containing the requested date; keep all other historical chunks cache-first. This limits data transfer and lets provider corrections repair incomplete selected-date data. If the bar remains absent, treat as true provider/data gap and do not infer an anchor.
- **Status:** PR/CI pending.


## E0016 — 2026-10-25 — Post-merge verification pending; legacy API deploy failure
- **Cache-refresh fix:** PR #16 merged as `c81a3c5e1bc9a6021c530ebdf691313acbd8c80a`; test and validation checks passed.
- **Selected-date output:** `docs/assets/predictions/2026-08-05.json` remains a failed status record with the explicit message that the latest attempt failed before producing a fresh prediction. No stale prediction was reused.
- **Post-merge run:** No fresh `Free scheduled NIFTY ExtraTrees prediction` run on the merged SHA was present at this check; cache-refresh behavior therefore remains unverified end-to-end.
- **Separate workflow:** `Deploy Live Dhan ExtraTrees API` run [40214787884](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40214787884) failed at the legacy external Docker Space deployment step. This is not the chosen free GitHub Actions + Pages prediction pipeline. Do not merge/depend on the legacy external service for this project unless architecture is explicitly changed.


## Scheduled prediction failure — run 40215041309
- Date: 2026-08-05
- Status: FAILED; inspect the linked Actions run for the failing step.
- No secrets or provider response bodies are copied into logs.


## E0017 — 2026-10-25 — Missing anchor without diagnostics or targeted retry
- **Run:** [40215041309](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40215041309)
- **Date:** 2026-08-05
- **Observed:** Large-window and refreshed cache requests still did not yield the expected 10:00–10:03 anchor.
- **Gap in troubleshooting:** Existing code did not retry the selected date as a one-day request and gave no count/timestamp range for the session.
- **Fix staged:** Add a targeted one-day Dhan request for the selected session and merge its bars by timestamp; improve safe error diagnostics with valid session bar count, timestamp range, and nearby 09:57–10:06 count. No response bodies, tokens, or client credentials are logged.
- **Status:** PR/CI pending; provider availability remains unconfirmed.


## Scheduled prediction failure — run 40310768077
- Date: 2026-10-26
- Status: FAILED; inspect the linked Actions run for the failing step.
- No secrets or provider response bodies are copied into logs.


## Scheduled prediction failure — run 40487276565
- Date: 2026-10-27
- Status: FAILED; inspect the linked Actions run for the failing step.
- No secrets or provider response bodies are copied into logs.


## Dhan authentication attempt — run 40675278048
- Status: FAILED or incomplete. The public archive route will still be attempted.
- Sensitive response fields and secrets were withheld. Inspect the Dhan-auth step status in Actions.


## Scheduled prediction failure — run 40677745627
- Date: 2026-10-28
- Status: FAILED; inspect the linked Actions run for the failing step.
- No secrets or provider response bodies are copied into logs.


## Scheduled prediction failure — run 40864956441
- Date: 2026-10-29
- Status: FAILED; inspect the linked Actions run for the failing step.
- No secrets or provider response bodies are copied into logs.


## Scheduled prediction failure — run 41046711634
- Date: 2026-10-30
- Status: FAILED; inspect the linked Actions run for the failing step.
- No secrets or provider response bodies are copied into logs.


## Dhan authentication attempt — run 41145607225
- Status: FAILED or incomplete. The public archive route will still be attempted.
- Sensitive response fields and secrets were withheld. Inspect the Dhan-auth step status in Actions.


## E0024 — 2026-10-31 — Dhan equity preflight blocked at profile authentication
- **Run:** [41181684573](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41181684573).
- **Observed:** The Dhan equity preflight workflow completed successfully and its nine offline response-validation tests passed. The live `/v2/profile` request returned HTTP 401 after the configured TOTP refresh/fallback path.
- **Impact:** No active data-plan confirmation, scrip-master equity ID resolution, 2018 daily-history request or stock intraday bars were obtained. This is not evidence that the stock historical endpoint lacks coverage; the request was blocked before those endpoints.
- **Correction/next step:** Keep the workflow fail-closed. Verify token/client binding and account/data-plan entitlement against Dhan's current authentication/profile requirements. Do not infer or hard-code security IDs, and do not attempt historical equity requests until profile authentication succeeds.
- **Security:** No credential, token, PIN, TOTP or raw provider response was copied to the repository.

E0025 — 2026-10-31 — Dhan TOTP endpoint returned HTTP 200 without an access token; profile rejected fallback

- **Run:** [41181948126](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41181948126).
- **Observed:** 10/10 mocked response tests passed. Live token-generation endpoint returned HTTP 200 but the JSON contained only `message` and `status` keys; no access-token field was present. The supplied `DHAN_ACCESS_TOKEN` fallback was then used, but the documented profile check returned HTTP 401.
- **Correction attempted:** changed the profile check to send only the `access-token` header, exactly as shown in Dhan's v2 documentation. The result remained HTTP 401.
- **Interpretation:** no data-plan response or market-data request was reached. This points to an account-secret/token validity issue, not evidence of missing equity history. The sanitized diagnostic deliberately omits provider message values.
- **Next step:** verify that `DHAN_CLIENT_ID`, `DHAN_PIN`, `DHAN_TOTP_SECRET` all belong to the same account, TOTP is enabled for API authentication, the PIN is current and six digits, and the fallback token is freshly generated (24-hour validity). Only rerun data probes after profile returns 200.
- **Security:** no credentials, tokens, PINs, TOTP values or raw provider messages were committed.


## E0026 — 2026-10-31 — Dhan TOTP endpoint returned no token
- **Observed:** Corrected shared helper now uses POST; BUP-01 preflight independently uses POST. Live endpoint returned HTTP 200 with only `message` and `status` keys. No `accessToken` field was present. The fallback profile request returned HTTP 401.
- **Impact:** No authenticated profile, data-plan confirmation, security-master resolution or equity price history was reached.
- **Correction:** Added sanitized classification of known authentication failure families without storing provider message text, plus regression coverage. Re-run is pending/in progress.
- **Security:** No credentials, token values or raw provider response text are stored.
- **Status:** OPEN — awaiting safe classification and, if confirmed by Dhan, correction of the relevant GitHub Actions secret(s).


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
