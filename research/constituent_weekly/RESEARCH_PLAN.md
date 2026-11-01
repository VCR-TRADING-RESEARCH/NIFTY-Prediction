# Bottom-Up NIFTY 50 Weekly Expiry Prediction — Pre-Registered Plan

**Track ID:** BUP-01  
**Plan version:** 1.2  
**Registered:** 2026-10-31  
**Status:** Locked for the first bounded research cycle  
**Research branch:** phase/constituent-weekly-outcomes-c0

## 1. Purpose and scope

This is a new research track, separate from the existing index-only NIFTY expiry predictor. Rather than asking a model to infer the weekly NIFTY 50 move mainly from NIFTY history, the system will forecast the weekly expiry outcome of **each stock that was actually a NIFTY 50 constituent at the forecast timestamp**, then aggregate those stock forecasts into a NIFTY 50 forecast.

The existing index-only ExtraTrees pipeline remains an independently reported benchmark. Its latest repository status (run 41145607225, 2026-10-30) has 398 weekly labels and a 318/80 development/holdout split, but the 10:00 anchor is still marked provisional and no executable strategy is certified. These results are benchmark context, not evidence for this new track.

The study covers one weekly cycle: from the first valid 10:00 IST observation on the first NSE session after the preceding verified weekly expiry, through the next verified weekly expiry close. Actual expiry dates and sessions must be exchange-verified, not inferred from a fixed weekday.

No live orders or automated trading are in scope. Prediction quality and trading profitability are separate acceptance decisions.

## 2. Research questions

- **RQ1 — Universe and data:** Can point-in-time NIFTY 50 membership, stable security identifiers, corporate-action mappings and free-float weights be reconstructed for the same historical weekly cycles as the index benchmark?
- **RQ2 — Stock forecasts:** Can information available by 10:00 IST predict each constituent's direction and continuous return through the next weekly expiry, out of sample?
- **RQ3 — Index aggregation:** Do stock-level expected returns, aggregated using point-in-time free-float weights, predict NIFTY weekly expiry direction better than simple breadth, equal-weight aggregation and a matched index-only model?
- **RQ4 — Cross-sectional information:** Do cross-sectional ranks, sector-relative strength, breadth, dispersion, liquidity and signal concentration add information beyond each stock's own history?
- **RQ5 — Dependence and uncertainty:** Does modelling cross-stock dependence improve the calibration and uncertainty interval of the aggregate index forecast compared with an independence assumption?
- **RQ6 — Additional context:** Do point-in-time global-market, India VIX, options, FII/DII, sector, corporate-action and timestamped news variables add value?
- **RQ7 — Robustness and economics:** Does any incremental edge survive the untouched time holdout, volatility/regime splits, source-quality stress and, only if an executable instrument is specified, date-effective Paytm Money costs, spreads, slippage and fills?

## 3. Aim and objectives

**Aim:** Determine whether forecasts of individual NIFTY 50 constituent outcomes can be combined into a more accurate, calibrated and robust weekly-expiry NIFTY 50 forecast than the current index-only approach.

**Objectives:**
1. Build a point-in-time constituent and security master with effective dates, stable identifiers and corporate-action links.
2. Reconstruct the free-float weights known at each forecast timestamp and independently reconcile them with official weightage evidence.
3. Acquire and validate stock-level anchor prices, expiry closes and causal daily lookback data.
4. Construct a constituent-by-expiry panel of continuous returns and UP/DOWN/FLAT labels.
5. Establish stock-level, breadth, equal-weight and free-float-weighted baselines.
6. Fit a small pre-registered set of pooled panel and per-stock benchmark models using chronological training only.
7. Aggregate stock-level expected returns and joint forecast distributions into index-level return and direction predictions.
8. Compare bottom-up forecasts against a matched direct-index benchmark on identical expiry cycles.
9. Quantify calibration, uncertainty, stability, cross-sectional ranking skill and missing-data sensitivity.
10. Publish a complete manuscript, data dictionary, reproducibility artifacts and independent audit decision.

