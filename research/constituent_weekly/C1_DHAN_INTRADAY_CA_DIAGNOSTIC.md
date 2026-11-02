# Dhan Intraday Corporate-Action Scale Diagnostic

**Updated:** 2026-11-02T19:20:09.974988+00:00
**Status:** BLOCKED_PROFILE_HTTP_401

This diagnostic compares the median close of the final five 1-minute bars on the last cum-event session (15:10–15:14 IST) with the median close of the first five bars on the ex-date (09:15–09:19 IST).
A ratio near the event's expected price factor indicates the intraday history remains on the old/cum-event scale; a ratio near 1 indicates the two sessions are presented on a common adjusted scale. The overnight market move is not removed, so borderline cases are marked ambiguous.

| Symbol | Action | Ex-date | Post/pre ratio | Expected raw factor | Diagnostic |
|---|---|---|---:|---:|---|

## Scope and limitations

- Only two issuer/exchange-adjudicated events are tested: one bonus and one combined split/bonus.
- The ratio is a diagnostic around a known ex-date, not a complete intraday adjustment audit.
- No raw OHLC values, security IDs, access tokens or credentials are published.
- A result does not establish adjustment behavior for all instruments, other event classes or all historical dates.
- If intraday bars are unadjusted, affected weekly stock-return windows must be adjusted using independently verified event factors or excluded before confirmatory fitting.
- Dhan's published support statement explicitly covers **daily** historical OHLCV adjustment for bonuses/splits; its intraday API documentation specifies minute bars and a five-year window but does not state an equivalent corporate-action adjustment guarantee.

## Official Dhan documentation

- Daily historical adjustment statement: https://dhan.co/support/platforms/dhanhq-api/is-the-historical-data-from-dhan-s-data-api-adjusted-for-corporate-actions-like-bonuses-and-splits/
- Intraday historical data documentation: https://dhanhq.co/docs/v2/historical-data/
