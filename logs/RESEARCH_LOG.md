# Research Step Log

Every major action, including failure and blockage, is recorded here. Update statuses after each phase step.

## 2026-10-25 — Run R0001 / repository bootstrap
- Status: IN PROGRESS.
- Confirmed VCR-TRADING-RESEARCH/NIFTY-Prediction was an empty public repository; README had no prior research plan/logs/artifacts to read.
- Read the available current project conversation context: a prior project thread requested organization/GitHub setup and described the same NIFTY weekly direction target. A screenshot-based organization-connection troubleshooting discussion is listed in the project summary, but full past messages/images are not accessible as plain text in this run.
- Initialized README and research/phase-0-foundation branch. Defined the target, initial pre-registration, source register, status/error/conversation logs, manuscript and method plan.
- Public source review: NSE currently describes NIFTY weekly expiries on Tuesday with shift to previous trading day for holidays; historical Thursday-to-Tuesday shift must be modelled. Public minute-data repository describes 1-minute NIFTY OHLC from 2017 and documents known quirks. See docs/LITERATURE_REVIEW.md and docs/DATA_SOURCES.md.
- Paytm Money F&O FAQ says ₹10 per unique executed order; cost schedule must be date-aware. NSE current STT page lists rates effective 2026-04-01, so present-day rates cannot be copied into older backtests.
- Dhan authentication documentation says access tokens expire after 24 hours and supports secure API-based token generation when TOTP is configured. Token implementation is deferred until the Actions environment can test it; never emit token fields in logs.
- Code/data validation: automated workflow has not yet executed. No market-data computation or empirical backtest result is claimed. Pending workflow/test run.
- Phase gate: Phase 0 = IN PROGRESS; Phase 1 = NOT STARTED.
- Next step: add data fetch, label/feature/prediction pipeline, unit tests and manual/scheduled GitHub Actions workflow; run and inspect logs.


## Automated run 40167611476 — 2026-10-25T06:05:13.210148+00:00
- Status: pipeline completed; empirical findings remain exploratory until calendar and instrument-cost gates pass.
- Source files read: 19; valid minute bars: 882839.
- Weekly labels: 398; binary rows: 398; feature-complete rows: 398.
- Development rows / held-out rows: 318 / 80.
- Development-selected model: logistic.
- Calendar gate: EXPLORATORY_ONLY — Weekly expiry dates were generated from weekday regimes and inferred from available bars; official historical expiry calendar and holiday shifts are not independently reconciled.
- Usable trading strategy: NOT VALIDATED. No verified historical futures/options fills, contract-specific price series, dated Paytm Money cost schedule and bid-ask/slippage data have been joined. Spot-direction classification is not executable P&L.
- Artifacts: data/processed/weekly_labels_features.csv, research/results/holdout_metrics.csv, research/results/summary.json and the associated plots.
