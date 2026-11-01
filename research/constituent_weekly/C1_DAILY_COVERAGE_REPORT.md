# C1 Daily OHLCV Member-Session Coverage Report

**Updated:** 2026-11-01T14:27:03.642080+00:00
**Auditor status:** COMPLETED_WITH_GAPS

## Scope

- Daily OHLCV for each point-in-time tradable NIFTY 50 security/member session from 2018-04-01 to the latest available official daily session.
- Membership intervals are half-open: valid_from is inclusive and valid_to is exclusive.
- The NIFTY session calendar is taken from the cached official daily reference; non-member days are not counted for that security.
- The report checks OHLC invariants and daily volume validity separately.
- Dhan daily history is requested through the historical daily endpoint; no minute/90-day window is requested here.
- Restricted fallback uses personal-use TejHQ raw NSE EQ bhavcopy pinned to a fixed dataset commit. Raw Parquet is read in temporary storage; only AES-256-GCM encrypted cache files and sanitized coverage metadata may persist.
- TejHQ terms (updated 2026-10-30) permit personal research and one's own trading decisions, but not client/business use or raw-data redistribution. The MIT licence covers code, not exchange data; NSE terms continue to apply.
- Source terms: https://tejhq.dev/data-terms; dataset description: https://huggingface.co/datasets/tejhq/indian-markets.
- Raw market bars and numeric price/volume values are discarded after QA and are not written to this artifact.

## Aggregate results

- Symbols expected: 70
- Symbols with parseable daily responses: 69
- Expected member sessions: 106392
- OHLC coverage: 106385 / 106392 (99.99%)
- OHLCV coverage: 106385 / 106392 (99.99%)

## Per-symbol coverage

