# Delete a custom table

> **Screenshots for this action (previously captured in an earlier pass; corroborated by INT facts 2026-10-08, admin store Amla, v10.14.4.0):**
>
>
>

> **Corrected (int, 2026-10-05, confirmed live both ways):** this file previously said the
> typed-keyword "Delete" confirmation dialog **always** appears in the admin, regardless of data.
> **Wrong - which dialog appears depends on whether the table has data:**
>
> - **Empty table** (`kbprobeDeleteMe`, no fields, no data): clicking the row Delete icon shows the
> **simple** dialog - title "CONFIRM DELETE?", body "Are you sure you want to delete the selected
> record(s)?", only **Back** and **OK** buttons, no text box. Clicking OK deletes it immediately.
> See `screenshots/01-admin-delete-confirm-dialog.png` and
> `screenshots/02-admin-delete-success-message.png`.
> - **Table with one data row** (`kbprobeDeleteWithData`, one Text field, one record): clicking the
> row Delete icon shows the **typed-keyword** dialog described below - "The selected table(s) may
> have data associated with it..." with the "Delete" text box. Typing "Delete" and clicking OK
> deletes it. See `screenshots/03-admin-delete-confirm-typed-keyword-with-data.png`.
>
> So the hover-check mentioned in step 2 below does decide which dialog variant is shown - it is not
> cosmetic. The warning text in the typed-keyword dialog is accurate as written; it just does not
> appear unconditionally as this file previously said.

## 1. What it is

Deleting a custom table permanently removes the table, all its field definitions, and all its data rows. The table is gone from the system — there is no soft delete or recycle bin. Both a single table and multiple tables at once can be deleted.

## 2. Where you do it

- **Admin**: Dev Center > Custom Tables (list page). Delete one table from the action column, or select several with checkboxes and click the toolbar Delete button.
- **API**: `DELETE /v1/custom-tables/{tableKeys}` for one or more (comma-separated), or `POST /v1/custom-tables/bulk-delete` with a list of table keys in the body.
- **Webstore / Commerce Portal / B Store**: Not available. Custom tables are managed only in the admin and via API.

## 3. Who can do it

| Role / context | Can delete? | Notes |
|---|---|---|
| Admin user with `DeleteBulkCustomTableRecord` permission | Yes | The delete icon and toolbar button are visible only if the role has this action |
| Admin user without the permission | No | The delete controls are not shown |
| API caller | Yes | No additional permission check beyond API authentication |

## 4. Step by step

### In the admin (single table)

1. Go to Dev Center > Custom Tables.
2. Hover over the delete icon on the row. The system checks in the background whether the table has any data rows (this check runs once per hover) and decides which confirmation dialog to show next.
3. Click the delete icon.
4. **If the table has no data rows** (confirmed live): a simple dialog appears - "CONFIRM DELETE? Are you sure you want to delete the selected record(s)?" - with only Back and OK, no text box.
5. **If the table has at least one data row** (confirmed live): the dialog says *"The selected table(s) may have data associated with it. Proceeding with this action will delete the table and its associated data (if any). To confirm the deletion, please type 'Delete' in the text box below:"* with a text box to type into.
6. Confirm - click OK (empty table), or type **Delete** (upper or lower case does not matter) and click OK (table with data).
7. The table, its fields, and all its data are permanently deleted.
8. You see the message *"Record deleted successfully."* and the list reloads.

### In the admin (multiple tables)

1. Go to Dev Center > Custom Tables.
2. Select the checkboxes next to the tables you want to delete. You can use the header checkbox to select all visible rows.
3. Click the Delete button in the toolbar.
4. If no rows are selected, you see a message asking you to select at least one.
5. The same confirmation dialog appears. Type **Delete** and click OK.
6. All selected tables are sent for deletion in one request.
7. You see *"Record deleted successfully."* if at least one table was deleted. The list reloads; successfully deleted tables are gone.

### Via API

Send a `DELETE /v1/custom-tables/{tableKey}` request with the table key in the URL, or a `POST /v1/custom-tables/bulk-delete` request with a list of table keys in the body. No typed-keyword confirmation is needed — the API deletes immediately.

## 5. What is allowed and what is not

- **System-defined tables cannot be deleted.** The only system-defined table is "Product Information Overrides". Attempting to delete it returns an error: *"Deleting System Tables is not allowed."*
- **Tables that hold data can still be deleted.** The warning in the admin dialog is informational only — it does not prevent deletion. The API does not check for data rows at all before deleting.
- **There is no undo.** Once confirmed, the table, its fields, and all its rows are permanently destroyed.
- **Duplicate keys in a bulk request are deduplicated.** The system treats "MyTable" and "mytable" as the same key.
- **There is no limit on how many tables can be deleted at once** in a bulk request.

## 6. Messages you may see

| Message | When it appears | When it does not appear |
|---|---|---|
| "CONFIRM DELETE?" / "Are you sure you want to delete the selected record(s)?" | Table has **no data rows** (confirmed live) | Table has data, or API |
| "The selected table(s) may have data associated with it. Proceeding with this action will delete the table and its associated data (if any). To confirm the deletion, please type 'Delete' in the text box below:" | Table has **at least one data row** (confirmed live) | Table is empty, or API |
| "Invalid keyword entered, please try again." | You type the wrong word in the confirmation box (admin, data-present dialog) | You type "Delete" correctly, or leave it empty |
| "Record deleted successfully." | At least one table was deleted (admin) | All tables failed to delete |
| "Failed to delete the record." | All tables failed to delete (admin) | At least one succeeded |
| "Custom table deleted successfully." | Per-key success message (API bulk response) | The key failed |
| "The requested table does not exist" | The table key does not match any existing non-system table | The key exists |
| "Deleting System Tables is not allowed" | The key matches a system-defined table | The key is not system-defined |
| "Failed to delete custom table." | An unexpected error occurred during deletion (API bulk per-key) | Deletion succeeded or a more specific error applies |
| "TableKey can not be null or empty." | The request body has no keys or a blank key (API bulk) | Valid keys provided |
| "Id cannot be less than 1." | The table key is missing in the single-delete API call | A key is provided |
| "Table Key can only contain letters and numbers." | The key in the URL contains invalid characters (API single) | Valid key format |
| "Table Key cannot exceed 100 characters." | The key in the URL is longer than 100 characters (API single) | Key is 100 or fewer characters |

