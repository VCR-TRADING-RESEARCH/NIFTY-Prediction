# BUP-01 Research Status

**Last updated:** 2026-11-02  
**Track:** Bottom-up NIFTY 50 constituent weekly-expiry prediction  
**Status:** C0 PASS; C1 intraday target-data sub-gate PASS; daily OHLCV COMPLETE at 106,392/106,392 (100%); overall C1 PARTIAL pending event-level corporate-action verification and dated historical security-identity closure  
**Prediction status:** No constituent panel, trained stock model or bottom-up forecast exists  
**Trading status:** NOT VALIDATED; no strategy is approved or implied

| Phase | Status | Next action |
|---|---|---|
| C0 — Registration/governance | PASS | Locked v1.3 plan and governance checks passed |
| C1 — Point-in-time universe/data audit | PARTIAL / CORPORATE ACTION + IDENTITY REVIEW | 258/258 intraday weekly target cycles pass; daily OHLCV is 106,392/106,392 across 70 symbols with zero gaps; all seven residual bars validated from official NSE archives and merged via encrypted cache; 711 point-in-time member action candidates still require independent issuer/exchange verification and event-specific treatment; dated historical identity checks remain under review |
| C2 — Panel labels/features | GATED | Build only after C1 acceptance; freeze source hashes, exclusion ledger and chronological split |
| C3 — Stock models/baselines | GATED | Pooled stock panel and bounded benchmarks only after C2 passes |
| C4 — Index aggregation/uncertainty | GATED | Calibrated NIFTY-direction meta-model on strictly OOF unweighted stock forecast summaries |
| C5 — Economic/execution gate | GATED | Contract-level fills and date-effective Paytm Money costs required before any strategy claim |
| C6 — Manuscript/independent audit | GATED | Complete manuscript, plots, tables, appendices and formula/repository audit

## Latest gate update — 2026-11-02

- **Daily OHLCV coverage: PASS.** 106,392/106,392 member sessions across 70 point-in-time symbols; zero OHLC/volume gaps; 100% minimum per-symbol coverage. The daily auditor restored the encrypted cache, downloaded zero TejHQ yearly partitions, and merged seven supplemental official-NSE rows.
- **Official NSE residual archive audit: PASS.** All seven remaining symbol/date pairs (six HDFC sessions and TATAMOTORS 2025-10-21) passed exact symbol/date/EQ, OHLC, volume and ISIN validation using legacy CM and UDiFF archive formats. Raw rows are retained only in AES-GCM encrypted Actions cache.
- **Intraday weekly target coverage: PASS on registered audit set.** 258/258 cycles pass the registered stock-member and NIFTY target coverage checks. Expiry proxy remains the latest valid 15:00–15:14 IST candle (15:15 proxy).
- **Security identity: PARTIAL / REVIEW.** Historical alias resolution remains 79/84 against the current master; dated predecessor/successor identity needs closure for in-scope observations.
- **Corporate actions: NOT PASSED.** 18,361 deduplicated discovery candidates include 711 point-in-time member events. Independent exchange/issuer verification, event-specific terms and affected-cycle adjusted-return/exclusion ledger remain open.
- **Decision:** C1 overall remains PARTIAL; C2–C6 remain gated. ETF/IWF weight comparison and basket-to-index reconstruction are not C1 requirements under locked v1.3.
- Evidence: [daily coverage run 41344197015](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41344197015), [direct NSE audit 41344104457](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41344104457), [offline regression run 41344196948](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41344196948).

## Historical gate update — 2026-11-01 (superseded by 2026-11-02 evidence)

- **Expiry proxy gate: PASS on the tested sample.** By user instruction, the expiry observation is the close of the latest one-minute candle timestamped 15:00 through 15:14 IST, treated as a 15:15 proxy and not mislabeled as the 15:30 exchange close. Protected run [41247509692](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41247509692) passed all 10 five-symbol/two-date anchor and expiry-proxy checks; all selected the 15:14 candle.
- **Current universe: 50/50. Historical symbol master match: 79/84.** A separate legacy HDFC Ltd ID test passed on 2022-10-31 and 2023-06-30 (2/2). JPASSOCIAT, RANBAXY and MCDOWELL-N only appear in the ledger in 2014, before the confirmatory 2018-04 start. TATAMOTORS/TMPV remains a dated demerger/symbol boundary; pre/post prices must not be joined unadjusted.
- **Historical weight candidate: acquired and validated.** 216 dated rows, 100 ticker columns, 2008-01-31 to 2025-08-31; row sums within 4.3e-14 of 100%. Cache: data/constituent_weekly/nifty50_weights_monthly.csv; audit: [C1_NIFTY50_WEIGHT_AUDIT.json](C1_NIFTY50_WEIGHT_AUDIT.json). Licence is CC BY-NC-SA 4.0 and commercial use is not permitted; the source has estimated/extrapolated event weights and is not accepted as official daily IWF.
- **Official source search:** NSE All Reports lists historical “Market Capitalisation, Weightage, Beta for NIFTY 50 & NIFTY Next 50” and “Indices - Market Capitalisation & Weightage” reports. NSE Market Pulse gives some recent sector-level weights but not a full stock-level point-in-time series. Automated NSE collection remains disabled pending rights/licence clearance. The candidate file does not cover 2025-09 onward.
- Latest offline workflow regression validation: [run 41247674443](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41247674443), **18 passed**. The status renderer now reports the user's expiry rule, HDFC legacy sample, and weight-cache result.
- **Overall C1 remains NOT PASSED.** Bounded 50-stock samples are not continuous history. Under v1.3, the remaining C1 gates are continuous 90-day-chunk stock and NIFTY index target coverage, verified expiry/session dates, dated ISIN/security identities and corporate-action continuity. Official weights, ETF holdings and basket-to-index weight reconciliation are no longer required.
## Initial source findings (document review only)

- NIFTY 50 methodology uses free-float market-cap weights; a majority vote of stock directions is not the primary index aggregation rule.
- One-time September 2026 report sample: NIFTY50 table parsed as 50 unique constituents with displayed weights summing to 100.0%; this is schema integrity only, not permission or historical point-in-time validation.
- BKKB20/nse-index-history is a promising historical membership reconstruction candidate, but its README discloses unprocessed scanned circulars and pre-2010 mapping limitations.
- vishalvx/nifty-indices-datasets provides binary membership rather than numerical free-float weights; it cannot be used as a primary weight series.
- Dhan v2 documentation describes up to five years of intraday history for active instruments and 90-day request windows; historical inactive constituents remain unverified.
- Parent repo's latest index-only run 41145607225 (2026-10-30) reports 398 weekly labels, 318 development and 80 holdout rows, but the anchor remains provisional and no executable strategy is certified. This is benchmark context only.

## Gate decision

No model training until point-in-time membership, numeric free-float weights, security mappings, corporate actions, stock anchor/close coverage and basket-to-index reconstruction all pass C1. If these inputs cannot be sourced reliably, stop at C1 and publish the exact data limitation rather than fabricate approximations.


## C0 acceptance evidence

- Automated Actions commit: [746d1b3](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/commit/746d1b382e338e760b1cf4b3ee5ea6fa6b63bc85).
- Validation artifact: C0_VALIDATION_REPORT.md — PASS.
- Scope: structural governance validation and the BUP-01 plan regression tests only.
- C1 remains IN PROGRESS / RIGHTS-BLOCKED: the one-time September 2026 CSV passed only a structural check; no licensed historic weights, certified membership history, constituent stock data or basket reconstruction has passed empirical validation.


## Historical C1 source-audit work started (pre-v1.3; superseded)

- Official report discovery: identified the NSE Indices monthly weightage ZIP families and the corresponding NSE India all-reports category.
- Automated retrieval: initial one-time Actions test downloaded a sample before terms review. All subsequent remote retrieval and raw artifact uploads have been disabled; the workflow now inspects only separately authorised local archives.
- Third-party data: the HF historical weight dataset is restricted to CC-BY-NC-SA non-commercial use and documents extrapolation/static-between-snapshot assumptions; not accepted as primary weights.
- Membership: the public circular reconstruction is only a candidate. Ticker-only aliases can collapse distinct predecessor/successor securities; ISIN and effective-date reconstruction is required.
- NSE Indices Terms of Use were reviewed; automated collection without express written consent and redistribution/copying without prior written permission are restricted. Issue #27 requests deletion of the earlier raw Actions artifact and associated cache if possible.

<!-- C1_FETCH_STATUS_START -->
## Latest automated C1 offline-source audit

- Recorded at (UTC): 2026-10-31T06:57:43.460536+00:00
- Audit status: NO_AUTHORISED_ARCHIVE
- Network collection performed: False
- This is file-integrity/schema evidence only; it is not point-in-time membership, source permission, weight validity or trading-data validation.
- C1 acceptance: NOT PASSED until licensed/authorised point-in-time weights, membership, identifiers, corporate actions, equity bar coverage and basket reconciliation pass.
<!-- C1_FETCH_STATUS_END -->

## Historical C1 decision update — 2026-10-31 (pre-v1.3; superseded)

