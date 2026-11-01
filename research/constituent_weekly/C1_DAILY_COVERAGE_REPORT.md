# C1 Daily OHLCV Member-Session Coverage Report

**Updated:** 2026-11-01T12:47:45.759152+00:00
**Auditor status:** PARTIAL_OR_BLOCKED_RUNTIME_ERROR

## Scope

- Daily OHLCV for each point-in-time tradable NIFTY 50 security/member session from 2018-04-01 to the latest available official daily session.
- Membership intervals are half-open: valid_from is inclusive and valid_to is exclusive.
- The NIFTY session calendar is taken from the cached official daily reference; non-member days are not counted for that security.
- The report checks OHLC invariants and daily volume validity separately.
- Dhan daily history is requested through the historical daily endpoint; no minute/90-day window is requested here.
- Raw market bars and numeric price/volume values are discarded after QA and are not written to this artifact.

## Aggregate results

- Symbols expected: 69
- Symbols with parseable daily responses: 68
- Expected member sessions: 95900
- OHLC coverage: 94799 / 95900 (98.85%)
- OHLCV coverage: 94799 / 95900 (98.85%)

## Per-symbol coverage

| Canonical member symbol | Expected sessions | Valid OHLC | OHLC coverage | Valid OHLCV | OHLCV coverage | Missing OHLC sessions | API status |
|---|---:|---:|---:|---:|---:|---:|---|
| ADANIENT | 1011 | 1011 | 100.00% | 1011 | 100.00% | 0 | PASS_RESPONSE |
| ADANIPORTS | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| APOLLOHOSP | 1136 | 1136 | 100.00% | 1136 | 100.00% | 0 | PASS_RESPONSE |
| ASIANPAINT | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| AXISBANK | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| BAJAJ-AUTO | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| BAJAJFINSV | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| BAJFINANCE | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| BEL | 517 | 517 | 100.00% | 517 | 100.00% | 0 | PASS_RESPONSE |
| BHARTIARTL | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| BPCL | 1525 | 1525 | 100.00% | 1525 | 100.00% | 0 | PASS_RESPONSE |
| BRITANNIA | 1487 | 1487 | 100.00% | 1487 | 100.00% | 0 | PASS_RESPONSE |
| BSE | 21 | 21 | 100.00% | 21 | 100.00% | 0 | PASS_RESPONSE |
| CIPLA | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| COALINDIA | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| DIVISLAB | 994 | 994 | 100.00% | 994 | 100.00% | 0 | PASS_RESPONSE |
| DRREDDY | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| EICHERMOT | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| ETERNAL | 393 | 393 | 100.00% | 393 | 100.00% | 0 | PASS_RESPONSE |
| GAIL | 534 | 534 | 100.00% | 534 | 100.00% | 0 | PASS_RESPONSE |
| GRASIM | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| HCLTECH | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| HDFC | 1100 | 0 | 0.00% | 0 | 0.00% | 1100 | MISSING_DAILY_ARRAY |
| HDFCBANK | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| HDFCLIFE | 1551 | 1551 | 100.00% | 1551 | 100.00% | 0 | PASS_RESPONSE |
| HEROMOTOCO | 1650 | 1650 | 100.00% | 1650 | 100.00% | 0 | PASS_RESPONSE |
| HINDALCO | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| HINDPETRO | 38 | 38 | 100.00% | 38 | 100.00% | 0 | PASS_RESPONSE |
| HINDUNILVR | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| ICICIBANK | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| INDIGO | 268 | 268 | 100.00% | 268 | 100.00% | 0 | PASS_RESPONSE |
| INDUSINDBK | 1650 | 1650 | 100.00% | 1650 | 100.00% | 0 | PASS_RESPONSE |
| INDUSTOWER | 407 | 407 | 100.00% | 407 | 100.00% | 0 | PASS_RESPONSE |
| INFY | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| IOC | 782 | 782 | 100.00% | 782 | 100.00% | 0 | PASS_RESPONSE |
| ITC | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| JIOFIN | 393 | 393 | 100.00% | 393 | 100.00% | 0 | PASS_RESPONSE |
| JSWSTEEL | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| KOTAKBANK | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| LT | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| LTM | 301 | 301 | 100.00% | 301 | 100.00% | 0 | PASS_RESPONSE |
| M&M | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| MARUTI | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| MAXHEALTH | 268 | 268 | 100.00% | 268 | 100.00% | 0 | PASS_RESPONSE |
| NESTLEIND | 1759 | 1759 | 100.00% | 1759 | 100.00% | 0 | PASS_RESPONSE |
| NTPC | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| ONGC | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| POWERGRID | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| RELIANCE | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| SAMMAANCAP | 159 | 159 | 100.00% | 159 | 100.00% | 0 | PASS_RESPONSE |
| SBILIFE | 1511 | 1511 | 100.00% | 1511 | 100.00% | 0 | PASS_RESPONSE |
| SBIN | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| SHREECEM | 624 | 624 | 100.00% | 624 | 100.00% | 0 | PASS_RESPONSE |
| SHRIRAMFIN | 642 | 642 | 100.00% | 642 | 100.00% | 0 | PASS_RESPONSE |
| SUNPHARMA | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| TATACONSUM | 1384 | 1384 | 100.00% | 1384 | 100.00% | 0 | PASS_RESPONSE |
| TATAMOTORS | 1666 | 1665 | 99.94% | 1665 | 99.94% | 1 | PASS_RESPONSE |
| TATASTEEL | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| TCS | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| TECHM | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| TITAN | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| TMPV | 252 | 252 | 100.00% | 252 | 100.00% | 0 | PASS_RESPONSE |
| TRENT | 517 | 517 | 100.00% | 517 | 100.00% | 0 | PASS_RESPONSE |
| ULTRACEMCO | 1918 | 1918 | 100.00% | 1918 | 100.00% | 0 | PASS_RESPONSE |
| UPL | 1276 | 1276 | 100.00% | 1276 | 100.00% | 0 | PASS_RESPONSE |
| VEDL | 367 | 367 | 100.00% | 367 | 100.00% | 0 | PASS_RESPONSE |
| WIPRO | 1897 | 1897 | 100.00% | 1897 | 100.00% | 0 | PASS_RESPONSE |
| YESBANK | 283 | 283 | 100.00% | 283 | 100.00% | 0 | PASS_RESPONSE |
| ZEEL | 407 | 407 | 100.00% | 407 | 100.00% | 0 | PASS_RESPONSE |

## Interpretation and limitations

- Daily history is a mandatory feature source in the registered plan. This report provides actual coverage counts but does not add a new acceptance threshold after the plan was locked.
- A valid daily API response is not by itself a full C1 pass; historical security IDs, point-in-time aliases, corporate actions and target coverage remain separate checks.
- Daily raw prices are not adjusted here for dividends, splits, bonuses, rights, mergers or demergers. The corporate-action adjustment review remains open.
- Volume coverage is measured independently; missing volume stays missing and must not be silently imputed.
- No raw market bars, raw prices, raw volumes, security IDs or credentials are included in this report.

## Reproducibility

- Membership SHA-256: 2bda35125f722c44dd4b402c91d28c57b56e925081bc67ba23a4e31616dee71d
- Official daily-session SHA-256: 5fee1979958e96276e53054c3e76b3818aa6cc1b3abe0e88dd5647c2976104c7
- Dhan scrip-master SHA-256: ad00a05b69606346a5e796bef8715a981242eab8063d615294ce8b3e54981a6a
- Requests this run: 1; cached symbols reused: 69
