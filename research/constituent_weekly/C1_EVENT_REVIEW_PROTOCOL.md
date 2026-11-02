# C1 Event-Level Corporate-Action Review Protocol

**Created:** 2026-11-03  
**Track:** BUP-01 / C1  
**Status:** ACTIVE — protocol only; no new events are accepted or adjusted by this document  
**Plan impact:** None. The registered research plan remains locked. This document operationalises the existing C1 identity and corporate-action gate.

## 1. Verified starting point

The latest sanitised catalogue (2026-11-01) contains 18,361 deduplicated NSE event candidates, of which 711 match point-in-time NIFTY 50 member intervals. The matched event classes are:

| Event class | Matched candidates | Default treatment |
|---|---:|---|
| Dividend | 625 | Do not apply a mechanical adjustment to a price-index target. Confirm amount/date only when an event feature or data-quality check requires it. |
| Buyback | 20 | No mechanical price factor. Treat as a known-event feature only when public by the forecast cutoff. |
| Bonus | 19 | Verify ratio and ex-date from issuer evidence; compare Dhan adjusted OHLC with raw reference around event; verify security identity. |
| Split | 9 | Verify face-value ratio and ex-date; compare adjusted/raw OHLC; verify ISIN transition. |
| Rights | 6 | Verify entitlement ratio, subscription price and ex-date; compute TERP only if required by the chosen price-series definition; otherwise exclude affected stock-cycle rows pending review. |
| Merger/demerger | 3 | Verify scheme, effective date, consideration and predecessor/successor identity; never stitch securities by ticker alone. |
| AGM/other | 29 | Classify from issuer evidence; no automatic price factor. |

Counts are discovery-catalogue counts, not verified corporate actions. They must not be interpreted as completed reviews.

## 2. Event handling rules

### 2.1 Preserve price-index semantics

The target is NIFTY 50 **price-index direction**, not total-return-index direction. Ordinary cash dividends therefore must not be mechanically reinvested or added back to the target return. Dividend events may be retained as known-event covariates only if their announcement/ex-date information was available by the forecast timestamp. A dividend is not, by itself, proof of a bad price bar.

### 2.2 Avoid double adjustment

Dhan documents daily historical OHLCV as adjusted for bonus and split events. The project must not apply a second split/bonus factor to already adjusted Dhan bars. Validate representative events by comparing Dhan adjusted bars with a permitted raw reference and the issuer/exchange ratio. If source series cannot be reconciled, mark the affected symbol-date window unresolved and exclude it from confirmatory stock features/labels.

### 2.3 Rights and complex restructurings

Rights issues require the entitlement ratio and subscription price to calculate a theoretical ex-rights price (TERP). Mergers/demergers require scheme-specific exchange ratios and effective dates. No generic factor, ticker substitution, or price-level stitching is permitted. Unresolved events trigger explicit affected-window exclusions.

### 2.4 Identity is a separate gate

A price-factor match does not prove that the security identity is correct. Validate point-in-time symbol, ISIN, issuer and Dhan instrument mapping independently. Known HDFC and Tata Motors action-crossing cycles remain excluded as documented unless their identity/action evidence is independently closed.

## 3. Review workflow

1. Build a private, ephemeral queue from the 711 matched candidates. Keep raw event rows, raw prices, ISINs, cash amounts and source subjects out of the public repository and public workflow artifacts.
2. Join each event to the point-in-time membership interval and the weekly forecast/expiry cycle it intersects. Distinguish events announced before the 10:00 forecast cutoff from events first disclosed afterwards.
3. Prioritise all 37 bonus/split/rights/merger-demerger candidates, then the 20 buybacks and 29 AGM/other candidates. Dividends are handled under the price-index rule above; only events with material data/feature implications require issuer-document verification.
4. For every candidate requiring mechanical treatment, collect issuer-first-party evidence for the event terms and effective date. Use exchange circulars only where their terms permit the intended research use. Dhan adjusted-price checks are corroboration, not proof of event terms or security identity.
5. Produce a private event-level decision ledger with statuses: VERIFIED_NO_ADJUSTMENT, VERIFIED_FACTOR, EXCLUDE_AFFECTED_WINDOW, IDENTITY_UNRESOLVED, SOURCE_UNRESOLVED, or NOT_RELEVANT_TO_TARGET.
6. Publish only aggregate counts, pass/fail totals, non-reconstructive QA summaries and hashes. Never publish raw TejHQ rows, raw Dhan prices, ISINs, personal-use-only source extracts or secrets.
7. Re-run C1 acceptance tests. C1 remains PARTIAL until all in-scope unresolved identity/action cases are either verified or explicitly excluded under the locked minimum-coverage rule.

## 4. Acceptance gates

