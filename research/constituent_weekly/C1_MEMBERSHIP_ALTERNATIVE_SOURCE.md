# NIFTY 50 historical membership proxy — source and licence

## Primary dataset
- Repository: https://github.com/aditya-jha/nse-historical-membership
- File: index_history/data/index_membership_history.csv
- Upstream file blob SHA: `519a9232e125cc044580ec7b90ef5c18475b4f0f`
- Data licence: CC BY 4.0 as declared in the upstream repository's `LICENSE-DATA`.
- Code licence: MIT (not applicable to the copied data file).
- Required attribution: Aditya Jha, `nse-historical-membership`; underlying facts derived by that repository from published NSE index press releases/circulars.
- Copied subset: NIFTY 50 only (index_id 217), 83 upstream membership intervals covering 2014-01-01 through the 2025-09-30 rebalance event. The upstream file has no historical numerical weightage values; this is membership only.
- Upstream coverage caveat: project README reports high confidence from 2018 onward and best-effort pre-2018; some pre-2018 index reconstructions have cardinality drift. Its NIFTY 50 latest membership event in the cached version is 2025-09-30.

## Local dated update
The upstream cached open interval for WIPRO was closed on 2026-09-30 and a new BSE interval was added from 2026-09-30, using the independently hosted reprint of the August 2026 index-review notice:
https://noticeblue.com/circulars/e56dd516-fb39-4f99-8f84-4b8bd582f5c2

The reprint states BSE inclusion and WIPRO exclusion effective 2026-09-30 (after 2026-09-29 close). The FundTracker India Nifty BeES portfolio page also shows BSE as new and WIPRO as exited in its September 2026 holdings comparison:
https://fundtrackerindia.com/scheme/nippon-india-etf-nifty-50-bees

This is a **membership proxy** and independent cross-check, not an official weights series. The added update is explicitly tagged `secondary_reprint`; the original upstream interval provenance is retained separately in `source` and `source_url`.

## Structural checks completed before import
- 83 upstream NIFTY 50 intervals, plus one BSE inclusion interval.
- Membership-set cross-check against the project's 86-row C1 ledger matches **103/103 month-ends** from 2018-04-30 through 2026-10-31 after applying two explicit normalizations: map upstream terminal symbol TMPV back to TATAMOTORS before its 2025-10-24 effective rename, and exclude the temporary non-tradable DUMMYTATAM zero-price placeholder from the tradable-stock comparison. The membership set is 50 on 102 dates and 51 on 2025-10-31 when the official temporary placeholder is counted. CI regression [run 41289992040](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41289992040) passed.
- 50 open membership intervals as at 2026-11-01; BSE is active and WIPRO is inactive.
- Historical `weightage` values are blank by design. Do not use equal weights or fill them from this file.

## Intended use
Use for survivorship-bias-aware membership and membership/identifier joins only. Historical weights must be separately sourced/reconstructed from an independently verified proxy basket. Keep raw shareholding/XBRL, ETF holdings and index-membership facts as distinct source classes.
