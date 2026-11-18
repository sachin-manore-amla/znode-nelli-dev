# CSV Template — Functional

> **Screenshot (2026-10-08, INT admin — new capture).** 🔄 Updated. Verified read-only on INT
> Import side panel (`/CustomTable/GetCustomTableTemplate?tablekey={tableKey}`) shows heading
> "IMPORT TABLE DATA", the text "Add Records to the Table using the csv Import", a
> "Download a sample csv file" block with a **Download Sample File** link, and a "Select a .csv file"
> Browse control. The template downloads from `/CustomTable/DownloadTemplate?tableKey={tableKey}` as
> **v** (content-type application/vnd.xls): a header row of the table's
> field codes (`name,Number,Address`) followed by one blank data row.
>

## 1. What it is

The CSV template is a downloadable file that shows which columns a custom table expects for import. It contains one header row with each field's code and one empty data row. You use it to prepare data for importing records into the table.

## 2. Where you do it

In the **admin**, navigate to **Dev Center > Custom Tables**, select a table, open its record grid, and click the **Import** button. A side panel opens with a **Download** link for the template.

Not available in the webstore, Commerce Portal, or B Store app.

## 3. Who can do it

Any admin user who can access the Custom Tables section in Dev Center can download the template.

## 4. Step by step

1. Open the custom table's record grid in the admin.
2. Click **Import**. A side panel opens.
3. Click the **Download** link in the side panel.
4. The browser downloads a CSV file.

## 5. What is allowed and what is not

- The table must exist. If the table key is invalid, the system returns a "The requested table does not exist" error.
- If the table has no fields defined, the template downloads but is essentially empty (one row, no columns).
- The template can be downloaded multiple times without any side effects.

## 6. Messages you may see

| Message | When it appears | When it does not |
|---|---|---|
| "The requested table does not exist" | The table key does not match any existing custom table | The table exists |

## 7. How it differs

- The template always uses **Field Codes** as column headers, not Field Names.
- The downloaded file has a fixed filename (it does not include the table's name or key).
- The internal row identifier is never included as a column.
- All field types are included (Text, TextArea, Number, Boolean, DateTime) regardless of type.
- Columns appear in the order the fields were created (database default order), not by any display-order setting.

## 8. What can be combined

No combinations apply. The template is a standalone download.

## 9. What it changes elsewhere

Nothing. Downloading the template is a read-only action. It does not create, modify, or delete any data.

## 10. Quick answers

| Question | Answer |
|---|---|
| What columns are in the template? | One column per field, using the Field Code as the header. |
| Is there sample data in the template? | There is one row of empty values. |
| Does the filename include the table name? | No, the filename is a fixed constant. |
| What format is the file? | CSV. |
| Does it include the row id? | No. |
| Is the template cached? | Yes, cached per request path at the API layer; regenerated on cache miss. |
| What if the table has no fields? | The template downloads but has no columns. |

## 11. For developers

See `03-frontend-admin.md` for the admin screen and call tree, `06-api.md` for the API endpoint, `07-functions.md` for every method line by line, and `08-database.md` for the tables read.

## Fields and options

The Download Template / Import screen (from verified code; not captured live):

| Control | Behaviour | Where it comes from |
|---|---|---|
| Download Template | downloads a CSV whose header row is the table's field codes | `GET v1/custom-table-data/{tableKey}/table-template` |
| Choose file / Upload | accepts a `.csv` file of records | admin-side blob upload then `POST v1/custom-table-data/import` |
| Template columns | one column per custom-table field (plus the key column) | the table's field definitions |

## Screenshot verification (2026-10-08)

| Screenshot | Shows | Result |
|---|---|---|
| 01-admin-import-panel-download-sample.png | The Import side panel with the "Download Sample File" link and the "Select a .csv file" Browse control | ✅ Verified |
| Template file contents |v` — header row of field codes (`name,Number,Address`) + one blank data row, downloaded from `/CustomTable/DownloadTemplate?tableKey={tableKey}` | ✅ Verified |

Path-only URL: `/CustomTable/GetCustomTableTemplate?tablekey={tableKey}` (the Import/Download panel); the template itself downloads from `/CustomTable/DownloadTemplate?tableKey={tableKey}` (ids shown as {placeholders}).

## Corrections (2026-10-08)

| Was documented as | Corrected to | Evidence |
|---|---|---|
| "⚠️ Not verifiable live in this pass" — screen not reachable, no table could be seeded | Verified on INT: the Import panel, the Download Sample File link and the template contents (field-code header + one blank row, filenamev`) are confirmed | New INT capture 01 and the downloaded template against seeded table `testabhi` (2026-10-08) |
| §4 said the side panel has a "Download" link | The link is labelled **Download Sample File** (within a "Download a sample csv file" block) | INT Import panel capture |
