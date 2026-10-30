# NIFTY Options Dual-Sleeve Backtest — Phase Plan

**Branch:** research/nifty-options-dual-sleeve-backtest  
**Plan version:** 1.3  
**Status at 2026-10-31:** PUBLIC DATA AUDIT PASSED BASIC INTEGRITY; FULL-PERIOD / EXECUTION-FIDELITY GATES BLOCKED; NO STRATEGY P&L RUN  
**Capital assumption:** INR 200,000  
**Research period:** intraday options source currently identified from October 2024 onward; do not imply 2021–2023 minute-option coverage from this source.

## Purpose and hypotheses

Test the proposed two-sleeve NIFTY options system without conflating directional spot prediction with executable option P&L. Four experiments are independent:
- A: intraday bull-call / bear-put debit spreads.
- B: positional bull-put / bear-call credit spreads.
- C: range-regime iron condors.
- D: portfolio combination of sleeves that pass individual gates.

H0: no candidate has positive net expectancy after date-effective costs and conservative execution assumptions. H1: at least one pre-registered candidate has positive out-of-sample net expectancy and acceptable drawdown under base and stress execution assumptions.

## Source investigation completed

1. Repository already contains NIFTY spot minute/daily research data, but not an archived, contract-level option minute series.
2. Hugging Face dataset `rissin/nse-options-intraday` provides audited NIFTY 1-minute option rows from 2024-10-01 to 2026-07-21 (124,458,249 rows). The audited schema includes OI and volume; no null OI or volume rows were found. OHLC/timestamp integrity passed. However, 65,768,348 rows (52.84%) have zero volume and 35 rows have negative volume; only 58,689,866 rows (47.16%) have positive volume and are candidates for executable fills. There is no IV or bid/ask field. Full details and checksums are in [DATA_AUDIT_REPORT.md](DATA_AUDIT_REPORT.md) and [data_audit_summary.json](data_audit_summary.json). The intraday data is sourced from Upstox historical API; licence is listed as "other", so raw data is not committed or redistributed.
3. Zenodo DOI 10.5281/zenodo.10899828 provides NIFTY spot, futures and options one-minute data for 2017–2020. It is useful for an independent historical slice but predates the main current expiry structure and requires schema, contract and timestamp audit.
4. Neither identified free intraday source guarantees bid/ask quotes. OHLC fills are not actual broker fills. Use conservative bar-based execution and sensitivity analysis; clearly separate modeled slippage from observed spread.
5. Dhan credentials must remain in Actions secrets. Do not assume Dhan can retrieve expired options merely because live token refresh works.

## Locked strategy rules to encode

### A — Intraday debit spreads
- Underlying regime/signal: 5-minute execution bars; 15-minute trend confirmation; price vs session VWAP; breakout close; exclude first 15 minutes.
- Bullish: buy CE around 0.50–0.60 delta and sell same-expiry OTM CE around 0.20–0.30 delta.
- Bearish: buy PE around 0.50–0.60 delta and sell same-expiry OTM PE around 0.20–0.30 delta.
- Exit: target +60% of initial debit, stop -40% of initial debit, time exit 15:10 IST; at most one re-entry; no new expiry-day entry.
- Important implementation: delta is not supplied by the identified dataset. Reconstruct IV/delta from synchronized underlying prices and option premiums using documented rates/dividend assumptions; if reliable synchronized spot data or sufficient quotes are unavailable, run a separately labelled strike-distance proxy only as exploratory and do not claim delta-rule replication.

### B — Positional credit spreads
- Enter only when 7–14 calendar DTE; short option target 0.15–0.20 absolute delta; buy protective option 50 index points farther OTM initially.
- Bullish: short PE, long lower-strike PE. Bearish: short CE, long higher-strike CE.
- Exit at 50% of initial credit, stop when spread buyback debit reaches 1.5x initial credit, or exit before final expiry trading day; regime invalidation is separately coded and reported.
- Delta reconstruction and synchronized spot required. Missing/illiquid contracts are no-trade, not zero-price fills.

### C — Iron condor
- Candidate only in a pre-defined range/low-trend regime; same expiry, short wings 15–20 delta, hedges 50 points farther OTM.
- Apply the same credit-spread exit conventions to the whole structure; test as a separate experiment, not retrofitted into B after seeing results.

### D — Combined portfolio
- Initial notional sleeves: ₹80,000 intraday, ₹70,000 positional, ₹50,000 reserve. These are capital envelopes, not assumptions about margin.
- Respect actual lot size and broker margin by trade date; reject trades exceeding available cash or specified risk caps.
- Per-trade planned loss limits: ₹2,000 intraday, ₹3,000 positional; daily stop ₹4,000; weekly stop ₹10,000; monthly drawdown review 6%.
- No martingale, averaging down, naked options or overlapping duplicate exposure. Portfolio chronology and concurrent positions must be simulated.

