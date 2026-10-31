# Literature and Source Review — Bottom-Up NIFTY Constituents

**Reviewed:** 2026-10-31  
**Track:** BUP-01  
**Status:** Initial evidence review, not an exhaustive global systematic review and not an empirical result.

## 1. Cross-sectional equity-return prediction

### Gu, Kelly and Xiu (2020)
Gu, Shihao, Bryan Kelly and Dacheng Xiu, “Empirical Asset Pricing via Machine Learning,” *The Review of Financial Studies*, 33(5), 2223–2273 (2020). DOI: https://doi.org/10.1093/rfs/hhaa009. The study compares machine-learning approaches to equity risk-premium measurement and reports that tree and neural-network methods capture nonlinear predictor interactions; momentum, liquidity and volatility are among the signals considered important. This motivates testing pooled stock-level models and nonlinear interactions. Its results do not establish that a 10:00-to-weekly-expiry NIFTY forecast will work: market, horizon and sample design differ.

### Fieberg, Metko, Poddig and Loy (2023)
“Machine learning techniques for cross-sectional equity returns' prediction,” *OR Spectrum*, 45 (2023). DOI: https://doi.org/10.1007/s00291-022-00693-w. The paper compares linear and nonlinear models using monthly data on a large European equity universe and reports gains from forecast combinations. It motivates a small forecast-combination benchmark, not unrestricted model search; European monthly returns are not the Indian weekly-expiry setting.

### Indian cross-section evidence
“The cross-section of Indian stock returns: evidence using machine learning,” *Applied Economics*, DOI: https://doi.org/10.1080/00036846.2021.1982132. This work describes a survivorship-bias-free Indian listed-equity sample from 1994–2019 and rolling one-month-ahead forecasts. Its market relevance motivates explicit survivorship control, but the one-month horizon and broad listed universe differ from this NIFTY 50 weekly target.

### Zhao and Cheng (2022)
“Stock return prediction: Stacking a variety of models,” *Journal of Empirical Finance*, 67, 288–317. DOI: https://doi.org/10.1016/j.jempfin.2022.03.001. This supports a bounded forecast-combination comparison after a valid panel is constructed; it does not justify a large model search or guarantee improvement at this horizon.

## 2. Index construction, weights and bottom-up aggregation

NSE Indices describes NIFTY 50 as a 50-company index and documents free-float market-capitalisation weighting since 26 June 2009. Under free-float weighting, constituent weight is based on float-adjusted market capitalisation; index methodology also specifies treatment of constituent changes and corporate actions. The main aggregate must therefore use point-in-time free-float weights, not a 50-stock majority vote.

Official references:
- NIFTY 50 description, constituents and downloads: https://www.nseindia.com/static/products-services/indices-nifty50-index
- NSE Indices methodology: https://archives.nseindia.com/content/indices/Method_Nifty_50.pdf
- NSE Indices FAQ: https://www.niftyindices.com/resources/index-concepts/faqs
- Investible Weight Factors: https://www.nseindia.com/static/products-services/indices-investible-weight-factors
- Monthly reports and index weightage archives: https://niftyindices.com/reports/monthly-reports
- NSE historical reports and daily data categories: https://www.nseindia.com/all-reports

## 3. Survivorship bias and point-in-time constituents

Historical membership must be reconstructed from effective-dated additions and removals. Applying today's membership to past dates creates survivorship/look-ahead bias.

The public repository BKKB20/nse-index-history claims to reconstruct 28 NSE indices for 2004–2026 from roughly 100 NSE circulars. Its README discloses three unprocessed scanned circulars from 2018–2019 and pre-2010 ticker mapping limitations. It is a candidate dataset to compare with original NSE circulars, not official ground truth: https://github.com/BKKB20/nse-index-history.

The public repository vishalvx/nifty-indices-datasets describes monthly reconstructed membership, but its README explicitly says the datasets use binary membership rather than numeric free-float weights. It can be a membership cross-check, not a primary numeric weight source: https://github.com/vishalvx/nifty-indices-datasets.

## 4. Market data, history and corporate actions

NSE's public report categories include historical index data, India VIX, equity security-wise price/volume, daily snapshots and index market-cap/weightage reports. These are the free-first source candidates. Original files and publication timestamps must be retained.

DhanHQ v2 documentation describes 1/5/15/25/60-minute historical OHLCV data for up to five years for active instruments, with a maximum 90-day request window; daily history is available from instrument inception. This supports a bounded stock-data feasibility test, but does not guarantee coverage for delisted, merged or otherwise inactive historical constituents:
- https://dhanhq.co/docs/v2/historical-data/
- https://dhan.co/support/platforms/dhanhq-api/what-timeframe-data-is-available-through-dhan-s-historical-data-apis/

