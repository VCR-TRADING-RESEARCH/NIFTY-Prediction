# C3 Confirmatory Stock Modelling Status

**Phase:** C3 — stock models/baselines  
**Branch:** `phase/constituent-weekly-outcomes-c3-models`  
**Status:** READY — secure C2 encrypted-panel artifact handoff being enabled  
**Prediction:** No C3 result yet  
**Trading:** NOT VALIDATED

## Gate inheritance from C2

- C2 PASS: 258/258 NIFTY target cycles (100%).
- 258/258 cycles satisfy at least 47 valid constituents and 94% point-in-time member coverage.
- 12,807 constituent-cycle rows; 61 symbols.
- Zero duplicate constituent-cycle and index-cycle rows.
- Holdout starts at cycle 206 (2025-10-29 anchor; 2025-11-04 expiry), final 20%.
- 292 identity-flagged rows and 3 known action-crossing rows remain excluded from primary modelling; unresolved historical checks are not certified.
- Full acceptance: [C2_ACCEPTANCE_REPORT.md](C2_ACCEPTANCE_REPORT.md).

## Next execution step

C2's encrypted frozen panel must be attached to the successful C2 workflow artifact as ciphertext. C3 will verify hashes, decrypt in Actions with HF_TOKEN, run registered chronological stock models, and keep per-stock OOF outputs encrypted for C4. No plaintext panel is to be committed.

## Locked C3 candidate set

1. UP-frequency / majority baseline.
2. Own-stock five-session momentum baseline.
3. Pooled regularised logistic regression (primary).
4. Constrained ExtraTrees classifier.
5. Pooled regularised return regression.
6. One constrained HistGradientBoosting candidate.

Minimum 104 prior cycles; complete cycles are indivisible; final 20% holdout remains sealed. Four-cycle block bootstrap, 2,000 replicates, seed 20261031. See [C3_MODEL_SPEC.md](C3_MODEL_SPEC.md).

C3 is not started until secure artifact transfer and hash verification are implemented. No model performance or forecast is claimed.