| Canonical member symbol | Expected sessions | Valid OHLC | OHLC coverage | Valid OHLCV | OHLCV coverage | Missing OHLC sessions | API status |
|---|---:|---:|---:|---:|---:|---:|---|
| ADANIENT | 1012 | 1012 | 100.00% | 1012 | 100.00% | 0 | PASS_RESPONSE |
| ADANIPORTS | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| APOLLOHOSP | 1137 | 1137 | 100.00% | 1137 | 100.00% | 0 | PASS_RESPONSE |
| ASIANPAINT | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| AXISBANK | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| BAJAJ-AUTO | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| BAJAJFINSV | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| BAJFINANCE | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| BEL | 517 | 517 | 100.00% | 517 | 100.00% | 0 | PASS_RESPONSE |
| BHARTIARTL | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| BPCL | 1735 | 1735 | 100.00% | 1735 | 100.00% | 0 | PASS_RESPONSE |
| BRITANNIA | 1488 | 1488 | 100.00% | 1488 | 100.00% | 0 | PASS_RESPONSE |
| BSE | 21 | 21 | 100.00% | 21 | 100.00% | 0 | PASS_RESPONSE |
| CIPLA | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| COALINDIA | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| DIVISLAB | 995 | 995 | 100.00% | 995 | 100.00% | 0 | PASS_RESPONSE |
| DRREDDY | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| EICHERMOT | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| ETERNAL | 393 | 393 | 100.00% | 393 | 100.00% | 0 | PASS_RESPONSE |
| GAIL | 743 | 743 | 100.00% | 743 | 100.00% | 0 | PASS_RESPONSE |
| GRASIM | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| HCLTECH | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| HDFC | 1301 | 1295 | 99.54% | 1295 | 99.54% | 6 | PARTIAL_WITH_TEJHQ_FALLBACK |
| HDFCBANK | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| HDFCLIFE | 1552 | 1552 | 100.00% | 1552 | 100.00% | 0 | PASS_RESPONSE |
| HEROMOTOCO | 1860 | 1860 | 100.00% | 1860 | 100.00% | 0 | PASS_RESPONSE |
| HINDALCO | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| HINDPETRO | 247 | 247 | 100.00% | 247 | 100.00% | 0 | PASS_RESPONSE |
| HINDUNILVR | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| ICICIBANK | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| INDIGO | 268 | 268 | 100.00% | 268 | 100.00% | 0 | PASS_RESPONSE |
| INDUSINDBK | 1860 | 1860 | 100.00% | 1860 | 100.00% | 0 | PASS_RESPONSE |
| INDUSTOWER | 616 | 616 | 100.00% | 616 | 100.00% | 0 | PASS_RESPONSE |
| INFY | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| IOC | 991 | 991 | 100.00% | 991 | 100.00% | 0 | PASS_RESPONSE |
| ITC | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| JIOFIN | 393 | 393 | 100.00% | 393 | 100.00% | 0 | PASS_RESPONSE |
| JSWSTEEL | 2004 | 2004 | 100.00% | 2004 | 100.00% | 0 | PASS_RESPONSE |
| KOTAKBANK | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| LT | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| LTM | 302 | 302 | 100.00% | 302 | 100.00% | 0 | PASS_RESPONSE |
| LUPIN | 124 | 124 | 100.00% | 124 | 100.00% | 0 | PASS_RESPONSE |
| M&M | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| MARUTI | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| MAXHEALTH | 268 | 268 | 100.00% | 268 | 100.00% | 0 | PASS_RESPONSE |
| NESTLEIND | 1760 | 1760 | 100.00% | 1760 | 100.00% | 0 | PASS_RESPONSE |
| NTPC | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| ONGC | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| POWERGRID | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| RELIANCE | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| SAMMAANCAP | 368 | 368 | 100.00% | 368 | 100.00% | 0 | PASS_RESPONSE |
| SBILIFE | 1512 | 1512 | 100.00% | 1512 | 100.00% | 0 | PASS_RESPONSE |
| SBIN | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| SHREECEM | 624 | 624 | 100.00% | 624 | 100.00% | 0 | PASS_RESPONSE |
| SHRIRAMFIN | 642 | 642 | 100.00% | 642 | 100.00% | 0 | PASS_RESPONSE |
| SUNPHARMA | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| TATACONSUM | 1385 | 1385 | 100.00% | 1385 | 100.00% | 0 | PASS_RESPONSE |
| TATAMOTORS | 1876 | 1875 | 99.95% | 1875 | 99.95% | 1 | PASS_RESPONSE |
| TATASTEEL | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| TCS | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| TECHM | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| TITAN | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| TMPV | 252 | 252 | 100.00% | 252 | 100.00% | 0 | PASS_RESPONSE |
| TRENT | 517 | 517 | 100.00% | 517 | 100.00% | 0 | PASS_RESPONSE |
| ULTRACEMCO | 2128 | 2128 | 100.00% | 2128 | 100.00% | 0 | PASS_RESPONSE |
| UPL | 1486 | 1486 | 100.00% | 1486 | 100.00% | 0 | PASS_RESPONSE |
| VEDL | 576 | 576 | 100.00% | 576 | 100.00% | 0 | PASS_RESPONSE |
| WIPRO | 2107 | 2107 | 100.00% | 2107 | 100.00% | 0 | PASS_RESPONSE |
| YESBANK | 492 | 492 | 100.00% | 492 | 100.00% | 0 | PASS_RESPONSE |
| ZEEL | 616 | 616 | 100.00% | 616 | 100.00% | 0 | PASS_RESPONSE |

## Restricted fallback summary

- Dataset: tejhq/indian-markets at revision f576704883fff86a6facdcde336db6ce19502063.
- Fallback status: COMPLETED_WITH_GAPS.
- Accepted symbols: HDFC.
- Encrypted local cache hits: 0; encrypted cache downloads: 7.
- Raw exchange-derived parquet is never persisted in this repository or uploaded as a workflow artifact.

## Interpretation and limitations

- Daily history is a mandatory feature source in the registered plan. This report provides actual coverage counts but does not add a new acceptance threshold after the plan was locked.
- A valid daily API response is not by itself a full C1 pass; historical security IDs, point-in-time aliases, corporate actions and target coverage remain separate checks.
- Daily raw prices are not adjusted here for dividends, splits, bonuses, rights, mergers or demergers. The corporate-action adjustment review remains open.
- Volume coverage is measured independently; missing volume stays missing and must not be silently imputed.
- No raw market bars, raw prices, raw volumes, security IDs or credentials are included in this report.

## Reproducibility

- Membership SHA-256: dda5d0aa6cb4feec5edaa53c9a7b099b5d9e46b6020c1ab69c5913f5402d2a08
- Official daily-session SHA-256: 5fee1979958e96276e53054c3e76b3818aa6cc1b3abe0e88dd5647c2976104c7
- Dhan scrip-master SHA-256: ad00a05b69606346a5e796bef8715a981242eab8063d615294ce8b3e54981a6a
- Requests this run: 71; cached symbols reused: 0
