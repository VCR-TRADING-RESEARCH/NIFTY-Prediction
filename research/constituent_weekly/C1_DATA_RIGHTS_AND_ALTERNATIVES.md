# C1 Data Rights Gate and Permitted Alternatives

**Date:** 2026-11-03  
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
- NSE's current Terms of Use also restrict use of website data/content for gaming, virtual trading or simulation. Because this project includes trading-model evaluation and backtesting, no workflow will ingest NSE website archive content without a documented rights basis.
- NSE's Data Sharing & Usage Policy defines Market Data to include historical and corporate data, governs subscriber handling through relevant agreements, restricts redistribution, and describes separate licensing for use of licensed market data to create a financial index or instrument. No exemption is presumed for this project.
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

## 4. Stop automated NSE website collection

The current NSE Terms of Use prohibit systematic or automated data collection (including scraping, data mining, extraction and harvesting) without express written consent. They also restrict website-content use for gaming, virtual trading and simulation. NSE's Data Sharing & Usage Policy defines historical and corporate data as Market Data governed by relevant agreements, restricts redistribution and describes separate licensing where market data is used to create a financial index or instrument. This research includes model evaluation and possible trading simulation, so the conservative operational rule is no further automated NSE website extraction without written permission/agreement that clearly covers this purpose. The four-date technical probe is not a rights clearance.

Sources:
- https://www.nseindia.com/static/nse-terms-of-use
- https://www.nseindia.com/static/market-data/nse-data-policy
- https://www.nseindia.com/static/market-data/non-display-data

Use the user's Dhan subscription for price-scale diagnostics under its API agreement and issuer-first-party disclosure pages where access terms permit. TejHQ remains personal-use-only; its raw rows remain encrypted and internal. Unverified events are marked SOURCE_UNRESOLVED and affected stock-cycles excluded.

## 5. Sources not adopted for bulk extraction

- The alternative `aswinv90/indian-market-historical-data` repository declares a non-commercial/personal/educational research licence and prohibits commercial automated trading-system operation without written permission. Do not use it for live/commercial deployment absent permission.
  - Repository: https://github.com/aswinv90/indian-market-historical-data
  - Licence: https://github.com/aswinv90/indian-market-historical-data/blob/main/LICENSE
- Third-party BSE historical-data utilities may impose manual-use/rate limits and do not themselves establish BSE redistribution rights. Do not treat them as a blanket permission for automated bulk acquisition.

## 6. Gate status

| Gate | Status | Meaning |
|---|---|---|
| NSE archive route/schema | PASS — 4/4 fixed dates | Technical feasibility only |
| Direct NSE automated bulk collection rights | NOT CLEARED | No further automated archive crawl |
| Dhan adjusted OHLCV route | AVAILABLE TO TEST | Existing subscription; validate response and terms |
| Event-level issuer/ISIN verification | NOT RUN | No event is accepted yet |
| Corporate-action adjustment ledger | NOT PASSED | No factor is applied |
| Overall C1 | PARTIAL / NOT PASSED | C2 remains gated |

The Dhan daily and intraday sample diagnostics have now passed for two events. The next task is a recipient-encrypted queue for the 37 complex TejHQ candidate events, followed by targeted issuer-first-party verification. Only ciphertext is uploaded as a one-day Actions artifact; no event rows are published. Do not scrape exchange websites for missing terms; use issuer documents or a documented licensed source, otherwise mark unresolved and exclude affected stock-cycles.


## 6. Dhan adjusted-price diagnostic results — 2026-11-02

The Dhan API test passed for two event classes:
- Reliance 1:1 bonus (28-Oct-2024): 9/9 sessions matched; the relative adjusted/raw factor was 0.5 for open, high, low and close.
- Bajaj Finserv 5:1 split plus 1:1 bonus (13-Sep-2022): 11/11 sessions matched; the relative adjusted/raw factor was 0.1 for all OHLC fields.

The Bajaj Finserv trading-security identity date is adjudicated: the specific trade-effective clause in NSE CML53597 and NSE Clearing FAOP53644 support the new trading ISIN from 2022-09-13 inclusive. The raw TejHQ 13-Sep old-ISIN field is preserved unchanged and flagged as stale metadata in the derived mapping. This closes only the one-day identity dispute, not the overall event catalogue. See [C1_BAJAJFINSV_ISIN_ADJUDICATION.md](C1_BAJAJFINSV_ISIN_ADJUDICATION.md), [C1_DHAN_ADJUSTMENT_DIAGNOSTIC.md](C1_DHAN_ADJUSTMENT_DIAGNOSTIC.md) and [C1_DHAN_INTRADAY_CA_DIAGNOSTIC.md](C1_DHAN_INTRADAY_CA_DIAGNOSTIC.md).

The protected Dhan daily adjustment check passed for RELIANCE and BAJAJFINSV. A separate same-session comparison found that Dhan intraday OHLC aggregates matched Dhan adjusted daily OHLC for both events. No raw prices or raw event rows were published. This validates two sampled bonus/split events only; it does not verify dividends, rights, other mergers/demergers or buybacks. Overall C1 remains PARTIAL / NOT PASSED; C2 panel results are accepted with C1 limitations, while confirmatory C4 remains gated.


## 7. Next bounded task — recipient-encrypted 37-event queue

A protected Actions job extracts the 37 complex point-in-time member-event candidates from the existing TejHQ personal-use-only source. The complete manifest is AES-256-GCM encrypted with a fresh data key, and that data key is wrapped to a one-time RSA recipient public key. Only ciphertext is uploaded as a one-day artifact. The private key is held outside GitHub and is not in the repository, Actions secrets, logs, artifacts or Pages. No cleartext event row is stored on disk or printed to logs. Issuer event verification follows only after the intended recipient decrypts the queue.
