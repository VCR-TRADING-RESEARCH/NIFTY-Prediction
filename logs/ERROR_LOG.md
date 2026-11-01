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

## E0027 — 2026-10-31 — C1 source rights and coverage
- Official NIFTY IWF methodology requires exclusions beyond ordinary promoter/public ownership roll-ups; quarterly ownership summaries are not official index weights.
- NSE website terms restrict systematic automated collection and copying/reuse. Remote NSE scraping remains disabled pending permission/licence confirmation.
- Dhan v2 historical intraday documentation covers active instruments and 90-day request windows; it does not guarantee inactive/delisted constituent history.
- Impact: C1 remains blocked; no panel/model was created. No further TOTP refresh was attempted.

## E0028 — 2026-10-31 — Membership dataset is not a free-float weight dataset
- **Observed:** An openly licensed CC BY 4.0 NIFTY 50 membership history is available, but the source's `weightage` column is blank. Its separate quarterly ownership table contains promoter/FII/DII/public/pledge roll-ups, not official IWF.
- **Impact:** Membership intervals can reduce survivorship and membership-date errors, but cannot support index-weighted forecasts or exact basket reconstruction. Do not fill weights with equal weights, ownership percentages or market-cap proxies and call them NIFTY weights.
- **Correction:** Import only the NIFTY 50 membership subset under its data licence with attribution, add the official 2026-09-30 WIPRO-to-BSE replacement and 103 month-end cardinality tests. Keep weights/IDs/corporate-actions and Dhan coverage as independent C1 blockers.
- **Status:** Membership sub-gate PASS WITH LIMITATIONS; overall C1 OPEN/BLOCKED; no C2 model or strategy produced.

## E0029 — 2026-10-31 — C1 membership audit under-specified Tata Motors corporate action
- **Original issue:** Earlier 103/103 month-end assertion expected exactly 50 members on every date and did not account for the official temporary zero-price `DUMMYTATAM` index placeholder. The dataset also carried the new `TMPV` ticker backwards before its NSE effective date.
- **Evidence:** NSE Indices 2025-10-07 release adds DUMMYTATAM at zero price effective 2025-10-14; 2025-11-13 release removes TMCV effective 2025-11-17. NSE circular NSE/FAOP/70882 changes TATAMOTORS -> TMPV effective 2025-10-24.
- **Correction:** Replace historical TMPV alias with TATAMOTORS to 2025-10-23; start TMPV on 2025-10-24; add the dummy interval 2025-10-14 to 2025-11-17 with `market_data_required=FALSE`. Update count expectations to 50 for 102 month-ends and 51 only for 2025-10-31.
- **Impact:** The earlier all-50 cardinality claim is superseded. Previous Actions run 41184751617 validated only the earlier four-test revision. New six-test workflow run is pending. No model or result used the flawed timeline.
- **Status:** CORRECTED IN DATA; membership integrity CI passed in run [41185169548](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41185169548), 6 tests. E0029 is closed for the point-in-time Tata symbol/dummy correction; broader C1 IWF/security/bar-coverage gates remain blocked.

## E0030 — 2026-10-31 — Membership CSV serialization and audit sequencing caused CI failures
- **Runs:** [41184902797](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41184902797) and [41184934278](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41184934278), both failed in the membership test step.
- **Observed:** An unquoted comma inside the DUMMYTATAM `notes` field was parsed as an extra CSV column, shifting `member_type` / `market_data_required`. The second assertion saw the earlier 84-row machine audit because the test revision triggered before the updated audit JSON had landed.
- **Correction:** Re-serialized the dummy row with valid CSV quoting and a comma-free note; verified 86 data rows × 11 columns, 85 unique symbols and no nonblank weightage. Ensured the updated audit JSON was committed before the next path-triggered test run.
- **Status:** CLOSED. Post-fix run [41185169548](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41185169548) succeeded with 6 tests. No market/model data was changed or used.

### E0030 resolution — 2026-10-31
- Corrective run [41185169548](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41185169548) succeeded; the dedicated membership workflow confirms **6 passed**. CSV column alignment and audit artifact sequencing issues are resolved.
- E0030 is **CLOSED** for this test/data-format defect. Do not reopen unless a regression occurs. Broader C1 gates remain blocked independently.

### E0029 resolution — 2026-10-31
- The corrected 86-row membership ledger, Tata symbol boundaries and temporary zero-price placeholder are now validated by the six-test Actions run [41185169548](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41185169548).
- E0029 is **CLOSED** for this specific corporate-action/interval correction. This does not certify all historic transitions, IWF weights or security-ID mappings.


## E0031 — 2026-11-01 — Five-year-edge QA fixture counted special session as post-market

- **Run:** [41252703953](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41252703953), test `test_analyse_intraday_range_excludes_2021_muhurat_date_and_postmarket_rows`.
- **Observed:** 25 tests passed and one failed. The fixture expected `outside_regular_hours_bar_count == 1`, but the implementation returned 2 because the count used total rows minus regular-session rows and therefore included both the 2021-11-04 Muhurat special-session row and the 2021-11-05 15:45 post-market row.
- **Correction:** Count post-market rows as outside regular hours only when they are not on an explicitly excluded special-session date; record special-session rows in the separate `special_session_excluded_bar_count`. The revised test suite passed 26/26 in run [41263593605](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41263593605).
- **Impact:** This closes the offline counter/test defect only. The 2021-11-01–2022-01-29 full-universe data request has not passed; the later live attempt was blocked by Dhan authentication.
- **Status:** CLOSED — offline logic and regression test. Historical 2021 coverage remains unverified.

## E0032 — 2026-11-01 — Dhan live preflight blocked while Actions job appeared green

