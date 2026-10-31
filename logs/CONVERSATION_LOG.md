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


## 2026-10-31 — New bottom-up constituent weekly-expiry research requested

- **User request (visible):** “Start a new research to predict nifty by predicting the weekly expiry outcomes of all the underlying stocks, rather than trying to predict just with nifty values!”
- **Assistant response (visible summary):** Start a separate bottom-up constituent forecast track, inspect repository governance and prior project decisions, then register a bounded plan and initiate the first reproducible step.
- **Decision:** Create BUP-01 separately from the index-only model and current options backtest branches. Preserve the existing index-only ExtraTrees study as a benchmark, not as validated trading evidence.
- **Aggregation decision:** Forecast continuous constituent returns and aggregate with point-in-time free-float weights. Do not use a simple 50-stock vote as the primary index forecast. Build index probability from a dependence-aware joint forecast; weighted stock UP probability is a breadth statistic, not P(NIFTY UP).
- **Data and leakage controls:** Reconstruct point-in-time membership, security identity, corporate actions and numeric weights; never backfill today's constituents or today's weights into historical cycles. Validate stock anchor/expiry prices and reconcile the realised weighted basket with the official NIFTY index before model training.
- **Scope and stop rule:** Register C0–C6 phases and stop at a failed C1 data gate rather than fabricate weights or search indefinitely. Strategy profitability remains a separate gate with dated Paytm Money costs, spread, slippage and fills.
- **Logging boundary:** Record visible requests, decisions and auditable rationales. Hidden private chain-of-thought is not copied into repository files.


## 2026-10-31 — BUP-01 C1 findings and source-rights correction

- **User-visible progress:** Reported that the initial official monthly archive was reachable via Actions, then clarified that the sample was only a technical integrity check.
- **One-time sample finding:** The September 2026 NIFTY50 CSV has 50 unique constituent rows and displayed weights summing to 100.0%. No individual weights or raw rows were copied into the repository summary. The October archive PDF was only inventoried, not analysed.
- **Membership cross-check:** A third-party March 2026 membership file has WIPRO where the September 2026 official sample has BSE. The third-party file is not accepted as a current/historical source.
- **Rights decision:** After reviewing the NSE Indices Terms of Use, disabled further automated NSE retrieval and public raw archive uploads. Created a local/offline-only archive inspector for separately authorised inputs. Raised issue #27 to remove the earlier raw Actions artifact/cache.
- **Dhan code review:** Existing Dhan refresh logic and NIFTY-index intraday pipeline were examined. They do not yet establish constituent-level equity data; parent auth logs show unresolved TOTP/auth problems. No stock API call is claimed as successful.
- **Research status:** C0 PASS, C1 IN PROGRESS / RIGHTS-BLOCKED. No constituent panel, trained model, bottom-up index prediction, or strategy result exists.
- **Logging boundary:** Visible conversation updates and auditable decisions are recorded. Hidden private reasoning is not stored.


## 2026-10-31 — BUP-01 C1 workflow correction and status
- Corrected a literal escape in the C1 checkout branch ref after Actions run #28 failed before tests; failure and fix recorded in E0022.
- The follow-up run #35 entered `action_required` without any job steps. The workflow now uses read-only permissions and only offline authorised-archive inspection, but its tests have not yet passed in Actions.
- C1 remains RIGHTS-BLOCKED while source permission, historical point-in-time weights/membership and stock equity bars are unresolved. No constituent model or forecast was generated.


## 2026-10-31 — BUP-01 literature review extended
- Added peer-reviewed and recent literature on component-based aggregate-market prediction, five-minute constituent-to-market forecasts, Indian momentum/reversal/liquidity evidence, weekly short-term reversal and cross-sectional/time-series distinctions.
- Explicitly distinguished literature motivation from NIFTY weekly-expiry empirical evidence; the locked plan v1.0 was not changed.


## 2026-10-31 — BUP-01 membership/ownership source findings

- Found and cached a CC BY 4.0 NIFTY 50 membership subset with attribution. It has monthly cardinality consistency from 2018-01 through 2025-09 but carries 50 snapshot_floor intervals, only 33 press-release intervals and no numeric free-float weights; its latest event is 2025-09-30.
- Its related shareholding data have useful quarterly coverage, reaching all 50 then-current reconstructed members from 2023-09 to 2025-09, but provide ownership roll-ups only. Broadcast timestamps must be joined from filing manifests before any ownership feature can be used. These are not index weights.
- AMFI ETF portfolios were identified but not ingested because AMFI site terms restrict public redistribution/derivative works and significant electronic storage.
- The research remains at C1; no panel, model or NIFTY prediction is available.


## 2026-10-31 — C1 offline workflow passed; Dhan equity preflight staged

- Reported offline C1 source-audit run 41180457400 as a successful workflow/code check, with no authorised local archives present.
- Added a new Dhan equity preflight path and offline tests using the existing POST-based live API auth function. The script avoids printing or storing credentials, token values, security IDs and raw prices.
- The Dhan workflow's execution is not yet visible; no live equity-data result is claimed.
- C1 remains blocked on official point-in-time free-float weights, post-2025-09-30 membership and verified constituent minute bars.

2026-10-31 — User requested resume of BUP-01

- Continued the C1 constituent weekly-expiry research and checked the phase records and latest Actions runs.
- Recorded offline audit success, 10/10 Dhan mocked tests passing, live token response without accessToken and profile HTTP 401.
- Updated the C1 branch status, README, source register, research/error/conversation logs. Also mirrored the latest C1 status and links into main README and logs.
- No private reasoning, credentials or secrets are copied into repository logs.
