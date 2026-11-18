# Edit field

> **Screenshot banner (2026-10-08, INT admin, read-only).** The Manage Fields inline-edit grid was reached read-only on INT for table `testabhi` and the edit-field behaviour confirmed (see Corrections and Screenshot verification below). Nothing was saved.
>
>

## 1. What it is

After a field has been added to a custom table and saved, some of its properties can still be changed. You can update the field name, display order, field length, and the unique setting. The field type and field code cannot be changed after creation.

## 2. Where you do it

In the admin: Dev Center > Custom Table > (select a table) > Fields tab. The same form used for adding fields also shows existing fields for editing.

Not available on the webstore, Commerce Portal, or B Store app.

## 3. Who can do it

Anyone with access to the Custom Table section in the admin. There is no separate permission for editing fields.

## 4. Step by step

1. Open the fields tab for a custom table.
2. The form loads with all existing fields pre-populated with their current values.
3. Change the field name, display order, field length, or unique setting as needed.
4. Click Save.
5. A success message appears and the page reloads with the updated fields.

## 5. What is allowed and what is not

- **Field Name** can be changed freely. It is a display label only — it does not affect the underlying data column. Two fields can have the same name (no uniqueness check).
- **Display Order** can be changed. It must be greater than zero.
- **Field Length** can be changed. The system alters the underlying column to match the new length. If the table has data and the new length is smaller than existing data, the change fails with an error.
- **Is Unique** can be changed if the table has no data rows. If the table has data, the dropdown
 was previously thought to be locked - **corrected (int, 2026-10-05, confirmed live): it is not**.
 Editing an EXISTING, already-saved field's Is Unique flag works even with data present - tested
 by switching uniqueness from one existing field to another in the same save (`kbprobeEditMe` ->
 false, `kbprobeEditTest` -> true) on a table with one data row: both changes persisted correctly,
 "Record updated successfully.", no error. This is **different from adding a brand-new field**
 with Is Unique = true on a table with data, which is silently saved as false instead (see
 `add-fields/01-functional.md` and `unique-field/01-functional.md`) - the restriction applies only
 to a newly-created field, not to editing an existing one. See
 `screenshots/01-admin-existing-field-unique-toggled-with-data-works.png`.
- **Field Type** cannot be changed in the admin for an existing field. **Confirmed live (int,
 2026-10-05):** the mechanism is not an HTML-disabled dropdown - the `<select>` is dynamically
 pruned down to only the field's current type as its one option, so there is nothing else to pick.
 Same practical result either way; see `../field-list/01-functional.md` for the corrected
 description and `../field-list/screenshots/01-admin-field-list-empty-table.png`.
- **Field Code** cannot be changed in the admin. It is locked (`readOnly`) for existing fields
 regardless of whether the table has data - confirmed live - and is the name of the underlying
 data column.

## 6. Messages you may see

| Message | When it appears | When it does not |
|---|---|---|
| Success notification (update message) | All fields updated successfully | When there is an error |
| "Display order can not be less than one" (API) / "Display Order should be between 1 and 500." (admin UI - **confirmed live, int, 2026-10-05**) | Display order is set to zero, negative, or over 500 | Display order is 1-500 |
| "The Field Name is required." | Field name is left blank | Field name is filled in |
| "Multiple fields cannot be set as Unique." | More than one field is marked as unique | Only one or no unique field |
| Field length validation messages | See "field-types" action for per-type messages | When length is valid |
| SQL error message | Changing length to a value incompatible with existing data | When data fits the new length |
| "A unique field cannot be changed as data associated with the table." | Internal error when DDL fails for non-SQL reasons | Normal operation |

## 7. How it differs

- **With data vs without data:** When the table has data, changing the field length could fail if existing data exceeds the new size. The unique setting is locked. Without data, all editable properties can be changed freely.
- **Admin vs API:** The admin prevents changing field type and field code by locking those controls. The API does not enforce this restriction — it uses whatever values are sent in the request to alter the column. Changing the type through the API could cause data loss or errors.

