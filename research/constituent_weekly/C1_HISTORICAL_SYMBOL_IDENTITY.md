# C1 historical symbol identity review

**Review date:** 2026-11-01  
**Confirmatory membership start:** 2018-04-01 (pre-2018 rows remain exploratory only).

| Historical alias | Ledger interval | Evidence / identity event | C1 handling |
|---|---|---|---|
| `HDFC` | 2014-01-01 to 2023-07-13 | HDFC Ltd merged into HDFC Bank effective 2023-07-01. Dhan v2 documentation includes HDFC Ltd as legacy security ID 1330 / ISIN INE001A01036 in its holdings example. | Test legacy ID 1330 for 2022-10-31 and 2023-06-30 intraday candles. Preserve pre-merger HDFC as a separate listed security; do not replace its whole history with HDFCBANK prices. |
| `JPASSOCIAT` | 2014-01-01 to 2014-03-28 | NSE reports suspension from 2026-03-18 and delisting from 2026-06-18; ledger membership is only in 2014 and outside confirmatory window. | Not a C1 confirmatory-window price blocker. Keep a historic-security archive note; do not substitute a successor. |
| `RANBAXY` | 2014-01-01 to 2014-03-28 | Ranbaxy merged into Sun Pharma in 2015; shareholders received 0.8 Sun Pharma shares per Ranbaxy share; trading stopped after 2015-04-01 close. Outside confirmatory window. | Not a C1 confirmatory-window price blocker. Preserve distinct pre-merger security; do not join raw price levels to SUNPHARMA. |
| `MCDOWELL-N` | 2014-03-28 to 2014-09-19 | NSE symbol changed to `UNITDSPR` effective 2024-06-07. Outside confirmatory window. | Record the same-issuer symbol alias; no reason to block 2018+ confirmatory panel. |
| `TATAMOTORS` | 2014-01-01 to 2025-10-24 | NSE circular changed symbol/name to `TMPV` effective 2025-10-24. | Treat as a dated same-listing symbol/name event for security resolution, but preserve a corporate-action marker and do not assume pre/post-demerger price continuity without adjusted data. |

## Evidence

- NSE circular NSE/FAOP/62365: [MCDOWELL-N → UNITDSPR, 2024-06-07](https://nsearchives.nseindia.com/content/circulars/FAOP62365.pdf).
- NSE circular NSE/FAOP/70882: [TATAMOTORS → TMPV, 2025-10-24](https://nsearchives.nseindia.com/content/circulars/FAOP70882.pdf).
- HDFC Bank: [HDFC Ltd merger effective 2023-07-01](https://www.hdfc.bank.in/press-release/2023/q2/hdfc-ltd-to-merge-into-hdfc-bank-effective-july-1-2023); Dhan API docs show legacy HDFC ID 1330 and ISIN [here](https://dhanhq.co/docs/v2/portfolio/).
- NSE: [JPASSOCIAT suspension circular](https://nsearchives.nseindia.com/content/circulars/CML73342.pdf) and [delisting circular](https://nsearchives.nseindia.com/content/circulars/CML74660.pdf).
- Sun Pharma: [Ranbaxy merger completion](https://www.daiichisankyo.com/media/press_release/detail/index_3515.html).

These events clarify the identity history but do not themselves prove historical Dhan candle coverage. The legacy HDFC probe is still required. JPASSOCIAT, RANBAXY and MCDOWELL-N end before the 2018-04 confirmatory cutoff, so they should not block the core 2018+ experiment.
