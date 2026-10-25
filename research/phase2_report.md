# Phase 2 Experimental Report — First Bounded Run

**Run:** [40171160326](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40171160326)  
**Generated:** 2026-10-25  
**Status:** PARTIAL / EXPLORATORY — PySR rerun is queued after correcting a workflow condition. No strategy validated.

## Research question

Can bounded evolutionary feature search, symbolic regression, a fixed-weight expiry-pressure indicator, or an agent-assisted review improve prediction of whether the candidate weekly expiry close exceeds the next-session 10:00 anchor?

## Sample and controls

- 398 candidate cycles, chronologically sorted.
- 318 development rows and 80 held-out rows.
- Candidate calendar remains heuristic and price-source discrepancies remain unresolved.
- The 80-row holdout is a single exploratory block, not an independent confirmation sample.
- No contract-level futures/options P&L, dated Paytm Money costs, bid/ask spread, slippage, fills or capital sizing was evaluated.

## Results

| Track | Status | Holdout result | Interpretation |
|---|---|---:|---|
| Logistic baseline | Completed | 56.25% accuracy; 56.29% balanced accuracy; MCC 0.125; Brier 0.251 | Reference model, not a tradable edge |
| QuantEvolve-inspired bounded evolutionary search | Completed | 53.75% accuracy; 53.58% balanced accuracy; MCC 0.072; Brier 0.294 | Worse than logistic baseline; do not promote |
| Custom indicator Python mirror | Completed | 38.78% directional accuracy on 49 signalled rows; 61.25% coverage | Poor direction results on this sample; fixed weights/threshold not supported |
| PySR symbolic regression | Not completed in first run | Import failed because the install step was skipped by a workflow condition | Workflow corrected; a rerun is queued |
| TradingAgents | Upstream smoke-test / deterministic risk review | No agent forecast score | Not a live multi-agent run; Python package was not importable in the local runner environment |
| AstraQuant | Cloned and revision recorded | Not evaluated as a signal model | Crypto-execution architecture is not assumed transferable to NIFTY; no orders or API keys used |

The baseline/evolution/indicator values are reproduced in `research/results/experimental/experimental_results.json`. Exact cloned upstream revisions are in `research/results/upstream_revisions.md`.

## Decision

**No usable strategy.** The evolutionary search did not beat the logistic baseline. The indicator was weak on its signalled subset. PySR still requires a completed run. TradingAgents has not been run as a live multi-agent forecasting system; the recorded role review is a deterministic safety review only. No profitability inference is justified.

## Corrections and next bounded action

1. The first Phase 2 workflow incorrectly skipped PySR installation on push. The workflow was corrected to attempt installation and report import status.
2. The feature pipeline was made opt-in for full rebuilds because a committed, reproducible feature snapshot exists. Manual `refresh_features=true` rebuilds it; this avoids needlessly spending the run budget on the same slow target pipeline.
3. One rerun is queued to attempt PySR and refresh the per-track report. Do not run repeated evolutionary searches on the same holdout.
4. If PySR cannot run due to Julia/runtime limitations, record it as unavailable and stop this phase rather than looping.
5. Pine compilation remains unverified because the TradingView Pine runtime is not available in CI.

## Limitations

This is a small, noisy, unverified candidate dataset. A high development fitness can reflect repeated search and overfitting. The baseline itself is not validated. The current target calendar and independent price-source mismatch were deliberately bypassed at the user's request; this is not a scientific acceptance pass. The spot index is not an executable instrument. Any future trading claim needs verified labels, a separate untouched evaluation, realistic instrument-level fills, date-aware brokerage/exchange taxes, spread and slippage.
