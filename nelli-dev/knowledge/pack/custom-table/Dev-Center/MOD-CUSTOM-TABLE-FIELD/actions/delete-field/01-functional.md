# Delete Field — Functional

> **Screenshot banner (2026-10-08).** Delete happens on the Manage Fields grid (previously captured):
>
>
>

## 1. What it is

Deleting a field permanently removes a column from a custom table. The field definition, any data stored in that column across all rows, and the physical database column are all destroyed. This cannot be undone.

## 2. Where you do it

- **Admin:** Dev Center > Custom Tables > select a table > Field List. Each field row has a delete icon.
- **API:** Send a DELETE request to the custom-table-fields endpoint with the field code and table key.
- **Not available** in the webstore, Commerce Portal or B Store.

## 3. Who can do it

Any admin user who can access the Custom Tables area can delete a field. There is no separate role restriction for deletion.

For the API, standard API authentication is required. No role-specific permission is checked.

## 4. Step by step

**In the admin:**

1. Open the field list for the table (Dev Center > Custom Tables > select table).
2. Click the delete icon on the field row you want to remove.
3. If the field is marked as unique, a message appears and the delete is blocked — see "What is allowed" below.
4. If the field is not unique, the deletion happens immediately. A success message appears, and the page refreshes to show the updated field list.

There is no confirmation dialog. Clicking delete acts immediately.

**Via the API:**

1. Send a DELETE request with the field code and table key in the URL path.
2. On success, the response indicates the field was deleted.
3. On failure, the response includes the error reason.

## 5. What is allowed and what is not

- A field marked as unique **cannot** be deleted. To delete it, you must first change it so it is no longer unique (via the edit field action), then delete it.
- A field **can** be deleted even when the table contains data rows. All data in that column is permanently lost without warning.
- Bulk delete is not available. Fields must be deleted one at a time.
- Only one field can be deleted per API call.
- A deleted field's code can be reused when creating a new field.

## 6. Messages you may see

| Message | When it appears | When it does not appear |
|---|---|---|
| "The field set as unique cannot be deleted." | You try to delete a field that is marked as unique (admin screen). | The field is not unique. |
| Record deleted successfully | The field is deleted successfully (admin screen). | The delete fails. |
| Error deleting field (unsaved changes) | The API returns an error or the field was not found (admin screen). | The delete succeeds. |
| "A unique field cannot be changed as data associated with the table." | API receives a delete request for the unique field. | The field is not unique. |
| "Key not found" | API receives a table key that does not match any table. | The table key is valid. |
| "Id can not be less than one" | API receives both field code and table key as empty. | At least one parameter has a value. |

## 7. How it differs

There are no differences by role, user type, account, country or product type. The behaviour is the same for all admin users and all API callers.

The only behavioural branch is whether the field is marked as unique:
- **Unique field:** Delete is blocked on both the admin screen (client-side check) and the API (server-side check).
- **Non-unique field:** Delete proceeds immediately.

## 8. What can be combined

Not applicable. Deleting a field is a standalone action with no stacking or combination rules.

## 9. What it changes elsewhere

- **Data loss:** All values stored in the deleted column across all data rows are permanently removed. There is no warning about data loss.
- **Last field:** If the deleted field was the last remaining field of the table, all data rows are cleared (truncated). The table structure remains with only its auto-generated identifier column.
- **Import templates:** If an import template references the deleted field, it will fail on next use. No check is performed during deletion.
- **No audit trail:** No log entry records the deletion.
- **No undo:** The deletion is permanent. The field record is removed and the database column is dropped.
- **Not transactional:** The field record is removed first, then the database column is dropped. If the column drop fails, the field record is already gone but the column remains — an inconsistent state with no automatic recovery.

## 10. Quick answers

**Q1. Who can delete a field?**
Any admin user with access to Custom Tables. No special role is required.

**Q2. Can fields be deleted from surfaces other than admin and API?**
No. Only the admin and API support field deletion.

**Q3. What must exist before a field can be deleted?**
The field must exist (identified by its field code and table key).

**Q4. What are the steps to delete a field on the admin screen?**
Click the delete icon on the field row. If the field is not unique, the delete happens immediately — no confirmation dialog.

