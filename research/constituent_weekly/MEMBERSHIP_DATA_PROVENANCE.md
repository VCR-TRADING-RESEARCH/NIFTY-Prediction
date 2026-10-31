# BUP-01 NIFTY 50 Point-in-Time Membership Dataset

**Status:** membership-only input; not a constituent weight file and not approval to train the bottom-up model by itself.

## Source and licence

The historical interval data is an 83-row NIFTY 50 subset of **Aditya Jha, NSE Historical Membership (Point-in-Time)**:
- Repository: https://github.com/aditya-jha/nse-historical-membership
- Source file: `index_history/data/index_membership_history.csv`
- Upstream data blob SHA (GitHub): `519a9232e125cc044580ec7b90ef5c18475b4f0f`
- Data licence: **Creative Commons Attribution 4.0 International (CC BY 4.0)**, as stated by the upstream `LICENSE-DATA`. The upstream repository's code licence is separate (MIT); this project uses only the licensed data subset.
- Required attribution: Aditya Jha, *NSE Historical Membership (Point-in-Time)*; underlying factual sources identified by the upstream repository as NSE Indices press releases / NSE Exchange circulars. Licence: CC BY 4.0.
- Project changes: NIFTY 50-only selection; official WIPRO-to-BSE reconstitution update; point-in-time Tata Motors security-symbol correction; temporary zero-price demerger dummy interval; explicit data-role fields.

## Official corrections to the upstream timeline

### 2026 NIFTY 50 reconstitution

The upstream NIFTY 50 rows stop at the 2025-09-30 reconstitution. The official NSE Indices press release dated 2026-08-10 states that WIPRO is excluded and BSE is included, effective 2026-09-30 (after the close on 2026-09-29):
https://niftyindices.com/Press_Release/ind_prs10082026.pdf

The official 2026-02-23 semi-annual review press release states no changes were made to NIFTY 50 effective 2026-03-30:
https://niftyindices.com/Press_Release/ind_prs23022026.pdf

### Tata Motors symbol change and temporary dummy member

The source file used `TMPV` as the symbol from 2014 onward, which is not point-in-time correct. NSE circular NSE/FAOP/70882 dated 2025-10-17 states `TATAMOTORS` changed to `TMPV` effective 2025-10-24:
https://nsearchives.nseindia.com/content/circulars/FAOP70882.pdf

The 2025 Tata Motors demerger also introduced a temporary zero-price index placeholder:
- NSE Indices press release dated 2025-10-07 says `DUMMYTATAM` (TML Commercial Vehicles) was included at zero price, without divisor adjustment, in NIFTY 50 effective 2025-10-14 (close of 2025-10-13):
  https://www.niftyindices.com/Press_Release/ind_prs07102025.pdf
- NSE Indices press release dated 2025-11-13 says the demerged TMCV entity was listed on 2025-11-12 and `DUMMYTATAM`/TMCV was excluded from NIFTY indices effective 2025-11-17 (close of 2025-11-14):
  https://www.niftyindices.com/Press_Release/ind_prs13112025.pdf

The project therefore records:
- `TATAMOTORS` up to 2025-10-23;
- `TMPV` from 2025-10-24 onward;
- `DUMMYTATAM` from 2025-10-14 through 2025-11-16, marked `member_type=zero_price_dummy` and `market_data_required=FALSE`.

The dummy remains in the index-membership ledger for auditability, but must **not** enter the tradable-equity stock panel or be assigned an invented market price. This temporary placeholder explains why the index membership ledger has 51 entries at the 2025-10-31 month-end snapshot.

## Schema and interval semantics

The original fields are retained and two safety fields are added:
`index_id,index_name,symbol,valid_from,valid_to,weightage,source,source_url,notes,member_type,market_data_required`.

Intervals are half-open: a row is active on date (d) when `valid_from <= d < valid_to`; a blank `valid_to` means still active. Normal securities are marked `equity_security` / `TRUE`; the temporary zero-price dummy is marked `zero_price_dummy` / `FALSE`. All `weightage` fields are intentionally blank. Do not infer or impute weights from membership.

## Coverage and validation

- Upstream documentation states NIFTY 50 membership is reliable from 2018-04 onward; earlier rows have known snapshot-floor / walk-back drift. Exclude pre-2018-04 rows from confirmatory modelling unless independently validated.
- Project output contains **86 interval rows and 85 distinct symbols** after the above official corrections.
- The offline regression checks 103 month-end dates from 2018-04-30 through 2026-10-31: 102 snapshots contain 50 unique members; the 2025-10-31 snapshot contains 51 entries because the official temporary zero-price dummy was active. All 103 dates match the documented expected cardinality.
- GitHub Actions run `41184751617` completed successfully: **6 tests passed**. It is an offline integrity check, not independent verification of every historical membership event or a market-data validation.
- The upstream validation report records curated transition checks passing but discloses pre-2018 drift. Keep these limitations attached to the data.
- No numerical historical free-float weights, ISIN history, or complete point-in-time security-ID mapping is supplied here. C1 remains blocked until these separate requirements and constituent price coverage pass.

## Usage restrictions

Use this copied subset with the CC BY 4.0 attribution above. Do not fetch/cache/re-publish further NSE website content automatically; the project's existing rights gate stays in force. The manual corrections above are based on specific official press releases/circulars cited above, not on a bulk report download.

## Audit correction — Tata Motors demerger identity timeline

A subsequent corporate-action review found that the source had assigned the post-demerger `TMPV` ticker to historical records back to 2014. That alias was not point-in-time correct. The project CSV is corrected using NSE circular NSE/FAOP/70882: `TATAMOTORS` is retained through 2025-10-23 and `TMPV` starts 2025-10-24.

The project also now records the official temporary zero-price placeholder `DUMMYTATAM` from 2025-10-14 through 2025-11-16, with `member_type=zero_price_dummy` and `market_data_required=FALSE`. NSE Indices stated that the dummy was added at zero price from 2025-10-14 (close 2025-10-13) and excluded effective 2025-11-17 (close 2025-11-14). This placeholder is retained for index-membership audit, never treated as a tradable equity or assigned a stock price.

The corrected 103-month-end test expects 50 unique constituents for 102 dates and 51 entries at 2025-10-31 because the official zero-price dummy remained active then. The earlier claim that all 103 dates should contain exactly 50 members is superseded. The updated six-test suite has been committed; the post-correction Actions run is pending and must be checked before the revised test suite is called CI-passed.
