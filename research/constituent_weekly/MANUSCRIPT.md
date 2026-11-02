# Bottom-Up NIFTY 50 Weekly-Expiry Direction Prediction: Exploratory Evidence from Point-in-Time Constituent Forecasts

**Track:** BUP-01  
**Plan:** v1.4 (with the user-directed unweighted aggregation scope from v1.3)  
**Manuscript status:** Research closeout / exploratory evidence; not a confirmatory study  
**Cut-off:** 2 November 2026  
**Repository:** [VCR-TRADING-RESEARCH/NIFTY-Prediction](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction)

## Abstract

This study tests whether forecasting individual NIFTY 50 constituent outcomes and aggregating those forecasts can improve weekly-expiry direction prediction for the observed NIFTY 50 spot index. The registered target is the price return from the first valid one-minute observation at or just after 10:00 IST on the first trading session after the preceding verified weekly expiry to the close of the latest valid one-minute candle timestamped 15:00–15:14 IST on the target expiry (a 15:15 proxy). Stock UP/DOWN labels are formed over the same interval. Point-in-time membership, whole-expiry-cycle chronology, fold-local preprocessing, an encrypted row-level panel and a sealed final chronological holdout were used.

The latest C2 panel contains 258 eligible weekly cycles, 12,807 constituent-cycle rows, 61 symbols and 258 valid index labels. The C3 stock modelling run generated 7,512 strictly out-of-fold forecasts over 154 forecast cycles (57 symbols), including 52 untouched holdout cycles and 2,583 holdout stock observations. On the holdout, the momentum sign baseline reached 50.52% accuracy, 50.77% balanced accuracy and 50.77% ROC-AUC. Logistic regression, ExtraTrees and HistGradientBoosting reached 48.12%, 48.51% and 46.69% accuracy, respectively; their balanced accuracies and ROC-AUCs were also close to or below chance. Logistic minus momentum cycle-macro accuracy was −2.37 percentage points, with a four-cycle moving-block bootstrap 95% interval of −10.04 to +4.29 percentage points. The mean holdout cross-sectional rank information coefficient for the ridge return forecasts was −0.0193.

A separate earlier plan-v1.4 C3-X exploratory run generated out-of-fold constituent summaries and tested a NIFTY direction logistic meta-model on 51 holdout cycles. It achieved 50.98% accuracy, 53.45% balanced accuracy and 48.68% ROC-AUC. Its accuracy advantage over the previous-cycle direction baseline was only 1.96 percentage points, with a very wide bootstrap 95% interval from −25.49 to +25.49 percentage points. That C3-X run used a different panel snapshot, eligibility set and training pipeline and is therefore reported separately, not pooled with the later C3 results.

The evidence does not establish a reliable stock-level or NIFTY-level predictive edge. C1 identity and corporate-action review remains partial; C4 confirmatory aggregation is therefore gated. C5 is blocked because no validated signal or instrument specification exists. No options/futures backtest, Paytm Money fees, spread, slippage, execution fills or net profitability were established. The valid conclusion is a negative/inconclusive research result: no model or trading strategy is selected.

**Keywords:** NIFTY 50; weekly expiry; constituent forecasting; cross-sectional machine learning; time-series validation; out-of-fold prediction; forecast aggregation; backtest overfitting.

---

## 1. Introduction

The research question is whether an index forecast can be improved by first forecasting the constituent stocks, then summarising those stock-level forecasts into a cycle-level signal. The motivation is that individual stocks may contain heterogeneous momentum, volatility, liquidity and cross-sectional information that a direct model built only on the index history can miss. Cross-sectional machine learning studies demonstrate that nonlinear models can be useful for broad equity-return forecasting, but their results do not imply success at a one-week, intraday-anchored NIFTY expiry horizon [1–3].

The NIFTY 50 is not a simple majority vote of fifty equally weighted stock returns. NSE Indices describes it as a free-float market-capitalisation-weighted index; the index has used the free-float methodology since 26 June 2009 [7,8]. This study does not attempt to reconstruct the index return from equal-weighted stock returns or unofficial weights. Instead, the observed NIFTY index return is the target, and unweighted constituent forecast summaries are predictors. That distinction is central: a model may learn that broad constituent direction co-moves with the index without representing breadth as the actual index return.

The research is also distinct from the repository's direct-index ExtraTrees project. That benchmark has an earlier data lineage and a provisional 10:00 anchor; it is not treated as a matched comparator in the C3 holdout results below. The current BUP-01 work is a bounded exploratory investigation, not a live-signal generator.

