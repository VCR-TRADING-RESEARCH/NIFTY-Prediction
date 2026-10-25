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


## Phase 3 official-source reconciliation — 2026-10-25T07:17:36.789826+00:00
- Status: BLOCKED
- Counts: {}
- Errors: HTTPError: 401 Client Error: Unauthorized for url: https://www.niftyindices.com/Backpage.aspx/getHistoricaldatatabletoString
- Detailed outputs: data/reconciliation/


## Dhan authentication attempt — run 40172557963
- Status: FAILED or incomplete. The public archive route will still be attempted.
- Sensitive response fields and secrets were withheld. Inspect the Dhan-auth step status in Actions.


## Dhan data cross-check — run 40172557963
- Status: FAILED or unavailable. The public archive will remain the core input; independent Dhan cross-check did not pass.
- Failure responses and credentials were not added to the log. Inspect only sanitized Actions step diagnostics.


## Phase 3 official-source reconciliation — 2026-10-25T07:49:08.356743+00:00
- Status: BLOCKED
- Counts: {}
- Errors: HTTPError: 401 Client Error: Unauthorized for url: https://www.niftyindices.com/Backpage.aspx/getHistoricaldatatabletoString
- Detailed outputs: data/reconciliation/


## E0006 — 2026-10-25 — Official source gate remains blocked after first full NSE run
- Severity: Critical / Phase 1 remains blocked.
- Evidence: run 40174191441 collected 1,913 official daily close rows and compared 1,901 candidate sessions. 1,717 absolute differences exceeded the pre-registered 1-point tolerance; median absolute difference 8.25 points, P95 32.45 and maximum 200.7. The initial expiry check confirmed 359/402 candidate dates and left 43 unconfirmed.
- Root cause is not fully isolated. Implementation defects found: the downloader tried UDiFF before the legacy format for all historical dates and used archives.nseindia.com as the primary UDiFF host. Daily close differences may additionally arise from the candidate intraday archive or close/session alignment.
- Fix attempted: prefer legacy URL through 5 July 2024 and UDiFF at nsearchives.nseindia.com from 8 July 2024; validate archive schema/trade date; prefer actual expiry field when populated; add tests for source order, date mismatch and actual expiry; serialize workflows that share a branch.
- Validation required: tests plus a fresh official reconciliation. Parser tests alone cannot validate 402 historical dates.
- Residual risk: do not accept model results or begin trade-cost optimization until all candidate labels have official expiry evidence and the price discrepancies are explained.

## E0007 — 2026-10-25 — Parallel Actions commits raced on the same branch
- Severity: High / research traceability.
- Symptom: Phase 3 run 40174191441 failed its final commit on a rebase conflict in logs/ERROR_LOG.md and logs/RESEARCH_LOG.md; main research run 40174191439 completed analysis but its push was rejected as non-fast-forward.
- Root cause: both workflows ran concurrently on research/phase-3-official-source-reconciliation and each changed the same logs/README/results paths.
- Fix attempted: both workflows now share a per-ref concurrency group with cancellation disabled; the main research commit step rebases with autostash before pushing.
- Validation required: confirm the next jobs serialize and status/results commit successfully. Artifacts remain the fallback evidence.
- Residual risk: an external push or rebase conflict can still require Git repair.


## Phase 3 official-source reconciliation — 2026-10-25T08:03:49.299759+00:00
- Status: BLOCKED
- Counts: {"candidate_expiries_checked": 402, "contract_verified_expiries": 338, "daily_source_rows_compared": 1901, "daily_source_rows_expected": 1901, "daily_source_rows_missing_official_close": 0, "expiry_source_errors": 38, "minute_vs_official_mismatches_over_1_point": 1717, "official_daily_rows": 1913}
- Errors: One or more candidate expiry dates were not confirmed in official F&O data, or minute archive daily closes differ from official NIFTY 50 closes by >1 point.
- Detailed outputs: data/reconciliation/


## Dhan authentication attempt — run 40175103450
- Status: FAILED or incomplete. The public archive route will still be attempted.
- Sensitive response fields and secrets were withheld. Inspect the Dhan-auth step status in Actions.


## Dhan data cross-check — run 40175103450
- Status: FAILED or unavailable. The public archive will remain the core input; independent Dhan cross-check did not pass.
- Failure responses and credentials were not added to the log. Inspect only sanitized Actions step diagnostics.


## E0008 — 2026-10-25 — NSE UDiFF validation failures were not diagnostic enough
- Severity: High / historical expiry calendar remains unverified.
- Symptom: Phase 3 run 40174991974 confirmed 338/402 candidate expiry dates, left 26 not verified, and returned 38 source-validation errors. The stored error text exposed only the exception type (ValueError), not the reason.
- Potential causes include un-warmed archive sessions / HTML interstitials, trade-date mismatches or schema variants. Exact cause is not yet proven and will be captured in the next run.
- Fix attempted: warm the NSE derivatives reports page per worker session; include sanitized exception details with bounded length; inspect nearby prior sessions only where no expiry was found on the candidate day; generate yearly summaries automatically.
- Validation required: next Actions run must show detailed failure causes and refreshed yearly outputs. Do not accept the expiry calendar yet.

## E0009 — 2026-10-25 — Official-close mismatch requires OHLC diagnosis
- Severity: Critical / source-quality blocker.
- Symptom: 1,717/1,901 minute-source session closes differed from official NSE NIFTY 50 close by >1 point; median difference 8.25, P95 32.45 and maximum 200.7 points.
- Root cause not isolated. The candidate archive documents frozen/missing/partial sessions, but many large close differences do not have long unchanged-close runs, so freezing alone cannot explain the full pattern.
- Fix attempted: retain official daily open/high/low where endpoint fields exist, compare minute-source O/H/L and close separately, and preserve the one-point close tolerance until evidence clarifies the discrepancy.
- Residual risk: no model advancement or trading strategy approval until the source/close-definition discrepancy is explained or a trusted alternative intraday source is validated.


## GitHub Actions failure — run 40175798910
- Status: BLOCKED. One or more workflow steps failed; inspect the Actions run for the exact failing step.
- The workflow is configured to continue with public data when the optional Dhan branch fails.
- No secrets, access tokens, PINs or TOTP values should be copied from runner diagnostics into repository logs.


## Phase 3 official-source reconciliation — 2026-10-25T08:15:03.103281+00:00
- Status: BLOCKED
- Counts: {"candidate_expiries_checked": 402, "contract_unverified_expiries": 26, "contract_verified_expiries": 338, "daily_source_rows_compared": 1901, "daily_source_rows_expected": 1901, "daily_source_rows_missing_official_close": 0, "expiry_source_errors": 38, "minute_vs_official_abs_difference_max_points": 200.7, "minute_vs_official_abs_difference_median_points": 8.25, "minute_vs_official_abs_difference_p95_points": 32.45, "minute_vs_official_mismatches_over_1_point": 1717, "minute_vs_official_within_1_point": 184, "official_daily_rows": 1913}
- Errors: 338/402 candidate dates were confirmed; 26 were not verified and 38 produced source-validation errors. Detailed failure diagnostics were not preserved by this run.; 1,717 of 1,901 daily minute-source closes differ from official NSE NIFTY 50 closes by more than the pre-registered 1-point tolerance.
- Detailed outputs: data/reconciliation/
