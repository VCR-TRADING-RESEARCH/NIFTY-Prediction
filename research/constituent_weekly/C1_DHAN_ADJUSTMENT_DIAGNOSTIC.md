# Dhan Daily Adjusted-Price Corporate-Action Diagnostics

**Updated:** 2026-11-02T10:08:02.739907+00:00
**Overall status:** PARTIAL_OR_BLOCKED
**Dhan daily endpoint:** https://api.dhan.co/v2/charts/historical
**Authentication:** Fresh TOTP token, HTTP 200 (one attempt); data plan active
**Encrypted TejHQ cache:** 2/2 year partitions hit; 0 downloads

| Symbol | Event | Ex-date | Expected pre factor | Matched dates | Relative OHLC factors | Status |
|---|---|---|---:|---:|---|---|
| RELIANCE | BONUS_1_TO_1 | 2024-10-28 | 0.5 | 9/9 | {'open': 0.5, 'high': 0.5, 'low': 0.500002, 'close': 0.5} | PASS_ADJUSTMENT_FACTOR |

### RELIANCE — BONUS_1_TO_1

- Issuer source: https://www.ril.com/sites/default/files/2024-10/SE_16102024.pdf
- Exchange adjustment source: https://nsearchives.nseindia.com/content/circulars/FAOP64621.pdf
- Security identity transition source: None
- ISIN transition verified: True
- Pre-event Dhan/raw median ratios: {'open': 0.5, 'high': 0.5, 'low': 0.500002, 'close': 0.5}
- Post-event Dhan/raw median ratios: {'open': 1.0, 'high': 1.0, 'low': 1.0, 'close': 1.0}
- Relative event factors: {'open': 0.5, 'high': 0.5, 'low': 0.500002, 'close': 0.5}
- Encrypted TejHQ cache hit: True

| BAJAJFINSV | SPLIT_5_TO_1_PLUS_BONUS_1_TO_1 | 2022-09-13 | 0.1 | 11/11 | {'open': 0.1, 'high': 0.1, 'low': 0.1, 'close': 0.1} | FACTOR_PASS_IDENTITY_WARNING |

### BAJAJFINSV — SPLIT_5_TO_1_PLUS_BONUS_1_TO_1

- Issuer source: https://www.bajajfinserv.in/finserv-digital-annual-report-fy23/assets/pdf/Bajaj-Finserv-AnnualReport-2022-23.pdf
- Exchange adjustment source: https://archives.nseindia.com/content/circulars/FAOP53548.pdf
- Security identity transition source: https://nsearchives.nseindia.com/content/circulars/CML53597.pdf
- ISIN transition verified: False
- Official NSE ISIN effective date: 2022-09-13 (Circular CML53597)
- Observed TejHQ daily-row transition date: 2022-09-14
- Identity discrepancy: the 2022-09-13 row still carries the old ISIN; no correction was applied
- Pre-event Dhan/raw median ratios: {'open': 0.1, 'high': 0.1, 'low': 0.1, 'close': 0.1}
- Post-event Dhan/raw median ratios: {'open': 1.0, 'high': 1.0, 'low': 1.0, 'close': 1.0}
- Relative event factors: {'open': 0.1, 'high': 0.1, 'low': 0.1, 'close': 0.1}
- Encrypted TejHQ cache hit: True

## Data and privacy

- Raw Dhan/TejHQ prices and ISINs are not written to reports or artifacts.
- TejHQ raw partitions are used only under the personal-use-only workflow opt-in and retained only as AES-GCM encrypted Actions cache.
- Dhan API credentials and tokens are runtime-only; no token values are logged.
- These two event diagnostics do not validate dividends, rights, mergers, demergers or buybacks.