### 1.1 Research questions

- **RQ1 — Universe and data:** Can point-in-time NIFTY membership, security identity and target observations be reconstructed with adequate cycle coverage?
- **RQ2 — Stock forecasts:** Can causal features available by 10:00 IST predict each eligible constituent's direction and continuous return through the weekly expiry proxy, out of sample?
- **RQ3 — NIFTY aggregation:** Do strictly out-of-fold constituent probabilities, predicted returns, breadth and dispersion add information for the observed NIFTY expiry direction beyond simple baselines?
- **RQ4 — Cross-sectional information:** Do cross-sectional ranks and summary statistics add information beyond own-stock history?
- **RQ5 — Dependence and uncertainty:** Does validation that keeps all stock observations within an expiry cycle together produce sufficiently robust uncertainty estimates?
- **RQ6 — Additional context:** Could timestamp-valid options, India VIX, FII/DII, global markets, sectors, corporate events and news add information?
- **RQ7 — Robustness and economics:** Does any predictive improvement survive holdout, regime and data-quality checks, and does it translate into positive net trading P&L after date-effective fees and realistic fills?

### 1.2 Aim and objectives

**Aim:** Evaluate whether forecasts of individual NIFTY 50 constituent outcomes can be aggregated into a more accurate and robust weekly-expiry forecast of the observed NIFTY 50 spot index.

The objectives were to: (1) audit the point-in-time universe and weekly target coverage; (2) construct causal constituent features and direction labels; (3) establish momentum and symbol-history baselines; (4) test a bounded set of pooled classification/regression models using chronological whole-cycle folds; (5) evaluate out-of-fold cross-sectional aggregation; (6) quantify uncertainty using a cycle-block bootstrap; and (7) decide whether any result qualifies for economic testing.

### 1.3 Hypotheses

- **H0-1:** The pooled stock models do not materially improve holdout direction metrics over simple stock baselines.
- **H0-2:** Any constituent-level signal does not translate into a reliable improvement in NIFTY direction when predictions are aggregated by expiry cycle.
- **H0-3:** No predictive edge is sufficiently robust to justify instrument-level transaction-cost and execution testing.
- **H0-4:** No strategy can be accepted without positive net results after all date-effective charges, spread, slippage and fills.

The alternatives require pre-registered, leakage-safe holdout improvement and uncertainty evidence. No hypothesis is treated as established merely because a GitHub Actions workflow completed.

---

## 2. Literature review

### 2.1 Machine learning and cross-sectional stock-return prediction

Gu, Kelly and Xiu compare a broad set of machine-learning methods for empirical asset pricing. Their work finds that trees and neural networks can capture nonlinear predictor interactions and highlights momentum, liquidity and volatility among important signals [1]. This motivates testing bounded nonlinear candidates alongside regularised linear models. It does not establish that those methods predict a short weekly expiry return for Indian large-cap constituents.

Fieberg, Metko, Poddig and Loy study cross-sectional equity-return forecasts over a broad European stock universe and compare linear and nonlinear approaches, including random forests and boosted trees. They report improvements from selected machine-learning approaches and forecast combinations [2]. The universe, sampling frequency and return horizon differ materially from this project; the paper motivates careful candidate comparison, not an assumption that ensemble forecasts will win here.

Lalwani and Meshram study the cross-section of Indian stock returns using a survivorship-bias-free listed-equity sample and rolling one-month-ahead forecasts. They report that machine learning improves forecast accuracy relative to OLS in their setting [3]. That evidence is more geographically relevant than US-only results, but their universe and monthly horizon are not equivalent to point-in-time NIFTY 50 members and weekly expiry targets.

The current experiment's results underline this distinction. A model family with good performance in a different market or horizon may fail at weekly expiry, particularly where the outcome horizon is short, label imbalance changes over time and market microstructure costs are large relative to the move being forecast.

### 2.2 Index targets and constituent aggregation

The NSE describes NIFTY 50 as a fifty-stock, free-float market-capitalisation-weighted index [7,8]. The project therefore uses the observed index series as its outcome label. A count of stocks predicted UP, average stock probability or equal-weight mean predicted return is an unweighted signal summary; none is the official index return.