- Technical sample result: September 2026 NIFTY50 CSV has a title preamble, table header at row index 2, 50 unique symbol rows and displayed weight total 100.0%. No individual symbol/weight values are reproduced.
- A third-party current-members CSV (project README dates it March 2026) differs from the September sample by one name each: candidate-only WIPRO, report-only BSE. Treat it as stale/date-mismatched, not ground truth.
- The official October report archive includes a NIFTY50 PDF; it has not been analysed.
- Rights correction: remote NSE scraping and raw archive artifact publication have been disabled. C1 workflow is now offline-only for separately authorised input files.
- Cleanup issue: [#27 remove the prior raw NSE sample artifact/cache](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/issues/27).
- The existing Dhan auth path and data pipeline are under audit. Prior parent logs report inconsistent TOTP renewal and a separate options DH-905 error; no stock-equity API call has yet been verified.
- C1 is NOT PASSED. No panel, feature table, stock prediction or trading result exists.


## Workflow validation record — 2026-10-31

- Initial one-time source retrieval workflow run 41177903446 completed successfully before the data-rights restriction was discovered. Its raw output artifact is under cleanup issue #27.
- Offline workflow run 41178553686 (run #28) failed during checkout because a literal backslash was prepended to the GitHub branch-ref expression. The test and inspection steps were skipped. The expression was corrected in commit 0b430118c003e2f626b70097756e641fea55067c.
- Subsequent run 41178676032 (run #35) is reported as action_required and exposes no job steps. It has not demonstrated a test pass. The workflow was then changed to read-only permissions and no longer uploads artifacts or commits data.
- Current workflow revision: a2dd17c865250a068ffb60ee94d3cc4fe19bbcd0. The read-only test has not yet been observed executing successfully.

**Validation status:** C0 PASS. C1 offline workflow tests are NOT YET VERIFIED by GitHub Actions. C1 data gate remains RIGHTS-BLOCKED / IN PROGRESS. No model or constituent forecast exists.


## Licensed open-source data candidate — audit completed 2026-10-31

- CC BY 4.0 NIFTY50 membership subset cached at `data/derived/constituent_weekly/nifty50_membership_intervals.csv`, with attribution file `C1_MEMBERSHIP_DATA_ATTRIBUTION.md`.
- Membership audit: 83 intervals, 82 symbols; 50 snapshot_floor / 33 press_release; all 93 month-15 cardinality checks from 2018-01 to 2025-09 returned 50 active intervals. Latest event 2025-09-30. No numeric weights.
- Shareholding dataset audit: 2,584 records / 78 NIFTY50-related tickers in all years; quarterly coverage 37/50 in 2018-03, 47/50 in 2018-06, 41/50 in 2020-06, 43/50 in 2022-03, 49/50 in 2023-06, and 50/50 from 2023-09 through 2025-09.
- Ownership records are not official IWF. Roll-ups lack detailed strategic exclusions; `100%-promoter` is rejected as an IWF calculation. Filing-index manifests contain broadcast timestamps, which must be joined by XBRL filename before causal feature use.
- AMFI ETF portfolio data are not used because its Terms of Use restrict public redistribution/derivative works and storage without permission.
- C1 stays BLOCKED: no point-in-time numerical free-float weights, no NIFTY50 membership update after 2025-09-30 in this candidate, and no Dhan stock intraday coverage result yet.


## C1 automation / workflow validation update — 2026-10-31

- Offline authorised-source workflow run [41180457400](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41180457400) completed **SUCCESS**. Checkout, offline source-audit tests, local archive inspection, status update and job-summary publication all passed.
- This is only code/structure and offline archive validation. No separately authorised archive was present in the runner; the result remains `NO_AUTHORISED_ARCHIVE`. The earlier one-time September 2026 sample is documented separately and does not provide historical weekly IWF.
- Dhan equity preflight script, response-validation tests and a separate manual/read-only same-repository PR workflow are now committed. The workflow uses the existing POST-based `live_api.app.refresh_dhan_token()` function and never writes raw bars or tokens.
- No Actions run for the Dhan equity preflight is visible as of this status update. Therefore no Dhan profile, equity security-ID resolution, 2018 daily history or 1-minute stock-bar request has passed yet.
- Shared scheduled Dhan token script defect is separately staged in [PR #28](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/pull/28): GET was corrected to POST. That PR's mocked Actions check also has no visible run yet.
- Current C1 workflow source revisions: offline audit workflow has read-only permissions; Dhan preflight workflow is read-only and only runs for same-repository C1 PRs/push/manual runs. No raw report scraping or artifact upload is configured.

**Phase decision:** C0 PASS. C1 offline workflow PASS. C1 market-data/weights gate remains BLOCKED. Do not create C2 panel or fit stock models until numeric point-in-time free-float weights, the post-2025-09-30 current membership, security identity/corporate actions, and constituent 1-minute price coverage are validated.

<!-- C1_DHAN_STATUS_START -->
## Latest Dhan equity preflight

- Recorded at (UTC): 2026-11-01T02:56:45.119214+00:00
- Dhan auth method/status: totp_refresh / SUCCESS
- Profile HTTP status: NOT_RECORDED
- Status: PASS_ACTIVE_EQUITIES
- Last successful Dhan preflight: PASS_ACTIVE_EQUITIES at 2026-11-01T02:56:45.119214+00:00; preserved separately from latest attempt.
- Data plan active: True
- Current NIFTY 50 universe resolved in current Dhan master: 50/50
- Historical membership symbol aliases matched in current Dhan master: 79/84
- Five-symbol one-minute anchor/expiry-proxy checks: 10/10
- Full point-in-time NIFTY 50 probe: 50/50 passed; resolved 50; date 2026-10-29
- 90-day Dhan one-minute range: 3/3 symbols passed; date range [('2022-10-03', '2022-12-30')]; standard-session counts [61]; non-standard session dates ['2022-10-24']
- Full-universe 90-day Dhan range: 50/50 passed; security IDs 50/50; dates {'from': '2026-06-29', 'to': '2026-09-26'}
- Historical 2022 point-in-time 90-day range: 50/50 passed; security IDs 50/50; dates {'from': '2022-10-03', 'to': '2022-12-30'}
- Five-year edge 2021 90-day range: 50/50 passed; security IDs 50/50; dates {'from': '2021-11-01', 'to': '2022-01-29'}
- Accepted expiry proxy: last returned one-minute candle at/before 15:15:00 IST; sample proxy timestamp(s): 2022-10-31T15:14:00+05:30, 2026-10-29T15:14:00+05:30
- Historic HDFC Ltd legacy-security-ID probes: 2/2 passed
- Deep daily-history probe: PASS
- Historical-weight candidate cache: CACHE_VALIDATED; 216 rows, 100 ticker columns, 2008-01-31 to 2025-08-31
- Weight candidate licence: CC BY-NC-SA 4.0; commercial use permitted: False
- The one-day 50-stock probe and three-symbol 90-day batch probe are not a complete five-year point-in-time constituent panel.
- Raw bars, prices, security IDs, credentials and tokens are not stored in this report.
- C1 remains gated by official/authorised point-in-time weights, the 2025-09 onward weight gap, full historical security identity and coverage, and index-basket reconciliation.
<!-- C1_DHAN_STATUS_END -->

## C1 resume checkpoint — 2026-10-31

- Offline authorised-source audit workflow [41181684637](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41181684637): SUCCESS; checkout, offline tests, local archive inventory and summary publication all passed. Result remains NO_AUTHORISED_ARCHIVE.
- Dhan equity preflight workflow [41181684573](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41181684573): workflow SUCCESS, offline tests 9/9 PASS, but live profile check returned HTTP 401. No equity price coverage was tested.
- Shared token refresh PR [#28](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/pull/28): mocked regression and Actions integration checks both SUCCESS. PR #28 has passing checks and was marked ready for review, but GitHub reports a merge conflict (`mergeable_state=dirty`); it remains open/unmerged. The main scheduled helper is not yet fixed.
- Open data candidate audit: CC BY 4.0 project ledger now has 86 NIFTY 50 intervals/85 symbols after 2026 WIPRO-to-BSE and Tata Motors demerger corrections. The corrected April 2018–October 2026 month-end test expects 50 entries on 102 dates and 51 on 2025-10-31 due the official zero-price DUMMYTATAM placeholder. There are no numeric weights; quarterly ownership disclosures are not official IWF.
- C1 remains BLOCKED. C2 panel construction and model training remain prohibited until rights, point-in-time official/free-float weights, current membership, ISIN/security identity, corporate actions, Dhan profile/data entitlement, historical equity bars and weighted basket reconciliation all pass.


## Dhan API documentation reconciliation — 2026-10-31

- Dhan v2 documentation specifies POST to `/app/generateAccessToken` with `dhanClientId`, `pin`, and `totp`; tokens are valid for 24 hours. The profile endpoint example sends only the `access-token` header and returns token validity plus `dataPlan` status. Data APIs require a separately subscribed plan. Source: https://dhanhq.co/docs/v2/authentication/.
- The preflight now tests the profile endpoint with only the documented access-token header, while retaining client-id for subsequent market-data requests. Regression tests pass 10/10. The latest live run still receives HTTP 200 without an accessToken from token generation and HTTP 401 from profile; account secret validation is now the blocking dependency.


## 2026-10-31 — Dhan authentication retry after shared-helper correction

- Corrected `scripts/refresh_dhan_token.py` on the C1 branch to use POST with query parameters, reject line breaks, mask the ephemeral token and export only through `GITHUB_ENV`. Added mocked regression tests and wired the helper/test paths into the C1 Dhan workflow.
- The BUP-01 preflight already used POST; its request shape was retained. This avoids conflating the shared-helper defect with the independent live-account authentication failure.
- Actions run [41182555655](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41182555655): all steps passed, including 10/10 offline tests. Live token endpoint returned HTTP 200 but only `message` and `status` keys; no access token was returned. The fallback profile request returned HTTP 401. No security master, daily bars or intraday bars were queried.
- Added safe provider-error categorisation (category only; no provider message text) and a regression test. A subsequent run is pending/in progress at the time of this log update; its result must be checked before closing this diagnostic.
- C1 remains BLOCKED. The token endpoint's HTTP 200 is not authentication success. Do not infer the token secret values or expose them. Next gate is to classify Dhan's authentication response safely, then request user-owned secret correction only if the provider confirms an invalid/mismatched credential.

## C1 source/rights audit update — 2026-10-31

- Official NIFTY methodology confirms free-float index capitalisation uses shares outstanding × IWF × capping factor × price; the IWF process excludes a broader set of strategic holdings than promoter/public/FII/DII roll-ups. Quarterly ownership data is not a substitute for official IWF.
- NSE website Terms of Use expressly restrict systematic/automated collection and restrict copying/storage/redistribution and virtual-trading/simulation use without permission. The project therefore keeps remote NSE scraping and raw report caching disabled pending an applicable written licence/permission determination.
- Dhan v2 documents five-year intraday coverage only for active instruments and a maximum 90-day request window. This does not establish coverage for delisted/inactive historic constituents. The successful five-symbol historical probe is a limited sample, not universe-wide evidence.
- No additional TOTP attempt was made. Existing 2026-10-30 close-window gap and 2026-10-29 inconclusive auth retry remain unchanged.
- **Decision:** C1 remains BLOCKED / RIGHTS-DEPENDENT. C2 remains prohibited. Next permitted work: review the exact Dhan subscription terms/covered inactive instruments and identify a licensed or explicitly authorised historical constituent-weight source; do not scrape NSE pages or ingest non-commercial weights into a trading workflow.

## C1 membership sub-gate — 2026-10-31

**MEMBERSHIP PASS WITH LIMITATIONS**

- Added the NIFTY 50-only CC BY 4.0 point-in-time membership subset at `data/constituent_weekly/nifty50_membership_intervals.csv`, with attribution/provenance in [MEMBERSHIP_DATA_PROVENANCE.md](MEMBERSHIP_DATA_PROVENANCE.md).
- Upstream data has 83 NIFTY 50 intervals, with no weights, and last reconstitution at 2025-09-30. The project snapshot adds the official 2026-09-30 one-for-one change WIPRO → BSE using the 2026-08-10 NSE Indices press release.
- Corrected regression/cardinality check: 103/103 month-end dates from 2018-04-30 through 2026-10-31 match expected counts: 102 dates have 50 entries and 2025-10-31 has 51 because DUMMYTATAM was temporarily included at zero price. This tests cardinality, not every member transition independently; pre-2018 data remains excluded from confirmatory modelling due known source drift.
- Added [machine-readable audit](C1_MEMBERSHIP_AUDIT.json) and `tests/test_bup01_membership_intervals.py`.

**Overall C1 remains BLOCKED.** The membership sub-gate is improved, but the dataset has no numerical free-float weights, ISIN/security-id history or corporate-action mapping. Dhan constituent-bar coverage still lacks a full-universe test and recent expiry-close completion. No C2 panel/model is permitted.

**Best official exact-weight route identified:** NSE Indices data subscription includes historical constituent identifiers, market caps, weights and prices; licensing enquiry: `indices@nse.co.in`. Free alternatives reviewed are insufficient or carry upstream/non-commercial restrictions. Automated NSE web scraping remains disabled.

## C1 membership identity correction — 2026-10-31

A second corporate-action audit refined the membership ledger. The upstream file's `TMPV` symbol was incorrectly carried backwards into dates before the NSE symbol change. It is now corrected to `TATAMOTORS` through 2025-10-23 and `TMPV` from 2025-10-24, as per NSE circular NSE/FAOP/70882.

The ledger also now captures the temporary `DUMMYTATAM` zero-price placeholder from 2025-10-14 through 2025-11-16, explicitly flagged `market_data_required=FALSE`. Thus the corrected 103 month-end snapshots contain 50 unique entries on 102 dates and 51 entries on 2025-10-31. The earlier all-50 count is superseded. The placeholder is for index-ledger completeness only; it is never a stock prediction input.

The revised six-test suite and machine audit are committed. **Post-correction Actions validation passed:** run [41185169548](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41185169548), 6 tests passed. Overall C1 remains BLOCKED on exact licensed IWF, ISIN/security identity history, other corporate actions and constituent price coverage; no C2 panel/model may be built yet.

## Membership CI acceptance — 2026-10-31

- Corrected membership integrity workflow [41185169548](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41185169548): **SUCCESS; 6 tests passed**.
- The passing suite checks half-open effective-date intervals, the 2025-10-24 TATAMOTORS/TMPV symbol transition, DUMMYTATAM zero-price placeholder inclusion/removal and its non-tradable flag, corrected 103 month-end cardinality (102×50, 1×51), no fabricated index weights, and machine-audit consistency.
- This passes the membership-file integrity sub-gate only. It does not certify every upstream membership event, official IWF, ISIN mapping, corporate actions other than those explicitly patched, stock OHLCV coverage or basket/index reconstruction.


## Recovery continuation — bounded public-source audit (2026-10-31)

- Verified the membership Actions run 41185169548 as SUCCESS (six tests passed); corrected stale log wording on main.
- Rechecked official NSE Indices data subscription, NSE free-float methodology page, Dhan v2 historical-data documentation, a CC BY-NC-SA Hugging Face weights dataset and a GitHub approximate-weight dataset.
- The official exact-weight/identifier data route is licensed/subscription. The Hugging Face dataset is non-commercial; the GitHub dataset explicitly uses equal-weighted/binary approximations. Dhan documents five-year minute history for active instruments and 90-day request windows, not guaranteed inactive/delisted history.
- No source found in this bounded pass clears rights + exact historical IWF + security/corporate-action identity + full constituent intraday/expiry-close coverage together.
- **Gate decision unchanged:** membership sub-gate PASS WITH LIMITATIONS; overall C1 BLOCKED; C2 not authorised. Do not fabricate weights, scrape NSE without permission, or fit stock models on an incomplete universe.
- References: https://www.nseindia.com/static/nse-indices/index-data-subscription ; https://www.nseindia.com/static/products-services/indices-nifty50-index ; https://dhanhq.co/docs/v2/historical-data/ ; https://huggingface.co/datasets/AMP4010/Historical_Nifty_50_Constituent_Weights_20Y ; https://github.com/vishalvx/nifty-indices-datasets.


## User data-source direction — 2026-10-31

User confirmed “Dhan” as the available data route. Treat the existing Dhan Data API subscription and GitHub Actions secrets as the primary permitted market-data source for constituent prices. Next C1 data work must use Dhan-first, cache-first acquisition: resolve the point-in-time constituent universe to Dhan security IDs, inventory historical daily/intraday coverage by symbol and date, test delisted/inactive coverage, and capture both forecast-time anchors and expiry-close bars. Reuse cached successful responses; make bounded date/security batches; serialize authentication and avoid unnecessary TOTP refresh loops. Never expose secrets or raw credentials.

Dhan price data does not itself establish official historical NIFTY free-float IWF or index methodology membership. Keep those as separate gates and do not infer weights from equal weights, market cap, or promoter/FII/DII ownership. Overall C1 remains BLOCKED until weights/identity and full price coverage are verified. C2 remains gated.

## Full-universe Dhan scrip-master audit — 2026-10-31

- Extended the C1 preflight to read the licensed point-in-time membership ledger and construct (a) the 2026-10-31 active tradable NIFTY 50 symbol set and (b) the distinct historical tradable symbol/alias set. The zero-price DUMMYTATAM placeholder is excluded from both tradable sets.
- The preflight now resolves both sets against the current Dhan scrip master, recording counts and unresolved symbol names only; security IDs and raw data are never written. The report explicitly warns that a current-master match does not prove historical security-ID validity for an inactive/delisted instrument.
- Five-symbol price probes remain separately bounded; no bulk 50-stock candle download was initiated by this code change.
- PR validation run [41223379333](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41223379333): SUCCESS; 13 offline tests passed. The live Dhan step was intentionally skipped because this was a pull-request event; workflow guard prevents exposing credentials to PR code.
- Live data status unchanged: latest successful live Dhan evidence remains the five-symbol partial preflight [41182679514](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41182679514). Full-universe security-ID resolution has not yet been run. Use the workflow's manual workflow_dispatch on the C1 branch for the live secret-backed step.
- C1 remains BLOCKED; C2 remains gated. No constituent panel/model/forecast or strategy is claimed.


## Live Dhan full-universe result — 2026-10-31

Protected Actions run [41224048773](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41224048773) completed successfully. The Dhan TOTP refresh returned an access token, profile authentication succeeded, and the Data API plan was active.

- Current active NIFTY 50: **50/50** symbols resolved against the current Dhan scrip master.
- Historical tradable membership ledger: **79/84** distinct symbols/aliases found in the current scrip master. Five absent from the current master: HDFC, JPASSOCIAT, MCDOWELL-N, RANBAXY, TATAMOTORS. These require dated corporate-action/successor/security-ID mapping; absence from today's master does not prove historical data unavailable.
- Five-stock candle sample: daily history returned 22 bars for Jan 2018. All five stocks passed the 2022-10-31 one-minute probe (374 bars each, including 10:00 anchor and 15:25–15:29 expiry close).
- Recent sample 2026-10-29: 359 bars per stock, valid 10:00 anchor, but feed stopped at 15:14 IST; expiry-close window missing for all five. Targeted 15:20–15:30 requests returned empty arrays (**0/5**).
- No raw price bars, security IDs or credentials were committed. Sanitized output is in [C1_DHAN_PREFLIGHT.json](C1_DHAN_PREFLIGHT.json).
- C1 remains BLOCKED: historical security mapping for five aliases, recent close-bar coverage, full constituent OHLCV history, official numerical IWF/weights and basket reconciliation remain open. C2 is not authorised.


## Public minute-data source audit — 2026-11-01

- Updated pre-registered plan to v1.1 to apply the user-approved 15:15 expiry proxy consistently to both constituent and NIFTY index outcomes; 15:30 official close is a separate sensitivity only.
- Discovered historical public minute archive gsidhu/nse-intraday-data: 47/50 point-in-time NIFTY 50 member files on both 2022-11-03 and 2022-11-04. Missing: DIVISLAB, SBILIFE, APOLLOHOSP. Five sample stocks plus NIFTY had 10:00–10:03 anchor rows and 15:14 bars on 2022-11-03.
- The archive README claims MIT but neither the fork nor upstream root had a LICENSE file. It is diagnostic only; no bars were imported. Another 2024–2026 stock dataset is limited to research/education and excludes commercial redistribution; a large HF candidate has no verified licence; DataPointX downloads are not open yet.
- Dhan docs confirm five years of minute history for active instruments and 90-day query chunks, but no guarantee for inactive/delisted instruments. Daily history extends to instrument inception.
- **C1 remains NOT PASSED / RIGHTS + COVERAGE BLOCKED.** We do not have licensed full-universe 1-minute history, point-in-time official weights or 98% basket coverage. C2 remains gated.
- Details: [C1_PUBLIC_INTRADAY_SOURCE_AUDIT.md](C1_PUBLIC_INTRADAY_SOURCE_AUDIT.md).


## Workflow mistake and correction — 2026-11-01

- Push run [41249370561](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41249370561) failed at `validate_plan.py` because its registration check hard-coded plan version 1.0 after the user-approved plan amendment to v1.1.
- This was a validator defect, not a research-data failure. The separate C1 authorised-source audit passed in run [41249370606](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41249370606).
- Corrective change: validator now parses the declared plan version, requires the same version in the version history, and verifies the 15:15-proxy definition and separate 15:30 sensitivity. A regression test covers the v1.1 amendment.
- Re-run status will be added after the next Actions result is observed. C1 remains NOT PASSED; C2 stays gated.


## Second CI correction — 2026-11-01

- Retry run [41249450033](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41249450033) exposed an escaping error in the first regex-based fix to `validate_plan.py`; the plan-version expression did not match the Markdown marker.
- Replaced regex parsing with direct extraction and numeric validation of the `**Plan version:**` line. The existing v1.1 regression test covers the version-history and expiry-proxy markers.
- No market data, labels or models were modified. A new workflow run is required to confirm the correction.


## CI validation closure — 2026-11-01

- Plan validator correction is confirmed by push run [41249521876](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41249521876): C0 plan structure passed and all 4 governance tests passed. The C1 offline source-audit push run [41249642494](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41249642494) also passed. E0037 and E0038 are resolved.
- Protected Dhan run [41249642409](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41249642409) succeeded with **50/50** point-in-time current-universe security IDs resolved and **50/50** one-minute data QA checks passing for 2026-10-29. Each passing sample had four 10:00–10:03 bars, one 15:14 expiry-proxy bar, 359 bars for the session and OHLCV invariants passing. This is a one-session coverage probe only, not full historical data or an expiry-return panel.
- New public source candidates: HF original dataset declares MIT but source feed provenance is unverified and its README limits intended use to research/education/backtesting; it is not admitted. NSE Indices March 2026 whitepaper Exhibit 26 gives a full 50-name 2026-02-27 weight snapshot; 2dp rounded weights sum to 100.02%, preserved as published in a separate reference CSV. It does not close the historical monthly/daily weight gap.
- C1 remains **NOT PASSED**: full historical point-in-time minute panel, official time-series weights, corporate-action security mapping and reconstructed-index tolerance remain outstanding. C2/model training remains gated.


## Official monthly archive permission gate — 2026-11-01

- Official monthly "Market Capitalisation, Weightage, Beta" ZIP family identified; independent documentation reports 159 monthly files from June 2013 onward and a public code example documents the `mcwb_{mon}{yy}.zip` filename pattern.
- NSE research-data policy lists historical reports/index data for research/analysis, but Nifty Indices Terms separately restrict automated collection without express written consent. The permissions interaction for recurring retrieval and caching is unresolved.
- No archive ZIP was fetched or parsed. Automated retrieval remains disabled until written permission or a suitable licence is confirmed.
- See [C1_OFFICIAL_WEIGHTAGE_ARCHIVE_TERMS_AUDIT.md](C1_OFFICIAL_WEIGHTAGE_ARCHIVE_TERMS_AUDIT.md). C1 NOT PASSED; C2 gated.



## Full-universe 90-day Dhan range validation — 2026-11-01

- **PASS:** Dhan fresh TOTP authentication succeeded; all 23 offline tests passed in run [41251346795](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41251346795).
- Full point-in-time NIFTY 50 cross-section for 2026-06-29 through 2026-09-26: **50/50 security IDs resolved and 50/50 symbols passed**.
- Each symbol returned 23,414 one-minute bars across 64 regular sessions; 64/64 anchor sessions and 64/64 expiry-proxy sessions; zero missing anchors/expiry bars, zero duplicate timestamps, all OHLCV invariants passed. Aggregate total = 1,170,700 one-minute rows.
- Raw market bars/prices were not committed; only sanitized QA metadata are in `C1_DHAN_PREFLIGHT.json` and `C1_DHAN_LAST_SUCCESS.json`.
- Earlier TOTP response anomaly (E0042) resolved on the successful retry run. Double-escaped fallback newline guard (E0043) corrected; 23 tests pass. Special-session logic (E0041) confirmed in 3-stock 90-day range test.
- Full results: [C1_DHAN_90D_RANGE_VALIDATION.md](C1_DHAN_90D_RANGE_VALIDATION.md).
- **C1 remains NOT PASSED.** The sample is one quarter only. Five-year point-in-time histories, legacy/inactive identities, minute-bar corporate-action treatment, official historical free-float weights and basket-to-index reconstruction remain open; C2 remains gated.


## Historical 2022 point-in-time universe — PASS (2026-11-01)

- Workflow [41251808946](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41251808946) passed all 24 offline tests and Dhan live preflight.
- 2022-10-03–2022-12-30 point-in-time NIFTY 50 basket: 50/50 symbols and security IDs passed.
- Each constituent had 61/61 regular sessions with 10:00–10:03 anchor and 15:00–15:14 expiry-proxy availability; zero missing sessions, zero duplicate timestamps, all OHLCV invariants pass. Aggregate 1,146,180 bars represented by per-symbol counts.
- Legacy mappings used only for the 2022 period: HDFC Ltd ID 1330; TATAMOTORS symbol mapped to TMPV security ID. No price series was stitched over the 2025 demerger.
- Combined full-basket 90-day coverage windows now pass for 2022Q4 (historic) and 2026Q3 (recent). This is not a continuous five-year backfill.
- Details: [C1_DHAN_HISTORICAL_2022_90D_VALIDATION.md](C1_DHAN_HISTORICAL_2022_90D_VALIDATION.md).
- **C1 remains NOT PASSED**: continuous 2021–2026 coverage, earlier inactive IDs, corporate-action minute treatment, authorised official weight time series and basket-to-index reconstruction remain outstanding. C2 remains gated.


## Five-year edge data-quality investigation — 2026-11-01

- First live 2021-11-01–2022-01-29 check resolved all 50 security IDs and returned 1,233,597 bars, but strict QA failed for 50/50 due one common missing anchor and OHLCV invariant flags on 48 symbols.
- Investigation found the range checker included post-market rows through 15:59 in OHLCV invariants and did not explicitly exclude the NSE evening-only Muhurat date 2021-11-04.
- NSE circular NSE/CMTR/50050 dated 2021-10-21 sets the 2021-11-04 normal Muhurat session at 18:15–19:15. This date is not a standard daytime 10:00/15:15 expiry session.
- Corrective code now excludes 2021-11-04 and 2022-10-24 from standard-session coverage, validates OHLCV only within 09:15–15:30, and records missing-session dates plus invalid-row counts. Regression tests added.
- Corrected validation run: [push 41252703953](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41252703953); final metrics pending.
- C1 remains NOT PASSED until corrected edge QA and all other data rights / weights / reconstruction gates are resolved.


## Verified continuation checkpoint — 2026-11-01

- Referenced protected Actions run [41263593605](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41263593605) completed its GitHub job, and its offline C1 test step passed **26/26**. The live Dhan sub-check did **not** pass: token generation returned HTTP 200 twice without an `accessToken`, the sanitized provider classification was `TOTP_REJECTED_OR_INVALID`, and the stored-token fallback received profile HTTP 401. No live scrip-master or equity candle requests were made in this run. The machine status remains `BLOCKED_PROFILE_HTTP_401`; the workflow's previous green conclusion was not a data-gate pass.
- Last successful live evidence remains separately preserved: the one-session current universe passed 50/50 (run [41249642409](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41249642409)); the 50-stock 2026-06-29–2026-09-26 quarter passed 50/50 (run [41251346795](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41251346795)); and the 50-stock 2022-10-03–2022-12-30 quarter passed 50/50 (run [41251808946](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41251808946)). These are separated sample windows, not continuous five-year coverage.
- Five-year edge run [41252703953](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41252703953) stopped before the live data step because one offline assertion expected one post-market row but the metric counted two rows (the Muhurat special-session row plus the post-market row). The implementation was corrected to count special-session exclusions and post-market rows separately; run 41263593605 passed the revised 26-test suite. **The 2021 five-year-edge data request itself remains untested** because the live authentication step was blocked.
- The cached 216-month weight candidate remains non-commercial CC BY-NC-SA 4.0, includes estimated/extrapolated event weights, and ends 2025-08-31. It is not admitted as official point-in-time IWF for an index reconstruction or trading workflow. Automated NSE collection remains disabled pending written permission/licensing.
- C1 remains **NOT PASSED / RIGHTS + DATA BLOCKED**. C2–C6 remain gated. No constituent panel, stock model, bottom-up NIFTY forecast or executable strategy exists. Do not use a majority vote, equal weights, or the non-commercial candidate as a substitute for official weights.
- Workflow correction: a post-diagnostics gate now checks the sanitized live preflight status after its report has been committed. A live run with a blocked/partial status will return a failed Actions conclusion instead of appearing green merely because the preflight script recorded the blocker and exited normally. Pull-request runs remain offline-only.

## Resume checkpoint — 2026-11-01 (after run 41263593605)

- Offline validator correction: **26/26 tests passed** in [run 41263593605](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41263593605). This closes the Muhurat/post-market counter regression only.
- Live Dhan result from the same run: **BLOCKED_PROFILE_HTTP_401**. Token generation returned HTTP 200 but no access-token field on two bounded attempts; sanitized diagnostics classified the response as `TOTP_REJECTED_OR_INVALID`. The configured fallback token then failed the profile endpoint with HTTP 401. No scrip-master or equity-history request ran.
- The Actions job was marked SUCCESS because the executed job did not include the subsequently added final status-enforcement step. The current workflow source now has that fail-closed step after the diagnostics commit; its runtime behavior has not yet been observed on a later run.
- Preserved prior evidence: 50/50 current constituents on a one-session check; 50/50 for 2026-06-29–2026-09-26; and 50/50 for 2022-10-03–2022-12-30. These are separated sample windows, not continuous five-year coverage.
- The corrected 2021-11-01–2022-01-29 full-universe edge request did **not** execute because the earlier test failure stopped the Dhan step; the subsequent run was blocked at authentication. It remains unverified.
- No C2 panel, stock model, weighted index forecast, or trading strategy is authorised. C1 remains **NOT PASSED** pending Dhan access, licensed/authorised point-in-time weights, identity/corporate-action coverage and basket reconstruction.
- Next action: correct the organization Dhan authentication secrets (verify client ID, six-digit PIN, and TOTP setup/seed) or configure the documented API-key/secret OAuth credentials. Do not loop token retries or use the expired fallback token.


## Dhan authentication hardening — 2026-11-01

- Merged PR [#29](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/pull/29), commit `cb7d304831f039bb994d819d5570a71f2bec0116`.
- Shared authentication helper now accepts either a raw Base32 TOTP seed or a standard `otpauth://totp/` provisioning URI. Whitespace around a raw seed is normalized conservatively; other unrecognized formats fail closed.
- Added a sanitized comparison of the Dhan HTTP `Date` header against runner UTC time. Only the integer clock difference is retained; no seed, OTP, token, PIN or provider response values are logged.
- Added offline regression tests for raw/URI equivalence, invalid HOTP/empty values and positive/negative clock offsets. The Dhan workflow now triggers when the shared helper or its tests change.
- Post-merge C1 source-audit and research workflows: [run 41266155292](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266155292) and [run 41266155248](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266155248) completed successfully.
- Protected Dhan preflight [run 41266155250](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266155250) was still installing dependencies at the last observation; offline tests, clock diagnostic and live authentication result are therefore pending. No new data coverage is claimed yet.
- Overall C1 remains **NOT PASSED / RIGHTS + DATA BLOCKED**; C2 remains gated. This code change diagnoses authentication; it does not establish that the previous secret configuration was incorrect.


## Protected Dhan preflight — authentication recovered; edge QA partial (2026-11-01)

- Protected live run [41266155250](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266155250) used the updated TOTP helper and succeeded on the first token request. Dhan returned an access-token response over HTTP 200; the API profile reported an active Data API plan. Dhan HTTP Date vs GitHub runner UTC difference was **0 seconds**. This resolves the current authentication blocker operationally; the precise reason for the previous failure is not established.
- Point-in-time current NIFTY 50 security master: **50/50**. Historical membership ledger aliases found in current scrip master: **79/84**; five absent from the current master remain a historical-identity review item, not proof that their older data cannot exist.
- Full current basket one-session 2026-10-29 probe: **50/50** with 10:00–10:03 anchors and 15:14 expiry-proxy candles.
- Three-stock 2022Q4 range probe: **3/3**. Full 50-stock range probes: **50/50** for 2026-06-29–2026-09-26 and **50/50** for 2022-10-03–2022-12-30.
- Five-year-edge 2021-11-01–2022-01-29 range: **49/50** full OHLCV passes. All 50 security IDs resolved; all 50 had 61/61 sessions, 61/61 anchor sessions and 61/61 expiry-proxy sessions. SHREECEM had one finite negative-volume row; no missing anchor/proxy sessions, duplicate timestamps, invalid numeric rows or OHLC violations. A separate one-symbol diagnostic is running to locate that row by timestamp without saving values.
- Reliance daily history probe: **22 bars** for 2018-01; this is only a one-stock daily-history existence test, not a daily 50-name panel.
- The live job's final fail-closed gate executed after committing its sanitized report and correctly returned failure because overall result was `PARTIAL_OR_BLOCKED`. This is not an authentication failure.
- **C1 remains NOT PASSED.** In addition to closing the SHREECEM anomaly, C1 still needs a licensed/authorised point-in-time official IWF weight series and a validated weighted constituent-basket reconstruction. The cached 216-month candidate remains non-commercial, contains estimated/extrapolated events and ends 2025-08; it cannot be used for commercial trading validation. No C2 model/forecast or strategy is authorised.


## Superseding C1 checkpoint — Dhan price QA passes bounded windows; IWF rights unresolved (2026-11-01)

- Protected Dhan run [41266897788](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266897788) completed **SUCCESS**, including the post-commit fail-closed gate. Machine status: `PASS_ACTIVE_EQUITIES`.
- Fresh TOTP token generated on attempt 1; profile confirmed active Data API. Dhan HTTP Date minus runner UTC was **-1 second** (HTTP Date is second-resolution; no material clock offset observed).
- Current NIFTY 50 security-master IDs: **50/50**. Historical member aliases found in today's master: **79/84**. Absence from today's master is not treated as proof that historic data is unavailable.
- Dhan 1-minute QA: current session **50/50** for 2026-10-29; full 50-stock 90-day sample **50/50** for 2026-06-29–2026-09-26; full 50-stock 90-day sample **50/50** for 2022-10-03–2022-12-30; full 50-stock 90-day edge sample **50/50** for 2021-11-01–2022-01-29. All 61 sessions in the edge window had an anchor and a 15:00–15:14 expiry-proxy observation. These are three separated 90-day windows plus one day, not a continuous five-year backfill.
- SHREECEM's anomalous negative-volume bar was timestamped 2021-12-30 15:29 IST, outside the pre-registered 15:15 target cutoff. The checker now applies strict OHLCV invariants only to 09:15–15:14 and records later bars/anomalies separately. The 15:29 anomaly no longer invalidates the target-scope panel; an equivalent negative volume at 15:14 remains a failure.
- Offline regression suite [41266922851](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266922851): **43 passed**. The separate five-symbol/range checks and final gate behaviour are verified.
- Historical NIFTY weights remain blocked. A detailed 62,850-filing / ~70-category XBRL candidate is under licence-scope and IWF-category-mapping review; the nested `_categories.csv.gz` path is not unambiguously covered by the repository's explicit licence globs. No rows were imported. The official IWF guideline has 22 exclusion categories; several require relationship/agreement data beyond aggregate categories.
- TejHQ daily EOD/corporate-action/symbol-history data is documented as usable for personal research/backtesting and private storage, but not raw redistribution; public-repository or public Actions-cache storage is therefore disallowed. It is a secondary daily cross-check candidate only—not intraday data, official NIFTY membership, or IWF.
- **Overall C1 remains NOT PASSED / RIGHTS-BLOCKED.** No stock panel, model, bottom-up forecast, index aggregation, or strategy has been built. C2–C6 remain gated by the locked plan until point-in-time IWF rights and completeness, continuous coverage, historic identity mapping and weighted basket-to-index reconciliation are demonstrated.
- Next action: obtain written permission/licence for official NSE Indices historical constituent weights and intended research/cache use, or obtain explicit path-specific licence confirmation for an admissible category dataset and validate all 22 exclusions. Do not substitute approximate weights or majority vote.


## Final bounded C1 closeout checkpoint — additional official data rights review (2026-11-01)

- Published [C1_DHAN_90D_VALIDATION_REPORT.md](C1_DHAN_90D_VALIDATION_REPORT.md) with exact counts and QA scope from protected run [41266897788](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266897788). Full 50-name probes pass in three non-contiguous 90-day windows (2021Q4/2022Q1 edge, 2022Q4, 2026Q3) plus one recent day. This is not continuous five-year coverage.
- Expanded source audit to official SEBI/NSE policy lists. Quarterly shareholding patterns appear in NSE's first-basket research data list, but NSE's Research Initiative data access explicitly limits use to academic/non-commercial work; NSE's Data Sharing & Usage Policy defines Research Activity as for purposes other than trading/profit. Its commercial subscriber route requires a relevant agreement. Do not use the academic route for this intended trading research without written confirmation.
- Identified the exact practical path: a commercial permission/agreement for official NIFTY 50 historical weights/IWF + point-in-time constituents/identifiers, covering automated retrieval, private caching, internal model training/backtesting, internal algorithmic trading use and permitted aggregate outputs.
- Added [NSE_DATA_RIGHTS_REQUEST.md](NSE_DATA_RIGHTS_REQUEST.md) as an unsent request template. It asks NSE Indices/NSE Data for the appropriate product, exact coverage, commercial-use terms, cache retention and output restrictions.
- Further alternatives exhausted: BSE historical filings portal returned 403 in web audit; public historical weight page only has official top-ten and equal-split estimated remainder; GitHub NSE EOD/constituent tracker has MIT code but no separate data licence and does not supply intraday targets or IWF. No third-party dataset met the rights + full 22-exclusion + point-in-time IWF + trading-use requirements.
- **C1 overall remains NOT PASSED / RIGHTS-BLOCKED.** Price acquisition is no longer the live blocker. No C2 panel/model/forecast or C5 strategy work should start until written official data rights/completeness and the weighted basket-to-index reconciliation gate pass. Plan v1.1 remains unchanged.


## Requested quant-toolchain evaluation — 2026-11-01

- Added [TOOLING_EVALUATION.md](TOOLING_EVALUATION.md) to map all seven requested repositories to the registered BUP-01 phases and record licences / technical limitations.
- Apache-2.0 references: QuantEvolve, TradingAgents and PySR. BSD-family: arch and tick; MAPIE declares BSD-3-Clause. AstraQuant declares a custom AGPL-3.0 + Commons Clause and additional terms, and its execution layer is OKX-specific; it is excluded from code import absent legal review and an India-market use case.
- No tool was imported or cloned in C1. The locked plan explicitly defers them until the validated panel exists: arch/PySR in bounded C3 experiments, MAPIE in C4 after sequential coverage assumptions, TradingAgents as sandboxed hypothesis review, QuantEvolve only in bounded C5 research. tick requires licensed event/tick data which is not presently available. No Binance/crypto collector is permitted in the India Dhan/NSE data pipeline.
- This is an evaluation artifact, not a change to plan v1.1. C1 overall remains NOT PASSED / RIGHTS-BLOCKED; C2–C6 remain gated.


## IWF exclusion-map and formula QA — 2026-11-01

- Added [C1_IWF_EXCLUSION_MAPPING.csv](C1_IWF_EXCLUSION_MAPPING.csv), one row per each of the 22 exclusions in the official NSE IWF guideline. It distinguishes potential XBRL category matches from exclusions requiring dated relationship, board-right, contract or beneficial-ownership evidence. This is a schema/source feasibility map, not proof that the candidate data contains or resolves those categories.
- Added [C1_IWF_MAPPING_AUDIT.md](C1_IWF_MAPPING_AUDIT.md) with the exact source denominator and de-duplication rules. The official IWF worked example uses total shares as denominator and rounds IWF to six decimals. The candidate parser's A+B+C2 shareholding percentage base is not interchangeable with that denominator. Any future reconstruction must use raw share counts, reconcile total share capital/DR treatment, and deduplicate unique holding positions across overlapping exclusions.
- Added scripts/constituent_weekly/iwf_math.py and tests/test_iwf_math.py. The helper reproduces NSE's published example at **0.608794**, rejects duplicate position IDs/invalid share counts and tests 22-item evidence dispositions and normalised free-float weights.
- The first workflow edit tracked the new test file but omitted it from the pytest command (E0049); corrected the invocation before accepting the IWF tests. Corrected run [41269516064](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41269516064) passed **50/50** including all seven new IWF tests. PR validation run [41269519499](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41269519499) also passed.
- Source audit workflow [41269430549](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41269430549) passed. No licensed historical weights/XBRL data or Dhan raw bars were downloaded/imported in this step.
- The main repository is public. Raw Dhan bars, NSE/XBRL rows, named shareholder records and private-license data must not be committed to its branches, artifacts or public Actions cache. This is an explicit data-handling restriction even though raw caching was requested as a project preference.
- **C1 remains NOT PASSED / RIGHTS-BLOCKED.** The source/rights/22-exclusion and basket reconciliation hard gate remains open. No panel, model, weighted prediction or strategy was produced. The v1.1 research plan is unchanged.


## Developer handoff — 2026-11-01

- Completed [C1_DEVELOPER_GATE_REPORT.md](C1_DEVELOPER_GATE_REPORT.md), independently summarising passed sub-gates, open source-rights/mapping/coverage gates, workflow evidence and exact next developer actions.
- Final phase disposition is **C1 PARTIAL PASS / RIGHTS-BLOCKED**. Dhan sampled data QA and the IWF arithmetic harness pass; no licensed complete IWF series or weighted basket reconciliation exists.
- BUP-01 v1.1 remains locked; C2–C6 remain gated. No model, forecast, strategy or full research manuscript is claimed.


## Public-source proxy route — 2026-11-01 (plan v1.2)

- User direction: proceed using available public web sources; an NSE permissions request is no longer a prerequisite for the separately labelled exploratory route.
- Located Nippon India ETF Nifty 50 BeES published holdings. The AMC's passive replication objective is to hold NIFTY 50 securities in the same proportions as the index. The February 2026 portfolio (28-Feb-2026 portfolio date; NAV date 27-Feb-2026) has 50 stocks and 0.08% cash.
- Compared the 50 ETF stock positions with the repo's NSE Indices 2026-02-27 official white-paper weight snapshot. After independent normalization over equity holdings: 50/50 matched; MAE 0.002214 pp; RMSE 0.003204 pp; max absolute difference 0.008967 pp; Pearson r 0.99999895. This is a one-date calibration only.
- Added [C1_ETF_PROXY_CALIBRATION.md](C1_ETF_PROXY_CALIBRATION.md), aggregate calibration metrics [CSV](../../data/constituent_weekly/etf_proxy_calibration_2026-02-27.csv), helper [weight_proxy.py](../../scripts/constituent_weekly/weight_proxy.py), and 8 unit tests.
- Added a separate point-in-time fixed-share price-drift method. It is valid only within unchanged membership/IWF/share-capital/corporate-action intervals; reset or exclude cycles around events. ETF holdings are never relabelled as official index weights or IWF.
- SEBI's passive-scheme disclosure framework changed equity passive disclosure to quarterly within 10 days after quarter end, effective 2025-03-16. This does not prove an actual publication timestamp. The proxy method uses actual publication timestamps where available; otherwise it labels period-end +15 calendar days as an imputed availability proxy and requires +10/+20 day sensitivities.
- Main limitation: only a single 50-stock calibration date has been fully cross-compared against official weights. Although a third-party source indexes 12 recent monthly AMC holdings and AMC factsheet archives exist, full historical snapshots, exact publication timestamps, historical membership/action reseeding and weighted basket-to-index reconciliation are not yet completed.
- Plan v1.2 adds this exploratory proxy path while preserving the original official-weight confirmatory track and all point-in-time, 98% coverage, 47-stock, walk-forward and transaction-cost gates.
- C1 current decision: **PARTIAL; proxy path enabled for bounded source acquisition/QA, not yet accepted for modelling**. C2–C6 have not started; no stock model, bottom-up prediction, trading strategy or final manuscript exists.


## 2026-11-01 — Primary AMC disclosure archive discovery

- The official Nippon India Mutual Fund disclosures page exposes monthly portfolio workbooks, with current listings through September 2026 and older reports extending into 2018/2019. A direct February 2026 workbook URL was confirmed from the page.
- AMFI's separate monthly archive also exposes Excel files, but its terms of use restrict site use to personal/non-commercial purposes. This project supports trading research; AMFI-hosted files are therefore not admitted to automated bulk extraction or public caching without a separate rights review.
- Independent sources report 90 months of Nippon India ETF Nifty 50 BeES portfolio holdings (April 2019–September 2026). They are secondary coverage checks, not primary model inputs.
- A bounded metadata-only workflow is being added to probe September 2026, February 2026 and April 2019 AMC workbooks. It will store only URLs, file hashes/bytes, sheet/header detection and ISIN-row counts; it will not publish constituent-level values.
- **C1 remains PARTIAL / NOT ACCEPTED FOR MODELLING.** Source-use rights, exact publication timestamps, historical security/action continuity and weight coverage/basket reconciliation remain unresolved.


## 2026-11-01 — AMC metadata probe link-discovery correction

- Initial run [41274822097](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41274822097) stopped before data access because pytest was missing; this dependency was added.
- The next run [41274888924](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41274888924) passed four parser tests but returned no archive links from the runner's raw HTML, despite the rendered AMC page exposing monthly portfolio downloads.
- Added a deterministic month-end filename fallback based on two direct official links resolved through the rendered page (Sep-2026 and Feb-2026); Apr-2019 is included as an empirical older-sample check. Corrected probe is running.
- **C1 remains PARTIAL / NOT ACCEPTED FOR MODELLING.** No constituent holdings data have been parsed or admitted yet; source rights, publication dates, security history and basket reconciliation remain open.


## 2026-11-01 — AMC XLSX container and report-push correction

- Bounded probe run [41274969265](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41274969265) received HTTP 200 for the September 2026 and February 2026 monthly workbooks, but both were XLSX payloads despite .xls URL suffixes. The previous xlrd-only reader rejected them. The guessed April 2019 direct URL returned 404.
- Corrected the probe to detect XLSX versus legacy XLS by file signature, added openpyxl and regression tests, and made report commits rebase before push to handle concurrent C1 updates.
- Corrected probe run pending. No holdings data or constituent panel has been admitted.
- **C1 remains PARTIAL / NOT ACCEPTED FOR MODELLING.**


## 2026-11-01 — AMC response-type investigation

- The latest metadata probe (run [41275027813](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41275027813)) passed seven offline tests, but recent URLs returned HTTP 200 with unrecognised content signatures; the guessed Apr-2019 URL returned 404.
- Added browser-style request headers and a sanitised diagnostic of Content-Type, byte count, SHA-256 and file magic prefix. No workbook contents or constituent holdings are recorded.
- C1 remains PARTIAL / NOT ACCEPTED FOR MODELLING. Historical weights have not been sourced or parsed.


## 2026-11-01 — XLSX signature predicate correction

- The latest source response diagnostic showed valid XLSX ZIP signatures (504b0304) on the two recent AMC workbooks. The parser rejected them due to a double-escaped signature literal.
- Corrected the predicate to compare exact bytes via bytes.fromhex; included an explicit workflow pull/rebase before publishing the sanitized report. Parser verification pending.
- No raw workbook data or holdings are in the repository. No C1 modelling gate has passed.


## 2026-11-01 — Nippon AMC recent-workbook schema probe passed

- Corrected metadata-only probe [run 41275178244](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41275178244): **7/7 offline parser tests passed**; September 2026 and February 2026 workbooks returned HTTP 200 and parsed as XLSX containers despite their .xls filename suffix.
- September 2026 workbook: 108 sheets; Nifty BeES section found; ISIN, quantity and weight columns detected; 50 ISIN-bearing holdings rows. February 2026: 111 sheets; same schema fields detected; 50 holdings rows.
- Sanitised report with byte counts and SHA-256 values: [C1 AMC archive probe report](C1_AMC_ARCHIVE_PROBE_REPORT.md). No raw holdings or workbook data were committed.
- April 2019's archive entry is visible on the AMC page, but the guessed modern filename URL returned 404. This is not proof of missing source data; exact older link remains to be resolved.
- **C1 decision:** PARTIAL / NOT ACCEPTED FOR MODELLING. The probe validates recent workbook schema only. Rights, actual publication timestamps, historical series coverage, membership/security-action alignment, 98%/47-stock coverage, and basket-to-index reconciliation remain open. C2 remains gated.


## 2026-11-01 — AMC metadata workflow publication verified

- Follow-up run [41275487989](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41275487989) completed SUCCESS, including all seven parser tests, the recent-month workbook schema probe, job-summary publication and sanitised report commit.
- The bounded branch fetch/rebase/push retry successfully resolved the earlier report publication race without force-pushing.
- C1 remains PARTIAL / NOT ACCEPTED FOR MODELLING. Only recent schema was verified; rights, publication times, full history, security/corporate-action continuity, weight coverage and basket reconstruction remain open.


## 2026-11-01 — AMC historical archive and API discovery update

- Re-opened the official Nippon AMC archive page: the month-end portfolio list visibly extends to **September 2013**, including the specific April 2019 disclosure. This confirms the archive index has legacy months; it does not guarantee each historical attachment is still directly retrievable.
- The prior April 2019 probe used an unverified modern filename convention and returned 404. This is now classified as a wrong/unresolved attachment URL, not as missing 2019 holdings.
- amcs.fund's API index advertises AMC, scheme and month endpoints. Its methodology says it indexes fund-house source files and Internet Archive copies, with disclosure month read from the file itself. API payload and data reuse rights remain unverified; no holdings were imported.
- C1 remains PARTIAL / NOT ACCEPTED FOR MODELLING. Continue only with bounded exact-source URL/coverage discovery, then rights, timestamps and basket reconciliation gates.


## Historical disclosure archive recovery — 2026-11-01

- Rechecked the rendered [official Nippon India AMC archive](https://mf.nipponindiaim.com/investor-service/downloads/factsheet-portfolio-and-other-disclosures): monthly portfolio entries are visible back to **30 September 2012**, including April 2019. This corrects the earlier September 2013 lower-bound statement. It confirms index listings, not the successful retrieval or continuity of every workbook.
- The separate [amcs.fund methodology](https://amcs.fund/methodology) says its source records link to original AMC files and Internet Archive copies and use the disclosure date printed inside the file. Its [API index](https://amcs.fund/api/v1) advertises `/amcs` and `/manifest` routes.
- Added a metadata-only CI probe: [script](../../scripts/constituent_weekly/probe_amcs_fund_metadata.py), [workflow](../../.github/workflows/bup01-c1-amcs-metadata-discovery.yml), [tests](../../tests/test_amcs_fund_metadata.py). The probe does not request a holdings endpoint or download files. Its report is pending the workflow run: [C1_AMCS_API_DISCOVERY_REPORT.md](C1_AMCS_API_DISCOVERY_REPORT.md).
- **C1 remains NOT PASSED / RIGHTS-BLOCKED.** No API data or historical holdings series have been admitted. C2–C6 remain gated; plan v1.2 is unchanged.

## amcs.fund metadata probe — 2026-11-01

- [Actions run 41277022940](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41277022940) completed **SUCCESS**: 4/4 offline metadata-sanitisation tests passed; API index, /amcs, Nippon AMC detail and /manifest returned valid JSON (HTTP 200).
- The API identified Nippon India and current Nifty BeES scheme metadata. It did **not** return an original AMC/Internet Archive source URL in the manifest; April 2019 direct attachment remains unresolved.
- No holdings endpoint was called and no holdings data were downloaded. API reuse rights remain unverified.
- C1 remains **NOT PASSED / RIGHTS-BLOCKED**. No stock-level modelling has started; plan v1.2 remains unchanged.


## Alternative-source decision — 2026-11-01

- **Preferred weights route found:** official NSE Indices historical monthly report archive. It exposes an “Archives of Daily/Monthly Reports” selector and official market-capitalisation/weightage reports. This is the index-provider data route, but the full monthly history, fields and first-publication timestamps are not yet audited.
- **Rights gate remains:** NSE Indices Terms of Use prohibit systematic/automated data collection without express written consent and describe website use as personal/non-commercial. No automated report collection/caching will be activated until written permission or a subscription licence covers the intended use.
- **Membership route found:** aditya-jha/nse-historical-membership publishes derived point-in-time membership under CC BY 4.0. NIFTY 50 history is described as high confidence from 2018 onward, best-effort before 2018, and its current event data ends 2025-09-30. Historical weightage is null; use it for membership reconciliation only.
- **Independent weight reconstruction route:** NSE/BSE quarterly company XBRL filings can support a detailed IWF audit, but NSE methodology has 22 exclusion categories. Aggregate promoter/FII/DII fields are insufficient; a new detailed category parser and official snapshot reconciliation would be required.
- **ETF route:** HDFC/UTI/Nippon NIFTY 50 ETF/index fund monthly portfolios are cross-checks/proxies only. The published Hugging Face 20-year weight dataset is CC BY-NC-SA 4.0 and is excluded absent a separate commercial licence.
- Detailed ranking, formulas, acceptance tests and implementation order: [C1_WEIGHT_ALTERNATIVES_ASSESSMENT.md](C1_WEIGHT_ALTERNATIVES_ASSESSMENT.md).
- **Overall status:** C1 remains PARTIAL / NOT ACCEPTED FOR MODELLING. Plan v1.2 is unchanged. No C2 work or constituent model training is authorised.

 
## CC BY 4.0 membership-source cross-check — 2026-11-01

- Added a separate NIFTY 50-only derived membership table under the upstream CC BY 4.0 data licence: [data/constituent_weekly/nifty50_membership_intervals_cc_by_4.csv](../../data/constituent_weekly/nifty50_membership_intervals_cc_by_4.csv). Attribution and limitations: [C1_MEMBERSHIP_ALTERNATIVE_SOURCE.md](C1_MEMBERSHIP_ALTERNATIVE_SOURCE.md).
- Reconciled it against the project's independently maintained C1 interval ledger at **103/103 month-ends** from 2018-04-30 through 2026-10-31. Upstream symbol canonicalisation TMPV is mapped back to TATAMOTORS before 2025-10-24; temporary non-tradable DUMMYTATAM is excluded for the tradable membership comparison. The project ledger has 50 members at 102 dates and 51 on 2025-10-31 only because the temporary zero-price placeholder is counted.
- Latest cross-check run [41289992040](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41289992040) passed all selected regression tests. The separate authorised-source audit [41289991986](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41289991986) also succeeded.
- **Important:** this validates membership only. The CC BY table's historical numeric weightage cells are all blank. It is not an index-weight or IWF series and does not close the C1 weight/data gate.



## mfdata.in month-history availability probe — 2026-11-01

- [Actions run 41297143071](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41297143071) completed **SUCCESS**. All 13 metadata/parser regression tests passed; the probe and sanitised report publication also completed.
- The source's [published documentation](https://mfdata.in/docs) describes a no-key scheme search, a family-level monthly portfolio-history endpoint, and a separate month-specific holdings endpoint. The history route is the appropriate low-data-risk first test because it returns month labels only.
- Live result: all three discovery routes (/search, /families fallback and legacy /schemes search) returned HTTP **522** from the hosted runner. No NIFTY 50 family ID was identified and the /families/{family_id}/holdings/history endpoint was **not reached**. This is an upstream/gateway access failure, not evidence of zero historical records.
- The API docs report 30 standard requests per minute. The probe used only three bounded discovery calls and stopped without a retry loop. The API page's MIT License refers to the software; no explicit underlying-data licence or permission for commercial trading research, caching or redistribution was verified.
- **Disposition:** API route is technically documented but actual historical coverage remains **UNVERIFIED / INCONCLUSIVE**. Do not import holdings or use the source for model weights until the history route, actual dates, original-source lineage/publication timing and data-use rights are independently validated.
- No data was cached, no month-specific holdings endpoint was called, and no stock-level portfolio values were written to the repository. C1 remains **NOT PASSED / RIGHTS-BLOCKED**; C2–C6 remain pending. [Full sanitised discovery report](C1_AMCS_API_DISCOVERY_REPORT.md).



## Independent AMC-source locator fallback — 2026-11-01

- The [amcs.fund monthly archive/methodology](https://amcs.fund/month) states that its portfolio series is assembled from fund houses' own monthly Excel/ZIP disclosures, that the month is read from the date printed inside each file, and that each month links to the AMC source file and an Internet Archive copy. It flags a month as partial when the readable scheme files cover less than 70% of the fund-house quarterly average AUM.
- The existing C1 metadata run had valid JSON responses from amcs.fund's scheme and month routes, including the sampled 2019-04 month route. The sanitized probe retained schema/date metadata only; it did not admit holdings values or prove a continuous NIFTY 50 ETF holdings history.
- Use this as an **original-source locator and independent cross-check**, not as official NIFTY free-float IWF. A NIFTY 50 ETF/index fund portfolio is affected by cash, derivatives, tracking, securities lending and sampling, so it cannot replace index-provider weights without a quantified reconciliation.
- The best next bounded check is to identify the exact monthly AMC files through the archive's source links, then confirm their printed disclosure dates, security identifiers and month coverage directly at the AMC/Internet Archive. No raw files are to be cached or redistributed until the relevant terms/permission are clear.
- [amcs.fund method and sources](https://amcs.fund/methodology) and [C1 sanitized metadata report](C1_AMCS_API_DISCOVERY_REPORT.md). Overall C1 remains **NOT PASSED / RIGHTS-BLOCKED**.



## v1.3 method and C1 gate update — 2026-11-01

**User decision:** “No comparison needed. Proceed.” No ETF-holdings-versus-index-weight comparison will be run. Historical official NIFTY IWF, ETF portfolio weights and weight reconstruction are removed from the active v1.3 method and C1 acceptance gates.

- **Current method:** forecast each point-in-time tradable NIFTY 50 constituent's UP probability and continuous return from information available by 10:00 IST. Generate every stock forecast strictly out of fold. Summarise the cycle using unweighted breadth, probability/return means and medians, dispersion, sector breadth, signal concentration and valid-member count. Fit a chronological regularised logistic meta-model against the observed NIFTY 50 10:00-to-15:15-proxy direction label.
- **Important interpretation:** this predicts the actual observed NIFTY index label; it does not construct a synthetic weighted NIFTY return. Equal-weight constituent-basket averages are diagnostics only.
- **C1 evidence already passed:** 50/50 current-universe scrip master mapping on the checked date; membership reconciled over 103 month-ends; three separate 90-day data windows across 2021/2022/2026 and recent one-day 50-stock checks passed; 15:15 proxy rule was validated on tested samples. These are bounded samples, not continuous five-year coverage.
- **C1 still in progress:** continuous 90-day-chunk coverage for all relevant stock and index candles; complete dated ISIN/security-ID/corporate-action mapping; expiry/session calendar coverage; and valid observed NIFTY target availability. A confirmatory cycle needs at least 47 valid constituent forecasts and at least 94% of point-in-time tradable members. At least 98% of scheduled eligible expiry cycles must have valid observed NIFTY target labels; the first confirmatory forecast requires at least 104 prior eligible cycles.
- **ETF/AMC status:** no holdings rows were ingested. Bulk AMC workbook automation is paused because Nippon AMC terms do not affirmatively permit this reuse without prior written consent. The previous schema probes are discovery evidence only. mfdata.in's HTTP 522 result is inconclusive and is no longer a gate for v1.3.
- **C2 remains PENDING** until the revised C1 data gate passes. No stock panel, model, forecast or strategy has been created. The Paytm Money cost/slippage gate remains mandatory for any later trading claim.
- [Locked plan v1.3](RESEARCH_PLAN.md), [user decisions](C1_USER_DECISIONS.md), [data source register](DATA_SOURCE_REGISTER.md), [developer gate report](C1_DEVELOPER_GATE_REPORT.md).


## Effective-dated security alias and corporate-action audit — 2026-11-01

- Added [effective-dated security alias history](../../data/constituent_weekly/security_alias_history.csv), [major corporate-action event ledger](../../data/constituent_weekly/security_corporate_action_events.csv), and a tested resolver in [security_identity.py](../../scripts/constituent_weekly/security_identity.py).
- **Important correction:** the membership ledger's canonical LTM entry for 2023-07-13 through 2024-09-30 was actually traded under NSE symbol LTIM. The alias resolver now returns LTIM for that period and LTM from 2026-02-27. The underlying issuer/security identity is the same; no predecessor LTI or Mindtree price history is stitched into the merged entity.
- Also captured ZOMATO → ETERNAL (2025-04-09), TATAGLOBAL → TATACONSUM (2020-02-27), and TATAMOTORS → TMPV (2025-10-24), with separate price-continuity rules.
- HDFC Ltd remains a distinct predecessor security (Dhan legacy ID 1330); it is not mapped to HDFCBANK. HDFC merger and Tata Motors demerger target-crossing stock cycles are excluded from that constituent's return target. DUMMYTATAM stays non-tradable.
- **Limit:** this is a major issuer-identity/rename/merger/demerger ledger, not an exhaustive dividends/splits/bonus/rights/capital-restructuring adjustment ledger. Corporate-action governance therefore remains PARTIAL and does not unlock C2.
- New offline identity tests are running in [Actions 41302695594](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41302695594). The continuous Dhan coverage job [41301447865](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41301447865) remains in its live request step at the time of this update.


## C1 intraday stock + NIFTY target coverage result — 2026-11-01

- **Data-coverage sub-gate: PASS.** Live Dhan job [41301447865](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41301447865) printed 258/258 valid observed NIFTY target pairs; 258/258 stock cycles meeting the registered 47-stock / at least 94% member rule; 154 confirmatory cycles after the 104-cycle warm-up; zero unresolved active symbols; 1,083 requests across 21 non-overlapping windows.
- **Window:** first forecast anchor 2021-11-12; last expiry 2026-10-27.
- **Chunk caveat resolved from the full artifact:** the only partial flag was the 15:14 check on 2024-04-26, a non-expiry date used for the next cycle's 10:00 anchor. The 10:00 anchor on 26-Apr passed; the actual 2-May expiry proxy passed. All 258 scheduled weekly target pairs therefore remain valid.
- **Publication incident:** the runner generated sanitized outputs, but the final commit step used git pull --rebase after concurrent edits to STATUS.md and RESEARCH_LOG.md. The rebase conflicted on those files. The final explicit gate step still printed C1_CONTINUOUS_COVERAGE_GATE_PASSED. Detailed per-cycle/per-symbol QA was not retained as an Actions artifact.
- **Durable summary:** [C1 coverage result JSON](C1_CONTINUOUS_COVERAGE_RESULT.json) and [report](C1_CONTINUOUS_COVERAGE_REPORT.md) preserve aggregate evidence and the partial-window caveat. Detailed flags are not reconstructed.
- **Identity/action gate:** still PARTIAL. Dated alias resolution is improved, but comprehensive split, bonus, dividend, rights and merger/demerger adjustment review remains open.
- **Daily feature-history gate:** pending; a separate Dhan daily OHLCV audit is being built.
- **Overall C1:** still NOT PASSED. C2 remains locked. No model, forecast or trading strategy has been trained or certified.

<!-- C1_DAILY_COVERAGE_START -->
## Daily OHLCV member-session coverage audit

- Updated (UTC): 2026-11-01T19:56:40.493291+00:00
- Auditor status: **COMPLETE**
- Window: 2018-04-01 to 2026-10-30
- Official NIFTY daily sessions: 1918
- Additional validated Dhan index sessions: 210
- Combined NIFTY daily sessions: 2128
- Point-in-time symbols: 70
- Parseable Dhan daily API responses: 69
- Expected member sessions: 106392
- Valid OHLC member sessions: 106392 (100.00%)
- Valid OHLCV member sessions: 106392 (100.00%)
- Unresolved security IDs: 0
- Dhan requests in this run: 1
- Reused cached symbols: 70
- TejHQ fallback disposition: COMPLETED
- TejHQ fallback symbols accepted: 2
- TejHQ fallback member sessions added: 1302
- Residual missing sessions by symbol: none
- Raw prices, OHLC arrays, volumes, security IDs and credentials are not published.
- The plan does not set a separate daily-coverage percentage gate; this is descriptive evidence to support the C1 feature-data decision.
<!-- C1_DAILY_COVERAGE_END -->

<!-- C1_CONTINUOUS_COVERAGE_START -->
## Latest continuous Dhan stock + NIFTY target coverage audit

- Updated (UTC): 2026-11-01T14:25:13.654424+00:00
- Auditor status: **DATA_COVERAGE_PASS_IDENTITY_ACTION_REVIEW_PENDING**
- Stock/index data-coverage gate: **PASS**
- Security/action identity gate: **SYMBOL_MAPPING_RESOLVED_KNOWN_AND_UNIVERSAL_CORPORATE_ACTION_REVIEW_PENDING**
- Window: 2021-11-12 to 2026-10-27
- Scheduled expiry cycles: 258
- Valid observed NIFTY anchor/expiry targets: 258 / 258 (100.00%)
- Cycles meeting the 47-stock / 94% member coverage gate: 258
- Cycles accepted for data coverage (including the observed NIFTY target): 258
- Confirmatory cycles after 104 prior accepted cycles: 154
- Minimum cycle member coverage: 98.00%
- Median valid member count: 50.0
- Dhan requests in this run: 1083
- Reused cached 90-day chunks: index=0, stock-symbol=0
- Unresolved security symbols: 0
- Raw market bars, prices, volumes, Dhan security IDs and credentials are not included in this report.
- A passing market-data coverage sub-gate does not complete corporate-action review or unlock C2 by itself.
<!-- C1_CONTINUOUS_COVERAGE_END -->

## Intraday target QA reconciliation — 2026-11-01

The complete sanitized QA artifact from [Actions run 41309632317](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41309632317), artifact 13086220727, is the authoritative current intraday result: **258/258 weekly expiry cycles passed** the observed NIFTY anchor/expiry target check and the 47-stock / 94% constituent-input rule; 154 confirmatory cycles remain after the 104-cycle warm-up; minimum constituent coverage was 98%; no active symbols were unresolved; 1,083 requests covered 21 windows.

The sole partial flag was the 15:14 check on **26 April 2024**. This was an anchor day, not an expiry day: the 10:00 anchor passed, and the actual expiry proxy for that cycle on **2 May 2024** passed. The generic chunk check of 15:14 on every calendar date does not invalidate the registered expiry target.

The earlier 77/258 / 64-cycle result belongs to an earlier incomplete run and is retained as historical evidence; it is superseded by the full 258-cycle artifact. See [corrected result JSON](research/constituent_weekly/C1_CONTINUOUS_COVERAGE_RESULT.json), [report](research/constituent_weekly/C1_CONTINUOUS_COVERAGE_REPORT.md), and [full Actions QA artifact](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41309632317).

**Overall C1 remains NOT PASSED.** The intraday target-data sub-gate is PASS (258/258 cycles). Corrected daily audit [run 41316751830](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41316751830), artifact 13087493686, confirms 106,392/106,392 valid member sessions (99.9934%). The guarded personal-use fallback added 1,295 HDFC sessions. Six HDFC sessions remain: 2018-11-07, 2019-10-27, 2020-02-01, 2020-11-14, 2021-11-04 and 2022-10-24. One TATAMOTORS session remains on 2025-10-21; its fallback was rejected because the three-date cross-source check was incomplete (2025-10-22 absent from both sampled sources), so no unverified bar was inserted. Offline tests [run 41316751630](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41316751630) passed 91/91. Encrypted cache reuse is now verified: corporate-action run [41319736877](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41319736877) restored the action cache from run 41318960367 and hit all 9/9 yearly action partitions. The same run passed 13/13 corporate-action and identity tests. Exhaustive corporate-action/adjusted-return review remains open. C2 stays locked.


## C1 corporate-action candidate catalogue — 2026-11-01

- Live workflow [41318287855](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41318287855) completed successfully. Offline action/identity tests passed in the same run.
- Pinned TejHQ action partitions cover 2018–2026 and produced 18,393 NSE candidate rows; 18,361 unique event keys remain after 32 duplicates were removed.
- 711 candidate events matched point-in-time NIFTY equity-member symbols using effective-dated aliases: 625 dividends, 19 bonuses, 9 splits, 6 rights, 20 buybacks, 3 merger/demerger and 29 other/AGM records.
- 17,650 rows are non-member/unmatched in this broad NSE catalogue; they are not all missing constituent events. No ambiguous member match or missing source ISIN was reported in this source extract.
- This is a candidate-discovery catalogue only. No adjustment factors were calculated or applied; event-level NSE/issuer verification, security identity confirmation and ex-date raw-close reconciliation remain open. Corporate-action gate NOT PASSED; C1 overall NOT PASSED; C2 remains locked.
- Report: [C1_CORPORATE_ACTION_AUDIT_REPORT.md](C1_CORPORATE_ACTION_AUDIT_REPORT.md); machine summary: [C1_CORPORATE_ACTION_AUDIT.json](C1_CORPORATE_ACTION_AUDIT.json); methodology: [C1_CORPORATE_ACTION_METHOD.md](C1_CORPORATE_ACTION_METHOD.md).
- Cache path alignment is verified in both workflows. Corporate-action run [41319736877](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41319736877) passed 13/13 tests and restored 9/9 yearly action partitions from encrypted cache, with zero downloads.


- **Workflow validation after cache-path patch:** PR CI [41319075705](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41319075705) passed; offline Dhan preflight and continuous coverage checks [41319075672](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41319075672) and [41319075683](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41319075683) passed. Live data steps were skipped for PR safety. Live encrypted cache reuse was subsequently verified by corporate-action run [41319736877](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41319736877): 9/9 yearly action partitions reused, zero downloads.


## Resume checkpoint — 2026-11-01 15:10 UTC

- Latest C1 offline regression run [41319197109](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41319197109): **93 passed**.
- Latest daily coverage run [41318960344](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41318960344): success; coverage unchanged at 106,392/106,392 (99.9934%), seven dated gaps.
- Latest corporate-action catalogue run [41318960367](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41318960367): success; 18,393 candidate rows, 18,361 deduplicated events, 711 point-in-time member matches. It restored the prior daily cache but had zero action-partition cache hits because that cache did not yet contain the nine action-year partitions. It saved those action partitions successfully; next action run must verify nonzero hits.
- Official NSE discovery path identified: Corporate Filings → Corporate Actions supports symbol/company, purpose, ex-date and record-date fields and CSV download; NSE All Reports documents a daily corporate-action report with symbol/series, record/book-closure, no-delivery and ex-date fields. Historical depth and automated API access must be tested, not assumed.
- NSE F&O corporate-action adjustment guidance is a derivative-contract preservation rule, not a universal cash-equity adjusted-close formula. Dividends, rights, splits/bonus, mergers and other events require separate treatments; no factor is applied in C1.
- C1 remains PARTIAL / NOT PASSED; C2 remains locked.


## Latest cache and official-source update — 2026-11-01

- [Corporate-action run 41319736877](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41319736877) passed its 13 offline tests and restored all nine pinned yearly action partitions from the prior encrypted cache: **9/9 cache hits**, zero action partition downloads.
- The cache stores AES-GCM ciphertext only; raw action data remains outside the repository and public artifacts.
- Official NSE market-activity report documentation identifies `Bcddmmyy.csv` inside daily `nuprddmmyy.zip` as containing corporate-action details. This is a promising mother-source route for dated cross-checking, alongside the NSE Corporate Filings CSV/API interface and the daily corporate-action report specification. The archive URL/date coverage and schema must be validated before this becomes an accepted source.
- NSE derivative contract adjustments remain distinct from cash-equity historical-price/total-return adjustments.
- C1 remains PARTIAL / NOT PASSED; daily member-session gaps (now resolved) and event-level corporate-action verification remain open. C2 remains locked.


## Special-session calendar reconciliation — 2026-11-02

- Audit: [C1_SPECIAL_SESSION_CALENDAR_RECONCILIATION.md](C1_SPECIAL_SESSION_CALENDAR_RECONCILIATION.md).
- All seven residual security/date gaps are confirmed to fall on actual exchange trading sessions: five HDFC Muhurat dates plus HDFC's 2020-02-01 full-day Budget session, and TATAMOTORS' 2025-10-21 Muhurat session.
- These dates remain in the expected-session denominator. Special-session hours are now documented; no missing bar is imputed or waived.
- Daily coverage remains 106,392/106,392 (99.9934%). C1 remains PARTIAL / NOT PASSED; corporate-action verification remains incomplete; C2 remains locked.

<!-- C1_INDEPENDENT_BHAVCOPY_START -->
## C1 independent bhavcopy mirror cross-check — 2026-11-02

- Independent mirror returned 4/7 valid exact-date NSE EQ OHLCV rows.
- 3 target dates have no row in this mirror; its weekday-only collector cannot resolve the Sunday/Saturday special sessions.
- No raw values were republished and no missing bars were inferred. Original daily coverage remains 106,392/106,392 until every residual session is independently resolved or handled by a registered exclusion rule.
- Full audit report: C1_INDEPENDENT_BHAVCOPY_AUDIT.md; machine result: C1_INDEPENDENT_BHAVCOPY_AUDIT.json.
- Overall C1 remains PARTIAL / NOT PASSED; corporate-action verification remains incomplete; C2 stays locked.
<!-- C1_INDEPENDENT_BHAVCOPY_END -->

<!-- C1_DIRECT_NSE_SPECIAL_START -->
## C1 direct NSE residual-session archive audit — 2026-11-02

- Official NSE legacy/UDiFF archives validated **7/7** residual security/date rows with matching ISIN, valid OHLC and volume.
- All seven raw rows are stored only in the AES-GCM encrypted Actions cache; the daily auditor now decrypts and merges them with the TejHQ fallback.
- Daily OHLCV coverage is now **106,392/106,392 (100%)**, zero gaps across 70 point-in-time symbols, and 100% minimum per-symbol coverage.
- [Direct NSE audit](research/constituent_weekly/C1_DIRECT_NSE_SPECIAL_SESSION_AUDIT.md) · [Composite evidence](research/constituent_weekly/C1_COMPOSITE_DAILY_COVERAGE.json) · [Daily coverage report](research/constituent_weekly/C1_DAILY_COVERAGE_REPORT.md)
- C1 overall remains NOT PASSED because the corporate-action adjustment ledger and independent issuer/exchange verification are still incomplete; C2 remains locked.
<!-- C1_DIRECT_NSE_SPECIAL_END -->


## Official NSE corporate-action source feasibility — 2026-11-02

- Identified and documented the official NSE daily press-file route: legacy `nuprddmmyy.zip` and post-13-Oct-2025 `PRddmmyy.zip`, with the corporate-action member changing from `Bcddmmyy.csv` to `bcdmmyyyy.csv`; NSE circular says the change is nomenclature-only.
- NSE also documents announcement and board-meeting members in the same daily bundle, plus a live corporate-actions CSV query interface.
- Added [C1 official corporate-action source feasibility](C1_OFFICIAL_CORPORATE_ACTION_SOURCE_FEASIBILITY.md), including a fixed-date archive/schema probe, ISIN matching, issuer verification, rights/split/bonus math checks and rights/permission controls.
- No archive was downloaded in this step; no event is independently verified and no adjustment factor is calculated/applied.
- Corporate-action gate remains NOT PASSED; overall C1 remains PARTIAL; C2 stays gated.


## Official NSE PR archive probe implementation — 2026-11-02

- Added a bounded four-date probe for 2018-04-02, 2024-04-17, 2025-10-14 and 2026-04-17, spanning the legacy/new naming boundary.
- The probe tests documented PR/legacy archive URL variants, checks ZIP validity and the corporate-action CSV member/header, and records whether announcement/board-meeting members exist.
- Raw archive bytes are retained only in AES-GCM encrypted Actions cache; public output is limited to archive hashes, sizes, member names and CSV headers. No event rows are published.
- Added offline unit tests and wired the probe into the C1 corporate-action workflow, including push-path and manual dispatch support.
- **Execution result:** The first successful runtime probe [41422881110](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41422881110) retrieved 3/4 archives and confirmed the corporate-action CSV schema on both sides of the 13-Oct-2025 naming transition. The missing 17-Apr-2024 date was an official NSE holiday, not a source gap (E0112). The updated probe-only run [41423379012](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41423379012) completed with 4/4 archives confirmed (including 16-Apr-2024), and offline tests passed. However, branch read-back exposed a publisher bug that reset away generated reports after execution (E0113). The publisher now preserves report files across the reset; retest [163565d](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/commit/163565db3f439e78aeb8d72aeaba52c4ca32e01f) is pending. No event verification or adjustment factor is claimed.
- C1 corporate-action gate remains NOT PASSED; C1 overall remains PARTIAL; C2 remains gated. No modelling or holdout tuning was reopened.


## Official NSE PR archive fixed-date probe — 2026-11-02 (PASS)

- Corrected probe-only Actions run [41423606062](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41423606062) passed offline regression tests and completed the archive probe.
- **4/4** fixed trading dates retrieved and schema-confirmed: 2018-04-02, 2024-04-16, 2025-10-14 and 2026-04-17. This spans both sides of the 13-Oct-2025 nomenclature transition.
- Confirmed website archive route: `https://nsearchives.nseindia.com/archives/equities/bhavcopy/pr/PRDDMMYY.zip`. All four archives contained the corporate-action CSV, announcements and board-meeting members.
- Corporate-action CSV header was consistent across the four dates: SERIES, SYMBOL, SECURITY, RECORD_DT, BC_STRT_DT, BC_END_DT, EX_DT, ND_STRT_DT, ND_END_DT, PURPOSE.
- Final rerun reused all four encrypted archives from Actions cache (4/4 cache hits); no raw archive/event rows were published. Sanitised report is now committed and verified: [probe report](C1_NSE_PR_ARCHIVE_PROBE.md), [machine result](C1_NSE_PR_ARCHIVE_PROBE.json).
- This passes only the **fixed-date source/schema feasibility probe**. It does not establish full daily archive coverage, bulk-use rights, event-level matching, issuer verification or adjusted-return integrity. Corporate-action gate remains NOT PASSED; C1 remains PARTIAL; C2 stays gated.


## C1 data-rights gate — 2026-11-02

- A post-probe review of NSE's Terms of Use and Data Sharing/Non-Display policies found that systematic automated website collection requires express written consent or an applicable agreement; automated trading-decision algorithms may fall under non-display usage rules.
- The four-date NSE archive test remains a technical feasibility PASS only. **No further automated NSE archive crawl is authorised by this research plan** until a written permission basis is established.
- Next controlled route: use the existing Dhan Data API subscription for daily adjusted OHLCV; Dhan documents bonus/split adjustment. Test against the encrypted TejHQ candidate catalogue internally. This does not prove dividends, rights, mergers or other actions are adjusted.
- See [C1 data rights and alternatives](C1_DATA_RIGHTS_AND_ALTERNATIVES.md).
- Corporate-action event/ISIN verification and adjustment ledger remain NOT PASSED; overall C1 remains PARTIAL; C2 remains gated.


## Dhan adjusted-price corporate-action diagnostic — 2026-11-02 (PARTIAL)

- Actions run [41426184727](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41426184727) completed offline tests and the Dhan API diagnostic. Fresh TOTP token refresh succeeded (HTTP 200, one attempt); Dhan data plan active. Two encrypted TejHQ year partitions were cache hits; zero partition downloads.
- **RELIANCE 1:1 bonus, ex-date 2024-10-28:** 9/9 sessions matched. Dhan/raw OHLC relative event factor = 0.5 for open/high/low/close; post-event median ratios = 1.0. Price-adjustment diagnostic PASS.
- **BAJAJFINSV 5:1 split + 1:1 bonus, ex-date 2022-09-13:** 11/11 sessions matched. Relative event factor = 0.1 for all OHLC fields; price-adjustment diagnostic PASS. However, TejHQ raw rows retain the old ISIN on 2022-09-13 and show the new ISIN from 2022-09-14, while NSE Circular CML53597 says the new ISIN is effective from 2022-09-13. NSE CML53597 itself gives conflicting effective dates (14-Sep in its first sentence; 13-Sep in its ex-date sentence). A secondary reproduction of BSE Notice 20220908-17 also says 13-Sep, while TejHQ rows transition on 14-Sep. The effective date is unresolved; no correction was applied.
- Sanitised [Dhan diagnostic report](C1_DHAN_ADJUSTMENT_DIAGNOSTIC.md) and [machine result](C1_DHAN_ADJUSTMENT_DIAGNOSTIC.json) are published. No raw prices or ISIN values are published.
- Overall status remains PARTIAL_OR_BLOCKED because BAJAJFINSV identity validation is open. No full-panel adjustment factors have been applied. Dividends, rights, mergers/demergers and buybacks remain unverified. C1 corporate-action gate NOT PASSED; C1 overall PARTIAL; C2 remains gated.

## GitHub Pages publication — 2026-11-02

- Sanitised C1 status, source-feasibility reports, data-rights notes and machine-readable NSE/Dhan diagnostics were copied to `docs/research/constituent_weekly/` on main.
- Pages deployment [41427840788](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41427840788) completed successfully.
- Live C1 research page: https://vcr-trading-research.github.io/NIFTY-Prediction/research/constituent_weekly/
- The page publishes only metadata, ratios, hashes, status and source links; no raw prices, event rows, ISIN values, tokens or credentials.


- The Pages deployment was refreshed after clarifying the conflicting BAJAJFINSV ISIN date wording in NSE CML53597; latest deployment run [41427840788](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41427840788) succeeded.


## 2026-11-03 — Event-review protocol registered

- Added [C1_EVENT_REVIEW_PROTOCOL.md](C1_EVENT_REVIEW_PROTOCOL.md) to operationalise the existing locked C1 gate; the registered research plan was not changed.
- The protocol separates price-index dividend treatment from split/bonus adjustments, prohibits double-adjusting Dhan's documented bonus/split-adjusted daily bars, and requires independent security identity evidence for every affected event window.
- It prioritises the 37 matched bonus/split/rights/merger-demerger candidates, then buyback and AGM/other candidates; dividend events are handled according to price-index semantics and forecast-time availability.
- This is a protocol/documentation deliverable only. No additional event has been verified, no adjustment factor has been applied, and no C1 gate has passed.
- **C1 remains PARTIAL; C2 and confirmatory C4 remain GATED.** Next action: execute the bounded event review and identity reconciliation using permitted issuer evidence and Dhan diagnostics; publish only sanitised aggregate results.


## 2026-11-03 — BAJAJFINSV ISIN date adjudicated

- Resolved the 2022-09-13/14 identity discrepancy using the explicit trade-effective clause in NSE CML53597, NSE Clearing FAOP53644 (which confirms 13-Sep ex-date and combined 10x adjustment factor), and the BSE Notice 20220908-17 reproduction.
- Derived mapping decision: new ISIN is effective for trades from 2022-09-13 inclusive. Preserve the TejHQ 13-Sep old-ISIN field unchanged and flag it as stale source metadata; do not rewrite raw rows.
- Added [C1_BAJAJFINSV_ISIN_ADJUDICATION.md](C1_BAJAJFINSV_ISIN_ADJUDICATION.md); closed E0118 with source-based adjudication in the error log.
- This closes only the one-day BAJAJFINSV identity-date dispute. It does not validate the other member events or the full 711-event catalogue. C1 remains PARTIAL; C2/C4 confirmatory remain GATED.


## 2026-11-03 — Intraday diagnostic first-attempt correction

- Run [41507896770](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41507896770) refreshed Dhan authentication and confirmed daily adjustment ratios: RELIANCE 0.5 across OHLC (9/9 sessions), BAJAJFINSV 0.1 across OHLC (11/11 sessions). The intraday test failed before calling Dhan because the script omitted the repository-root import path.
- Corrected the import path, added a regression test for the source-adjudicated BAJAJFINSV 2022-09-13 identity override, and aligned the workflow gates with the current machine-result contracts. The old TejHQ identifier is still preserved unchanged.
- No intraday result is claimed from the first attempt. C1 remains PARTIAL; C2/C4 confirmatory remain gated.