### Pre-registered hypotheses (v1.0)

- **H0-1:** On matched eligible expiry cycles, the bottom-up free-float-weighted forecast does not improve a pre-registered primary index metric over the best simple baseline and matched index-only model by a practically meaningful amount.
- **H1-1:** At least one bounded bottom-up candidate improves that primary metric on the untouched chronological holdout, with uncertainty bounds that support a real incremental effect and no material calibration or robustness failure.
- **H0-2:** Any apparent stock-level predictive skill does not translate into better aggregate NIFTY forecasts after point-in-time weighting and cross-stock dependence are handled.
- **H1-2:** Stock-level forecasts contain incremental cross-sectional information that survives weighting, dependence-aware aggregation and the matched-cycle test.
- **H0-3:** Any directional forecast edge does not survive realistic instrument-specific trading costs, spreads, slippage and fills.
- **H1-3:** A fully specified and independently audited strategy remains net positive after all date-effective costs and conservative execution assumptions.

H1-1/H1-2 are prediction hypotheses. H1-3 is an independent economic hypothesis; prediction success does not imply trading profitability.

## 4. Frozen target and mathematical construction

Let E[t-1] and E[t] be consecutive **verified actual NIFTY 50 weekly option expiry trade dates**. Let D[t] be the first official NSE trading session after E[t-1]. The forecast timestamp is 10:00 IST on D[t].

### 4.1 Index target

- A_N[t]: first valid NIFTY 50 one-minute candle open stamped at or after 10:00 IST and no later than 10:03 IST on D[t].
- C_N[t]: close of the latest valid one-minute NIFTY 50 index candle timestamped from 15:00 through 15:14 IST on E[t], interpreted as a 15:15 expiry proxy. This is not the official 15:30 close; the official daily close may be reported only as a separate sensitivity and must not be mixed with the stock 15:15-proxy target.
- R_N[t] = C_N[t] / A_N[t] - 1.
- Label UP if R_N[t] > 0; DOWN if R_N[t] < 0; exact ties are FLAT and reported separately. No arbitrary deadband is introduced in v1.0.

These semantics match the parent repository's registered weekly target. A future change to the parent target does not silently change this track; it requires a versioned impact assessment.

### 4.2 Point-in-time universe and stock targets

Let U[t] be the set of stocks officially included in NIFTY 50 and effective at the forecast timestamp. Historical membership must be reconstructed from information available by that date. Today's membership must never be applied to earlier years. A symbol is an alias, not a primary key: retain ISIN, exchange security ID, aliases and validity periods.

For each stock i in U[t]:
- A[i,t]: first valid stock one-minute candle open at or after 10:00 IST and no later than 10:03 IST on D[t].
- C[i,t]: close of the latest valid stock one-minute candle timestamped from 15:00 through 15:14 IST on E[t], interpreted as a 15:15 expiry proxy. Record the actual timestamp; exclude later bars.
- R[i,t] = C[i,t] / A[i,t] - 1 after documented mechanical continuity treatment for splits, bonuses, rights, mergers, demergers and security changes.
- Stock label: UP if R[i,t] > 0, DOWN if R[i,t] < 0, exact tie FLAT.

Ordinary dividends are not silently reinvested in the primary price-return target. A separately labelled total-return sensitivity may include them. Unresolved corporate actions invalidate the affected security-cycle for confirmatory evaluation. Missing/invalid prices are excluded with a reason; they are never forward-filled or fabricated.

### 4.3 Weight-based index aggregation

Let w[i,t] be the free-float index weight for stock i reconstructed from membership, market capitalisation, IWF and index methodology information known at or before the 10:00 forecast timestamp.

The primary bottom-up expected-return forecast is:

Rhat_N[t] = sum over i in U[t] of w[i,t] * muhat[i,t]

