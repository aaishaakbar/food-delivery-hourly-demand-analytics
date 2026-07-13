# Power Query (M) Transformations

Below is the actual M logic from the original confidential file, annotated, with the confidential elements (marked ⚠️) contrasted against the cleaned public version. This matches the queries in `hourly-demand-analytics.pbix`, sourced from `data/sample_orders.csv` and `data/sample_restaurant_master.csv`.

## 1. Orders query (`sample_orders`, originally `All Order History`)

**Original pattern (folder-based multi-file ingestion):**
```m
let
    Source = Folder.Files("C:\Users\user.FEL-OPS-89155\Downloads\All Order History"), // ⚠️ real file path + asset ID
    #"Filtered Hidden Files1" = Table.SelectRows(Source, each [Attributes]?[Hidden]? <> true),
    #"Invoke Custom Function1" = Table.AddColumn(#"Filtered Hidden Files1", "Transform File", each #"Transform File"([Content])),
    #"Renamed Columns1" = Table.RenameColumns(#"Invoke Custom Function1", {"Name", "Source.Name"}),
    #"Removed Other Columns1" = Table.SelectColumns(#"Renamed Columns1", {"Source.Name", "Transform File"}),
    #"Expanded Table Column1" = Table.ExpandTableColumn(#"Removed Other Columns1", "Transform File", Table.ColumnNames(#"Transform File"(#"Sample File"))),
    #"Changed Type" = Table.TransformColumnTypes(#"Expanded Table Column1", {
        {"Source.Name", type text}, {"Order ID", type text}, {"Order Date", type datetime},
        {"Restaurant Name", type text}, {"User Name", type text}, {"User Phone", Int64.Type}, // ⚠️ PII
        {"Rider Name", type text}, // ⚠️ PII
        {"Total Amount", type number}, {"Foodi Burn", type number}, /* ⚠️ brand name in column */
        ... /* remaining ~30 columns, all straightforward type casts */
    }),
    #"Inserted Month Name" = Table.AddColumn(#"Changed Type", "Month Name", each Date.MonthName([Order Date]), type text),
    #"Inserted Date" = Table.AddColumn(#"Inserted Month Name", "Date", each DateTime.Date([Order Date]), type date)
in
    #"Inserted Date"
```