NSE distinguishes a price index from a total-return index: the price index reflects constituent price movements, while the total-return variant additionally accounts for dividends reinvested under its methodology [9]. The registered target here is a price-return target based on the intraday index observations defined in Section 3. The project's stock-level labels are also price-return labels, with unresolved mechanical corporate-action cycles excluded rather than adjusted by an unverified universal factor.

### 2.3 Point-in-time membership and survivorship

Applying current constituents to historical observations can create survivorship and look-ahead bias. The C1 work uses effective-dated membership intervals and a security identity/alias ledger; ticker strings alone are not treated as stable identifiers. A remaining limitation is that the historical identity and corporate-action review is not complete. A catalogue of candidate events is a discovery tool, not proof that each event's terms, effective date and adjusted price basis have been validated.

### 2.4 Forecast evaluation and probability quality

Accuracy alone can be misleading when the class mix changes. Balanced accuracy, Matthews correlation, ROC-AUC, Brier score and log loss were therefore retained as complementary measures. The Brier score is a proper score for probability forecasts; Murphy's decomposition distinguishes reliability, resolution and uncertainty [5]. The C3 outputs are explicitly uncalibrated, so Brier and log loss are diagnostic scores rather than evidence of calibrated probabilities.

Diebold and Mariano formulate tests for equal predictive accuracy of competing forecasts under general loss functions and serially correlated forecast errors [4]. This project used a four-cycle moving-block bootstrap for the registered paired cycle-accuracy difference. That preserves local time dependence better than resampling individual stock rows, but the short holdout still produces wide intervals.

Bailey, Borwein, López de Prado and Zhu warn that repeated strategy/model selection can overfit backtests and propose a framework for estimating the probability of backtest overfitting [6]. Accordingly, this study kept a bounded candidate set and did not retune on the final holdout after observing results. Negative outcomes are retained in the experiment record.

### 2.5 Research gap

The literature supports testing cross-sectional machine learning and forecast aggregation, but it does not answer the project's precise question: whether constituent forecasts generated at a 10:00 IST anchor predict the observed NIFTY 50 weekly-expiry proxy direction on a leakage-safe, point-in-time sample. The present evidence does not close that gap positively. Instead, it shows that stock-level models near chance did not translate into a demonstrably reliable index signal in the separate exploratory NIFTY aggregation run.

---

## 3. Data, universe and target construction

### 3.1 Point-in-time universe

The BUP-01 C2 build reports 258 scheduled weekly expiry cycles, 12,807 constituent-cycle rows, 61 distinct symbols, 258/258 valid NIFTY index labels and 258/258 cycles meeting the registered primary member-coverage threshold. Duplicate stock-cycle and index-cycle keys were zero. The C2 input manifest hash is:

`9d263e441f09c70693e30f1541440ac6b249c5293da61faceb0af729d699c305`.

The C1 gate report dated 2 November 2026 records daily OHLCV coverage of 106,392/106,392 observations across 70 symbols and successful validation of seven residual NSE archive rows. It also records only 79/84 historical alias resolutions against the current master and 711 point-in-time member-event candidates requiring further independent event-level review. Thus C1 remains PARTIAL, not fully accepted.

The user's explicit decision allowed progression to exploratory modelling despite incomplete identity/action work. That is a progression waiver, not evidence that the unresolved events passed. C3 excludes 292 identity-flagged rows and 3 known action-crossing rows. It also excludes 19 flat stock labels from binary UP/DOWN fitting. The 92 missing predictor observations are retained and handled by imputation fitted only on each training fold.

### 3.2 Forecast window and expiry proxy

For each weekly expiry cycle (t), the anchor is the first valid one-minute observation at or after 10:00 IST and no later than 10:03 IST on the first NSE session after the preceding verified expiry. The target expiry observation is the close of the latest valid one-minute candle timestamped from 15:00 through 15:14 IST. By user instruction, this is treated as a 15:15 proxy; no 15:25–15:29 data are required, and the proxy is not represented as the official 15:30 close.

For index level (N) and constituent (i):

[
R^N_t = rac{C^N_t}{A^N_t}-1,qquad
R^i_t = rac{C^i_t}{A^i_t}-1.
]

The binary label is UP when (R>0), DOWN when (R<0), and FLAT when (R=0). Flat stock rows are not fitted as binary outcomes. The observed NIFTY index series, not any equal-weight stock basket, supplies the NIFTY label.

### 3.3 Data security and provenance

