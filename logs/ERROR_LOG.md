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


## E0010 — 2026-10-25 — Holiday-shift helper test expected only two sessions
- Severity: Medium / validation-run failure.
- Symptom: unit test candidate_verification_checks_nearby_previous_sessions_for_holiday_shift failed because the helper returned all official trading sessions within the four-calendar-day inspection window (Nov 4, 3, 2 and 1), while the assertion expected only Nov 4 and Nov 3.
- Root cause: test expectation did not match the documented four-calendar-day window; the implementation's output was correct.
- Fix: update the expected list to include every trading session within the window. The expiry verifier stops once it finds an expiry, so additional dates are not fetched unnecessarily after a match.
- Validation required: rerun both workflow unit-test gates; no source reconciliation result is inferred from this test-only correction.


## Dhan authentication attempt — run 40175978898
- Status: FAILED or incomplete. The public archive route will still be attempted.
- Sensitive response fields and secrets were withheld. Inspect the Dhan-auth step status in Actions.


## Dhan data cross-check — run 40175978898
- Status: FAILED or unavailable. The public archive will remain the core input; independent Dhan cross-check did not pass.
- Failure responses and credentials were not added to the log. Inspect only sanitized Actions step diagnostics.


## Phase 3 official-source reconciliation — 2026-10-25T08:23:11.400151+00:00
- Status: BLOCKED
- Counts: {"candidate_expiries_checked": 402, "contract_unverified_expiries": 22, "contract_verified_expiries": 340, "daily_source_rows_compared": 1901, "daily_source_rows_expected": 1901, "daily_source_rows_missing_official_close": 0, "expiry_source_errors": 40, "minute_vs_official_abs_difference_max_points": 200.70000000000073, "minute_vs_official_abs_difference_median_points": 8.25, "minute_vs_official_abs_difference_p95_points": 32.44999999999709, "minute_vs_official_high_abs_difference_median_points": 0.049999999999272404, "minute_vs_official_high_mismatches_over_1_point": 197, "minute_vs_official_high_rows_compared": 1901, "minute_vs_official_low_abs_difference_median_points": 0.049999999999272404, "minute_vs_official_low_mismatches_over_1_point": 185, "minute_vs_official_low_rows_compared": 1901, "minute_vs_official_mismatches_over_1_point": 1717, "minute_vs_official_open_abs_difference_median_points": 0.0, "minute_vs_official_open_mismatches_over_1_point": 587, "minute_vs_official_open_rows_compared": 1901, "minute_vs_official_within_1_point": 184, "official_daily_rows": 1913}
- Errors: One or more candidate expiry dates were not confirmed in official F&O data, or minute archive daily closes differ from official NIFTY 50 closes by >1 point.
- Detailed outputs: data/reconciliation/


## E0013 — 2026-10-25 — Independent minute-source cross-check added
- Severity: High / source quality gate remains blocked.
- Action: Added automated comparison of a second public 1-minute NIFTY 50 archive with official NSE daily OHLC and current candidate archive.
- Source: https://github.com/technovusin/nifty50-historical-data; its README documents residual missing bars, frozen-price periods, and special-session exceptions.
- Validation: automated run pending. A third-party source is diagnostic only. No strategy promotion is authorized by cross-source agreement alone.


## Dhan authentication attempt — run 40177007671
- Status: FAILED or incomplete. The public archive route will still be attempted.
- Sensitive response fields and secrets were withheld. Inspect the Dhan-auth step status in Actions.


## Dhan data cross-check — run 40177007671
- Status: FAILED or unavailable. The public archive will remain the core input; independent Dhan cross-check did not pass.
- Failure responses and credentials were not added to the log. Inspect only sanitized Actions step diagnostics.


