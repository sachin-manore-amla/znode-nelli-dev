# Unique field

> **Screenshot banner (2026-10-08).** Unique-field evidence (previously captured):
>
>

> **Corrected (int, 2026-10-05, confirmed live):** this file previously said the Is Unique dropdown
> is **disabled** in the admin when the table has data (see step 2 and §5 below), implying the admin
> blocks the action visibly. **Not what happens for a newly added field.** Live test: added a new
> field to a table that already had one data row, set its Is Unique select to `true` via the admin
> grid (the control was interactive, not disabled), and saved. The save succeeded, but the field was
> written with Is Unique silently forced back to `false` - no disabled control, no error message, no
> indication at all that the value did not take. See
> ../add-fields/01-functional.md for the full finding and
> screenshot. Not yet re-tested for the case of **editing an already-existing field's** Is Unique
> dropdown on a table with data (as opposed to adding a brand new field) - that case may behave
> differently and is left for a future pass.

## 1. What it is

You can mark one field in a custom table as unique. This ensures that no two records in the table can have the same value in that field. The unique setting is **documented** to only be applicable while the table has no data rows - confirmed live that the save is accepted but the flag is silently dropped instead, see the correction note above.

## 2. Where you do it

In the admin: Dev Center > Custom Table > (select a table) > Fields tab. Each field row has an "Is Unique" dropdown with true/false options.

Not available on the webstore, Commerce Portal, or B Store app.

## 3. Who can do it

Anyone with access to the Custom Table section in the admin. There is no separate permission for the unique field setting.

## 4. Step by step

1. Open the fields tab for a custom table.
2. Make sure the table has no data rows. **Confirmed live: for a newly added field, the dropdown is
 not actually disabled when the table has data** - it can be set to "true", but the save silently
 resets it to "false" instead of rejecting it or disabling the control. See the correction note at
 the top of this file.
3. On the desired field row, set the Is Unique dropdown to "true".
4. Save.

To change which field is unique:
1. Set the current unique field's dropdown to "false".
2. Set the new field's dropdown to "true".
3. Save.

## 5. What is allowed and what is not

- Only one field per table can be marked as unique. Setting a second field as unique is rejected with a message.
- The unique setting is documented to be applicable only when the table has no data rows. **Confirmed live: for a newly added field, the dropdown is not disabled** - the admin accepts "true" and silently saves it as "false" instead when the table has data. See the correction note at the top of this file.
- Only Text and Number field types can be marked as unique. For Boolean and Date And Time, the admin locks the unique option.
- A unique field cannot be deleted. You must first remove the unique setting, then delete the field.
- If the unique setting is applied and then data is added, the constraint remains. Future records must have unique values in that field.

## 6. Messages you may see

| Message | When it appears | When it does not |
|---|---|---|
| "Multiple fields cannot be set as Unique." | More than one field is marked as unique in the same save | Only one field is unique |
| "The field cannot be added or modified with a UNIQUE constraint after data has been inserted into the custom table." | Trying to add a unique constraint when the table already has data (through the API create path) | Table has no data |
| "The field set as unique cannot be deleted." | Clicking delete on a field that is marked as unique (admin client-side check) | Field is not unique |
| "A unique field cannot be changed as data associated with the table." | Trying to delete a unique field through the API | Field is not unique |
| SQL duplicate error | Adding a record with a duplicate value in the unique field | Values are unique |

## 7. How it differs

- **Create vs edit path in the API:** When creating fields, the system checks if the table has data before allowing a unique constraint. When editing fields, the system does not check for data — it directly attempts to add the constraint. If the column has duplicate data, the database rejects it with an error.
- **By field type:** Only Text and Number fields can be unique. Boolean fields would be limited to at most three rows (true, false, and empty). Date And Time fields are not offered the unique option in the admin.
- **Case sensitivity:** Whether "ABC" and "abc" are treated as the same value depends on the database collation, which is typically case-insensitive.
- **Empty values:** The unique constraint allows only one empty (null) value per field.

## 8. What can be combined

The unique setting is independent of field length. A Text field can be unique and have any length, though very long text fields (over 450 characters) may be rejected by the database when creating the unique constraint due to a key size limit.

## 9. What it changes elsewhere

- A unique constraint is physically created on the data table column. This persists even after the admin session ends.
- Importing data with duplicate values in the unique field will fail at the database level.
- Deleting the custom table removes the constraint along with the table.

## 10. Quick answers

**Q: Can I mark more than one field as unique?**
No. Only one field per table can be unique.

**Q: Can I set a field as unique after data has been added?**
In the admin, no — the dropdown is disabled when the table has data. Through the API's edit path, it is technically attempted but will fail if duplicate data exists in the column.

**Q: Can I remove the unique setting?**
Yes, during editing — set the dropdown to "false" and save. This works even when the table has data.

**Q: Can I delete a unique field?**
No. You must first remove the unique setting, then delete the field.

**Q: Which field types can be unique?**
Text and Number only.

**Q: What happens if I import duplicate values?**
The import fails for the duplicate row — the database rejects it.

**Q: Is the unique check case-sensitive?**
It depends on the database collation. Typically it is case-insensitive.

## 11. For developers

See `03-frontend-admin.md` for admin dropdown and client-side restrictions, `06-api.md` for API behavior per path, `07-functions.md` for the full call tree and function details, `08-database.md` for DDL and constraint behavior.

## Fields and options

The unique setting is the **Is Unique** column on each row of the Manage Fields grid (`/CustomTable/CustomTableFieldList?tableKey={tableKey}`):

| Control | Options / behaviour | Where the value comes from |
|---|---|---|
| Field Type (gates Is Unique) | Boolean / Date And Time do not offer the unique option | fixed field-type enum |

## Screenshot verification (2026-10-08)

Grid / record screens under `/CustomTable/CustomTableFieldList?tableKey={tableKey}` (path only; ids as `{tableKey}`).

| Screenshot | Shows | Result |
|---|---|---|
| `screenshots/01-admin-add-record-unique-warning-dialog-non-unique-field.png` | Warning dialog raised for a duplicate value against a field's uniqueness | ✅ Verified — previously captured; not re-captured this pass |

New-row `Is Unique` being disabled until first save is ✅ Verified on INT (2026-10-08, read-only; see `../field-types/01-functional.md`). Nothing was saved.
