# C1 Corporate-Action Candidate Catalogue

**Updated:** 2026-11-01T14:54:00.799437+00:00
**Status:** COMPLETED_WITH_REVIEW_REQUIRED; corporate-action gate NOT PASSED
**Window:** 2018-04-01 to 2026-10-30

## Aggregate counts

- Candidate NSE action rows: 18393
- Deduplicated event rows: 18361
- Duplicate rows: 32
- Matched to point-in-time members by effective symbol alias: 711
- Unmatched/non-member: 17650
- Ambiguous member events: 0
- Missing ISIN: 0

| Action class | All | Matched member | Unresolved |
|---|---:|---:|---:|
| agm_or_other | 5628 | 29 | 5599 |
| bonus | 337 | 19 | 318 |
| buyback | 253 | 20 | 233 |
| dividend | 11485 | 625 | 10860 |
| merger_demerger | 94 | 3 | 91 |
| rights | 246 | 6 | 240 |
| split | 318 | 9 | 309 |

## Adjustment handling

- **dividend:** Needs previous raw close and confirmed cash amount; candidate factor (previous_close-cash)/previous_close; not calculated.
- **split:** Check face_value_to/face_value_from against issuer/exchange notice; not applied.
- **bonus:** Verify source ratio semantics and issuer notice before calculating a factor; not applied.
- **rights:** TERP requires entitlement ratio and subscription price; manual review required.
- **buyback:** No mechanical price factor; keep as a separately dated event feature.
- **merger_demerger:** No generic scaling or cross-security stitching; exclude affected cycles until scheme terms are verified.
- **agm_or_other:** Review source subject and issuer filing before classification.
- **unclassified:** Unknown event class; affected windows remain unresolved.

## Cache and source controls

- Pinned revision: f576704883fff86a6facdcde336db6ce19502063
- Encrypted cache hits: 0
- New partitions downloaded: 9
- Only AES-256-GCM ciphertext is retained in Actions cache.
- Raw action rows, ISINs, cash values, ratios and source subjects are not published.

**Conclusion:** candidate events are catalogued, but no return adjustment or C1 corporate-action pass is claimed.
