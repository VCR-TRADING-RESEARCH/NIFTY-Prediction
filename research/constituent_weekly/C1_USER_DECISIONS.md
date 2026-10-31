# C1 user-approved data-definition decisions

## 2026-11-01

1. **Expiry proxy:** Do not require 15:25–15:29 bars. Use the close of the most recent available one-minute candle timestamped 15:00–15:14 IST as the proxy at the 15:15 cutoff. Ignore all candles timestamped after 15:14. Persist the actual proxy timestamp and label it as a proxy, not the official 15:30 exchange close.
2. **Historical symbols:** Retain the 79 symbols currently found in Dhan's master as candidate instruments. Resolve dated aliases and probe legacy identities; never infer complete historical coverage from a current-master match. JPASSOCIAT, RANBAXY and MCDOWELL-N only appear in the current membership ledger in 2014 and are outside the 2018-04 confirmatory window.
3. **Weights:** Use free web research to discover public sources. A CC BY-NC-SA historical weight dataset is permitted only as a provisional non-commercial research candidate; it is not automatically accepted as official weights or commercially cleared. Reconcile against official monthly reports and fill the 2025-09 onward gap before C1 acceptance.

C2/model work remains gated until C1 acceptance conditions are met.
