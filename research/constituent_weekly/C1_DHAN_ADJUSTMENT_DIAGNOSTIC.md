# Dhan Daily Adjusted-Price Corporate-Action Diagnostic

**Updated:** 2026-11-02T09:56:20.229479+00:00
**Overall status:** PASS_BONUS_ADJUSTMENT_FACTOR
**Instrument:** RELIANCE
**Event:** 1:1 bonus; ex-date 2024-10-28
**Dhan daily endpoint:** https://api.dhan.co/v2/charts/historical
**Matched sessions:** 9/9
**Pre-ex median factors (OHLC):** {'open': 0.5, 'high': 0.5, 'low': 0.500002, 'close': 0.5}
**Post-ex median factors (OHLC):** {'open': 1.0, 'high': 1.0, 'low': 1.0, 'close': 1.0}
**Pre/post checks:** True / True

## Primary-source event terms

- Issuer record-date notice: https://www.ril.com/sites/default/files/2024-10/SE_16102024.pdf
- NSE F&O adjustment circular (factor 2, revised market lot 500): https://nsearchives.nseindia.com/content/circulars/FAOP64621.pdf

## Data and privacy

- Raw Dhan/TejHQ prices and ISIN are not written to reports or artifacts.
- The raw TejHQ NSE partition is used only under the personal-use-only workflow opt-in and retained only as AES-GCM encrypted Actions cache.
- Dhan API credentials and tokens are runtime-only; no token values are logged.
- This single bonus-event diagnostic does not validate dividends, rights, mergers, demergers or buybacks.
