# Bottom-Up NIFTY 50 Weekly Expiry Prediction — Pre-Registered Plan

**Track ID:** BUP-01  
**Plan version:** 1.4  
**Registered:** 2026-10-31  
**Status:** Locked after user-directed v1.3 aggregation-scope amendment; first bounded research cycle  
**Research branch:** phase/constituent-weekly-outcomes-c0

## 1. Purpose and scope

This is a new research track, separate from the existing index-only NIFTY expiry predictor. Rather than asking a model to infer the weekly NIFTY 50 move mainly from NIFTY history, the system will forecast the weekly expiry outcome of **each stock that was actually a NIFTY 50 constituent at the forecast timestamp**, then aggregate those stock forecasts into a NIFTY 50 forecast.

The existing index-only ExtraTrees pipeline remains an independently reported benchmark. Its latest repository status (run 41145607225, 2026-10-30) has 398 weekly labels and a 318/80 development/holdout split, but the 10:00 anchor is still marked provisional and no executable strategy is certified. These results are benchmark context, not evidence for this new track.

The study covers one weekly cycle: from the first valid 10:00 IST observation on the first NSE session after the preceding verified weekly expiry, through the next verified weekly expiry close. Actual expiry dates and sessions must be exchange-verified, not inferred from a fixed weekday. The primary index outcome is the observed NIFTY 50 index return over this interval. Constituent forecasts predict that observed index label; an equal-weight stock basket is never substituted for the index.

No live orders or automated trading are in scope. Prediction quality and trading profitability are separate acceptance decisions.

## 2. Research questions

- **RQ1 — Universe and data:** Can point-in-time NIFTY 50 membership, stable security identifiers, dated aliases and corporate-action continuity be reconstructed for the same historical weekly cycles as the index target, with adequate constituent price coverage?
- **RQ2 — Stock forecasts:** Can information available by 10:00 IST predict each eligible constituent's direction and continuous return through the next weekly expiry, out of sample?
- **RQ3 — Index direction from constituents:** Do strictly out-of-fold stock forecast probabilities, predicted returns, cross-sectional breadth, dispersion and sector summaries predict the observed NIFTY 50 weekly-expiry direction beyond simple historical/breadth baselines?
- **RQ4 — Cross-sectional information:** Do point-in-time cross-sectional ranks, sector-relative strength, breadth, dispersion, liquidity and forecast concentration add information beyond each stock's own history?
- **RQ5 — Dependence and uncertainty:** Does preserving cycle-level cross-stock dependence improve calibration and uncertainty for the index-direction meta-model compared with treating stock rows as independent?
- **RQ6 — Additional context:** Do point-in-time global-market, India VIX, options, FII/DII, sector, corporate-action and timestamped news variables add value?
- **RQ7 — Robustness and economics:** Does any incremental prediction edge survive the untouched time holdout, volatility/regime splits, source-quality stress and, only if an executable instrument is specified, date-effective Paytm Money costs, spreads, slippage and fills?

**Scope decision (v1.3):** The user directed that no ETF-holdings-versus-index-weight comparison is needed. This research will not acquire ETF portfolio weights to reconstruct or compare against official NIFTY weights, and it will not require point-in-time free-float IWF as a model input. It will use point-in-time constituent membership and security identity, stock outcomes, and an unweighted cross-sectional forecast-signal aggregator. The actual NIFTY 50 index series remains the index target label.


## 3. Aim and objectives

**Aim:** Determine whether forecasts of individual NIFTY 50 constituent outcomes can be combined into a more accurate, calibrated and robust weekly-expiry NIFTY 50 forecast than the current index-only approach.

