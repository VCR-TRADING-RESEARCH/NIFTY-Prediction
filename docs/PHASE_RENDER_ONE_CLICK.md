# One-click prediction backend deployment

## Goal
Replace the GitHub Issue submission workaround with a direct browser-to-secure-API request. The Pages app calls `POST /predict`, polls `GET /jobs/{job_id}`, and renders the returned inference. Dhan credentials remain server-side.

## Prepared implementation
- `render.yaml`: deploys the existing FastAPI inference service on Render.
- `live_api/Dockerfile.render`: root-context Docker build that includes the tested app, research core, official close data and expiry calendar.
- `docs/assets/predictor.js`: calls the configured API directly; it no longer creates GitHub issues.
- `docs/assets/live-api-config.json`: public endpoint config, intentionally blank until a real deployment is healthy.
- `docs/index.html`: describes direct prediction and no longer displays an issue link.

## Required deployment steps
1. Authorize deployment to a Render account you control.
2. Create/deploy the service from this repository using `render.yaml`.
3. Add `DHAN_CLIENT_ID`, `DHAN_PIN`, and `DHAN_TOTP_SECRET` as private Render environment variables; never place them in GitHub Pages or committed files.
4. Wait for `/health` to return `{"status":"ready"}`.
5. Set `docs/assets/live-api-config.json` `api_base_url` to the deployed HTTPS service URL and merge the change.
6. Verify browser CORS, a real Dhan request, job polling, result rendering, and sanitized failure behavior.

## Current gate
**BLOCKED pending service-account authorization/deployment.** No fake endpoint is configured. The page fails closed and does not return to the GitHub issue workaround. Prediction output remains exploratory until the separate anchor-reconciliation and instrument-cost gates pass.
