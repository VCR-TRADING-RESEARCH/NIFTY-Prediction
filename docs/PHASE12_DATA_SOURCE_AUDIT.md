# Phase 12 — Free Data Source Audit

**Checked:** 2026-10-26  
**Status:** FREE SOURCES IDENTIFIED; DATA ACQUISITION AND LINEAGE VALIDATION PENDING

## 1. Official NSE contract-wise price/volume history
- Source: [NSE Historical Contract-wise Price Volume Data](https://www.nseindia.com/report-detail/fo_eq_security)
- Official page exposes filters for instrument, symbol, year, expiry, option type and strike, plus CSV download. It is the preferred exchange source for contract-wise historical prices/volume where coverage and download terms permit.
- Limitation: this page alone does not prove availability of a complete, bulk, one-minute history or bid/ask quotes for the full strategy period. EOD contract data cannot substitute for 10:00 IST executable prices.
- Official daily derivatives reports are also available through [NSE historical derivatives reports](https://www.nseindia.com/resources/historical-reports-capital-market-daily-monthly-archives-derivative-market). The official daily F&O bhavcopy contains contract rows and traded OHLC/volume/OI, but must be aligned to contract identifiers and not mistaken for intraday fills.

## 2. Free expired-option sample data
- Source: [Cloud Trader Pro — NIFTY expired options CSV](https://cloudtraderpro.in/free-historical-nifty-expired-options-data/?ref=shoonyatrader), linked from [Shoonya Trader historical data page](https://shoonyatrader.in/free-historical-expired-options-contract-data/).
- The provider describes a free sample of NIFTY expired weekly/monthly options at one-minute OHLCV + open interest, with a Google Drive download link. The page says the sample expiries are free; full multi-year coverage is requested separately.
- Access attempt: the linked Drive file returned HTTP 401 to the research browsing environment, so bytes were not acquired or validated. Provider-stated coverage is not treated as verified data lineage.
- Limitation: OHLCV bars do not contain historical bid/ask quotes. Midpoint-to-fill assumptions must therefore be conservative and stress-tested; no guarantee of exact historical execution.

## 3. Public NSE bhavcopy archive repository
- Source: [NSE-FNO-Data-bank on GitHub](https://github.com/SantoshSrinivas79/NSE-FNO-Data-bank).
- Its README describes an open-source downloader/validator for official NSE F&O bhavcopy archives and reports daily coverage from 2020-04-13 through 2026-08-31. This is a useful free cache/build reference for EOD contract data and settlement checks.
- Limitation: it stores daily bhavcopy ZIPs, not the 10:00 minute-level expired option price series required for the requested entry time. NSE data remain subject to NSE's terms and rights.

## 4. Paytm Money costs
- Costs must be based on official Paytm Money schedules effective on each historical trade date and instrument. Do not apply the current tariff retrospectively without evidence.
- Required charge fields include brokerage, exchange transaction charges, STT, GST, stamp duty, SEBI charges and other applicable levies. Historical schedule coverage has not yet been joined to contract-level fills.

## Conclusion
The free-source search is **not exhausted** and it would be incorrect to claim historical options data are unavailable everywhere. Free sample data and official EOD contract sources have been identified, but they have not yet been acquired, reconciled and source-registered. Phase 12 remains blocked until a validated dataset supports the exact entry/exit times and a dated cost schedule. No paid source should be considered before these free avenues are fully tested.
