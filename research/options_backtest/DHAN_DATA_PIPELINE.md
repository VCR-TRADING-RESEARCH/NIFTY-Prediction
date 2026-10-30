# Dhan expired-options collection

The research branch now uses the subscribed Dhan Data API as the preferred historical options source. The official endpoint is `POST /v2/charts/rollingoption`. Dhan documents up to five years of minute data, 30-day maximum request windows, and ATM-relative strikes through ATM ±10 for near-expiry index options. Returned fields can include OHLC, IV, volume, OI and spot.

The collector refreshes a short-lived token from the existing GitHub organization secrets, requests NIFTY weekly expiry codes 0 (near/current) and 1 (next), both CALL and PUT, and ATM ±10. It writes compressed Parquet files only to the Actions cache and emits a provenance/checksum manifest. Credentials and raw market data are not committed to Git.

**Important modelling caveats**
- `expiry_code` is a rolling code, not a contract expiry date. Map it point-in-time to actual NSE expiry dates and holiday shifts before any trade simulation.
- ATM-relative strikes change as spot moves. Keep both `relative_strike` and returned absolute `strike`; never treat relative strike as a fixed contract.
- Dhan's endpoint returns bar OHLC, not bid/ask/order-book fills. The simulator must use adverse fill assumptions and slippage scenarios.
- The API does not return futures VWAP. NIFTY spot is an index and has no traded volume; the requested VWAP filter must be sourced from a verified NIFTY futures series or explicitly excluded in a separate ablation. Do not fabricate spot VWAP.
- The data is rolling and near-ATM-limited. The positional 50-point hedge must be verified to fall within available strike coverage at each entry; otherwise mark no-trade.

Sources:
- Dhan expired options API: https://dhanhq.co/docs/v2/expired-options-data/
- Dhan expiry-code definitions: https://dhanhq.co/docs/v2/annexure/
- Dhan historical data API: https://dhanhq.co/docs/v2/historical-data/
\n\n## Current validation status (2026-10-31)\n- Dhan authentication and rolling-options request did not pass the automated smoke test. The existing token could not be renewed; TOTP generation was inconsistent; one request returned DH-905 (input exception) on the tested requiredData fields. No Dhan raw data was downloaded.\n- Workflow triggers are manual dispatch and monthly schedule only, to avoid repeated failing PR retries.\n- User intervention needed before a full five-year Dhan pull: verify/refresh the organization secrets DHAN_ACCESS_TOKEN, DHAN_PIN and DHAN_TOTP_SECRET, and confirm the Dhan TOTP setup. Never paste these values into chat or repository logs.\n- Public fallback audit is documented in DATA_AUDIT_REPORT.md.\n