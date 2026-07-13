# DAX — Measures & Calculated Columns

This reflects exactly what's built in `hourly-demand-analytics.pbix`.

## 1. Explicit Measures

These aggregate the fact table and are reused across the report's KPI cards and visuals.

```dax
Total Orders = COUNTROWS('sample_orders')
```
A simple row count of the fact table — the base measure everything else is built from.

```dax
Total Revenue = SUM('sample_orders'[Total Amount])
```
Sums the order value column.

```dax
Avg Order Value = DIVIDE([Total Revenue], [Total Orders])
```
Uses `DIVIDE` instead of `/` so it returns blank (not an error) if `Total Orders` is ever zero — e.g. under a filter combination with no matching rows.

```dax
Cancellation Rate % =
DIVIDE(
    CALCULATE(
        [Total Orders],
        'sample_orders'[Order Status] IN {"cancelled", "restaurant_rejected", "not_delivered"}
    ),
    [Total Orders]
)
```
`CALCULATE` overrides the current filter context to count only the three "did not complete" statuses, then divides by the unfiltered total to get a percentage. Formatted as a percentage in the model so it displays as `16.84%` rather than `0.17`.

## 2. Calculated Columns

Computed once at the model layer (row-by-row, stored in the table) so every visual across every page reuses the exact same buckets consistently, instead of recalculating per visual.

### `1 Hour Range`
```dax
1 Hour Range = FORMAT(HOUR('sample_orders'[Order Date]), "00") & "-" & FORMAT(MOD(HOUR('sample_orders'[Order Date]) + 1, 24), "00")
```
Buckets each order into an hour band like `13-14`. The `MOD(...,24)` handles the midnight wraparound (`23-00`) correctly.

### `30 Min Range`
```dax
30 Min Range =
VAR h = HOUR('sample_orders'[Order Date])
VAR m = MINUTE('sample_orders'[Order Date])
VAR startMin = IF(m < 30, 0, 30)
VAR endHour = IF(startMin = 30, h + 1, h)
VAR endMin = IF(startMin = 30, 0, 30)
RETURN
FORMAT(TIME(h, startMin, 0), "HH:mm") & "-" & FORMAT(TIME(MOD(endHour, 24), endMin, 0), "HH:mm")
```
Same idea at 30-minute granularity, written with `VAR`/`RETURN` for readability and to avoid recomputing `HOUR()`/`MINUTE()` multiple times.

### `15 Min Range`
```dax
15 Min Range =
VAR h = HOUR('sample_orders'[Order Date])
VAR m = MINUTE('sample_orders'[Order Date])
VAR startMin = INT(m / 15) * 15
VAR totalEnd = h * 60 + startMin + 15
VAR endHour = INT(totalEnd / 60)
VAR endMin = MOD(totalEnd, 60)
RETURN
FORMAT(TIME(h, startMin, 0), "HH:mm") & "-" & FORMAT(TIME(MOD(endHour, 24), endMin, 0), "HH:mm")
```
Same pattern at 15-minute granularity, using total-minutes arithmetic to correctly roll over both the hour and (at midnight) the day boundary.

### Sort-helper columns
```dax
1 Hour Sort  = HOUR('sample_orders'[Order Date])
30 Min Sort  = HOUR('sample_orders'[Order Date]) * 60 + IF(MINUTE('sample_orders'[Order Date]) < 30, 0, 30)
15 Min Sort  = HOUR('sample_orders'[Order Date]) * 60 + INT(MINUTE('sample_orders'[Order Date]) / 15) * 15
```
These exist purely so the text-formatted range columns above can be sorted chronologically (via **Column tools → Sort by column** in Power BI) instead of alphabetically, where `"09-10"` would otherwise sort after `"19-20"`. `1 Hour Sort` stays small (0-23) since it's just the hour number; `30 Min Sort` and `15 Min Sort` are measured in **minutes since midnight**, which is why they show larger numbers like `1020` — that's what lets a bucket like `17:00-17:30` correctly sort after `12:00-12:30` across the full day.

### `Sunday Occurrence` — the most interesting DAX in the file
```dax
Sunday Occurrence =
VAR d = 'sample_orders'[Date]
RETURN
IF(
    WEEKDAY(d, 1) = 1,
    "Sunday " & ROUNDUP(DAY(d) / 7, 0),
    BLANK()
)
```
For every row, this checks whether the date falls on a Sunday (`WEEKDAY(d, 1) = 1`, where the `1` argument means the week starts on Sunday). If it does, it labels that Sunday with its occurrence number within the calendar month — `ROUNDUP(DAY(d) / 7, 0)` turns "the 4th" into `1`, "the 11th" into `2`, "the 18th" into `3`, and so on — producing labels like `"Sunday 1"`, `"Sunday 2"`, `"Sunday 3"`, `"Sunday 4"`. Every non-Sunday row returns blank.

This is what powers the **Sunday Comparison** page: instead of only ever comparing the two most recent Sundays, it lets a pivot table show order volume broken out by *every* Sunday across the whole dataset, side by side — so an account manager can see whether Sunday demand is trending up, down, or holding flat across a full month or more, not just week-to-week.

## 3. Ideas for further additions (not yet built — optional next steps)

- **YoY / MoM % change measures** using `DATEADD` or `SAMEPERIODLASTYEAR`, e.g.:
```dax
Orders WoW % Change =
VAR CurrentWeek = [Total Orders]
VAR PriorWeek = CALCULATE([Total Orders], DATEADD('sample_orders'[Date], -7, DAY))
RETURN DIVIDE(CurrentWeek - PriorWeek, PriorWeek)
```
- **Total Platform Subsidy** and **Subsidy % of Revenue**, since both columns already exist in the fact table but aren't yet surfaced as measures:
```dax
Total Platform Subsidy = SUM('sample_orders'[Platform Subsidy])
Subsidy % of Revenue = DIVIDE([Total Platform Subsidy], [Total Revenue])
```