- **Run:** [41263593605](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41263593605).
- **Observed:** Dhan token generation returned HTTP 200 but no access-token field in two attempts. Sanitized diagnostics classify the provider response as `TOTP_REJECTED_OR_INVALID`; the configured access-token fallback then received profile HTTP 401. No security-master or equity-history endpoints were called. The preflight JSON correctly records `BLOCKED_PROFILE_HTTP_401`, but the script's reporting path exited with code zero, allowing the overall Actions job to appear successful.
- **Correction:** Added a final workflow gate after sanitized diagnostics are committed. For non-PR/live runs, it requires `C1_DHAN_PREFLIGHT.json.status == PASS_ACTIVE_EQUITIES`; blocked/partial/no-result states now fail the Actions run. PR validation continues to run offline tests without secrets.
- **Security:** No token, PIN, TOTP seed, raw provider body, security ID or raw candle was added to logs.
- **Impact:** No new market data was acquired in this run. Prior successful samples remain valid only for their stated dates and scope.
- **Status:** CLOSED for the authentication blocker. Protected run [41266155250](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266155250) generated a fresh token on the first attempt, confirmed an active Data API plan and recorded a 0-second Dhan-server/runner clock difference. This proves the current protected flow works operationally; it does not establish which factor caused the previous response anomaly or imply that the user's configuration was incorrect. The same run correctly failed its separate data-quality gate because SHREECEM had one negative-volume row in the five-year-edge window.


## E0033 — 2026-11-01 — Workflow status gate initially preceded diagnostics commit

- **Observed during review:** The first workflow-gate patch in commit [8e31a7d](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/commit/8e31a7d813019733ccf23b07129f24d2a7cb7884) placed the new failing status check before the sanitized diagnostics commit step. A blocked live run could therefore have stopped before preserving its result.
- **Correction:** Moved the gate to the end of the workflow, after the diagnostics commit, in commit [02c8074](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/commit/02c8074750a65642ddf6078dd4abafce48c3f1fc). Read-back verified that the commit step precedes the fail-closed gate.
- **Impact:** No live workflow was dispatched between the two revisions; no diagnostic result was lost. The corrected workflow commits sanitized evidence first and only then returns a failing conclusion for a blocked/partial live preflight.
- **Status:** CLOSED — runtime verified in run [41266155250](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266155250): sanitized diagnostics committed first; final gate then exited non-zero on `PARTIAL_OR_BLOCKED` as designed.

### Runtime clarification — 2026-11-01
- Inspection of the executed job steps for run [41263593605](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41263593605) shows that it did not execute the `Enforce live Dhan preflight result` step. The current C1 workflow source does contain that step after the sanitized diagnostics commit, but that later workflow revision has not yet been exercised by a subsequent protected live run.
- Therefore run 41263593605 must be described as **offline tests PASS (26/26), live data gate BLOCKED, Actions job conclusion SUCCESS due to older workflow revision**. The later protected run [41266155250](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266155250) executed the gate after diagnostics were committed; it failed on the explicit `PARTIAL_OR_BLOCKED` data status. The workflow's fail-closed runtime behavior is now verified.
- Dhan authentication was subsequently recovered and is now CLOSED: protected run [41266897788](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266897788) generated a fresh token on attempt one, confirmed profile HTTP 200 and an active Data API plan, and passed the final Dhan data gate. The diagnostic clock difference was -1 second.
- This clarification does not change C1/C2 acceptance status.


## E0044 — 2026-11-01 — Offline Dhan authentication tests missing runtime dependencies

- **Run:** [41266339150](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266339150).
- **Observed:** The newly added offline CI step failed during test collection with `ModuleNotFoundError: No module named 'pyotp'`. The membership workflow installed pytest only, but the imported Dhan token module and shared TOTP helper require `pyotp` (and requests).
- **Correction:** Added explicit `pyotp` and `requests` installation to the offline workflow. Follow-up run [41266377005](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266377005) completed SUCCESS with **12 passed**.
- **Impact:** No live auth request or market-data request was affected by this failed offline job. It was a CI dependency-setup error, not a TOTP/provider credential finding.
- **Status:** CLOSED — required dependencies are explicit and the corrected offline suite passes.


## E0045 — 2026-11-01 — SHREECEM five-year-edge data contains one negative-volume row

- **Run:** [41266155250](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266155250).
- **Observed:** In the 2021-11-01–2022-01-29 90-day edge check, SHREECEM returned all 61 regular sessions, all 61 anchor sessions and all 61 15:00–15:14 expiry-proxy sessions; timestamps were unique and OHLC/numeric checks passed. Exactly one finite negative volume row caused the OHLCV invariant to fail. The other 49 point-in-time constituents passed all checks.
- **Correction/investigation:** Added a bounded, single-symbol diagnostic workflow to identify the offending timestamp only. It records no price/volume values, token or security ID. Its offline test caught an unsupported pandas `.dt.isoformat()` call before the live request; corrected it to format individual Timestamp values.
- **Status:** CLOSED — the single-symbol diagnostic [41266690449](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266690449) located the negative-volume row at **2021-12-30 15:29 IST**. This is after the locked 15:15 target cutoff and outside the target-scope data. The QA checker now validates OHLCV strictly through 15:14 and separately records post-cutoff anomalies. The corrected full 50-stock edge range then passed 50/50 in [run 41266897788](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266897788).


## E0046 — 2026-11-01 — Standalone SHREECEM diagnostic could not import repository module

- **Run:** [41266604463](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266604463).
- **Observed:** Offline diagnostic tests passed 2/2, but direct execution of the diagnostic script failed before any Dhan request with ModuleNotFoundError: No module named live_api. Direct script execution had not added the repository root to sys.path.
- **Correction:** Added the resolved repository root to sys.path before importing live_api or project scripts (commit 34e067d).
- **Impact:** No authentication or data endpoint call was made by this failed diagnostic attempt. The full-universe Dhan preflight result from run 41266155250 is unchanged.
- **Status:** CLOSED — corrected diagnostic run [41266690449](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266690449) passed. Repository root is added to `sys.path` before project imports; no Dhan requests were made by the failed run.


## E0047 — 2026-11-01 — Pandas datetime accessor does not implement vectorized isoformat

