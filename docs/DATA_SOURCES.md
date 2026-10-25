# Data Sources, Provenance and Data Dictionary

Updated: 2026-10-25.

## Primary source register
| Source | Intended variables | Historical coverage / granularity | Priority | Known issues / gate |
|---|---|---|---|---|
| NSE official historical index data / NSE Indices | NIFTY spot daily OHLC, index/VIX and official statistics | As published on source portal | 1 | May require interactive download; preserve date range, source file and checksum |
| NSE contract/derivative information | Actual weekly expiry dates, holiday shifts, options contracts | Contract archive dependent | 1 | No fixed-weekday shortcut for confirmatory labels |
| Public minute bars: technovusin/nifty50-historical-data | NIFTY spot OHLC at 1m; 15s data in 2026 | README states from April 2017; 1m data to 2026 | 2 | Open source candidate, known missing bars/frozen stretches/partial sessions. Compare selected dates to official NSE/Dhan |
| Dhan Data API | Intraday spot/options/futures and possibly expired contracts | Subscription / endpoint coverage | 2 | Token valid 24h; refresh securely; do not log token; document API pagination/rate limits |
| Zenodo dataset 10899828 | NIFTY spot, futures, options 1m OHLC | 2017–2020 | 3 | Large archive; verify timestamps, schema, contracts, rights, and consistency |
| HF rissin/nse-options-intraday | Historical daily index options and intraday options | Page describes daily 2001+ and intraday 2024+ | 3 | Large dataset; selectively download exact partitions only |
| NSE India VIX history | Implied-volatility regime | Daily | Optional | Align publication/availability timestamps; volatility is not direction |
| NSE FII/DII / market reports | Flow/market structure | Daily, report-dependent | Optional | Use only data available before forecast time, not hindsight revisions |
| Global benchmark history | US/Asia indices, USD/INR, crude, gold | Daily/intraday | Optional | Timezones/close timing and holidays must be explicit |
| Timestamped news/event data | Event/sentiment flags | Source dependent | Optional | Publication timestamps, duplicates, survivorship and licensing need checks |

## Download candidate
Automation queries the GitHub contents API at https://api.github.com/repos/technovusin/nifty50-historical-data/contents/1min?ref=main and downloads raw CSV paths from year folders and the current-year monthly folder. The workflow caches inputs by run and keeps large raw CSVs in Actions cache rather than committing them. Derived weekly labels, compact feature tables and result artifacts may be committed only after licence/data-policy checks and a size review.

## Canonical raw schema
- Timestamp: candle start, ISO timestamp in IST as specified by source.
- Open, High, Low, Close: NIFTY 50 index OHLC.
- Epoch: Unix seconds if present; use for audit, not as a substitute for timezone validation.
- Volume: present in some newer files; often missing for historical index candles. Do not fabricate it.
- Source path, download time, source commit SHA/ETag, file SHA-256 and row count should be retained in metadata.

## Derived weekly table
Required columns: previous_expiry, expiry_date, anchor_date, anchor_timestamp, anchor_price, expiry_close_timestamp, expiry_close, return_pct, label, expiry_calendar_status, source_quality_status, exclusion_reason. Feature columns are defined in research/METHODOLOGY.md. Label is UP, DOWN or FLAT. All times are interpreted in Asia/Kolkata; timezone-naive input may be localized only where source specification says IST.

## Quality controls
- Parse timestamps in IST; sort; count duplicates and out-of-session rows; check OHLC invariants (low <= open/close <= high), positive prices, duplicate epochs, frozen runs, missing sessions and missing minutes.
- For each anchor, retain the source row, bar timestamp and open; for each expiry, retain final bar timestamp/close. Check selected close against NSE daily close on a sample of expiries.
- Missing anchor or expiry close means excluded with reason; never forward-fill the outcome.
- An inferred holiday expiry is not automatically verified. Keep a flag, cross-check against contracts and exclude uncertain rows from confirmatory analysis.
- Store coverage dates, session counts, median bars/session, completeness by year/month, missingness and price comparison diagnostics.
- Never publish credentials, raw tokens, PIN, TOTP seed, private account identifiers or API responses containing secrets.

## Data-rights note
The upstream repository has a published MIT licence file. That is not by itself proof every underlying market-data value can be freely redistributed. Use remote caching/analysis first and avoid republishing raw data; keep attribution and verify rights before committing substantial data.
