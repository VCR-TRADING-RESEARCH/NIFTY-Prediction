# C1 Direct NSE Residual-session Bhavcopy Audit

Updated: 2026-11-01T19:54:48.343345+00:00
Status: PASS_ALL_SEVEN
Direct official NSE rows validated: 7/7.
Encrypted supplemental cache written: True

| Date | Symbol | Session | Result | OHLC | Volume | Identity |
|---|---|---|---|---|---|---|
| 2018-11-07 | HDFC | Diwali Muhurat | VALID_DIRECT_NSE_EQ_OHLCV_ROW | PASS | PASS | MATCH |
| 2019-10-27 | HDFC | Sunday Diwali Muhurat | VALID_DIRECT_NSE_EQ_OHLCV_ROW | PASS | PASS | MATCH |
| 2020-02-01 | HDFC | Saturday Union Budget special session | VALID_DIRECT_NSE_EQ_OHLCV_ROW | PASS | PASS | MATCH |
| 2020-11-14 | HDFC | Saturday Diwali Muhurat | VALID_DIRECT_NSE_EQ_OHLCV_ROW | PASS | PASS | MATCH |
| 2021-11-04 | HDFC | Diwali Muhurat | VALID_DIRECT_NSE_EQ_OHLCV_ROW | PASS | PASS | MATCH |
| 2022-10-24 | HDFC | Diwali Muhurat | VALID_DIRECT_NSE_EQ_OHLCV_ROW | PASS | PASS | MATCH |
| 2025-10-21 | TATAMOTORS | Diwali Muhurat | VALID_DIRECT_NSE_EQ_OHLCV_ROW | PASS | PASS | MATCH |

## Method

Downloaded the exact official NSE cash-market archive for each residual date, selecting legacy CM ZIP/CSV before 8 July 2024 and UDiFF CM ZIP/CSV thereafter. Filtered exact point-in-time symbol, EQ series and trade date; validated unique row, OHLC ordering, nonnegative volume and ISIN. Raw rows are encrypted using the existing BUP01/HF_TOKEN-derived AES-GCM cache key; only metadata and archive hashes are published.

## Limitations

- Legacy CSV is checked by symbol/series/timestamp and ISIN when present.
- Modern UDiFF CSV is checked by TckrSymb/SctySrs/TradDt and ISIN.
- HTTP 404 is unavailable, not proof of no trade.
- Raw rows are persisted only in AES-GCM encrypted Actions cache, not repository or artifacts.
- Daily feature panel and corporate-action adjusted returns are separate gates.