## 7. How it differs

### Admin versus API

| Aspect | Admin | API (single DELETE) | API (bulk POST) |
|---|---|---|---|
| Typed-keyword confirmation | Yes — must type "Delete" | No | No |
| Data-row warning | Shown in dialog (always, static text) | Not shown | Not shown |
| Endpoint used | Always bulk POST | DELETE with path param | POST with body |
| Response detail | Single success/failure message | Single boolean | Per-key success/failure |
| Partial success | Shown as "success" if any table deleted | N/A (batch all-or-nothing) | 207 Multi-Status with per-key detail |

### Single delete versus bulk delete (API)

| Aspect | Single DELETE | Bulk POST |
|---|---|---|
| System-defined check | Fails the whole request if any key is system-defined | Reports system-defined keys individually; deletes the rest |
| Not-found handling | Fails the whole request | Reports not-found keys individually; deletes the rest |
| Response | Boolean success/failure | Per-key results |

## 8. What can be combined

There are no combination or stacking rules for delete. Each table is independent.

## 9. What it changes elsewhere

- **All data rows in the table are destroyed.** The physical database table is dropped. Any data that was stored in the custom table is permanently lost.
- **All field definitions for the table are removed.** The columns that were configured for the table are deleted from the system.
- **Import and export history is not cleaned up.** If the table had been used for import or export, those history records remain.
- **No audit log entry is created.** The deletion is not recorded in any audit trail.
- **No event or notification is triggered.** Other parts of the system are not notified of the deletion.

## 10. Quick answers

**Q: Can I recover a deleted custom table?**
No. Deletion is permanent — the table, its fields, and all its data are destroyed. There is no undo, recycle bin, or soft delete.

**Q: What happens if the table has data rows?**
The table and all its data are deleted anyway. The admin shows a warning, but it does not prevent the action.

**Q: Can I delete a system table?**
No. The only system-defined table ("Product Information Overrides") is protected. The system returns "Deleting System Tables is not allowed."

**Q: Do I need to type "Delete" to confirm?**
Only in the admin, and only when the table has at least one data row (confirmed live). For an empty
table, a simple OK/Back dialog is shown instead - no typing required. The API never requires a
confirmation keyword.

**Q: What is the keyword? Is it case-sensitive?**
The keyword is "Delete". It is not case-sensitive — "delete", "DELETE", and "Delete" all work.

**Q: What if I select multiple tables and some cannot be deleted?**
In the admin, you see "Record deleted successfully" if at least one table was deleted — you are not told which ones failed. In the API bulk endpoint, the response lists each key with its own success or error status, and you get a 207 Multi-Status code.

**Q: Is there a limit on how many tables I can delete at once?**
No. The bulk endpoint accepts any number of table keys.

**Q: Does the admin check whether the table has data before I click delete?**
Yes — on hover, the admin checks if the table has data rows. **Confirmed live (int, 2026-10-05):
this result decides which confirmation dialog is shown** - a simple OK/Back dialog for an empty
table, or the typed-"Delete" keyword dialog for a table with data. It is not cosmetic.

**Q: What permission do I need to delete a custom table in the admin?**
Your role must have the `DeleteBulkCustomTableRecord` action for the `CustomTable` controller. Without it, the delete controls are not visible.

## 11. For developers

See `03-frontend-admin.md` for the admin screens, selectors, and JS logic. See `06-api.md` for the API endpoints, request/response formats, and curls. See `07-functions.md` for the back-end call tree, service methods line by line, and validation rules. See `08-database.md` for the tables affected and the deletion order.

---

## Screenshot verification (2026-10-08)

Screenshots were captured in an earlier pass and are not re-captured here; they are corroborated against the verified INT facts (admin store Amla, v10.14.4.0, 2026-10-08) where those facts cover the screen.

| Screenshot | Shows | Status |
|---|---|---|
| 01-admin-delete-confirm-dialog.png | Simple confirm dialog (OK / Back) for an empty table | ✅ Verified — per-row Delete opens a confirm popup on INT |
| 02-admin-delete-success-message.png | "Record deleted successfully." banner, row removed, count decremented | ⚠️ Not verifiable — a real delete was not performed in this read-only pass |
| 03-admin-delete-confirm-typed-keyword-with-data.png | Typed-keyword "Delete" confirm dialog for a table that holds data | ✅ Verified — the typed-keyword `#PopUpConfirm` variant exists on INT |

Path-only URL: `/CustomTable/List` (per-row Delete opens the `#PopUpConfirm` dialog; bulk Delete via the Tools dropdown)

## Fields and options

| Element | Type | Values / behaviour | Notes |
|---|---|---|---|
| Per-row Delete | action (Manage menu) | opens the confirm popup for that table | single table |
| Bulk Delete | Tools dropdown | deletes all checked rows | select rows via checkboxes |
| Confirmation keyword | text box (data-present dialog) | must equal "Delete" (case-insensitive, trimmed) | client-side check only; empty table shows a simple OK/Back dialog with no box |
| OK | button | confirms and deletes | permanent, no undo |
| Back / Cancel | button | dismisses, no change | |