**Objectives:**
1. Build a point-in-time constituent and security master with effective dates, stable identifiers and corporate-action links.
2. Establish point-in-time membership, stable security IDs, aliases and corporate-action continuity for every eligible constituent cycle.
3. Acquire and validate stock-level anchor prices, expiry closes and causal daily lookback data.
4. Construct a constituent-by-expiry panel of continuous returns and UP/DOWN/FLAT labels.
5. Establish stock-level baselines and unweighted cross-sectional breadth/forecast-summary baselines.
6. Fit a small pre-registered set of pooled panel and per-stock benchmark models using chronological training only.
7. Convert strictly out-of-fold constituent predictions into cycle-level breadth, dispersion, sector and forecast-summary features; fit a chronological index-direction meta-model against the observed NIFTY label.
8. Compare the bottom-up forecast-signal model with simple NIFTY historical/breadth baselines and the matched direct-index benchmark on identical expiry cycles.
9. Quantify calibration, uncertainty, stability, cross-sectional ranking skill and missing-data sensitivity.
10. Publish a complete manuscript, data dictionary, reproducibility artifacts and independent audit decision.

### Pre-registered hypotheses (v1.0)

- **H0-1:** On matched eligible expiry cycles, the bottom-up out-of-fold forecast-signal meta-model does not improve a pre-registered primary index metric over the best simple/breadth baseline and matched index-only model by a practically meaningful amount.
- **H1-1:** The pre-registered unweighted constituent forecast-signal meta-model improves that primary metric on the untouched chronological holdout, with uncertainty bounds that support a real incremental effect and no material calibration or robustness failure.
- **H0-2:** Any apparent stock-level predictive skill does not translate into better NIFTY direction forecasts after cycle-level aggregation and cross-stock dependence are handled.
- **H1-2:** Stock-level forecasts contain incremental cross-sectional information that survives out-of-fold breadth/dispersion aggregation, dependence-aware validation and the matched-cycle test.
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

### 4.3 Unweighted forecast-signal aggregation (v1.3)

No constituent free-float weights, ETF portfolio weights or weight-reconstruction series are required or used in this v1.3 track. The actual NIFTY 50 index return remains the observed target from Section 4.1. The stock forecasts are predictors of that target, not a synthetic reconstruction of the index return.

For each point-in-time tradable constituent i in U[t], the pooled stock model emits:
- p[i,t] = P(stock i is UP through expiry | information available by 10:00 IST);
- mu[i,t] = forecast continuous stock price return through the expiry proxy;
- every p[i,t] and mu[i,t] used in the index model must be generated strictly out of fold. The model generating a row must not have trained on that row, any stock row from the same expiry cycle, or any later cycle.

For each expiry cycle, construct a fixed, pre-registered, unweighted summary vector S[t]:
- mean and median of p[i,t];
- unweighted predicted breadth B[t] = valid_count^(-1) * sum_i 1(p[i,t] > 0.5);
- mean, median and 10%-trimmed mean of mu[i,t];
- cross-sectional dispersion of p[i,t] and mu[i,t];
- sector-wise predicted breadth and dispersion of sector summaries;
- forecast concentration (for example, the top-decile share of absolute predicted signal);
- valid constituent forecast count and valid_count / point-in-time tradable member count.

The primary NIFTY direction meta-model is a regularised logistic model:
P(NIFTY UP[t] | S[t]) = g[t](S[t])
where g[t] is fitted only on earlier expiry cycles whose constituent inputs are themselves out-of-fold. A bounded tree model may be evaluated as a secondary pre-registered candidate. Calibration is chronological and uses only earlier cycles. The meta-model predicts the observed NIFTY target label; it does not infer index weights.

The unweighted mean/median/trimmed mean of mu[i,t] may be shown as an **equal-weighted constituent-basket diagnostic only**. It must never be called the NIFTY 50 index return, an official index forecast return, or a substitute for the observed NIFTY index target.

For an accepted cycle, require at least 47 valid tradable constituent forecasts and at least 94% of that cycle's point-in-time tradable member count. Missing stock predictions are reported with reasons; they are never forward-filled, fabricated or silently imputed. The NIFTY target itself must also be valid under Section 4.1.

Cross-stock dependence is preserved by keeping every stock row from an expiry cycle together in each fold and by resampling whole expiry cycles (all constituent rows and their index label together) for uncertainty. A simple majority vote or average probability is a feature/baseline only, not automatically P(NIFTY UP).


## 5. Data requirements and source hierarchy