**What this pattern does (in plain English):**
1. Points at a *folder*, not a single file — so every `.xlsx`/`.csv` dropped into that folder becomes part of the model automatically
2. Filters out hidden/system files (e.g. Excel lock files like `~$filename.xlsx`)
3. Applies a reusable **custom function** (`Transform File`) to every file so each file goes through identical cleaning logic — this is the scalable part: adding a new month of data means adding one file, not editing the query
4. Captures which file each row came from into `Source.Name` — useful for auditing/debugging by month
5. Casts every column to its correct type explicitly (Power BI's auto-detect is not reliable enough for a production model)
6. Derives two convenience columns: `Month Name` (text, for slicers) and `Date` (date-only, stripped of time, for day-level slicing)

**Public/portfolio version — as actually built:**
```m
let
    Source = Csv.Document(File.Contents("C:\PowerBI-Projects\food-delivery-hourly-demand-analytics\sample_orders.csv"), [Delimiter=",", Encoding=1252, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"Order ID", type text}, {"Order Date", type datetime}, {"Restaurant Branch ID", Int64.Type},
        {"Restaurant Name", type text}, {"Customer ID", type text}, {"Rider ID", type text},
        {"Order Status", type text}, {"Order Type", type text}, {"Total Amount", type number},
        {"Branch Zone", type text}, {"Delivery Zone", type text}, {"Payment Method", type text},
        {"Payment Gateway", type text}, {"Payment Status", type text}, {"Delivery Charge", Int64.Type},
        {"Discount Amount", Int64.Type}, {"Promo Code", type text}, {"Restaurant Commission", type number},
        {"Platform Subsidy", type number}, {"Restaurant Subsidy Share", type number}, {"Rider Earning", Int64.Type},
        {"Avg Delivery Time Min", Int64.Type}, {"Delivery Status", type logical}
    }),
    #"Inserted Month Name" = Table.AddColumn(#"Changed Type", "Month Name", each Date.MonthName([Order Date]), type text),
    #"Inserted Date" = Table.AddColumn(#"Inserted Month Name", "Date", each DateTime.Date([Order Date]), type date)
in
    #"Inserted Date"
```

**Note on `Restaurant Branch ID`:** this column is what the `sample_orders` → `sample_restaurant_master` relationship is built on — it must be cast to `Int64.Type` (a whole number) so it matches the type of `restaurant_branch_id` in the restaurant master table. A mismatched type on either side of a relationship key is one of the most common reasons a Power BI relationship silently fails to filter correctly.

**Note on the file path:** the source path above intentionally points at a folder (`C:\PowerBI-Projects\...`) that doesn't exist on any real machine. This is deliberate — it replaces the original internal file path (which contained a real company asset tag) without needing to actually relocate any files. Because of this, the query will show a refresh error if you try to reload it from source — that's expected for a static portfolio snapshot; the data is already cached in the model and doesn't need to be refreshed again.

*(If you want to keep the "folder of files" pattern for portfolio realism, split `sample_orders.csv` into a few monthly CSVs and point `Folder.Files()` at a folder instead — the logic is identical, just swap the source step.)*

## 2. Restaurant Master query (`sample_restaurant_master`, originally `APR26`)

**Original:**
```m
let
    Source = Excel.Workbook(File.Contents("C:\...\RESTAURANT LIST APR'26 (1).xlsx"), null, true),
    APR26_Sheet = Source{[Item="APR26",Kind="Sheet"]}[Data],
    #"Promoted Headers" = Table.PromoteHeaders(APR26_Sheet, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"restaurant_branch_name", type text}, {"restaurant_branch_id", Int64.Type},
        {"CHAIN", type text}, {"KAM", type text}, /* ⚠️ real employee names live in this column */
        {"OPS", type text}, {"OPS MANAGER", type text}, /* ⚠️ real employee names */
        ...
    })
in
    #"Changed Type"
```

**Public/portfolio version — as actually built:**
```m
let
    Source = Csv.Document(File.Contents("C:\PowerBI-Projects\food-delivery-hourly-demand-analytics\sample_restaurant_master.csv"), [Delimiter=",", Encoding=1252, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"restaurant_branch_id", Int64.Type}, {"restaurant_branch_name", type text},
        {"restaurant_primary_id", Int64.Type}, {"restaurant_primary_name", type text},
        {"restaurant_zone_id", Int64.Type}, {"restaurant_zone_name", type text},
        {"city_name", type text}, {"cuisine_name", type text}, {"commission_pct", type number},
        {"enabled_disabled", type text}, {"restaurant_onboard_date", type date},
        {"is_credit", type text}, {"delivery_by_partner", type logical},
        {"restaurant_type", type text}, {"chain", type text}, {"account_manager", type text},
        {"cuisine", type text}, {"ops_staff", type text}, {"ops_manager", type text}, {"status", type text}
    })
in
    #"Changed Type"
```

The four trailing unused columns present in the original (`Column21`–`Column24`, all blank) were dropped in the rebuild — they added no value and were a sign of a messy source Excel file, which isn't something you want visible in a portfolio piece.

## 3. Calculated columns added after loading

Both `Month Name`/`Date` (added at the query stage, shown above) and the time-bucketing/Sunday columns (added as DAX calculated columns after loading — see `docs/dax_measures.md`) work together: Power Query handles the type-safe ingestion and the two simple date derivations, while DAX handles everything that needs row-context logic (hour bucketing, Sunday-occurrence numbering). This split is a deliberate modeling choice worth explaining in an interview: M is better suited to source-shaping and type-casting, DAX is better suited to logic that depends on relationships or needs to recalculate dynamically.
