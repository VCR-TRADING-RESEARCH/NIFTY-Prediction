# Visible conversation decisions

## 2026-10-25
- User clarified the required deliverable: a page that predicts the upcoming NIFTY expiry using the ExtraTrees Classifier and a selectable as-of date.
- Assistant acknowledged that a prediction CSV/backtesting configuration was not the requested deliverable.
- User approved proceeding.
- Implementation decision: provide a GitHub Pages reporting UI backed by published prediction records; use strict unavailable state when model/data prerequisites are missing. Do not record hidden reasoning or internal chain-of-thought.


## 2026-10-25 — Continued integration after user approval
- User again approved proceeding to finish the as-of-date ExtraTrees expiry prediction page.
- Repository inspection found an existing research-backed forecast payload and exporter on the research/phase-6-prediction-pages branch. The latest saved forecast was as-of 2026-10-21 10:00 IST for candidate expiry 2026-10-27, direction DOWN, p_up approximately 0.3848; source gate blocked.
- Corrective decision: integrate the existing walk-forward exporter, page JavaScript/CSS, JSON payload, research pipeline, data artifacts, tests and workflows rather than maintain a duplicate stub.
- Visible conversation decisions only; hidden chain-of-thought is not stored.

## 2026-10-25 — Live inference requirement clarified
- User clarified the desired behavior: on clicking Predict, refresh the Dhan token, fetch the NIFTY data required through the chosen as-of date from Dhan API, run the ExtraTrees classifier, and show that newly computed prediction.
- Decision recorded: keep credentials on a server-side inference service; GitHub Pages must not contain Dhan/GitHub/Hugging Face secrets. Static CSV/JSON lookup was not acceptable as the Predict action.
- Implementation branch: `phase/live-dhan-inference`. See [Phase 7 plan](../docs/PHASE_7_LIVE_DHAN_INFERENCE.md).
- Only visible conversation decisions and engineering rationales are logged; hidden private chain-of-thought is not stored.

## 2026-10-25 — Live service provider blocker discovered
- Deployment workflow reached Hugging Face Space creation, then received HTTP 402. Current Hugging Face docs state Docker/Gradio CPU-basic Spaces require an individual Pro subscription or Team/Enterprise for organizations. Static GitHub Pages cannot securely hold the Dhan PIN/TOTP secret or execute Python, so direct browser-only fallback is not safe.
- A follow-up deployment-script diagnostic bug (temporary directory variable shadowing the stage label) was corrected and logged as E0009; the next run reconfirmed HTTP 402 at the Space-creation stage.
- User intervention is now required to provide eligible Hugging Face compute or point `HF_SPACE_ID` at an existing writable, eligible Docker Space. No secrets are copied into the page or repository logs.


## 2026-10-25 — Alternative backend approved
- User approved proceeding with a secure alternative backend while keeping GitHub Pages as the front end.
- Decision: do not place Dhan PIN/TOTP in the browser or use a publicly callable GitHub Actions trigger. Current Hugging Face provisioning is blocked by HTTP 402; no other host deployment credential is available in the repository workflow configuration.
- Next actionable prerequisite: eligible existing Docker Space ID or a credential for a host such as Render/Cloudflare. Then deploy, test live Dhan auth/history, and verify browser result rendering.


## 2026-10-25 — GitHub Actions execution approved
- User approved proceeding with a design where the Pages Predict action runs Python in GitHub Actions.
- Implemented a prefilled, authenticated GitHub issue request as the secure trigger; GitHub Actions executes the existing Dhan-backed ExtraTrees pipeline, and Pages polls for a newly generated date-specific JSON result. The workflow has owner/member authorization checks and a manual dispatch input.
- Explicit limitation: because static Pages has no private credentials, the user must submit the prefilled request in GitHub after clicking the request link. No browser token or Dhan secret is exposed.
- The workflow and frontend are not yet live-verified. Keep status transparent until CI, permissions, Pages publication and Dhan inference succeed.


