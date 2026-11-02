# C1 Official NSE PR Bundle Fixed-Date Probe

Updated: 2026-11-02T09:49:03.750861+00:00
Result: PASS_FIXED_PROBE
Schema-confirmed archives: 4/4
Pre-13-Oct-2025 schema: True
Post-13-Oct-2025 schema: True

| Date | Status | Bytes | SHA-256 | Encrypted cache hit |
|---|---|---:|---|---|
| 2018-04-02 | SCHEMA_CONFIRMED | 502142 | 10dafb999b73f73bc2aa7df57c0e62b130e7291dec290cfa897964c12bec9e92 | True |

### Schema: 2018-04-02

- Corporate-action member: bc020418.csv
- Header fields: SERIES, SYMBOL, SECURITY, RECORD_DT, BC_STRT_DT, BC_END_DT, EX_DT, ND_STRT_DT, ND_END_DT, PURPOSE
- Announcement member present: True
- Board-meeting member present: True

| 2024-04-16 | SCHEMA_CONFIRMED | 432838 | c8d77309dd868db21bfa376021e02c8fa8c19b94c26c32136417d9a2afe29bda | True |

### Schema: 2024-04-16

- Corporate-action member: bc160424.csv
- Header fields: SERIES, SYMBOL, SECURITY, RECORD_DT, BC_STRT_DT, BC_END_DT, EX_DT, ND_STRT_DT, ND_END_DT, PURPOSE
- Announcement member present: True
- Board-meeting member present: True

| 2025-10-14 | SCHEMA_CONFIRMED | 579043 | e039feca01b7a49e9f76c135ae36927d94392a42f3dde64b201ab541b4e97746 | True |

### Schema: 2025-10-14

- Corporate-action member: bc14102025.csv
- Header fields: SERIES, SYMBOL, SECURITY, RECORD_DT, BC_STRT_DT, BC_END_DT, EX_DT, ND_STRT_DT, ND_END_DT, PURPOSE
- Announcement member present: True
- Board-meeting member present: True

| 2026-04-17 | SCHEMA_CONFIRMED | 599129 | 7d755b44abd7896c256dd2490214740c9c13a7874db5c7ae8df595d1efb0c6f3 | True |

### Schema: 2026-04-17

- Corporate-action member: bc17042026.csv
- Header fields: SERIES, SYMBOL, SECURITY, RECORD_DT, BC_STRT_DT, BC_END_DT, EX_DT, ND_STRT_DT, ND_END_DT, PURPOSE
- Announcement member present: True
- Board-meeting member present: True


## Limitations

- Four-date probe only; not complete daily archive coverage.
- Only CSV headers and member presence are inspected; no event rows are published.
- Retrieval does not establish licence for bulk extraction or redistribution.
- No issuer verification or adjustment-factor calculation/application is performed.


## 2026-11-03 — Rights interpretation and archive-probe retirement

The 4/4 result establishes technical archive access and schema only. It is not permission for systematic automated extraction or for use of NSE website data in trading simulation. Following review of the current NSE Terms of Use and Data Sharing & Usage Policy, the automated PR archive route is retired pending written permission/agreement. The historical result is retained only as technical-feasibility metadata. Sources: https://www.nseindia.com/static/nse-terms-of-use and https://www.nseindia.com/static/market-data/nse-data-policy
