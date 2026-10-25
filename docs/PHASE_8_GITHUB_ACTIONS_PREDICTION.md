# Phase 8 — GitHub Actions on-demand prediction

**Branch:** `phase/github-actions-on-demand-prediction`  
**Goal:** Run the existing Dhan-backed ExtraTrees inference inside GitHub Actions and publish a date-specific result to GitHub Pages without a separate paid API host.

## Intended click flow

1. On the Pages predictor, select the 10:00 IST anchor date and click **Predict**.
2. The page displays a prefilled GitHub request link. Open it and submit the issue; GitHub authentication is the authorization boundary.
3. The `on-demand-prediction.yml` workflow accepts only issue requests created by repository owners/members, with a strict `[NIFTY PREDICT] YYYY-MM-DD` title. It also supports a manual `workflow_dispatch` input from `main`.
4. The runner refreshes Dhan authentication from `DHAN_CLIENT_ID`, `DHAN_PIN`, and `DHAN_TOTP_SECRET` GitHub Secrets, fetches/reuses Dhan minute chunks, and calls the existing `live_api.app._do_prediction` pipeline.
5. The workflow publishes a sanitized JSON record at `docs/assets/predictions/YYYY-MM-DD.json`; the still-open Pages tab polls for a newly generated result and displays it.
6. Failed data/model validation is represented as a failure. A prior record is never accepted as a fresh prediction because the page checks its generation timestamp.

## Security and platform constraints

- GitHub Pages cannot run Python or securely hold a GitHub/Dhan token. The page therefore never receives Dhan credentials or a GitHub API token.
- The page cannot silently invoke the authenticated Actions API from browser JavaScript. The user must authenticate to GitHub and submit the prefilled request issue. This extra submit step is intentional; do not embed a PAT in the page.
- Only `OWNER` or `MEMBER` issue authors may trigger the secret-bearing job. The issue title is parsed as data and never executed as shell code.
- Workflow runs are restricted to `main`; the manual workflow dispatch is also supported.
- The Actions cache retains old Dhan minute-data chunks between runs. Dhan token refresh still occurs on every inference request.
- The workflow writes only the public prediction summary and sanitized errors to the Pages assets directory. Raw bars, tokens, PIN, TOTP and provider response bodies are not published.

## Acceptance checklist

| Gate | Evidence | Status |
|---|---|---|
| Python runner | Reuses tested inference function; sanitized JSON output | Implemented; CI pending |
| Secure trigger | Authenticated GitHub issue submission and owner/member gate | Implemented; live event test pending |
| Manual workflow | `workflow_dispatch` accepts ISO date on `main` | Implemented; CI pending |
| Data cache | Actions cache restore/save around Dhan minute chunks | Implemented; runtime test pending |
| Pages result | Date-specific JSON is polled and freshness-checked | Implemented; browser test pending |
| Live Dhan request | Valid token, sufficient bars, model fit and published result | Not yet verified |
| Trading readiness | Independent anchor validation and instrument-level cost/slippage backtest | BLOCKED |

## Known limitations / next steps

- A workflow run and a JSON result do not prove the forecast is profitable. The 10:00 anchor remains independently unvalidated, and Paytm Money charges, spread, slippage, fills and options P&L are not yet validated.
- Public issue submissions by non-members do not receive Dhan secrets or run the job. If the signed-in account is not a repository owner/member, the request will not execute.
- GitHub Pages deployment may take a short time to publish a new JSON file after the workflow pushes it.
- Test the browser flow, confirm Actions permissions allow the workflow's commit to `main`, then make a live Dhan request. If Dhan credentials or API entitlements fail, keep the result marked failed and record the sanitized reason.
