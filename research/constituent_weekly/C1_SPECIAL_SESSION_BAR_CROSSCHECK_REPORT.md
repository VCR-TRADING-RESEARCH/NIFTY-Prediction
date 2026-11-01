# C1 Special-Session OHLCV Cross-Check

**Updated:** 2026-11-01T19:16:24.188453+00:00
**Status:** ALL_SEVEN_DIRECT_NSE_ROWS_VALID

## Source controls

- Pinned mirror: floyds1995/Auto-Index-Constituents-Tracker at revision aa57b1050383c33e436f81844230ad2a4d52c949.
- The mirror maintainer documents daily OHLCV downloads from NSE archive endpoints.
- Direct NSE daily files are queried separately for each security/date.
- Raw data are processed in temporary runner storage only; no price/volume values are published or cached.
- The mirror repository's MIT licence covers software; no separate market-data licence was identified.

## Results

| Security/date | Mirror result | Direct NSE result | Disposition |
|---|---|---|---|
| HDFC 2018-11-07 | VALID | VALID_OFFICIAL_NSE_ROW | DIRECT_NSE_AND_PINNED_MIRROR_MATCH |
| HDFC 2019-10-27 | NO_EQ_ROW | VALID_OFFICIAL_NSE_ROW | DIRECT_NSE_VALIDATED |
| HDFC 2020-02-01 | NO_EQ_ROW | VALID_OFFICIAL_NSE_ROW | DIRECT_NSE_VALIDATED |
| HDFC 2020-11-14 | NO_EQ_ROW | VALID_OFFICIAL_NSE_ROW | DIRECT_NSE_VALIDATED |
| HDFC 2021-11-04 | VALID | VALID_OFFICIAL_NSE_ROW | DIRECT_NSE_AND_PINNED_MIRROR_MATCH |
| HDFC 2022-10-24 | VALID | VALID_OFFICIAL_NSE_ROW | DIRECT_NSE_AND_PINNED_MIRROR_MATCH |
| TATAMOTORS 2025-10-21 | VALID | VALID_OFFICIAL_NSE_ROW | DIRECT_NSE_AND_PINNED_MIRROR_MATCH |

## Summary

- Direct NSE rows valid: 7/7.
- Valid mirror rows: 4/7.
- Exact mirror-to-NSE matches: 4/7.
- Unresolved security/date pairs: 0.
- No denominator change, no imputation, and no daily coverage pass is inferred from calendar classification.
- C1 corporate-action validation remains a separate blocker.

## Reproducibility

- Mirror revision: aa57b1050383c33e436f81844230ad2a4d52c949.
- 2018-11.parquet: status LOADED; SHA-256 e46d30d4d13e0ac9380e4f3ad87b14b207967a8f7b4e532fce58544ecde1c238.
- 2019-10.parquet: status LOADED; SHA-256 ffb7067c3f3710197c03b0113a5df046e3d58cce52a8ba844aa1c8d208a7a013.
- 2020-02.parquet: status LOADED; SHA-256 88525b34243582b19630d65ca1e298723480f51e0c4efaca57664b145979d349.
- 2020-11.parquet: status LOADED; SHA-256 f03c7861967e24a90aa16931eeb553bff320104ac81732e7b948da76d024f252.
- 2021-11.parquet: status LOADED; SHA-256 d3a0e9ef35bac8610f0b3e4cfaffce0a06d00b805d255335b6108645b34e3119.
- 2022-10.parquet: status LOADED; SHA-256 6378ae28df3482fbcdb9aeba26929f437572401b1278dce6688b56581b077dc5.
- 2025-10.parquet: status LOADED; SHA-256 1084887d80358e747411fd582405c1166cce44a18eebef8902baea75e6a1b243.