where muhat[i,t] is the model's forecast of that stock's continuous return. The weights must sum to one over the full point-in-time universe. Missing weight must be reported, not concealed by silent renormalisation.

A forecast of the probability that NIFTY rises must preserve cross-stock dependence, for example with a joint residual-block bootstrap or a factor residual simulation trained only on earlier expiry cycles. The weighted sum of stock UP probabilities, sum(w[i,t] * p[i,t]), is reported as **weighted breadth**, not as P(NIFTY UP). A simple vote is a baseline only.

For realised reconstruction, calculate the weighted constituent basket return and compare it with the official NIFTY price-return move over the same interval. If index divisor adjustments, membership/weight changes or corporate actions occur inside the horizon, replay the official treatment or exclude that cycle from confirmatory aggregation with an explicit reason. Do not hide a mismatch through silent reweighting.

For the primary aggregation gate, an accepted expiry cycle must have at least 98% of point-in-time free-float weight represented at both endpoints and at least 47 valid constituents. Full-coverage and 98%-coverage results are reported separately. The C1 data audit must lock the allowable basket-to-index reconstruction tolerance before any model results are viewed.

## 5. Data requirements and source hierarchy

### 5.1 Mandatory data
- Official weekly expiry trade dates and first-session-after-expiry calendar.
- Point-in-time constituent membership and effective dates.
- Historical free-float weights / IWF with publication or availability timestamps.
- Stable security identifiers and corporate-action/security-history mapping.
- Stock one-minute bars for the 10:00 anchor and expiry close.
- Daily OHLCV for causal stock features, retaining missing volume as missing.
- Official NIFTY 50 price-return index target and matched index-only benchmark.
- Source provenance, access time, hashes, schema versions, row counts and exclusions.

### 5.2 Optional data, only after timestamp validation
- India VIX and constituent/NIFTY options IV, skew, OI and volume as observed before the forecast.
- Sector strength, advance/decline breadth, cross-sectional dispersion and concentration.
- Global equity indices/futures, USD/INR, crude, gold and rates, aligned to information actually available by 10:00 IST.
- FII/DII and participant flows only if the report was released before the forecast; later or revised values are forbidden.
- Corporate announcements, earnings and news only where historical publication timestamps and usage rights exist.

### 5.3 Free-first acquisition
1. NSE official reports: equity UDiFF bhavcopy, security masters, corporate actions, price/volume, NIFTY index history, FII/DII and contract/expiry archives.
2. NSE Indices: methodology, constituent downloads, reconstitution releases, factsheets, monthly reports and index weightage/IWF evidence.
3. BSE public records as a cross-check where appropriate; not as an un-reconciled substitute for NSE price records.
4. Open GitHub, Kaggle, Hugging Face, Zenodo and published research datasets after provenance, survivorship, adjustment, timezone, coverage and licence checks.
5. The already-subscribed Dhan API for missing intraday/equity data, using secrets only in GitHub Actions and sanitized diagnostics.
6. Hugging Face token as an optional download accelerator, not an exclusive or preferred source.
7. Consider other paid sources only after documented free-source and configured Dhan tests fail.

Composite datasets are allowed only after timestamps, identifiers, OHLC definitions, adjustment policies and conflicting values are reconciled. Preserve source-native values and row-level provenance; never overwrite raw source values with a preferred value.

### 5.4 Historical membership and weights — hard data gate

Candidate membership sources include official NSE Indices circulars and public reconstruction projects. The public BKKB20/nse-index-history repository claims 2004–2026 coverage but documents three unprocessed scanned circulars from 2018–2019 and pre-2010 mapping limitations; it is a candidate reconstruction, not official ground truth. The vishalvx/nifty-indices-datasets repository describes binary membership rather than numeric free-float weights; it can be a list cross-check but cannot supply primary weights.

Numeric aggregation must use official point-in-time weight/IWF evidence or an auditable reconstruction checked against official monthly/daily weight reports. Equal weights, binary membership and present-day weights are not substitutes.