- **Run:** [41266547991](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266547991).
- **Observed:** The bounded SHREECEM diagnostic's offline test failed with `AttributeError: 'DatetimeProperties' object has no attribute 'isoformat'`. Pandas supports `Timestamp.isoformat()` on individual values, not `.dt.isoformat()` as a vectorized accessor.
- **Correction:** Convert the selected timestamp values to Python/Pandas Timestamp objects and call `isoformat()` per value.
- **Verification:** The next diagnostic workflow [41266604463](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266604463) passed both offline tests before reaching the separate import-path issue E0046.
- **Status:** CLOSED — regression test now protects the timestamp serialization.

## E0048 — 2026-11-01 — 15:15 target-scope refactor referenced an uninitialised post-cutoff frame

- **Runs:** [41266827905](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266827905) and [41266830527](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266830527).
- **Observed:** Offline range tests failed with `NameError: post_cutoff_frame is not defined` after the first partial edit moved the volume diagnostic but had not yet created the post-cutoff frame in `analyse_intraday_range`.
- **Correction:** Constructed `post_cutoff_frame` and the corresponding 15:15–15:30 mask explicitly, with target QA restricted to 09:15–15:14.
- **Verification:** Live protected preflight [41266897788](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266897788) passed its 50-stock data gate; offline regressions [41266922851](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266922851) passed **43/43**.
- **Status:** CLOSED — the target cutoff is covered by tests for both negative in-scope and out-of-scope volume cases.


## E0049 — 2026-11-01 — IWF unit-test file initially omitted from pytest invocation

- **Runs:** [41269416939](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41269416939) and [41269424179](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41269424179).
- **Observed:** The workflow path filter included tests/test_iwf_math.py, but its pytest command still listed only the pre-existing test files. The run passed **43 tests**, but none of the seven newly added IWF tests were executed. This was a CI coverage gap, not a test failure.
- **Correction:** Added tests/test_iwf_math.py explicitly to the pytest command in commit 12d997bf51c12a5780abcd6a9836d69853327bd0.
- **Verification:** Corrected push run [41269516064](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41269516064) and PR run [41269519499](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41269519499) both passed **50 tests**, including the seven IWF cases.
- **Status:** CLOSED — path trigger and test command now both include the IWF test module.

## E0050 — 2026-11-01 — Potential share-capital denominator mismatch in third-party IWF reconstruction candidate

- **Observed during mathematical audit:** The third-party parser documents its reported shareholding-percentage base as total shares less shares underlying depository receipts (A+B+C2). The official NSE IWF guideline's worked example explicitly calculates IWF using (Total Shares - excluded shares) / Total Shares, then rounds to six decimals. These are different denominators and must not be conflated.
- **Impact:** No project IWF, constituent weight, model or forecast was calculated from the third-party parser, so no model result is affected. The issue was caught before any data import.
- **Correction/guard:** Added the official example as a regression fixture; the arithmetic helper accepts full total share capital and a deduplicated list of unique excluded positions, not percentage rollups. Added a separate 22-item exclusion-coverage check. All tests pass in [run 41269516064](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41269516064).
- **Status:** OPEN as a source-reconciliation gate — verify denominator, share classes and C1/DR treatment against authoritative source records before any IWF reconstruction. No unlicensed source data was fetched.


## E0051 — 2026-11-01 — Partial multi-file create and duplicate retry during public-source proxy implementation

- **Observed:** A batched file-create operation committed some of the requested new proxy artifacts before returning an interrupted/blocked response. A retry against the already-created utility file returned GitHub HTTP 422 because the path existed and the create operation did not include its current SHA.
- **Correction:** Re-read the branch tree and fetched the existing utility/report/aggregate-summary files; verified their contents and blob SHAs. Created the one missing test file separately and then wired it into the workflow.
- **Impact:** No existing file was overwritten, no data artifact was duplicated, and no research calculation was affected.
- **Status:** CLOSED — all expected proxy files were individually read back. Workflow regression run is the next verification step.


## E0052 — 2026-11-01 — BUP-01 plan validator rejected v1.2 due missing version-history line

- **Run:** [41272355566](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41272355566).
- **Observed:** The first v1.2 plan edit changed the registered plan version but the text patch did not add the exact required history marker `- **v1.2 —`. The structural governance workflow correctly failed before running governance tests.
- **Correction:** Appended a controlled v1.2 version-history entry documenting the user's public-source ETF-proxy amendment. No pre-registered statistical thresholds or original outcome definitions were removed.
- **Verification:** Corrected push/PR governance validation is pending; no empirical test or model was run under the failed plan validation.
- **Status:** CLOSED — C0 validation run [41272603916](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41272603916) completed successfully with the corrected v1.2 validator and regression suite.


## E0053 — 2026-11-01 — BUP-01 plan tests still asserted the previous protocol version

- **Run:** [41272427814](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41272427814).
- **Observed:** After the v1.2 validator fix, structural validation passed, but two legacy assertions in `tests/test_constituent_weekly_plan.py` still expected plan version 1.1 and the old stop-rule wording ("Stop at C1").
- **Correction:** Updated the assertions to require v1.2, retain the v1.1 expiry-proxy history, verify the v1.2 ETF-replica amendment, and check the new split between the confirmatory and exploratory gates.
- **Impact:** The plan methodology was not invalid; this was stale regression-test text.
- **Status:** CLOSED — C0 validation run [41272603916](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41272603916) completed successfully with plan v1.2 assertions.


## E0054 — 2026-11-01 — C1 commit fan-out ran C0 governance and duplicated PR/push checks

- **Observed:** On the C1 branch push, the broad phase/constituent-* trigger in constituent-weekly-research.yml ran the C0 registration job (run [41272603916](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41272603916)). This was a successful but semantically misplaced governance run. The offline-regression workflow also listed tests/test_iwf_math.py twice and ran the same suite on both push and PR events. The authorised-source audit likewise ran twice for the same C1 change.
- **Correction:** Restrict the governance workflow push trigger to phase/constituent-weekly-outcomes-c0; make the offline-regression and authorised-source audit workflows PR/manual checks rather than repeated push+PR checks; remove the duplicate IWF test invocation.
- **Impact:** No data, labels or model output was affected. The correction reduces redundant runs and prevents C1 changes from being misrepresented as C0 registration activity.
- **Verification:** Latest pre-correction runs [41272606532](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41272606532), [41272606507](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41272606507) and [41272606502](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41272606502) all succeeded. Corrected workflow validation is pending.
- **Status:** CLOSED — C0 governance trigger is restricted to the C0 branch; subsequent C1 validation runs completed without C0 governance fan-out.


