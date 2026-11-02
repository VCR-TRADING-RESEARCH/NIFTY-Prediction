# C1 Continuous Dhan Stock and NIFTY Target Coverage Report

**Updated:** 2026-11-02T21:54:16.471643+00:00
**Status:** PARTIAL_OR_BLOCKED_TARGET_COVERAGE
**Target coverage gate:** FAIL
**Security/action gate:** SYMBOL_MAPPING_RESOLVED_KNOWN_AND_UNIVERSAL_CORPORATE_ACTION_REVIEW_PENDING

## Registered scope

- Point-in-time NIFTY 50 tradable constituents at each weekly forecast anchor.
- One-minute stock candles for the 10:00–10:03 anchor and latest 15:00–15:14 expiry proxy.
- One-minute NIFTY 50 index candles for the same target timestamps; index volume is not required.
- Inclusive Dhan request windows are limited to 90 calendar days.
- The target outcome remains the observed NIFTY 50 index direction; no weight or ETF comparison is involved.

## Coverage summary

| Metric | Result |
|---|---:|
| Scheduled cycles | 260 |
| Valid NIFTY target cycles | 26 |
| NIFTY target valid fraction | 10.00% |
| Cycles meeting 47 / 94% stock rule | 13 |
| Cycles meeting stock + index data gates | 13 |
| Confirmatory cycles after 104 prior cycles | 0 |
| Minimum constituent coverage fraction | 0.00% |
| Median valid constituents | 0.0 |

## Known corporate-action crossing exclusions

| Anchor | Expiry | Excluded security aliases |
|---|---|---|
| 2023-06-30 | 2023-07-06 | HDFC |
| 2025-10-08 | 2025-10-14 | TATAMOTORS |

## Identity and remaining C1 limitations

- Unresolved symbols: None in current scrip-master resolution.
- The current scrip master provides a present-day identifier mapping, not complete historical proof for every inactive security.
- HDFC Ltd and Tata Motors known target-crossing action weeks are separately excluded. All issuer actions, adjustments and symbol/security-ID intervals still require a full dated audit.
- Coverage flags establish that source bars were returned and passed target-window OHLC checks; they do not establish adjusted-return correctness or model skill.
- No raw market bars, raw price/volume values, credentials, access tokens or security IDs are published.
- This report does not pass the entire C1 gate, unlock C2 or certify a trading strategy.

## Reproducibility

- Membership SHA-256: dda5d0aa6cb4feec5edaa53c9a7b099b5d9e46b6020c1ab69c5913f5402d2a08
- Expiry calendar SHA-256: a1a37949278934fbddebd7ea61092930eb7f25ba171c95fca1421e5ae098eaa5
- Official NIFTY daily-session SHA-256: 5fee1979958e96276e53054c3e76b3818aa6cc1b3abe0e88dd5647c2976104c7
- Dhan scrip-master SHA-256: 83c59ef4b2a6234cdda916f0955a9cd7f374989236bb24a5ffc37e5587bd0acd
- Dhan requests this run: 1083
- Cached index chunks: 21; cached stock-symbol chunks: 1062

The machine-readable companion C1_CONTINUOUS_COVERAGE.json contains only source-window status, timestamps, QA flags, and constituent symbols; it does not contain raw market prices or Dhan security IDs.
