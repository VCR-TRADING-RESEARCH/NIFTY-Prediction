# BUP-01 — ETF portfolio holdings as a public weight proxy

**Audit date:** 2026-11-01  
**Phase:** C1 / BUP-01  
**Disposition:** One-date calibration PASS; historical proxy panel NOT YET BUILT; C1 overall remains PARTIAL.

## Executive finding

A usable public-source proxy was identified: **Nippon India ETF Nifty 50 BeES** publishes portfolio holdings, and the asset manager describes a passive strategy that invests in NIFTY 50 securities in the same proportion as the index. It is not the official index file, but it provides an independently disclosed, investable replication basket. The AMC's February 2026 scheme portfolio is dated 28-Feb-2026 and reports NAV as of 27-Feb-2026. It lists the complete 50-stock portfolio plus 0.08% cash.

The February 2026 holdings were compared with the repo's one-date official NIFTY 50 weight snapshot dated 2026-02-27 (NSE Indices white paper, Exhibit 26). Both sets were normalized independently over the 50 equity rows; the 0.08% cash balance was excluded from the ETF stock basket. All 50 symbols matched.

| Calibration statistic | Result |
|---|---:|
| Matched stocks | 50 / 50 |
| ETF equity total before normalization (% NAV) | 99.92% |
| Official weights sum as printed | 100.02% |
| Mean absolute difference | 0.002214 percentage points |
| RMSE | 0.003204 percentage points |
| Maximum absolute difference | 0.008967 percentage points |
| Pearson correlation | 0.99999895 |
| Official top-10 concentration (normalized) | 54.6091% |
| ETF top-10 concentration (normalized) | 54.6037% |

These are **single-date cross-source calibration metrics**, not out-of-sample validation of a historical proxy. Both sources round individual values to two decimal places. This tiny discrepancy is consistent with rounding; it does not prove the ETF replicates exact index weights every month.

## Sources and provenance

