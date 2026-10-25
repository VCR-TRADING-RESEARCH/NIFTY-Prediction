# Phase — Free GitHub Actions + GitHub Pages prediction

**Branch:** `phase/github-actions-pages-free`  
**Goal:** Remove the external API-host dependency. Use GitHub Actions to calculate predictions and GitHub Pages to display published JSON.

## Design

1. Scheduled workflow runs weekdays at 10:30 IST (05:00 UTC), after the 10:00 IST anchor bars should be available.
2. The workflow also exposes `workflow_dispatch` for a manual run with an optional `YYYY-MM-DD` cutoff.
3. It uses the existing tested `scripts/run_live_prediction.py` / `live_api.app._do_prediction` pipeline and GitHub Actions secrets for Dhan credentials.
4. It restores/saves the Actions minute-data cache and writes the per-date JSON record.
5. It publishes `docs/assets/predictions/latest.json` plus the date-specific JSON file to `main`, so Pages can load the latest record without any GitHub Issue submission or external API.
6. The Pages UI reads `latest.json` on load; the user may select a date to read a date-specific published record. It does not contain tokens or start Actions itself.

## Important platform constraint

GitHub Pages is static hosting. A browser button cannot securely dispatch a private GitHub Actions workflow without an authenticated trigger. Therefore this free implementation refreshes on schedule/manual Actions and the button loads the latest published prediction. It does not claim immediate fresh computation on every click.

## Security and correctness

- Keep `DHAN_CLIENT_ID`, `DHAN_PIN`, and `DHAN_TOTP_SECRET` in repository/organization Actions secrets only.
- Never embed a PAT, Actions token, Dhan token, PIN, or TOTP in JavaScript or Pages assets.
- Validate ISO dates before using them.
- Publish failed status records and log failures; overwrite prior same-date output on failed inference, never silently substitute a stale prediction.
- Reuse cached historical data where available; cache misses may cause a fetch.
- Do not label the raw ExtraTrees score as probability of profit.
- No prediction is cleared for trading until independent 10:00 anchor reconciliation, leakage-safe walk-forward validation, and instrument-level options P&L with Paytm Money charges, bid/ask spreads and slippage pass.

## Acceptance gates

| Gate | Status |
|---|---|
| Workflow implementation and manual dispatch | Prepared on branch |
| Pages no longer requests Issue submission or external API | Prepared on branch |
| JS syntax / Python regression tests | Pending branch CI |
| YAML accepted by GitHub Actions | Pending push-triggered run |
| First scheduled/manual Dhan inference and JSON publication | Pending after merge/dispatch |
| Browser check on deployed GitHub Pages | Pending |
| Independent data/anchor and options cost validation | BLOCKED |

## Stop condition

Stop deployment work when the scheduled/manual workflow, result publication, and Pages display are verified. Continue quantitative research separately only through the predefined research phases; do not treat a functioning website as evidence of a profitable strategy.
