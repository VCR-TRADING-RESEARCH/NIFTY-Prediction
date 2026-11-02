# C1 Data Rights Gate and Permitted Alternatives

**Date:** 2026-11-02  
**Status:** Direct automated NSE website collection is not approved for further bulk use without express written consent or an applicable data agreement. The four-date technical probe is complete; no bulk archive crawl will be run.

## 1. Findings from primary terms and policies

### NSE website Terms of Use

NSE's current website terms state that content/data may not be copied, stored, transmitted or otherwise reused without prior written permission, except where the content is expressly made available for download under applicable terms. They also prohibit systematic or automated data collection (including scraping, data mining, extraction and harvesting) on or in relation to the website without express written consent.

Source: https://www.nseindia.com/static/nse-terms-of-use

### NSE Data Sharing & Usage Policy

NSE/NSE Data's policy defines Market Data broadly to include end-of-day, historical, corporate and securities/derivatives data. Use, handling, sharing and redistribution are governed by the relevant agreement. Commercial data access is priced under the policy; redistribution is restricted unless agreed. The policy describes a research route through NSE's Economic Policy Research Department and confidentiality documentation.

Source: https://www.nseindia.com/static/market-data/nse-data-policy

### NSE non-display usage

NSE's Non-Display Usage Policy defines non-display usage to include market data used in automated calculations or algorithms that support trading decision-making, as well as derived data for internal analysis. It describes subscription/agreement and applicable fee requirements, with case-by-case approval for other persons.

Sources:
- https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Non_Display_Policy.pdf
- https://www.nseindia.com/static/market-data/non-display-data

### NSE research access

NSE's research initiative page says research data is strictly for academic and non-commercial use and provides a Data Seeking Request Form route. The project is intended to develop trading strategies for personal trading; do not assume it qualifies for this research-only channel.

Source: https://www.nseindia.com/static/research/research-initiatives

## 2. Decision

- The four-date archive/schema probe is retained as a bounded technical feasibility result only.
- **Do not automate or expand direct NSE website archive downloads** unless written consent or a suitable agreement explicitly covers this purpose and use.
- Do not publish NSE raw archive bytes, corporate-action rows or derived data that would reconstruct restricted market data.
- The technical availability of a public URL is not a grant of rights.
- This is a research compliance control, not a legal opinion.

## 3. Permitted alternative route to test

### Dhan Data API (existing project subscription)

Dhan's v2 documentation provides daily historical OHLCV data from an instrument's inception and intraday data for active instruments. Dhan's support documentation states that daily historical data is adjusted for corporate actions such as bonuses and splits, and describes Data APIs as market-data inputs for algorithms and analysis.

Sources:
- https://dhanhq.co/docs/v2/historical-data/
- https://dhan.co/support/platforms/dhanhq-api/is-the-historical-data-from-dhan-s-data-api-adjusted-for-corporate-actions-like-bonuses-and-splits/
- https://dhan.co/support/platforms/dhanhq-api/what-types-of-apis-does-dhan-offer/

Next controlled tests:
1. Use the user's subscribed Dhan Data API as the primary permitted channel for daily adjusted OHLCV, subject to Dhan's current API agreement.
2. Compare Dhan adjusted series with the existing raw daily panel around the 711 candidate events; derive split/bonus adjustment ratios as diagnostics, not as issuer-level proof.
3. Keep event descriptions/terms from the existing TejHQ personal-use-only catalogue (no client/business use; no raw redistribution) internal and encrypted; do not redistribute its raw rows.
4. For high-impact events (splits, bonuses, rights, mergers/demergers, large dividends), perform targeted issuer-first-party document verification where access terms permit; do not mass-scrape exchange websites.
5. Keep dividends, rights, buybacks and contract-adjustment effects separate from split/bonus price adjustments. Dhan's cited help page only explicitly confirms bonus/split adjustments.

## 4. Sources not adopted for bulk extraction

- The alternative `aswinv90/indian-market-historical-data` repository declares a non-commercial/personal/educational research licence and prohibits commercial automated trading-system operation without written permission. Do not use it for live/commercial deployment absent permission.
  - Repository: https://github.com/aswinv90/indian-market-historical-data
  - Licence: https://github.com/aswinv90/indian-market-historical-data/blob/main/LICENSE
- Third-party BSE historical-data utilities may impose manual-use/rate limits and do not themselves establish BSE redistribution rights. Do not treat them as a blanket permission for automated bulk acquisition.

## 5. Gate status

| Gate | Status | Meaning |
|---|---|---|
| NSE archive route/schema | PASS — 4/4 fixed dates | Technical feasibility only |
| Direct NSE automated bulk collection rights | NOT CLEARED | No further automated archive crawl |
| Dhan adjusted OHLCV route | AVAILABLE TO TEST | Existing subscription; validate response and terms |
| Event-level issuer/ISIN verification | NOT RUN | No event is accepted yet |
| Corporate-action adjustment ledger | NOT PASSED | No factor is applied |
| Overall C1 | PARTIAL / NOT PASSED | C2 remains gated |

The next work item is the Dhan-based adjustment diagnostic and a small, targeted event-verification design—not another NSE archive crawl.


## 6. Dhan adjusted-price diagnostic results — 2026-11-02

The Dhan API test passed for two event classes:
- Reliance 1:1 bonus (28-Oct-2024): 9/9 sessions matched; the relative adjusted/raw factor was 0.5 for open, high, low and close.
- Bajaj Finserv 5:1 split plus 1:1 bonus (13-Sep-2022): 11/11 sessions matched; the relative adjusted/raw factor was 0.1 for all OHLC fields.

The Bajaj Finserv price-factor check passed, but identity did not: the TejHQ raw rows show the old ISIN on 13-Sep-2022 and the new ISIN from 14-Sep, while NSE Circular CML53597 states that the new ISIN is effective from 13-Sep. This is logged as E0118; no silent date shift or source correction was made. See [C1_DHAN_ADJUSTMENT_DIAGNOSTIC.md](C1_DHAN_ADJUSTMENT_DIAGNOSTIC.md) and its JSON.

The final run used a fresh TOTP token and hit both encrypted TejHQ year partitions from cache. No raw prices or ISINs were published. This validates two price-adjustment cases only; it does not verify dividends, rights, mergers/demergers or buybacks. Overall C1 remains PARTIAL / NOT PASSED and C2 remains gated.