## Phase 3 official-source reconciliation — 2026-10-25T08:39:38.674792+00:00
- Status: BLOCKED
- Counts: {"candidate_expiries_checked": 402, "contract_unverified_expiries": 22, "contract_verified_expiries": 340, "daily_source_rows_compared": 1901, "daily_source_rows_expected": 1901, "daily_source_rows_missing_official_close": 0, "expiry_source_errors": 40, "minute_vs_official_abs_difference_max_points": 200.70000000000073, "minute_vs_official_abs_difference_median_points": 8.25, "minute_vs_official_abs_difference_p95_points": 32.44999999999709, "minute_vs_official_high_abs_difference_median_points": 0.049999999999272404, "minute_vs_official_high_mismatches_over_1_point": 197, "minute_vs_official_high_rows_compared": 1901, "minute_vs_official_low_abs_difference_median_points": 0.049999999999272404, "minute_vs_official_low_mismatches_over_1_point": 185, "minute_vs_official_low_rows_compared": 1901, "minute_vs_official_mismatches_over_1_point": 1717, "minute_vs_official_open_abs_difference_median_points": 0.0, "minute_vs_official_open_mismatches_over_1_point": 587, "minute_vs_official_open_rows_compared": 1901, "minute_vs_official_within_1_point": 184, "official_daily_rows": 1913}
- Errors: One or more candidate expiry dates were not confirmed in official F&O data, or minute archive daily closes differ from official NIFTY 50 closes by >1 point.
- Detailed outputs: data/reconciliation/


## E0014 — 2026-10-25 — ISO expiry-date strings were parsed with day-first fallback
- Severity: High / expiry calendar completeness.
- Symptom: the latest archive check produced 40 UDiFF source errors; examples expected 2024-12-04 but parsed the source date as 2024-04-12, and expected 2025-01-02 but parsed 2025-02-01.
- Root cause: _parse_date_values applied a generic dayfirst=True parser after compact-date parsing; ISO year-first strings were therefore interpreted with the month and day reversed.
- Fix attempted: use explicit format masks for compact YYYYMMDD and ISO YYYY-MM-DD; parse ISO timestamps year-first; apply day-first fallback only to legacy formats.
- Validation: tests added for ISO, compact and legacy date variants. Await a full Phase 3 workflow to establish whether remaining errors clear.
- Residual risk: the existing run result is still only 340/402 confirmed; do not mark the expiry calendar validated before the fresh run.

## E0015 — 2026-10-25 — Cross-check mistakenly used the primary input repository
- Severity: High / research-method independence.
- Symptom: the “alternative” series showed a zero-point median difference to the primary series, which could falsely be read as independent corroboration.
- Root cause: scripts/fetch_data.py fetches technovusin/nifty50-historical-data, and scripts/compare_alternative_minute_source.py fetched the same repo. The overlap had 1,901 exact daily-close matches out of 1,901.
- Fix attempted: mark the existing result MIRROR_NOT_INDEPENDENT; stop describing it as independent evidence; add a comparator for sandeepkapri/Nifty50-Minute-Data with explicit partial-coverage and source-lineage caveats.
- Validation required: inspect source coverage and all OHLC metrics from the new run. A separate GitHub repository does not prove independent market-data vendor lineage.
- Residual risk: close mismatch from 2019 through 2026 remains unresolved, and the secondary source ends on 2024-03-27.


## Phase 3 official-source reconciliation — 2026-10-25T08:48:38.145298+00:00
- Status: BLOCKED
- Counts: {"candidate_expiries_checked": 402, "contract_unverified_expiries": 22, "contract_verified_expiries": 340, "daily_source_rows_compared": 1901, "daily_source_rows_expected": 1901, "daily_source_rows_missing_official_close": 0, "expiry_source_errors": 40, "minute_vs_official_abs_difference_max_points": 200.70000000000073, "minute_vs_official_abs_difference_median_points": 8.25, "minute_vs_official_abs_difference_p95_points": 32.44999999999709, "minute_vs_official_high_mismatches_over_1_point": 197, "minute_vs_official_low_mismatches_over_1_point": 185, "minute_vs_official_mismatches_over_1_point": 1717, "minute_vs_official_open_mismatches_over_1_point": 587, "minute_vs_official_within_1_point": 184, "official_daily_rows": 1913}
- Errors: 340 of 402 candidate dates were confirmed (including two shifted expiries), 22 were not verified, and 40 had source-validation errors. Artifact examples reveal ISO dates were incorrectly parsed with a day-first fallback; fix added for revalidation.; 1,717 of 1,901 daily minute-source closes differ from official NSE close by more than the pre-registered 1-point tolerance.
- Detailed outputs: data/reconciliation/


