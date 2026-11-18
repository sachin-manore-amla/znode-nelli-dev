# Edit record — Functional

> **Screenshots (2026-10-08).** Captures of editing a record (previously captured in an earlier pass).
>
>
>

## 1. What it is

Editing a record updates the values of an existing data row in a custom table. You change field values on the form and save. The record is updated in place — the same row id is kept.

## 2. Where you do it

- **Admin**: Dev Center > Custom Tables > open a table > Data tab > click a row (or edit icon).
- **Webstore**: Not available.
- **Commerce Portal**: Not available.
- **B Store**: Not available.
- **API**: Records can be updated directly through two API endpoints — a single-row update and a bulk update (upsert on the unique field).

## 3. Who can do it

Any admin user who can access the Dev Center > Custom Tables menu can edit records. There is no separate permission for editing. API consumers need a valid Znode API authentication token.

## 4. Step by step

1. Navigate to Dev Center > Custom Tables > open a table > Data tab.
2. Click a row in the grid (or its edit icon).
3. The edit form loads with all fields pre-populated with the record's current values.
4. Change any field values. All fields are editable, including the unique field.
5. Click Save.
6. **Corrected (int, 2026-10-05, confirmed live):** on success, you do **not** stay on the same edit
 form - the admin redirects back to the table's record grid, showing "Record saved successfully."
 as a banner there. See `screenshots/03-admin-record-saved-redirects-to-grid.png`. (Section 7
 below, which said "you stay on the same form" for edit vs. "redirected to the edit form" for add,
 has the direction backwards for edit - both add and edit end up redirecting away from the form
 that was just submitted, just to different destinations: add goes to the new record's own edit
 form, edit goes back to the grid.)
7. On error, you stay on the edit form with an error message - confirmed live for a length-exceeded
 error: "Input cannot exceed the maximum character limit of {max}." (see
 `screenshots/02-admin-length-exceeded-error.png`), which is a field-level inline message, not the
 generic "Failed to update record." banner - that generic message is reserved for errors the
 client can't catch itself (see §6).

## 5. What is allowed and what is not

- All field values are editable, including the unique field.
- The same field type rules apply as for adding a record: **corrected (confirmed live, int,
 2026-10-05, via add-record):** Number fields on the admin form do NOT block negative values or
 decimals - both are accepted as long as they fit precision/scale, same as the API. Boolean is a
 "YES"/"NO" dropdown; Text and TextArea are free text; DateTime has a date picker. See
 `../add-record/01-functional.md` and `../add-record/screenshots/01-admin-negative-decimal-number-accepted.png`.
- If you change a unique field's value to one that already exists in another record, the save fails.
- Only the fields included in the request are updated. Fields not sent are not changed. However, the admin form always sends all fields.
- If the row id does not exist (deleted by another user), the update fails with a "Model cannot be null." error.

## 6. Messages you may see

| Message | When it appears | When it does not |
|---|---|---|
| "Record saved successfully." | The record was updated without error | Any error occurred |
| "Failed to update record." | Any error at all — including unique constraint violations, missing fields, SQL errors, or a null response | The record was saved |

**Important difference from adding a record**: When editing, there is no friendly message for a unique constraint violation. The admin always shows the generic "Failed to update record." message, unlike the add form which shows a specific unique key message.

## 7. How it differs

- The edit form shares the same view as the add form, but fields are pre-populated with existing values.
- **Corrected (confirmed live, int, 2026-10-05):** after a successful save on edit, the admin
 redirects to the table's record grid (not staying on the same form as previously documented).
 After a successful add, you are redirected to the new record's own edit form instead.
- The edit form uses PUT (update) instead of POST (create) when calling the API.
- Updating a record does NOT update the table's "Modified Date" in the table definition. This is different from adding a record, which does update it.
- **Corrected (confirmed live):** there is no admin-vs-API difference for Number validation - both
 accept negatives and decimals within precision/scale.

## 8. What can be combined

Bulk update (upsert) is available through the API. It requires the table to have a unique field. Rows are matched by the unique field's value: matching rows are updated, non-matching rows are inserted. If the table has no unique field, bulk update returns an error.

## 9. What it changes elsewhere

- An "Updated" event is dispatched for the record after a successful single-row update.
- If the table key is "ProductInformationOverrides", product override status is updated.
- The table's "Modified Date" is NOT updated on edit (unlike add).
- Bulk update does not dispatch events per row.

## 10. Quick answers

**Q: What is the API endpoint to update a record?**
PUT to `/api/v1/custom-table-data` with the row Id, table key, table id, and an array of field code / value pairs.

**Q: Is partial update supported?**
Yes — only the fields included in the request body are updated. Fields not sent keep their existing values.

**Q: Can I change the unique field value?**
Yes, as long as the new value does not already exist in another record.

**Q: What happens when editing a record that was deleted by another user?**
The update affects zero rows and the API returns an error: "Model cannot be null."

**Q: What happens on concurrent edits by two users?**
Last write wins. There is no optimistic concurrency check.

**Q: Does editing set a ModifiedDate?**
No. The table contains only custom-defined fields and the auto-increment Id. No audit columns are updated. The table definition's Modified Date is also not updated on edit.

**Q: What is the bulk update endpoint?**
PUT to `/api/v1/custom-table-data/{tableKey}/bulk-update` with a JSON array. The table must have a unique field. Existing rows (matched by unique value) are updated; unmatched rows are inserted.

**Q: What error appears when bulk-updating a table with no unique field?**
"Table does not have unique column."

**Q: What status code does a successful update return?**
201 Created.

**Q: What is the response when the row id does not exist?**
400 with error message "Model cannot be null." (because UPDATE affected 0 rows).

## 11. For developers

See `03-frontend-admin.md` for the admin form, call tree and difference from the add form; `06-api.md` for the update and bulk update endpoints with curls and data maps; `07-functions.md` for the service logic and validation; `08-database.md` for the UPDATE SQL and table writes.

## Fields and options

The Edit Record form (heading "Edit Record {tableKey}") renders one labelled control per field, pre-populated with the current values (verified live on INT for `testabhi`, fields name / Number / Address):

| Field / control | On the form | Rules |
|---|---|---|
| Custom fields (name, Number, Address) | One labelled text input each, pre-filled with the record's current values | All editable, including the unique field |
| Unique field (name) | Text input marked required (`*`) | Must stay non-empty and distinct; duplicate save fails |
| Hidden fields | Id, TableKey, TableId (testabhi = 90) | Carried on the form, not user-editable |
| Save & Close | Submits the update (PUT) | On success redirects to the record grid with "Record saved successfully." |
| Back | Returns to the grid without saving | — |

## Screenshot verification (2026-10-08)

| Screenshot | Shows | Result |
|---|---|---|
| 01-admin-edit-record-form.png | The Edit Record form with the row's values pre-populated | ✅ Verified (previously captured) |
| 02-admin-length-exceeded-error.png | The inline "Input cannot exceed the maximum character limit of {max}." field error | ✅ Verified (previously captured) |
| 03-admin-record-saved-redirects-to-grid.png | The redirect back to the record grid showing "Record saved successfully." | ✅ Verified (previously captured) |

Path-only URL: `/CustomTable/EditCustomTableData?TableKey={tableKey}&Id={id}` (the edit form; ids shown as {placeholders}).
