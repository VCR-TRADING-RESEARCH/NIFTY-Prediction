# Research Plan Version 1.1 Addendum — New Directional Methods

**Date:** 26 October 2026  
**User authorisation:** “Extend the research to identify new methods to predict weekly expiry nifty up or down!”  
**Branch:** research/phase-9-new-direction-methods  
**Baseline:** docs/RESEARCH_PLAN.md Version 1.0, registered 25 October 2026.

## Change control and compatibility

Version 1.0's target definition, causal feature clock, chronological holdout rules, primary metrics, transaction-cost requirements and finite stop rules remain unchanged. This dated addendum does not relax source-quality gates or redefine the target. It adds a bounded new-method discovery workstream because the user explicitly requested it. Version 1.0 remains part of the audit history; future outputs must state which version produced them.

## Added workstream: Phase 9 method discovery

1. **Literature and method mapping — COMPLETE for this bounded pass.** Candidate families and limitations are documented in docs/PHASE_9_NEW_DIRECTION_METHODS.md and the targeted extension to docs/LITERATURE_REVIEW.md.
2. **Input availability audit — AUTOMATED.** Publish the current feature inventory, known blockers, candidate data requirements and existing exploratory results as research/results/method_discovery_readiness.json.
3. **Empirical method comparison — BLOCKED.** Do not train or tune new candidates until independent 10:00 anchor validation and the minute-source / official-OHLC discrepancy gate pass. Current labels may contain source error; after repair rebuild labels and re-freeze the holdout.
4. **Bounded model evaluation — PENDING DATA GATE.** After repair, compare only registered method families using expanding walk-forward evaluation and nested development selection. Evaluate one untouched contiguous 20% holdout once.
5. **Independent statistics and trading audit — PENDING.** Apply paired contiguous-block bootstrap intervals, multiplicity correction, calibration/leakage checks and date-specific Paytm Money cost/spread/slippage stress tests.
6. **Stop rule.** If bounded source repair remains blocked, record the precise missing evidence and stop empirical candidate search. Do not loop through model families on unverified labels.

## Added candidate priorities

1. Independent target and anchor integrity.
2. Low-complexity multiscale trend, reversal, range, gap, asymmetry and volatility-ratio features.
3. Fold-local volatility-regime interactions and optional GARCH/HAR derived features.
4. Historical point-in-time options IV/skew/term structure/straddle-implied-move and OI data.
5. Timestamp-valid global overnight/cross-market inputs and correctly lagged FII/DII/participant reports.
6. Calibration and time-series-aware uncertainty/abstention.
7. Only then, bounded PySR/Quantevolve-inspired candidate generation: maximum 100 candidate expressions/rules, at most 3 development-only generations, complexity constraints and complete candidate registry.
8. Large sequence models and LLM-generated rules are deferred unless data depth and point-in-time provenance materially improve. LLMs may propose hypotheses but cannot act as ground truth.

## Decision thresholds to register before the repaired holdout is viewed

Do not use the current holdout to choose methods while source quality is blocked. Before viewing results on a rebuilt holdout, register a screening threshold of at least +0.03 balanced accuracy versus the strongest pre-registered baseline, a paired 95% contiguous-block bootstrap interval above zero, no material Brier/log-loss degradation, and effect direction that does not reverse across the principal time/volatility regimes. These are screening criteria, not a profitability guarantee. The split manifest must record exact block construction and the multiplicity correction before evaluation.

## Status at amendment

- Method design and literature mapping: **PASS**.
- Automated readiness report and regression tests: **IMPLEMENTED ON PHASE 9 BRANCH; RUN PENDING**.
- Independent target/source integrity: **BLOCKED**.
- Empirical comparison of new methods: **NOT RUN / BLOCKED**.
- Usable trading strategy: **NOT VALIDATED**.
