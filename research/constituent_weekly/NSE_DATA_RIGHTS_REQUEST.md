# NIFTY constituent IWF / historical weight data — rights request draft

**Purpose:** Obtain written permission and/or a licence for BUP-01, the bottom-up NIFTY 50 weekly-expiry research track.

**Do not send until the requester confirms the intended legal entity, contact details and commercial-use terms.** This is a draft template only; no request has been sent.

## Requested data

Please identify the relevant NSE Indices / NSE Data product(s) and confirm availability for the period needed for a historical weekly study beginning in 2021 through the latest available date:

1. Point-in-time NIFTY 50 constituent list with effective-from/effective-to dates, stable company identifiers, ISINs, NSE security IDs, and dated symbol/ISIN transitions.
2. Official historical NIFTY 50 constituent weights and/or IWFs, preferably as effective-dated monthly/rebalance snapshots with the original publication/broadcast timestamp, revision/version history and correction metadata.
3. The underlying shareholding-pattern / IWF input fields or certified IWF values needed to trace all methodology exclusions and reconcile weights.
4. Corporate action and index-maintenance information needed to replay the official index basket and divisor treatment.
5. Data dictionary, methodology versions, rounding precision, calculation dates and known coverage limitations.

Please advise whether the official monthly “Market Capitalisation, Weightage, Beta” reports are the correct product, or whether a separate constituent-weight / IWF time-series feed exists.

## Intended use that must be covered

The project is an internal quantitative research and algorithmic-trading research effort. The data would be used to:
- construct point-in-time features and historical constituent baskets;
- calculate and validate weekly constituent returns and weighted index forecasts;
- train and evaluate research models using chronological, leakage-controlled backtests;
- test candidate trading strategies internally after a separate cost/execution gate;
- publish the research methodology, aggregate statistical results and non-reconstructive charts/tables.

No raw vendor data, complete weight tables, individual-level shareholder information or other licensed source records would be published or redistributed. Raw records would be held in an access-controlled private store; the public GitHub repository would contain only code, provenance metadata, rights status and non-reconstructive QA summaries. Please specify any further restrictions on derived outputs, model parameters, aggregate statistics, internal use, retention and archival.

## Rights / technical questions

Please confirm in writing:

1. Whether the licence expressly permits automated retrieval/API access and scheduled incremental refreshes (no website scraping unless explicitly authorised).
2. Whether raw files may be cached and retained in an access-controlled private data store, and for how long.
3. Whether the permitted use includes internal model training, quantitative backtesting and algorithmic trading decisions with the requester’s own capital.
4. Whether derived features, model predictions, non-reconstructive aggregate statistics and research manuscripts may be retained/published.
5. Whether redistribution of source records is prohibited and whether any derived-output sharing limits apply.
6. Whether the data includes actual IWF values, or only market-cap/weight snapshots, and whether all 22 IWF exclusions are resolved by NSE methodology before weights are published.
7. Historical coverage start/end, snapshot cadence, effective-date semantics, publication/broadcast timestamps and revision history.
8. Whether a data licence is available for an individual researcher / small trading research project, its price, term, user count and renewal requirements.
9. Whether the data may be accessed through a permitted machine-readable API or designated secure download endpoint.
10. Whether historical security-ID/ISIN mappings, delisted constituents and corporate-action-adjusted index divisor data are included.

## Draft email

**To:** indices@nse.co.in (please redirect to the appropriate NSE Indices / NSE Data licensing team if needed)

**Subject:** Request for historical NIFTY 50 constituent weights / IWF data and permitted quantitative research use

Dear NSE Indices / NSE Data team,

I am conducting a point-in-time quantitative research project on NIFTY 50 constituent-level weekly expiry prediction. The work requires historical NIFTY 50 constituent membership, official free-float IWF/constituent weights, security identity history and the relevant publication/effective timestamps.

Could you please advise the appropriate historical data product and provide a quotation and licence terms covering internal quantitative research, model training, backtesting and algorithmic trading decisions using the requester’s own capital? The project will not redistribute raw records. Raw data can be held in a private access-controlled store, and public research outputs can be limited to non-reconstructive aggregate statistics and methodology, subject to your terms.

In particular, I would appreciate confirmation that the data includes point-in-time numerical IWF/weights (not only current constituents or selected top-ten factsheet weights), the historical coverage period, publication/revision timestamps, ISIN/security-ID history and whether the weights reflect the full official IWF methodology.

Please also specify whether automated retrieval and private caching are permitted, retention limits, derivative-output/publication restrictions and the applicable fees.

If there is a designated request form or another contact for this data product, please direct me accordingly.

Regards,

[Requester name]  
[Organisation / legal entity, if applicable]  
[Contact email]  
[Contact number]

## Repository gate

Until written terms are obtained and reviewed:
- Do not scrape NSE/Nifty Indices websites or automate retrieval of the historical weight archives.
- Do not import the non-commercial AMP4010 dataset into the commercial/algorithmic-trading track.
- Do not import the category-level XBRL CSV from the third-party GitHub repository until its nested parsed-file licence scope is explicitly confirmed and its 22-exclusion mapping is independently tested.
- Do not place licensed raw data in this public repository or its public Actions cache.
- Keep BUP-01 C1 blocked; do not train/aggregate a confirmatory bottom-up index model.
