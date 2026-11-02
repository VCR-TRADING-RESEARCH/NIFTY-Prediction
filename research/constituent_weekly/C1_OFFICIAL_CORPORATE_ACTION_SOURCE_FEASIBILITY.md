# C1 Official Exchange Corporate-Action Source Feasibility — 2026-11-02

**Status:** FIXED-DATE ARCHIVE/SCHEMA PROBE PASSED (4/4); AUTOMATED NSE BULK EXTRACTION RIGHTS-BLOCKED; ISSUER-FIRST-PARTY ROUTE REQUIRED  
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


## 7. Executed fixed-date archive/schema probe — 2026-11-02

The automated probe passed on four known NSE trading dates spanning the old and new naming regimes: **2018-04-02, 2024-04-16, 2025-10-14 and 2026-04-17 (4/4)**. The 17-Apr-2024 sample from the initial probe was an official capital-market holiday (NSE Circular NSE/CMTR/59722) and was replaced with 16-Apr-2024.

The working public website archive pattern was empirically confirmed as:

`https://nsearchives.nseindia.com/archives/equities/bhavcopy/pr/PRDDMMYY.zip`

All four ZIPs contained a corporate-action CSV, an announcement text file and a board-meeting text file. The corporate-action CSV had the same ten headers in all four samples: SERIES, SYMBOL, SECURITY, RECORD_DT, BC_STRT_DT, BC_END_DT, EX_DT, ND_STRT_DT, ND_END_DT, PURPOSE. The member names observed were `bc020418.csv`, `bc160424.csv`, `bc14102025.csv` and `bc17042026.csv`.

The final probe run [41423606062](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41423606062) reused all four encrypted archive-cache entries (4/4 cache hits). The public outputs contain only archive sizes/hashes, member names, headers and presence flags; raw archive bytes remain encrypted in Actions cache and no event rows are published. See [C1_NSE_PR_ARCHIVE_PROBE.md](C1_NSE_PR_ARCHIVE_PROBE.md) and [machine result](C1_NSE_PR_ARCHIVE_PROBE.json).

**Interpretation:** this establishes that the website archive route and corporate-action member schema are retrievable on the four sampled dates, including before and after the October 2025 naming change. It does not establish continuous daily availability, permission for systematic bulk extraction, event completeness, security/ISIN identity, issuer terms or adjustment-factor correctness. No candidate event has been verified and no factor has been calculated/applied. Corporate-action gate remains NOT PASSED; overall C1 remains PARTIAL; C2 stays gated.


## 8. Data-rights gate — 2026-11-02

A primary-source review after the technical probe found that NSE's current website Terms of Use prohibit systematic/automated data collection without express written consent and restrict copying/storing website content without prior written permission. NSE's Data Sharing & Usage Policy governs historical/corporate market data through relevant agreements, and its Non-Display Usage Policy expressly covers automated algorithms used for trading decisions and derived data. NSE's research route is described as academic/non-commercial. These rules mean the public archive URL is not permission for a 711-event automated crawl.

Sources:
- NSE Terms of Use: https://www.nseindia.com/static/nse-terms-of-use
- NSE Data Sharing & Usage Policy: https://www.nseindia.com/static/market-data/nse-data-policy
- NSE Non-Display Usage Policy: https://www.nseindia.com/static/market-data/non-display-data
- NSE Research Initiative: https://www.nseindia.com/static/research/research-initiatives

**Decision:** no further automated NSE website archive downloads until express written consent or a suitable agreement is established. The four-date technical probe remains valid as a bounded feasibility test. The next data-validation route is Dhan's subscribed Data API: its daily historical data is documented as adjusted for bonus and split events. Use that data only under the user's Dhan API agreement; compare adjustments against the existing encrypted TejHQ candidate catalogue and verify high-impact events through permitted issuer-first-party documents. Dhan's help page explicitly mentions bonus/split adjustment; it does not establish that dividends, rights or all other event classes are adjusted.

See [C1_DATA_RIGHTS_AND_ALTERNATIVES.md](C1_DATA_RIGHTS_AND_ALTERNATIVES.md) for the source-by-source gate and next tests. C1 corporate-action gate remains NOT PASSED; overall C1 remains PARTIAL; C2 remains gated.


## 9. BAJAJFINSV ISIN date-source adjudication — 2026-11-03

The new trading ISIN is adjudicated effective from the 2022-09-13 ex-date inclusive. NSE Clearing FAOP53644 confirms the 5:1 split, 1:1 bonus, ex-date and combined 10x adjustment. The explicit trade-effective clause in NSE CML53597 states that the new ISIN applies to trades on and from 13-Sep, notwithstanding preceding general 14-Sep wording. The TejHQ 13-Sep old-ISIN field remains unchanged and is flagged as stale source metadata in the derived point-in-time mapping. This closes only the one-day identity dispute, not the 711-event corporate-action gate. See [C1_BAJAJFINSV_ISIN_ADJUDICATION.md](C1_BAJAJFINSV_ISIN_ADJUDICATION.md).


## 10. 2026-11-03 — Stop automated NSE archive expansion

NSE's current Terms of Use prohibit systematic or automated website data collection, including scraping, data mining, data extraction and harvesting, without express written consent. The same terms restrict use of website data/content for gaming, virtual trading and simulation. NSE's Data Sharing & Usage Policy defines Market Data to include historical and corporate data, requires relevant agreements and restricts redistribution. The research adopts a conservative operational decision: no automated expansion of the four-date PR archive probe without written permission/agreement expressly covering this research use.

Sources:
- https://www.nseindia.com/static/nse-terms-of-use
- https://www.nseindia.com/static/market-data/nse-data-policy
- https://www.nseindia.com/static/market-data/non-display-data

The four-date probe remains a technical feasibility result only. The corporate-action workflow now forces the NSE probe scope to false even on manual dispatch. Remaining work uses Dhan for price-scale diagnostics and issuer-first-party disclosures where permitted; otherwise affected stock-cycles are marked unresolved/excluded.
