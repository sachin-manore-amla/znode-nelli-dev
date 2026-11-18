# Add record — Functional

> **Screenshots (2026-10-08).** Captures of adding a record (previously captured in an earlier pass).
>
>

> **New finding, added from live testing (int, 2026-10-05):** clicking "Add a Record" shows a
> proactive warning popup before the form appears: "A unique column cannot be added or changed once
> a row is added to the system. Do you still want to continue?" (title "NOTE", Back / OK buttons).
> **Confirmed live that this appears unconditionally** - it was triggered on `kbprobeDeleteWithData`,
> a table whose only field (`kbprobeDataField`) is **not** marked unique at all. The dialog's wording
> is misleading: it is not actually conditional on the table having a unique field. Clicking OK
> proceeds to the normal Add a Record form exactly as described below; clicking Back cancels. See
> `../../MOD-CUSTOM-TABLE-FIELD/actions/unique-field/screenshots/01-admin-add-record-unique-warning-dialog-non-unique-field.png`.

## 1. What it is

Adding a record inserts a new data row into a custom table. You fill in a value for each field defined on the table and save. The new record then appears in the record grid.

## 2. Where you do it

- **Admin**: Dev Center > Custom Tables > open a table > Data tab > "Add a Record" button.
- **Webstore**: Not available.
- **Commerce Portal**: Not available.
- **B Store**: Not available.
- **API**: Records can be inserted directly through three API endpoints — the standard form-style insert, a single JSON record insert, and a bulk JSON insert.

## 3. Who can do it

Any admin user who can access the Dev Center > Custom Tables menu can add records. There is no separate permission for adding records. API consumers need a valid Znode API authentication token.

## 4. Step by step

1. Navigate to Dev Center > Custom Tables > open a table > Data tab.
2. Click "Add a Record".
3. A proactive warning popup appears first (confirmed live, unconditionally - see the note at the
 top of this file): "A unique column cannot be added or changed once a row is added to the
 system. Do you still want to continue?" Click OK to proceed, or Back to cancel.
4. A form appears with one control per field, ordered by each field's Display Order.
5. Fill in the values:
 - Text fields appear as text inputs.
 - TextArea fields appear as multi-line text areas.
 - Number fields appear as plain text inputs. **Corrected (int, 2026-10-05, confirmed live):**
 they do **not** only accept non-negative whole numbers - a negative decimal (`-12.34`) was
 typed and saved successfully on a field with length `5,2`. The field is not marked required
 unless it is also the table's unique field. See
 `screenshots/02-admin-negative-decimal-typed-in-form.png` (the value accepted in the input,
 no rejection) and `screenshots/01-admin-negative-decimal-number-accepted.png` (the saved
 value in the grid after Save & Close).
 - Boolean fields appear as a dropdown with two choices: "NO" (the default) and "YES".
 - DateTime fields appear with a date picker.
6. Click Save.
7. On success, you are redirected to the edit form for the newly created record, and a message confirms the record was created.
8. On error, you stay on the create form with an error message.

## 5. What is allowed and what is not

- All fields defined on the table appear on the form.
- Text and TextArea values are optional. **Corrected (confirmed live):** a Number value is
 mandatory only when that field is the table's unique field - an ordinary (non-unique) Number
 field is optional, and the form does not restrict entry to non-negative whole numbers; negative
 numbers and decimals within the field's precision/scale are accepted.
- Boolean values default to "NO" (false) and can only be "YES" or "NO" on the admin form.
- DateTime values are optional on the form.
- If a field is marked as Unique, its value must not be empty. If the value already exists in another record, the save fails.
- Number values must fit within the precision and scale defined by the field's length setting (for example, "10,2" means up to 8 integer digits and 2 decimal places).
- Uniqueness is enforced at the database level when the record is inserted. The admin form does not check for duplicates before submitting.
- Values that exceed the database column's maximum length cause a database error.

## 6. Messages you may see

| Message | When it appears | When it does not |
|---|---|---|
| "NOTE" / "A unique column cannot be added or changed once a row is added to the system. Do you still want to continue?" | Clicking "Add a Record" - confirmed live to appear unconditionally, even when no field on the table is unique | Never observed to be skipped |
| "Record created successfully." | The record was saved without error | Any error occurred |
| "A record with this unique key already exists. Please ensure that the value entered for the unique key column is distinct." | A unique field's value already exists in another record | The unique value is new |
| "Failed to create." | Any other error (database error, missing data, etc.) | The record was saved or a unique key error was detected |
| "FieldValue is required for Unique Field: {field name}" | A unique field was left empty (API-level message) | The unique field has a value |
| "Input is required." | A numeric unique field was set to 0 (API-level) | The numeric unique field has a non-zero value |
| "The numeric value should fall within the range of ({precision},{scale})" | A number exceeds the field's configured precision and scale (API-level) | The number fits within range |
| "The requested table does not exist" | The table key does not match any table | The table key is valid |
| "Model cannot be null." | The table key is empty | A table key is provided |