### 5.1 Mandatory data
- Verified actual weekly expiry trade dates and the first official NSE session after each preceding expiry.
- Point-in-time tradable NIFTY 50 constituent membership and effective dates.
- Stable ISIN/security IDs, dated trading-symbol aliases and corporate-action/security-history mapping.
- Stock one-minute bars for the 10:00 anchor and 15:00–15:14 expiry proxy.
- Daily OHLCV for causal stock features, retaining missing volume as missing.
- The observed NIFTY 50 index 10:00 anchor and 15:00–15:14 expiry-proxy candle used to form the index target label.
- Source provenance, access time, hashes/manifests, schema versions, row counts, missing-cycle counts and exclusions.

Historical index free-float weights, ETF portfolio weights and official-versus-ETF weight comparison are **not mandatory inputs** to v1.3.


### 5.2 Optional data, only after timestamp validation
- India VIX and constituent/NIFTY options IV, skew, OI and volume as observed before the forecast.
- Sector strength, advance/decline breadth, cross-sectional dispersion and concentration.
- Global equity indices/futures, USD/INR, crude, gold and rates, aligned to information actually available by 10:00 IST.
- FII/DII and participant flows only if the report was released before the forecast; later or revised values are forbidden.
- Corporate announcements, earnings and news only where historical publication timestamps and usage rights exist.

### 5.3 Free-first acquisition
1. Use licensed/user-entitled Dhan API data for constituent and index intraday OHLCV where the subscription and data terms permit the intended internal research use. Keep credentials in GitHub Actions secrets and diagnostics sanitized.
2. Use the CC BY 4.0 point-in-time membership subset already cached in the repository, with its attribution and source hash, and refresh later membership events from independently accessible, rights-permitted source material.
3. Use open GitHub, Kaggle, Hugging Face, Zenodo and published research datasets for security metadata, sector labels, corporate actions and feature context only after provenance, coverage, survivorship, timezone, adjustment and licence checks.
4. Use exchange publications for expiry dates, membership changes and corporate-action identity only through access and use paths permitted by their terms; do not automate restricted scraping or bulk extraction.
5. Use Yahoo or other public EOD data only as a separately labelled diagnostic if terms and point-in-time availability permit; never merge conflicting prices without row-level provenance and a frozen source-selection rule.
6. Use the Hugging Face token only as a download accelerator for datasets with suitable reuse rights; it does not grant rights to upstream financial data.
7. Consider additional paid sources only after documented free-source and configured Dhan tests fail.

The primary v1.3 model does not need ETF portfolio holdings, index weight series, official IWF or reconstructed free-float factors. Do not download or compare those series for this track. Composite datasets are allowed only after timestamps, identifiers, OHLC definitions, adjustment policies and conflicting values are reconciled. Preserve source-native values and row-level provenance; never overwrite raw source values with a preferred value.


### 5.4 Historical membership and security identity — hard data gate

The primary dataset is a point-in-time tradable-member panel, not a weight table. Use the cached NIFTY 50 membership intervals from the CC BY 4.0 source with attribution and documented confidence. The project has reconciled the tradable member set over 103 month-ends from 2018-04 to 2026-10; preserve the symbol normalization rules, including TATAMOTORS/TMPV and the non-tradable DUMMYTATAM placeholder. The upstream public membership table itself has no numeric weights and is used only for dated membership.

A symbol is an alias, not a primary key. Retain ISIN, exchange/security ID, aliases, effective-from/to dates, issuer events and corporate-action references. Historical HDFC Ltd remains a distinct security before its merger; do not replace its price history with HDFCBANK. Do not stitch TATAMOTORS/TMPV across the demerger without a documented action-adjustment rule. Unresolved security identity or corporate actions invalidate the affected stock-cycle.

Confirmatory membership history starts 2018-04-01 for membership confidence; however, intraday target coverage may define a shorter usable period. Dhan documents up to five years of one-minute data for active instruments and a maximum 90-day request window. The actual continuous coverage boundary must be measured rather than assumed. The confirmatory model period begins only at the earliest date for which full point-in-time membership, required stock anchor/expiry proxies, observed NIFTY index target and identifier/action checks pass.

