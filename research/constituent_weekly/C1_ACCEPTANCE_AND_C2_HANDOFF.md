# C1 acceptance decision and C2 handoff — 2026-11-02

## Decision
The user has explicitly directed that the remaining historical security-identity and corporate-action verification checks are not required before proceeding. This is recorded as a scope decision, not as evidence that those checks passed.

## C1 disposition
- Daily OHLCV coverage: PASS, 106,392/106,392 (100%) across 70 point-in-time symbols.
- Weekly intraday target coverage: PASS, 258/258 cycles under the registered 47-member / 94% coverage rule.
- Historical security-identity residuals: ACCEPTED WITH LIMITATION; 79/84 alias ledger entries previously matched.
- Corporate-action catalogue: ACCEPTED WITH LIMITATION; 711 member/event matches are discovery candidates, not independently verified adjustment records. No generic adjustment factor is applied.
- The five unresolved identity aliases and all potentially affected event windows must be carried as provenance/quality flags. Where a known action makes a price series discontinuous or its mapping ambiguous, do not fabricate an adjustment; retain a raw-price sensitivity analysis and report affected observations separately.

## C2 modelling rules
1. Proceed with the available validated daily/intraday dataset; do not repeat C1 source searches.
2. Use point-in-time membership and the existing dated symbol resolver. Preserve unresolved aliases as explicit flags; do not silently map them.
3. Build both (a) broad exploratory panel and (b) conservative sensitivity panel excluding observations with ambiguous identity or material corporate-action exposure. This is a robustness comparison, not a new C1 gate.
4. Never apply unverified split/bonus/rights/merger factors. Keep raw prices and action flags; if model labels/features are sensitive, exclude affected rows in the conservative panel.
5. Start with leakage-safe baselines, then ExtraTrees, regularized logistic regression and gradient-boosted/tree candidates where supported. Use chronological walk-forward splits, nested tuning, class-balance checks, calibration and confidence intervals.
6. Evaluate constituent weekly expiry direction first, then aggregate to NIFTY only using point-in-time constituents and available weights/proxies permitted by locked plan v1.3. Do not reintroduce ETF/IWF reconstruction.
7. Report every model result, including negative results. No trading claim until a separate executable strategy backtest includes Paytm Money brokerage, exchange/statutory charges, GST, stamp duty, bid-ask spread, slippage, fills and position sizing.

## Scope/status
C1 is treated as accepted for progression with limitations by explicit user direction. This does not certify the historical identity/action data as fully verified. C2 is now authorised to begin on branch `phase/constituent-weekly-outcomes-c2-models`.

## Audit trail
The user message on 2026-11-02 was: "No check needed". The decision is recorded without hidden reasoning or credentials.
