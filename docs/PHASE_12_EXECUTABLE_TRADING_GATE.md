# Phase 12 — Executable Trading and Cost Gate

**Branch:** `research/phase-12-executable-trading-gate`  
**Status:** BLOCKED_PENDING_CONTRACT_LEVEL_DATA  
**Bound:** One source-availability audit, one cost-engine validation, one reproducible run. No parameter search and no repeated strategy tuning.

## Research question
Does any Phase 11 directional forecast translate into positive, robust NIFTY futures/options P&L after realistic execution, date-effective Paytm Money charges, spread, slippage, and settlement handling?

## Aim and objectives
1. Verify whether source-registered historical contract-level prices and expiry/settlement data are available in the repository.
2. Define a fail-closed schema for option/futures trade reconstruction and dated transaction costs.
3. Test execution-cost arithmetic, sign conventions, date validation, provenance requirements, and missing-data behavior.
4. Produce a machine-readable gate report. If inputs are missing, report BLOCKED and do not invent fills or costs.
5. Update manuscript, logs and repository status, and stop at this bounded gate.

## Method
- Spot-direction scores from Phase 11 are not themselves trading returns.
- Required input: `research/data/phase12_contract_fills.csv`, with columns listed in `scripts/phase12_cost_gate.py` and per-row provenance for prices, fill method and date-effective cost schedule.
- Long positions buy at midpoint + half spread + adverse slippage and sell at midpoint − half spread − adverse slippage. Short positions reverse the direction. Multiply price changes by quantity and lot size, then subtract explicit brokerage, exchange transaction charges, STT, GST, stamp duty, SEBI charges and other documented charges.
- Do not assume today's fee schedule applies historically. Fee values must be sourced for the trade date and instrument. If the historical fee schedule is unavailable, the gate remains blocked.
- All cost fields must use consistent units; input documentation must identify whether spread/slippage are index points or option premium points.
- The cost engine is a validation utility, not a substitute for official contract history, expiry-specific option mapping, exercise/settlement cashflows or conservative fills.
- If contract data is eventually supplied, the resulting backtest remains exploratory because the model-development sample has already been inspected. A new prospective window is needed for confirmatory claims.

## Acceptance criteria
- [x] Fixed cost arithmetic implemented with unit tests.
- [x] Missing file or missing schema returns a BLOCKED report without P&L.
- [x] No fabricated trades, fee values, or profitability claims.
- [ ] Source-registered historical contract-level futures/options data available.
- [ ] Date-effective Paytm Money costs verified against official archived schedules.
- [ ] Option contract mapping, expiry settlement, lot sizes and corporate-action/contract-spec changes validated.
- [ ] Out-of-sample strategy evaluated with conservative fills, drawdown, turnover, uncertainty and cost stress.
- [ ] Independent audit passes.

## Phase status and stop rule
The code/logic gate may pass while the trading-evidence gate remains blocked. If required historical fills and dated cost schedules are not present, stop this phase with **NO USABLE TRADING STRATEGY VALIDATED**. Do not replace missing data with spot proxies or arbitrary fee assumptions.
