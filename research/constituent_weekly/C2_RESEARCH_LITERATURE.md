# C2 literature update — constituent-level forecasting and evaluation

**Review date:** 2026-11-02  
**Scope:** Evidence relevant to point-in-time stock-level return/direction forecasting, cross-sectional aggregation, probability evaluation, overfitting controls and trading-cost interpretation. This is a targeted C2 addendum, not the final systematic review required in C6.

## Findings that shape the protocol

### 1. Nonlinear cross-sectional predictors can add information, but regularisation matters

Gu, Kelly and Xiu (2020) compare linear and nonlinear estimators in the canonical stock-return cross-section. Their results favour trees and neural networks when nonlinear interactions are represented, while also finding that shallow/regularised learners can perform better than unnecessarily deep models. Momentum, liquidity and volatility repeatedly appear among important predictor families. Their bottom-up portfolio exercise is particularly relevant: aggregating stock-level forecasts can be more informative than a separate benchmark that only uses a few aggregate predictors.

**Implication:** retain a regularised linear/logistic baseline and shallow tree ensembles; do not assume an arbitrarily complex learner is superior. Build forecasts at the constituent level first, then test aggregation separately on strictly out-of-fold forecasts. Their monthly US equity results do not establish a weekly NIFTY expiry edge.

Reference: Gu, S., Kelly, B., & Xiu, D. (2020). *Empirical Asset Pricing via Machine Learning*. Review of Financial Studies, 33(5), 2223–2273. https://doi.org/10.1093/rfs/hhaa009

### 2. Indian cross-sectional evidence exists, but does not directly answer the weekly NIFTY expiry question

Lalwani and Meshram (2022) study 35 characteristics in a survivorship-bias-free sample of Indian listed companies from 1994–2019. They report that several characteristics predict the cross-section and that rolling one-month-ahead machine-learning forecasts improve on OLS, including elastic-net, random-forest and XGBoost approaches.

**Implication:** the Indian-market setting supports testing point-in-time constituent characteristics and nonlinear models. The target horizon and universe differ materially: their broad-market monthly return design is not proof of predictive power for a weekly NIFTY-50 expiry-to-expiry window.

Reference: Lalwani, V., & Meshram, V. (2022). *The cross-section of Indian stock returns: evidence using machine learning*. Applied Economics, 54(16), 1814–1828. https://doi.org/10.1080/00036846.2021.1982132

### 3. Large model comparisons require careful model selection and out-of-sample tests

Fieberg et al. (2023) compare penalised linear methods, support-vector regression, random forests, boosted trees and neural networks on a large European equity panel. They report that machine-learning methods improve cross-sectional forecasting over a linear benchmark in their sample, with the gains not explained solely by higher turnover.

**Implication:** the C3 phase should compare regularised linear/logistic, random forest/ExtraTrees and a bounded boosting model, with complexity and tuning controlled inside the training window. Transfer to NSE weekly outcomes must be tested rather than presumed.

Reference: Fieberg, C., Metko, D., Poddig, T., & Loy, T. (2023). *Machine learning techniques for cross-sectional equity returns’ prediction*. OR Spectrum, 45, 289–323. https://doi.org/10.1007/s00291-022-00693-w

### 4. Forecast combination and cross-sectional inference can be made more disciplined

Han, He, Rapach and Zhou (2024) extend Fama–MacBeth-style cross-sectional prediction with regularisation, characteristic selection, forecast combination and encompassing. They also introduce cross-sectional forecast performance measures.

**Implication:** C4 should compare a simple stock-probability breadth signal with a regularised meta-model, measure incremental value over a direct-index benchmark, and avoid fitting the aggregator to in-sample constituent predictions. A strictly OOF stock forecast matrix is a non-negotiable input.

Reference: Han, Y., He, A., Rapach, D. E., & Zhou, G. (2024). *Cross-sectional expected returns: new Fama–MacBeth regressions in the era of machine learning*. Review of Finance, 28(6), 1807–1831. https://doi.org/10.1093/rof/rfae027

### 5. Backtest selection itself can be overfit

Bailey, Borwein, López de Prado and Zhu (2017) formalise probability of backtest overfitting and propose combinatorially symmetric cross-validation (CSCV). They emphasise that conventional holdout alone may not adequately diagnose strategy-selection bias when many strategies/configurations are tried.

**Implication:** the locked chronological final 20% remains untouched during development; model/strategy selection counts must be reported. A PBO/CSCV-style diagnostic may supplement, but not replace, chronological walk-forward evaluation. The C2–C4 forecasts do not by themselves establish a tradable strategy.

