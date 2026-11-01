# C1 Special-Session Calendar Reconciliation

**Date:** 2026-11-02  
**Disposition:** Calendar classifications verified; missing bars remain unresolved.  
**Scope:** Seven residual daily OHLCV gaps in the 2018-04-01–2026-10-30 member-session audit.

## Findings

The seven reported gaps are not ordinary non-trading holidays. Six dates are documented special live equity sessions and must remain in the expected-session denominator:

| Security | Date | Exchange session | Evidence | Treatment |
|---|---|---|---|---|
| HDFC | 2018-11-07 | Diwali Muhurat, 17:30–18:30 | NSE circular NSE/CMTR/39216, 2018-10-23 | Valid special session; missing daily bar unresolved |
| HDFC | 2019-10-27 | Diwali Muhurat, Sunday; 1-hour session | NSE 2019 holiday notice and NSE Market Pulse historical Muhurat dates | Valid special session; missing daily bar unresolved |
| HDFC | 2020-02-01 | Union Budget live session, 09:15–15:30 | NSE circular NSE/CMTR/43290, 2020-01-22 | Full regular-hours session; missing daily bar unresolved |
| HDFC | 2020-11-14 | Diwali Muhurat, 18:15–19:15 | NSE circular NSE/FAOP/46231, 2020-11-02; NSE Market Pulse | Valid special session; missing daily bar unresolved |
| HDFC | 2021-11-04 | Diwali Muhurat, 18:15–19:15 | NSE circular NSE/CMTR/50050, 2021-10-21 | Valid special session; missing daily bar unresolved |
| HDFC | 2022-10-24 | Diwali Muhurat, 18:15–19:15 | NSE circular NSE/FAOP/54024, 2022-10-11 | Valid special session; missing daily bar unresolved |
| TATAMOTORS | 2025-10-21 | Diwali Muhurat, 13:45–14:45 | NSE circular NSE/CMTR/70319, 2025-09-22 | Valid special session; missing daily bar unresolved |

The 2019, 2020, 2021 and 2022 dates are also identified as Muhurat trading dates in NSE Market Pulse (November 2024). NSE's official circulars establish the 2018, 2021, 2022 and 2025 session timings. The 2020-02-01 session was a full regular-hours trading day, not a holiday.

## Data-quality decision

1. Do not remove any of the seven dates from the expected-session denominator.
2. Do not impute or synthesize a daily OHLCV bar.
3. For Muhurat sessions, retain the actual exchange session time in the calendar metadata; do not apply ordinary 09:15–15:30 intraday assumptions to those dates.
4. For 2020-02-01, treat the session as full-day and verify HDFC against Dhan daily history plus an independently sourced NSE/BSE bhavcopy or licensed source.
5. Re-run the targeted source reconciliation for each exact security/date. A source match must agree on symbol/security identity, series, session date and OHLCV validity. Do not accept a fallback solely because a same-date index or another stock has data.
6. This note does not alter the registered plan, coverage gate, C1 status or corporate-action gate.

## Public evidence

- NSE, circular NSE/CMTR/39216 (2018 Muhurat session): https://www.smifs.com/files/downloads/636760073765330180_CMTR39216%2023Oct2018%20Muhurat%20Trading%20Session%20on%20Account%20of%20Diwali.pdf
- NSE Market Pulse, November 2024, Figure 116/Table 27 lists Muhurat sessions on 2018-11-07, 2019-10-27, 2020-11-14, 2021-11-04 and 2022-10-24: https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Market%20Pulse_November%202024_FINAL_3.pdf
- NSE, circular NSE/CMTR/43290 (2020-02-01 Budget trading): https://www.achiieversequitiesltd.com/wp-content/uploads/2019/04/Live-trading-session.pdf
- NSE, circular NSE/CMTR/50050 (2021 Muhurat session): https://archives.nseindia.com/content/circulars/CMTR50050.pdf
- NSE, circular NSE/FAOP/54024 (2022 Muhurat session): https://archives.nseindia.com/content/circulars/FAOP54024.pdf
- NSE, circular NSE/CMTR/70319 (2025 Muhurat session): https://nsearchives.nseindia.com/content/circulars/CMTR70319.pdf

## Conclusion

The earlier classification of these dates as generic residual missing sessions was insufficiently specific. The exchange calendar explains why generic weekday and daytime-session rules are unsafe, but it does not explain away the absent daily bars. The audit remains 106,385/106,392 (99.9934%) until each missing security/date is sourced or explicitly excluded under a pre-registered, defensible data rule. C1 remains PARTIAL / NOT PASSED and C2 remains locked.
