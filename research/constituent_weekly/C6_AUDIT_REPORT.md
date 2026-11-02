# C6 Automated Summary Audit Report

**Date:** 2026-11-02  
**Workflow:** [41411057657](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41411057657)  
**Decision:** PASS WITH LIMITATIONS

## Checks passed

| Check | Result | Evidence |
|---|---|---|
| C2 panel row/cycle accounting | PASS | 258 cycles; 258/258 valid index targets; 12,807 stock-cycle rows; duplicate keys zero |
| C3 OOF row accounting | PASS | 4,929 development + 2,583 holdout = 7,512 |
| C3 cycle accounting | PASS | 102 development + 52 holdout = 154 |
| C3 holdout isolation | PASS (code/protocol audit) | Final 52 cycles fitted only on development cycles 0–205 |
| Paired C3 accuracy difference | PASS | Cycle-macro difference re-computes to −0.0237255 |
| C3 bootstrap interpretation | PASS | 95% interval [−0.1003779, +0.0428564] crosses zero |
| C3-X confusion matrix | PASS | 26/51 accuracy = 0.509804; balanced accuracy = 0.534539 |
| C3-X paired accuracy difference | PASS | One additional correct cycle = 1/51 = 0.019608 |
| C3-X bootstrap interpretation | PASS | 95% interval [−0.254902, +0.254902] crosses zero |
| C4/C5 fail-closed decisions | PASS | C4 confirmatory GATED; C5 BLOCKED_NOT_RUN |
| Manuscript completeness and figures | PASS | Required sections and both SVG charts present |

## Workflow evidence

The final Actions run completed successfully. The job log contains:
- C6_AUDIT_PASS_WITH_LIMITATIONS
- C2 sample accounting, C3 split and paired-difference arithmetic passed.
- C3-X confusion-matrix accuracy/balanced-accuracy checks passed.
- Manuscript structure and figures passed.

## Scope and limitations

This is an automated summary-level mathematical and repository-state audit. It checks sanitised values and registered gate states; it does not download or decrypt the full raw market panel, independently reproduce model predictions from raw bars, or re-adjudicate the underlying issuer/exchange evidence for the 711 candidate member corporate-action events. It is not an external human audit.

C1 remains PARTIAL, so C4 confirmatory is still gated. C5 is blocked because neither a reliable forecast nor a fixed instrument specification is available. No execution-cost backtest, net P&L, or trading strategy is accepted.

## Final disposition

BUP-01 exploratory closeout is complete with limitations. The negative/inconclusive findings are retained. Any continuation that reopens confirmatory testing must first close C1 identity/corporate-action evidence and use a single frozen, fully auditable dataset and holdout protocol.