## 7. How it differs

- The form shows different fields depending on which fields are defined on the table.
- **Corrected (confirmed live, int, 2026-10-05):** the admin form does **not** block negative values
 or decimals on Number fields - both are accepted on the admin form itself, the same as through the
 API, as long as the value fits the field's precision and scale. There is no difference between
 admin and API here.
- Text and TextArea length is not validated at the API level — it is only enforced by the database column constraint.
- Boolean values are restricted to "YES"/"NO" on the admin form but the API accepts any value.
- DateTime is converted on create but no strict format validation exists — an unparseable date causes a server error.

## 8. What can be combined

The standard insert, JSON single insert, and JSON bulk insert are three separate ways to add records. The standard insert is what the admin form uses. The JSON endpoints accept a different request format (a JSON array of objects with field names as keys).

Bulk insert can add many records at once. If some rows fail and others succeed, the response reports each row's result individually (partial success is possible).

## 9. What it changes elsewhere

- The table's "Modified Date" in the table definition is updated to the current time after a successful insert (single form-style insert only).
- A "Created" event is dispatched for the record (single form-style insert only).
- If the table key is "ProductInformationOverrides", product override status is updated.
- Bulk insert does not update the table's Modified Date or dispatch events per row.

## 10. Quick answers

**Q: What is the API endpoint to insert a record?**
POST to `/api/v1/custom-table-data` with the table key, table id, and an array of field code / value pairs.

**Q: Does the response include the new record's id?**
Yes — the response includes the id generated by the database.

**Q: Can I insert multiple records at once?**
Yes, using the bulk insert endpoint: POST to `/api/v1/custom-table-data/{tableKey}/bulk-insert` with a JSON array.

**Q: What happens if one record in a bulk insert fails?**
The successful rows are inserted and the failed rows are reported individually. A 207 Multi-Status response is returned for mixed results.

**Q: Is uniqueness checked before the insert or at insert time?**
At insert time, by the database constraint. The API only checks that the unique field is not empty.

**Q: Is the uniqueness check case-sensitive?**
It depends on the database collation (typically case-insensitive on SQL Server default collation).

**Q: What happens when inserting a record with a field code that does not exist on the table?**
The insert fails with a SQL error (500 Internal Server Error).

**Q: What happens when adding a record to a table with no fields?**
An insert with no columns is attempted, which may fail at the SQL level.

**Q: What happens on a concurrent insert of two records with the same unique value?**
One succeeds and the other fails with a SQL unique constraint error.

**Q: Does inserting a record set audit columns like CreatedDate?**
No. The table schema contains only the custom-defined fields and the auto-increment Id. No audit columns are added automatically.

**Q: Can I add a record with all fields empty?**
Only if no field is marked as unique and no field is a required Number type. Text, TextArea, DateTime, and Boolean can all be empty.

## 11. For developers

See `03-frontend-admin.md` for the admin form, controls and call tree; `06-api.md` for all three insert endpoints with curls and data maps; `07-functions.md` for the service logic, validation methods and workflow; `08-database.md` for the INSERT SQL and table writes.

## Fields and options

The Add a Record form renders one control per field defined on the table, ordered by Display Order:

| Field type | Control on the form | Rules |
|---|---|---|
| Text | Text input | Optional; length enforced by the database column |
| TextArea | Multi-line text area | Optional; `NVARCHAR(MAX)` column |
| Number | Text input | Optional unless it is the unique field; negatives and decimals accepted within the field's precision/scale (confirmed live on a `5,2` field) |
| Boolean | Dropdown "NO" (default) / "YES" | Only YES/NO possible on the admin form |
| DateTime | Date picker | Optional |
| Unique field | As per its type, marked required | Must be non-empty and distinct; duplicate rejected at save |

## Screenshot verification (2026-10-08)

| Screenshot | Shows | Result |
|---|---|---|
| 02-admin-negative-decimal-typed-in-form.png | A negative decimal (`-12.34`) typed into the Number field with no inline rejection | ✅ Verified (previously captured) |
| 01-admin-negative-decimal-number-accepted.png | The same negative decimal saved and shown in the record grid after Save & Close | ✅ Verified (previously captured) |

Path-only URL: `/CustomTable/GetCustomTableDataList?tableKey={tableKey}` (the record grid reached via the "Add a Record" button; ids shown as {placeholders}).
