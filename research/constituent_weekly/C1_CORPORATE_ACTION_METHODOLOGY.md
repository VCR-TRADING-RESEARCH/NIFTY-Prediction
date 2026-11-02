# C1 corporate-action methodology and label-continuity rules

**Plan scope:** BUP-01 research plan v1.3  
**Window:** 2018-04-01 to 2026-10-30  
**Status:** Methods specified; complete issuer/event-level factor validation remains OPEN.  
**Purpose:** Prevent mechanical corporate-action gaps, stale-symbol joins and future information from contaminating constituent features and weekly expiry labels.

## 1. Keep the research target distinct from trading-contract adjustment

The registered stock target is a point-in-time **price return** from the first eligible 10:00 IST anchor to the 15:15 expiry proxy. It is not a total-return target, and it is not an F&O strike/lot adjustment calculation. The actual NIFTY price-index return remains the index label.

A separate dividend-reinvested total-return sensitivity may be reported, but it must not replace the primary price-return label. NSE Indices explains that price indices measure constituent price movement, while total-return indices additionally incorporate dividends reinvested after the ex-date. For special dividends and short-notice cases, apply the exact NIFTY index methodology effective on the relevant date; do not hard-code a single percentage threshold across all years or index families.

## 2. Event-specific policy

| Event family | Required treatment for BUP-01 | Automatic adjustment allowed now? |
|---|---|---|
| Ordinary cash dividend | Retain the primary price-return observation without reinvesting ordinary cash dividends. Add a separately labelled total-return sensitivity only after validating the cash payout, ex-date and prior close. | No |
| Special / extraordinary dividend | Determine treatment from the NIFTY price-index methodology effective on that date, including the relevant notice/threshold rule. Keep separate from ordinary dividend treatment. | No |
| Stock split / consolidation | Verify old and new face value, share-count ratio, ex-date and ISIN/security continuity. Restate historical per-share prices and quantities consistently; test value continuity across the ex-date. | No, pending event-level verification |
| Bonus issue | Verify the source ratio semantics (new shares : existing shares), ex-date and security continuity. For A new shares for every B old shares, the theoretical ex-bonus price ratio is B/(A+B), but apply only after the issuer/exchange notice confirms A and B. | No |
| Rights issue | Require entitlement ratio, subscription price, cum-date price and terms. The theoretical ex-rights price is (B × Pcum + A × Pissue)/(A+B), where A new shares are offered for B existing shares. The adjustment must also state whether it models price-only or a shareholder who exercises/sells the right. | No |
| Buyback | Do not insert a generic mechanical price factor. Record the event separately; tender acceptance, price and shareholder participation can differ from an ordinary split/dividend. | No |
| Merger / demerger / amalgamation | Retain predecessor and successor securities separately. Require effective date, scheme ratio, cash consideration, listing date and ISIN evidence. Exclude any target cycle crossing an unresolved structural event. Never stitch raw prices by ticker alone. | No |
| Symbol rename | Alias the same security only when issuer/ISIN evidence supports continuity and the effective date is known. A ticker match is not proof of a stable security. | Only after identity check |
| AGM / other / unknown | Inspect the original subject and issuer/exchange notice; classify individually. | No |

## 3. Formula controls

Candidate calculations are diagnostics, not instructions to apply factors blindly:

- **Cash dividend total-return sensitivity:** stock total return over an ex-date interval is derived from post-ex price plus the cash amount relative to the prior cum-date close, after checking the applicable share basis and tax/withholding assumptions. The primary price-return label does not add the dividend.
- **Split:** for a pure face-value split with unchanged issuer capital, the ex-basis price multiplier is the new share count basis relative to the old basis. If face value changes from FV_old to FV_new, the candidate multiplier is FV_new/FV_old; independently verify the actual share-ratio notice and test price × shares value continuity.
- **Bonus:** if the notice says A new shares for every B old shares, the candidate ex-bonus price multiplier is B/(A+B). Do not assume the source field order means A:B until confirmed.
- **Rights:** calculate theoretical ex-rights price from the verified issue terms. With A new shares for B existing shares, TERP = (B × Pcum + A × Pissue)/(A+B). Price-only return, right-sale value and subscription cash must not be mixed.
- **Merger / demerger:** no universal factor. Scheme ratios, cash components, separate successor instruments and index divisor treatment require issuer- and date-specific adjudication.
- **Buyback:** no universal factor; participation and consideration differ from a mechanical share-count event.