### 5.5 Caching and security

- Cache immutable inputs by source, security identifier, date range and schema/version; retain SHA-256 and retrieval time.
- Dhan intraday requests must be chunked to at most 90 days; retain only validated compact datasets/manifests in the repository and large raw inputs in Actions cache/artifacts subject to rights.
- Historical inactive/delisted constituents need a separate coverage test; active-instrument history claims do not prove data availability for removed securities.
- Never commit or log Dhan tokens, client IDs, PINs, TOTP seeds, API keys or sensitive auth payloads.
- Fail closed on authentication or data failure. Never reuse a stale successful prediction for a failed current request.

## 4.4 Public ETF portfolio holdings proxy (version 1.2 amendment)

Where a complete historical official constituent-weight/IWF series cannot be obtained from the available public sources, BUP-01 may run a separately reported **ETF-replica proxy** track using published holdings of Nippon India ETF Nifty 50 BeES. This is an exploratory fallback, not a relabelling of ETF holdings as official NIFTY 50 weights or IWF. The original official-weight confirmatory track remains separately identified wherever official data are available.

The AMC describes a passive replication objective: hold the securities constituting NIFTY 50 in the same proportion as the index. A one-date calibration against an NSE Indices white-paper snapshot on 2026-02-27 matched 50/50 stocks. After independently normalising equity holdings to 100% and excluding 0.08% cash, mean absolute difference was 0.002214 percentage points, RMSE 0.003204 points, maximum absolute difference 0.008967 points and Pearson correlation 0.99999895. This single-date result is calibration only; it is not evidence of historic accuracy or exact daily replication.

Rules for the proxy track:
1. Keep source snapshot date, actual publication timestamp, period end, scheme, source URL, source hash, acquisition timestamp and source method in separate fields. A portfolio period-end date is not its publication date.
2. Normalize only constituent equity holdings to 100%. Exclude cash, debt, collateral and non-equity assets from the equity denominator, and report their share of NAV separately. Do not treat an ETF position outside the point-in-time NIFTY universe as an index constituent.
3. Use a snapshot only when it was published by the forecast timestamp. If an exact public publication timestamp is unavailable, use period-end + 15 calendar days as an explicitly imputed conservative availability proxy and report +10/+20 day sensitivities. Never use a not-yet-disclosed quarter/month snapshot.
4. Between observed snapshots, weights may be drifted using the fixed-share basket identity: prior normalized equity weight multiplied by the stock's adjusted price relative, then renormalized over the unchanged universe. This is valid only while share quantities, IWF, membership and corporate-action status are unchanged. It is not an IWF calculation.
5. Reseed after every known NIFTY constituent change, IWF/free-float update, share-capital change or corporate action. Use dated official index notices and corporate-action/ISIN records. If event effective date, new stock weight or security continuity is unresolved, exclude the affected cycle rather than carrying stale weights or using a future snapshot.
6. SEBI Circular SEBI/HO/IMD/PoD2/P/CIR/2024/183 changed equity passive-scheme portfolio disclosure to within 10 days after each quarter, effective 2025-03-16. Do not assume monthly snapshots were legally required after that date; a voluntary monthly factsheet may be used only with its own verifiable publication timestamp. Prior periods require their then-applicable disclosure rule and source evidence.
7. Maintain an explicit ETF tracking-difference, cash, trading, replication, corporate-action and stale-snapshot risk register. Proxy output must be labelled ETF-replica or ETF-holdings-derived, never official NIFTY IWF.
8. Official weights, ETF proxy weights and reconstructed/provisional weights must be stored in separate source classes and tested side by side. Missing weight is never silently renormalized away. For any admitted cycle maintain at least 98% point-in-time weight coverage and at least 47 valid constituents.

