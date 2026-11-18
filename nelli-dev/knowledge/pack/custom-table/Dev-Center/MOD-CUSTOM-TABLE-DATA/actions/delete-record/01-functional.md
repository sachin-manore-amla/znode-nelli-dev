# Delete record — Functional

> **Screenshots (2026-10-08).** Captures of deleting a record (previously captured in an earlier pass).
>
>

## 1. What it is

Deleting a record permanently removes one or more data rows from a custom table. This is a hard delete — the row is physically removed from the database and cannot be recovered through the application.

## 2. Where you do it

- **Admin**: Dev Center > Custom Tables > open a table > Data tab > delete icon on a row (single) or select rows with checkboxes and click the toolbar Delete button (bulk).
- **Webstore**: Not available.
- **Commerce Portal**: Not available.
- **B Store**: Not available.
- **API**: Four delete endpoints exist — delete by row id, delete by multiple row ids, delete by unique column value, and delete by filter condition.

## 3. Who can do it

Any admin user who can access the Dev Center > Custom Tables menu can delete records. There is no separate permission for deleting. API consumers need a valid Znode API authentication token.

## 4. Step by step

### Single delete (admin)

1. Navigate to Dev Center > Custom Tables > open a table > Data tab.
2. Click the delete icon on a row.
3. A confirmation dialog appears (standard grid delete confirmation).
4. Confirm the deletion.
5. On success, the message "Record deleted successfully." appears and the grid refreshes.
6. On failure, an error message appears.

### Bulk delete (admin)

1. Select rows using the checkboxes in the grid.
2. Click the Delete button in the toolbar.
3. No confirmation dialog is shown — the delete happens immediately.
4. On success, a notification appears and the page redirects to the table view after one second.
5. On failure, an error notification appears.
6. If no rows are selected, clicking the Delete button does nothing.

## 5. What is allowed and what is not

- Any visible record can be deleted. There is no protection against deleting specific records.
- Bulk delete sends all selected row ids in one request. If some ids exist and some do not, the existing ones are deleted and the missing ones are ignored (partial delete). There is no rollback.
- Deleting by unique column value requires the table to have a unique field. The column name in the request must match the table's unique constraint column.
- Deleting by filter condition supports all standard Znode filter operators. If the filter matches all rows, all rows are deleted. There is no safety limit.
- Each single-row delete through the standard endpoint dispatches a "Deleted" event. Bulk delete by ids, delete by unique value, and delete by filter condition do NOT dispatch events.

## 6. Messages you may see

| Message | When it appears | When it does not |
|---|---|---|
| "Record deleted successfully." | Single or bulk delete succeeded | Delete failed |
| "Unable to delete the selected account(s). Please remove any child relationship of the selected account(s)." | Delete failed (any reason — API returned failure, network error, exception). This is a generic message not specific to custom tables. | Delete succeeded |
| "Failed to delete the record." | The table key was empty or the row id was invalid (guard check failed) | Valid parameters were provided |
| "The requested table does not exist" | The table key does not match any table (API-level) | The table key is valid |
| "No records were found for the requested row id." | The row id does not exist in the table (API-level) | The row exists |
| "Id cannot be less than 1." | The row id is negative (API-level) | The row id is positive |
| "Table not found" | Delete by unique value: table does not exist in the database schema | Table exists |
| "Table does not have unique column." | Delete by unique value: the column name does not match the table's unique constraint, or the table has no unique field | Column matches |

## 7. How it differs

- Single delete dispatches a "Deleted" event; bulk delete does not.
- Bulk delete by ids is a partial operation — some rows may be deleted while others are not, with no rollback.
- Delete by unique column value checks the column against the table's unique constraint. If the column does not match, it returns an error rather than silently deleting nothing.
- Delete by filter condition can delete many rows at once based on conditions. There is no upper limit.
- The admin failure message ("Unable to delete the selected account(s)...") is a generic message borrowed from account deletion — it is not specific to custom tables.

## 8. What can be combined

Not applicable.

## 9. What it changes elsewhere

- The record is permanently removed from the database.
- A "Deleted" event is dispatched for single-row deletes only, which may trigger downstream listeners.
- The table definition's "Modified Date" is NOT updated when records are deleted.
- No audit log entry is created for the deletion.

## 10. Quick answers

**Q: Is there a confirmation before deleting?**
For single delete from the grid: yes, a standard grid confirmation dialog. For bulk delete from the toolbar: no confirmation — it deletes immediately.

**Q: Can deleted records be recovered?**
No. This is a physical delete. The rows are removed from the database.

**Q: What happens when deleting a record that was already deleted?**
The API returns a 404 error with "No records were found for the requested row id."

**Q: What happens with bulk delete when some ids do not exist?**
The existing rows are deleted and the response reports partial success. The API returns `{IsSuccess: false}` because not all requested ids were deleted.

**Q: Is there a maximum number of records that can be bulk-deleted?**
No hard limit is enforced. All ids are processed one at a time.

**Q: What happens when deleting by filter with an empty filter?**
The behaviour is unpredictable — the filter-to-SQL conversion may produce an empty WHERE clause, potentially deleting all rows, or it may throw an error.

**Q: Are there any stored procedures for delete?**

**Q: Is there a transaction wrapping the delete?**
No explicit transaction. Each delete statement runs as its own implicit transaction. In bulk, if the process fails mid-way, already-deleted rows remain deleted.

## 11. For developers

See `03-frontend-admin.md` for the admin call trees (single and bulk); `06-api.md` for all four delete endpoints with curls and data maps; `07-functions.md` for the service and repository logic; `08-database.md` for the SQL and event dispatch details.

## Fields and options

Delete controls on the record grid:

| Control | What it does | Rules |
|---|---|---|
| Delete (trash) icon on a row | Single delete; opens a confirmation dialog (`#PopUpConfirm`) before removing the row | Must be confirmed; dispatches a "Deleted" event |
| Row checkboxes + toolbar Delete | Bulk delete of the selected rows | No confirmation dialog; immediate; no event dispatched |
| Confirmation dialog | Confirms/cancels a single delete | Confirm removes the row and refreshes the grid; cancel keeps it |

## Screenshot verification (2026-10-08)

| Screenshot | Shows | Result |
|---|---|---|
| 01-admin-delete-confirm-dialog.png | The confirmation dialog shown before a single-row delete | ✅ Verified (previously captured) |
| 02-admin-record-deleted-grid-empty.png | The record grid after the row was deleted | ✅ Verified (previously captured) |

Path-only URL: `/CustomTable/GetCustomTableDataList?tableKey={tableKey}` (the record grid where the delete action and confirmation appear; ids shown as {placeholders}).
