# Import Records — Functional

> **Screenshots (2026-10-08).** Captures of importing records (previously captured in an earlier pass).
>
>

## 1. What it is

Import lets you add records to a custom table by uploading a CSV file. The system reads the file, converts it, and sends the data to a background process that inserts new rows or updates existing ones if the table has a unique field.

## 2. Where you do it

In the **admin**, navigate to **Dev Center > Custom Tables**, select a table, open its record grid, and click the **Import** button. A side panel opens where you select the CSV file and click Import.

Not available in the webstore, Commerce Portal, or B Store app.

## 3. Who can do it

Any admin user who can access the Custom Tables section in Dev Center can import records.

## 4. Step by step

1. Open the custom table's record grid in the admin.
2. Click **Import**. A side panel opens (confirmed live, int, 2026-10-05 - see
 `screenshots/01-admin-import-panel.png`): "IMPORT TABLE DATA" with a "Download a sample csv
 file" box, a "Download Sample File" link, and a "Select a .csv file" Browse control.
3. Optionally, click **Download** to get the CSV template (see csv-template action).
4. Select a `.csv` file using the file upload control.
5. Click **Import**.
6. The system validates the file (must be `.csv`, filename not too long, must contain data).
7. The file is uploaded, converted to an intermediate format, and sent to the server.
8. A background process runs the import.
9. A notification appears: either a success message with a link to view import logs, or an error message.
10. The page redirects back to the table after a short delay.

## 5. What is allowed and what is not

- Only `.csv` files are accepted. Other file types are rejected with an error.
- The filename (without extension) must not exceed 200 characters.
- The CSV must contain at least one data row (beyond the header). An empty CSV is rejected.
- The CSV header row must use Field Codes (not Field Names) as column headers.
- The delimiter is auto-detected (comma, semicolon, or tab).
- Malformed data in the CSV is silently ignored.
- There is no explicit file size or row count limit in the code.
- There is no preview step; import starts immediately after clicking Import.
- Insert vs. upsert behavior is handled by the background process: if the table has a unique field, existing records matched by that field are updated; otherwise, records are inserted.
- There is no toggle on the admin screen to choose between insert and upsert.

## 6. Messages you may see

| Message | When it appears | When it does not |
|---|---|---|
| Wrong file type error | A non-CSV file is selected | A .csv file is selected |
| "File not present." (confirmed live, int, 2026-10-05) | Import clicked with no file selected | A file is selected. See `screenshots/02-admin-no-file-selected-error.png` |
| Filename too long error | Filename exceeds 200 characters | Filename is within limit |
| "No data found in the CSV file." | CSV has no data rows | CSV has at least one data row |
| Empty CSV message | JSON conversion results in zero rows | Data rows exist |
| Import initiated + link to logs | Import starts successfully | Import fails |
| Import failed + link to logs | The background process reports failure | Import succeeds |
| "Import process failed. Please check the database logs..." | API-level failure | API returns success |

## 7. How it differs

- The CSV is converted to JSON on the admin server before being sent to the API. The API's stored procedure reads from the file in blob storage.
- A SQL timeout during the stored procedure is treated as success (the import is assumed to still be running in the background).
- The background process handles all row-level validation, duplicate detection on the unique field, and error logging internally.
- The API returns only success or failure (no count of imported rows, no per-row error details at the API level).

## 8. What can be combined

Only one custom table import process can run at a time (per the knowledge base). The lock applies globally, not per table.

## 9. What it changes elsewhere

- New records appear in the custom table's record grid after import.
- If upserting, existing records matched by the unique field are updated with new values.
- Import activity may be logged in the application logs.
- The import status can be viewed in the Import Logs area.

## 10. Quick answers

| Question | Answer |
|---|---|
| Can I import an Excel file? | No, only CSV files are accepted. |
| Does the CSV need a header row? | Yes, with Field Codes as column headers. |
| Is there a row limit? | No explicit limit in the code. |
| What delimiter should I use? | The system auto-detects comma, semicolon, or tab. |
| Does import update existing records? | Yes, if the table has a unique field, matching records are updated (upsert). |
| Can I choose insert-only vs. upsert? | No, the behavior is determined automatically by the stored procedure. |
| Where do I see import errors? | In the import logs, linked from the notification message. |
| What happens if the CSV has extra columns? | Handled by the stored procedure; columns not matching a field are likely ignored. |
| What if a value fails validation? | Row-level errors are logged by the stored procedure. |
| Is there a progress indicator? | No. You see a notification when import starts and can check the logs. |

## 11. For developers

See `03-frontend-admin.md` for the admin screen and call tree, `06-api.md` for the API endpoint, `07-functions.md` for every method line by line, and `08-database.md` for the stored procedure.

## Fields and options

The Import side panel ("IMPORT TABLE DATA"), verified live on INT (`/CustomTable/GetCustomTableTemplate?tablekey={tableKey}`):

| Control | What it does | Rules |
|---|---|---|
| "Download a sample csv file" / Download Sample File link | Downloads the CSV template of the table's field codes | See the csv-template action |
| "Select a .csv file" Browse / Choose File | Picks the CSV to upload | Only `.csv` accepted; filename (without extension) ≤ 200 chars |
| Import button | Uploads and starts the background import | Rejected with "File not present." when no file is selected; CSV must have ≥1 data row |

## Screenshot verification (2026-10-08)

| Screenshot | Shows | Result |
|---|---|---|
| 01-admin-import-panel.png | The Import side panel with Download Sample File and the .csv Browse control | ✅ Verified (previously captured) |
| 02-admin-no-file-selected-error.png | The "File not present." error after clicking Import with no file selected | ✅ Verified (previously captured) |

Path-only URL: `/CustomTable/GetCustomTableTemplate?tablekey={tableKey}` (the Import side panel; ids shown as {placeholders}).
