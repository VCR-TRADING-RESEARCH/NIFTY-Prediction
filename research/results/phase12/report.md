# Phase 12 — Executable Trading Gate

**Status: BLOCKED_PENDING_CONTRACT_LEVEL_DATA**

Phase 11 model ranking does not establish a tradable strategy. The repository has no source-registered contract-level options/futures fills and no complete date-effective Paytm Money cost schedule linked to those fills. Therefore no strategy P&L is reported.

The automated cost gate requires contract type, side, entry/exit midpoint, spread, slippage, quantity, lot size, explicit statutory/broker charges and source provenance. It computes a conservative net P&L only when these fields exist. Missing input produces a blocked status, not a fabricated backtest.

Required evidence: historical contract identifiers and contract-spec/lot-size history; entry/exit prices with timestamp/fill model; official expiry settlement/exercise treatment; Paytm Money fee schedule effective on each trade date; spread/slippage stress; and an untouched prospective evaluation window.

Conclusion: **NO USABLE TRADING STRATEGY VALIDATED.** Do not trade the directional model on these results.


## Free-source search update
The free-source search identified [official NSE contract-wise historical data](https://www.nseindia.com/report-detail/fo_eq_security), [NSE daily derivatives reports](https://www.nseindia.com/resources/historical-reports-capital-market-daily-monthly-archives-derivative-market), a [public NSE bhavcopy archive project](https://github.com/SantoshSrinivas79/NSE-FNO-Data-bank), and a provider-stated [free NIFTY expired-options sample](https://cloudtraderpro.in/free-historical-nifty-expired-options-data/?ref=shoonyatrader). The free sample's linked Drive download returned HTTP 401 in the research browsing environment. Official EOD bhavcopy alone does not supply the requested 10:00 IST intraday option entry price. Data acquisition and lineage/completeness validation therefore remain pending. This is not a claim that free data is unavailable everywhere; no paid source should be considered before these avenues are tested further. See [source audit](../../docs/PHASE12_DATA_SOURCE_AUDIT.md).