## E0055 — 2026-11-01 — AMC metadata probe workflow omitted pytest

- **Run:** [41274822097](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41274822097).
- **Observed:** Python dependency installation succeeded, but the parser-regression step stopped before source retrieval because the dedicated probe workflow installed requests, BeautifulSoup, pandas and xlrd but not pytest.
- **Correction:** Added pytest explicitly to the workflow dependency install command. The source-probe step will run only after its tests execute.
- **Impact:** No AMC workbook was requested or parsed by this failed run; it does not indicate a source-access or data-availability failure.
- **Status:** CLOSED — subsequent probe resolved and parsed both required recent monthly workbooks.


## E0056 — 2026-11-01 — AMC page rendered archive links not discoverable as ordinary .xls anchors in runner HTML

- **Run:** [41274888924](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41274888924).
- **Observed:** All four parser tests passed. The discovery parser returned no matching links for September 2026, February 2026 or April 2019, although the rendered official AMC archive page lists those monthly portfolio items. No direct workbook request was made in that run.
- **Investigation:** The rendered official page exposes direct download URLs for September 2026 and February 2026; the underlying page response available to the runner does not expose those as ordinary anchor hrefs matching the initial parser's assumptions. The AMC links use a regular month-end filename pattern.
- **Correction:** Retain page discovery when available and add a deterministic month-end URL fallback. The filename pattern is checked against the direct September 2026 and February 2026 download URLs surfaced from the official AMC page. April 2019 remains a candidate to be empirically checked in the next run.
- **Impact:** No holdings workbook was downloaded in the failed discovery run; no data or research result is affected.
- **Status:** FIX COMMITTED — close after the new run's HTTP and schema results are inspected.


## E0057 — 2026-11-01 — AMC workbooks served as XLSX despite .xls filenames; report commit raced with concurrent push

- **Run:** [41274969265](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41274969265).
- **Observed:** The five parser tests passed. September 2026 and February 2026 URLs returned HTTP 200, but the payloads were XLSX containers while the filenames ended in .xls; xlrd correctly rejected those files. The guessed April 2019 URL returned HTTP 404. The workflow created the sanitised report, but its commit push was rejected because another commit had advanced the same C1 branch during the job.
- **Correction:** Detect workbook type by file signature (XLSX ZIP signature -> openpyxl; legacy OLE XLS -> xlrd), install openpyxl in the workflow, and rebase the sanitized report commit onto the latest branch before pushing.
- **Impact:** No constituent holdings values were published. Two recent AMC files are reachable, but schema parsing and the historical URL remain unverified.
- **Status:** FIX COMMITTED — validate in the next probe run; close only after successful schema parsing and a successful report push.


## E0058 — 2026-11-01 — Recent AMC download responses returned unrecognised file signatures

- **Run:** [41275027813](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41275027813).
- **Observed:** Seven offline parser and file-signature tests passed. The September 2026 and February 2026 requests both returned HTTP 200, but the downloaded bytes did not begin with either the XLSX ZIP signature or the legacy XLS OLE signature; the guessed April 2019 URL returned HTTP 404. The metadata probe therefore failed closed before reading workbook contents.
- **Correction/investigation:** Added a browser-style User-Agent, Accept and Referer header; the next run records only response content type, byte count, SHA-256 and the first 12 bytes as hex. No response body, workbook rows or holdings values are emitted.
- **Impact:** No constituent holdings or weights were parsed or admitted. A 200 status alone is not treated as successful file retrieval.
- **Status:** CLOSED — run [41275178244](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41275178244) found valid XLSX ZIP signatures and parsed both recent workbooks.


## E0059 — 2026-11-01 — XLSX signature predicate was double-escaped in the first container-detection implementation

- **Run:** [41275096839](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41275096839).
- **Observed:** The run's report showed content type application/vnd.ms-excel, 1,352,141 bytes and ZIP magic prefix 504b03041400060008000000 for September 2026, and 1,206,358 bytes with the same ZIP prefix for February 2026. Yet workbook_engine rejected both because its Python bytes literal contained double-escaped backslashes rather than the ZIP bytes.
- **Correction:** Replaced string-style signature literals with bytes.fromhex("504b0304") for XLSX and bytes.fromhex("d0cf11e0") for legacy XLS; updated unit fixtures accordingly. The same commit adds the pull --rebase command to the report-commit step (the earlier run used the workflow version before that correction).
- **Impact:** No raw workbook body or holdings values were recorded. The direct archive URL works at the transport layer, but actual schema is still unverified. April 2019 candidate remains HTTP 404.
- **Status:** CLOSED — exact-byte XLSX signature detection passed; E0060 separately tracks the concurrent report-push issue.


## E0060 — 2026-11-01 — AMC probe report auto-commit raced with parallel C1 branch updates

- **Run:** [41275178244](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41275178244).
- **Observed:** The parser and schema probe completed successfully, but the report auto-commit's single git pull/rebase was followed by another C1 branch update before push. GitHub rejected the push because the ref had advanced again.
- **Correction:** The successful sanitised report is committed through the repository Git data API. The workflow publisher is upgraded to bounded fetch/rebase/push retries; it never force-pushes.
- **Impact:** No research result or raw data was lost. The report is now committed at C1; no raw holdings or workbook data are stored.
- **Status:** CLOSED — bounded publisher verified by successful workflow [41275487989](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41275487989); all probe steps and report publication completed successfully without force-push.


## E0061 — 2026-11-01 — Official Nippon archive lower bound was under-reported