## Costs and execution

Use Paytm Money's date-effective official schedule, not the unrelated Zerodha fee table in the proposal. At minimum account for per-order brokerage on every executed leg, STT on option sale/expiry as applicable, exchange transaction fees, GST on taxable service charges, stamp duty on buys, SEBI/regulatory charges, statutory rounding, and slippage on each leg. Store rate source, effective dates and formulas. If the date-specific Paytm schedule cannot be verified, publish a range and mark broker-specific net P&L blocked.

No midpoint or close fills by default. Use next executable bar open as a proxy with adverse per-leg slippage scenarios 0.5, 1.0 and 2.0 points; add spread stress because bid/ask is unavailable. Report fill-model limitations. Reject stale, zero-volume, missing, crossed/impossible OHLC, and unsynchronized legs.

## Data and validation gates

1. Download only needed NIFTY partitions to Actions cache; retain manifest, dataset revision, file checksums, row counts and source provenance. Do not commit raw Parquet unless licence explicitly permits it.
2. Audit schema, timestamp timezone, duplicates/conflicts, session boundaries, OHLC invariants, zero-price rows, OI/volume completeness, zero/negative volume, expiry/strike mapping, missing bars and contract survivorship. Only positive-volume bars are eligible for fills.
3. Independently reconcile a sample to NSE/broker sources and spot series. Confirm the source's expiry labels are actual contract expiries and account for historical weekly expiry weekday changes. Apply the expiry-date-based NIFTY lot schedule in [LOT_SIZE_SCHEDULE.md](LOT_SIZE_SCHEDULE.md): 25 for 2024-10-01 through 2024-12-19 expiries, 75 for 2025-01-02 through 2025-12-23, and 65 from 2026-01-06; resolve holiday shifts before sizing.
4. Verify point-in-time strike selection: only data available at signal time; no selecting contracts based on future liquidity or end-of-day volume.
5. Build contract chain panel; compute IV/Greeks only with a documented solver, rates, dividends and bounds. Validate reconstructed prices/deltas against independent observations where available.
6. Keep development, validation and final untouched chronological holdout. Use walk-forward selection; no random shuffling or holdout tuning.
7. Test each experiment A, B, C independently before D.

## Statistical reporting

Per experiment and cost scenario: number of trades/no-trades, win rate with Wilson 95% CI, average/median win and loss, net expectancy in INR and per risk unit, profit factor, max drawdown, CAGR only if capital timeline is valid, Sharpe/Sortino with stated frequency, turnover, costs, slippage sensitivity, tail loss, consecutive losses, exposure and margin utilization. Use block bootstrap over trading weeks/months for expectancy and drawdown uncertainty; report sample size and multiple-testing adjustment. Include year, volatility regime, expiry weekday era and directional regime breakdowns.

## Acceptance gates and stop rules

- Gate 0: source files and legal-use policy inspected; reproducible cache and code tests.
- Gate 1: basic schema/OHLC/timestamp and OI/volume completeness passed on the 2024-10 to 2026-07 public archive; full 2021–2026 coverage, bid/ask execution, IV/Greeks validation, futures VWAP and Dhan source remain blocked. Positive-volume filtering is mandatory.
- Gate 2: all four strategies are coded against locked rules and unit-tested with synthetic payoff cases.
- Gate 3: walk-forward results produced for A/B/C separately, including all failures and exclusions.
- Gate 4: combined portfolio D tested only after individual results; costs and slippage stress pass.
- Gate 5: independent audit of signs, payoff, quantity, lot-size changes, order counts, fee formulas, timestamps, leakage and accounting; manuscript and README status updated.

Stop after Gate 5. If source licence, required option history, synchronization, historical lot sizes, or Paytm Money fee schedule cannot be verified, mark the affected result BLOCKED/EXPLORATORY. Never manufacture missing prices, zero missing costs, or claim live readiness. Do not purchase a paid dataset without explicit user authorization.

## Deliverables

- data manifest and [data quality report](DATA_AUDIT_REPORT.md) (no restricted raw data committed)
- contract-level trade ledger CSV and per-leg cashflow ledger
- metrics by experiment and cost/slippage scenario
- equity curve, drawdown, monthly/yearly and regime charts
- tests for payoff, signs, order counts, lot size, fees and timestamp leakage
- reproducible command/workflow and run log
- complete manuscript with limitations, inferences and future research