No external weight comparison or ETF-weight substitution is required.


### 5.5 Caching and security

- Cache immutable inputs by source, security identifier, date range and schema/version; retain SHA-256 and retrieval time.
- Dhan intraday requests must be chunked to at most 90 days; retain only validated compact datasets/manifests in the repository and large raw inputs in Actions cache/artifacts subject to rights.
- Historical inactive/delisted constituents need a separate coverage test; active-instrument history claims do not prove data availability for removed securities.
- Never commit or log Dhan tokens, client IDs, PINs, TOTP seeds, API keys or sensitive auth payloads.
- Fail closed on authentication or data failure. Never reuse a stale successful prediction for a failed current request.

### 5.6 ETF and historical index-weight sources excluded from v1.3

On 2026-11-01, the user instructed: “No comparison needed”. Accordingly, v1.3 does not acquire ETF holdings to compare against official NIFTY weights, does not use ETF portfolio weights as NIFTY IWF, and does not require official numerical weight histories. The prior v1.2 proxy calibration and source discovery notes remain in the audit trail as historical work only; they are not inputs, acceptance gates or claims in v1.3.

The Nippon AMC site terms prohibit unauthorized aggregation/copying and require prior written consent for reuse of proprietary content. Third-party portfolio aggregators and datasets were reviewed; no clearly reusable licence for bulk historical holdings ingestion into this trading research was established. No further bulk ETF holdings download is authorized in this track. The monthly AMC schema probes are discovery-only and no underlying holding values were admitted.

All v1.3 index predictions must be trained on point-in-time constituent forecast summaries and evaluated against the observed NIFTY index target. An equal-weight constituent-basket statistic remains a diagnostic feature; it is not an index return.


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

Index-direction aggregation candidates (no external weights):
- **Primary:** regularised logistic meta-model trained on cycle-level, strictly out-of-fold stock probabilities/returns and pre-registered cross-sectional summary features.
- **Unweighted diagnostics:** fraction of constituents predicted UP, mean/median predicted UP probability, mean/median/10%-trimmed mean predicted return, cross-sectional dispersion and sector breadth.
- **Missing-data controls:** include valid member count and fraction; no silent imputation or renormalisation. Require at least 47 valid forecasts and ≥94% of that cycle's point-in-time tradable constituents.
- **Uncertainty:** moving-block bootstrap over complete expiry cycles, retaining all stock rows and the index label for each sampled cycle.
- A secondary tree meta-model may be run only if development sample size and pre-registered capacity allow it.
- The average constituent forecast is not interpreted as an exact NIFTY index return.


Direct benchmarks:
- Expanding NIFTY UP frequency/majority.
- Prior NIFTY cycle sign and pre-anchor NIFTY momentum.
- Matched direct-index ExtraTrees on the same accepted cycles and price target.
- Existing parent ExtraTrees results only as context when timestamps/source definitions differ.

Research tools may be used only after the data gate: Quantevolve for bounded rule proposals; TradingAgents for hypothesis review; AstraQuant for architecture/risk-control ideas; PySR for constrained symbolic features; arch for volatility; tick for optional microstructure; MAPIE for time-series uncertainty only after coverage assumptions are tested. No listed tool is presumed to work or produce a profitable signal.

## 8. Validation and statistics