The row-level C2 panel was held as AES-GCM encrypted data in Actions cache/artifacts. C3 verified ciphertext checksums and authenticated/decrypted the panel only within the workflow runner. Per-stock OOF forecasts were re-encrypted before artifact publication. The public repository contains sanitised aggregate metrics and reports, not raw prices or plaintext member-feature rows. Secrets are not reproduced in this manuscript.

### 3.4 C3-X versus C3 samples

Two exploratory runs must be kept separate:

| Attribute | C3-X plan v1.4 | Later C3 stock-model run |
|---|---:|---:|
| C1 target cycles | 258 | 258 |
| Eligible modelling cycles | 252 | 258 C2 cycles; forecasts after warm-up |
| Constituent rows | 12,560 | 7,512 OOF forecast rows |
| Symbols | 62 | 57 |
| First holdout index | cycle 201 | cycle 206 |
| Holdout cycles | 51 | 52 |
| Holdout stock rows | 2,543 | 2,583 |
| Structural event treatment | 6 known events considered; 18 rows excluded | 292 identity flags and 3 action-crossing rows excluded |

The C3-X run was executed on 1 November 2026 using its own exploratory build. The newer C3 stock model run consumed the refreshed C2 artifact from 2 November 2026. Different row eligibility, samples and pipeline versions mean their metrics are not pooled or treated as a single experiment.

---

## 4. Methodology

### 4.1 Causal stock features

The C3 stock model used the following 14 features, subject to fold-local imputation and scaling where applicable:

- lagged returns: 1, 5, 10, 20 and 60 sessions;
- realised volatility: 5, 20 and 60 sessions;
- rolling range measures: 10 and 20 sessions;
- one-session gap;
- 20-session volume z-score;
- cross-sectional ranks of 5-session and 20-session returns.

The features were constructed from historical data available before the forecast target. Index prices, options, global markets, India VIX, FII/DII, news and event text were not inputs to this C3 experiment.

### 4.2 Walk-forward split and leakage control

The unit of time splitting is the complete expiry cycle. All constituent observations from a cycle remain together. The first 104 cycles are the warm-up. Forecasts are generated for 154 cycles. Development forecasts cover 102 cycles, and the final holdout covers 52 cycles (cycle indices 206–257).

During development, models refit every four expiry cycles using only prior cycles. The entire final holdout is predicted by models fitted exclusively on development cycles 0–205; no holdout label enters a holdout refit. All imputers, scalers and estimators are fitted inside the training fold. Cycle weights equalise each expiry cycle's total influence in model fitting.

### 4.3 Candidates

- **Momentum sign baseline:** UP probability 0.55 when the 5-session return is positive, otherwise 0.45.
- **Symbol-frequency baseline:** smoothed per-symbol UP frequency based only on prior training observations, with a global prior for unseen symbols.
- **Logistic regression:** regularised pooled classifier with fold-local median imputation and standardisation.
- **ExtraTrees:** constrained ensemble (300 trees, max depth 10, minimum leaf 25, 80% max features).
- **HistGradientBoosting:** constrained histogram boosting (150 iterations, 0.05 learning rate, 15 leaf nodes, L2 regularisation 5, minimum leaf 40).
- **Ridge return model:** regularised continuous-return regression used for cross-sectional rank-IC diagnostics.

No additional model families or holdout tuning were introduced.

### 4.4 Metrics and uncertainty

The reported metrics are accuracy, balanced accuracy, Matthews correlation coefficient (MCC), ROC-AUC, Brier score and log loss. Cycle-macro accuracy averages per-cycle accuracy so that larger constituent counts do not dominate the summary. Return ranking is measured by per-cycle Spearman correlation between forecast return and realised stock return.

The registered uncertainty calculation uses 2,000 moving-block bootstrap replicates over four adjacent expiry cycles with seed 20261031. The paired quantity is per-cycle logistic accuracy minus momentum accuracy. The interval retains whole cycles. It is not a confidence interval for every individual stock or for trading P&L.

### 4.5 Separate C3-X NIFTY aggregation test

The earlier plan-v1.4 C3-X run created cycle-level summaries from strictly out-of-fold constituent forecasts and fitted a logistic meta-model to the observed NIFTY label. The available summary metrics are reported separately. It is an exploratory result on a different panel and holdout and does not satisfy the locked C4 confirmatory gate.

---

## 5. Results

### 5.1 C3 stock direction: untouched holdout

