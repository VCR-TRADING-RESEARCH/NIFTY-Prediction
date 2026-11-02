# C1 Corporate-Action Handling Method

**Status:** Method registered for implementation; event-level factors are NOT validated or applied.
**Coverage window:** 2018-04-01 to 2026-10-30.
**Scope:** Point-in-time NIFTY 50 constituent daily features and weekly-expiry return labels.

## 1. Governing distinction

The NSE page titled [Adjustments in case of Corporate Actions](https://www.nseindia.com/static/products-services/equity-derivatives-corporate-actions-adjustments) specifies adjustments to equity-derivative contract terms to preserve position value across cum/ex dates. It is authoritative for those exchange contract adjustments, but it is not automatically a complete total-return adjustment specification for historical cash-equity bars. The research must not transplant a derivative strike/lot adjustment factor into a stock-price series without deriving the corresponding equity-price and share-quantity transformation.

NSE says derivative adjustments occur after close on the last cum-traded day. It lists bonus, rights, merger/demerger, amalgamation, splits, consolidations, hive-offs and cash dividends. Its derivative rules specify bonus factor (A+B)/B for ratio A:B, split/consolidation factor A/B, and a rights factor based on cum-date close P, issue price S, entitlement A and existing shares B: E=((P-S)*A)/(A+B), factor=(P-E)/P. For dividends, the NSE F&O rules distinguish ordinary dividends below 2% of the relevant market value from extraordinary dividends at or above 2%, with the comparison price tied to the board announcement timing; special exceptions apply where the issuer seeks exemption from the SEBI LODR timeline. These are derivative-contract rules, not direct cash-equity adjustment instructions.

## 2. Event-specific handling

| Event family | Evidence required | Research treatment |
|---|---|---|
| Cash dividend | Official ex-date, amount per share, currency, announcement time, previous close, issuer/exchange filing | Preserve raw close. If constructing a total-return series, calculate a separately named cash-reinvested return using the verified dividend and an explicit reinvestment convention. Do not silently replace raw OHLC. Apply NSE extraordinary-dividend logic only to derivative-contract backtests where relevant. |
| Bonus | Official ratio and its convention (new shares : existing shares), record/ex-date, face value, issuer notice | Verify ratio semantics. For an equity-share continuity transformation, share count changes inversely to per-share price; record the exact factor and transformed series separately. Do not infer ratio semantics from free-text labels alone. |
| Split/consolidation | Old/new face values, ratio convention, ex-date, official circular | Reconcile old/new share count and per-share scale. Verify against adjacent raw prices and volume/turnover; preserve original raw series. |
| Rights | Entitlement ratio, subscription price, cum-date close, ex-date, renunciation/part-paid terms and issuer notice | Compute TERP only when all inputs and ratio conventions are verified. Otherwise flag affected return windows as unresolved/excluded. |
| Buyback | Offer type, record date, tender price, size, acceptance terms, exchange/issuer notice | No blanket price factor. Treat as event metadata; consider separately only if a registered feature hypothesis requires it. |
| Merger/demerger/amalgamation | Scheme, effective date, record/ex-date, consideration/exchange ratio, successor ISIN, last cum-date, listing/trading commencement | Never stitch securities with a generic scalar. Exclude or split affected security cycles until scheme terms and successor identity are reconciled. |
| Other/unclassified | Full issuer filing and official exchange record | Keep unresolved; no adjustment until classified and independently checked. |

## 3. Required event ledger schema

The private working ledger must contain: canonical member key; actual traded symbol on event date; ISIN/security identity; event family; announcement timestamp; ex-date; record date; source URL and retrieval timestamp; source document hash; issuer filing reference; all raw formula inputs; ratio convention; calculation version; factor (if applicable); validation status; reviewer/status reason; affected feature dates and weekly expiry cycles; inclusion/exclusion decision.

Public reports may expose aggregate counts, dates and source links only where permitted. Do not publish restricted raw rows, private dataset fields, security identifiers or credentials.

## 4. Mathematical controls

- Every ratio must declare numerator and denominator meaning in words before calculation.
- For split/bonus transformations, assert value continuity: pre-event shares × pre-event price must approximately equal post-event shares × post-event price, allowing only documented market movement and rounding.
- For dividends, distinguish raw-price return from total-return return. A simple ex-date cash adjustment candidate is not enough without a reinvestment convention and verified cash entitlement.
- For rights, independently recompute TERP and verify the value identity from cum-date value plus rights subscription cash.
- No event factor may be applied twice. Event keys must be unique on security identity + event type + ex-date + official notice reference.
- Compare raw and transformed series on both sides of each event. Flag discontinuities; do not force continuity by fitting a factor to observed prices.
- A weekly label whose anchor-to-expiry window crosses an unresolved material event is excluded for that security; the index target remains the observed NIFTY index label.
- Keep raw OHLCV, split/bonus-adjusted series and total-return series distinct, with feature availability timestamps and provenance.

## 5. Acceptance gate

The corporate-action gate passes only after every matched point-in-time constituent event is either (a) independently verified and correctly classified with event-specific treatment, or (b) explicitly excluded from affected feature/label windows with documented rationale. Ambiguous ISIN/symbol identity, missing event terms, incomplete rights inputs, unresolved mergers/demergers or unexplained price/volume discontinuities keep C1 open. Catalogue completion is not gate completion.

## 6. Official source references

- NSE, [Adjustments in case of Corporate Actions](https://www.nseindia.com/static/products-services/equity-derivatives-corporate-actions-adjustments), updated 2023-03-14. Relevant points: cum-date adjustment timing; stock-benefit/cash-benefit classes; bonus, split/consolidation, dividend, rights and merger treatment.
- NSE, [Corporate Actions](https://www.nseindia.com/companies-listing/corporate-filings-actions), live corporate-action search with symbol, purpose, ex-date, record date and series.
- NSE, [Corporate Actions investor-relations archive](https://www.nseindia.com/static/investor-relations/corporate-actions), archived circular/attachment examples.
- NSE Clearing, [Data and Reports Download](https://www.nseindia.com/static/products-services/equity-market-data-reports-download), describes securities master and corporate-action report fields including symbol, series, record/book-closure dates and ex-date.

**Important:** source catalogue uses a pinned third-party personal-use dataset as a discovery source. Official exchange/issuer verification remains mandatory and no redistribution rights are inferred.