- The expiry cycle is the indivisible time unit. Every stock row from one cycle remains in the same fold. Never randomly split stocks across train/test. Generate stock predictions out of fold and freeze one forecast-summary row per cycle before fitting the NIFTY meta-model.
- Use chronological expanding walk-forward validation; target at least 104 prior eligible weekly cycles for the first confirmatory forecast. Reduced-history results are exploratory and labelled as such. Require at least 47 valid tradable constituent forecasts and ≥94% member coverage on each accepted cycle, and valid observed NIFTY target labels for at least 98% of scheduled eligible expiry cycles.
- Freeze eligible cycles, source hashes and the final chronological holdout before model fitting. The last 20% of eligible cycles after C1 data filtering is the untouched holdout; store its boundary before model comparison.
- All imputation, scaling, feature selection, ranks/transforms, fitting, hyperparameter selection and probability calibration occur inside the training fold.
- Keep all candidates, failures and deferred tests in an experiment registry. Do not reopen or tune the untouched holdout after first evaluation.
- Stock metrics: balanced accuracy, MCC, ROC-AUC where defined, Brier score, log loss, precision/recall, calibration and per-cycle cross-sectional Spearman rank IC.
- Index metrics: accuracy, balanced accuracy, MCC, ROC-AUC where defined, Brier/log loss, calibration, return MAE/RMSE, directional hit rate, interval coverage and abstention rate.
- Use matched expiry dates for paired comparisons between the bottom-up signal meta-model, simple/breadth baselines and the direct-index benchmark. Uncertainty: moving-block bootstrap over expiry cycles, four-cycle blocks, 2,000 replicates, fixed seed 20261031, retaining all stocks and the NIFTY label per sampled cycle. Any change to block length requires a plan-version change before holdout inspection.
- Apply Holm family-wise adjustment (or a pre-registered alternative) to exploratory comparisons. Report all candidates.
- Robustness: high/low VIX and realised volatility; trend/range/bear regimes; sector and signal concentration; pre/post expiry weekday change; major calendar regimes; constituent-count coverage and missingness; corporate-action exclusions; alternate price sources; delayed execution.
- Do not use IID standard errors on a pooled stock panel without clustering by expiry cycle and accounting for cross-stock dependence.

## 9. Trading and transaction-cost gate

Forecast quality is not trading P&L. Any later NIFTY options/futures strategy must specify contract, expiry, strike/structure, entry/exit times, lot sizes, order type, position sizing and fill assumptions. Apply date-effective Paytm Money brokerage, exchange fees, STT, GST, stamp duty, SEBI/regulatory charges, bid/ask spread, impact, slippage, lot-size changes and entry/exit costs. Missing cost data means BLOCKED, never zero. Direct stock-basket simulations must include constituent-level brokerage, levies, spread/impact, turnover and corporate-action cash flows. No orders are placed in this research.

## 10. Phases, branches and gates

Each phase has its own branch. Update status and logs after every phase step. The registered confirmatory method may change only through a versioned amendment with dated user direction/rationale and a documented impact assessment. Plan v1.4 preserves all confirmatory gates and adds one bounded exploratory exception (C3-X) that does not waive C1/C2 acceptance.

| Phase | Planned branch | Deliverables | Acceptance gate |
|---|---|---|---|
| C0 — Registration/governance | phase/constituent-weekly-outcomes-c0 | Locked plan, questions, sources, literature, status/logs, tests and workflow | Governance files committed; structural checks pass |
| C1 — Point-in-time universe/data audit | phase/constituent-weekly-outcomes-c1-data | Membership/security master, identity/action ledger, 90-day chunk coverage report for stock and NIFTY index candles, source manifests and exclusion ledger | Dated member/security identity passes; confirmatory period fixed only where continuous stock anchor/expiry proxies and NIFTY target are present; ≥47/94% valid stocks per accepted cycle; ≥98% valid NIFTY labels across scheduled eligible cycles |
| C2 — Panel labels/features | phase/constituent-weekly-outcomes-c2-panel | Confirmatory stock-cycle panel, observed NIFTY targets, causal features, OOF split design, hashes and tests | Full C1 gate passed; no unresolved identity/action gaps, future leakage or fabricated member forecasts |
| C3-X — Bounded exploratory prediction tests (new v1.4 exception) | phase/constituent-weekly-outcomes-c3-exploratory | Encrypted ephemeral feature cache; causal stock-cycle features; pooled Logistic/ExtraTrees stock tests; OOF constituent-signal NIFTY test; sanitized metrics and error log | Exploratory only; use cycles that pass the already measured target-coverage and 47/94% member thresholds after known structural-event exclusions; minimum 104 prior eligible cycles for first stock forecast; whole-cycle chronology; no raw bars in repo/artifacts; no final model/strategy claims |
| C3 — Confirmatory stock models/baselines | phase/constituent-weekly-outcomes-c3-models | Confirmatory walk-forward stock forecasts, strictly OOF per-cycle forecast summaries, experiment registry and metrics | Only after C1 and C2 pass; untouched chronological holdout and registered statistical tests |
| C3 — Stock models/baselines | phase/constituent-weekly-outcomes-c3-models | Walk-forward stock forecasts, strictly OOF per-cycle forecast summaries, experiment registry and metrics | Pre-registered candidates; chronological and cycle-clustered uncertainty; holdout sealed |
| C4 — Index aggregation/uncertainty | phase/constituent-weekly-outcomes-c4-aggregation | Unweighted breadth/dispersion feature panel, calibrated NIFTY-direction meta-model, benchmark metrics and robustness charts | Only OOF stock summaries feed the meta-model; NIFTY target is actual observed index label; no equal-weight basket is represented as NIFTY return |
| C5 — Economic/execution gate | phase/constituent-weekly-outcomes-c5-costs | Instrument specification, date-effective fees, fills, slippage and net P&L if feasible | Verified cost-adjusted positive result required for strategy claim; otherwise BLOCKED/no strategy |
| C6 — Manuscript/independent audit | phase/constituent-weekly-outcomes-c6-audit | Full manuscript, figures/tables, appendices, supplements, independent mathematical and repository audit | Reproducible claims; errors, exclusions and gate outcomes disclosed |


