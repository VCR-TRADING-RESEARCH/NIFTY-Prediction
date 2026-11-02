# C2 Point-in-Time Constituent Panel Build

**Status:** FAILED

- Error category: RuntimeError
- Error message: NIFTY target coverage is 79.2308%; minimum is 98%.
- Source location: {'file': 'run_c2_panel_and_models.py', 'line': 798, 'function': 'main'}
- Authentication method: totp_refresh
- Token refresh status: SUCCESS
- Profile HTTP status: 200
- Provided-token fallback: NOT_NEEDED
- Scheduled cycles: 260
- Valid NIFTY target cycles: 206
- Constituent target rows: 10194
- Cycles meeting 47/94%: 206
- Eligible constituent-count distribution: {'47': 14, '48': 166, '49': 26}
- Build failure counts: {'stock_daily_features_missing': 79, 'stock_target_missing': 26, 'index_target_missing': 54}
- Detailed value-free diagnostics are in C2_PANEL_BUILD.json.
