# BUP-01 — One-time official weight sample audit

**Date:** 2026-10-31  
**Source sample:** NSE Indices September 2026 Market Capitalisation, Weightage and Beta archive  
**Retrieval record:** C1 workflow run 41177903446, attempt #8  
**Use status:** Source-format inspection only. No training, backtest or trading use is authorised by this audit.

## Sample artefact metadata

- Archive: mcwb_sep26.zip
- Official URL recorded by the workflow: https://niftyindices.com/Market_Capitalisation_Weightage_Beta_for_NIFTY_50_And_NIFTY_Next_50/mcwb_sep26.zip
- Archive bytes: 6,761
- SHA-256: eb6336b8e0c55a0b2cfd1a29d0c79e2b962e091d8d3a3d724e2245320ec0799b
- Relevant member: nifty50_mcwb.csv
- CSV contains a title preamble and blank line before the actual table header; the table header is at zero-based row 2.
- Parsed constituent rows: 50; unique symbols: 50; duplicate symbol rows: 0.
- Sum of displayed Weightage (%) field: 100.0%.
- The file notes the last trading day as 30-Sep-2026.
- No individual symbol or weight values are reproduced in this report.

The ZIP also contains the NIFTY Next 50 CSV. The separately downloaded October 2026 market-cap/weightage archive contains a NIFTY 50 PDF and other index PDFs; the PDF content was not analysed for this audit.

## Cross-check against a third-party membership reconstruction

The BKKB20/nse-index-history current_members/NIFTY_50.csv file contains 50 symbols and is described by its project as a March 2026 current membership list. When compared with the official September 2026 report's 50-symbol list:
- candidate-only symbol: WIPRO
- official-report-only symbol: BSE
- both lists: 50 rows, no duplicates

This difference may reflect a genuine constituent change between the snapshot dates and is enough to show that the third-party "current" file must not be applied blindly to later dates. It is not a full historical membership audit. Original circulars, announcement/effective dates, ISIN and security-ID continuity are still required.

## Interpretation and limits

This validates only that the retrieved archive is a structurally readable ZIP/CSV, the table has 50 unique symbol rows, and the displayed weights sum to 100%. It does **not** establish:
- the exact time the report became publicly available;
- the right to collect, retain, redistribute, publish or use the source data in an automated trading research workflow;
- historical monthly coverage back to 2019 or daily point-in-time weight history;
- validity of carrying weights forward or drifting them between snapshots;
- accuracy of historical membership/security mapping;
- stock-level intraday price coverage;
- reconciliation of weighted stock returns with the NIFTY index return.

## Data-rights correction

The NSE Indices website Terms of Use state that systematic or automated data collection requires express written consent, restrict copying/reproduction/distribution without prior written permission, and describe the site as personal, non-commercial use only. After this condition was discovered, repeated remote retrieval was disabled in the C1 workflow. The prior raw archive upload is being retired; future automated workflows inspect only separately authorised, pre-provisioned data and do not fetch the NSE website.

Reference: https://www.niftyindices.com/terms-of-use

## C1 decision

**C1 remains BLOCKED / IN PROGRESS.** The source-format sample is a technical pass only. Obtain an appropriately licensed/authorised point-in-time weight source, verify historical membership and security identity, and validate stock price availability before constructing any stock-cycle panel or fitting models.