1. **Primary proxy source:** Nippon India Mutual Fund, *Nippon India ETF Nifty 50 BeES — February 2026 Product Note*, portfolio as on 28-Feb-2026; NAV date 27-Feb-2026. [AMC PDF](https://mf.nipponindiaim.com/FundsAndPerformance/ProductNotes/NipponIndia-ETF-Nifty-50-BeES-Feb-2026.pdf). The AMC states its passive approach is to hold NIFTY 50 securities in the same proportion as the index. [AMC archive](https://etf.nipponindiaim.com/home/archives).
2. **Independent reference:** NSE Indices, NIFTY 50 white-paper Exhibit 26, 2026-02-27. Existing project transcription: [official snapshot CSV](../../data/constituent_weekly/nifty50_official_weights_2026-02-27.csv). The published two-decimal weights sum to 100.02%; values were not manually reweighted in the source file.
3. **Secondary historical index:** Fund Tracker India displays monthly AMC portfolio-derived holdings, a 12-month month-end history to September 2026, and identifies Nippon India Mutual Fund monthly portfolio as the underlying source. It is a redisplay/aggregation, not the primary record. [Portfolio page](https://fundtrackerindia.com/scheme/nippon-india-etf-nifty-50-bees).
4. **Disclosure timing framework:** SEBI circular SEBI/HO/IMD/PoD2/P/CIR/2024/183 (31-Dec-2024) changed portfolio disclosure timing for equity passive schemes to within 10 days after each quarter. The circular became effective 16-Mar-2025. [SEBI circular PDF](https://www.sebi.gov.in/legal/circulars/dec-2024/review-of-regulatory-framework-for-passive-schemes-under-mutual-funds_90050.html). This is a minimum disclosure deadline, not proof of the actual publication timestamp of a particular AMC file.
5. **Weight drift:** NSE explains that a market-cap-weighted index is self-weighting between rebalances: relative stock prices move weights, while constituent changes and corporate actions require adjustments. [NSE index FAQ](https://www.nseindia.com/static/products-services/indices-faqs). The NIFTY 50 follows free-float market-cap methodology. [NIFTY 50 methodology](https://www.niftyindices.com/Methodology/Method_Nifty_50.pdf).

## Point-in-time method for a proxy panel

### Snapshot admission

- Retain source period-end, actual publication timestamp (when verifiable), source URL, file hash, scheme, source revision, and acquisition timestamp separately.
- Use a holdings snapshot only after its publication is demonstrably no later than the forecast timestamp.
- If only the period-end date is known, do **not** assume it was available on period-end. For a conservative exploratory fallback, set availability to period-end + 15 calendar days, flag the availability timestamp as imputed, and run sensitivity checks at +10 and +20 days. Do not mix imputed-availability and observed-publication results.
- Equity stock holdings must be normalized to 100% of disclosed equity; cash, debt, derivatives collateral and other non-equity assets are excluded from the denominator and reported separately.
- The ETF portfolio remains a proxy. It may contain cash, tracking differences, rebalancing/trading frictions, sampling, or non-index positions. A portfolio with 51 names or any position not in the point-in-time index universe is not automatically a valid 50-name index basket.

### Daily weight drift between observations

For a holdings snapshot at time \(s\), within a period with unchanged membership, share quantities, IWF and no unresolved corporate action:

\[
\widetilde w_i(t)=w_i(s)\frac{P_i^{adj}(t)}{P_i^{adj}(s)},\qquad
w_i(t)=\frac{\widetilde w_i(t)}{\sum_{j\in U(s)}\widetilde w_j(t)}.
\]

This is the usual market-value drift identity for a fixed-share portfolio. It is not an IWF estimator. Use adjusted price relatives only when corporate-action treatment is documented. Reseed from a later observed holdings snapshot and/or official index event at constituent changes, IWF changes, share-capital changes, mergers, demergers, splits, bonus/rights issues and other relevant corporate actions. Do not carry a stale basket through an unresolved event. Do not add/remove a constituent using a future holdings snapshot.

### Data availability and reporting lags

For periods governed by SEBI's post-16-Mar-2025 equity passive disclosure rule, the outer deadline is ten calendar days after the quarter. Actual publication timestamps should be obtained and stored for every snapshot. A missing timestamp must be labelled as imputed, not observed. Prior to the circular's effective date, the historical regulatory disclosure rule differed; it must be separately versioned and sourced before use. Fund Tracker's displayed monthly series is a discovery aid; monthly values are not automatically available on their month-end date or evidence of what an investor knew at 10:00 on a particular day.

### Rebalance and stale-weight safety

The index has scheduled semi-annual reviews and can also change following corporate actions or other events. The AMC/ETF may trade around the index effective date and may lag it. A proxy panel must be split or reseeded around any known membership/IWF/corporate event. If the correct point-in-time 50-name universe and weights cannot be mapped with at least 98% coverage and at least 47 valid constituents, exclude that cycle; do not renormalize missing weight silently.

## Implementation added

- `scripts/constituent_weekly/weight_proxy.py`: equity-only normalization, fixed-share price drift, and normalized cross-source weight comparison.
- `tests/test_constituent_weekly_weight_proxy.py`: numerical and input-invariant tests (8 tests).
- `C1_ETF_PROXY_CALIBRATION.md`: source, calibration, point-in-time rules and limitations.
- No raw Dhan minute bars, private shareholder records or restricted data are included in this artifact.

## Limitations and next gates

1. This one-date calibration does not establish historical fidelity over 2008–2026.
2. The complete 50-row ETF portfolio and actual first-publication timestamp must be acquired for each historical snapshot. The currently reviewed AMC PDFs establish only isolated dates; a third-party page summarizes 12 recent monthly snapshots but should not substitute for raw AMC evidence.
3. SEBI's equity-passive quarterly disclosure rule after 16-Mar-2025 means one cannot assume monthly availability from the regulation. Any monthly factsheet voluntarily published by the AMC must carry its own actual publication date.
4. ETF tracking deviation, cash/non-equity holdings, securities lending, derivatives and creation/redemption mechanics may make its holdings differ from index weights.
5. Historical membership, IWF/float updates, security identities and corporate actions must be point-in-time resolved; ETF holdings alone do not prove the official index constituents.
6. Basket-to-index realised return reconciliation remains mandatory before confirmatory aggregation. The proxy-based results must be labelled exploratory and shown alongside any official-weight result.

**Decision:** Public-source work has removed the requirement to stop solely because there is no readily available historical official IWF file. It has not passed C1. Proceed with historical holdings acquisition and proxy QA as a bounded exploratory source track; do not yet claim a validated bottom-up NIFTY model or strategy.
