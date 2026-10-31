# Data Source Register — BUP-01

**Last reviewed:** 2026-10-31  
**Status:** Document-level source discovery complete; empirical coverage audit pending C1.

| Priority | Source | Intended data | Evidence / status |
|---:|---|---|---|
| 1 | NSE historical reports | UDiFF bhavcopy, security master, corporate actions, index history, FII/DII and expiry archives | https://www.nseindia.com/all-reports. Official candidate; archive depth, schemas, publication timestamps and rights must be checked. |
| 1 | NSE Indices NIFTY 50 | Constituents, methodology, historical index data and reconstitution evidence | https://www.nseindia.com/static/products-services/indices-nifty50-index. Historical effective dates and weights must be reconstructed. |
| 1 | NSE Indices monthly reports | Historical constituent weightage and market-cap reports | https://niftyindices.com/reports/monthly-reports. Record exact coverage and availability dates. |
| 1 | NSE IWF / methodology | Free-float factors and index computation | https://www.nseindia.com/static/products-services/indices-investible-weight-factors and https://archives.nseindia.com/content/indices/Method_Nifty_50.pdf. Historical point-in-time factors are still required. |
| 1 | NSE F&O archives | Verified NIFTY weekly expiries and calendar | Reuse parent repo's verified expiry artifacts; do not assume a fixed weekday. |
| 2 | DhanHQ v2 | One-minute anchors/expiry closes and daily stock OHLCV | https://dhanhq.co/docs/v2/historical-data/. Docs state up to five years intraday for active instruments and 90-day windows; test auth, entitlement and inactive instruments. |
| 2 | BSE public market data | Cross-check dual-listed securities and corporate actions | Supplemental only; reconcile identifiers and timing. |
| 3 | BKKB20/nse-index-history | Reconstructed historical NIFTY membership/change dates | https://github.com/BKKB20/nse-index-history. Candidate only; original circular validation required; scanned circular and ticker-mapping gaps disclosed. |
| 3 | vishalvx/nifty-indices-datasets | Monthly membership cross-check | https://github.com/vishalvx/nifty-indices-datasets. Binary membership only; not numeric weights. |
| 3 | Zenodo / Kaggle / Hugging Face / GitHub | Historical minute/daily equities | Search by stable security ID and date. Validate source lineage, survivorship, adjustment, timestamps, coverage and licence. |
| Optional | India VIX / sector / global benchmarks | Regime and external context | Point-in-time availability and time-zone validation required. |
| Optional | FII/DII reports | Positioning/flow context | Use only if the report was published before forecast time. |
| Optional | News and corporate announcements | Event/sentiment features | Require historical publication timestamps and lawful use. |

## Dhan-specific implementation notes

- Request only instruments with an as-of security-ID mapping.
- Split intraday requests into windows no longer than 90 days; use API throttling/backoff.
- Store raw response hashes and sanitized metadata; never log credentials or auth response bodies.
- Verify the 10:00–10:03 anchor and 15:25–15:29 expiry bar for every included stock-cycle.
- Dhan documentation's active-instrument qualifier does not establish coverage for delisted/merged legacy constituents. Prove coverage or exclude with reason.
- Do not treat authentication as working until a real data request succeeds in Actions with secrets protected.

## Membership/security mapping

Build a canonical security table using ISIN, exchange segment/security ID and validity dates. Retain raw symbol, normalized symbol, historical aliases, issuer, corporate-action event, effective date, official source/circular and confidence. Reconstruct membership effective at forecast time and compare each change with original exchange evidence.

## Weight history

- Prefer official free-float constituent weights/IWF and market-cap weightage snapshots.
- Record report date separately from public availability timestamp.
- If a snapshot is carried between official reports, specify the price/IWF/corporate-action recursion and test against the next official snapshot.
- Never use today's weights as if they were known at earlier forecast dates.
- Binary membership or equal-weight assumptions are not acceptable primary weights.

## Composite dataset policy

Combine sources only after matching stable identifiers, timestamps and adjustment conventions. Retain source name, security ID, timestamp, raw and normalized values, adjustment factor, conflict flag, chosen-source reason and file hash. Never silently drop disagreements or overwrite source-native values.

## Phase C1 checklist

- [ ] Official expiries and next NSE sessions resolved.
- [ ] Historic membership dates supported by documentary evidence.
- [ ] Numeric free-float weights/IWF point-in-time available or reproducibly reconstructed.
- [ ] Security master resolves historical aliases, ISINs, IDs and corporate actions.
- [ ] Split/bonus/rights/merger/demerger/dividend handling tested.
- [ ] Stock anchor and expiry-close coverage quantified by symbol, date and index weight.
- [ ] At least 98% of free-float weight represented at both endpoints for accepted cycles.
- [ ] Realised weighted basket reconciles with official NIFTY within a tolerance frozen before modelling.
- [ ] Data rights reviewed; no raw private/broker data committed.
- [ ] Cache keys, hashes, provenance and exclusions retained.