## 2026-10-25 — GitHub Actions workflow validation and smoke test
- PR #8 implemented the Actions inference path and merged after CI passed; PR #10 broadened the authorized issue-trigger gate and added retry support, also after CI passed.
- A controlled request issue #9 was opened and reopened to test the real event path. At the latest inspection, no completion comment or result JSON was visible, so the live Dhan workflow is not yet verified end-to-end.
- Visible decisions and test status are logged; no hidden chain-of-thought is recorded.


## 2026-10-25 — Diagnosed first actual Dhan request
- The first non-skipped workflow reached inference but wrote a failure record: HTTP 405 during Dhan token generation. Official docs show the endpoint requires POST, while the code used GET.
- Corrected method, added a mocked regression test, and changed runner exit status so failures fail the inference step. Triggered a retry by editing request issue #11. Run [40201653154](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40201653154) was in progress at latest check.
- A separate Actions cache write-scope warning was observed and is not considered solved. No successful forecast claimed yet.


## 2026-10-25 — First fresh live prediction completed
- Fixed the Dhan token-refresh HTTP method (GET to POST) based on official DhanHQ docs, added a mocked regression test, and made inference failures return a non-zero process exit.
- Retry run [40201653154](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40201653154) succeeded and wrote the live result for 2024-09-20: UP, raw UP score 51.3%, target expiry 2024-09-26, 147 training labels, 268,510 minute bars, training through 2024-09-19.
- This confirms the Dhan-backed Python/Actions/Pages publication path can produce a fresh result. The source-quality gate remains BLOCKED because the 10:00 anchor is not independently reconciled and costs/options P&L are not validated. It is historical, not a current signal.
- The Pages UI opens a prefilled GitHub issue link and requires submitting it; this remains a usability limitation. The result should appear in the original Pages tab that is polling, after the workflow publishes.


## 2026-10-25 — Result deep link added
- Added `?as_of_date=YYYY-MM-DD` support to the Pages predictor so a completed date-specific JSON result can be opened directly without generating another request. The Actions completion comment now links back to that exact result page.
- Pages deployment for the deep-link JavaScript passed in run [40201836007](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40201836007). A later documentation deployment was still running at latest inspection.
- Direct historical result link: https://vcr-trading-research.github.io/NIFTY-Prediction/?as_of_date=2024-09-20. External browser verification of the rendered page was unavailable; the JSON record and deployment run are verified.


## 2026-10-31 — User requested resume; BUP-01 C1 checkpoint
- User asked to resume the ongoing BUP-01 constituent-level weekly-expiry research.
- Reviewed existing C1 plan/status, source register, feasibility note, README, research/error logs, and the latest relevant GitHub Actions evidence.
- Reported and recorded: offline source audit run 41181684637 passed; Dhan preflight run 41181684573 had 9/9 offline tests pass but live profile HTTP 401; token-refresh PR #28 checks pass but PR remains draft/open; licensed membership candidate is not a weight series and is stale after 2025-09.
- Updated C1 status and README. No private reasoning or credentials are stored; this log records the visible decision and outcomes only.

2026-10-31 — Dhan profile authentication diagnostic follow-up

- Continued the BUP-01 C1 resume after the Dhan preflight returned HTTP 401.
- Aligned the profile request with Dhan's documented access-token-only header and added a regression test.
- Latest Actions run 41181948126 passed 10/10 offline tests; live token generation returned HTTP 200 without an accessToken field and the fallback token was rejected by profile with HTTP 401.
- Updated STATUS.md, README.md, ERROR_LOG.md and RESEARCH_LOG.md. This is a visible-outcome summary only; credentials and private reasoning are not stored.

2026-10-31 — PR #28 review state updated

- After its mocked Actions checks passed, PR #28 was marked ready for review. GitHub reports `mergeable_state=dirty`, so it was not merged. No direct main-branch bypass was used.


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

