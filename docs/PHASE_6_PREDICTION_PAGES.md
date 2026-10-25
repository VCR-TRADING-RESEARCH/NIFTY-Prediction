# Phase 6 — ExtraTrees Prediction Interface and Deployment

**Branch:** \`research/phase-6-prediction-pages\`  
**Status:** IMPLEMENTATION ADDED; automated pipeline and deployment verification pending.  
**Purpose (original implementation):** Publish a GitHub Pages interface for displaying precomputed ExtraTrees forecast records. This phase is now superseded for live Predict requests by [Phase 7 — On-demand Dhan-backed inference](PHASE_7_LIVE_DHAN_INFERENCE.md).

## Scope

The original Phase 6 page read a static JSON payload and did not run Python on button click. That behavior did not meet the user's intended requirement. Phase 7 now wires **Predict** to a secure backend that refreshes Dhan authentication, fetches/caches minute bars through the selected date, and refits the existing ExtraTrees pipeline. The static historical JSON remains a research artifact only; it is not the response to a live Predict request.

## Research and implementation questions

1. Can the existing ExtraTrees pipeline produce the exact same class of out-of-sample forecast on the fixed 2025-04-09 holdout boundary without training on the target's expiry outcome?
2. Can a next-cycle feature row be constructed using only the first valid minute-bar open at/after 10:00 IST on the first session after the latest verified expiry?
3. Can the prediction page show an explicit failure state when the input date has no eligible anchor, the current forecast is stale, or data-quality validation is blocked?
4. Can GitHub Actions update forecast records and deploy the static page without placing Dhan/GitHub tokens in client-side JavaScript?

## Plan and gates

| Step | Work | Acceptance criteria | Status |
|---|---|---|---|
| 4.1 | Build historical ExtraTrees forecast exporter | Uses the same ExtraTrees hyperparameters and feature list; each historical model is fitted only on targets with expiry dates strictly before the prediction anchor | Implemented; tests pending |
| 4.2 | Add latest forward forecast | Builds features from the first valid post-expiry 10:00–10:03 IST bar; training labels must already be settled; future expiry marked provisional until exchange verification | Implemented; workflow run pending |
| 4.3 | Add static web interface | Date input, Predict button, UP/DOWN result, score, training cutoff, expiry date, blocked gate and clear error state | Implemented |
| 4.4 | Wire prediction JSON into the research workflow | JSON is generated and committed alongside research output; no credentials or raw Dhan data committed | Implemented; workflow run pending |
| 4.5 | Add Pages deployment workflow | Builds/deploys \`docs/\` from the default \`main\` branch and supports manual run | Implemented; deployment pending branch merge and GitHub Pages setup |
| 4.6 | Validate page/data outputs | Unit tests pass, current forecast has a valid anchor and future expiry, no future label enters training, page JSON schema validates | Pending |
| 4.7 | Report limitations and status | README and research log link the site; no claim that the model is a validated trading strategy | In progress |

## Model behavior

- Model: \`sklearn.ensemble.ExtraTreesClassifier\` inside the existing median-imputation pipeline.
- Parameters: 300 trees, maximum depth 3, minimum leaf size 8, \`max_features=0.8\`, \`class_weight="balanced"\`, seed 42.
- Feature columns and transforms are imported from \`scripts/research_core.py\`; duplicate logic is avoided.
- Historical records start at the fixed 2025-04-09 expiry holdout boundary. The boundary is not recomputed when new weekly cycles are added.
- For every historical target, the training set is restricted to records whose expiry dates precede the target expiry and are settled before that target's anchor.
- The live forward forecast is trained only on binary labelled cycles that have expired by the prior verified expiry and precede the new anchor.
- The model's \`p_up\` is displayed as an uncalibrated score, not as a trusted probability of success.
- If the expiry calendar has not refreshed past the prior known expiry, or the next candidate expiry has already passed, the page must not silently reuse an expired forecast as a current signal.

## Known blockers and safety gates

- The main data-quality gate is still **BLOCKED**: the preserved archive close differs from the official close by more than one index point on 1,719 of 1,903 sessions in the latest independent audit.
- The 10:00 reference price is from the public minute archive and has not been independently validated.
- The expiry date for a forward forecast is a candidate date until confirmed against official contract history.
- The historical holdout metric (61.25% on 80 observations) is descriptive only; its Wilson 95% interval is approximately 50.3%–71.2%.
- This page forecasts spot direction, not options strategy profit. It does not model contracts, strikes, Greeks, fills, bid/ask spreads, slippage, Paytm Money brokerage, exchange fees, STT, GST, stamp duty, or position sizing.
- A blocked source gate must remain visible in the user interface. Prediction outputs must not be labelled as trade recommendations.

## Files

- Page: \`docs/index.html\`
- Browser behavior: \`docs/assets/predictor.js\`
- Styles: \`docs/assets/predictor.css\`
- Forecast export: \`scripts/build_pages_forecasts.py\`
- Workflow integration: \`scripts/run_research.py\`, \`.github/workflows/nifty-research.yml\`
- Static forecast data: \`docs/data/extra_trees_forecasts.json\`
- Deployment: \`.github/workflows/deploy-pages.yml\`
- Tests: \`tests/test_pages_forecasts.py\`
- Research manuscript and current source gate: \`research/manuscript.md\`, \`docs/PHASE_3_SOURCE_RECONCILIATION.md\`

## Completion rule

The static interface stage is complete but does not satisfy live on-demand inference. See [Phase 7 acceptance gates](PHASE_7_LIVE_DHAN_INFERENCE.md). Even after the backend is deployed, the app remains research-only until independent source/anchor and instrument-cost gates are cleared.
