# BUP-01 licensed membership input

**Source:** [aditya-jha/nse-historical-membership](https://github.com/aditya-jha/nse-historical-membership)  
**Pinned source commit:** `cc6f89fd6699a92afa8d398896d0aac385eb9e8c`  
**Input file:** `index_history/data/index_membership_history.csv`  
**Source file SHA-1 (Git blob):** `519a9232e125cc044580ec7b90ef5c18475b4f0f`  
**Dataset licence:** CC BY 4.0, per source repository `LICENSE-DATA`  
**Required attribution:** Jha, A. (2026). *NSE Historical Membership (Point-in-Time).* GitHub. https://github.com/aditya-jha/nse-historical-membership. Underlying-source attribution: publicly published NSE Indices press releases and NSE Exchange circulars.

This file is a derived NIFTY 50-only subset containing the source's effective-dated membership intervals and original source/confidence fields. It is a small, cached, attributable input; no raw NSE circular PDFs are copied.

## File audit

- Rows: 83
- Unique symbols over all intervals: 82
- `snapshot_floor` intervals: 50
- `press_release` intervals: 33
- Earliest interval start: 2014-01-01
- Latest interval start / latest known membership event: 2025-09-30
- Numeric historical weights present: false
- Monthly 15th-day cardinality audit performed separately for 2018-01 through 2025-09: 93/93 checks returned 50 active intervals.

## Use restrictions and research limitations

- Keep `source` and `notes` attached to every row. The 50 `snapshot_floor` intervals are reconstructed from the coverage-floor snapshot rather than a row-specific official inclusion record; they must not be treated as documentary confirmation of each member's historical entry.
- The source repo's validation report has 29/29 curated famous-transition tests passing and 0/42 current-snapshot differences, but reports material pre-2018 cardinality/internal-consistency errors. BUP-01 will not use pre-2018 records for confirmatory modelling.
- This subset's latest NIFTY 50 interval event is dated 2025-09-30. It is not a current 2026-10 universe. No post-2025-09 membership is inferred.
- This dataset has no numeric historical NIFTY 50 free-float weight series. `weightage` is empty for the NIFTY 50 rows inspected. Do not substitute equal weights or use today's weights backwards.
- This is a candidate membership series, not yet C1 certification. Event-by-event effective-date and security-identity reconciliation is still required.