## 2026-10-31 — User approved continuation of BUP-01 C1
- User said “Ok Proceed”.
- Re-read the C1 status, Dhan preflight JSON, source register, research/error/conversation logs, operating rules, pre-registered research plan and relevant workflow on the C1 branch; checked the corresponding main README state.
- New source review: official NIFTY methodology/IWF guidance, NSE website Terms of Use and Dhan v2 historical-data documentation. Confirmed IWF is more complex than ownership roll-ups; NSE website terms create a rights gate for automated scraping/simulation; Dhan intraday history is documented for active instruments only and is queried in 90-day windows.
- Decision: do not repeat TOTP refresh without a meaningful reason; keep NSE scraping disabled; keep C1 BLOCKED and C2 gated. Record only visible decisions and outcomes, not hidden private reasoning or secrets.

## 2026-10-31 — User approved continued BUP-01 C1 source audit
- User said “Ok proceed”.
- Re-read project instructions, phase plan, status, preflight JSON, source register and available branch logs before continuing.
- Discovered CC BY 4.0 NIFTY 50 point-in-time membership data. Extracted 83 upstream NIFTY 50 intervals; the source ends at 2025-09-30 and has no numeric weights. Applied the official 2026-09-30 replacement (WIPRO out, BSE in) from the NSE Indices press release dated 2026-08-10.
- Validated half-open intervals against 103 month-end snapshots from 2018-04 through 2026-10: all dates had 50 unique members. Added a provenance note, machine audit JSON and regression tests. This is a membership/cardinality check, not independent transition verification.
- Identified the official NSE Indices historical data subscription as an exact-weight/identifier path but requiring licensing. Free public weights candidates were either non-commercial or subject to upstream terms; binary weights are not official IWF.
- Decision: membership sub-gate PASS WITH LIMITATIONS; overall C1 remains BLOCKED; no model training. Only visible decisions/outcomes are recorded, not hidden reasoning or secrets.

## 2026-10-31 — BUP-01 membership validation automation
- Added `bup01-c1-membership-tests.yml` with automatic push/path and pull-request triggers plus a manual Actions dispatch button. It runs only local membership integrity tests and does not call Dhan or scrape NSE.
- Added an audit-JSON consistency test. The code and data files are committed on the C1 branch; workflow outcome must be inspected before labelling CI as passed.


## 2026-10-31 — Conversation recovery and continuation
- User shared a screenshot of a ChatGPT send/response failure while the prior conversation displayed repeated audit/provenance/validation update operations.
- Assistant advised retrying safely and verifying GitHub state rather than assuming the displayed operations had committed.
- User said “Ok Proceed”.
- Recovery action: checked the main README, main research/error/conversation logs, available branches, BUP-01 C1 status and membership workflow definition. Verified Actions run 41185169548 directly; it completed successfully with six tests passing.
- Decision: do not repeat completed membership work or trigger another Dhan token request. Membership sub-gate PASS WITH LIMITATIONS; overall C1 BLOCKED; C2 remains gated by licensed exact IWF, security identity/corporate actions and complete constituent price coverage.
- Only visible conversation statements and auditable decisions are recorded; hidden private reasoning is not stored.


## 2026-10-31 — Recovery continuation: bounded C1 source audit
- After verifying membership CI success, performed a bounded search of official NSE Indices, Dhan documentation, Hugging Face and public GitHub datasets for exact historical IWF, identifiers and constituent price coverage.
- Found official historical weights/identifiers are a licensed NSE Indices subscription product; the HF dataset is CC BY-NC-SA 4.0; the GitHub alternative explicitly uses equal-weighted/binary approximations; Dhan minute history is documented for active instruments, not guaranteed inactive/delisted constituents.
- Updated main README, research log and error log with the source audit and retained C1 BLOCKED / C2 gated. No Dhan token refresh, market-data call, panel build or model fit was initiated.


