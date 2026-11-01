# C2 formal acceptance report

**Decision:** PASS — panel construction and registered C2 acceptance checks completed.

- Workflow: [41353406358](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41353406358)
- Runner commit: [4f37920](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/commit/4f37920c7dc2d719be2c310a1555962343c1616b)
- Methodology: `bup01-c2-panel-v1`
- Input manifest SHA-256: `715623a04ff8e32a2a7b0a744a1e4b590d37f758c708eb5d7f5352d7dd00a553`
- Scheduled cycles: 258
- Valid NIFTY targets: 258/258 (100%)
- Cycles satisfying at least 47 valid members and at least 94% of point-in-time tradable members: 258/258
- Constituent-cycle rows: 12,807; distinct symbols: 61
- Duplicate index-cycle rows: 0; duplicate constituent-cycle rows: 0
- Holdout boundary: cycle 206, anchor 2025-10-29, expiry 2025-11-04; final 20% holdout.
- Identity-flagged rows: 292; known action-crossing rows: 3; primary-flagged rows: 293.
- Stock daily-feature missing rows: 92; these did not invalidate the registered per-cycle 47/94% gate.
- Index flat labels: 0; stock flat labels: 19.
- Encrypted AES-GCM frozen-panel cache: stock ciphertext 1,654,615 bytes; index ciphertext 30,334 bytes. Raw panel values remain encrypted.

**Limitations:** Historical identity and event-level corporate-action checks were waived as progression preconditions by user direction, not declared passed. No unverified corporate-action adjustment was applied. Flagged observations remain excluded from the primary sensitivity panel. C2 did not fit models; stock modelling is C3, NIFTY meta-model is C4. This acceptance is not evidence of prediction skill or trading profitability.

**Next phase:** C3 pooled stock baselines/models using the frozen panel, chronological cycle-level splits, minimum 104 prior cycles, and the sealed final 20% holdout. The encrypted panel must be transferred to the C3 workflow as ciphertext only and decrypted in Actions using the existing secret; no plaintext price data may be committed or published.
