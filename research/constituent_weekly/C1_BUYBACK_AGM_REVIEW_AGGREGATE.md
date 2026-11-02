# C1 Buyback, Dividend-Misclassification and AGM Review — 49 Candidates

**Review date:** 2026-11-03  
**Protected queue:** [41517328794 — SUCCESS](https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/41517328794)  
**Disposition:** 49 candidates reconciled; **C1 overall remains PARTIAL / NOT PASSED**.

## Scope and corrected classification

The recipient-encrypted queue contained 49 unique candidates (20 feed-labelled buybacks and 29 feed-labelled AGM/other entries). All 49 joined unambiguously to point-in-time member keys. Raw source rows and the private source-to-row mapping remain outside GitHub because the underlying TejHQ source is personal-use-only.

| Corrected class | Count | Result |
|---|---:|---|
| Buybacks | 21 | One feed “other” reclassified; primary offer/record-date sources found for all 21 |
| Dividends reclassified from “other” | 3 | Amount and record-date disclosures found |
| AGM/governance events | 25 | No price factor; forecast-time notice gate remains closed |
| **Total** | **49** | **All candidates classified** |

## Dividend reclassifications

- **HCL Technologies:** interim dividend ₹2 per share; record date 6 August 2018. HCL issuer history confirms the amount/date, with the MSE security record corroborating the ex-date.
- **TCS:** interim dividend ₹4 per share; record date 24 October 2018. TCS issuer dividend-payment history confirms amount/date.
- **Nestlé India:** interim dividend ₹135 per share; record date 2 November 2020. The issuer board outcome confirms amount, record date and payment commencement.

These are dividends, not AGM or buyback events. Preserve NIFTY **price-index** semantics: do not mechanically reinvest cash dividends or substitute a total-return target.

## Buyback review

Primary issuer, SEBI letter-of-offer/public-announcement or official-exchange offer/record-date evidence was found for all 21 buybacks. Public sources cover HCLTech, L&T, IndianOil, ONGC, Coal India, Tech Mahindra, Adani Ports, Wipro, TCS, NTPC, GAIL, Bajaj Auto and Infosys. Selected links are listed in the machine-readable summary.

A buyback has **no universal mechanical price-adjustment factor**. Its price/float effects depend on offer size, premium, tender route, entitlement, acceptance, completion and extinguishment. For predictive features, use only announcement/offer information public by the 10:00 IST forecast cutoff. Never backdate later record-date, acceptance or extinguishment information. No factor has been applied and no buyback-affected cycle has been released into confirmatory modelling.

## AGM/governance treatment

The remaining 25 entries are AGM/governance and meeting-calendar events. They do not change equity share count and receive no price adjustment. A meeting date is not the time the notice became public. Until the issuer/exchange public-notice timestamp is verified relative to 10:00 IST, all 25 stay excluded from predictive features; governance/calendar metadata may be retained for audit only.

## Corrected full 711-candidate catalogue

| Final class | Count |
|---|---:|
| Equity bonus-share actions | 17 |
| Bonus-labelled non-convertible debenture distributions | 2 |
| Stock splits | 9 |
| Rights issues | 6 |
| Merger/demerger schemes | 3 |
| Buybacks | 21 |
| Dividends | 628 |
| AGM/governance events | 25 |
| **Total** | **711** |

The 628 dividends comprise the original 625 dividend-labelled candidates plus three reclassified “other” entries. No dividend reinvestment or total-return target substitution is allowed.

## Remaining limitations

- Buyback acceptance, completion and extinguishment have not been joined to all affected weekly stock cycles.
- The 25 AGM public-notice timestamps are not all checked against the 10:00 IST cutoff; they remain excluded from features.
- Announcement timestamps for all 628 dividends have not been joined to forecast-time availability.
- Full historical ISIN/predecessor-successor identity and price continuity remain incomplete.
- Dhan adjusted-scale continuity has direct empirical checks for only two bonus/split examples; it is not universal evidence.
- Rights TERP and scheme-specific merger/demerger continuity remain open.