**Important:** NSE's F&O corporate-action circulars describe adjustments to derivative strikes, positions and market lots to preserve contract value. Those contract adjustment factors are not automatically historical equity price factors. The audit must not copy an F&O factor into stock OHLC series without deriving the correct equity basis.

## 4. Point-in-time and leakage safeguards

1. Match actions to the actual NSE symbol active on the ex-date using the effective-dated alias ledger; independently reconcile issuer and ISIN. Do not infer identity from a symbol alone.
2. Keep action announcement/record/ex-dates distinct. A model feature available at the 10:00 forecast timestamp may use only information already public by that timestamp.
3. For a feature lookback, only apply an adjustment whose event and required terms were available as of the historical feature timestamp. For outcome labels, identify events falling between anchor and expiry and apply the pre-registered event policy.
4. Missing event terms, conflicting ISINs, ambiguous ratios, duplicate actions, or missing prior closes make the affected adjustment unresolved; exclude the affected security-cycle rather than forward-fill, fabricate or guess.
5. Validate each action by a value-continuity test and an independent event-source check. Keep raw source data private/encrypted; publish only sanitised aggregates and method decisions.
6. The action feed is a discovery source. Its publisher warns that the dataset licence does not grant exchange-data rights; personal-use terms and exchange terms apply independently. No raw source redistribution or client/business use is in scope.

## 5. Acceptance gates before C2

C1 action gate remains NOT PASSED until all of the following are evidenced:

- Coverage of all point-in-time NIFTY 50 member actions in the target window, including zero-event checks and symbol/ISIN identity.
- Independent exchange/issuer confirmation for all candidate split, bonus, rights, cash dividend, special dividend, buyback, merger and demerger events that affect a member label or feature history.
- Dated, reproducible adjustment decisions with factor formula, inputs, units, sign, event date, share basis and price/volume transformation.
- Unit/property tests for price × share value continuity, reverse/split ratios, bonus ratios, rights TERP and dividend price/total-return separation.
- Affected-cycle exclusion ledger and audit of every omitted member label.
- Independent reviewer re-performance and no unresolved material action/identity issue.

The catalogue alone is not sufficient to pass C1 or unlock C2.

## 6. Primary methodology references

- [NSE — Adjustments in case of Corporate Actions](https://www.nseindia.com/static/products-services/equity-derivatives-corporate-actions-adjustments): describes corporate-action families and timing for derivative-contract adjustments; it is not a substitute for equity price-return methodology.
- [NSE — Total Returns Index](https://www.nseindia.com/static/products-services/indices-total-returns-index): explains the distinction between price-index returns and dividend-reinvested total returns.
- [NSE Indices — Equity Index Methodology (May 2026)](https://archives.nseindia.com/content/indices/Method_NIFTY_Equity_Indices.pdf): dated rules for price-index special dividends and TR/NTR calculation.
- [SEBI — adjustment principles for corporate actions](https://www.sebi.gov.in/legal/circulars/dec-2002/adjustment-in-stock-option-contracts-and-single-stock-future-contracts-at-the-time-of-corporate-actions_16776.html): general principle that contract value should be preserved across cum/ex dates.
- [TejHQ Indian Markets dataset card](https://huggingface.co/datasets/tejhq/indian-markets): action schema, raw vs adjusted data scope and caveats. Its adjusted price tree does not provide a universal solution for rights, buybacks or merger/demerger events.
