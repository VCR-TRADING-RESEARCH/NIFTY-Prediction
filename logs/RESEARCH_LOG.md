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
- First provider deployment attempt failed with `HfHubHTTPError` before publishing endpoint config; no user-facing live result is being presented as if this deployment succeeded.
- Added sanitized diagnostics (stage, HTTP status, no secret/body logging) and retriggered deployment. Await its conclusion before reporting backend availability.
