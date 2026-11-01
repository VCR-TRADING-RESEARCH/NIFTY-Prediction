# C2 feature and label dictionary

All fields below are constructed from point-in-time NIFTY 50 constituents and the frozen weekly expiry-cycle calendar. Full row-level values, targets and feature matrices remain in the AES-GCM encrypted panel cache; the public report contains field names, hashes, counts and QA only.

| Field | Definition | Availability / notes |
|---|---|---|
| `cycle_idx` | Stable ordinal for the verified expiry cycle in chronological order | Calendar key; not a feature |
| `previous_expiry` | Prior verified weekly expiry | Exchange-calendar-derived |
| `anchor_date` | First regular session after preceding expiry | Point-in-time session calendar |
| `expiry_date` | Actual verified weekly expiry date | Holiday shifts and weekday transition retained |
| `symbol` | Canonical member key in the membership ledger | Stable panel key |
| `point_in_time_symbol` | Exchange ticker resolved for the anchor date | Alias history; unresolved cases must be flagged |
| `anchor_open` | First valid 1-minute bar open timestamped 10:00–10:03 IST | Actual timestamp retained; forecast cutoff convention is 10:00 |
| `expiry_close` | Close of latest valid 1-minute bar timestamped 15:00–15:14 IST on expiry | 15:15 proxy, not 15:30 close |
| `stock_return` | `expiry_close / anchor_open - 1` | Target only; never a feature |
| `stock_label` | UP for positive return, DOWN for negative, FLAT for exact zero | FLAT retained in panel and omitted from binary fitting |
| `ret_1d`, `ret_5d`, `ret_10d`, `ret_20d`, `ret_60d` | Prior close divided by close 1/5/10/20/60 sessions earlier, minus one | Only daily sessions strictly before anchor date |
| `vol_5d`, `vol_20d`, `vol_60d` | Sample standard deviation (ddof=1) of prior daily close-to-close returns over 5/20/60 observations | Only sessions strictly before anchor |
| `range_10d`, `range_20d` | Mean of `(high-low)/close` over prior 10/20 sessions | Only sessions strictly before anchor |
| `gap_1d` | Most recent prior session open divided by the preceding session close, minus one | Historical overnight gap; not the current session's 10:00 gap |
| `volume_z20` | Z-score of latest prior-session log(1+volume) against the preceding 20 sessions | Zero denominator guarded by a small numerical epsilon |
| `cs_rank_ret5`, `cs_rank_ret20` | Percentile rank of 5/20-session prior return within that cycle's active point-in-time constituents | Computed after the point-in-time membership panel is built |
| `identity_review_flag` | Indicates a security with unresolved historical identity concerns (HDFC/TATAMOTORS in current C1 handoff) | Limitation flag; flagged rows are excluded from primary sensitivity panel |
| `action_crossing_flag` | Known catalogue event for that symbol with event date in (anchor, expiry] | No adjustment applied; excluded from primary sensitivity panel |
| `index_return`, `index_label` | NIFTY expiry-proxy close divided by 10:00 anchor open minus one; UP/DOWN/FLAT | Actual observed index target; not an equal-weight basket |
| `idx_ret_*`, `idx_vol_*`, `idx_range_*` | Same prior-only daily formulas applied to NIFTY official daily OHLC | Index context for descriptive or hybrid analyses; excluded from the primary pure-bottom-up C4 meta-model |

## Nulls and exclusions

- Invalid target OHLC, missing required stock volume, duplicate target timestamps, missing 62-session history or unavailable security identity do not create synthetic values.
- Exact zero target returns remain FLAT. They count as observed target coverage, but they are excluded from binary classifier fits.
- The primary sensitivity panel excludes rows with identity-review or known action-crossing flags. The full exploratory panel retains them with flags.
- Unverified corporate-action events remain unverified. No generic split/bonus/rights/merger adjustment is applied.
- Cross-sectional ranks use only members active for the specific cycle; no current-universe ranking is backfilled into historical dates.
- Any model feature transformation, scaling, imputation, feature selection or calibration added in C3/C4 must be fitted on each training window only.

## Forecast-time caveat

The daily features above are deliberately lagged through the prior completed session. The C2 panel records the current 10:00 anchor open for target construction. A current-session open-gap feature may be proposed in a later plan-controlled feature revision, but must not be silently added after the final holdout boundary has been frozen.
