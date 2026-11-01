# C1 AMC disclosure metadata probe

- Run time (UTC): 2026-11-01T04:57:51.816984+00:00
- Overall: **PARTIAL_OR_BLOCKED**
- Scope: metadata/schema validation only; no raw holdings are published.

| Month | Status | HTTP | Bytes | SHA-256 | Sheets | Scheme | Headers | ISIN rows |
|---|---:|---:|---:|---|---:|---|---|---:|
| 2026-09 | ERROR | 200 |  |  |  |  |  |  |
- 2026-09: ValueError: Unrecognised Excel container signature
| 2026-02 | ERROR | 200 |  |  |  |  |  |  |
- 2026-02: ValueError: Unrecognised Excel container signature
| 2019-04 | ERROR | 404 |  |  |  |  |  |  |
- 2019-04: HTTPError: 404 Client Error: Not Found for url: https://mf.nipponindiaim.com/InvestorServices/FactsheetsDocuments/NIMF-MONTHLY-PORTFOLIO-30-Apr-19.xls

No constituent names, ISINs, quantities, market values, portfolio weights or raw workbook rows are stored in this report.
A schema pass does not establish publication-time availability, source-use rights, historical security continuity, index-weight equivalence or permission to trade.
