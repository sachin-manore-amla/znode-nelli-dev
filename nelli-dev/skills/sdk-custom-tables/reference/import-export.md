# Import and export

What this answers: how to load many rows from a CSV, how to get data out, what the engine does with each row, and where the published contract and the real behaviour differ.

## Import at a glance

| | |
|---|---|
| Admin path | Dev Center > Custom Tables > Edit Custom Table > **Import** |
| File | **CSV only** (`.csv`; anything else: *Only select a CSV file.* / *Please select file with .csv extension only*). File name (without extension) up to 200 characters. |
| Header row | **Field Codes**, never Field Names; no `Id` column |
| Commas in text | enclose the value in double quotes |
| Behaviour | **upsert** when the table has a unique field, **blind insert** when it does not |
| Errors | per row, good rows still load; the import log has the reasons |
| After upload | *Update process has been initiated.* with a link to the import logs |

Always start from the template: **Download Template** on the Import panel (or `GET /v1/custom-table-data/{tableKey}/table-template`). It has the right headers and one blank row. Columns come back in repository order, not Display Order. Export uses the same headers, so an exported file re-imports cleanly.

```csv
StoreCode,StoreName,SeatCount,IsOpen,OpenedOn
LONDON01,London Bridge,48,true,2026-01-31
LEEDS01,Leeds Central,32,1,2026-02-15
```

## What the engine does

1. Reads the file into a temporary area.
2. Matches columns to the table's fields **by Field Code**. A column that is not a field fails the **whole** import (*Data column must be mapped with the template.*).
3. Validates each value by field type, length and uniqueness.
4. Rows that fail are logged and dropped; duplicates of the unique value inside the file are reduced to the **last** occurrence (*Duplicate records must be excluded from the import/update file.* on the dropped ones).
5. The rest are inserted or updated inside a transaction.
6. A status is recorded: success, partial or failed (Imports screen: Started, Completed Successfully, Completed With Errors, Failed).

**Re-importing the same file into a table with no unique field duplicates every row.** Give the table a unique field first if imports will repeat.

## Per-row validation

| Check | Result |
|---|---|
| Column not in the table | whole import fails |
| Unique field missing from the file | whole import fails (*Unique column must be included in the import/update file.*) |
| Unique value empty | row rejected (*Input is required.*) |
| Every column in the row blank | row rejected (*All column data in the provided row is empty.*) |
| Unique value already exists on a pure insert | row rejected (*The input cannot be added as it already exists in the database.*) |
| Unique value not found on a pure update | row rejected (*Input cannot be updated because of its unavailability in database.*) |
| Boolean not in the accepted set | row rejected: accepted are True/False/1/0 and **Yes/No** (import accepts Yes and No; the direct API does not) |
| Invalid date | row rejected (*Input must include a valid date and time.*) |
| Numeric out of precision/scale | row rejected (*The numeric value should fall within the range of ...*) |
| Text longer than Field Length | row rejected (*Input value must not exceed the maximum character limit of N*) |

Empty values: an empty `datetime` or `Numeric` cell becomes NULL on import (the direct API stores `1900-01-01` for an empty date); an empty Text cell becomes an empty string. There is no general "required field" rule.

## Partial failures report success

Failed rows are logged and the good rows commit, but the API still returns `IsSuccess: true`, and the Admin import action always reports success to the browser; only the notification banner reflects a failure (*Import process failed. Please review the logs for more details.*). **Always open View Import Logs after an import**: per-row reasons are only there. Other Admin messages: *CSV does not contain any data.*, *No data found in the CSV file.*, *File not present.*

## Through the API: the real contract

`POST /v1/custom-table-data/import` with `{ "TableKey", "FileName", "ImportType", "UserId", ... }`.

The published spec describes `importData` as base64 CSV and `importType` as `Insert`, `Update` or `Replace`. **The implementation does not use them.** What Admin actually does: converts the CSV to JSON, uploads it to blob storage, then calls the API with only the file name and an import type of `CustomTableTemplate`. The service reads `FileName` and ignores `importData`; an empty `FileName` gives a 500. An integration written strictly from the published contract fails. To import through the API: place the file in blob storage and pass its path, or, for fewer than a few hundred rows, call the row endpoints (single rows give a clear per-row error; use bulk-insert / bulk-update for volume). Confirm on the customer's version; the file name in the request must not include the container name.

For recurring ERP loads use a Commerce Connector data exchange rather than scripting this endpoint (see `sdk-data-exchange`).

## Export

| | |
|---|---|
| Admin | Edit Custom Table > **Export**. *Export has been initiated. Click here or redirect to the Exports screen to view more details.* Download from Dev Center > Export (Export Type: Custom Table, File Type: CSV). |
| API | `GET /v1/custom-table-data/{tableKey}/export`, then `GET /v1/custom-table-data/{tableName}/download` |
| Timing | **asynchronous**: the call returns at once, the file is produced in the background |
| Output | a **ZIP of CSV parts** (`CustomTable1.csv`, `CustomTable2.csv`, ...), split at roughly 96 MB |
| Headers | the Field Codes; `Id` is excluded |
| Rows | **all rows**: the filter, sort and paging parameters in the spec are ignored |
| Empty table | refused: *No Data to Export the Custom Table* (Admin: *No Data Available to Export.*) |

Known gaps: the response `Message` is always null; the download file name carries a random suffix that is never returned, and download is keyed by table **name**, so scripting a download needs the Export screen or the process log; on deployments that use cloud storage the download route reads local disk only. Treat scripted downloads as unreliable and use the Export screen.

## Limits and advice

| | |
|---|---|
| Import file size and row count | no limit enforced in the product |
| Import timeout | 500 seconds at the data layer |
| Export timeout | 1800 seconds |
| KB advice | CSV only; one import at a time (even from a scheduler: if several schedulers start together, the first-created runs and the others fail to start); avoid more than one import an hour; prefer batches |
| Observed | no lock stops two imports starting together: treat concurrent imports as unsafe |

## Sources

KB Managing Custom Tables (43000757107) and Limitations & Fair Usage (43000782807); observed on a development environment (2026-10-05/08); release notes 10.12.1.0 (blob file imports fixed) and 10.13.0.0 (imports failing on numeric precision fixed).