- **Observed:** The initial historical archive note said the visible Nippon India monthly portfolio index began in September 2013.
- **Root cause:** The earlier page inspection did not inspect the final older archive lines.
- **Correction:** Re-opened and searched the full rendered official archive. It explicitly lists monthly portfolio files down to 30 September 2012 (lines 555–561 of the source page), including the April 2019 entry elsewhere in the same index.
- **Impact:** The archive discovery range is corrected to September 2012. This does not imply every file in the range is downloadable, legally reusable, or present without gaps.
- **Status:** CLOSED — audit, status, source register and README summaries updated. No model input or empirical data were altered.


## E0062 — 2026-11-01 — AMC metadata probe regression test mixed AMC and scheme records

- **Run:** [41276748532](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41276748532).
- **Observed:** Three of four metadata sanitisation tests passed. One fixture placed both AMC and scheme records in the same list; the generic recursive matcher correctly returned the scheme record for the “Nippon” filter as well, while the test incorrectly expected an AMC-only result.
- **Root cause:** The fixture did not reflect the actual distinct `/amcs` and `/amc/{id}` endpoint payloads.
- **Correction:** Split the test into independent AMC-list and scheme-detail payload fixtures. Keep the recursive matcher unchanged; it is intentionally designed to search nested manifest structures.
- **Impact:** The failure occurred before any network probe. No API data or holdings files were requested, and no source or model result was affected.
- **Status:** CLOSED — follow-up [run 41277022940](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41277022940) passed all 4 tests, fetched the metadata endpoints successfully, and committed the sanitized report. The manifest returned no historical source links; that is a source-discovery outcome, not a test failure.

## E0063 — 2026-11-01 — Membership cross-source regression had an incorrect expected month count

- **Run:** [41289838557](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41289838557).
- **Observed:** The membership comparison reached the assertion that expected 79 monthly observations, but the generated date list contained 103 month-ends.
- **Root cause:** A manual tally was wrong. The period April 2018 through October 2026 inclusive is 103 calendar month-ends; the comparison loop itself covered the full period and found no membership-set differences.
- **Correction:** Changed the regression assertion and test name to 103 month-ends, then reran the full C1 regression suite.
- **Result:** [Run 41289992040](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41289992040) completed SUCCESS. The membership regression and all other tests passed.
- **Impact:** No membership mismatch or data change was found; this was a test expectation/reporting arithmetic error.
- **Status:** CLOSED — corrected test passed in CI.



## E0064 — 2026-11-01 — Double-escaped month regex hid valid YYYY-MM labels in source metadata

- **Observed:** The mfdata month parser used a raw regular expression containing a doubled backslash before the digit token. The regex therefore searched for a literal backslash rather than matching calendar digits.
- **Root cause:** Regex escaping was doubled when the source code was generated or edited; the original test fixture did not expose it.
- **Correction:** Fixed the recursive mfdata month parser. Added month-gap coverage tests and a first/last month extraction check.
- **Validation:** [Actions run 41297143071](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41297143071) passed all 13 metadata/parser tests after the fix.
- **Impact:** This was a date-metadata parsing defect only. The original discovery result contained no admitted holdings values; no historical data were fabricated or modelled.
- **Status:** CLOSED — corrected parser and regression suite passed.


## E0065 — 2026-11-01 — mfdata.in discovery endpoints returned HTTP 522 from hosted Actions runner

- **Run:** [41297143071](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41297143071).
- **Observed:** The documented /api/v1/search, the /api/v1/families catalogue fallback, and the legacy /api/v1/schemes search fallback each returned HTTP 522 with no response body. No family ID was available and the dedicated family holdings-history route was not called.
- **Interpretation:** This is an upstream/gateway timeout for all bounded discovery requests. It is **not** evidence that the service has no NIFTY 50 families or no historical month records.
- **Control:** Three discovery routes only; no repeated polling, no token/secrets use, and no holdings-value endpoint was called. The workflow completed, tested offline logic and committed the sanitised status.
- **Next action:** Leave this source inconclusive. Revisit only when the provider responds from an authorised/reliable network route; do not loop requests. Cross-check another independent AMC archive in parallel if the phase gate requires further progress.
- **Status:** OPEN / EXTERNAL SOURCE ACCESS BLOCKER. No model inputs were admitted.



## E0066 — 2026-11-01 — New mother-source URL tests omitted the private payload-shape import

- **Run:** [41298283454](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41298283454).
- **Observed:** 13 existing tests passed; two newly added tests failed with NameError because the test module called _payload_shape without importing it.
- **Root cause:** The test cases were appended after the import block without adding their helper to that block.
- **Correction:** Import _payload_shape explicitly in tests/test_amcs_fund_metadata.py. No production code or source data were changed by the failed run.
- **Impact:** The metadata API probe was skipped by the workflow's test gate; no live source request was made.
- **Validation:** Follow-up [Actions run 41298336318](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41298336318) completed SUCCESS; the offline metadata-sanitisation tests, live metadata probe, job summary and sanitized report commit all completed.
- **Status:** CLOSED — missing import fixed and workflow rerun passed.



## E0067 — 2026-11-01 — v1.3 plan regression fixtures retained two obsolete strings

- **Runs:** [41299407476](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41299407476) and [41299414057](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41299414057).
- **Observed:** The shared offline regression step reported 43 passed and 2 failed. Both failures were assertion text mismatches: the membership bullet begins with a capital letter, and the legacy assertion expected the v1.2 phrase "exploratory gate" after v1.3 had retired the ETF proxy path.
- **Root cause:** Unit-test strings were not aligned with the final v1.3 wording; no mathematical, data, authentication or prediction-code failure was observed.
- **Impact:** The Dhan live test step was correctly skipped because its preceding offline test gate failed. These runs do **not** indicate a Dhan authentication/API failure.
- **Correction:** Updated assertions to match the current plan wording and to check the explicit v1.3 exclusion of historical free-float/ETF weights from the active gates.
- **Status:** FIX COMMITTED — awaiting automatic offline validation.


## E0068 — 2026-11-01 — C1 continuous coverage auditor first-pass corrections

