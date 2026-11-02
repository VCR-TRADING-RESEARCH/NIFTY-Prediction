# C1 Official Exchange Corporate-Action Source Feasibility — 2026-11-02

**Status:** SOURCE ROUTE IDENTIFIED; HISTORICAL EXTRACTION AND EVENT ADJUDICATION NOT YET RUN  
**Scope:** Independent verification of the 711 candidate point-in-time member events catalogued in C1.  
**Decision:** Use official NSE daily press-file bundles as the next primary-source discovery path; do not calculate or apply price factors from catalogue descriptions alone.

## 1. New primary-source evidence

The NSE's official *Description of Market Activity Reports* explicitly documents that the daily `nuprddmmyy.zip` bundle contains `Bcddmmyy.csv`, described as the file containing corporate-action details for securities. The same bundle includes announcement text (`Anddmmyy.txt`) and board-meeting text (`Bmddmmyy.txt`), which may help resolve purpose labels and announcement context. Source: https://www.nseindia.com/static/market-data/description-of-market-activity-reports

NSE Circular NSE/CMTR/70563 dated 1 October 2025 confirms a nomenclature transition effective 13 October 2025 for the daily press-file bundle from `nuprddmmyy.zip` to `PRddmmyy.zip`, and lists the corporate-action member as `Bcddmmyy.csv` → `bcdmmyyyy.csv`. The circular says the change is limited to file nomenclature and does not change file structure or dissemination frequency. Source: https://nsearchives.nseindia.com/content/circulars/CMTR70563.pdf

NSE's live Corporate Filings → Actions page exposes company/symbol, purpose, ex-date, record date and book-closure fields, with CSV download. This is a current query interface; historical depth and reliable automated pagination/export must be tested rather than assumed. Source: https://www.nseindia.com/companies-listing/corporate-filings-actions

NSE's data/report documentation separately describes a corporate-action report with symbol-wise and series-wise actions and record/book-closure dates, no-delivery period and ex-date. Access is described in the clearing-member report context; public accessibility to the historical member report is not established. Source: https://www.nseindia.com/static/products-services/equity-market-data-reports-download

## 2. What this improves—and what it does not

This is a stronger official mother-source route than relying solely on the third-party TejHQ discovery catalogue. It creates a practical way to corroborate the event catalogue against dated exchange files, and potentially to link events to daily security-master / bhavcopy identity records.

It does **not** yet prove that the PR bundle archive is continuously retrievable for every trading day from 2018-04-01 onward; that each bundle's corporate-action file includes the full event terms needed for adjustment; or that the 711 candidate events have been matched and issuer-adjudicated. The NSE live page's CSV export is not assumed to be a complete historical archive. The historical member-specific corporate-action report is not treated as freely accessible merely because NSE documents its schema.

No source data have been downloaded in this step, no event has been marked verified, no adjustment factor has been calculated, and no raw market/event data have been added to the repository.

## 3. Bounded implementation protocol

1. **Archive availability probe:** choose a small, fixed set of known event dates spanning 2018–2026, including one date before and after 13 October 2025. Request the documented daily PR/legacy bundles only; record HTTP status, archive size, SHA-256 and member filenames. Do not loop across all dates until this probe passes.
2. **Schema probe:** parse only the corporate-action member and announcement/board-meeting members. Record headers, field types, date conventions, action-purpose coverage and whether event amount/ratio fields exist. Keep source bytes encrypted in the existing Actions cache; publish only sanitised metadata and hashes.
3. **Event-level matching:** join on exchange symbol + series + ex-date/record date, then independently resolve ISIN/security identity using same-date security master/bhavcopy. Symbol-only matches are not accepted as identity proof.
4. **Coverage accounting:** for each of the 711 candidate events, classify as exact official match, partial match, conflicting source, absent from sampled archive, or not applicable. Absence from a sampled file is not proof the event did not occur.
5. **Terms verification:** use the original issuer/exchange circular or filing for dividend cash amount, bonus/split ratio convention, rights subscription/entitlement terms, buyback terms and merger/demerger scheme. Preserve unresolved cases as unresolved.
6. **Math controls:** independently verify share/price continuity for bonus/split transformations and TERP identities for rights issues. Keep raw OHLC, split/bonus-adjusted prices and total-return series separate. Never use NSE F&O strike/lot adjustment factors as a generic cash-equity adjustment.
7. **Stop rule:** after the fixed probe, continue only if archive availability, schema and legal-use assessment are adequate. Otherwise document the precise blocker and use direct issuer/exchange filings for the bounded member-event subset; do not perform an unbounded daily archive crawl.

## 4. Source and rights controls

The NSE pages establish that the reports exist and describe their contents; they do not, by themselves, grant permission for systematic automated extraction, redistribution or commercial use. Before bulk acquisition, verify the applicable NSE website/data terms and any licence/permission requirement. Keep source files private/encrypted, publish no raw event rows, and do not reuse TejHQ data beyond its recorded personal-use scope.

## 5. Gate disposition

- Daily constituent OHLCV coverage: previously verified 106,392/106,392 sessions (100%).
- Corporate-action candidate catalogue: 711 member-matched events; discovery only.
- Independent official event verification: **NOT RUN in this step**.
- Adjustment ledger / adjusted-return integrity: **NOT PASSED**.
- Overall C1: **PARTIAL / NOT PASSED**.
- C2 onward: no gate change; no further holdout tuning is authorised.

## 6. References

- NSE, Description of Market Activity Reports: https://www.nseindia.com/static/market-data/description-of-market-activity-reports
- NSE Circular NSE/CMTR/70563 (1 October 2025): https://nsearchives.nseindia.com/content/circulars/CMTR70563.pdf
- NSE Corporate Actions query/download page: https://www.nseindia.com/companies-listing/corporate-filings-actions
- NSE Data and Reports Download: https://www.nseindia.com/static/products-services/equity-market-data-reports-download
