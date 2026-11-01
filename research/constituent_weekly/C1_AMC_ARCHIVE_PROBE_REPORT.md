# C1 AMC disclosure metadata probe

- Run time (UTC): 2026-11-01T05:00:10.876565+00:00
- Overall: **PASS_SCHEMA_ONLY**
- Scope: metadata/schema validation only; no raw holdings are published.

| Month | Status | HTTP | Content type | Bytes | SHA-256 | Magic prefix | Sheets | Scheme | Headers | ISIN rows |
|---|---|---|---|---:|---|---|---:|---|---|---:|
| 2026-09 | PASS_SCHEMA | 200 | application/vnd.ms-excel | 1352141 | f8b25cedeecdd9912e0b4b19f74714fc849bae4dae0cb494c4863fde42a178d1 | 504b03041400060008000000 | 108 | True | ISIN, quantity, weight_pct | 50 |
| 2026-02 | PASS_SCHEMA | 200 | application/vnd.ms-excel | 1206358 | 8eabaeabf1436487f78894e432eb78f911dd8c13c872af03edde2b6f7d8e13f | 504b03041400060008000000 | 111 | True | ISIN, quantity, weight_pct | 50 |
| 2019-04 | NOT_FOUND | 404 | text/html; charset=utf-8 | — | — | — | — | — | — | — |

## Interpretation

- The September 2026 and February 2026 direct AMC workbooks were retrieved successfully. The payloads are XLSX ZIP containers even though the direct URLs end in .xls; the parser detects the container signature and uses the correct reader.
- Both workbooks contain the Nippon India ETF Nifty 50 BeES scheme section and 50 ISIN-bearing holdings rows. The detected generic columns include ISIN, quantity and portfolio weight.
- The April 2019 month is listed on the AMC archive page, but the guessed modern month-end filename path returned HTTP 404. This is a URL-discovery failure, not evidence that the historical portfolio is unavailable. Do not substitute an inferred holdings record.
- Offline parser tests: **7 passed**. Probe workflow run: [41275178244](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41275178244). The probe and report generation succeeded; the job's final push failed due a concurrent C1 branch update. The sanitised report is being committed separately by the research controller.

## Limits and gate

This is **schema validation**, not admission of a historical weight series. No constituent names, ISINs, quantities, market values, portfolio weights or raw workbook rows are reproduced in this public report. No raw workbook was cached or uploaded as an artifact.

Still unresolved:
- source-use rights for automated extraction and intended internal trading-research use;
- actual public availability timestamps for every monthly portfolio;
- exact historical month-to-file mapping and complete series coverage;
- stable security identity and corporate-action handling;
- point-in-time membership and at least 98% weight coverage / 47 valid constituents;
- weighted constituent basket reconstruction against official NIFTY index returns.

Therefore BUP-01 C1 remains **PARTIAL / NOT ACCEPTED FOR MODELLING**. This result does not pass C2, does not validate an index forecast, and does not authorise a trading strategy.