- **Status:** FIX COMMITTED — validate in offline regression workflow.
- **Issues found during resumed review:** the new test module contained invalid Python identifiers beginning with digits; the member-fraction calculation divided a list by an integer instead of dividing its length; the accepted-cycle counter retained an old field name; the output printer retained stale variable names after refactoring; and partial target-day results were being marked cache-complete.
- **Corrections:** use legal test names; calculate member fraction as len(valid_members)/member_count; require 104 prior accepted coverage cycles; print from the canonical summary dictionary; mark a chunk cache-complete only when every requested target date passes; respect the Dhan five-year floor with its one-day margin; explicitly flag HDFC Ltd merger and Tata Motors demerger target-crossing cycles for exclusion from the coverage-eligible panel.
- **Important distinction:** the coverage audit reports data availability separately from complete corporate-action treatment. A passing data-coverage gate does not itself pass C1 identity/action governance or authorise C2 modelling.


## E0069 — 2026-11-01 — Canonical membership ticker differed from point-in-time exchange symbol (LTIM/LTM)

- **Observed:** The project membership ledger stores the LTIMindtree NIFTY 50 interval 2023-07-13 to 2024-09-30 under canonical symbol LTM, but the exchange-traded symbol during those dates was LTIM. NSE circulars confirm LTIM→LTM effective only 2026-02-27.
- **Root cause:** The canonical membership source normalizes rename chains to the terminal/current symbol; it is not by itself a point-in-time traded-ticker ledger.
- **Correction:** Added security_alias_history.csv, security_corporate_action_events.csv and a tested point_in_time_symbol() resolver. The resolver maps canonical LTM to actual LTIM for dates before 2026-02-27, and records other major symbol changes and action events.
- **Impact:** The C1 data coverage audit still requests the current LTIMindtree instrument using the current security ID, which resolves the same listed security. The correction is needed for point-in-time feature panels, provenance and historical labels. No model or stock return label was trained on the incorrect alias.
- **Validation:** [Actions 41302695594](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41302695594) passed 61 tests including the new alias regressions.
- **Status:** CORRECTED FOR C2 IDENTITY RESOLUTION; exhaustive corporate-action/adjustment audit remains OPEN.


## E0070 — 2026-11-01 — C1 intraday coverage passed but publication rebase conflicted

- **Run:** [41301447865](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41301447865).
- **Observed:** Dhan audit completed SUCCESS and reported 258/258 valid NIFTY target pairs; 258/258 stock coverage cycles met the 47 / at least 94% gate; 154 confirmatory cycles after warm-up; zero unresolved active symbols; 1,083 requests across 21 windows. The final explicit gate step printed PASS.
- **Failure point:** The later git pull --rebase conflicted on STATUS.md and RESEARCH_LOG.md due concurrent C1 commits.
- **Artifact issue:** No Actions artifact upload step existed, so per-cycle/per-symbol QA was not retained. Logs preserve aggregate counts and the partial-window caveat.
- **Correction:** A durable summary JSON/report is committed. The workflow now uploads sanitized artifacts before publication and regenerates status/logs from the latest branch with bounded retries.
- **Impact:** Intraday target-data sub-gate PASS; C1 overall remains NOT PASSED pending daily OHLCV feature history and full corporate-action adjustment validation.
- **Status:** DATA RESULT RECORDED; publisher fix committed for next validation.


## C1 daily OHLCV coverage audit — 2026-11-01T12:47:45.759152+00:00

- **Status:** PARTIAL_OR_BLOCKED_RUNTIME_ERROR.
- **Sanitized failure category:** NameError.
- **Requests completed:** 1.
- **Impact:** daily feature-source coverage remains unproven; C2 is not unlocked.

## E0072 — 2026-11-01 — Daily audit regression fixture/dependency corrections

- **Observed:** The combined offline suite ran after the daily-auditor syntax correction: 84 tests passed and 3 failed.
- **Causes:** the common offline workflow did not install `cryptography`, required by the AES-GCM cache test; the synthetic NSE fixture incorrectly counted a BE-series row as EQ; and the test module omitted the `Path` import.
- **Corrections:** install `cryptography` in the common offline workflow; count only the matching ticker and EQ series in the fixture expectation; add the missing `Path` import.
- **Interpretation:** these were test harness/fixture defects, not evidence of a live data-source failure. No live TejHQ/HDFC fallback result is claimed until the corrected test gate passes.

## E0073 — 2026-11-01 — Earlier incomplete intraday coverage summary superseded by full artifact

- **Observed:** The interim result JSON retained a prior incomplete run summary (77/258 NIFTY targets; 64 accepted cycles) even though a later full run had been uploaded as a sanitized artifact.
- **Evidence:** Full run [41309632317](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41309632317), artifact 13086220727, contains all 258 cycle results and date-level index chunk QA. It reports 258/258 NIFTY target pairs and 258/258 stock-input cycles accepted; 154 confirmatory cycles after warm-up; 98% minimum member coverage; zero unresolved active symbols; and 1,083 requests.
- **Partial-window root cause:** 2024-04-26's 15:14 check failed while its 10:00 anchor passed. 26-Apr was an anchor-only date for the cycle ending 2024-05-02; the actual 2-May expiry proxy passed. The generic 15:14 check on every day in the 90-day window incorrectly made the window appear partial for a date that was not an expiry target.
- **Correction:** Updated the authoritative result JSON, coverage report, status and README to identify the later full artifact as current evidence. The earlier 77/258 run remains historical evidence but is superseded.
- **Impact:** Intraday target-data sub-gate PASS. Overall C1 remains NOT PASSED pending daily OHLCV gap resolution and exhaustive corporate-action/adjusted-return validation.

## E0074 — 2026-11-01 — Daily fallback residual-date diagnostics were stale or incomplete

