# BUP-01 C1 — Dhan 1-minute coverage validation report

**Run:** [GitHub Actions 41266897788](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266897788)  
**Machine status:** `PASS_ACTIVE_EQUITIES`  
**Result timestamp:** 2026-11-01 02:52:56–02:56:45 UTC  
**Branch:** `phase/constituent-weekly-outcomes-c1-data`  
**Raw data:** Not committed; only sanitized QA metadata in [C1_DHAN_PREFLIGHT.json](C1_DHAN_PREFLIGHT.json).

## 1. Scope and test design

This report records the bounded Dhan data-availability test used to determine whether constituent prices are feasible for BUP-01. It is a source/coverage QA report, not a return panel, prediction or strategy result.

- Dhan token refreshed on first attempt; profile HTTP 200; Data API plan active.
- Sanitized Dhan HTTP Date minus runner UTC offset: -1 second (the HTTP Date header has one-second granularity).
- Current NIFTY 50 point-in-time membership security master: 50/50 IDs resolved.
- Historical tradable membership aliases in the licensed ledger: 79/84 found in today's master. The five absent historical symbols require dated alias/security-ID review; absence from the current master is not proof of historical unavailability.
- Price probes use one-minute equity bars, strict numeric/OHLCV QA only within the registered target scope 09:15–15:14 IST, first anchor in 10:00–10:03, and latest expiry proxy close in 15:00–15:14. Bars timestamped 15:15 and later are separately counted and cannot alter the target.
- NSE evening-only Muhurat sessions (2021-11-04 and 2022-10-24 where present) are excluded from normal daytime target-session counts.

## 2. Results

| Window | Symbols passing | Regular sessions per symbol | Anchor sessions | 15:00–15:14 proxy sessions | Total bars | Target-scope checks |
|---|---:|---:|---:|---:|---:|---|
| 2026-06-29 to 2026-09-26 | 50/50 | 64/64 | 64/64 | 64/64 | 1,170,700 | 0 missing anchors/proxies, duplicates, invalid numeric rows, OHLC or volume failures |
| 2022-10-03 to 2022-12-30 | 50/50 | 61/61 | 61/61 | 61/61 | 1,146,180 | 0 missing anchors/proxies, duplicates, invalid numeric rows, OHLC or volume failures |
| 2021-11-01 to 2022-01-29 | 50/50 | 61/61 | 61/61 | 61/61 | 1,233,597 | 0 missing anchors/proxies, duplicates, invalid numeric rows, OHLC or volume failures |

Separate one-session full basket probe on 2026-10-29 passed **50/50**. Each stock had four anchor-window bars (10:00–10:03) and a latest expiry-proxy bar timestamped 15:14 IST.

### The 2021 SHREECEM post-cutoff observation

A single finite negative-volume observation for SHREECEM was timestamped **2021-12-30 15:29 IST**. This observation is outside the pre-registered 15:15 cutoff and therefore outside the primary target scope. The diagnostic records only the timestamp and count, never the volume or price.

The target checker now:
- enforces non-negative volume and OHLC invariants strictly through 15:14;
- separately counts 15:15–15:30 bars and any negative-volume rows they contain;
- fails if the same negative-volume anomaly appears inside the target scope.

The corrected 2021 edge window passed 50/50. Offline regression run [41266922851](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41266922851) passed 43 tests, including in-scope and out-of-scope negative-volume cases.

## 3. What this demonstrates — and what it does not

**Demonstrated:** The configured Dhan subscription can return full 50-stock minute-bar coverage for the current one-session probe and three separate 90-day historical samples. The latest TOTP-based authentication path works on the protected Actions runner. The final workflow status gate ran after report commit and passed on run 41266897788.

**Not demonstrated:**
- continuous five-year minute-bar coverage; the three 90-day windows are disjoint;
- reliable history for every inactive/delisted security alias or every corporate-action successor;
- a full historical daily OHLCV panel for all point-in-time members;
- official point-in-time numerical NIFTY 50 free-float IWF/weights;
- 22-exclusion IWF category completeness or official weighted constituent basket reconstruction.

A Reliance daily-history request returned 22 observations for January 2018; this is a one-symbol historical existence probe only, not a full daily panel.

## 4. Gate result

- **Dhan bounded intraday coverage sub-gate: PASS** for the listed windows.
- **C1 overall: NOT PASSED / RIGHTS-BLOCKED.** The required IWF/weight rights, completeness and basket-reconciliation gates remain unresolved. No stock panel/model/forecast or executable strategy is authorised by this report.
- C2 remains gated under the locked BUP-01 v1.1 plan.

## 5. Reproducibility and security

The machine-readable QA JSON contains sanitized aggregate counts, timestamps, statuses and validation flags only. It contains no raw prices, raw volume values, Dhan security IDs, client IDs, PINs, TOTP seed, OTP or access token. The last-success JSON is kept separately so a later transient failure does not destroy evidence of a passing run.

See [registered plan](RESEARCH_PLAN.md), [phase status](STATUS.md), [IWF/rights audit](C1_OFFICIAL_WEIGHTAGE_ARCHIVE_TERMS_AUDIT.md), [error log](../../logs/ERROR_LOG.md) and [research log](../../logs/RESEARCH_LOG.md).
