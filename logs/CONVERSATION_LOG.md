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
