# C1 Public Intraday Source Audit — BUP-01

**Recorded:** 2026-11-01  
**Branch:** `phase/constituent-weekly-outcomes-c1-data`  
**Decision:** Source discovery expanded; no third-party raw intraday dataset admitted to the confirmatory panel at this step.

## Executive finding

A public historical minute archive can fill part of the gap left by Dhan's active-instrument five-year intraday window. A sample of the GitHub archive [gsidhu/nse-intraday-data](https://github.com/gsidhu/nse-intraday-data) contains 1-minute rows with both the 10:00 anchor window and a 15:14 candle for five sampled NIFTY-related series on 2022-11-03. However, its README says MIT while the repository root has no `LICENSE` file; the upstream repository it forks also has no root licence file. Its effective data rights and original feed provenance therefore remain unverified. It is not copied into this repository or used for model labels.

A second recent dataset is explicitly limited to research/educational use and says it is not for redistribution as a commercial product. A large Hugging Face dataset advertises broader 2022–2026 coverage but no usable licence was surfaced and the card endpoint returned an authorization error in this review. A commercial-data-style public project reports extensive NIFTY 50 1-minute coverage but says downloads are not yet open pending licensing.

## Source findings

| Candidate | Discovered coverage | What was tested | Licence / rights finding | Decision |
|---|---|---|---|---|
| [gsidhu/nse-intraday-data](https://github.com/gsidhu/nse-intraday-data) (fork of [aeron7/nifty-banknifty-intraday-data](https://github.com/aeron7/nifty-banknifty-intraday-data)) | Repository folders span 2012–2023; one-minute per-symbol daily files | Point-in-time membership ledger returned 50 expected equity members on 2022-11-03 and 2022-11-04. The archive had files for 47/50 on each date; absent names: DIVISLAB, SBILIFE, APOLLOHOSP. For 2022-11-03, RELIANCE, HDFCBANK, ICICIBANK, INFY and TCS each had 4 anchor rows (10:00–10:03) and a 15:14 row; NIFTY also had 4 anchor rows and a 15:14 row. | README asserts MIT but no `LICENSE` file exists in the fork or inspected upstream root. Data provenance/feed rights not independently established. | **Diagnostic only; do not ingest/redistribute until licence and source rights are established.** 47/50 file presence is not 98% free-float-weight coverage. |
| [voletiramu/nse-fno-1min-data](https://github.com/voletiramu/nse-fno-1min-data) | 214 F&O underlyings, 1-minute OHLCV, 2024-04-01 to 2026-04-30; GitHub Release archive about 464 MB compressed | README/schema and release metadata reviewed; no data file imported. | States research/educational use, no redistribution as a commercial product, and asks users to respect NSE/Zerodha terms. | Not suitable for a commercial trading data pipeline absent written permission. |
| [Hitjob-Done/indian-stock-market-minute-data](https://huggingface.co/datasets/Hitjob-Done/indian-stock-market-minute-data) | Dataset card search result claims 2,500+ equities/indices, minute 2022–2026, about 715M rows / 10.5 GB compressed | Public card preview fetch returned HTTP 401; no files or samples downloaded. | No licence or redistribution grant verified in this audit. | **Not admitted.** Require readable licence, source provenance and access/usage terms first. |
| [DataPointX data catalogue](https://datapointx.com/data/) | Catalogue claims 76 point-in-time NIFTY 50 stocks, 1-minute OHLCV, 2016-01-04 to 2026-08-31 | Catalogue description only. | Page says downloads are not open yet pending licensing. | Not available as a free data source today; do not scrape or infer access rights. |
| [technovusin/nifty50-historical-data](https://github.com/technovusin/nifty50-historical-data) | NIFTY 50 index 1-minute bars from 2017; 15-second bars from 2026-09 | README reviewed; index-only, not constituent stock data. | Data licence/source rights require separate review. | Potential index-level diagnostic only; not a substitute for stock bars or accepted index ground truth. |

## Dhan constraints confirmed

Dhan's current v2 documentation states that daily candles are available back to a scrip's inception, while minute history is up to five years for active instruments and each intraday request is limited to 90 days. It does not promise minute history for inactive/delisted historic securities. This makes Dhan a plausible primary route for the recent active universe, but it does not close the pre-five-year or inactive-security gap.

## Implications for C1

1. Do not treat a README-only MIT assertion as a verified data licence.
2. Do not merge diagnostic third-party prices into the canonical panel before source rights, timestamp conventions, price adjustment basis, symbol/ISIN mapping and bar-level QA pass.
3. The 47/50 symbol coverage in the 2022 sample is insufficient evidence for the 98% free-float-weight acceptance gate; the missing names' exact point-in-time weights are not established by this source test.
4. Continue authorized Dhan coverage tests for the active universe, and continue free-source research for the missing/inactive historical identities. Do not use the non-commercial weight candidate as trading weights.
5. C1 remains **NOT PASSED**. C2 panel construction and model training remain gated.

## Reproducibility references

- Dhan historical data documentation: https://dhanhq.co/docs/v2/historical-data/
- Dhan historical-data five-year release note: https://dhanhq.co/docs/v2/releases/
- NSE equity-index methodology: https://archives.nseindia.com/content/indices/Method_NIFTY_Equity_Indices.pdf
- NSE IWF reference: https://www.nseindia.com/static/products-services/indices-investible-weight-factors
- Public archive file examples: `2022/NOV/03NOV/03NOV/{RELIANCE,HDFCBANK,ICICIBANK,INFY,TCS,NIFTY}.txt`

**Important:** This report records file discovery and sampled values/row counts only; it does not assert that third-party data are officially sourced, complete, licensed for redistribution, price-adjusted correctly, or suitable for trading.

## Additional Hugging Face minute-data candidate

The original dataset [xxparthparekhxx/indian-stock-market-minute-data](https://huggingface.co/datasets/xxparthparekhxx/indian-stock-market-minute-data) declares MIT in its dataset card and README and reports about 715 million one-minute rows in an approximately 10.5 GB compressed Parquet collection. It describes minute data from 2022–2026 and daily data from 2000–2026, timestamped in UTC, grouped into Parquet shards by symbol. Its README says it is for research, education and backtesting only, is not a live feed, and should not be used as the primary basis for live financial trading. The dataset carries an Upstox tag, but the documentation reviewed here does not explicitly identify the actual upstream feed, collection method or data source. The MIT declaration covers the dataset as published but does not independently establish that the uploader had rights to redistribute the underlying market feed.

Decision: **exploratory candidate only; not admitted to the canonical C1 dataset yet.** A full 10.5 GB bulk download was not run in this step because source provenance and feed rights remain unclear. HF token availability does not remove this data-governance gate. A limited exploratory sample may be considered only after the source owner confirms the data origin and permissions, and it must be reconciled against Dhan and official NSE data before use.

## Official single-date weight snapshot found — 2026-02-27

NSE Indices' March 2026 NIFTY 50 white paper, Exhibit 26, publishes all 50 constituent weights as of 2026-02-27. The 50 published two-decimal values were transcribed to [nifty50_official_weights_2026-02-27.csv](../../data/constituent_weekly/nifty50_official_weights_2026-02-27.csv). Their rounded sum is 100.02%, so values are kept exactly as published, without normalisation.

This materially improves the official cross-check evidence: we now have a licensed-authority source for a single complete date. It does **not** supply the missing 2025-09 onward continuous historical series, the daily publication timestamps, or the earlier 2018–2025 exact weights. It is a reference snapshot, not a substitute for the official monthly/daily IWF history. Full source limitations and the PDF rendering limitation are recorded in [NIFTY50_OFFICIAL_WEIGHT_SNAPSHOT_NOTE.md](../../data/constituent_weekly/NIFTY50_OFFICIAL_WEIGHT_SNAPSHOT_NOTE.md).


## Official monthly weights archive and access terms — 2026-11-01

The official NSE Indices monthly "Market Capitalisation, Weightage, Beta" ZIP family was located. Third-party documentation reports 159 month-end files from June 2013 onward; public research code documents the `mcwb_{mon}{yy}.zip` filename pattern. These figures and the filename convention are a discovery lead, not a direct download or validation in this project.

NSE's research-data policy includes historical reports/index data in its research/analysis basket, while Nifty Indices Terms of Use separately restrict systematic/automated collection without express written consent. The scope of permission for recurring automated retrieval, caching and subsequent use for this research-to-personal-trading workflow is not clear enough to proceed. **No ZIP was requested, downloaded or parsed in this step.**

Automated collection remains disabled pending express written consent or a suitable licence. See [C1_OFFICIAL_WEIGHTAGE_ARCHIVE_TERMS_AUDIT.md](C1_OFFICIAL_WEIGHTAGE_ARCHIVE_TERMS_AUDIT.md). The 2026-02-27 official white-paper snapshot is a single-date reference only; the third-party monthly weights file remains CC BY-NC-SA, provisional and non-commercial. C1 remains NOT PASSED.
