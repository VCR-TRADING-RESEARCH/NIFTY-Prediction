# C1 user-approved data-definition decisions

## 2026-11-01

1. **Expiry proxy:** Do not require 15:25–15:29 bars. Use the close of the most recent available one-minute candle timestamped 15:00–15:14 IST as the proxy at the 15:15 cutoff. Ignore all candles timestamped after 15:14. Persist the actual proxy timestamp and label it as a proxy, not the official 15:30 exchange close.
2. **Historical symbols:** Retain the 79 symbols currently found in Dhan's master as candidate instruments. Resolve dated aliases and probe legacy identities; never infer complete historical coverage from a current-master match. JPASSOCIAT, RANBAXY and MCDOWELL-N only appear in the current membership ledger in 2014 and are outside the 2018-04 confirmatory window.
3. **Weights:** Use free web research to discover public sources. A CC BY-NC-SA historical weight dataset is permitted only as a provisional non-commercial research candidate; it is not automatically accepted as official weights or commercially cleared. Reconcile against official monthly reports and fill the 2025-09 onward gap before C1 acceptance.

C2/model work remains gated until C1 acceptance conditions are met.


## 2026-11-01 — Expiry target convention amendment

- User directed that 15:25–15:29 minute data is not required and that the latest available time should be treated as expiry, using a 15:15 proxy.
- Plan v1.1 defines both constituent and NIFTY index outcomes using the close of the latest valid 1-minute bar timestamped 15:00–15:14 IST on the expiry session. Store the actual timestamp; do not call it the 15:30 official close. If the index series lacks the same proxy, do not mix it with constituent targets.


## 2026-11-01 — Public-source proxy path approved

- User directed: "Just use the available web sources", then approved continuation.
- Decision: do not make an NSE data-rights request a prerequisite for an exploratory public-source proxy track.
- Use published Nippon India ETF Nifty 50 BeES portfolio holdings as an explicitly labelled ETF-replica proxy. Do not call these official NIFTY 50 weights/IWF.
- Keep official white-paper/official weights, ETF holdings, and reconstructed/drifted proxy weights in distinct source classes. Preserve actual publication timestamps or explicitly flagged imputed availability; do not introduce future snapshots.
- Single-date 2026-02-27 calibration against the official NSE Indices weight snapshot: 50/50 matched; MAE 0.002214 pp; RMSE 0.003204 pp; max abs difference 0.008967 pp; Pearson r 0.99999895. Historical series and event reconciliation remain to be built.
- Plan amended to v1.2. The official confirmatory gate remains separate; proxy results are exploratory until a point-in-time history and basket-to-index reconciliation pass.