## 8. What can be combined

Multiple fields can be edited in a single save. The admin submits all field rows together, and the API processes them in one call.

## 9. What it changes elsewhere

- Changing the field length alters the physical column on the underlying data table. This affects the maximum size of data that can be stored.
- Changing the field name updates only the display label — no effect on the data column or existing records.
- Changing the display order may affect the order in which fields appear in the admin and in import/export templates.
- Toggling the unique setting adds or removes a uniqueness constraint on the data column (see the "unique-field" action).

## 10. Quick answers

**Q: Can I change the field type after it is saved?**
No, not in the admin. The field type dropdown is locked for existing fields.

**Q: Can I change the field code after it is saved?**
No. The field code is the name of the data column and cannot be renamed.

**Q: Can I change the field length?**
Yes. The system alters the underlying column. If the table has data that exceeds the new length, the change will fail.

**Q: Can I change the field name to one that already exists?**
Yes. There is no uniqueness check on field names.

**Q: What happens if I set display order to zero?**
In the admin, the save is blocked inline with "Display Order should be between 1 and 500." (confirmed
live, int, 2026-10-05) - also the upper bound, 500, not just a lower-bound check as previously
documented. The API-level message for the same condition is "Display order can not be less than
one." See `screenshots/02-admin-display-order-validation.png`.

**Q: Can two admins edit the same field at the same time?**
Yes, but there is no concurrency control. The last save wins.

**Q: Is there an audit trail for field edits?**
Only the "Modified By" and "Modified Date" columns are updated. There is no separate audit log.

**Q: Can I edit a field while the table has data?**
Yes, but the unique setting is locked, and changing the field length could fail if existing data exceeds the new size.

## 11. For developers

See `03-frontend-admin.md` for admin form behavior and call tree, `06-api.md` for API endpoint details and what is honored vs ignored, `07-functions.md` for the full service call tree and function details, `08-database.md` for ALTER COLUMN DDL and metadata updates.

## Fields and options

The Edit-field panel exposes these controls (from verified code; not captured live):

| Control | Options / behaviour | Where it comes from |
|---|---|---|
| Field Type | fixed list: `Text`, `Text Area`, `Number`, `Boolean`, `Date And Time` - **locked (read-only) for an existing field** | fixed field-type enum |
| Display name | editable text | field display name |
| Field length | editable for Text / Text Area (character count) and Number (`precision,scale`); hidden for Boolean / Date And Time | field length |
| Is Unique | available only for Text and Number fields | unique constraint |

## Screenshot verification (2026-10-08)

Screen: `/CustomTable/CustomTableFieldList?tableKey={tableKey}` (path only; ids as `{tableKey}`).

| Screenshot | Shows | Result |
|---|---|---|
| `screenshots/01-admin-manage-fields-inline-edit-grid.png` | FIELD TYPE dropdown locked to the field's current type only for each existing field (type cannot be changed after creation) | 🔄 Updated — newly captured read-only on INT (2026-10-08); supersedes the earlier "not verifiable" note |
| `screenshots/01-admin-manage-fields-inline-edit-grid.png` | Is Unique dropdown remains editable for existing fields | 🔄 Updated — newly captured read-only on INT (2026-10-08) |

Both findings are ✅ Verified on INT (table `testabhi`, store Amla, v10.14.4.0). Nothing was saved.

## Corrections (2026-10-08)

| Was | Now | Evidence |
|---|---|---|
| "⚠️ Not verifiable live in this pass … no table could be seeded (transient SQL write failure on int)." | The Manage Fields inline-edit grid **was** reached read-only on INT (`testabhi`); the field-type lock and the editable Is Unique were confirmed. | `screenshots/01-admin-manage-fields-inline-edit-grid.png`, INT admin 2026-10-08 |
| Field-type lock described only "from verified code; not captured live". | ✅ Verified live on INT (read-only): an existing field's FIELD TYPE dropdown contains only its current type as its single option. | same screenshot |