## Selected source links

**Buybacks:** [HCLTech 2018 SEBI letter of offer](https://www.sebi.gov.in/sebi_data/attachdocs/aug-2018/1535088017164.pdf); [L&T 2018 announcement](https://investors.larsentoubro.com/upload/Announcements/LARSEN_%26_TUBRO_LIMITED_Buyback_ad.pdf); [IndianOil buyback archive](https://www.iocl.com/buyback-of-shares-by-indianoil); [ONGC SEBI filing](https://www.sebi.gov.in/sebi_data/attachdocs/mar-2019/1551418134010.pdf); [Coal India SEBI filing](https://www.sebi.gov.in/sebi_data/attachdocs/feb-2019/1550670210902.pdf); [Tech Mahindra SEBI filing](https://www.sebi.gov.in/sebi_data/attachdocs/mar-2019/1552973486748.pdf); [Adani Ports LOF](https://www.adaniports.com/-/media/Project/Ports/CorporateGovernance/Buy-back/Letter-of-Offer-for-Buyback.pdf); [Wipro 2019 announcement](https://www.wipro.com/content/dam/nexus/en/investor/buy-back/buyback2019/stock-exchange-public-announcement-for-buy-back-of-equity-shares.pdf); [TCS 2020 filing](https://www.sebi.gov.in/sebi_data/attachdocs/nov-2020/1605951361683.pdf); [NTPC 2020 NSE LOF](https://nsearchives.nseindia.com/corporate/NTPC_26112020195518_NTPCLOF.pdf); [GAIL 2021 LOF](https://www.sebi.gov.in/sebi_data/attachdocs/jan-2021/1611747155575.pdf); [TCS 2022 filing](https://www.sebi.gov.in/sebi_data/commondocs/feb-2022/TCS-DLO_p.pdf); [Wipro 2023 announcement](https://www.wipro.com/content/dam/nexus/en/investor/buy-back/buyback2023/post-buyback-public-announcement.pdf); [L&T 2023 disclosure](https://www.lnt.in/LSEQFRSept2023/); [TCS 2023 LOF](https://www.sebi.gov.in/sebi_data/commondocs/nov-2023/Tata_Consultancy_LOO_p.pdf); [Bajaj Auto 2024 filing](https://www.bseindia.com/xml-data/corpfiling/AttachHis/fb78f27e-699e-4e07-88d8-f22d404a8dec.pdf); [Infosys 2025 LOF](https://www.infosys.com/investors/shareholder-services/documents/buyback-2025/letter-offer.pdf); [Wipro 2026 LOF](https://www.sebi.gov.in/sebi_data/commondocs/jun-2026/Wipro%20Limited%20-%20LOF_p.pdf); [Bajaj Auto 2026 filing](https://legacy.bajajauto.com/-/media/images/bajajauto/media-kit/press-release/disclosures/newspaper-publications/fy2026-27/se-with-lof.pdf).

**Dividends:** [HCLTech issuer history](https://www.hcltech.com/investor-relations/unpaid-dividend-information) and [MSE exchange record](https://www.mse-india.in/corporates/corporate-securities-information/corporate-update/default?symbol=HCLTECH&type=4&vmode=vm); [TCS issuer dividend history](https://www.tcs.com/investor-relations/dividend-payment-details); [Nestlé India issuer board outcome](https://www.nestle.in/media/specialannouncements/outcome-meeting-board-directors-company-held-23rd-october-2020).

## Phase decision

**C1 remains PARTIAL / NOT PASSED.** The 37 complex and 49 secondary candidate reviews are complete at aggregate classification level. The 628 dividends require forecast-time and price-index treatment; 25 AGM notice timestamps and buyback affected-cycle evidence remain open. Full dated security identity, adjusted-price continuity and affected-cycle exclusions are incomplete. C2 remains PASS WITH C1 LIMITATIONS; C3 remains exploratory with no confirmed edge; confirmatory C4 and execution/trading C5 remain gated.
