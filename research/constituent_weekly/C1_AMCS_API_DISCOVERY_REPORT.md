# C1 amcs.fund API metadata discovery

- Run time (UTC): 2026-11-01T08:48:12.501948+00:00
- Scope: **metadata only**; the probe calls the documented scheme/month endpoints but retains only date/source metadata, discards ISIN-level holdings fields, does not download workbooks, and does not store portfolio values.
- Rights: **UNVERIFIED**. Public API access is not treated as permission for commercial/trading-research extraction, caching, or redistribution.

| Endpoint | Result | HTTP | Content type | Bytes | Top-level records |
|---|---|---:|---|---:|---:|
| API index | PASS_JSON | 200 | application/json; charset=utf-8 | 330 | 4 |
| /amcs | PASS_JSON | 200 | application/json; charset=utf-8 | 15090 | 5 |
| Nippon AMC detail | PASS_JSON | 200 | application/json; charset=utf-8 | 71595 | 5 |
| /scheme/{slug} | PASS_JSON | 200 | application/json; charset=utf-8 | 19743 | 5 |
| /manifest | PASS_JSON | 200 | application/json; charset=utf-8 | 3050 | 5 |
| Tipsheet /data/v1/manifest.json | PASS_JSON | 200 | application/json | 252882 | 3 |
| /month/2026-09 | PASS_JSON | 200 | application/json; charset=utf-8 | 15250 | 5 |
| /month/2019-04 | PASS_JSON | 200 | application/json; charset=utf-8 | 7880 | 5 |
| /month/2022-09 | PASS_JSON | 200 | application/json; charset=utf-8 | 14444 | 5 |
| /month/2025-09 | PASS_JSON | 200 | application/json; charset=utf-8 | 10934 | 5 |

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
- API index top-level JSON keys: api, docs, endpoints, unit
- /amcs top-level JSON keys: api, data, month, source, unit
- AMC detail top-level JSON keys: api, data, month, source, unit
- /scheme/{slug} top-level JSON keys: api, data, month, source, unit
- /manifest top-level JSON keys: api, data, month, source, unit
- /scheme/{slug} JSON shape: {"data_keys": ["events", "exited", "first_month", "flows_basis", "history", "hold_hist", "holdings", "investors", "lookthrough", "mix", "peers", "prev_month", "returns", "scheme", "unit"], "data_nested_types": {"events": "list", "exited": "list", "first_month": "str", "flows_basis": "str", "history": "list", "hold_hist": "dict", "holdings": "list", "investors": "NoneType", "lookthrough": "NoneType", "mix": "dict", "peers": "list", "prev_month": "str", "returns": "dict", "scheme": "dict", "unit": "str"}, "data_type": "dict", "events_count": 1, "events_item_keys": ["kind", "m"], "history_count": 51, "holdings_count": 51, "holdings_item_keys": ["cr", "dq_pct", "ind", "isin", "key", "name", "pct", "qty", "sector", "t"], "root_keys": ["api", "data", "month", "source", "unit"], "root_type": "object"}
- /month/2026-09 JSON shape: {"data_keys": ["amcs", "buys", "events", "flows_basis", "groups", "label", "month", "next", "prev", "rich", "sector_flows", "sells", "totals", "unit"], "data_nested_types": {"amcs": "list", "buys": "list", "events": "list", "flows_basis": "str", "groups": "list", "label": "str", "month": "str", "next": "NoneType", "prev": "str", "rich": "bool", "sector_flows": "list", "sells": "list", "totals": "dict", "unit": "str"}, "data_type": "dict", "events_count": 32, "events_item_keys": ["amc", "amc_name", "aum", "kind", "live", "name", "slug"], "root_keys": ["api", "data", "month", "source", "unit"], "root_type": "object"}
- /month/2019-04 JSON shape: {"data_keys": ["amcs", "buys", "events", "flows_basis", "groups", "label", "month", "next", "prev", "rich", "sector_flows", "sells", "totals", "unit"], "data_nested_types": {"amcs": "list", "buys": "list", "events": "list", "flows_basis": "str", "groups": "list", "label": "str", "month": "str", "next": "str", "prev": "str", "rich": "bool", "sector_flows": "list", "sells": "list", "totals": "dict", "unit": "str"}, "data_type": "dict", "events_count": 1, "events_item_keys": ["amc", "amc_name", "aum", "kind", "live", "name", "slug"], "root_keys": ["api", "data", "month", "source", "unit"], "root_type": "object"}
- /month/2022-09 JSON shape: {"data_keys": ["amcs", "buys", "events", "flows_basis", "groups", "label", "month", "next", "prev", "rich", "sector_flows", "sells", "totals", "unit"], "data_nested_types": {"amcs": "list", "buys": "list", "events": "list", "flows_basis": "str", "groups": "list", "label": "str", "month": "str", "next": "str", "prev": "str", "rich": "bool", "sector_flows": "list", "sells": "list", "totals": "dict", "unit": "str"}, "data_type": "dict", "events_count": 37, "events_item_keys": ["amc", "amc_name", "aum", "kind", "live", "name", "slug"], "root_keys": ["api", "data", "month", "source", "unit"], "root_type": "object"}
- /month/2025-09 JSON shape: {"data_keys": ["amcs", "buys", "events", "flows_basis", "groups", "label", "month", "next", "prev", "rich", "sector_flows", "sells", "totals", "unit"], "data_nested_types": {"amcs": "list", "buys": "list", "events": "list", "flows_basis": "str", "groups": "list", "label": "str", "month": "str", "next": "str", "prev": "str", "rich": "bool", "sector_flows": "list", "sells": "list", "totals": "dict", "unit": "str"}, "data_type": "dict", "events_count": 12, "events_item_keys": ["amc", "amc_name", "aum", "kind", "live", "name", "slug"], "root_keys": ["api", "data", "month", "source", "unit"], "root_type": "object"}

## Scheme-history metadata (source URLs and dates only)

- {"amc": "nippon-india", "month": "2026-09", "name": "Nippon India ETF Nifty 50 BeES", "slug": "nippon-india-etf-nifty-50-bees"}

## Month-level source metadata

- {"month": "2026-09"}
- {"month": "2019-04"}
- {"month": "2022-09"}
- {"month": "2025-09"}

## Tipsheet NIFTY 50 weight-data catalogue entries

- No NIFTY 50 weight dataset entry was found in the Tipsheet manifest.
- Tipsheet says its files are free to fetch with attribution, but upstream sources retain their own terms; this report does not establish a blanket redistribution licence.

## Historical source-file metadata matches

- No matching historical source metadata was returned by /manifest.

## Whitelisted source-link checks

- No whitelisted official-AMC or Internet Archive source URL was found to check.

No portfolio holdings, ISINs, quantities, market values, weights, or source-file bytes were downloaded or stored by this probe.
A source URL or successful HEAD response is not proof of disclosure publication time, point-in-time availability, or permission to use the data.