## 2026-10-31 — User confirmed Dhan as the data source
- User replied “Dhan” to the question about available historical data access. Interpreted as confirmation to use the existing Dhan Data API subscription as the primary constituent price-data route, not as confirmation that Dhan supplies official historical NIFTY IWF.
- Decision: Dhan-first, cache-first constituent security-ID and historical OHLCV coverage audit; include active and delisted/inactive symbols, anchor bars and expiry-close bars. Use bounded/serialized calls and avoid unnecessary TOTP refreshes. Keep credentials in Actions secrets.
- Exact official point-in-time IWF, index membership/identity history and full coverage remain separate acceptance gates. No approximate weights and no C2 model until gates pass.

## 2026-10-31 — User said “Proceed”: Dhan full-universe security master audit
- Re-read the C1 status, source register, Dhan preflight code/workflow, membership ledger, research/error/conversation logs and README before continuing.
- Added full current-universe and historical-symbol resolution against the Dhan current scrip master; added tests for the 50-member effective-date universe, BSE/WIPRO transition, DUMMYTATAM exclusion and generic multi-symbol resolution. Updated status reporting.
- Commit 05b71dc111779ef40da748319f7d109a012c4451 was validated by Actions run [41223379333](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41223379333): 13 tests passed. The run was a PR event, so the live Dhan step was skipped by the explicit credential-safety guard.
- A follow-up contents commit 8c71118461b3a047ef258bd3345e109423ee8440 synchronized the push-trigger path; the observed run remained PR-triggered. No fresh TOTP, profile or price request was made in this step.
- Decision: full-universe resolution is implemented but not yet measured. Manual workflow_dispatch on the C1 Dhan workflow is the remaining protected live action. Do not infer coverage from offline tests. C1 remains BLOCKED and C2 remains gated.

## 2026-10-31 — User asked ChatGPT to run the protected Dhan workflow directly
- Initiated the existing push-triggered, secret-backed Dhan preflight on the C1 data branch after the user requested that ChatGPT run it rather than asking the user to click Run workflow.
- Latest successful run: [41224048773](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41224048773). TOTP refresh/profile authentication succeeded; Dhan Data API plan active; offline tests 13/13.
- Live findings: current active NIFTY 50 resolution 50/50; historical membership aliases 79/84 (missing current-master symbols HDFC, JPASSOCIAT, MCDOWELL-N, RANBAXY, TATAMOTORS); daily 2018 probe PASS; 2022-10-31 minute bars 5/5 PASS; 2026-10-29 minute bars stop at 15:14 and targeted expiry-close 0/5.
- One preceding attempt failed because TOTP returned HTTP 200 without accessToken and fallback profile returned 401; later refresh succeeded. A workflow defect that staged but did not commit diagnostics was corrected; latest run committed sanitized JSON and phase status.
- Decision: do not keep refreshing tokens unnecessarily. Next research task is resolve historical symbol aliases and investigate missing recent expiry-close bars using documented Dhan parameters/free alternative sources; no C2 model until complete universe labels/weights pass.

## 2026-10-31 — User asked assistant to run protected Dhan workflow

- User instructed: “Run it yourself as you were doing before.”
- Triggered the C1 Dhan workflow through the branch's existing push trigger rather than asking the user to click the manual dispatch button.
- Successful live run [41223795394](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41223795394): 13 offline tests passed; fresh TOTP authentication/profile and active Data API plan passed; current universe resolved 50/50; historical aliases 79/84; five-stock daily-history sample passed; 2022 intraday sample 5/5 passed; recent 2026 expiry-close sample 0/5.
- Later TOTP retries returned HTTP 200 without an access token and fallback profile HTTP 401. No price calls occurred in those retries. No secrets or token values were requested or recorded.
- Diagnosed and fixed the workflow's generated-report persistence bug. The first workflow revision's autostash/rebase sequence left generated files unstaged. The corrected workflow commits diagnostics before rebasing.
- Preserved the successful run's sanitized results and the later failed auth-only attempt separately in the C1 branch. Current status remains C1 BLOCKED; C2 is not authorised until historic IDs, weights, corporate actions and full price/close coverage pass.

## 2026-10-31 — Final Dhan run and persistence verification

