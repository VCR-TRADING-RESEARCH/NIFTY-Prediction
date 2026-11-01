# C1 historical symbol identity and corporate-action review

**Review date:** 2026-11-01  
**Confirmatory membership source starts:** 2018-04-01. The Dhan minute-data floor is separately applied by the continuous coverage auditor.

The point-in-time membership file uses a canonical symbol in some later rename chains. The new [security alias history](../../data/constituent_weekly/security_alias_history.csv) translates those canonical member keys to the exchange symbol actually traded on each date. The [security corporate-action event ledger](../../data/constituent_weekly/security_corporate_action_events.csv) separately records events where raw price continuity must not be assumed. A symbol alias is not proof that two different securities are the same security.

| Canonical member key | Actual point-in-time NSE symbol | Effective dates relevant to this study | Identity / action handling |
|---|---|---|---|
| LTM | LTIM | LTIM from 2022-12-05 through 2026-02-26; LTM from 2026-02-27 | The NIFTY 50 membership interval 2023-07-13 to 2024-09-30 was traded as LTIM, not LTM. Map LTIM to the current LTM scrip-master identity for historical candles; do not splice pre-merger LTI or Mindtree price histories into LTIMindtree. |
| ETERNAL | ZOMATO | ZOMATO through 2025-04-08; ETERNAL from 2025-04-09 | Same listed issuer/security rename; the membership interval begins 2025-03-28, so the first member week must be labelled ZOMATO. Rename alone does not require a price adjustment. |
| TMPV | TATAMOTORS | TATAMOTORS through 2025-10-23; TMPV from 2025-10-24 | The demerger ex-date was 2025-10-14. Do not assume continuity of raw price levels across that date. Coverage auditor excludes a constituent target cycle crossing the ex-date; DUMMYTATAM is non-tradable and excluded. |
| TATACONSUM | TATAGLOBAL | TATAGLOBAL through 2020-02-26; TATACONSUM from 2020-02-27 | Scheme/name/symbol event. Raw pre/post scheme levels require adjustment validation. NIFTY 50 membership for this constituent starts after the event. |
| HDFC | HDFC | HDFC Ltd is a distinct predecessor security through the merger effective 2023-07-01 | Dhan legacy ID 1330 was probed on 2022-10-31 and 2023-06-30. Do not map HDFC Ltd onto HDFCBANK or concatenate their raw price histories. The expiry cycle crossing 2023-07-01 excludes HDFC's return target. |
| MCDOWELL-N | MCDOWELL-N | 2014-era membership only | Changed to UNITDSPR in 2024; outside the 2018-04 confirmatory membership sample and therefore not a live C1 minute-coverage blocker. |
| JPASSOCIAT | JPASSOCIAT | 2014-era membership only | Outside the confirmatory window; no successor substitution. |
| RANBAXY | RANBAXY | 2014-era membership only | Merged into Sun Pharma in 2015, outside the confirmatory window; no raw price stitching to SUNPHARMA. |
| DUMMYTATAM | DUMMYTATAM | 2025-10-14 to 2025-11-17 in membership event ledger | Zero-price non-tradable placeholder; must never be counted as a tradable member or sent to Dhan. |

## Primary evidence

- NSE circular [LTI → LTIM, effective 2022-12-05](https://archives.nseindia.com/content/circulars/CML54604.pdf).
- LTIMindtree company release confirming NIFTY 50 inclusion under symbol LTIM on 2023-07-13: [release](https://www.ltm.com/news-events/press-releases/2023/ltimindtree-enters-the-nifty-50-index).
- NSE Indices review dated 2024-08-23: [LTIM and DIVISLAB removed effective 2024-09-30](https://www.niftyindices.com/Press_Release/ind_prs23082024.pdf).
- NSE circular [LTIM → LTM, effective 2026-02-27](https://nsearchives.nseindia.com/content/circulars/FAOP72935.pdf).
- NSE circular [ZOMATO → ETERNAL, effective 2025-04-09](https://nsearchives.nseindia.com/content/circulars/CML67420.pdf).
- NSE circular [TATAMOTORS → TMPV, effective 2025-10-24](https://nsearchives.nseindia.com/content/circulars/FAOP70882.pdf); NIFTY Indices demerger placeholder notice: [2025-10-07](https://www.niftyindices.com/Press_Release/ind_prs07102025.pdf).
- NSE/HDFC Bank: [HDFC Ltd merger effective 2023-07-01](https://www.hdfc.bank.in/press-release/2023/q2/hdfc-ltd-to-merge-into-hdfc-bank-effective-july-1-2023); Dhan legacy HDFC security details: [Dhan portfolio API example](https://dhanhq.co/docs/v2/portfolio/).
- NSE circular [TATAGLOBAL → TATACONSUM, effective 2020-02-27](https://www.steelcitynettrade.com/Circulars/Change%20in%20Symbol%20and%20Name%20of%20the%20Company%20-%20Tata%20Global%20Beverages%20Limited.pdf).
- Earlier outside-window identity events: [JPASSOCIAT suspension](https://nsearchives.nseindia.com/content/circulars/CML73342.pdf), [delisting](https://nsearchives.nseindia.com/content/circulars/CML74660.pdf), [Ranbaxy merger completion](https://www.daiichisankyo.com/media/press_release/detail/index_3515.html), [MCDOWELL-N → UNITDSPR](https://nsearchives.nseindia.com/content/circulars/FAOP62365.pdf).

## C1 interpretation and remaining limitations

- Current Dhan scrip-master security IDs are used only to locate an instrument's history; they do not prove that the current symbol was traded on every historic date.
- Dhan legacy HDFC ID 1330 is explicitly sampled. LTIM history is resolved by its current LTM identity using the effective-dated alias. TATAMOTORS history is resolved through the current TMPV identity, with the demerger crossing week excluded.
- The event ledger is a targeted identity/major-merger/demerger/symbol audit, not an exhaustive dividend, split, bonus, rights issue or every issuer action adjustment ledger. Those are still needed before adjusted-return labels are accepted.
- Coverage flags are not proof of a valid total-return adjustment. C1 identity/action governance remains PARTIAL until the full corporate-action ledger and action-aware stock returns pass independent review.