**Q5. Is there a confirmation dialog?**
No. The delete is immediate upon clicking the icon.

**Q6. Is bulk delete available?**
No. Fields are deleted one at a time.

**Q7. What happens after deletion?**
A success message appears, then the page redirects to the updated field list after one second.

**Q8. Is the deletion immediate or does it require Save?**
Immediate. No Save or Save & Close step is needed.

**Q9. Which API endpoint deletes a field?**
DELETE v1/custom-table-fields/{fieldCode}/{tableKey}.

**Q10. What parameters does the API accept?**
Two path parameters: fieldCode (alphanumeric, starts with a letter, max 100 characters) and tableKey (required).

**Q11. What does the API return on success?**
200 with IsSuccess true.

**Q12. What does the API return when the field does not exist?**
200 with IsSuccess false. No 404.

**Q13. What does the API return when the table does not exist?**
404 with "Key not found".

**Q14. What status codes can the API return?**
200 (success or field not found), 404 (table not found or unique field), 500 (unhandled error).

**Q15. Can multiple fields be deleted in one API call?**
No. One field per call.

**Q16. What authentication does the API require?**
Standard API gateway token. No role-specific check.

**Q17. Which API does the admin call internally?**
DELETE v1/custom-table-fields/{fieldCode}/{tableKey}, called via the admin agent.

**Q18. How does the admin handle an API error?**
It shows a generic error notification. The specific API error message is not displayed.

**Q19. Can a field be deleted when the table has data rows?**
Yes. No restrictions. Data in the deleted column is permanently lost.

**Q20. Is there a warning about data loss?**
No.

**Q21. Can the unique field be deleted?**
No. It is blocked on both the admin screen and the API. First change the field to non-unique, then delete.

**Q22. What happens if the unique field is deleted?**
The delete is refused. The unique constraint is not removed.

**Q23. Can the last remaining field be deleted?**
Yes. The table is truncated (all data rows removed), but the table structure remains.

**Q24. What happens if a field is referenced by an import template?**
No check is performed. The template will fail on next use.

**Q25. Can a deletion be undone?**
No. It is a permanent (hard) delete.

**Q26. Which stored procedure deletes a field?**
None. The deletion uses Entity Framework and raw SQL (ALTER TABLE DROP COLUMN).

**Q27. Is the deletion transactional?**
No. The field record is deleted first, then the column is dropped. A failure in the column drop leaves the metadata deleted but the column still present.

**Q28. Is there an audit trail?**
No.

**Q29. What if two admins delete the same field simultaneously?**
The first succeeds; the second finds the field gone and gets a false/failure response.

**Q30. What if a field is deleted while an import is in progress?**
No check is performed. The import may fail.

**Q31. Can a deleted field's code be reused?**
Yes. After deletion, the code is available for a new field.

## 11. For developers

See `03-frontend-admin.md` (admin screen and call tree), `06-api.md` (API contract and curls), `07-functions.md` (back-end code line by line) and `08-database.md` (tables and SQL).

## Fields and options

Delete is driven from the **Action** column of the Manage Fields grid (`/CustomTable/CustomTableFieldList?tableKey={tableKey}`); there is no separate delete form:

| Control | Behaviour | Where it comes from |
|---|---|---|
| Delete icon (Action column) | removes the field row immediately — **no confirmation dialog** | per-row action on the grid |
| Edit icon (Action column) | opens the row for inline edit (see edit-field) | per-row action on the grid |

## Screenshot verification (2026-10-08)

Grid screen: `/CustomTable/CustomTableFieldList?tableKey={tableKey}` (path only; ids as `{tableKey}`).

| Screenshot | Shows | Result |
|---|---|---|
| `screenshots/01-admin-delete-field-no-confirm-dialog-removed-immediately.png` | Clicking the delete icon removes the field row immediately, with no confirmation dialog | ✅ Verified — previously captured; not re-captured this pass |
| `screenshots/02-admin-field-deleted-successfully-table-has-data.png` | "Record deleted successfully", grid refreshed, table still has data rows | ✅ Verified — previously captured; not re-captured this pass |
