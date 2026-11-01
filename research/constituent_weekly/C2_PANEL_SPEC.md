# C2 — Point-in-time constituent panel specification

**Plan:** BUP-01 v1.3 (locked)  
**Formal phase branch:** `phase/constituent-weekly-outcomes-c2-panel`  
**Status:** IN PROGRESS — formal panel-only implementation follows after a diagnostic bundled pilot on `phase/constituent-weekly-outcomes-c2-models`.

## Decision carried from C1

The user explicitly waived the remaining historical security-identity and corporate-action checks as preconditions. This is acceptance to progress with limitations, not a statement that the five residual alias records or 711 event candidates have been verified. The C2 panel must carry identity/action flags and use a conservative sensitivity set. It must not invent adjusted prices or use unverified adjustment factors.

## Panel unit and targets

The unit is one point-in-time tradable constituent × one verified weekly expiry cycle.

For cycle (t):
- Anchor date is the first regular NSE session after the preceding verified weekly expiry.
- Forecast cutoff is 10:00 IST. The anchor is the first valid one-minute candle open timestamped 10:00–10:03 IST.
- Expiry observation is the latest valid one-minute close timestamped 15:00–15:14 IST on the actual expiry session; record its exact timestamp and call it the 15:15 proxy.
- Return is (R_{i,t}=C_{i,t}/A_{i,t}-1). UP if positive, DOWN if negative, FLAT if exactly zero. FLAT stays in data QA and is excluded from binary fits unless plan version changes.
- NIFTY target is independently calculated from its observed index bars under the same time convention. Equal-weight constituent averages are diagnostics/features, never substituted for the NIFTY target.

## Required row-level fields

The encrypted panel must include:
- cycle key, previous expiry, anchor date, expiry date, point-in-time canonical ticker and actual exchange ticker;
- stock anchor price/time and expiry-proxy price/time; continuous return and ternary/binary label;
- prior-only daily OHLCV features (1/5/10/20/60-session returns; 5/20/60-session realised volatility; 10/20-session average range; prior-session gap; 20-session log-volume surprise);
- within-cycle cross-sectional ranks of prior 5/20-session return;
- identity-review, known corporate-action-crossing, unresolved mapping, source provenance and missingness flags;
- cycle-level observed NIFTY anchor/expiry target, return and label, plus its own causal daily features;
- source file hashes, security-master hash, data-method/version and cache manifest.

No price or feature row may be created using data after the 10:00 forecast cutoff. No forward fill or fabricated observation is permitted.

## Acceptance

1. Verified expiry calendar and session builder; no fixed weekday inference.
2. One unique stock row per (cycle, stable security identity); no duplicate identity-cycle pairs.
3. Point-in-time membership only; no current-universe survivorship substitution.
4. Required stock targets: at least 47 valid members and at least 94% of that cycle's point-in-time tradable member count.
5. Valid NIFTY target on at least 98% of scheduled eligible cycles.
6. At least 104 prior accepted cycles for the first confirmatory C3 stock-model forecast. Earlier rows may be retained for descriptive/training context where the locked plan allows but must not be described as confirmatory.
7. All features are computed strictly before the 10:00 cutoff; test with future-row mutation invariance.
8. Unverified event/identity observations remain flagged. No generic corporate-action scaling factor may be applied. Primary sensitivity panel excludes flagged identity/action-crossing rows; exploratory panel may show them separately.
9. Raw Dhan payloads and derived full-value panels stay AES-GCM encrypted in Actions cache/artifacts. The public repo may contain schema, hashes, counts, QA flags and sanitized aggregate reports, not raw daily/minute prices or full feature matrices.
10. No stock or index model fitting in formal C2. Stock models belong to C3; NIFTY aggregation belongs to C4.

## Handoff

C2 output is a frozen encrypted panel plus a sanitized manifest/report, feature dictionary, exclusion ledger, row-count and missingness QA, input hashes, reproducibility tests, and a declared chronological holdout boundary. C3 consumes only this frozen snapshot and generates out-of-fold stock predictions. C4 trains the NIFTY direction meta-model on strictly out-of-fold stock summaries.

The exploratory bundled pilot is kept separately for diagnostics and may not be used as formal C2/C3/C4 acceptance evidence until its methods and holdout design have been brought into conformance with plan v1.3.
