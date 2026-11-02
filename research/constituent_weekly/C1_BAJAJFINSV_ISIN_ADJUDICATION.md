# C1 Security Identity Adjudication — BAJAJFINSV 2022 Split/Bonus

**Review date:** 2026-11-03  
**Decision:** EFFECTIVE ISIN DATE RESOLVED FOR RESEARCH MAPPING; RAW REFERENCE ROW FLAGGED AS STALE  
**Scope:** Bajaj Finserv 5:1 face-value split plus 1:1 bonus, ex-date 2022-09-13  
**This does not pass the overall C1 corporate-action gate.**

## Question

The Dhan adjusted-price diagnostic found the expected combined 10x adjustment factor, but the TejHQ raw reference row for 2022-09-13 retained the old ISIN, with the new ISIN first appearing on 2022-09-14. NSE circular CML53597 contains both (a) a statement that the new ISIN is effective 2022-09-14 and (b) a specific statement that the new ISIN applies to trades on and from the 2022-09-13 ex-date.

## Independent evidence

1. **NSE Clearing / NSE F&O circular FAOP53644 dated 2022-09-12** explicitly states: split 5:1, bonus 1:1, ex-date 2022-09-13, combined adjustment factor 10, and that the changes are effective from 2022-09-13. Source: https://archives.nseindia.com/content/circulars/FAOP53644.pdf
2. **BSE Notice 20220908-17 dated 2022-09-08**, reproduced as an unedited BSE publication by Publicnow/MarketScreener, identifies new ISIN INE918I01026 and says it applies to trades on and from the 2022-09-13 ex-date. Source: https://www.marketscreener.com/quote/stock/BSE-LIMITED-33930062/news/New-ISIN-Number-of-Bajaj-Finserv-Limited-Scrip-Code-532978-41723564/
3. **NSE listing circular CML53597 dated 2022-09-08** itself states that the new ISIN is effective for all trades done on and from the 2022-09-13 ex-date, notwithstanding its preceding general “w.e.f. 14-Sep-2022” sentence. Source: https://nsearchives.nseindia.com/content/circulars/CML53597.pdf

## Adjudication

For the point-in-time **trading-security identity**, apply the new ISIN from the ex-date **2022-09-13**. The specific trade-effective clause in CML53597 is consistent with the independent BSE Notice 20220908-17 reproduction and NSE Clearing circular FAOP53644. The first sentence's 14-Sep wording is interpreted as the general ISIN effective-date/record-date wording, while the explicit trade-effective clause governs exchange trades from the ex-date.

The TejHQ old-ISIN value on 2022-09-13 is therefore treated as a **stale source identifier**, not as evidence that the old security remained the trading security that day. Do not rewrite the raw source row. Preserve it and attach this adjudication as a derived point-in-time identity override, with provenance.

## Quantitative checks

- Existing Dhan adjusted/raw diagnostic: 11/11 sessions matched.
- Relative OHLC adjustment factor: 0.1 for open, high, low and close, equivalent to the combined 10x split/bonus adjustment.
- This confirms the price adjustment ratio for this sampled event; it does not independently validate all other corporate-action events.

## Implementation rule

- For derived security mapping, new ISIN INE918I01026 is effective from 2022-09-13 (inclusive).
- Preserve the raw TejHQ 2022-09-13 identifier unchanged and mark it as a stale-reference discrepancy.
- The affected weekly cycle is no longer excluded solely because of this one-day ISIN timestamp discrepancy, provided the implementation applies the derived override and all other cycle-level checks pass.
- Do not generalise this decision to other issuers or events.

## Remaining C1 limitations

This adjudication closes only the BAJAJFINSV one-day identity-date dispute. The broader 711-event catalogue, the other dated security aliases, event-specific dividend/rights/merger/buyback treatment, and the overall C1 acceptance gate remain open. C1 remains PARTIAL; C2 and confirmatory C4 remain gated.
