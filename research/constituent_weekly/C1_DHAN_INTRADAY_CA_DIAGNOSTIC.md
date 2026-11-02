# Dhan Intraday Corporate-Action Scale Diagnostic

**Updated:** 2026-11-02T19:32:36.963359+00:00
**Status:** COMPLETED_INTRADAY_SCALE_DIAGNOSTIC

Primary test: aggregate the full Dhan intraday session OHLC for the last cum-event day and ex-date, then compare each same-session OHLC field with Dhan daily adjusted historical OHLC for that exact date. This removes the overnight return from the scale comparison.
A pre-event intraday/daily ratio near 1 indicates a common adjusted scale. A pre-event ratio near the reciprocal of the documented event factor (2x for a 1:1 bonus; 10x for the combined 5:1 split + 1:1 bonus) indicates intraday bars remain unadjusted while daily OHLC is adjusted. Ex-date ratios should remain near 1 in either case.

| Symbol | Action | Ex-date | Pre intraday/daily OHLC ratios | Ex-date intraday/daily OHLC ratios | Diagnostic |
|---|---|---|---:|---:|---|
| RELIANCE | 1:1 bonus | 2024-10-28 | {'open': 0.994008, 'high': 0.997211, 'low': 1.0, 'close': 1.000226} | {'open': 1.0, 'high': 1.0, 'low': 1.0, 'close': 1.0003} | INTRADAY_MATCHES_DHAN_DAILY_ADJUSTED_SCALE |
| BAJAJFINSV | 5:1 split plus 1:1 bonus | 2022-09-13 | {'open': 0.996548, 'high': 0.997072, 'low': 1.000164, 'close': 1.006179} | {'open': 1.0, 'high': 0.999756, 'low': 1.0, 'close': 0.997899} | INTRADAY_MATCHES_DHAN_DAILY_ADJUSTED_SCALE |

## Scope and limitations

- Only two issuer/exchange-adjudicated events are tested: one bonus and one combined split/bonus.
- The same-session comparison removes the overnight gap, but remains a diagnostic on only two known events rather than a complete intraday adjustment audit.
- No raw OHLC values, security IDs, access tokens or credentials are published.
- A result does not establish adjustment behavior for all instruments, other event classes or all historical dates.
- The daily endpoint is the adjusted-scale comparator for this test; source-specific intraday adjustment still requires broader independent event coverage.
- If intraday bars are unadjusted, affected weekly stock-return windows must be adjusted using independently verified event factors or excluded before confirmatory fitting.
- Dhan's published support statement explicitly covers **daily** historical OHLCV adjustment for bonuses/splits; its intraday API documentation specifies minute bars and a five-year window but does not state an equivalent corporate-action adjustment guarantee.

## Official Dhan documentation

- Daily historical adjustment statement: https://dhan.co/support/platforms/dhanhq-api/is-the-historical-data-from-dhan-s-data-api-adjusted-for-corporate-actions-like-bonuses-and-splits/
- Intraday historical data documentation: https://dhanhq.co/docs/v2/historical-data/