Proxy-track acceptance is a bounded, exploratory C1 sub-gate: complete point-in-time holdings/membership/security identity for the relevant cycles, leakage-safe availability timestamps, action-adjusted price drift, and matched-cycle basket-vs-index reconciliation must pass before C2 exploratory modelling. The original confirmatory C1 gate still requires official methodology/weight reconciliation. Results from proxy and confirmatory tracks must never be pooled without an explicit sensitivity analysis.

## 6. Causal feature families

Every feature must be available by 10:00 IST. The 10:00 bar's open may be used as the anchor; its later high, low, close and volume must not enter the feature row. All transforms and cross-sectional ranks are fit within training folds.

**Own-stock price/volume:** prior 1/5/10/20/60-session returns; overnight gap; pre-anchor morning return; realised volatility; range/ATR; distance to rolling high/low; turnover/volume surprise; trend and reversal features.

**Cross-sectional:** point-in-time cross-sectional ranks; sector-relative strength; stock return versus sector peers; breadth and advance-decline; weighted/equal-weight breadth; return dispersion; forecast concentration. Use only then-current constituents and available observations.

**Sector/global:** sector returns, prior US/European/Asian returns, USD/INR, crude, gold and rates. Respect local close times, holidays and daylight-saving shifts. The primary stock model excludes NIFTY index prices to preserve the bottom-up question; a secondary ablation may add market context.

**Volatility/options:** India VIX and historical volatility; observed option IV, skew, OI and volume only where point-in-time archive coverage exists. Do not label reconstructed data as observed historical options data.

**Events/flows:** corporate actions, earnings, timestamped news and FII/DII only if genuine point-in-time data is available. These are optional and do not block the core price-based test.

## 7. Bounded models and aggregation candidates

The primary design is a **pooled stock panel model**, since each individual stock has limited weekly observations. All stock rows from one expiry cycle stay together in a fold.

Stock candidates:
1. Expanding stock-specific UP frequency / majority, own-stock momentum and prior-cycle sign baselines.
2. Pooled regularised logistic regression for stock direction.
3. Pooled regularised regression for continuous stock return.
4. Constrained ExtraTrees as a repository tree reference.
5. One constrained boosting candidate (HistGradientBoosting or equivalent).
6. A small forecast ensemble only if development results justify it.

Per-stock/sector-specific models are secondary and require a pre-fixed minimum history. Large neural models are not introduced merely because they are available.

Index aggregators:
- Equal-weight stock expected return.
- Point-in-time free-float-weighted expected return (primary).
- Weighted breadth, median and trimmed-mean diagnostics.
- Joint residual-block bootstrap / factor residual simulation for an index return distribution and P(NIFTY UP).
- A small index-level calibrator only if sufficient development cycles exist and it is trained strictly on earlier out-of-fold bottom-up forecasts.

Direct benchmarks:
- Expanding NIFTY UP frequency/majority.
- Prior NIFTY cycle sign and pre-anchor NIFTY momentum.
- Matched direct-index ExtraTrees on the same accepted cycles and price target.
- Existing parent ExtraTrees results only as context when timestamps/source definitions differ.

Research tools may be used only after the data gate: Quantevolve for bounded rule proposals; TradingAgents for hypothesis review; AstraQuant for architecture/risk-control ideas; PySR for constrained symbolic features; arch for volatility; tick for optional microstructure; MAPIE for time-series uncertainty only after coverage assumptions are tested. No listed tool is presumed to work or produce a profitable signal.

## 8. Validation and statistics

