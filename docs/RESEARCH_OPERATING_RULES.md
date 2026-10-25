# Research Operating Rules

Version: 1.0
Created: 2026-10-25
Scope: NIFTY weekly expiry direction label defined in the repository README.

## Mandatory rules
1. Read this file, the fixed research plan, current research log, error log, data-source register and latest results before each new phase.
2. The research question is strictly whether NIFTY 50 spot at weekly-expiry close is above or below its value at 10:00 IST on the first trading day after the preceding weekly expiry. Do not drift into a different target without versioning the plan.
3. Use the actual historical expiry contract/calendar; current expiry day is Tuesday and the schedule changed from Thursday in September 2025. Holidays and special sessions must be handled explicitly.
4. No look-ahead leakage: every predictive feature must be observable by the forecast cutoff. Learn transformations and model parameters only from each training fold.
5. Begin with free official/public sources before considering paid sources. Record provenance, licence, access date, coverage, gaps, schema. Composite datasets are permitted only after timestamps and conflicting values are reconciled.
6. Retain source snapshot hashes, validated target/feature rows, result tables, model/configuration version and log entries. Cache large immutable raw data; do not commit large raw market data unless licensing/size/retention are verified.
7. Every strategy family and parameter search must have a pre-defined budget and be reported, including failures. Do not select or describe a winner based on training accuracy.
8. Use expanding walk-forward validation and a final untouched time holdout. Use a baseline, balanced accuracy, proper probability scores and uncertainty estimates. Correct for multiple strategy comparisons where appropriate.
9. Distinguish prediction accuracy from tradability. For any trade simulation include Paytm Money brokerage (current public FAQ states ₹10 per unique executed order), date-effective statutory/exchange charges, GST, stamp duty, STT, lot sizing, bid/ask spread, slippage and realistic fills. Verify historical rate schedules instead of applying present rates to old periods.
10. If options/futures prices, fees or a complete expiry calendar are missing, explicitly mark that test as blocked or approximate. Never report unavailable results as zero cost or verified performance.
11. Keep secret values in GitHub Actions secrets; never print tokens/PIN/TOTP/API responses containing credentials. Dhan access tokens have 24-hour validity; refresh by the documented secure flow before data API calls, and fail closed when refresh fails.
12. Each phase gets a separate branch; merge phase results to the default branch only with a record of acceptance-gate outcomes. Every workflow supports manual dispatch as well as automation.
13. Update the phase status after every major step. Log exceptions, failed attempts, corrections, omissions and data warnings in logs/ERROR_LOG.md and logs/RESEARCH_LOG.md.
14. Stop at the pre-registered gates. If no robust edge is found, the conclusion is “no usable strategy validated in this run”, not “keep searching forever”.
15. Keep a complete log of visible project conversations that are available to this agent and preserve user-visible decisions. Hidden private chain-of-thought is not copied; replace it with an auditable decision rationale, methods and results.
16. Produce the structured manuscript, tables, plots, appendices, supplements and reproducibility notes after evidence is available. Do not create fabricated results, charts or p-values.

## Required review before each phase
- Read README.md, docs/RESEARCH_PLAN.md, docs/LITERATURE_REVIEW.md, docs/DATA_SOURCES.md, logs/RESEARCH_LOG.md, logs/ERROR_LOG.md and current output artifacts.
- Check for known prior errors before new code or model changes.
- Review math/sign conventions, date alignment, duplicate rows, timezone handling, missing values, train/test chronology and cost formulas.
- Record a phase gate: PASS / FAIL / BLOCKED / INCONCLUSIVE, with evidence and next action.

## Plan-change control
RESEARCH_PLAN.md is pre-registered and must not be silently edited when results look poor. Any substantive change requires a new version, a dated rationale in RESEARCH_LOG.md, a summary of impact on comparability, and explicit separation of pre- and post-change experiments. Routine completion/status updates belong in the logs rather than rewriting the plan.
