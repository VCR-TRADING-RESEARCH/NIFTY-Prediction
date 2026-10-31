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


## C1 weight-report discovery (2026-10-31)

The official [NSE Indices monthly reports page](https://niftyindices.com/reports/monthly-reports) lists “Indices Market Capitalisation & Weightage (zip)” and “Market Capitalisation, Weightage, Beta (Zip)”. The official [NSE India all-reports archive](https://www.nseindia.com/all-reports) separately lists “Market Capitalisation, Weightage, Beta for NIFTY 50 & NIFTY Next 50”, equity UDiFF bhavcopy, historical index data, security-wise price/volume and daily/monthly report archives. These are the preferred source paths. A page link alone does not establish historical file coverage or schema.

A page extraction exposed a current-style file path using the mcwb_*.zip naming convention under the NSE Indices monthly report directory. The chat runtime could not fetch the ZIP payload, so no row counts, data columns or historical month coverage are asserted. The Actions workflow records the real retrieval status, URL, archive members, CSV headers, row counts and SHA-256 when available.

## Third-party historic weights candidate — restricted and diagnostic only

The Hugging Face dataset AMP4010/Historical_Nifty_50_Constituent_Weights_20Y describes 216 monthly/event observations from 2008-01 through 2025-08 with 100 ticker columns. The data card says it derives from NSE Indices reports but includes extrapolation for some event changes, static-between-snapshot assumptions and normalisation to 100%; it is licensed CC-BY-NC-SA 4.0. It is not accepted as primary data and must not be used for commercial deployment. A direct chat-runtime download attempt failed; no local raw data was retrieved. Use the data card only for discovery and, subject to licence, an optional non-commercial sanity check.

## Daily point-in-time weight derivation

Between official snapshots, a daily weight may be algebraically drifted only under the explicit fixed-universe, fixed-index-shares and fixed-IWF assumption:

w_i(t) = [w_i(t0) × P_i(t) / P_i(t0)] / Σ_j [w_j(t0) × P_j(t) / P_j(t0)]

This is a hypothesis to validate, not an approved input yet. A rebalance, IWF change, split, bonus, rights, merger, demerger, spin-off, divisor/index-share change or security-identity event resets the reconstruction or invalidates the affected cycle until the official treatment is applied. Check report publication time, not just as-of date; a report published after the 10:00 forecast is future information.

The audit must compare reconstructed weights against the next official snapshot, report top-weight and total absolute deviations, and then compare the realised weighted constituent basket with the official NIFTY price-return index. Tolerance must be registered before model fitting.

## Source-code review of the membership candidate

The BKKB20 reconstruction uses circular-derived ticker snapshots and audit warnings, not numerical free-float weights. The reviewed query script has a hard-coded Windows path and derives snapshot keys from a parsed circular date; confirm that the date is the index effective date rather than publication/announcement date. Alias mappings that collapse predecessors and successors (for example HDFC/HDFCBANK and MINDTREE/LTIM) are not sufficient for point-in-time security identity. The current-member CSV has 50 symbols, but is not date-certified for the forecast history. Preserve distinct ISIN/security IDs and validity dates before reconstructing past membership.


## Data rights and reuse boundaries (updated 2026-10-31)

### NSE / NSE Indices

The official NSE Indices Terms of Use (https://www.niftyindices.com/terms-of-use) state:
- systematic or automated data collection, scraping, extraction or harvesting without express written consent is prohibited (clause 12);
- copying, reproducing, republishing, uploading, transmitting or distributing site material without prior written permission is restricted (clause 7);
- website use is described as personal, non-commercial use only, and clause 20 also prohibits aggregation/copy/duplication of site content.

The initial report sample was retrieved before this terms review. The current BUP-01 workflow is offline-only and does not request NSE endpoints or upload raw archives. Any further use of NSE archive content needs the relevant use/redistribution permission or an independently licensed supply arrangement. Do not treat a public download link as an unrestricted market-data licence.

### Licensed / user-entitled Dhan data

Dhan v2 documentation specifies:
- daily OHLCV is documented back to instrument inception (https://dhanhq.co/docs/v2/historical-data/, lines on daily historical data);
- 1-minute intraday data is documented for the last five years for active instruments;
- a maximum 90-day range can be polled per intraday request.

This is a promising route for stock prices under the user's existing subscription, but it does not establish coverage for historical instruments that are now inactive, delisted or merged. C1 must test actual account entitlement, authentication, current security-master mappings and a representative sample of current/removed securities before bulk collection. Keep Dhan credentials in Actions/runtime secrets only.

The parent repository already has a Dhan integration in scripts/fetch_dhan_recent.py and live_api/app.py. The former is an index-only cross-check and cannot be repurposed as a constituent downloader without extension. The latter refreshes a token and caches historical NIFTY index bars, but the parent logs record inconsistent token/TOTP renewal and a DH-905 response for a separate rolling-options request. That failure does not prove equity candle requests fail; it does mean the new stock-data preflight must be an isolated, non-secret, fail-closed test. Do not assume that Dhan access is currently working. Do not build a parallel auth/token implementation until the existing code has been audited.

### Open-source code vs market data ownership

- [floyds1995/Auto-Index-Constituents-Tracker](https://github.com/floyds1995/Auto-Index-Constituents-Tracker) publishes MIT-licensed software for automated historical index-constituent tracking and NSE reference/price archives. The software licence does not automatically licence underlying NSE market data; its README flags source-data ownership/redistribution conditions. Reuse code only after checking its current licence and dependencies; do not assume its bundled/downloaded market data can be republished.
- [NikhilSuthar/indian-market-data](https://github.com/NikhilSuthar/indian-market-data) is MIT-licensed software that wraps NSE/BSE/MCX/MSCI archives and documents a NIFTY market-cap/weightage report dataset. This is a convenient API wrapper, not an independent data licence; the source exchange's use terms still apply.
- [BKKB20/nse-index-history](https://github.com/BKKB20/nse-index-history) is a reconstruction candidate with circular/date/security alias limitations described above. Its current-members file differs from the official September 2026 sample (WIPRO only in the candidate; BSE only in the official sample), and is not a verified current or historical master.
- [vishalvx/nifty-indices-datasets](https://github.com/vishalvx/nifty-indices-datasets) is binary membership only; it has no numerical free-float weights.
- [AMP4010/Historical_Nifty_50_Constituent_Weights_20Y](https://huggingface.co/datasets/AMP4010/Historical_Nifty_50_Constituent_Weights_20Y) is CC-BY-NC-SA 4.0 according to its data card. It describes 216 monthly/event-date rows from 2008-01 to 2025-08, but also says it extrapolates some rebalance/event weights, assumes static weights between snapshots and normalises rows to 100%. It is not accepted as a confirmatory primary weight source. Use is conditional on the project's non-commercial purpose and full attribution/share-alike compliance; do not put its raw dataset into the public repository or a commercial workflow.

## Current decision and C1 next step

No source currently clears all of: legal rights for the intended use, exact point-in-time NIFTY 50 membership, numeric free-float weights, publication-time evidence, stable ISIN/security-ID history, corporate-action treatment, stock-level 10:00/expiry bars, and basket-to-index reconciliation.

The next C1 step is to reuse and audit the parent Dhan token/data path, conduct a small current-stock daily/intraday endpoint preflight through Actions secrets, then explicitly test removed/inactive instrument coverage using lawful user-entitled inputs. The weight-source problem remains a separate gate; Dhan daily equity data alone does not provide historic NIFTY index weights.


## Official index construction detail (verified 2026-10-31)

NSE Indices states that NIFTY 50 uses free-float market-cap weighting from 26 June 2009. Its IWF description explains that free-float capitalisation is total shares outstanding × IWF × stock price, and that constituent IWFs are determined from public shareholding patterns reported to exchanges quarterly. See:
- https://www.niftyindices.com/indices/equity/broad-based-indices/nifty--50
- https://www.niftyindices.com/resources/investible-weight-factors
- https://niftyindices.com/resources/tutorial/calculation-of-indices

Implications for the C1 data audit:
1. A dated constituent list is insufficient; historical point-in-time IWF and effective dates are required.
2. Weight reconstruction between snapshots must not carry forward a stale float factor across a quarterly public-shareholding update or a corporate action.
3. Publication/filing timestamps must be distinguished from the underlying shareholding quarter, because a later filing cannot be used as if it were available at the earlier 10:00 forecast.
4. The exact free-float weight formula and index-divisor adjustments must be reconciled against the official index methodology before stock-level forecasts are aggregated.


## Licensed point-in-time membership and shareholding source (reviewed 2026-10-31)

**Candidate:** [aditya-jha/nse-historical-membership](https://github.com/aditya-jha/nse-historical-membership), source revision `cc6f89fd6699a92afa8d398896d0aac385eb9e8c`. Its data files carry CC BY 4.0 under the source repository's `LICENSE-DATA`; code is MIT. BUP-01 includes the NIFTY 50-only effective-dated subset at `data/derived/constituent_weekly/nifty50_membership_intervals.csv` and the attribution/caveats at `C1_MEMBERSHIP_DATA_ATTRIBUTION.md`.

Audited membership subset:
- 83 membership intervals, 82 distinct historical symbols.
- 50 intervals are `snapshot_floor`; 33 are `press_release` sourced.
- 93 sampled month-15 dates from 2018-01 through 2025-09 had 50 overlapping active intervals each.
- The latest NIFTY 50 effective event in this data is 2025-09-30. This does not give us the October 2026 current universe.
- The `weightage` field is empty for all NIFTY 50 intervals checked; the file supplies membership dates, not historical free-float weights.
- The source's own 2026-05 validation report records 29/29 curated transition checks passing and 0/42 current-snapshot mismatches, but major pre-2018 G2/G4 cardinality and consistency failures. We restrict confirmatory use to candidate 2018+ intervals and retain the source confidence flag; a 50-row count at a sample date is not independent member-by-member validation.

**Quarterly ownership dataset in the same CC BY 4.0 repository:** `shareholding_history/data/parsed/_flat.csv` contains 59,773 rows across the broader NSE universe. Matching symbols to NIFTY 50 membership intervals found 2,584 records for 78 historically matching tickers. Quarter-end coverage against the reconstructed 50-stock membership:
- 2018-03: 37/50 (74%)
- 2018-06: 47/50 (94%)
- 2020-06: 41/50 (82%)
- 2022-03: 43/50 (86%)
- 2023-06: 49/50 (98%)
- 2023-09 onward through 2025-09: 50/50 for each audited quarter.
The ownership file includes promoter, FII, DII, public and non-institutional roll-ups, share count, filing date, submission date and XBRL filename. It does **not** contain the complete public-shareholding category detail needed to reproduce official IWF exclusions. The actual `_categories.csv.gz` file mentioned in older documentation is absent from the pinned source tree.

The filing-index manifests retain `broadcast_date`, `revised` and record IDs, but `_flat.csv` does not. We inspected a RELIANCE manifest and verified that the broadcast timestamp is recorded separately from the quarter-end/report date. Before any ownership feature is used, BUP-01 must join each parsed row to its manifest by XBRL filename, use broadcast time as its availability timestamp, and exclude any ownership fact not broadcast before the weekly 10:00 IST forecast. Submission date alone is only day-resolution and is insufficient where a same-day 10:00 cutoff matters.

**Critical mathematical warning:** `IWF ≠ 100% − promoter_pct`. Official NIFTY float methodology excludes multiple strategic/locked/controlled holdings beyond promoter ownership. The current five-roll-up public data cannot support official free-float weights, and the derived ownership roll-ups must not be used as a substitute.

### AMFI ETF portfolio data — identified but not accepted

AMFI's public monthly portal contains scheme portfolio Excel/PDF files from at least 2019 through 2026, including NIFTY 50 ETF/fund schemes. This could provide a cross-check of ETF-replicated holdings, not official index weights. AMFI Terms of Use grant only personal/non-commercial access and prohibit public display, publication, derivative works and electronic storage of significant portions. The files are therefore not used or automated in this public repository without express permission. SEBI's circulars require portfolio disclosures, but regulatory disclosure does not override AMFI's site-use terms. Source: https://www.amfiindia.com/research-information/amfi-monthly and https://www.amfiindia.com/terms-of-use.

## Additional public weight-source sweep — 2026-10-31

A further search across Hugging Face, GitHub and Figshare surfaced no clearly reusable, commercially permissive official historical IWF series:

| Candidate | Coverage/content | Rights/quality finding | Decision |
|---|---|---|---|
| [AMP4010 Historical Nifty 50 Constituent Weights](https://huggingface.co/datasets/AMP4010/Historical_Nifty_50_Constituent_Weights_20Y) / [Figshare DOI](https://doi.org/10.6084/m9.figshare.30217915) | 216 monthly/event snapshots, 2008-01-31 to 2025-08-31; 100 ticker columns; rows normalised to 100% | CC BY-NC-SA 4.0 (non-commercial only); publisher documents static-between-snapshot assumptions and estimates/extrapolations for some gaps/events | NOT ACCEPTED for the trading research workflow without separate commercial permission and independent event/weight validation |
| [vishalvx/nifty-indices-datasets](https://github.com/vishalvx/nifty-indices-datasets) | Reconstructed monthly membership/binary weights | Binary/equal-weight approximations, not numeric official free-float weights | Membership diagnostic only |
| [BKKB20/nse-index-history](https://github.com/BKKB20/nse-index-history) | Reconstructed historical membership from circulars; current-member files dated March 2026 | No numeric IWF series; known scanned-circular and identity-mapping gaps | Membership diagnostic only |
| [Auto-Index-Constituents-Tracker](https://github.com/floyds1995/Auto-Index-Constituents-Tracker) | Daily NSE equity EOD history and index composition change snapshots | Best-effort reconstructions; publisher explicitly notes NSE redistribution is subject to NSE terms | Do not ingest/redistribute pending rights review; potential source-discovery lead only |

The HF dataset's exact row-sum validation is useful as a structural check, but it does not cure its non-commercial licence, its snapshot/static assumption, or the need to prove point-in-time availability for a weekly 10:00 IST forecast. Do not infer a daily IWF by carrying monthly weights forward without corporate-action and official-snapshot reconciliation.

**Source sweep conclusion:** the best currently reusable open candidate remains the CC BY 4.0 membership/quarterly ownership repository already cached. It is not a numerical index-weight source. C1 therefore remains blocked; no model work is authorised.