## 11. Stop rules

1. Stop confirmatory C2/C3 if point-in-time membership/security identity, corporate-action handling, continuous stock anchor/expiry-proxy coverage or the observed NIFTY index target cannot be validated for the registered sample. Historical free-float weights and ETF holdings are not gates in v1.4. A bounded C3-X exploratory run is permitted only on already validated cycle-level target data with known structural-event exclusions and the registered 47/94% threshold; its findings cannot satisfy C1/C2 or unlock confirmatory testing.
2. Do not train a stock panel with future membership, unresolved security mapping, non-causal features, unhandled corporate actions or fabricated/missing-bar replacements.
3. Do not fit the index meta-model on in-sample stock predictions. Every per-stock forecast that enters a cycle summary must be generated out of fold; all constituent rows from one cycle remain in the same fold.
4. Do not call unweighted breadth, mean predicted return or an equal-weight basket the NIFTY 50 index return. The index target is always the observed NIFTY index series from Section 4.1.
5. Require at least 47 valid tradable constituent forecasts and ≥94% member coverage for an accepted cycle; require valid NIFTY target labels for at least 98% of scheduled eligible cycles. If the thresholds fail, report the exact sample reduction; do not lower thresholds after seeing model results.
6. Do not retune on the final holdout. No unbounded model or strategy search beyond the candidates above.
7. End after C6 or at a documented BLOCKED gate. Negative or inconclusive results are valid completion outcomes.
8. A validated directional forecast requires meaningful improvement over matched simple/breadth and direct-index baselines on the untouched holdout, uncertainty evidence, calibration and robustness. A usable trading strategy additionally requires executable fills and net profitability after verified costs. Neither is assumed.


## 12. Final manuscript requirements

The final manuscript must contain abstract; introduction; research questions and hypotheses; extensive literature review; data and provenance; point-in-time universe/membership; formal target and unweighted forecast-signal aggregation; scientific methodology; model/feature specifications; statistical analysis; results with tables/charts; inferences and discussion; robustness; strengths; limitations; conclusion; future directions; references; appendices and supplements.

Appendices include security aliases, membership intervals, corporate-action exclusions, source manifests/hashes, feature dictionary/availability timestamps, stock-model and meta-model configurations, out-of-fold forecast-generation scheme, fold schedule, candidate registry, costs/fills, audit tests and machine-readable results. Never fabricate results, p-values, figures or source coverage.

## 13. Prior research lessons and mandatory checks

