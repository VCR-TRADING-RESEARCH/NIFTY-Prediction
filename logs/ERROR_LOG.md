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


## E0019 — 2026-10-26 — Anchor audit timestamp-match statistic invalid due timezone mismatch
- Severity: Moderate — the first report understated timestamp matches because the comparison did not normalize timestamp timezone representations.
- Finding: primary archive timestamps were timezone-aware Asia/Kolkata timestamps; the secondary archive parser left timestamps timezone-naive even though its data convention is local IST. Comparing the values yielded zero exact timestamp matches, which was not a valid inference about candle timestamps.
- Correction: normalize both timestamp series to timezone-aware Asia/Kolkata before comparison; add regression tests that naive IST and timezone-aware IST timestamps compare equal.
- Corrected result: 1,269 / 1,269 overlapping session anchor timestamps match. Anchor-open difference median 0.05 points, P95 1.00, max 6.70; 62 of 1,269 daily anchors differ by over 1 point.
- Weekly sensitivity result: 265 weekly rows overlap the secondary archive; recalculating direction with the same expiry close and secondary anchor produced zero label switches. This is diagnostic only because the second archive's provider lineage is not verified.
- Prevention: future anchor audit workflows run focused tests before data work and delete prior report outputs before the next run to avoid accidentally reusing stale results.
- Remaining blocker: no exchange-grade independent anchor validation for the full label history; broader daily OHLC disagreements remain unresolved. No new model should be trained until the source gate is accepted.
- Security: no credentials, API tokens, PIN, TOTP values or raw Dhan provider responses are stored in Git.


## Phase 9 Dhan historical anchor audit — run 40279493086 — 2026-10-26T06:24:56.225852+00:00
- Status: ERROR.
- Window: {}.
- Counts: {}.
- Difference summary: {}.
- Weekly label sensitivity: {}.
- Dhan source chunks are cache-only; credentials and response bodies are not recorded.
- Interpretation: this is diagnostic evidence only; source conflicts do not pass the confirmatory gate.


## Phase 9 Dhan historical anchor audit — run 40279800889 — 2026-10-26T06:26:58.935386+00:00
- Status: ERROR.
- Window: {}.
- Counts: {}.
- Difference summary: {}.
- Weekly label sensitivity: {}.
- Dhan source chunks are cache-only; credentials and response bodies are not recorded.
- Interpretation: this is diagnostic evidence only; source conflicts do not pass the confirmatory gate.


## Phase 9 historical anchor source audit — run 40279815377 — 2026-10-26T06:27:51.168462+00:00
- Status: DIAGNOSTIC_ONLY (diagnostic only).
- Counts: {"anchor_open_mismatches_over_1_point": 62, "exact_timestamp_matches": 1269, "overlap_sessions": 1269, "primary_anchors": 1269, "secondary_anchors": 1271}.
- Difference summary: {"max": 6.700000000000728, "median": 0.049999999999272404, "p95": 1.0}.
- Caveat: secondary archive provider lineage is unverified; this comparison cannot pass the official independent-anchor gate.
- Output: data/reconciliation/anchor_source_comparison.csv and anchor_source_comparison_report.json.


## E0020 — 2026-10-26 — Phase 10 manuscript renderer displayed missing source metrics
- Severity: Moderate — the machine-readable dataset report and holdout metrics were correct, but the generated manuscript's data-quality summary read some values from the wrong JSON nesting and displayed "n/a".
- Finding: official daily-session counts are under official_daily_quality; weekly row-gate counts are under row_source_gate; holdout boundary dates were in the split manifest but were not copied into the top-level summary.
- Correction: the report renderer now reads the nested data-quality fields and the summary now records the exact first/last holdout expiry dates. The data-quality construction summary now reconciles its legacy pre-Dhan confirmatory flag with the Phase 10 row-level source gate and states the correct Dhan-backed source semantics.
- Regression prevention: added a test asserting official session counts, source-gate counts and holdout dates are rendered, rather than left as missing values.
- The fixed model result remains unchanged: base ExtraTrees balanced accuracy 0.5485 versus augmented ExtraTrees 0.5379 on the 52-row locked holdout; bootstrap 95% interval for the difference spans -0.0500 to +0.0344. The augmented method does not pass the pre-registered screen.
- Trading acceptance remains BLOCKED; no contract-level futures/options P&L with dated Paytm Money costs, bid/ask spread, slippage and conservative fills was performed.
- Security: no Dhan credentials, tokens, PINs, TOTP values or provider response bodies are logged.


## 2026-10-26 — Phase 10 workflow publication errors (runs 40282004301 and 40283034584)

- Error 1: Run 40282004301 completed tests, authenticated Dhan history retrieval and model evaluation, but the final reporting step failed with a Python SyntaxError because an inline shell/Python heredoc boundary was parsed incorrectly.
- Correction: Extracted the reporting logic to scripts/record_phase10_outcome.py and invoked it as a standalone script.
- Error 2: Run 40283034584 completed tests, data retrieval and model evaluation, then failed at the Git push step with fatal: invalid refspec due to literal backslashes before the GitHub Actions branch-name expression.
- Correction: Removed the literal backslashes from github.ref_name and step outcome expressions in .github/workflows/phase10-dhan-verified-dataset.yml.
- Impact: Both runs produced the same research metrics; the failure was in publishing generated files/logs, not model fitting. A prior run (40282667293) successfully committed the result summary and outputs. No credentials or provider response bodies were logged.
- Prevention: Keep outcome reporting in a standalone Python file; validate workflow expressions and refspecs before rerunning; check both the job conclusion and the presence/contents of the committed result summary.
