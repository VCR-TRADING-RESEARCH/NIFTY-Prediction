# Phase 8 — GitHub Actions + Pages prediction (free hosting)

**Current implementation:** [Phase — Free GitHub Actions + Pages](PHASE_GITHUB_ACTIONS_PAGES_FREE.md)  
**Workflow:** [`.github/workflows/free-pages-prediction.yml`](../.github/workflows/free-pages-prediction.yml)

The old issue-submission workflow is retained for audit/history, but it is no longer the intended Pages interaction. The new free flow is:

1. GitHub Actions runs on weekdays at 10:30 IST and also supports a manual run from the Actions tab.
2. Dhan credentials remain in Actions secrets; the existing Python ExtraTrees pipeline runs on the hosted runner.
3. The workflow publishes `docs/assets/predictions/YYYY-MM-DD.json` and `docs/assets/predictions/latest.json`.
4. GitHub Pages reads the published JSON. The user does not need to open or submit a GitHub Issue.
5. If the latest run fails, the published status is shown as unavailable; an older prediction is not silently passed off as fresh.

## Platform limitation

GitHub Pages is static. It cannot securely launch a private Actions run directly from a browser button without an authenticated trigger. In this no-extra-hosting design, the page's button loads a published result; scheduled/manual Actions does the Python computation.

## Status

Implementation is prepared on `phase/github-actions-pages-free`. CI, merge, a first scheduled/manual Dhan run, publication and a live Pages browser check remain pending. Existing historical inference for 2024-09-20 succeeded, but that result is not current and not trading-cleared.

Trading acceptance remains BLOCKED until independent anchor reconciliation, leakage-safe walk-forward tests and executable option-level P&L include Paytm Money fees, bid-ask spreads, slippage and realistic fills.
