# Phase 7 — On-demand Dhan-backed ExtraTrees inference

**Branch:** `phase/live-dhan-inference`  
**Purpose:** Replace the static forecast lookup with true per-click inference using the selected as-of date, Dhan historical index bars, and the repository's existing ExtraTrees feature/model implementation.

## User-visible behavior

1. User enters an as-of anchor date (`YYYY-MM-DD` or `DD/MM/YYYY`) and clicks **Predict**.
2. GitHub Pages submits the date to a private-credential backend hosted as a Hugging Face Docker Space. The page bundle contains only the API endpoint, never a Dhan or Hugging Face token.
3. The backend generates a fresh Dhan access token using the configured Client ID, PIN and TOTP secret.
4. It resolves the NIFTY 50 index security ID from the current Dhan scrip master, then fetches one-minute candles from DhanHQ v2 up through the selected date. Requests are split into date windows of no more than 90 days, with server-side caching for previously downloaded historical chunks.
5. The backend validates timestamps/OHLC, merges the repository's official NSE daily-close reference data, and reuses `scripts/research_core.py` for target-cycle construction and feature calculations.
6. It validates that the requested date is the first trading session after the preceding verified expiry, and finds a valid 10:00–10:03 IST anchor.
7. It fits the repository's ExtraTrees pipeline only on weekly target labels whose expiry dates are strictly before the selected date, checks the feature row and training count, then returns UP/DOWN, the uncalibrated UP-class score, target expiry, anchor, and data provenance.
8. The page polls job status and renders a result or a sanitized, actionable error. It does not fall back to the old saved CSV/JSON output when live inference fails.

## Security and abuse protections

- Dhan credentials exist only as private runtime secrets on the backend, provisioned from GitHub Actions secrets. They are never uploaded as application source, written to logs, committed to Git, or returned to the browser.
- The backend refreshes the Dhan token for each request. The historical minute data may be served from its backend disk cache when the same old date chunk was already retrieved; the model is still refitted per click.
- CORS and request-origin checks restrict ordinary browser calls to the published GitHub Pages origin; an in-memory per-client rate limit and a single active prediction job limit accidental abuse. This is not a substitute for infrastructure-grade authentication.
- The backend returns only prediction summaries and diagnostics, never raw bars, tokens, PINs, TOTP values, or provider response bodies.
- Dhan credentials must have permitted historical-data access. If a secret is missing, auth fails, security mapping is ambiguous, or data are unavailable, the request fails closed.

## Source and leakage safeguards

- Dhan API's documented intraday history is limited to five years and each request can cover at most 90 days. Requests never extend beyond the selected as-of date.
- Historical labels use official NSE closing values where the repository has them; Dhan minute bars supply the selected 10:00 anchor and historical intraday features.
- Features for the selected date use bars strictly before the chosen anchor and daily aggregates from earlier sessions only.
- Training labels are filtered to expiry dates `<= previous_expiry` and strictly less than the as-of date; code checks the final training expiry is earlier than the selected date.
- At least 104 eligible binary weekly labels and both direction classes are required.
- The result remains **BLOCKED / exploratory** pending independent validation of the Dhan 10:00 anchor, complete expiry-date verification for the selected target, and a separate instrument-level backtest including bid/ask, slippage, Paytm Money fees, and statutory costs. Spot direction is not options P&L.

## Deployment

- Backend app: `live_api/app.py`
- Docker image specification: `live_api/Dockerfile`
- Backend deployment script: `scripts/deploy_live_api_space.py`
- Automatic/manual deployment workflow: `.github/workflows/deploy-live-api.yml`
- Safe public endpoint config: `docs/assets/live-api-config.json`
- Frontend request/polling logic: `docs/assets/predictor.js`
- Test suite: `tests/test_live_api.py`
- Branch validation workflow: `.github/workflows/test-live-api.yml`

The deployment workflow uses `HF_TOKEN` plus `DHAN_CLIENT_ID`, `DHAN_PIN`, and `DHAN_TOTP_SECRET` from GitHub Actions secrets. It creates/updates a Docker Space, installs those values as Space runtime secrets, and writes only the non-secret endpoint URL into the Pages configuration. If Hugging Face token permissions or required GitHub secrets are missing, deployment fails and the page remains safely disabled.

## Acceptance gates

| Gate | Required evidence | Initial status |
|---|---|---|
| A. Python correctness | Date parser, security-ID resolution and research core tests pass | Pending CI |
| B. Backend deployment | Space creation/upload succeeds; runtime health is ready; credentials reported configured without exposing their values | Pending CI / provider |
| C. Browser wiring | Page loads endpoint config, starts one job, polls result, handles errors and never reads saved forecasts as the click result | Implemented; browser verification pending |
| D. Dhan source validation | Selected cutoff bars and official close merge verified with acceptable missingness; 10:00 anchor independently reconciled | Blocked pending live API and independent check |
| E. Model leakage | Training labels strictly precede as-of date; features end at the 10:00 anchor | Code checks implemented; run-level verification pending |
| F. Usable trading strategy | Separate option/futures execution backtest with date-correct Paytm Money costs, spreads and slippage | Not yet attempted by this live inference phase; research gate remains blocked |

No phase is accepted just because the Space was created or an UP/DOWN score was returned. Failed deployment and inference attempts must be logged.