| Model | Observations | Accuracy | Balanced accuracy | MCC | ROC-AUC | Brier | Log loss |
|---|---:|---:|---:|---:|---:|---:|---:|
| Momentum | 2,583 | 0.5052 | 0.5077 | 0.0153 | 0.5077 | 0.2520 | 0.6971 |
| Symbol frequency | 2,583 | 0.4592 | 0.5075 | 0.0229 | 0.5199 | 0.2590 | 0.7133 |
| Logistic regression | 2,583 | 0.4812 | 0.4903 | −0.0194 | 0.4853 | 0.2528 | 0.6989 |
| ExtraTrees | 2,583 | 0.4851 | 0.4921 | −0.0157 | 0.4792 | 0.2520 | 0.6971 |
| HistGradientBoosting | 2,583 | 0.4669 | 0.4894 | −0.0224 | 0.4883 | 0.2604 | 0.7147 |

The holdout positive-label rate was 43.67%, versus 52.65% in the development OOF sample, a decline of approximately 8.98 percentage points. This is evidence of label-prior drift between development and holdout. The baseline based on prior symbol frequency did not adapt successfully. The model probabilities were not calibrated; neither raw accuracy nor small differences between Brier/log-loss values should be treated as calibrated trading probabilities.

The cycle-macro results were:

| Split | Cycles | Momentum accuracy | Logistic accuracy | ExtraTrees accuracy | HistGradientBoosting accuracy | Ridge return rank IC |
|---|---:|---:|---:|---:|---:|---:|
| Development | 102 | 0.4752 | 0.5106 | 0.4971 | 0.4973 | 0.0261 |
| Untouched holdout | 52 | 0.5052 | 0.4815 | 0.4852 | 0.4668 | −0.0193 |

The paired logistic-minus-momentum cycle-macro accuracy difference was:

[
Delta = -0.0237255
]

with a four-cycle moving-block bootstrap 95% interval:

[
[-0.1003779, 0.0428564].
]

The point estimate favours momentum over logistic regression; the interval crosses zero. The evidence is therefore inconclusive about the size of the difference, but it does not support selecting logistic regression. ExtraTrees and HistGradientBoosting also failed to improve on the momentum baseline.

### 5.2 C3-X NIFTY direction: separate exploratory holdout

| Model | Cycles | Accuracy | Balanced accuracy | MCC | ROC-AUC | Brier |
|---|---:|---:|---:|---:|---:|---:|
| OOF constituent-signal logistic meta-model | 51 | 0.5098 | 0.5345 | 0.0679 | 0.4868 | 0.2681 |
| Constituent breadth baseline | 51 | 0.4314 | 0.4827 | −0.0366 | 0.4457 | 0.3289 |
| Previous eligible-cycle direction | 51 | 0.4902 | 0.4548 | −0.0905 | 0.4548 | 0.5098 |

The meta-model's observed accuracy advantage over previous-cycle direction was 1.96 percentage points (one additional correct cycle out of 51). The registered four-cycle moving-block bootstrap 95% interval was [−25.49, +25.49] percentage points. This range is extremely wide and includes substantial underperformance and outperformance.

The NIFTY holdout UP rate was 37.25%. Therefore, the ex-post all-DOWN classification rate would be 62.75%; this uses the realised holdout class mix and is **not** an admissible forecasting baseline, but it shows why the meta-model's 50.98% accuracy cannot be interpreted in isolation. Its ROC-AUC was below 0.50. Its Brier score (0.2681) was also above the ex-post constant-rate uncertainty score (q(1-q)approx0.2337); this is a descriptive diagnostic, not a pre-fit benchmark. The run therefore does not demonstrate robust probability discrimination.

### 5.3 Result interpretation

The direct stock-model evidence is negative/inconclusive. The best direction baseline was only marginally above chance by balanced accuracy and ROC-AUC, and the pooled nonlinear models did not outperform it. The separate NIFTY meta-model achieved a little over 50% accuracy but had below-chance ROC-AUC and an extremely wide uncertainty interval on only 51 cycles. No reliable incremental NIFTY edge is established.

---

## 6. Statistical and mathematical audit

The following arithmetic and protocol checks were independently re-performed from the sanitised JSON/CSV summary data:

