# BUP-01 NIFTY 50 Point-in-Time Membership Dataset

**Status:** membership-only input; not a constituent weight file and not approval to train the bottom-up model by itself.

## Source and licence

The historical interval data is an 83-row NIFTY 50 subset of **Aditya Jha, NSE Historical Membership (Point-in-Time)**:
- Repository: https://github.com/aditya-jha/nse-historical-membership
- Source file: `index_history/data/index_membership_history.csv`
- Upstream data blob SHA (GitHub): `519a9232e125cc044580ec7b90ef5c18475b4f0f`
- Data licence: **Creative Commons Attribution 4.0 International (CC BY 4.0)**, as stated by the upstream `LICENSE-DATA`. The upstream repository's code licence is separate (MIT); this project uses only the licensed data subset.
- Required attribution: Aditya Jha, *NSE Historical Membership (Point-in-Time)*; underlying factual sources identified by the upstream repository as NSE Indices press releases / NSE Exchange circulars. Licence: CC BY 4.0. Changes made: subset to NIFTY 50 and added the verified 2026-09-30 replacement.

## 2026 correction

The upstream NIFTY 50 rows stop at the 2025-09-30 reconstitution. The official NSE Indices press release dated 2026-08-10 states that WIPRO is excluded and BSE is included, effective 2026-09-30 (after the close on 2026-09-29):
https://niftyindices.com/Press_Release/ind_prs10082026.pdf

The official 2026-02-23 semi-annual review press release states no changes were made to NIFTY 50 effective 2026-03-30:
https://niftyindices.com/Press_Release/ind_prs23022026.pdf

Therefore this snapshot applies the one-for-one WIPRO -> BSE update from 2026-09-30. This correction is recorded explicitly in the affected rows; it is not an automated scrape or a current weight series.

## Schema and interval semantics

Columns are preserved from the upstream table: `index_id,index_name,symbol,valid_from,valid_to,weightage,source,source_url,notes`.
Intervals are half-open: a row is active on date (d) when `valid_from <= d < valid_to`; a blank `valid_to` means still active. All `weightage` fields are intentionally blank. Do not infer or impute weights from membership.

## Coverage and validation

- Upstream documentation states NIFTY 50 membership is reliable from 2018-04 onward; earlier rows have known snapshot-floor / walk-back drift. Exclude pre-2018-04 rows from confirmatory modelling unless independently validated.
- This project's local check confirms exactly 50 unique members on each of **103 month-end snapshots** from 2018-04 through 2026-10 (including the 2026-09-30 change).
- This is a cardinality test, not independent source verification of every member/date. The upstream validation report records 29/29 curated famous-transition tests passing; its aggregate cardinality checks across all index families still report pre-2018 failures. Keep these limitations attached to the data.
- No numerical historical free-float weights, ISIN history, or point-in-time security-ID mapping is supplied here. C1 remains blocked until these separate requirements and constituent price coverage pass.

## Usage restrictions

Use this copied subset with the CC BY 4.0 attribution above. Do not fetch/cache/re-publish further NSE website content automatically; the project's existing rights gate stays in force. The manual correction is based on the official press release cited above, not on a bulk report download.
