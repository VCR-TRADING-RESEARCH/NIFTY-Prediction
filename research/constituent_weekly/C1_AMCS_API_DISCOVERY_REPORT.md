# C1 amcs.fund API metadata discovery

- Run time (UTC): 2026-11-01T05:27:56.919121+00:00
- Scope: **metadata only**; this probe does not request a scheme holdings endpoint, download workbooks, or store constituent values.
- Rights: **UNVERIFIED**. Public API access is not treated as permission for commercial/trading-research extraction, caching, or redistribution.

| Endpoint | Result | HTTP | Content type | Bytes | Top-level records |
|---|---|---:|---|---:|---:|
| API index | PASS_JSON | 200 | application/json; charset=utf-8 | 330 | 4 |
| /amcs | PASS_JSON | 200 | application/json; charset=utf-8 | 15090 | 5 |
| Nippon AMC detail | PASS_JSON | 200 | application/json; charset=utf-8 | 71595 | 5 |
| /manifest | PASS_JSON | 200 | application/json; charset=utf-8 | 3050 | 5 |

## Nippon AMC metadata matches

- {"month": "2026-09", "name": "Nippon India", "slug": "nippon-india"}

## Nifty BeES scheme metadata matches

- {"amc": "nippon-india", "month": "2026-09", "name": "Nippon India ETF Nifty 50 BeES", "slug": "nippon-india-etf-nifty-50-bees"}
- {"amc": "nippon-india", "month": "2026-09", "name": "Nippon India ETF Nifty 1D Rate Liquid BeES", "slug": "nippon-india-etf-nifty-1d-rate-liquid-bees"}
- {"amc": "nippon-india", "month": "2026-09", "name": "Nippon India ETF Nifty Next 50 Junior BeES", "slug": "nippon-india-etf-nifty-next-50-junior-bees"}
- {"amc": "nippon-india", "month": "2026-09", "name": "Nippon India ETF Nifty Bank BeES", "slug": "nippon-india-etf-nifty-bank-bees"}
- {"amc": "nippon-india", "month": "2026-09", "name": "Nippon India ETF Nifty PSU Bank BeES", "slug": "nippon-india-etf-nifty-psu-bank-bees"}
- {"amc": "nippon-india", "month": "2026-09", "name": "Nippon India Nifty Next 50 Junior BeES FoF", "slug": "nippon-india-nifty-next-50-junior-bees-fof"}
- {"amc": "nippon-india", "month": "2026-09", "name": "Nippon India ETF Nifty Infrastructure BeES", "slug": "nippon-india-etf-nifty-infrastructure-bees"}
- {"amc": "nippon-india", "month": "2026-09", "name": "Nippon India ETF Nifty 50 Shariah BeES", "slug": "nippon-india-etf-nifty-50-shariah-bees"}

## Historical source-file metadata matches

- No matching historical source metadata was returned by /manifest.

## Whitelisted source-link checks

- No whitelisted official-AMC or Internet Archive source URL was found to check.

No portfolio holdings, ISINs, quantities, market values, weights, or source-file bytes were downloaded or stored by this probe.
A source URL or successful HEAD response is not proof of disclosure publication time, point-in-time availability, or permission to use the data.
