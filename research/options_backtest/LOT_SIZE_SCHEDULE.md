# NIFTY 50 Options Historical Market-Lot Schedule

**Status:** Official NSE circular evidence identified; apply by contract expiry, not simply trade date.

| Contract expiry | NIFTY market lot | Effective basis |
|---|---:|---|
| Through 2024-04-25 | 50 | Existing lot before Apr-2024 revision |
| 2024-04-26 through 2024-12-19 | 25 | NSE revised from 50 to 25 for contracts introduced from 2024-04-26; last weekly expiry with this lot was 2024-12-19 |
| 2025-01-02 through 2025-12-23 | 75 | NSE contract-size revision; first weekly expiry with revised lot was 2025-01-02; last weekly expiry with 75 was 2025-12-23 |
| From 2026-01-06 | 65 | NSE revision from 75 to 65; first weekly expiry with revised lot was 2026-01-06 |

**Research window implications:** The public intraday options archive begins 2024-10-01, so the tested expiry-lot mapping is 25 through 2024-12-19, 75 from 2025-01-02 through 2025-12-23, and 65 from 2026-01-06 onward. Expiries around the transition dates must be joined to the actual contract expiry and official holiday-adjusted expiry calendar. Do not assign lot size from the trade date alone.

## Official sources

- NSE circular NSE/FAOP/61415, 2024-04-02, revised NIFTY lot 50 to 25 effective for contracts introduced from 2024-04-26: https://nsearchives.nseindia.com/content/circulars/FAOP61415.pdf
- NSE circular NSE/FAOP/64625, 2024-10-18, revised NIFTY lot 25 to 75; effective for new index derivatives from 2024-11-20: https://nsearchives.nseindia.com/content/circulars/FAOP64625.pdf
- NSE corrigendum NSE/FAOP/64672, 2024-10-22, identifies last weekly expiry at 25 as 2024-12-19 and first weekly expiry at 75 as 2025-01-02: https://nsearchives.nseindia.com/content/circulars/FAOP64672.pdf
- NSE circular NSE/FAOP/70616, 2025-10-03, revised NIFTY lot 75 to 65: https://nsearchives.nseindia.com/content/circulars/FAOP70616.pdf
- NSE contract information page: https://www.nseindia.com/static/products-services/equity-derivatives-contract-information

## Implementation test

For each trade, store both `trade_date` and `expiry_date`; derive `lot_size` from the actual expiry's applicable contract specification. Add unit tests for boundary expiries 2024-12-19, 2025-01-02, 2025-12-23 and 2026-01-06. If an expiry falls on a holiday, map to the official shifted expiry date before applying the schedule.
