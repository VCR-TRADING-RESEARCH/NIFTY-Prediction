# C1 Complex-Event Weekly-Cycle Exclusion Sensitivity

Updated: 2026-11-02T20:59:24.469306+00:00
Result: SENSITIVITY_PRESERVES_47_94_FOR_ALL_258_CYCLES

## Frozen C2 source

- C2 run: https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41398864378
- C2 source commit: bff9fae12dbc1396a9e322c3001096bf4d5b0709
- Frozen C2 manifest: 9d263e441f09c70693e30f1541440ac6b249c5293da61faceb0af729d699c305
- Accepted cycles: 258; stock rows: 12807.

## Event-to-cycle overlap

- Complex candidates reviewed: 37.
- Events intersecting at least one member window: 16.
- Unique affected constituent-cycle pairs: 14.
- Affected expiry cycles: 13.
- Previously flagged pairs: 0.
- Pairs absent from C2 panel: 0.
- Additional primary-eligible rows excluded: 14.

## Registered 47-member / 94% rule

- Before extra exclusions: 258 / 258 cycles pass.
- After extra exclusions: 258 / 258 cycles pass.
- Failing cycles after exclusion: 0.
- Minimum remaining members: 47.
- Minimum remaining fraction: 0.94.
- Sensitivity status: PASS_47_94_ALL_CYCLES.

## Interpretation and limitations

This is a conservative exclusion sensitivity, not an adjustment-factor calculation. It excludes affected constituent-cycle observations rather than inferring split, bonus, rights, demerger or debenture price factors.
The frozen C2 panel, C3 forecasts, holdout and model metrics were not changed or used for tuning. No model was fitted.
A passing sensitivity is not itself C1 acceptance. Full historical identity, price-series continuity, rights TERP/merger scheme treatment and the 49 secondary-event timing gates remain separate.
Only aggregate counts and threshold summaries are published; event dates, securities and underlying vendor rows remain private.
