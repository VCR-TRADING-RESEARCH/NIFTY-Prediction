# C1 historical NIFTY 50 weights — source audit

**Audit date:** 2026-11-01  
**Gate:** C1 / BUP-01  
**Decision:** Provisional candidate found; not yet cleared as official ground truth or for commercial use.

## Candidate dataset

- **Dataset:** AMP4010, *Historical Nifty 50 Constituent Weights (Rolling 20-Year Window)*.
- **Creator/citation:** Sukrit Bera (2025), Figshare DOI [10.6084/m9.figshare.30217915](https://doi.org/10.6084/m9.figshare.30217915).
- **File:** [weights.csv](https://huggingface.co/datasets/AMP4010/Historical_Nifty_50_Constituent_Weights_20Y/resolve/main/weights.csv).
- **Pinned source revision:** `c15498388ae4d346f42291c4e5937235e56ae67c`.
- **Reported coverage:** 2008-01-31 to 2025-08-31; 216 dated rows; 100 ticker columns.
- **Reported integrity:** the dataset card's validation reports every row totals 100% to within 1e-6.
- **Reported source/frequency:** official Nifty Indices reports; month-end plus event-driven observations around reconstitutions.

## Important limitations and permissions

The dataset author's own documentation says some intra-month entrant/exit weights are extrapolated, corporate actions are adjusted by the author, and 2013 rebalancing weights required a special recalculation. Therefore the CSV is not a verbatim official daily IWF feed. Row sums equal 100% by construction and do not, alone, establish the truth of each stock weight.

The dataset is licensed **CC BY-NC-SA 4.0**. Attribution and ShareAlike apply, and commercial use is not permitted. The source may support provisional non-commercial research only. Do not use it in a commercial product/service or treat it as cleared for monetized deployment. If the intended use changes, obtain a separate licence or official licensed weights.

The C1 workflow downloads the pinned file only when the local cache is absent; subsequent runs validate the cache rather than downloading it again. The validation checks valid/ascending unique dates, at least 50 ticker columns, numeric non-missing weights in [0,100], exact row totals within 1e-6, and records a SHA-256 digest. It does not certify the author's individual historical estimates.

## Official cross-check path

NSE Indices provides an archive of daily/monthly reports. The report selector includes **“Market Capitalisation, Weightage, Beta for NIFTY 50 & NIFTY Next 50”** and **“Indices - Market Capitalisation & Weightage”**. These are the preferred references for sample validation and for filling 2025-09 onward, subject to the applicable NSE terms/licence. NSE's index-data subscription specifically describes constituent identifiers, market capitalisation, weights and prices as data products.

Relevant official/public references:
- [NSE All Reports](https://www.nseindia.com/all-reports)
- [Nifty Indices historical reports](https://www.niftyindices.com/reports)
- [NSE index-data subscription](https://www.nseindia.com/static/nse-indices/index-data-subscription)
- [NIFTY 50 methodology/index page](https://www.niftyindices.com/indices/equity/broad-based-indices/nifty--50)

## Acceptance rule

This candidate is **not** sufficient by itself to pass C1. Before C2, reconcile a sample of historical dates against official reports, check event-date weights against membership effective dates, close the 2025-09 onward gap using an authorized source, verify all historical identifiers/corporate actions, and complete constituent bar coverage. Do not backfill missing weights using equal weights or current weights.