1. **C3 sample accounting:** 4,929 development rows + 2,583 holdout rows = 7,512 total OOF stock rows.
2. **C3 cycle accounting:** 102 development forecast cycles + 52 holdout forecast cycles = 154 total forecast cycles.
3. **Holdout boundary:** all 52 holdout cycles are 206–257; the C3 runner sets the training cutoff for the complete final block to 206, so every final-holdout fit uses cycle indices below 206 only.
4. **C3 paired result:** 0.481455 cycle-macro logistic accuracy − 0.505181 momentum accuracy = −0.023726 (rounding difference only).
5. **C3 bootstrap gate:** the reported lower bound is negative and the upper bound positive; the interval crosses zero.
6. **C3-X NIFTY confusion matrix:** TN=14, FP=18, FN=7, TP=12; ( (TN+TP)/51=26/51=0.509804). Sensitivity is (12/19), specificity is (14/32), giving balanced accuracy (0.534539). The paired one-cycle accuracy difference to lag direction is (1/51=0.019608), matching the reported 1.96 pp.
7. **C3-X uncertainty:** the interval [−0.254902, +0.254902] is symmetric and crosses zero; it does not establish a positive edge.
8. **No post-holdout model selection:** no model family, threshold or feature was tuned using the final holdout after inspection.
9. **No strategy arithmetic claimed:** no P&L, fee, lot-size, payoff, margin or fill calculations were supplied; C5 correctly remains blocked.

These checks validate the internal consistency of the published summaries and the visible split logic. They do not replace a fresh independent reproduction from restricted raw data, issuer-level action notices or broker fills.

---

## 7. Discussion

### 7.1 Why the bottom-up hypothesis did not succeed here

The stock forecasts did not show useful holdout discrimination. The development cycle-macro logistic accuracy was 51.06%, but the holdout cycle-macro accuracy fell to 48.15%. The holdout return rank IC was negative. The other tree models did not repair the short-horizon signal. This is compatible with the notion that patterns useful in longer-horizon equity cross-sections may not translate to weekly expiry prediction.

The shift in stock UP rate from 52.65% in development to 43.67% in holdout suggests a change in label distribution. Models trained on a development period with a higher UP share can be poorly calibrated or misclassified when the future regime changes. No calibration or adaptive-prior procedure was selected, because the study does not permit holdout retuning.

### 7.2 Why a 50.98% NIFTY accuracy is not a result to trade

The earlier C3-X meta-model's 50.98% accuracy is based on just 51 weekly cycles. Its ROC-AUC was 0.4868, which does not indicate useful ordering of UP versus DOWN cases. Its uncertainty interval spans roughly −25 to +25 percentage points for the paired accuracy difference. The positive class rate was only 37.25%, further limiting the interpretability of raw accuracy. Balanced accuracy was above 50%, but the sample and interval are too weak to establish a reproducible edge.

### 7.3 Why no C4 confirmatory phase is opened

The C1 developer gate report still identifies unresolved dated security aliases and event-level corporate-action validation, including 711 member-event candidates requiring independent review. The user authorised exploratory progression, and the C2 panel and C3 run were executed accordingly. That authorisation does not certify C1 or unlock confirmatory evaluation. C4 confirmatory aggregation is therefore GATED. The C3-X meta-model remains the only reported NIFTY aggregation experiment, and it remains exploratory.

### 7.4 No trading inference

A directional classifier is not a strategy. A strategy needs a product, expiry/strike/contract, order timing, exit rules, position size, margin assumptions, fill model and date-effective fee schedule. Directional accuracy, even if higher, would not establish positive after-cost P&L. Because no dependable NIFTY edge or instrument specification exists, running a Paytm Money fee model now would imply false precision. C5 is blocked, not passed.

---

## 8. Strengths

- Point-in-time membership and dated identity controls are explicit rather than applying today's list to history.
- Complete weekly expiry cycles are kept together in chronological folds.
- The final C3 holdout was kept out of all training and refitting.
- Imputation and scaling are fitted inside each training fold.
- A compact candidate family was registered; holdout-driven search was avoided.
- Cycle-level uncertainty retains weekly blocks rather than treating thousands of stock rows as independent samples.
- Row-level panels and individual OOF forecasts are encrypted; public outputs are sanitised.
- Failed workflow attempts and code corrections are retained in the error log.
- The negative/inconclusive result is reported rather than selecting a model by development performance.

## 9. Limitations