Before each phase, reread parent README, operating rules, registered parent plan, literature/source registers, research and error logs, latest summary/manuscript, and this track's status/logs. Known mistakes that must not recur:
- A successful workflow is not proof of data validity or profitability.
- Do not compare a source to values overwritten by that same source.
- A duplicate download/read is not independent validation.
- Do not infer expiries from one weekday; verify the actual expiry contracts and holiday shifts.
- Do not use current constituents or current weights for past dates.
- Do not use binary/equal-weight membership as a free-float weight series.
- Do not represent unweighted stock breadth or an equal-weight constituent statistic as the actual NIFTY 50 return or as official index weights.
- Do not couple official sessions to broker data coverage.
- Do not reuse stale cache chunks without provenance/targeted refresh or publish stale results after failures.
- Do not call a raw score a calibrated probability.
- Do not claim an unrun/failed research tool produced results.
- Include all date-specific brokerage/levies, GST, STT, stamp duty, spread, slippage, lot sizes and fills in strategy P&L.

Visible user conversations and decisions may be logged; hidden private chain-of-thought is not copied. Use auditable summaries and reproducible rationales instead.

## 14. Registration status

At v1.4, C0 governance remains PASS. The C1 intraday target-data sub-gate has passed on 258 cycles, with 154 cycles after the 104-cycle warm-up; daily OHLCV remains 99.9934% with seven residual sessions and corporate-action verification remains incomplete. The user authorized a bounded exploratory stock/constituent-signal prediction test on eligible validated cycles, with known structural-event exclusions and no raw bars published. This is not a C1/C2 pass; confirmatory tests and trading remain locked.


## Version history and controlled amendment

- **v1.0 — 2026-10-31:** Original pre-registered scope, targets, hypotheses, validation plan and acceptance gates.
- **v1.1 — 2026-11-01:** User-directed expiry convention change. For both stock constituents and the NIFTY 50 index outcome, use the close of the latest valid one-minute candle whose timestamp is within 15:00–15:14 IST on the expiry session, label it the 15:15 expiry proxy, and store the actual timestamp. It is not the official 15:30 close. A 15:30 index close may be shown only as a separate sensitivity and cannot be mixed into the primary stock/index target. This replaces the earlier 15:25–15:29 stock-bar requirement. No other research question, hypothesis, entry time, feature policy, fold design or acceptance threshold is changed by this amendment.
- **v1.2 — 2026-11-01:** User-directed public-source fallback. Added a separate exploratory ETF-replica proxy track based on Nippon India ETF Nifty 50 BeES holdings. No historical holdings series was admitted; the single-date calibration was discovery only.
- **v1.3 — 2026-11-01:** User directed: “No comparison needed”. Removed ETF-versus-index weight comparison, free-float IWF reconstruction and weight/basket reconciliation from the active method and C1 gate. Replaced weighted index-return aggregation with a pre-registered, unweighted, strictly out-of-fold constituent forecast-signal meta-model (breadth, probability/return summaries, dispersion, sector breadth and member coverage) trained against the observed NIFTY 50 index-direction label. An equal-weight basket remains a diagnostic only and is never called the NIFTY index. Point-in-time membership, stable security identity, corporate actions, 47-member/94% per-cycle stock-forecast coverage, 98% valid index-label coverage, at least 104 prior cycles, leakage-safe walk-forward validation and Paytm Money execution-cost gates remain.

- **v1.4 — 2026-11-01:** User approved proceeding with prediction experiments despite incomplete final C1 corporate-action review. This amendment creates C3-X, a bounded exploratory-only path using already validated intraday target windows, the registered 47-member/94% threshold, at least 104 prior eligible weekly cycles, point-in-time membership and known structural-event exclusions. The stock training panel is generated in-memory and cached only as authenticated encrypted data; repository reports contain aggregate metrics and cycle-level NIFTY forecasts, not raw constituent bars or per-stock price rows. This does not waive C1/C2 gates, resolve the 711-event catalogue, authorize confirmatory claims, alter the final holdout or trading-cost requirements, or unlock live trading. The normal C2/C3 confirmatory phases remain blocked until C1 passes.