- The expiry cycle is the indivisible time unit. Every stock row from one cycle remains in the same fold. Never randomly split stocks across train/test.
- Use chronological expanding walk-forward validation; target at least 104 prior eligible weekly cycles for the first confirmatory forecast. Reduced-history results are exploratory and labelled as such.
- Freeze eligible cycles, source hashes and the final chronological holdout before model fitting. The last 20% of eligible cycles after C1 data filtering is the untouched holdout; store its boundary before model comparison.
- All imputation, scaling, feature selection, ranks/transforms, fitting, hyperparameter selection and probability calibration occur inside the training fold.
- Keep all candidates, failures and deferred tests in an experiment registry. Do not reopen or tune the untouched holdout after first evaluation.
- Stock metrics: balanced accuracy, MCC, ROC-AUC where defined, Brier score, log loss, precision/recall, calibration and per-cycle cross-sectional Spearman rank IC.
- Index metrics: accuracy, balanced accuracy, MCC, ROC-AUC where defined, Brier/log loss, calibration, return MAE/RMSE, directional hit rate, interval coverage and abstention rate.
- Use matched expiry dates for paired comparisons. Uncertainty: moving-block bootstrap over expiry cycles, four-cycle blocks, 2,000 replicates, fixed seed 20261031, retaining all stocks per sampled cycle. Any change to block length requires a plan-version change before holdout inspection.
- Apply Holm family-wise adjustment (or a pre-registered alternative) to exploratory comparisons. Report all candidates.
- Robustness: high/low VIX and realised volatility; trend/range/bear regimes; sector and signal concentration; pre/post expiry weekday change; major calendar regimes; weight coverage; corporate-action exclusions; alternate sources; delayed execution.
- Do not use IID standard errors on a pooled stock panel without clustering by expiry cycle and accounting for cross-stock dependence.

## 9. Trading and transaction-cost gate

Forecast quality is not trading P&L. Any later NIFTY options/futures strategy must specify contract, expiry, strike/structure, entry/exit times, lot sizes, order type, position sizing and fill assumptions. Apply date-effective Paytm Money brokerage, exchange fees, STT, GST, stamp duty, SEBI/regulatory charges, bid/ask spread, impact, slippage, lot-size changes and entry/exit costs. Missing cost data means BLOCKED, never zero. Direct stock-basket simulations must include constituent-level brokerage, levies, spread/impact, turnover and corporate-action cash flows. No orders are placed in this research.

## 10. Phases, branches and gates

Each phase has its own branch. Update status and logs after every phase step. The plan itself remains locked; substantive changes require plan v1.1 or later, dated rationale and an impact assessment.

| Phase | Planned branch | Deliverables | Acceptance gate |
|---|---|---|---|
| C0 — Registration/governance | phase/constituent-weekly-outcomes-c0 | Locked plan, questions, sources, literature, status/logs, tests and workflow | Governance files committed; structural checks pass |
| C1 — Point-in-time universe/data audit | phase/constituent-weekly-outcomes-c1-data | Membership/security master, corporate actions, official weights/IWF where available, ETF holdings proxy and source manifest | For confirmatory track: official weights reconciled. For exploratory proxy track: published holdings point-in-time validated, 98% weight coverage, dated membership/actions pass and weighted basket reconstruction within frozen tolerance |
| C2 — Panel labels/features | phase/constituent-weekly-outcomes-c2-panel | Stock-cycle panel, index targets, causal features, hashes, frozen split and tests | No duplicate security-cycle, future leakage, identifier/action errors; exclusions documented |
| C3 — Stock models/baselines | phase/constituent-weekly-outcomes-c3-models | Walk-forward stock forecasts, baselines, experiment registry and metrics | Pre-registered candidates; comparison with baselines and clustered uncertainty; holdout sealed |
| C4 — Index aggregation/uncertainty | phase/constituent-weekly-outcomes-c4-aggregation | Weighted expected-return forecast, joint probability, benchmark results, calibration and robustness charts | Matched-cycle bottom-up comparison; improvement with evidence or explicit negative/inconclusive result |
| C5 — Economic/execution gate | phase/constituent-weekly-outcomes-c5-costs | Instrument specification, dated fees, fills, slippage and net P&L if feasible | Verified cost-adjusted positive result required for strategy claim; otherwise BLOCKED/no strategy |
| C6 — Manuscript/independent audit | phase/constituent-weekly-outcomes-c6-audit | Full manuscript, figures/tables, appendices, supplements, independent mathematical and repository audit | Reproducible claims; errors, exclusions and gate outcomes disclosed |

