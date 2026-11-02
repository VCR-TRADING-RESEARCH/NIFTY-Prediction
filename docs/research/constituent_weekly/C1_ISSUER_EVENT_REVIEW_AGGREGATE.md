# C1 Issuer-Source Review — 37 Complex Corporate-Action Candidates

**Review date:** 2026-11-03  
**Phase:** BUP-01 / C1  
**Disposition:** COMPLETED FOR THE 37-CANDIDATE COMPLEX-EVENT QUEUE; **C1 OVERALL REMAINS PARTIAL / NOT PASSED**.

## Scope and method

The protected queue workflow assembled 37 unique point-in-time NIFTY-member candidates from the encrypted TejHQ personal-use-only cache. Membership matching was unambiguous for all 37 candidates (37 matched, zero ambiguous). The ciphertext was decrypted only in the private research runtime. Event-level source rows, raw identifiers, cash amounts, subjects and raw prices have not been copied to the repository, Actions logs or GitHub Pages.

Each candidate was classified against issuer-first-party filings and official exchange primary notices where the issuer notice was not located in this bounded review. The review checked event type, entitlement/ratio or face-value change, record date and whether the candidate represented an equity-security action or another security distribution.

## Aggregate result

| Catalogue label | Candidate count | Review disposition |
|---|---:|---|
| Bonus-labelled | 19 | 17 confirmed as equity bonus-share actions; 2 reclassified as bonus debenture distributions (not equity bonus shares) |
| Split | 9 | 9 equity split events; terms/record-date evidence located |
| Rights | 6 | 6 rights offers; entitlement, issue terms and record-date evidence located |
| Merger/demerger | 3 | 3 scheme events; issuer scheme/entitlement evidence located |
| **Total** | **37** | **All 37 classified and event terms/date source-checked** |

Source provenance across this queue: 35 candidate entries have issuer-first-party source evidence; two are supported by official exchange-primary material because the corresponding issuer notice was not located in this bounded search. This is not a claim that every affected historical security identifier or price series has passed continuity validation.

## Material corrections and interpretation

1. **Two bonus-labelled entries were not equity bonus shares.** Issuer annual reports establish that these distributions were fully paid non-convertible debentures issued by way of a bonus to equity holders. They must not be assigned a stock-bonus factor such as 0.5. They are retained as non-equity security distributions and require separate affected-window treatment; no equity-share factor is applied.
2. **A later issuer corrigendum superseded an initially announced record date.** The final record date is used in the private review ledger; the earlier notice is not treated as controlling.
3. **Combined actions are treated as combined capital restructurings.** Where a bonus and split occurred together, their terms are not applied twice to a price series already adjusted by Dhan.
4. **The previously adjudicated Bajaj Finserv trading-identity boundary remains effective from 2022-09-13 inclusive.** The raw TejHQ source identifier is preserved unchanged and flagged as stale source metadata; the derived identity mapping carries the exchange-source adjudication.

## What this review does not pass

- The unambiguous membership join is not proof that every historical ISIN, predecessor/successor mapping or Dhan security ID is correct for every date.
- Dhan's daily adjusted OHLC and same-session intraday OHLC scale matched for two tested events only. It has not been demonstrated for every one of the 26 equity bonus/split candidates.
- Rights issues require date-correct TERP calculations using pre-event prices, entitlement ratios, subscription price and any staged payment/call schedule. No TERP has been computed here.
- Merger/demerger windows require scheme-specific predecessor/successor identity and price-series continuity. No generic factor or ticker-only price stitching is applied.
- No new manual adjustment factor has been applied to the constituent panel and no candidate stock-cycle has been released into confirmatory fitting on the strength of this review alone.

## Remaining catalogue scope

The remaining point-in-time member-event catalogue contains 625 dividend candidates, 20 buyback candidates and 29 AGM/other candidates. Dividends retain NIFTY price-index semantics: do not mechanically reinvest cash dividends or substitute a total-return target. Buybacks and other events need forecast-time availability and affected-cycle classification. The full 711-event catalogue and dated historical security identity audit remain open.

## Source evidence (illustrative primary disclosures)

The private event-to-source decision ledger remains outside GitHub because the queue is derived from personal-use-only data. The following public issuer disclosures illustrate the source review and key classifications:

- [TCS 2018 bonus record-date notice](https://www.tcs.com/content/dam/tcs/pdf/discover-tcs/investor-relations/corporate-actions/2017-18/notice-record-date-bonus-issue-2018.pdf) — 1:1 equity bonus, record date 2 June 2018.
- [UPL 2018-19 annual report](https://www.upl-ltd.com/financial_pdfs/6vohVH3pKznTyjdhdAuC2phXr0iGlHp1OLsau2p3/UPL-Annual-Report-2018-19.pdf) and [standalone results](https://www.upl-ltd.com/financial_pdfs/QJGDHXjw8fe0ZPxt52KxPIzWDDuQWeXxtD0B0FW9/UPL_Standalone_March-2019.pdf) — 1:2 equity bonus terms and the subsequent record-date notice trail.
- [Britannia Annual Report 2019-20](https://media.britannia.co.in/Annual_Report_2019_20_b376843dc6.pdf), [2020-21](https://media.britannia.co.in/Annual_Report_2020_21_be3a70d511.pdf) and [2021-22](https://media.britannia.co.in/Annual_Report_2021_22_6eb6f3ae88.pdf) — the two bonus-labelled cases are ₹30 secured and ₹29 unsecured non-convertible debenture distributions, not bonus equity shares.
- [POWERGRID 2023 AGM notice](https://www.powergrid.in/sites/default/files/agm_egm_files/NSEBSENoticeARdt08082023.pdf) and [board-meeting outcome](https://www.powergrid.in/sites/default/files/quarter1/Binder1.pdf) — 1:3 bonus terms and record date 12 September 2023.
- [Trent issuer corrigendum on revised bonus record date](https://docs.trent-tata.com/Intimation_of_Revised_Record_date-Corrigendum.pdf) — record date revised from 29 May to 4 June 2026.
- [Bharti Airtel 2019 rights Letter of Offer](https://assets.airtel.in/teams/simplycms/web/docs/Letter_of_Offer_dated_April_19_2019.pdf), [Reliance 2020 rights-issue terms](https://www.ril.com/sites/default/files/2023-01/ET13062020.pdf), and [Adani Enterprises 2025 rights-entitlement letter](https://www.adanienterprises.com/-/media/Project/Enterprises/Investors/Investor-Downloads/Rights-Issue-Other-Documents/Rights-Entitlement-Letter.pdf) — representative primary rights disclosures.
- [Hindustan Unilever / KWIL record-date notice](https://www.hul.co.in/files/newspaper-publication-regarding-intimation-of-record-date-21-11-2025.pdf) — 1:1 demerger entitlement, record date 5 December 2025.

## Phase decision

**C1 remains PARTIAL / NOT PASSED.** The 37-candidate terms review is complete, but identity, adjusted-price continuity and affected-cycle exclusions are not complete for the full 711-candidate catalogue. C2's panel remains accepted with C1 limitations under the existing progression decision; C3 remains exploratory only; confirmatory C4 and trading/execution C5 remain gated.
