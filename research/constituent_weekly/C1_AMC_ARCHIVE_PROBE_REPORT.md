# C1 AMC disclosure metadata probe

- Run time (UTC): 2026-11-01T05:04:56.738736+00:00
- Overall: **PASS_SCHEMA_ONLY**
- Scope: metadata/schema validation only; no raw holdings are published.

| Month | Status | HTTP | Content type | Bytes | SHA-256 | Magic prefix | Sheets | Scheme | Headers | ISIN rows |
|---|---:|---|---|---:|---|---|---:|---|---|---:|
| 2026-09 | PASS_SCHEMA | 200 | application/vnd.ms-excel | 1352141 | f8b25cedeecdd9912e0b4b19f74714fc849bae4dae0cb494c4863fde42a178d1 | 504b03041400060008000000 | 108 | True | ISIN,quantity,weight_pct | 50 |
| 2026-02 | PASS_SCHEMA | 200 | application/vnd.ms-excel | 1206358 | 8eabaeabf1436487f78894e432eb78f911dd8c13c872af03ecdde2b6f7d8e13f | 504b03041400060008000000 | 111 | True | ISIN,quantity,weight_pct | 50 |
| 2019-04 | ERROR | 404 | text/html; charset=utf-8 |  |  |  |  |  |  |  |
- 2019-04: HTTPError: 404 Client Error: Not Found for url: https://mf.nipponindiaim.com/InvestorServices/FactsheetsDocuments/NIMF-MONTHLY-PORTFOLIO-30-Apr-19.xls

No constituent names, ISINs, quantities, market values, portfolio weights or raw workbook rows are stored in this report.
A schema pass does not establish publication-time availability, source-use rights, historical security continuity, index-weight equivalence or permission to trade.