- Every point-in-time member event is assigned to a symbol identity and one or more affected weekly cycles, or explicitly marked outside the forecast window.
- Every split, bonus, rights, merger/demerger event affecting a candidate stock-cycle has issuer-supported terms and an independently checked identity transition, or the affected stock-cycle is excluded.
- No double adjustment is applied to Dhan split/bonus-adjusted daily prices.
- Dividend handling preserves price-index semantics and uses no post-cutoff information.
- Exclusions are applied before fitting and reported by symbol-cycle counts; the 47-member / 94% and 98% coverage requirements are re-evaluated after exclusions.
- The unresolved-event ledger, code version, source hashes and all test outcomes are recorded.
- If exclusions breach the minimum coverage rule, the affected cycle is excluded; do not lower the threshold to force a pass.

## 5. Current blockers and next action

The two-event Dhan daily and same-session intraday diagnostics pass for RELIANCE 1:1 bonus and BAJAJFINSV 5:1 split + 1:1 bonus. BAJAJFINSV's trading-ISIN date is adjudicated from 2022-09-13 inclusive; its discrepant TejHQ raw row remains preserved and flagged as stale metadata. These two samples do not certify the wider event catalogue.

NSE terms prohibit systematic automated collection without permission and restrict website-data use for simulation. The four-date archive probe is technical feasibility only; its automated workflow branch is disabled. Next: build the recipient-encrypted queue for 37 complex member-event candidates from the existing personal-use-only TejHQ source, then verify terms using issuer-first-party evidence where permitted. Dhan is the subscribed price-scale source. Events lacking evidence remain unresolved and affected stock-cycles are excluded. C4 confirmatory fitting stays gated until C1 acceptance is explicit.

## 6. Source rights and permitted evidence

- NSE website content will not be bulk-collected automatically without express written permission or an agreement covering this research/backtest use.
- Use Dhan's subscribed Data API for price histories subject to the user's agreement.
- Use issuer-first-party disclosures for event terms where access permits; do not mass-scrape exchange websites.
- The TejHQ source is personal-use-only; the 37-event queue is recipient-encrypted, uploaded as ciphertext for one day, and never published as cleartext.
- Mark unsupported event terms SOURCE_UNRESOLVED and exclude affected stock-cycles rather than infer a factor.

## 7. Safety and research integrity

This protocol does not grant data rights. The TejHQ catalogue remains personal-use-only; exchange terms apply independently. Raw restricted data must remain in the authorised encrypted runtime/cache only. No public repository or artifact may contain reconstructive source rows. Do not claim that a technical API response, adjusted-price ratio or symbol match independently verifies an issuer event.


## 6. 37-candidate complex-event review result — 2026-11-03

- The protected queue [41514027613](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41514027613) yielded 37 unique candidate records and zero ambiguous point-in-time member-key matches.
- Source review classified the queue as 17 equity bonus-share events, 9 splits, 6 rights offers and 3 merger/demerger schemes. Two bonus-labelled candidates were reclassified by issuer evidence as non-equity debenture distributions.
- The reviewed candidate terms and record dates have issuer-first-party evidence for 35 entries and official exchange-primary evidence for 2 entries where an issuer notice was not located in this bounded search. The event-level ledger remains outside GitHub; only aggregate counts are published in [C1_ISSUER_EVENT_REVIEW_AGGREGATE.md](C1_ISSUER_EVENT_REVIEW_AGGREGATE.md).
- This does **not** close historical ISIN/predecessor-successor identity or full price-series continuity. Rights TERPs, scheme-specific predecessor/successor adjustments and affected-weekly-cycle exclusions have not been computed/applied. The 2-event Dhan scale test is not universal evidence.
- Remaining catalogue: 625 dividends, 20 buybacks, 29 AGM/other. C1 remains PARTIAL / NOT PASSED.


## 7. Remaining 49 buyback and AGM/other candidates

- The 20 buyback and 29 AGM/other candidates are reviewed separately from the completed 37 complex event queue.
- Buybacks have no universal mechanical price factor. Review announcement date, board approval, tender/open-market route, price, ratio/size, record date, closure/extinguishment, and whether each item was public by the 10:00 forecast cutoff. Only use these as point-in-time known-event features; do not backdate knowledge from record/ex-date notices.
- AGM/other is a discovery-feed umbrella, not a corporate-action class. Classify each item as board/AGM notice, dividend, buyback, split/bonus, rights, merger/demerger, delisting, name/ISIN change, or non-price-affecting governance announcement. Use the relevant specific rule, or SOURCE_UNRESOLVED and exclude affected cycle if event type/identity cannot be established.
- The 625 ordinary dividend candidates remain separate. Do not mechanically reinvest dividends into the NIFTY price-index target. Retain only point-in-time features disclosed by the forecast cutoff; review price-bar effects only where the frozen label/feature methodology requires it.
