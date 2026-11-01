# BUP-01 C1 developer gate report

**Report date:** 2026-11-01  
**Phase branch:** phase/constituent-weekly-outcomes-c1-data  
**Plan:** BUP-01 v1.1, locked; no plan amendment  
**Developer decision:** C1 is **PARTIAL PASS / RIGHTS-BLOCKED**. Do not enable C2–C6 until the listed hard gates are evidenced.

## 1. Executive finding

The Dhan authentication and bounded 1-minute equity-data validation pipeline is operational. The latest protected preflight passed its final fail-closed gate and every tested constituent passed strict target-window QA in three separate 90-day windows plus one current session.

The remaining hard blocker is not a token/API outage. No available source has been admitted that provides a complete, point-in-time official NIFTY 50 IWF/constituent-weight history with rights for automated retrieval, private retention, model training/backtesting and the intended internal algorithmic-trading research use. The XBRL category candidate is technically promising but its explicit data-licence globs do not clearly cover the nested compressed category CSV, and aggregate categories do not establish all 22 IWF exclusions. The weighted constituent basket has therefore not been reconciled to the official NIFTY 50 index.

**No C2 constituent panel, C3 stock model, C4 weighted NIFTY forecast, C5 economic strategy or C6 final manuscript has been generated.** No usable bottom-up prediction or strategy is claimed.

## 2. Gate scoreboard

| Gate | Result | Evidence / limitation |
|---|---|---|
| C0 research registration and governance | PASS | Pre-registered BUP-01 v1.1; required phase files and governance checks exist |
| Current NIFTY 50 scrip master | PASS on tested date | 50/50 current symbols resolved |
| Historical membership alias resolution | PARTIAL | 79/84 ledger aliases resolve against today's security master; five not found in current master require dated historical identity proof |
| Dhan authentication / data plan | PASS | TOTP refresh on first attempt; active plan; protected live workflow status PASS_ACTIVE_EQUITIES |
| One-session 50-name intraday QA | PASS | 2026-10-29: 50/50 |
| 90-day 50-name intraday QA | PASS on three disjoint samples | 2021-11-01–2022-01-29: 50/50; 2022-10-03–2022-12-30: 50/50; 2026-06-29–2026-09-26: 50/50 |
| Continuous five-year one-minute coverage | NOT PROVEN | Three separate windows are not a continuous five-year backfill |
| 10:00 anchor / 15:15 expiry-proxy convention | PASS on sampled rows | Latest candle at 15:00–15:14; all late bars excluded; 15:14 used in examples |
| SHREECEM 2021 edge QA | PASS after scope correction | Only negative-volume row was 2021-12-30 15:29 IST, beyond the pre-registered 15:15 cutoff; reported separately; target scope remains strict |
| Historical ISIN/security-ID and corporate actions | PARTIAL / OPEN | Symbol ledger exists but full dated stable-ID history and corporate-action continuity not independently complete |
| Official point-in-time IWF/weights with intended-use rights | BLOCKED | Official monthly ZIP family identified; written permission/licence for automation, caching and trading-research use not obtained |
| 22 IWF exclusion evidence | PARTIAL / OPEN | Machine-readable matrix created; multiple relationship/contract categories are not provable from category aggregates alone |
| IWF mathematical implementation harness | PASS | Official NSE example reproduced as 0.608794; duplicate share-position deduction rejected; seven new tests included |
| Weighted basket-to-index reconciliation | NOT RUN | Requires authorised complete weights/IWF and identity/corporate-action mapping first |
| C2–C6 | GATED | No modelling or strategy work without C1 acceptance |

## 3. Key Actions runs

- Protected Dhan preflight, final status PASS: [41266897788](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266897788).
- Baseline regression suite before IWF arithmetic tests: [41266922851](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266922851), 43 passed.
- Corrected full offline suite including IWF tests: [41269516064](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41269516064), 50 passed.
- Pull-request validation of the same full suite: [41269519499](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41269519499), 50 passed.
- C1 authorised-source audit workflow: [41269430549](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41269430549), successful.

The offline regression workflow initially omitted the newly added IWF test module despite its path filter. This was recorded as E0049, corrected in commit 12d997bf51c12a5780abcd6a9836d69853327bd0, and verified by the 50-test runs above.

## 4. Methodological controls and outstanding risks

### 4.1 IWF denominator and double counting

