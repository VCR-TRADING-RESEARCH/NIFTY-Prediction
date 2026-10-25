# Phase 2 — QuantEvolve, PySR, TradingAgents and custom indicator

**Branch:** `research/phase-2-quant-pysr-agents`  
**Status:** IN PROGRESS; all outputs are exploratory.  
**Requested scope:** Proceed with these four tracks while bypassing the earlier data-validation phases by user direction. The bypass is not a scientific pass and must not be represented as such.

## Tracks and bounded budgets

1. **QuantEvolve** — clone and smoke-test the upstream project; run a local bounded, auditable evolutionary search over sparse signed feature rules (80 candidates × 35 generations). The upstream repository is Binance/Gemini-oriented; its full code-generation/backtest loop is not pointed at NIFTY labels because its data and evaluator contract differ. This local search is labelled QuantEvolve-inspired, not an official upstream run.
2. **PySR** — attempt symbolic regression of continuous cycle return, with 25 iterations, 8 populations, max expression size 12, and chronological development/holdout split. Record expressions, holdout RMSE and R². Failure to install Julia/PySR is a logged result, not a silent skip.
3. **TradingAgents** — clone/smoke-test upstream. Record a deterministic three-role research review of quant, data, and execution risks. No live LLM calls, brokerage actions, or secret use. Full live agent debate is deferred unless provider config is safely available and explicitly included in a future plan revision.
4. **Custom TradingView indicator** — retain the existing Pine prototype and add an independent Python mirror/evaluation of its fixed components on the available weekly rows. Pine Script itself requires TradingView/Pine runtime for final compilation; CI cannot claim Pine compilation.

## Experimental controls

- Use chronological 80/20 development/holdout split; never randomly shuffle rows.
- QuantEvolve-inspired search uses rolling-origin development balanced accuracy and a fixed sparsity penalty; the holdout is scored once.
- PySR fits continuous cycle return, not the binary label, and reports the holdout result separately.
- The existing candidate expiry calendar remains heuristic and independent daily-close discrepancies remain unresolved. Therefore every score and expression is exploratory only.
- No strategy promotion without official expiry dates, independently reconciled prices, purged/embargoed walk-forward validation, realistic entry/exit contract prices, point-in-time Paytm Money charges, bid/ask spread, slippage, rejected/partial fills, and a separate untouched final holdout.
- No live trading or brokerage API order placement is included.

## Automation

`.github/workflows/phase2-experiments.yml` runs on push, weekly schedule, and manual dispatch. It reuses cached public market data, reruns the existing feature pipeline, clones the named upstream repositories, installs PySR, runs bounded experiments, uploads results/logs, and updates the experiment status. Each track fails independently so one unavailable optional dependency does not suppress other evidence.

## Acceptance outcomes

The phase ends after one bounded run and one automatic repair/retry for deterministic code defects. It does not loop indefinitely. Results must distinguish completed, unavailable, failed, and not run. A candidate is not a usable strategy merely because its holdout score exceeds a baseline on this unverified dataset.