- **Observed:** The live daily audit completed with 106,385/106,392 valid member sessions (99.9934%). HDFC received 1,295 valid TejHQ fallback sessions, leaving six missing sessions, but its displayed missing-date sample still showed the first 20 Dhan-unavailable dates. The TATAMOTORS cross-check reported only 2/3 dates checked and matched, without identifying the missing comparison date.
- **Root cause:** The fallback merge updated the residual missing count but did not recompute its date sample after accepted fallback rows. The cross-source comparator retained only aggregate match counts and omitted per-source date-presence diagnostics.
- **Correction:** Recompute exact residual date samples only when the source sample is complete; preserve an explicit incomplete marker when it is truncated. Emit sanitized date-only Dhan/TejHQ presence and missing-date arrays for cross-source comparisons. Keep Tata acceptance strict: every registered comparison date must have one row from each source and match; no bar is inferred or inserted when the comparison is incomplete.
- **Validation:** Added regression tests for post-fallback residual dates, truncated missing-date samples and date-only Tata source diagnostics. The next daily workflow rerun is the live validation.
- **Impact:** Reporting/diagnostic correction only. The 99.9934% first audited coverage remains provisional pending exact residual-date review; no stock label, model or trading strategy is changed, and C2 remains gated.


## E0075 — 2026-11-01 — Encrypted TejHQ cache path mismatch

- **Observed:** Consecutive daily audits re-downloaded all seven TejHQ annual NSE partitions and reported zero encrypted cache hits, despite successful Actions cache restore/save steps.
- **Root cause:** The configured cache path contained a literal leading `~`. Python `Path()` does not expand that token, so the audit wrote encrypted files to a relative directory while GitHub Actions cached the runner's home-directory path.
- **Correction:** Added `resolve_tejhq_encrypted_cache_dir()` using `Path.expanduser().resolve()` and a regression test for both home-relative and explicit absolute paths.
- **Validation:** Commit [021aac8](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/commit/021aac89ce7d26d808e53fffc79fd7c1037ac669) triggered run [41317402483](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41317402483). The first corrected run had no previous cache to restore, downloaded seven partitions and successfully saved the encrypted cache (87,911,829 bytes) under the pinned revision/run-specific key. A subsequent run must confirm nonzero cache hits before reuse is declared verified.
- **Impact:** No market-data values or daily coverage counts changed. This is a repeat-download/cache-location defect; raw market rows and credentials were not committed.


## E0076 — 2026-11-01 — First corporate-action cache was cold, not a path failure

- **Observed:** The corporate-action workflow restored the existing daily-history cache successfully but reported zero action-partition cache hits and downloaded nine annual action partitions.
- **Root cause:** The restored daily cache contained the seven raw NSE equity bhavcopy partitions, not the separate `actions/nse_YYYY.parquet` corporate-action partitions. The action-specific cache entries did not exist yet. The corporate-action run then saved its nine encrypted action partitions to its own run-keyed cache entry.
- **Correction:** No code-path correction was needed for this first action-cache miss. The daily and corporate-action workflows use the same absolute `${{ runner.temp }}/bup01-tejhq-encrypted` directory, and both use the same revision-scoped restore prefix. Added an encrypted action-partition round-trip regression to prove that a first call downloads/encrypts and a second call decrypts/reuses without downloading again.
- **Validation:** Corporate-action run [41319736877](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41319736877) restored the cache created by 41318960367 and reported 9/9 yearly action partition hits; zero action partitions were downloaded. Its 13/13 action/identity tests also passed. Cache reuse is now verified.
- **Impact:** No event counts, market values or labels changed. This is cache warm-up, not a data-integrity failure.

## E0077 — 2026-11-01 — Corporate-action catalogue is not an adjustment ledger

- **Observed:** The first pinned NSE candidate catalogue found 18,393 rows (18,361 deduplicated), including 711 point-in-time constituent-symbol matches.
- **Risk:** Treating source labels as confirmed events or applying a generic factor could corrupt return targets, particularly for rights, merger/demerger, buyback and extraordinary dividends. NSE's listed F&O contract-adjustment rules are not a universal total-return adjustment recipe for cash-equity historical features.
- **Correction/guard:** Keep all factors unapplied. Require per-event exchange/issuer confirmation, event terms, ISIN/security identity, effective/ex-date, prior raw close and event-family-specific formula checks. Rights must use TERP inputs; merger/demerger must be scheme-specific; buybacks remain event features, not mechanical scale factors.
- **Validation:** Candidate catalogue workflow [41318287855](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41318287855) succeeded; corporate-action gate remains NOT PASSED.
- **Impact:** No stock label or target was adjusted. C2 remains locked.


## E0085 — 2026-11-02 — Special-session calendar classification risk
- Severity: Medium / data-calendar QA.
- Observation: Seven residual daily OHLCV gaps were reported without a linked special-session calendar classification.
- Cause: The coverage report exposed date-level gaps but not the exchange session type and hours. Ordinary daytime assumptions are unsafe for Muhurat dates and exceptional Saturday Budget sessions.
- Evidence and correction: NSE circulars confirm all seven dates were genuine exchange trading sessions. The dated reconciliation is recorded in `research/constituent_weekly/C1_SPECIAL_SESSION_CALENDAR_RECONCILIATION.md`. All seven dates remain in the expected-session denominator; no value was imputed and no gap was waived.
- Follow-up: independently obtain and validate each security/date bar, or document a pre-registered evidence-based exclusion. No model data or labels were changed.

## E0086 — 2026-11-02 — Special-session audit parser precheck failed
- **Severity:** Medium — audit execution blocked before external data retrieval.
- **Run:** [41340624209](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41340624209).
- **Symptom:** Five parser tests passed; the ISO-date UDIFF test failed because pandas with `dayfirst=True` interpreted an ISO string ambiguously, causing the target row to be missed. The live market-data query was skipped, so this run produced no bar-level finding.
- **Root cause:** The normalizer applied day-first parsing to both ISO (YYYY-MM-DD) and day-month text dates.
- **Correction:** Split ISO dates from non-ISO dates and parse the ISO subset with explicit `%Y-%m-%d`; retain day-first parsing only for exchange text formats. Add the regression assertion and make artifact/publish steps success-gated so precheck failures do not create cascading publish failures.
- **Status:** Correction committed; rerun required. No prices were changed, no missing bars were imputed, and no coverage credit was granted.
- **Prevention:** Keep regression tests for legacy CM, modern sec_bhavdata_full and UDIFF date schemas; require offline tests to pass before any network request.

