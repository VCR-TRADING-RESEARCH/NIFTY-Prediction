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