- A subsequent protected push run [41224048773](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41224048773) successfully authenticated with a fresh TOTP token, passed profile/data-plan checks, and completed all 13 offline tests.
- It reconfirmed 50/50 current NIFTY 50 symbols and 79/84 historical aliases in the current Dhan master. The five-stock 2022 historical intraday sample passed, while the 2026-10-29 expiry-close bars remained missing for all five.
- The corrected workflow committed the sanitized result and status as d5a82d8. Repository verification confirmed the latest successful report and the earlier auth-only failure are separately preserved.
- Research decision unchanged: C1 BLOCKED; do not proceed to C2 or claim a model/strategy until remaining identity, weights and price-coverage gates pass.



## 2026-11-01 — Expiry proxy, historical aliases and weight search

- User direction: “I don't need 15:25–15:29 data treat the available time as expiry like 15:15”; “Do the necessary to resolve, if it couldn't be resolved, no issues. 79 are available right?”; “Do a web search to obtain the weights.”
- Updated C1 expiry acceptance to the final available one-minute candle at/before 15:15 IST and removed the late close-window dependency. The live Dhan run 41247509692 authenticated, resolved 50/50 current symbols and matched 79/84 historical names; 10/10 five-symbol/two-date checks passed with 15:14 timestamps.
- Tested historic HDFC Ltd security ID on 2022-10-31 and 2023-06-30; both passed. Classified JPASSOCIAT, RANBAXY and MCDOWELL-N as 2014-only membership aliases, outside the confirmatory window; recorded TATAMOTORS/TMPV as a dated identity/corporate-action change.
- Searched for historic NIFTY 50 weights. Located official NSE archive report family for monthly market-cap/weightage reports, and acquired an openly hosted 216-row/100-ticker weight dataset through 2025-08-31. It is CC BY-NC-SA 4.0, non-commercial only, uses some estimated/extrapolated event weights, and needs cross-checks; no 2025-09 onward weights found/added yet.
- Added cache-first download/validation, provenance/licence notes, identity history notes, user decision file and workflow-driven status updates. No private chain-of-thought is stored in repo; only user-visible decisions, technical steps and outcomes.
- Overall C1 remains NOT PASSED and C2 remains gated; no prediction model or strategy is claimed.

## 2026-11-01 — C1 reporting correction verified

- Corrected the automatically rendered C1 status block so it describes the 15:15 expiry proxy, latest 15:14 observations, HDFC legacy probes and weight cache rather than the obsolete 15:25–15:29 condition.
- Replaced a deprecated pandas validation call and added finite/range tests. Follow-up workflow [41247674443](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41247674443) succeeded with 18 passing tests. Cached weights revalidated.
- Updated the C1 phase status with the latest gate summary. The main README and research/error/conversation logs link the relevant phase artifacts. C1 remains NOT PASSED; no C2/model/strategy was created.


## 2026-11-01 — BUP-01 C1 continuation
- User: “Ok proceed”.
- Assistant continued the BUP-01 C1 source audit after re-checking the current phase plan/status and main repository logs.
- Visible outcome: amended the frozen expiry target to use the user-approved 15:15 proxy consistently for stock and index outcomes; found a public minute archive with 47/50 member-file presence on a 2022 expiry/next-session pair; sampled five equities plus NIFTY at 10:00–10:03 and 15:14.
- Licence finding: README-only MIT assertion was not accepted because no LICENSE file was present in the inspected fork or upstream root. No bars were imported. Other public candidates were not admitted because their rights/availability were unresolved or restrictive.
- C1 remains NOT PASSED; no model/strategy result exists. Only visible messages, decisions and outcomes are logged; private reasoning and secrets are not stored.