1. **C1 incompleteness:** historical security identity is not completely reconciled; 79/84 aliases were resolved against the current master. Event-level issuer/exchange corporate-action verification remains incomplete; the candidate action catalogue contains 711 point-in-time member events.
2. **Exclusions:** 292 identity-flagged rows and 3 known action-crossing rows were excluded from C3; 19 flat stock labels were excluded from binary classification.
3. **Predictor missingness:** 92 stock feature observations were missing and handled by fold-local median imputation. This is leakage-safe but can still reduce information quality.
4. **Limited horizon and holdout:** 52 C3 holdout cycles and 51 C3-X holdout cycles are small for establishing a stable weekly signal.
5. **Pipeline differences:** C3-X and later C3 have different panel eligibility, model pipeline and holdout boundary. Their metrics must not be pooled.
6. **Limited features:** no timestamped historical options chain, implied volatility/skew, India VIX, FII/DII release-time series, global futures, FX, commodity, rates, news or earnings features were included in these runs.
7. **No calibration acceptance:** probability outputs are uncalibrated; calibration plots and formal reliability evaluation were not passed.
8. **No matched direct-index re-test:** the earlier index-only model benchmark uses a separate data lineage and provisional anchor; it is not a fair matched-cycle comparator here.
9. **No economic test:** Paytm Money brokerage/levies, taxes, spread, slippage, lot-size changes, execution fills, market impact, margin and net P&L were not tested.
10. **Public repository constraints:** raw source rows and per-stock price data remain encrypted/not published; independent raw-data reproduction requires the authorised private data and credentials.

## 10. Conclusion

The study does not find evidence that the tested constituent stock models can reliably predict weekly expiry direction, nor that the separate exploratory aggregation test yields a dependable NIFTY 50 direction signal. Logistic regression, ExtraTrees and HistGradientBoosting did not beat the simple momentum baseline on the later C3 holdout. The C3-X NIFTY meta-model's point accuracy was 50.98%, but ROC-AUC was 48.68% and uncertainty was extremely wide.

**No stock model is selected. No NIFTY forecast model is accepted. No trading strategy is validated.** C1 remains partial, C4 confirmatory is gated, and C5 remains blocked. This is a completed negative/inconclusive exploratory result under the current bounded evidence, not a recommendation to trade.

## 11. Future research

1. Complete dated ISIN/security identity reconciliation and independent issuer/exchange verification of member corporate actions before opening confirmatory C4.
2. If C1 is accepted, regenerate stock OOF forecasts from one single frozen panel and one locked model pipeline, then aggregate those forecasts on identical cycles against the observed NIFTY label. Include a matched direct-index benchmark.
3. Add point-in-time India VIX and options IV/skew/OI/volume only after verifying historical timestamp coverage and source permissions.
4. Evaluate FII/DII flows only where release timestamps are available before the 10:00 forecast. Add global equity futures, USD/INR, crude, gold, rates and sector returns with local market-close and daylight-saving alignment.
5. Explore robust abstention or calibration only on development data and freeze the method before a new holdout. Any conformal method must be tested under serial dependence and distribution shift; nominal coverage should not be assumed.
6. Consider constrained symbolic feature discovery or volatility-regime estimates only within a pre-registered candidate budget; log the full search space to control selection bias.
7. Reopen C5 only after a validated NIFTY signal and fixed instrument specification exist. Then use historical Paytm Money fee schedules, contract specifications, bid/ask data and conservative execution fills.
8. Extend the final audit with re-performance from an access-controlled private data store, independent event adjudication and contract-level P&L reconciliation.

---

## References