Reference: Bailey, D. H., Borwein, J. M., López de Prado, M., & Zhu, Q. J. (2017). *The Probability of Backtest Overfitting*. Journal of Computational Finance. https://doi.org/10.21314/JCF.2016.322

### 6. Probability forecasts should be assessed as probabilities, not just hard labels

Murphy (1973) discusses skill scores based on the Brier/probability score. The Brier score is a proper scoring rule for binary-event probabilities; a model that predicts the right class but is systematically overconfident can still be poorly calibrated.

**Implication:** report accuracy and balanced accuracy alongside Brier score, log loss, ROC AUC, calibration/reliability diagnostics and baseline comparisons. Calibration itself must be fitted on training/development data only, never on the final holdout.

Reference: Murphy, A. H. (1973). *Hedging and Skill Scores for Probability Forecasts*. Journal of Applied Meteorology, 12(1), 215–223. https://doi.org/10.1175/1520-0450(1973)012%3C0215:HASSFP%3E2.0.CO;2

### 7. NSE intraday liquidity is time-of-day dependent

Krishnan and Mishra (2013) use trade-and-quote data for NIFTY stocks and document U-shaped intraday volume/spread patterns on the NSE, including periods when volume and spreads are simultaneously high.

**Implication:** C5 execution modelling must use time-specific spread/liquidity assumptions and cannot equate a valid 1-minute OHLC bar with an executable fill at the bar price. The present OHLC-only C2/C3 panel cannot measure order-book depth or slippage directly.

Reference: Krishnan, R., & Mishra, V. (2013). *Intraday liquidity patterns in Indian stock market*. Journal of Asian Economics, 28, 99–114. https://doi.org/10.1016/j.asieco.2013.05.005

### 8. Trading costs and turnover change over time

Lipson and Zhang (2026) update long-run US equity liquidity and trading-cost estimates. They highlight that lower spreads/commissions can be offset by rising turnover and that trading-cost relationships can shift over time.

**Implication:** cost assumptions must be date-specific and the strategy must report gross and net results, turnover, spread, brokerage and statutory costs separately. This US historical result is not a substitute for India-specific Paytm Money/NSE fee schedules or actual bid/ask observations.

Reference: Lipson, M. L., & Zhang, J. (2026). *A Century and a Quarter of Stock Market Liquidity and Trading Costs*. Financial Management. https://doi.org/10.1111/fima.70070

## Research gap

The reviewed literature supports cross-sectional stock-level modelling and out-of-sample aggregation in principle. It does not demonstrate that forecasts of individual NIFTY 50 stocks, generated at 10:00 IST, predict the actual NIFTY 50 index direction at the 15:15 weekly-expiry proxy. It also does not establish executable net returns from a weekly option strategy on Paytm Money.

The project's empirical contribution must therefore be narrow and falsifiable:

1. Test whether point-in-time constituent features improve stock expiry-direction forecasts over simple momentum and regularised linear baselines.
2. Test whether strictly OOF stock probabilities/expected returns add information for the observed NIFTY 50 expiry direction over a matched direct-index benchmark.
3. Determine whether any signal survives calibration, regime sensitivity, uncertainty intervals and (only later, in C5) realistic trading costs.

## Source links checked

- Oxford Academic / RFS: https://academic.oup.com/rfs/article/33/5/2223/5758276
- Lalwani & Meshram publisher page: https://www.tandfonline.com/doi/full/10.1080/00036846.2021.1982132
- Springer / OR Spectrum: https://link.springer.com/article/10.1007/s00291-022-00693-w
- Oxford Academic / Review of Finance: https://academic.oup.com/rof/article-abstract/28/6/1807/7737488
- eScholarship / PBO: https://escholarship.org/uc/item/4w1110bb
- AMS / Murphy probability score: https://journals.ametsoc.org/view/journals/apme/12/1/1520-0450_1973_012_0215_hassfp_2_0_co_2.xml
- Monash / NSE intraday liquidity: https://research.monash.edu/en/publications/intraday-liquidity-patterns-in-indian-stock-market/
- Wiley / 2026 trading-cost update: https://onlinelibrary.wiley.com/doi/10.1111/fima.70070

**Limitations:** This addendum is a focused literature update, not a PRISMA-style systematic review. Citation chaining, preprints, Indian market microstructure papers, derivatives/options forecasting, official NSE/Dhan/Paytm documentation and relevant conference/video material remain to be consolidated in C6.