## 11. Stop rules

1. Stop confirmatory C1 if official point-in-time membership/weights cannot be independently established. The separately labelled ETF-replica proxy track may proceed through its own exploratory gate using public disclosed holdings, but only with point-in-time availability, event handling, 98% weight coverage and basket reconciliation. Do not fabricate proxies or merge them with official results.
2. Stop confirmatory aggregation if the realised weighted constituent basket does not reconcile with official NIFTY under the tolerance frozen before modelling.
3. Do not train on a panel with future membership, unresolved security mapping, non-causal features or unhandled corporate actions.
4. Do not retune on the final holdout. No unbounded model or strategy search beyond the candidates above.
5. End after C6 or at a documented BLOCKED gate. Negative or inconclusive results are valid completion outcomes.
6. A validated directional forecast requires meaningful improvement over matched direct-index and simple baselines on the untouched holdout, uncertainty evidence, calibration and robustness. A usable trading strategy additionally requires executable fills and net profitability after verified costs. Neither is assumed.

## 12. Final manuscript requirements

The final manuscript must contain abstract; introduction; research questions and hypotheses; extensive literature review; data and provenance; point-in-time universe/membership; formal target and mathematical aggregation; scientific methodology; model/feature specifications; statistical analysis; results with tables/charts; inferences and discussion; robustness; strengths; limitations; conclusion; future directions; references; appendices and supplements.

Appendices include security aliases, membership/weight snapshots, corporate-action exclusions, source manifests/hashes, feature dictionary/availability timestamps, model configs, fold schedule, candidate registry, costs/fills, audit tests and machine-readable results. Never fabricate results, p-values, figures or source coverage.

## 13. Prior research lessons and mandatory checks

Before each phase, reread parent README, operating rules, registered parent plan, literature/source registers, research and error logs, latest summary/manuscript, and this track's status/logs. Known mistakes that must not recur:
- A successful workflow is not proof of data validity or profitability.
- Do not compare a source to values overwritten by that same source.
- A duplicate download/read is not independent validation.
- Do not infer expiries from one weekday; verify the actual expiry contracts and holiday shifts.
- Do not use current constituents or current weights for past dates.
- Do not use binary/equal-weight membership as a free-float weight series.
- Do not couple official sessions to broker data coverage.
- Do not reuse stale cache chunks without provenance/targeted refresh or publish stale results after failures.
- Do not call a raw score a calibrated probability.
- Do not claim an unrun/failed research tool produced results.
- Include all date-specific brokerage/levies, GST, STT, stamp duty, spread, slippage, lot sizes and fills in strategy P&L.

Visible user conversations and decisions may be logged; hidden private chain-of-thought is not copied. Use auditable summaries and reproducible rationales instead.

## 14. Registration status

At registration, C0 is active; C1–C6 are pending. No constituent panel has been built, no stock model has been trained and no bottom-up prediction result exists. The next empirical decision is the point-in-time data/weight feasibility audit, not model selection.


## Version history and controlled amendment

- **v1.0 — 2026-10-31:** Original pre-registered scope, targets, hypotheses, validation plan and acceptance gates.
- **v1.1 — 2026-11-01:** User-directed expiry convention change. For both stock constituents and the NIFTY 50 index outcome, use the close of the latest valid one-minute candle whose timestamp is within 15:00–15:14 IST on the expiry session, label it the 15:15 expiry proxy, and store the actual timestamp. It is not the official 15:30 close. A 15:30 index close may be shown only as a separate sensitivity and cannot be mixed into the primary stock/index target. This replaces the earlier 15:25–15:29 stock-bar requirement. No other research question, hypothesis, entry time, feature policy, fold design or acceptance threshold is changed by this amendment.