## E0087 — 2026-11-02 — Independent-source calendar coverage limitation

- Class: Data-source coverage limitation, not a market-data disagreement.
- Observed: pinned independent NSE bhavcopy mirror returned 4/7 valid exact-date EQ OHLCV rows; 3 dates had no EQ row in that mirror.
- Limitation: the mirror collector enumerates weekdays only. It cannot prove absence for Sunday 2019-10-27 or Saturdays 2020-02-01 / 2020-11-14, all genuine special sessions.
- Correction: treat mirror no-row as INCONCLUSIVE; retain all seven dates in the denominator; use a source with explicit special-session capture for remaining dates. No price was imputed.
- Impact: no change to 106,385/106,392 daily coverage. C1 remains PARTIAL and C2 remains gated.

## E0088 — 2026-11-02 — Direct NSE legacy bhavcopy parser used the wrong trade-date column

- **Class:** Parser/schema mismatch; corrected before accepting the direct-NSE result.
- **Observed:** Initial exact-date audit reported zero HDFC rows for three special sessions despite successfully downloading valid NSE ZIP/CSV archives.
- **Cause:** Legacy CM bhavcopy headers use `TIMESTAMP` and `OPEN/HIGH/LOW/CLOSE`; the first parser expected `DATE1` and modern `*_PRICE` names. The OHLC fallback already supported legacy price columns, but the date parser did not read `TIMESTAMP`.
- **Correction:** Parse `TIMESTAMP` as a supported trade-date field; rerun the exact three archives; verify one EQ row, OHLC invariants, nonnegative volume and matching ISIN per date.
- **Outcome:** 3/3 direct NSE rows validated. The earlier 0/3 result is superseded and must not be used. Parser fix is committed; the expanded official-NSE audit subsequently validated 7/7 residual sessions.
- **Impact:** No raw values were published. Original Dhan/TejHQ coverage remains unchanged until supplemental encrypted-cache integration.

## E0089 — 2026-11-02 — Encrypted direct-NSE cache writer imported project module without its runtime dependencies

- **Class:** Workflow dependency omission; corrected.
- **Observed:** Initial cache-enhancement run failed with `ModuleNotFoundError: pyotp` while importing the shared encryption helper from the daily-history module.
- **Correction:** Removed the heavy module import and implemented the exact same AES-GCM key derivation locally (`SHA-256` over the established BUP01 cache-key prefix plus the HF token), preserving compatibility with the shared cache format. The workflow now installs only requests and cryptography.
- **Verification:** Rerun [41343953567](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41343953567) succeeded, restored the prior encrypted cache, validated 3/3 direct NSE rows, wrote the supplemental encrypted CSV cache, and saved the new cache key.
- **Impact:** No raw data or token was committed. Cache persistence and daily feature-panel merge are now complete. Successful daily run 41344197015 reports 106,392/106,392 valid OHLCV sessions.



## E0090 — 2026-11-02 — C2 offline regression used a too-strict Brier boundary

- **Run:** [41347512132](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41347512132).
- **Observed:** Five C2 offline tests passed; the metric test failed because the fixture's exact Brier score was 0.10 while the assertion required strictly less than 0.10.
- **Root cause:** Test expectation used a strict inequality at an exact mathematical boundary; the model metric calculation was correct.
- **Correction:** Changed the fixture assertion to accept a Brier score equal to 0.10. No model logic, input data or prediction target was changed.
- **Status:** FIX COMMITTED; automatic rerun [41347616436](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41347616436) is in progress.


## E0091 — 2026-11-02 — C2 encrypted-cache writer dependency was absent

- **Run:** [41347616436](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41347616436).
- **Observed:** C2 authentication and the 258-cycle calendar build succeeded, then execution stopped with ModuleNotFoundError in the shared AES-GCM cache helper.
- **Root cause:** The workflow installed project and live API requirements but neither dependency set included `cryptography`, required by AES-GCM cache writes.
- **Correction:** Add `cryptography>=42` to the workflow install command. The updated run [41347849285](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41347849285) passed offline tests and entered live model-data acquisition.
- **Impact:** No model fitting occurred in the failed run. No raw data or credentials were published.

## E0092 — 2026-11-02 — C2 output publisher lost a push race

- **Run:** [41347616436](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41347616436).
- **Observed:** The model step wrote a sanitized failure report, but publication was rejected because a separate error-log commit advanced the branch during the job.
- **Root cause:** The initial publisher committed against its checkout snapshot and had no fetch/rebase/rebuild retry loop.
- **Correction:** Replaced it with `publish_c2_run.py`, which snapshots generated outputs, fetches the latest branch, reapplies outputs/status/log updates and retries non-forced pushes up to five times. A follow-up correction deletes stale prior-run outputs before a new execution.
- **Status:** CORRECTED IN C2 WORKFLOW; retry-safe publisher is used by current run [41347849285](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41347849285).


## E0093 — 2026-11-02 — C2 index-feature reader did not match the official daily CSV schema

- **Detected during:** Static contract review of the C2 runner against `data/reconciliation/nifty50_official_daily.csv`.
- **Observed:** The source schema uses `official_open`, `official_high`, `official_low`, `official_close`; the first C2 feature function expected bare `open/high/low/close` names.
- **Root cause:** The new C2 reader did not reuse the source's canonical field aliases.
- **Correction:** Added explicit support for both source-native `official_*` fields and generic OHLC fields; added an offline regression using the exact official header.
- **Status:** FIX COMMITTED in 76c2c47 and 780f214. Current in-flight run [41347849285](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41347849285) uses the pre-fix checkout and may stop at the feature-reader gate; the queued corrected run [41348608291](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41348608291) contains the corrected reader and regression.
