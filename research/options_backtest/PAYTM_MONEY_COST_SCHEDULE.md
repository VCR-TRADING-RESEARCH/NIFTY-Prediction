# Paytm Money / NSE Options Cost Schedule — Evidence Register

**Checked:** 2026-10-31  
**Status:** PARTIALLY VERIFIED; use as an initial dated schedule, not a substitute for contract-note reconciliation.  
**Scope:** NIFTY index options traded on NSE through Paytm Money.

## Broker brokerage

- Paytm Money's F&O FAQ states ₹10 brokerage per unique order that gets executed.
- For a two-leg spread opened and closed, expected four executed leg-orders => ₹40 brokerage if each leg is a separate executed order. Partial fills/replacements and multiple child orders can change the actual count; count executions as Paytm Money bills them, not the strategy's logical entry/exit count.
- Source: https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web (checked 2026-10-31).

## Exchange / statutory schedule

| Component | Up to 2026-02-28 | From 2026-03-01 / 2026-04-01 | Basis |
|---|---:|---:|---|
| NSE equity options transaction charge | 0.03503% from 2024-10-01 to 2026-02-28 | 0.03553% from 2026-03-01 | Option premium turnover, buy and sell sides |
| STT on option sale | 0.10% through 2026-03-31 | 0.15% from 2026-04-01 | Premium value, seller |
| STT on option exercised | 0.125% through 2026-03-31 | 0.15% from 2026-04-01 | Intrinsic value, purchaser |
| Stamp duty on option purchase | 0.003% | 0.003% | Buyer, premium value |
| SEBI turnover fee | 0.0001% (₹10/crore) | 0.0001% (₹10/crore) | Turnover, both sides |
| GST | 18% | 18% | Applicable taxable service charges; calculate only on components prescribed as GST base |

NSE circular NSE/FA/64232 dated September 27, 2024 specifies equity-options transaction charges of ₹35.03 per lakh (0.03503%) effective October 1, 2024. NSE circular NSE/FA/73061 dated February 27, 2026 specifies ₹3,552 per crore plus ₹0.01 per crore NSE IPFT contribution (total ₹3,553 per crore) effective March 1, 2026, i.e. 0.03553% total. Both are on option premium, not notional strike value.

Sources:
- Paytm Money F&O FAQ (₹10 per unique executed order): https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web
- NSE transaction charge circular NSE/FA/64232, 2024-09-27, effective 2024-10-01 (₹35.03/lakh): https://nsearchives.nseindia.com/content/circulars/FA64232.pdf
- NSE transaction charge circular NSE/FA/73061, 2026-02-27, effective 2026-03-01 (₹35.53/lakh): https://nsearchives.nseindia.com/content/circulars/FA73061.pdf
- NSE STT table, effective 2026-04-01: https://www.nseindia.com/static/products-services/equity-derivatives-securities-transaction-tax
- NSE stamp duty and SEBI fee table: https://www.nseindia.com/static/invest/first-time-investor-sebi-turnover-fees-stt-other-levies

## Implementation cautions

1. Use trade-date effective rates, not today's rates retroactively.
2. Apply STT to each sell-side premium fill. If an option is exercised ITM, calculate exercise STT on intrinsic value; the strategy specification exits before final expiry day to avoid accidental exercise, but test and log any expiry exposure.
3. Stamp duty applies to buy-side option premium. Brokerage is per executed order; transaction fees and SEBI fees are turnover-based.
4. GST must be applied to the statutory taxable service-fee base, not blindly to STT or stamp duty.
5. Round charges using the exchange/broker's actual rounding rules at order/contract-note level; verify the final calculator against anonymized contract notes if available.
6. Paytm Money tariff pages can change. The public pricing page does not expose every F&O charge component in one static table; this file records sources and must be reconciled to the brokerage calculator / actual contract note before calling net P&L broker-exact.
7. The strategy text supplied in chat used Zerodha as a reference broker for a cost example. That is not the broker used in this backtest. Use Paytm Money ₹10/order and its actual fee/tax treatment.

## Cost-model acceptance gate

Backtest outputs must show separate brokerage, exchange transaction charge, STT, GST, stamp duty, SEBI fee and slippage by leg and by trade. If any component cannot be verified for a historical date, show a conservative range and mark broker-specific net P&L provisional.
