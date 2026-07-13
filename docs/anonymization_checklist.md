# Anonymization Checklist — What Was Found & What To Do About It

This checklist is based on a direct technical inspection of the original `.pbix` file's Power Query M code, data model schema, calculated columns, relationships, and the actual cached row-level data (3,027,528 order rows, 11,987 restaurant rows). Nothing below is guessed — it reflects what was literally stored inside that file.

## 0. The single most important finding

**Renaming or hiding a field in the Power BI Desktop UI does not remove the underlying data.** A `.pbix` file embeds a compressed copy of the entire data model (the VertiPaq store). Even after renaming or hiding a column in the report, the full original column — with every real value — is still physically inside the file, extractable in minutes with free tools.

**Conclusion: the original confidential file must never be uploaded to GitHub, in any form.** The only safe path is building a brand-new `.pbix` from scratch pointed at synthetic data — which is exactly what `hourly-demand-analytics.pbix` in this repository is.

## 1. Confidential elements found in the original file, and what was done

| # | Element | Where found | Confidentiality reason | Action taken |
|---|---|---|---|---|
| 1 | `Foodi Burn` column name | `All Order History` table | Embeds the real product/brand name directly in a column name | **Renamed** to `Platform Subsidy` |
| 2 | Windows file path `C:\Users\user.FEL-OPS-89155\Downloads\...` | Power Query source step | Exposes an internal employee/machine asset ID and internal folder naming convention | **Rebuilt query** with a generic, non-existent local path (the model no longer needs to refresh from a live source) |
| 3 | File name `RESTAURANT LIST APR'26 (1).xlsx` | Power Query source step | Internal file-naming convention tied to a real business process | **Renamed** the source concept generically (`sample_restaurant_master.csv`) |
| 4 | ~8,000 real restaurant chain/brand names | Original `CHAIN`, `Restaurant Name` columns | Real third-party businesses — publishing their order volumes and commission data without consent is a confidentiality and third-party-privacy issue | **Replaced entirely** with 30 fictional chains across 450 fictional branches |
| 5 | Real Account/Key Account Manager names (27), Operations staff names (26), and Ops Manager names (3, including a leftover `"TEST"` row) | Original `KAM`, `OPS`, `OPS MANAGER` columns | Real employee names tied to real performance figures | **Replaced entirely** with fictional names; the `"TEST"` placeholder row was dropped |
| 6 | ~3,000,000 real customer names and phone numbers | Original `User Name`, `User Phone` columns | Direct customer PII — a legal/regulatory issue, not just a confidentiality one | **Removed entirely**, replaced with synthetic `CUST#####` IDs |
| 7 | ~6,000 real delivery rider names | Original `Rider Name` column | Real gig-worker personal data | **Removed entirely**, replaced with synthetic `RDR-####` IDs |
| 8 | Real cities and zones | Both original tables | Combined with real order volumes and commission data, reveals exactly which real locations the business operates in and how well it's doing there | **Replaced** with fictional cities (Rivermouth, Northgate, Lakeview, Eastport, Westbridge, Hillcrest) and fictional neighborhood/zone names |
| 9 | Real payment gateway/bank names | Original `Payment Gateway` column | Reveals real financial partner relationships and their relative transaction share — commercially sensitive | **Replaced** with generic labels (`walletA`, `bankA`, etc.) |
| 10 | Real financial figures (order amounts, commissions, payables, subsidies, rider earnings) | Both original tables | Core confidential business data | **Never published.** The synthetic dataset generates statistically similar but entirely fabricated amounts |
| 11 | Real live production date range (Oct 2025 – Jun 2026) | Original `All Order History` | Reveals the current live operating window and order volume scale | The synthetic dataset uses its own arbitrary date range instead |
| 12 | `"TEST"` rows in status/manager fields | Original `APR26` table | Leftover test/QA rows, not real business data | **Removed** in the rebuild |
| 13 | A leftover working/scratch duplicate report page | Original report layout | Not confidential, but makes the portfolio look unfinished | **Deleted** before publishing — the rebuilt file only contains the 6 finished pages |

## 2. What was NOT found (so there's no guessing involved)

- The original model had **no explicit DAX measures** — every number was Power BI's implicit `Count of Order ID`. The rebuilt version adds a proper measure layer (`Total Orders`, `Total Revenue`, `Avg Order Value`, `Cancellation Rate %`) — see `docs/dax_measures.md`.
- No Row-Level Security (RLS) roles were defined in the original file.
- No Python/R scripts, no external API calls, and no custom visuals were used (all visuals were Power BI's built-in `clusteredColumnChart`, `pivotTable`, and `slicer`) — so there was nothing hidden in scripting steps.
- No textboxes, images, or logos were found embedded in the original report layout.

## 3. Pages: what exists in the published version

| Page (as rebuilt) | Notes |
|---|---|
| **Overview** | Rebuilt with 3 clustered column charts (hour / 30-min / 15-min), 4 KPI cards, and a Month slicer |
| **Hour Wise** | Pivot table of order volume by hour × date, with hour and date slicers |
| **Restaurant Wise** | Pivot table of order volume by restaurant × date (the original file's equivalent page was called "Chain wise") |
| **City Wise** | Pivot table of order volume by city × date (the original file's equivalent page was called "Zone Wise") |
| **Account Manager Wise** | Pivot table of order volume by account manager/restaurant × date |
| **Sunday Comparison** | Pivot table using the `Sunday Occurrence` calculated column, comparing order volume across every Sunday in the dataset by month-occurrence number |

The original file's leftover "Duplicate of Chain wise" working-copy page was not recreated — it added no analytical value and only existed as a scratch copy during development.