## E0016 — 2026-10-25 — Pre-run code review caught regex escaping and missing yearly append in secondary-source script
- Severity: Medium / test readiness.
- Symptom: inspection of the just-created patch found regex character classes over-escaped in the ISO date parser and the new secondary-source comparator lacked a yearly-row append.
- Root cause: serialization of backslashes during GitHub API source updates and an incomplete loop tail in the new comparator.
- Fix: correct the regular-expression strings in the repository file and append one yearly metric row after each grouped calculation.
- Validation: automated workflow tests and output generation must pass before accepting either fix.
- Residual risk: no additional expiry/source findings are inferred from a code review alone.


## Phase 3 official-source reconciliation — 2026-10-25T08:49:59.243276+00:00
- Status: BLOCKED
- Counts: {"candidate_expiries_checked": 402, "contract_unverified_expiries": 22, "contract_verified_expiries": 340, "daily_source_rows_compared": 1901, "daily_source_rows_expected": 1901, "daily_source_rows_missing_official_close": 0, "expiry_source_errors": 40, "minute_vs_official_abs_difference_max_points": 200.70000000000073, "minute_vs_official_abs_difference_median_points": 8.25, "minute_vs_official_abs_difference_p95_points": 32.44999999999709, "minute_vs_official_high_mismatches_over_1_point": 197, "minute_vs_official_low_mismatches_over_1_point": 185, "minute_vs_official_mismatches_over_1_point": 1717, "minute_vs_official_open_mismatches_over_1_point": 587, "minute_vs_official_within_1_point": 184, "official_daily_rows": 1913}
- Errors: 340 of 402 candidate dates were confirmed (including two shifted expiries), 22 were not verified, and 40 had source-validation errors. Artifact examples reveal ISO dates were incorrectly parsed with a day-first fallback; fix added for revalidation.; 1,717 of 1,901 daily minute-source closes differ from official NSE close by more than the pre-registered 1-point tolerance.
- Detailed outputs: data/reconciliation/


## GitHub Actions failure — run 40178173663
- Status: BLOCKED. One or more workflow steps failed; inspect the Actions run for the exact failing step.
- The workflow is configured to continue with public data when the optional Dhan branch fails.
- No secrets, access tokens, PINs or TOTP values should be copied from runner diagnostics into repository logs.


## E0017 — 2026-10-25 — Secondary-source test date was outside the source coverage window
- Severity: Medium / test correctness.
- Symptom: aggregate_sandeep_frame test used 2 January 2025 although the configured secondary dataset comparison window ends 27 March 2024; the aggregator correctly returned no rows.
- Root cause: the test fixture did not respect the declared source date coverage.
- Fix: changed the synthetic fixture to 2 January 2023; the expected session remains the same relative to the source's supported interval.
- Validation: rerun CI tests and the secondary-source comparison; do not infer market-data metrics from the failed test.


## E0018 — 2026-10-25 — Broad main-workflow path filter caused unnecessary concurrent workflows
- Severity: Medium / automation reliability.
- Symptom: Phase 3 parser and source-audit edits also triggered the full core research workflow because the path filter included all scripts, all tests, all docs, and the manuscript. Both workflows share a serialized group and their pending runs could interrupt the desired source validation.
- Root cause: the core research workflow was triggered by files unrelated to the core label/model pipeline.
- Fix: restrict main-workflow push paths to the data fetch, core analysis, status update, Dhan helper scripts, core test file and requirements. Phase 3 parser/test/doc changes now trigger only the Phase 3 workflow.
- Validation: inspect Actions after this commit; the Phase 3 reconciliation should execute at the latest branch tip without a newly triggered full model run.
- Residual risk: scheduled or manually dispatched core workflow can still share the research log/README, so serialization remains enabled.


