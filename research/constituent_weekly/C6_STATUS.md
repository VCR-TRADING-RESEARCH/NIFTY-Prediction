# C6 Final Manuscript and Independent Summary Audit — Status

- **Phase:** C6 — closeout manuscript and independent summary audit
- **Status:** <badge> AUTOMATED SUMMARY AUDIT PASS WITH LIMITATIONS
- **Audit workflow:** [41411057657 — SUCCESS](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41411057657)
- **C1:** PARTIAL
- **C2:** PASS WITH C1 LIMITATIONS
- **C3:** EXPLORATORY COMPLETE — NO STOCK EDGE
- **C3-X:** EXPLORATORY COMPLETE — NIFTY AGGREGATION INCONCLUSIVE
- **C4 confirmatory:** GATED
- **C5:** BLOCKED / NOT RUN
- **Trading:** NOT VALIDATED

## Automated audit outcome

The C6 workflow independently re-calculated:
- C2/C3 row and cycle accounting;
- the cycle-macro logistic-minus-momentum difference;
- the C3 four-cycle bootstrap interval crossing zero;
- C3-X NIFTY accuracy and balanced accuracy from its confusion matrix;
- the C3-X one-correct-cycle accuracy difference and bootstrap interval;
- fail-closed C5 and C4 gate states.

The same workflow passed the manuscript-section and chart-file checks. The final run is [41411057657](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41411057657).

**Audit boundary:** this is an automated independent check of sanitised summaries, arithmetic and repository gate states. It is not a fresh reconstruction from encrypted raw market data, does not independently re-adjudicate the 711 unresolved corporate-action candidates, and is not an external human audit. C6 therefore passes with explicit limitations.

## Deliverables

- [Full research manuscript](MANUSCRIPT.md)
- [Audit report](C6_AUDIT_REPORT.md)
- [Consolidated sanitised results](C6_RESULTS_SUMMARY.json)
- [C3 stock-model chart](C3_HOLDOUT_ACCURACY.svg)
- [C3-X NIFTY meta-model chart](C3X_NIFTY_HOLDOUT_METRICS.svg)
- [C5 economic gate decision](C5_COST_GATE.md)
- [Independent arithmetic audit script](../../scripts/constituent_weekly/audit_bup01_final.py)

No C6 result certifies C1, unlocks confirmatory C4, or makes a trading claim. The workflow has both automatic branch-push and manual dispatch triggers.