The official NSE IWF guideline's worked example uses:

IWF = (Total Shares - sum of separately identified excluded shares) / Total Shares

and rounds the result to six decimals. The third-party XBRL parser also reports shareholding percentages on an A+B+C2 base (total less C1/DR shares). That percentage base must not be substituted for the IWF denominator. Reconstruct from absolute share counts and reconcile the correct full share-capital base and DR treatment to official historical files.

A single holding may satisfy more than one exclusion description (e.g. promoter-related and DR-related). Deduplicate holding positions before subtracting. Never sum 22 overlapping category aggregates blindly.

### 4.2 Category mapping

The matrix in C1_IWF_EXCLUSION_MAPPING.csv covers all 22 official IWF exclusions. Promoter, government, FDI, FVCI, SWF, IEPF and locked-in data have plausible category-level candidates; promoter family, group/associate ownership, director/KMP roles, board nomination rights, right-of-first-refusal, strategic purpose and PAC status require dated relationship or contractual evidence. These statuses are candidates only until actual authorised XBRL rows and official weights are audited.

### 4.3 Data rights and storage

The upstream detailed shareholding candidate's LICENSE-DATA globs do not unambiguously include the nested parsed compressed CSV. Do not copy or import that file without written path-specific licence confirmation. Its named-shareholder file is excluded from scope.

The NIFTY-Prediction repository is public. Do not commit raw Dhan minute bars, NSE/XBRL source rows, named shareholder records or private-license datasets to public branches, workflow artifacts or public Actions caches. The user's preference for repo caching does not override source terms. A separately authorised private store is required for raw restricted data.

## 5. Required next developer actions

1. Obtain a written NSE Indices/NSE Data agreement (or equivalent explicit permission) covering historical NIFTY 50 constituent weights/IWF, machine retrieval, private cache retention, model training, quantitative backtesting, own-capital algorithmic-trading research and the permitted publication of non-reconstructive derived outputs.
2. If the XBRL category dataset is proposed instead, obtain an explicit licence statement covering the exact nested path shareholding_history/data/parsed/_categories.csv.gz; validate representative filings from every taxonomy generation; and complete the 22-exclusion mapping with overlap resolution and date-effective evidence.
3. Arrange an access-controlled private data store before any raw Dhan/NSE/XBRL data is retained. Public repo should keep only code, permitted provenance/hashes and non-reconstructive QA reports.
4. Complete the continuous weekly-cycle one-minute data coverage across the intended confirmatory history in bounded <=90-day chunks, with dated historical security ID/ISIN/symbol mapping and corporate-action continuity. Preserve source-native values and QA.
5. Reconstruct daily free-float weights using the latest authorised IWF known at each 10:00 forecast timestamp and dated prices/share capital. Confirm official methodology, capping, rounding and divisor treatment.
6. Reconcile weighted constituent basket return to the official NIFTY 50 price-return move on matched cycles. Enforce at least 98% point-in-time weight and at least 47 valid names. Lock the numerical tolerance before model results are viewed.
7. Only after all gates above pass, move to C2 and follow the locked walk-forward, untouched holdout and uncertainty plan.

## 6. Repository integrity review

At handoff:
- Main README contains the latest C1 data result, remaining rights gate and links to phase files.
- C1 STATUS.md records current gate outcomes; C1 RESEARCH_PLAN.md remains version 1.1 and unchanged.
- RESEARCH_LOG.md and CONVERSATION_LOG.md record visible research actions/results; hidden reasoning and secrets are not stored.
- ERROR_LOG.md records E0049 as closed and E0050 as an open denominator/source-reconciliation risk.
- The IWF matrix, mathematical audit, code helper, unit tests and offline workflow changes are committed on the C1 phase branch.
- The source-audit and offline workflows passed; the protected Dhan run passed its final fail-closed check.
- No raw market data or unlicensed shareholding records were imported during this continuation.

## 7. Final C1 decision

**C1 is not accepted.** The market-data acquisition component passed on the bounded Dhan samples, and the IWF arithmetic harness is tested, but source rights, complete exclusion evidence, continuous historical coverage, stable historical identity and weighted basket reconstruction are unresolved. The next gating event is a documented data-rights resolution and secure data-access/storage arrangement—not another unbounded search or model-training attempt.

BUP-01 v1.1 remains locked. C2–C6 remain pending. No trading recommendation is implied.
