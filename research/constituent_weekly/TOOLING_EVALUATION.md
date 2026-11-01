# BUP-01 tooling repository evaluation

**Date:** 2026-11-01  
**Purpose:** Record the requested external research tooling, intended use, licence review and integration gates.  
**Decision:** Reference and evaluate now; defer code imports/integration until the relevant BUP-01 phase is authorised. This is not a change to locked plan v1.1.

## 1. Evaluation matrix

| Repository | Licence read from repository | What it provides | BUP-01 fit | Planned phase / decision |
|---|---|---|---|---|
| [tarsyang/quantevolve](https://github.com/tarsyang/quantevolve) | Apache-2.0 | Evolutionary strategy/code proposal loop with LLM scoring; README describes Gemini integration and Binance OHLCV collector | Could propose bounded hypotheses once a clean India-market dataset and fixed backtester exist. Binance collector is not an approved data route for this NSE/Dhan study. LLM/evolutionary search risks overfitting and multiple testing. | C5 exploratory strategy-rule proposals only, after C3/C4 and hard trial-budget, nested validation, locked holdout, and costs. No import now. |
| [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) | Apache-2.0 | Multi-agent financial research/analysis and decision workflow; README reports recent point-in-time and settled-decision fixes | Useful as a structured reviewer for market context / hypothesis generation, not as the primary numerical prediction engine. External vendor/news data availability, provider costs, as-of timestamps and data leakage must be controlled. | C3/C4 optional analyst support, sandboxed; outputs converted to falsifiable hypotheses, never accepted as model labels/signals. No import now. |
| [0xethanq/astra-quant-agent](https://github.com/0xethanq/astra-quant-agent) | Custom AGPL-3.0 + Commons Clause + additional terms | Multi-LLM crypto trading system, deterministic risk control and OKX-native execution; README says exchange execution is OKX-specific | Poor fit for NSE/Dhan; no native Dhan adapter and execution assumptions are crypto/OKX-specific. Custom Commons Clause / addenda need legal review before copying or integrating. | Architecture reference only. Do not import, copy code or connect execution. No use in BUP-01. |
| [astroautomata/PySR](https://github.com/astroautomata/PySR) | Apache-2.0 | Symbolic regression via Python + Julia engine; interpretable feature/expression search | Could test low-dimensional, constrained symbolic transformations or distilled rules. It is a search process and can overfit; Julia build/compute adds complexity. | C3 optional bounded feature discovery, with training-fold-only fitting and feature-selection budget; C6 document selected expressions. No import now. |
| [bashtage/arch](https://github.com/bashtage/arch) | Permissive BSD-style terms in repository LICENSE.md | ARCH/GARCH and other volatility models, bootstrap, unit-root/cointegration tests and multiple-comparison utilities | Good fit for realised/conditional volatility regimes and robustness; not itself a directional stock model. | C3/C4 volatility regime/variance diagnostics and selected bootstrap methods, after panel labels and timestamps pass. Add dependency only when needed. |
| [X-DataInitiative/tick](https://github.com/X-DataInitiative/tick) | BSD-3-Clause (LICENSE.txt) | Time-dependent statistical learning, Hawkes point processes, GLMs and optimization; C++ extensions | Primarily event/tick/point-process workloads. Present evidence is Dhan one-minute OHLCV, not a validated event/order-book feed. Build/runtime compatibility and C++ compilation would add friction. | Defer; consider only if a licensed event/tick dataset and a pre-registered microstructure research question exist. No import. |
| [scikit-learn-contrib/MAPIE](https://github.com/scikit-learn-contrib/MAPIE) | BSD-3-Clause | Model-agnostic conformal intervals/sets and risk control, including time-series methods; README notes exchangeability diagnostics/adaptive methods | Relevant for stock return intervals and index uncertainty, but ordinary IID conformal assumptions cannot be presumed for serially dependent weekly market data. | C4 uncertainty stage only, with sequential/block/adaptive method selection, calibration-window discipline, coverage diagnostics and out-of-sample checks. No import now. |

## 2. Integration principles

1. No framework-led research. Model/tool choice must follow a validated target panel and the pre-registered hypotheses, not the availability or novelty of a library.
2. No external data collectors as silent dependencies. Disable/quarantine Binance, crypto exchange, Yahoo/news or other vendor collectors unless a source is explicitly approved, licensed, point-in-time and added to the data source register.
3. No unconstrained evolutionary search. Any QuantEvolve/PySR search must have a fixed compute/trial budget, candidate registry, train-only selection, nested walk-forward validation and untouched final holdout. Every failed candidate remains logged.
4. No agent output as evidence. TradingAgents/AstraQuant-style textual analysis is a hypothesis only; it must be converted into a deterministic feature/test and evaluated against baselines.
5. Uncertainty is not automatically calibrated. MAPIE or any conformal method must be checked for exchangeability/sequential assumptions, interval coverage by regime, sample dependence and leakage before any coverage claim.
6. No code adoption of AstraQuant until legal review of its custom AGPL/Commons Clause/additional terms and a compelling India-market need. Its OKX-native execution path is explicitly not the Dhan/NSE route.
7. Minimum dependencies. Prefer the existing Python/scikit-learn/NumPy/pandas stack. Add arch, MAPIE or Julia-backed PySR only in the phase where an approved experiment actually needs it. tick is deferred without event-level data.
8. Execution remains disabled. None of these repositories may place orders. Any later execution study requires separate instrument-specific paper simulation and Paytm Money charge/slippage/fill accounting.

## 3. Phase mapping

- C1 (current): no listed modelling framework is needed. Complete licensed point-in-time IWF, identity/corporate actions, continuous coverage and index-basket reconciliation first.
- C2: use project-native, tested panel/feature pipeline only; lock feature availability and split.
- C3: existing sklearn baselines first; optional arch and constrained PySR experiments only after the C2 panel passes. TradingAgents may be a research reviewer only.
- C4: project-native dependence-aware aggregation first; optional MAPIE uncertainty methods only after a time-series calibration design is validated. Report interval coverage by regime.
- C5: optional QuantEvolve only inside a fixed, leakage-safe strategy-search budget; no external exchange data collector or live execution. AstraQuant remains excluded unless a separate legal/technical decision changes.
- C6: reproducibility, full model/tool inventory, licence and dependency audit.

## 4. Licence and dependency notes

- Apache-2.0 repositories identified: QuantEvolve, TradingAgents and PySR. Preserve notices/attribution if code is ever imported.
- BSD-family repositories identified: arch (repository has LICENSE.md with permissive redistribution terms) and tick (BSD-3-Clause). Preserve notices and check current dependency compatibility at integration time.
- MAPIE repository declares BSD-3-Clause.
- AstraQuant has a custom AGPL-3.0 + Commons Clause and additional terms; do not infer permissive reuse from its README badge.
- This is a repository-level snapshot on 2026-11-01; re-check exact commit, licence files and dependency security before any future import. No repositories were cloned or copied into the NIFTY project in this evaluation.

## 5. Gate decision

The tool evaluation is complete as a planning artifact, not as an implementation step. **C1 remains NOT PASSED / RIGHTS-BLOCKED** because no admissible complete point-in-time official IWF/constituent-weight data product has been licensed for the intended internal trading research, and weighted basket-to-index reconciliation cannot yet be performed. No C2 panel, model, bottom-up forecast or strategy has been created. BUP-01 plan v1.1 remains locked.
