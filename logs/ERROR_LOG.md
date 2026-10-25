# Error, Omission and Correction Log

Do not delete earlier entries. Add dated entries with severity, symptom, root cause, fix, test and residual risk.

## E0001 — 2026-10-25 — Repository had no initial files
- Severity: Medium / bootstrapping blocker.
- Symptom: GitHub contents API returned 404 with message “This repository is empty” for README and expected plan/log paths.
- Root cause: No initial commit or branch contents existed.
- Fix: Created initial README commit and seeded dedicated research/phase-0-foundation branch.
- Validation: GitHub commit API returned a commit SHA; repository metadata confirmed default branch main and authenticated admin/push permissions.
- Residual risk: No previous experiments, hidden data files or logs could be resumed because the repository was empty.

## E0002 — 2026-10-25 — Local shell had no network DNS
- Severity: Low / data execution limitation for current interactive session.
- Symptom: Python urllib test from the container failed with “Temporary failure in name resolution”.
- Root cause: Current container execution environment cannot download external files directly.
- Fix: Verified source metadata through connected GitHub/web tools and designed GitHub Actions to download/cache data in the repository runtime.
- Residual risk: This assistant session has not locally executed the full historical backtest. A GitHub Actions run is required for empirical outputs.

## E0003 — 2026-10-25 — Intraday source has published data-quality caveats
- Severity: High until independently reconciled.
- Symptom: Upstream README lists missing minute bars, frozen-price stretches and partial/special sessions.
- Root cause: Third-party archival/cleaning imperfections can affect anchor and closing-price selection.
- Fix: Require OHLC invariants, duplicate/missing-session reporting, raw row timestamps, explicit expiry-calendar status and sample comparison to NSE/Dhan.
- Residual risk: Do not certify confirmatory inference until source validation passes.


## GitHub Actions failure — run 40167544027
- Status: BLOCKED. One or more workflow steps failed; inspect the Actions run for the exact failing step.
- The workflow is configured to continue with public data when the optional Dhan branch fails.
- No secrets, access tokens, PINs or TOTP values should be copied from runner diagnostics into repository logs.


## Dhan authentication attempt — run 40167611476
- Status: FAILED or incomplete. The public archive route will still be attempted.
- Sensitive response fields and secrets were withheld. Inspect the Dhan-auth step status in Actions.


## Dhan data cross-check — run 40167611476
- Status: FAILED or unavailable. The public archive will remain the core input; independent Dhan cross-check did not pass.
- Failure responses and credentials were not added to the log. Inspect only sanitized Actions step diagnostics.


## E0004 — 2026-10-25 — Independent close cross-check failed the source gate
- Severity: Critical / Phase 1 acceptance blocked.
- Symptom: 368 of 402 candidate expiry-date daily closes differed from the independent Yahoo Finance daily close by more than one index point; across 2,352 matched daily sessions, median absolute difference was about 7.20 points and 95th percentile about 30.52 points. The archive also had repeated-close runs longer than 10 bars on 63 sessions, maximum 239 bars.
- Root cause: not yet isolated; potential causes include bad/frozen source bars, a different close definition, or timestamp/session alignment. Do not assume any single cause without row-level diagnosis.
- Fix attempted: added an independent daily-close comparison and surfaced the result in the machine-readable quality report and README.
- Validation: comparison completed; source quality gate failed visibly rather than silently accepting the data.
- Required next action: create a date-level mismatch report, verify a sample and then all mismatches against official NSE/NSE Indices data or a trusted vendor; investigate repeated-close runs; only regenerate labels after this is resolved.
- Residual risk: all metrics in run 40167611476 are exploratory and must not be used for trading.

## E0005 — 2026-10-25 — Dhan cross-check did not produce data
- Severity: High / independent intraday validation missing.
- Symptom: no Dhan bars were available for comparison; authentication and fetch steps were logged as failed or unavailable without exposing secrets.
- Root cause: not conclusively diagnosed from sanitized run outputs; the organization secrets may not be exposed to this branch/workflow or the token/API request may need correction.
- Fix attempted: secure job-only token generation, a security-master lookup, optional Dhan intraday fetch, and graceful continuation on public data were implemented.
- Required next action: inspect sanitized Actions step outcomes and confirm secret visibility/API schema. Never print token, PIN or TOTP values. Do not hard-code a security ID as a workaround.
- Residual risk: no independent intraday validation exists for the current run.


## Dhan authentication attempt — run 40169213949
- Status: FAILED or incomplete. The public archive route will still be attempted.
- Sensitive response fields and secrets were withheld. Inspect the Dhan-auth step status in Actions.


## Dhan data cross-check — run 40169213949
- Status: FAILED or unavailable. The public archive will remain the core input; independent Dhan cross-check did not pass.
- Failure responses and credentials were not added to the log. Inspect only sanitized Actions step diagnostics.


## 2026-10-25T07:03:57.848235+00:00 — PySR experimental track
- Severity: Medium; this track is non-blocking and results remain exploratory.
- Symptom: ModuleNotFoundError: No module named 'pysr'
- Response: record failure, retain other tracks, do not promote a model.
- Secrets: no environment values or request bodies recorded.


## E0006 — 2026-10-25 — PySR installation was skipped on first Phase 2 run
- Severity: Medium; optional track incomplete, other tracks remained available.
- Symptom: experimental report returned ModuleNotFoundError: No module named 'pysr'.
- Root cause: workflow conditional evaluated to skip the install step on a push event.
- Fix: removed the push-sensitive condition; install step now runs and checks import explicitly while allowing other tracks to complete if unavailable.
- Validation: rerun queued as Actions run 40171512727; final PySR status is pending.
- Residual risk: PySR depends on Julia runtime availability and can fail for environmental reasons. Do not interpret failure as evidence for or against predictive utility.


## E0007 — 2026-10-25 — PySR workflow condition corrected and run completed
- Severity: Medium; optional symbolic-regression track was initially omitted.
- Symptom: initial Phase 2 result recorded `ModuleNotFoundError: No module named 'pysr'`.
- Root cause: install step was skipped on push due to an event-sensitive condition.
- Fix: workflow now attempts PySR installation on push and verifies the import; committed feature snapshot avoids unrelated raw-data rebuilds by default.
- Validation: Actions run [40171572720](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40171572720) completed successfully; PySR completed, core/experimental tests passed, artifacts were uploaded.
- Result: held-out return RMSE 0.014925; R² -0.00124. Negative R² indicates no improvement over a constant-mean return predictor on this holdout.
- Residual risk: labels/calendar remain unverified, close-source mismatch gate remains failed, and no executable costed P&L was tested. Phase 2 completion is computational, not strategy acceptance.
