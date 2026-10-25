# Phase 3 — Official Source and Expiry Reconciliation

**Branch:** `research/phase-3-official-source-reconciliation`  
**Status:** BLOCKED — run 40174191441 completed computation and artifact upload, but its final Git commit collided with the parallel research run. Source routing/parser corrections are being tested in the next bounded run.  
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
3. For each nominal candidate expiry, use the official index session list to identify the last trading session on or before the nominal date.
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

The completed official-source pass (40174191441) compared 1,901 sessions: 1,717 daily closes differ from official NSE close by more than one point (median absolute difference 8.25; P95 32.45; maximum 200.7 index points). The initial contract parser reported 359/402 candidate dates confirmed and 43 unconfirmed. The downloader was found to try the UDiFF URL first even for pre-8-Jul-2024 dates, and to use an alternate host as the primary UDiFF URL. The next run prioritizes the format matching each historical period and validates archive trade dates. The 43 rows remain unresolved until revalidation.