## Phase 3 official-source reconciliation — 2026-10-25T08:53:10.741957+00:00
- Status: BLOCKED
- Counts: {"candidate_expiries_checked": 402, "contract_unverified_expiries": 22, "contract_verified_expiries": 340, "daily_source_rows_compared": 1901, "daily_source_rows_expected": 1901, "daily_source_rows_missing_official_close": 0, "expiry_source_errors": 40, "minute_vs_official_abs_difference_max_points": 200.70000000000073, "minute_vs_official_abs_difference_median_points": 8.25, "minute_vs_official_abs_difference_p95_points": 32.44999999999709, "minute_vs_official_high_mismatches_over_1_point": 197, "minute_vs_official_low_mismatches_over_1_point": 185, "minute_vs_official_mismatches_over_1_point": 1717, "minute_vs_official_open_mismatches_over_1_point": 587, "minute_vs_official_within_1_point": 184, "official_daily_rows": 1913}
- Errors: 340 of 402 candidate dates were confirmed (including two shifted expiries), 22 were not verified, and 40 had source-validation errors. Artifact examples reveal ISO dates were incorrectly parsed with a day-first fallback; fix added for revalidation.; 1,717 of 1,901 daily minute-source closes differ from official NSE close by more than the pre-registered 1-point tolerance.
- Detailed outputs: data/reconciliation/


## E0019 — 2026-10-25 — Mixed legacy date formats require format-specific parsing
- Severity: High / expiry verification gate.
- Symptom: after the ISO regex correction, 18/19 tests passed; the remaining date parser test returned NaT for legacy numeric date 04-12-2024 when mixed in the same vector with 11-Jul-2024.
- Root cause: pandas inferred one generic format for a mixed legacy-format vector; the string DD-MM-YYYY did not parse under the inferred month-name format.
- Fix attempted: parse common numeric day-first, abbreviated-month day-first, compact and ISO formats with explicit formats; use a scalar day-first fallback only for uncommon legacy strings.
- Validation required: fresh unit tests and full source reconciliation. No new source status is inferred before CI confirms.
- Residual risk: unknown source-specific date strings may still fall to scalar parsing; validation errors remain explicit.


## Phase 3 official-source reconciliation — 2026-10-25T08:58:02.301767+00:00
- Status: BLOCKED
- Counts: {"candidate_expiries_checked": 402, "contract_unverified_expiries": 0, "contract_verified_expiries": 402, "daily_source_rows_compared": 1901, "daily_source_rows_expected": 1901, "daily_source_rows_missing_official_close": 0, "expiry_source_errors": 0, "minute_vs_official_abs_difference_max_points": 200.70000000000073, "minute_vs_official_abs_difference_median_points": 8.25, "minute_vs_official_abs_difference_p95_points": 32.44999999999709, "minute_vs_official_high_abs_difference_median_points": 0.049999999999272404, "minute_vs_official_high_mismatches_over_1_point": 197, "minute_vs_official_high_rows_compared": 1901, "minute_vs_official_low_abs_difference_median_points": 0.049999999999272404, "minute_vs_official_low_mismatches_over_1_point": 185, "minute_vs_official_low_rows_compared": 1901, "minute_vs_official_mismatches_over_1_point": 1717, "minute_vs_official_open_abs_difference_median_points": 0.0, "minute_vs_official_open_mismatches_over_1_point": 587, "minute_vs_official_open_rows_compared": 1901, "minute_vs_official_within_1_point": 184, "official_daily_rows": 1913}
- Errors: One or more candidate expiry dates were not confirmed in official F&O data, or minute archive daily closes differ from official NIFTY 50 closes by >1 point.
- Detailed outputs: data/reconciliation/


## Dhan authentication attempt — run 40180474671
- Status: FAILED or incomplete. The public archive route will still be attempted.
- Sensitive response fields and secrets were withheld. Inspect the Dhan-auth step status in Actions.


## Dhan data cross-check — run 40180474671
- Status: FAILED or unavailable. The public archive will remain the core input; independent Dhan cross-check did not pass.
- Failure responses and credentials were not added to the log. Inspect only sanitized Actions step diagnostics.


## GitHub Actions failure — run 40180566929
- Status: BLOCKED. One or more workflow steps failed; inspect the Actions run for the exact failing step.
- The workflow is configured to continue with public data when the optional Dhan branch fails.
- No secrets, access tokens, PINs or TOTP values should be copied from runner diagnostics into repository logs.


## Dhan authentication attempt — run 40180819590
- Status: FAILED or incomplete. The public archive route will still be attempted.
- Sensitive response fields and secrets were withheld. Inspect the Dhan-auth step status in Actions.


## Dhan data cross-check — run 40180819590
- Status: FAILED or unavailable. The public archive will remain the core input; independent Dhan cross-check did not pass.
- Failure responses and credentials were not added to the log. Inspect only sanitized Actions step diagnostics.