1. Gu, S., Kelly, B., & Xiu, D. (2020). Empirical Asset Pricing via Machine Learning. *The Review of Financial Studies*, 33(5), 2223–2273. [https://doi.org/10.1093/rfs/hhaa009](https://doi.org/10.1093/rfs/hhaa009).
2. Fieberg, C., Metko, D., Poddig, T., & Loy, T. (2023). Machine learning techniques for cross-sectional equity returns' prediction. *OR Spectrum*, 45, 289–323. [https://doi.org/10.1007/s00291-022-00693-w](https://doi.org/10.1007/s00291-022-00693-w).
3. Lalwani, V., & Meshram, V. V. (2022). The cross-section of Indian stock returns: evidence using machine learning. *Applied Economics*, 54(16), 1814–1828. [https://doi.org/10.1080/00036846.2021.1982132](https://doi.org/10.1080/00036846.2021.1982132).
4. Diebold, F. X., & Mariano, R. S. (1995). Comparing Predictive Accuracy. *Journal of Business & Economic Statistics*, 13(3), 253–263. [https://doi.org/10.1080/07350015.1995.10524599](https://doi.org/10.1080/07350015.1995.10524599).
5. Murphy, A. H. (1973). A New Vector Partition of the Probability Score. *Journal of Applied Meteorology*, 12(4), 595–600. [https://doi.org/10.1175/1520-0450(1973)012<0595:ANVPOT>2.0.CO;2](https://doi.org/10.1175/1520-0450(1973)012<0595:ANVPOT>2.0.CO;2).
6. Bailey, D. H., Borwein, J. M., López de Prado, M., & Zhu, Q. J. (2017). The Probability of Backtest Overfitting. *The Journal of Computational Finance*. [https://doi.org/10.21314/jcf.2016.322](https://doi.org/10.21314/jcf.2016.322).
7. NSE Indices. NIFTY 50 Index description and methodology. [Official NIFTY 50 page](https://www.nseindia.com/static/products-services/indices-nifty50-index).
8. NSE Indices. Methodology Document for Equity Indices. [NIFTY 50 methodology PDF](https://nsearchives.nseindia.com/content/indices/Method_Nifty_50.pdf).
9. NSE India. Total Returns Index: price index and dividend reinvestment distinction. [Official total return index page](https://www.nseindia.com/static/products-services/indices-total-returns-index).
10. DhanHQ. Historical Data API documentation. [https://dhanhq.co/docs/v2/historical-data/](https://dhanhq.co/docs/v2/historical-data/).

---

## Appendix A — Data and feature dictionary

| Field family | Feature examples | Availability rule |
|---|---|---|
| Lagged return | ret_1d, ret_5d, ret_10d, ret_20d, ret_60d | Prior completed sessions only |
| Volatility | vol_5d, vol_20d, vol_60d | Prior sessions only |
| Range | range_10d, range_20d | Prior sessions only |
| Gap | gap_1d | Pre-forecast session boundary |
| Volume | volume_z20 | Historical volume only; missing retained as missing |
| Cross-section | cs_rank_ret5, cs_rank_ret20 | Point-in-time member universe; fold-safe transforms |
| Labels | stock_label, index_label | Anchor-to-expiry proxy; FLAT separate |

## Appendix B — Execution records

- C2 source build and formal acceptance: [run 41398864378](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41398864378).
- C3 stock-model workflow, successful attempt 2: [run 41401986460](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41401986460).
- C3 machine results: [C3_RESULTS.json](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c3-models/research/constituent_weekly/C3_RESULTS.json).
- C3 report: [C3_RESULTS.md](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c3-models/research/constituent_weekly/C3_RESULTS.md).
- C3-X report: [EXPLORATORY_REPORT.md](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c3-exploratory/research/constituent_weekly/EXPLORATORY_REPORT.md).
- C1 developer gate report: [C1_DEVELOPER_GATE_REPORT.md](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c1-data/research/constituent_weekly/C1_DEVELOPER_GATE_REPORT.md).
- C5 economics gate: [C5_COST_GATE.md](C5_COST_GATE.md).

## Appendix C — Error and correction register

- E0101: C3 workflow source-run discovery lacked an explicit GitHub token context; corrected before accepted modelling.
- E0102: initial walk-forward scheduling allowed holdout cycles into subsequent refits; corrected so all cycles 206–257 use development cycles 0–205 only.
- E0103: C3 branch manifest was stale relative to random-nonce ciphertext; corrected by copying manifest from the exact matching C2 artifact before hash validation.
- E0104: complete-case feature filtering would unnecessarily remove rows with missing predictors; corrected to use fold-local imputation.
- E0105: C2 coverage acceptance was incorrectly reapplied after excluding flat binary labels; corrected to preserve the original panel gate and handle flats as a model-specific exclusion.
- E0106: decrypted CSV bytes were passed to pandas as a filename; corrected with io.BytesIO and verified by encrypted/gzip round-trip test. C3 workflow attempt 2 then passed.

## Appendix D — Reproducibility and phase state

- C1: PARTIAL / identity and corporate-action review remains open.
- C2: PASS for the frozen panel and formal coverage/uniqueness gates; upstream C1 limitations remain.
- C3: exploratory stock-modelling run complete; no stock edge demonstrated.
- C3-X: separate exploratory NIFTY aggregation run complete; inconclusive.
- C4 confirmatory: GATED by C1.
- C5: BLOCKED / NOT RUN; no instrument or verified costs/fills.
- C6: manuscript and independent summary audit prepared; raw-data re-performance remains constrained by private/encrypted data access.
