# C5 — Economic and execution gate

**Decision (2026-11-02): BLOCKED — no eligible trading signal or instrument specification.**

## Why the gate is not run

The stock-level holdout test found no reliable predictive advantage: momentum achieved 50.52% accuracy, while logistic regression, ExtraTrees and HistGradientBoosting achieved 48.12%, 48.51% and 46.69%. Logistic's paired cycle-level accuracy difference to momentum was −2.37 percentage points, with a four-cycle moving-block bootstrap 95% interval of −10.04 to +4.29 percentage points.

The separate plan-v1.4 C3-X NIFTY meta-model had 50.98% accuracy, 53.45% balanced accuracy and 48.68% ROC-AUC on 51 cycles; its paired accuracy-difference interval was −25.49 to +25.49 percentage points. This is exploratory, statistically inconclusive and below the bar for a strategy signal. C1 remains PARTIAL and C4 confirmatory is gated.

There is consequently no validated signal to translate into entry/exit rules. No futures or options contract, strike/expiry selection, spread structure, position sizing, risk limit, order type, or fill model has been selected. Running a costed backtest now would create a false impression of precision.

## Required net-P&L identity

For each executed trade (j):

[
operatorname{NetPnL}_j=operatorname{GrossPnL}_j
-operatorname{Brokerage}_j
-operatorname{STT/CTT}_j
-operatorname{ExchangeCharges}_j
-operatorname{SEBICharges}_j
-operatorname{GST}_j
-operatorname{StampDuty}_j
-operatorname{SpreadCost}_j
-operatorname{Slippage}_j
-operatorname{MarketImpact}_j.
]

Gross P&L must be calculated from actual contract quantity, lot size, entry/exit fills, multiplier, expiry settlement and contract-specific payoff. Option premium cash flows, exercised/expired positions, assignment/settlement, partial fills and multi-leg sequencing must be handled explicitly. Costs are not interchangeable between cash, futures and options.

**No fee rates are inserted here.** The applicable Paytm Money brokerage and statutory/exchange schedule must be verified for the actual product, exchange, order date and buy/sell side before modelling. A current fee page cannot be assumed to describe earlier years. GST bases and statutory levies must use the correct date-effective rules.

## Minimum evidence to reopen C5

1. A C4 directional model passing its locked chronological holdout and robustness criteria, with calibrated probabilities and a defined abstention rule.
2. A fixed instrument: NIFTY futures or a fully specified options strategy (expiry, strikes, legs, entry timestamp, exit rule, lot sizing, capital and margin).
3. Dated exchange contract specifications, lot-size history, expiry/settlement rules and historical bid/ask or a conservative executable proxy.
4. Paytm Money date-effective brokerage and levies, including brokerage caps/minimums, exchange transaction charges, SEBI fees, GST, STT/CTT and stamp duty.
5. Fill simulation with bid/ask spread, queue/market impact and adverse slippage; partial/no-fill and gap stress.
6. Leakage-safe walk-forward out-of-sample P&L and risk report: net expectancy, drawdown, turnover, win/loss distribution, tail loss, capital/margin use, Sharpe/Sortino and regime stability.
7. Independent re-performance of all fee calculations and trade cash flows.

## Decision

C5 is **BLOCKED / NOT RUN**. No trading strategy, paper-trading instruction, live signal or profitability claim is issued. This is a valid stop outcome under the registered plan. Do not try random option structures to rescue a weak prediction model.

See the parent [C3 stock results](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c3-models/research/constituent_weekly/C3_RESULTS.md) and [C3-X exploratory NIFTY report](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/blob/phase/constituent-weekly-outcomes-c3-exploratory/research/constituent_weekly/EXPLORATORY_REPORT.md).


## Automated gate validation

The fail-closed C5 workflow [41410573458](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41410573458) passed. It verified that no instrument, date-effective fee schedule, execution model or net-P&L test is being falsely marked complete. This validates the blocked status, not trading economics.