## 5. Validation, selection bias and uncertainty

Bailey, Borwein, López de Prado and Zhu (2017), “The Probability of Backtest Overfitting,” *Journal of Computational Finance*. DOI: https://doi.org/10.21314/jcf.2016.322. This explains why extensive strategy selection can make ordinary holdout procedures unreliable. BUP-01 therefore fixes a bounded candidate set, chronological holdout, experiment registry and multiple-testing control.

MAPIE/conformal methods may be considered for uncertainty or abstention only after time-series assumptions are examined; standard conformal coverage should not be presumed under arbitrary market drift. The arch package may support lagged volatility/regime features; volatility is not itself a direction signal. PySR and Quantevolve may generate constrained feature candidates only within development folds. TradingAgents and AstraQuant may help structure hypotheses, but their outputs are not labels, observations or independent validation.

## 6. Research tools and intended role

| Repository/tool | Intended role | Guardrail |
|---|---|---|
| [Quantevolve](https://github.com/tarsyang/quantevolve) | Bounded evolutionary rule/hypothesis proposals after data validation | Fold isolation, candidate budget and multiple-testing log |
| [TradingAgents](https://github.com/TauricResearch/TradingAgents) | Technical/fundamental/sentiment/risk hypothesis review | Deterministic validation; no autonomous orders |
| [AstraQuant Agent](https://github.com/0xethanq/astra-quant-agent) | Architecture and risk-control inspiration | Crypto-oriented; inspect licence before copying code |
| [PySR](https://github.com/astroautomata/PySR) | Constrained symbolic feature discovery within development folds | Complexity penalty and fixed search budget |
| [arch](https://github.com/bashtage/arch) | Stock/market volatility estimates and regime features | Volatility is not direction; estimates must be lagged |
| [tick](https://github.com/X-DataInitiative/tick) | Optional point-process/microstructure analysis if granular data supports it | Optional and data-intensive |
| [MAPIE](https://github.com/scikit-learn-contrib/MAPIE) | Prediction intervals/sets and uncertainty/abstention analysis | Validate dependence, drift and time-series coverage assumptions |

## 7. Research gap and contribution

The reviewed evidence supports the plausibility of cross-sectional equity modelling, nonlinear stock forecasts and bounded forecast combinations. It does not establish that constituent-level weekly-expiry forecasts aggregate into a better NIFTY 50 prediction. BUP-01 tests that exact bottom-up hypothesis with point-in-time membership, free-float weights, cross-stock dependence, a matched direct-index benchmark and explicit source/cost gates.

No model from the reviewed papers or tool repositories is assumed superior here. No experiment with those tools is claimed to have run at registration.


## 8. Component-based aggregate-market prediction

### Ellington, Pybis and Zheng (2026)
“Industry Signals and the Dynamics of Stock Market Predictability,” *International Journal of Finance & Economics*, first published 17 September 2026. DOI: https://doi.org/10.1002/ijfe.70300. Using updated U.S. data, the study reports that industry portfolios have weak/unstable forecasting power when aggregate market returns are modelled directly, while two component-based designs (return-component decomposition and a sum-of-the-parts forecast) generally improve out-of-sample performance; the strongest sum-of-parts combination in the reported exercise has out-of-sample R-squared around 1.49%. Its inputs are monthly industry returns and aggregate market components, not weekly constituent-level NIFTY returns. It provides direct conceptual support for testing component-based aggregation while also warning that simply throwing component returns into a direct aggregate regression may fail. The authors recursively form inputs and estimates using information available at each forecast origin, a discipline adopted here.

### Huddleston, Liu and Stentoft (2023)
“Intraday Market Predictability: A Machine Learning Approach,” *Journal of Financial Econometrics*, 21(2), 485–527. DOI: https://doi.org/10.1093/jjfinec/nbab007. The study uses lagged returns of index constituents in the cross-section to predict short-horizon aggregate equity-market returns. It reports meaningful market return predictability from regularised linear and tree models, with ensembles performing best in its application, and finds that constituent returns add information beyond market returns and common trend/liquidity features. The horizon is five-minute market-return forecasting, not a weekly expiry horizon, and the market/data setting differs. It is the closest design precedent for asking whether constituent return features carry information beyond the index's own history.

## 9. Short-horizon cross-sectional signals and India-specific evidence

### Chui, Ranganathan, Rohit and Veeraraghavan (2023)
“Momentum, reversals and liquidity: Indian evidence,” *Pacific-Basin Finance Journal*, 82, article 102193. DOI: https://doi.org/10.1016/j.pacfin.2023.102193. In a sample of 3,956 BSE-listed stocks from 2000–2021, the authors report intermediate/long-term momentum, stronger momentum among liquid stocks, short-term momentum in the most liquid stocks, and more pronounced short/intermediate reversals among illiquid portfolios without the same persistence. This supports including explicit liquidity/turnover interactions and testing whether the most liquid NIFTY constituents behave differently from illiquid stocks. It is broad BSE cross-sectional evidence, not a weekly NIFTY constituent experiment.

### Chen, Cohen, Liang and Sun (2025)
“Maxing out short-term reversals in weekly stock returns,” *Journal of Empirical Finance*, 82, article 101608. DOI: https://doi.org/10.1016/j.jempfin.2025.101608. Using U.S. weekly stock returns (July 1963–December 2022), the paper reports a stronger 1-week reversal effect among high-MAX (high recent maximum daily return) stocks, especially when retail order imbalance is high; the reported high-MAX weekly reversal portfolio return is materially larger than the low-MAX comparison. This motivates a bounded feature/interaction test for prior-week return, recent daily MAX and liquidity/imbalance proxies. It does not establish the same effect in the NIFTY 50 or after free-float weighting, and portfolio returns in the paper should not be read as an available NIFTY alpha.

### Goyal and Jegadeesh (2018)
“Cross-Sectional and Time-Series Tests of Return Predictability: What Is the Difference?” *The Review of Financial Studies*, 31(5), 1784–1824. DOI: https://doi.org/10.1093/rfs/hhx131. The paper clarifies that cross-sectional and time-series return-predictability strategies answer different questions and can differ because of time-varying net market exposure. This is important for BUP-01: predicting which constituents outperform peers is not the same as predicting the sign of the aggregate NIFTY return. The research must report both cross-sectional rank skill and the correctly weighted aggregate market forecast; neither metric substitutes for the other.

### Han, He, Rapach and Zhou (2024)
“Cross-sectional expected returns: new Fama–MacBeth regressions in the era of machine learning,” *Review of Finance*, 28(6), 1807–1831. DOI: https://doi.org/10.1093/rof/rfae027. The authors extend Fama–MacBeth forecasts with regularisation, predictor selection, forecast combination and encompassing, and propose cross-sectional predictive performance measures. They report out-of-sample gains over a large set of characteristics. BUP-01 borrows the principle of fold-local feature selection/regularisation and a constrained ensemble comparison, but a 50-stock, weekly panel has far fewer independent time observations and stronger cross-stock dependence than the broad characteristic dataset.

## 10. Synthesis: what is plausible, what is not yet known

The literature offers three separate propositions, which must not be conflated:

1. **Relative stock ranking can contain signal.** Cross-sectional studies in the U.S. and India report momentum, reversal, liquidity and characteristic-based predictability. This motivates stock-specific features, cross-sectional ranks, liquidity interactions and per-cycle rank IC.
2. **Lagged components can contain aggregate-market information.** Intraday constituent-return research and the 2026 industry sum-of-the-parts work show that component returns can help forecast an aggregate market return in their settings. These are direct conceptual precedents, but differ in market, aggregation level and horizon.
3. **Weekly prediction of the NIFTY 50 aggregate from its own contemporaneous point-in-time constituent weekly-expiry forecasts remains untested.** Stock rank skill may fail to translate into aggregate direction after free-float weighting, common shocks, security changes, index divisor actions and cross-stock dependence are incorporated.

Accordingly, BUP-01 will not optimize the model on stock-level accuracy alone. The primary question is incremental NIFTY expiry forecast value on matched dates. Stock-level balanced accuracy/MCC/ROC-AUC and rank IC are diagnostic. The index-level expected return, P(NIFTY UP), Brier/log loss, calibration, interval coverage and errors against the direct-index baseline determine whether the bottom-up approach adds value.

## 11. New design implications added without changing locked protocol

The locked Plan v1.0 remains unchanged. The following candidates are already within its feature/model scope and will be prioritised as planned, not added as new model families:
- One-week stock return and 1/5/10-day reversal/momentum features; recent maximum daily return (MAX) and volatility-scaled MAX.
- Turnover, traded-value, spread/liquidity proxies and volume surprise; liquidity × momentum/reversal interactions.
- Cross-sectional ranks and breadth/dispersion, but only as-of the forecast timestamp and only over the point-in-time universe.
- Compare linear pooled models with constrained trees; do not assume nonlinear models or ensembles must win.
- Compare direct prediction of aggregate NIFTY returns with a component/sum-of-parts aggregation, then require the latter to reconcile mathematically with point-in-time index weights.
- Keep weekly rank prediction, aggregate index direction and tradable net P&L as three distinct result layers.

No new empirical claims about NIFTY have been made. These papers motivate hypotheses and features only.