## 2026-11-01 — BUP-01 full-universe data and weight-source audit continuation
- User: “Ok proceed”.
- Assistant ran a fixed-session Dhan coverage probe across all 50 point-in-time current NIFTY 50 constituents on 2026-10-29. Result: 50/50 security IDs resolved, 50/50 one-minute sessions passed QA with the 10:00–10:03 anchor and latest 15:14 expiry-proxy bar.
- Governance C0 run 41249521876 passed plan validation and 4 tests; C1 source-audit run 41249642494 passed.
- Found and cached the NSE Indices March 2026 whitepaper full 50-constituent weight snapshot as of 2026-02-27, preserving two-decimal published weights (sum 100.02% due rounding, no normalisation).
- Identified the original HF minute dataset declaring MIT and broad 2022–2026/2000–2026 coverage; upstream feed provenance is not documented, and the README restricts stated purpose to research/education/backtesting. No bulk data import yet.
- E0037/E0038 governance CI issues resolved. C1 remains NOT PASSED; no model or trading result produced. Only visible outcomes are logged.


## 2026-11-01 — BUP-01 official weights archive terms review
- User: "Ok proceed".
- Assistant identified the official NSE Indices monthly constituent-weight ZIP archive and a public naming-pattern example. Independent documentation reports historical month-end coverage from June 2013.
- Reviewed the NSE research-data policy and Nifty Indices site terms. Since automated collection requires express written consent under the site terms, no archive ZIP was requested or fetched.
- Added the permission-gate report to the C1 branch and updated README plus research/error/conversation logs. C1 remains NOT PASSED; no model or strategy was generated.


## 2026-11-01 — C1 90-day Dhan range test implementation
- Assistant added a 90-day one-minute history QA probe for RELIANCE, TCS and INFY on 2022-10-03 through 2022-12-30; the probe stores only aggregate coverage/quality metadata.
- Initial tests found a missing NumPy import (2 new tests failed, 19 passed). The import was corrected and the follow-up workflow was queued. No live data request ran in the failed test step.


## 2026-11-01 — Dhan 90-day/full-universe validation continuation
- User: “Ok proceed”.
- The three-symbol historical range test passed for RELIANCE, TCS and INFY over 2022-10-03–2022-12-30: 61 normal sessions per stock, all 61 had both anchor and 15:14 expiry-proxy coverage, no duplicate timestamps or OHLCV errors. The Diwali Muhurat evening-only date was separated from daytime sessions.
- Full 50-stock one-session preflight passed 50/50 on 2026-10-29.
- A subsequent full 50-stock 90-day run did not reach data requests because token refresh returned no usable access token and the stored fallback returned HTTP 401. A bounded retry and last-success preservation were added; current validation run 41251346795 was pending at this update.
- Logged E0041 (special-session QA), E0042 (transient Dhan auth) and E0043 (initial retry newline guard).
- Only visible outcomes and decisions are logged, not private reasoning or secrets.


## 2026-11-01 — Full 50-stock 90-day Dhan coverage check completed
- User said “Ok proceed”.
- The expanded Dhan run [41251346795](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41251346795) completed successfully after the transient auth incident was corrected.
- Result: 50/50 point-in-time active constituents passed for 2026-06-29–2026-09-26. Each symbol had 23,414 bars over 64 regular sessions, 64/64 anchor and expiry-proxy coverage, no missing bars, no duplicates and valid OHLCV; 1,170,700 aggregate rows.
- The last-success JSON is now separately preserved. Raw prices and private credentials are not committed.
- Phase status and full validation report updated. C1 remains NOT PASSED; no model/strategy yet.


## 2026-11-01 — Historical 2022 50-stock coverage completed
- User: “Ok proceed”.
- Dhan full point-in-time universe test for 2022-10-03–2022-12-30 passed 50/50. All 61 regular sessions per stock had both the anchor and expiry-proxy bars; no duplicates or OHLCV errors; aggregate 1,146,180 rows.
- Included HDFC Ltd legacy Dhan ID 1330 and the dated pre-demerger TATAMOTORS→TMPV security ID mapping. No cross-event stitching.
- Workflow [41251808946](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41251808946): 24 tests passed. Repo phase status, historical audit and README/logs updated. C1 remains NOT PASSED.
