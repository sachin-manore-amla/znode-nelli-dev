# Export records — Functional

> **Screenshots (2026-10-08).** Captures of exporting records (previously captured in an earlier pass).
>
>

## 1. What it is

Exporting records generates a CSV file containing all data rows from a custom table. The export runs in the background, and the file becomes available for download on the Export Screen.

## 2. Where you do it

- **Admin**: Dev Center > Custom Tables > open a table > Data tab > Export button. The exported file is downloaded from the Export Screen (Dev Center > Exports).
- **Webstore**: Not available.
- **Commerce Portal**: Not available.
- **B Store**: Not available.
- **API**: Two endpoints — one to initiate the export and one to download the file.

## 3. Who can do it

Any admin user who can access the Dev Center > Custom Tables menu can export records. There is no separate permission for exporting. API consumers need a valid Znode API authentication token.

## 4. Step by step

1. Navigate to Dev Center > Custom Tables > open a table > Data tab.
2. Click the Export button.
3. The system first checks whether the table has any records.
4. If the table has no records, an error appears: "No Data Available to Export." The export stops.
5. If records exist, a "please wait" message appears.
6. The export starts in the background.
7. A success message appears: "Export has been initiated. Click here or redirect to the Exports screen to view more details." (confirmed live, int, 2026-10-05, verbatim - see `screenshots/01-admin-export-initiated-message.png`)
8. Navigate to the Export Screen (System Settings > Exports) to check the status.
9. The export entry shows "In Progress" while generating, then "Completed" when done, or "Failed" if an error occurred. Confirmed live: the export completed almost immediately for a 1-row table, listed with ID, Export Type ("CustomTable"), File Type (CSV), Status, Start Date and End Date. See `screenshots/02-admin-exports-screen-completed.png`.
10. Click Download to get the zip file containing the CSV.

## 5. What is allowed and what is not

- The export always includes all records and all columns from the table. There is no option to filter or select specific columns for export.
- The only supported file format is CSV. There is no option for Excel or other formats.
- The CSV is packaged into a zip file before it is stored.
- The export runs in a background task (not a queued job framework like Hangfire — it uses a simple background thread).
- The file is stored either on the server's local file system or in Azure Blob Storage, depending on a global setting.
- Temporary files are cleaned up after the zip is created and uploaded.
- Multiple exports of the same table can run concurrently (no blocking or deduplication).

## 6. Messages you may see

| Message | When it appears | When it does not |
|---|---|---|
| "No Data Available to Export." | The table has no records (checked before initiating) | The table has records |
| "Export has been initiated. Click here or redirect to the Exports screen to view more details." | Export started successfully | Pre-check found no records or an error occurred |
| "No Data To Export the Custom Table." | API-level: table has no records | Table has records |
| "In Progress" / "Completed" / "Failed" | Export Screen status column | — |

## 7. How it differs

- The export response returns immediately before the background task finishes. The message and error status in the response may still be default values because they are set inside the background task.
- The Export Type shown on the Export Screen is "Custom Table" and the File Type is "CSV".
- The generated file name follows the pattern `{tableName}{random number}.zip`.

## 8. What can be combined

Not applicable.

## 9. What it changes elsewhere

- A progress log entry is created in the export progress log table when the background task starts and is updated to "Completed" or "Failed" when it finishes.
- Temporary CSV and zip files are created and then cleaned up.
- No changes are made to the custom table's data or definition.

## 10. Quick answers

**Q: Can I export only specific records or columns?**
No. The export always dumps all records and all columns.

**Q: What format is the exported file?**
CSV, packaged in a zip file.

**Q: Where is the exported file stored?**
Either on the server's local file system or in Azure Blob Storage, controlled by the StorageType global setting.

**Q: How do I know when the export is done?**
Check the Export Screen (Dev Center > Exports). The status changes from "In Progress" to "Completed".

**Q: What happens when the table has no records?**
The admin shows "No Data Available to Export." and does not initiate the export.

**Q: Can I export a table with 100,000+ records?**
Yes, but the background task runs `SELECT * FROM {tableName}` to fetch everything, so very large tables may take significant time and memory.

**Q: Can the exported file be downloaded more than once?**
Yes. The file persists in storage until manually deleted from the Export Screen.

**Q: What happens when the background job fails?**
The export status on the Export Screen shows "Failed".

**Q: Is there a Hangfire job for the export?**
No. The export uses `Task.Run` (a simple background thread), not a persistent job queue.

**Q: What is the API endpoint to start an export?**
GET `v1/custom-table-data/{tableKey}/export`. It returns immediately with a response, and the background task runs asynchronously.

**Q: What is the API endpoint to download the file?**
GET `v1/custom-table-data/{tableName}/download`. The `tableName` is the generated export name, not the original table key.

## 11. For developers

See `03-frontend-admin.md` for the admin flow and JS call tree; `06-api.md` for both API endpoints with curls; `07-functions.md` for the background task logic; `08-database.md` for the SQL queries and progress logging.

## Fields and options

Export controls and the Exports screen:

| Element | What it does / shows | Rules |
|---|---|---|
| Export button (Data tab) | Starts the CSV export after a record pre-check | Blocked with "No Data Available to Export." when the table is empty |
| Initiated message | "Export has been initiated. Click here or redirect to the Exports screen to view more details." | Shown when the background export starts |
| Exports screen row | ID, Export Type ("CustomTable"), File Type (CSV), Status, Start Date, End Date | Status goes In Progress → Completed (or Failed) |
| Download | Downloads the zip containing the CSV | Available once Status is Completed |

## Screenshot verification (2026-10-08)

| Screenshot | Shows | Result |
|---|---|---|
| 01-admin-export-initiated-message.png | The "Export has been initiated…" confirmation after clicking Export | ✅ Verified (previously captured) |
| 02-admin-exports-screen-completed.png | The Exports screen row listing the completed CustomTable/CSV export | ✅ Verified (previously captured) |

Path-only URL: `/CustomTable/GetCustomTableDataList?tableKey={tableKey}` (the Data tab grid where Export is started; ids shown as {placeholders}).
