# Phase 3 — Official Source and Expiry Reconciliation

**Branch:** `research/phase-3-official-source-reconciliation`  
**Status:** BLOCKED — corrected audit run 40181901081 completed; 402/402 candidate expiries verified, but 1,719/1,903 preserved archive daily closes differ from official closes by more than one point. The prior apparent zero-mismatch PASS was circular and is invalidated.  
**Objective:** Resolve the known daily-close discrepancy and heuristic expiry calendar using exchange/index-publisher data before any further model discovery.

## Research questions

1. Do the minute archive's daily close values agree with the official NIFTY 50 price-return index close?
2. Does each candidate weekly expiry date correspond to a NIFTY index-option expiry in NSE's official F&O bhavcopy?
3. Which rows remain unverified because the source endpoint, schema, or archive file is unavailable?
4. After source correction, how many cycles can be considered eligible for a new, pre-registered model evaluation?

## Data sources and priority

- **Official index OHLC:** NSE Indices historical NIFTY 50 price-return OHLC page and its public endpoint. The endpoint is undocumented and may change; all outputs are cached and parsed defensively. Reference: https://www.niftyindices.com/reports/historical-data
- **Official contract evidence:** NSE F&O daily bhavcopy archives, legacy CSV ZIP through 5 July 2024 and UDiFF CSV ZIP from 8 July 2024 onward. Reference: https://www.nseindia.com/all-reports-derivatives and https://www.nseindia.com/report-detail/fo_eq_security
- **Expiry rules:** Official circulars show Thursday weekly expiry through August 2025, then Tuesday for September 2025 onward. The March 2025 Monday proposal was withheld. References: [NSE Circular FAOP68747 (25 Jun 2025)](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAOP68747.pdf), [NSE Circular FAOP68685 (23 Jun 2025)](https://nsearchives.nseindia.com/content/circulars/FAOP68685.pdf), and [current NIFTY 50 contract specification](https://www.nseindia.com/static/products-services/equity-derivatives-nifty50). Historical contract evidence, not a weekday generator, is the acceptance source.
- **Candidate input only:** Existing minute archive and candidate calendar. Neither is treated as ground truth.

## Methods

1. Fetch official NIFTY 50 daily OHLC in chunks no longer than 350 days. Cache immutable date-range CSVs to avoid repeated downloads.
2. Compare every overlapping date with the minute archive's last valid session close. Write the row-level differences and a machine-readable source report.
3. For each nominal candidate expiry, check the latest official session and, only if no expiry is present, inspect nearby prior trading sessions within four calendar days to verify holiday-shifted dates, including special-session days.
4. Fetch the NSE F&O bhavcopy for that session; parse both legacy and UDiFF schemas and confirm that a NIFTY OPTIDX call/put contract expires on the session date.
5. Record every source failure, missing date, schema mismatch, or unconfirmed expiry. Do not silently convert a failure into a verified calendar row.
6. Run unit tests on parsing and weekday-regime logic before any data/model work.
7. Keep all outcomes, including partial failures, in `data/reconciliation/`, the research log, and the error log.

## Acceptance gates

- Every cycle used for confirmatory analysis must have contract-level expiry-date evidence.
- Official daily closes must match the minute archive within the pre-registered one-point tolerance; mismatches require date-level investigation, not automatic correction.
- Source coverage must include the entire label period. A partially available source means the gate remains blocked.
- The source report must be reproducible from cached official snapshots and must include row counts, exact comparison coverage, and errors.
- Only after passing this gate may the team rebuild labels and define a fresh untouched model holdout.
- No trading strategy can be accepted without a separate instrument-level backtest using date-effective Paytm Money brokerage, exchange/statutory fees, bid-ask spread, slippage, and conservative fill assumptions.

## Bounded execution

The workflow runs on branch push, monthly schedule, and manual dispatch. It has a 60-minute cap, caches source data, and continues after source errors so the final report can document them. This is one bounded validation pass; do not loop or retry indefinitely. If NSE/NiftyIndices blocks the workflow or historical contract archives cannot be obtained, record the limitation and request a decision only after free official and public alternatives have been attempted.

## Outputs

- `data/reconciliation/source_reconciliation_report.json`
- `data/reconciliation/nifty50_official_daily.csv`
- `data/reconciliation/minute_vs_official_daily.csv`
- `data/reconciliation/expiry_verification.csv`
- `logs/RESEARCH_LOG.md` and `logs/ERROR_LOG.md`
- Updated README status and Phase 3 pull request.

## Current prior blockers

The completed official-source pass (40174191441) compared 1,901 sessions: 1,717 daily closes differ from official NSE close by more than one point (median absolute difference 8.25; P95 32.45; maximum 200.7 index points). The latest run (40174991974) reported 338/402 confirmed, 26 not verified and 38 source-validation errors. The error strings previously retained only the exception type, so the downloader is being amended to preserve a sanitized validation reason and warm an NSE session before archive requests. The downloader was found to try the UDiFF URL first even for pre-8-Jul-2024 dates, and to use an alternate host as the primary UDiFF URL. The next run prioritizes the format matching each historical period and validates archive trade dates. The 43 rows remain unresolved until revalidation.


## Independent minute archive
Phase 3 now retrieves the public 1-minute NIFTY 50 dataset at https://github.com/technovusin/nifty50-historical-data (annual files 2019-2025, monthly files for 2026), caches it, aggregates 09:15-15:29 IST sessions, and compares OHLC against official NSE daily bars and the incumbent archive. The publisher identifies remaining missing bars, frozen stretches and special-session exceptions, so it cannot be treated as official ground truth. Outputs are alternative_minute_source_report.json, alternative_minute_vs_official_daily.csv, and alternative_minute_comparison_by_year.csv.


## Corrected interpretation of minute-source checks
The previous “alternative minute source” step used technovusin/nifty50-historical-data, which is also the input repository fetched by the main pipeline in scripts/fetch_data.py. The latest run compared 1,901 overlapping primary sessions and returned 1,901 exact same-source daily-close matches. This is a mirror consistency test, not independent validation. Its output is now labelled MIRROR_NOT_INDEPENDENT.

A second published dataset from https://github.com/sandeepkapri/Nifty50-Minute-Data is being checked for 2019-02-01 through 2024-03-27. Its README lists Date/Time/OHLC columns and an MIT repository license, but does not establish the underlying provider's identity or independence. The script caches the 51 MB source in the Actions cache, aggregates ordinary 09:15-15:29 IST sessions, and compares OHLC against official NSE daily values and the current archive. This remains diagnostic, with partial historical coverage and unverified lineage.

The latest expiry error sample revealed the parser regression: ISO-formatted dates such as 2024-12-04 were incorrectly reinterpreted as 2024-04-12 by a day-first parser fallback. The fix explicitly separates compact YYYYMMDD, ISO YYYY-MM-DD / ISO timestamps, and legacy day-first strings. Regression tests now cover all formats. A fresh historical reconciliation must confirm the impact; the old 340/402 result remains the valid state until a new run completes.


## Downstream target correction (25 October 2026)
Phase 3 run 40178592924 verified 402/402 candidate expiry dates against NSE derivatives records, with zero unverified dates and zero source errors. The primary minute archive differs from official daily close by more than one point on 1,717/1,901 sessions (median absolute difference 8.25 points; P95 32.45). A second published minute dataset covers 1,271 sessions through 2024-03-27 and differs by more than one point on 1,182 sessions; its provider lineage is not independently established. The downstream model now uses official NSE daily close and verified expiry dates. The 10:00 anchor remains minute-archive-derived and unvalidated, so all predictive results remain exploratory.


## Corrected independent audit — 25 October 2026

Latest workflow: [40181901081](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/40181901081). It verified 402/402 candidate expiries with zero unverified dates/source errors. It compared preserved original archive closes against official closes across 1,903 sessions: 1,719 mismatches above one point, median absolute difference 8.25, P95 32.435, maximum 200.7 points. Source gate remains **BLOCKED**.

A previous zero-mismatch PASS was false because the comparator used a table whose closes had already been overridden by official values. The result was circular and is invalidated. The separate `scripts/reconcile_archive_closes.py` audit compares preserved archive close against official close. See `data/reconciliation/source_reconciliation_report.json`, `data/reconciliation/minute_vs_official_daily.csv`, and `data/reconciliation/daily_close_mismatch_summary_by_year.csv`.

The downstream model run 40181159630 reported 61.25% holdout accuracy on 80 observations, but the 10:00 anchor is still provisional and source validation fails. Results remain exploratory. Do not proceed to further model search or trading-cost optimization until the anchor and source mismatches are resolved. No strategy is accepted.
