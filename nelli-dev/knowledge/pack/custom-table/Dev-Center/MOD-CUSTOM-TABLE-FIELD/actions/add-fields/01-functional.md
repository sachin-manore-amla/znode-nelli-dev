# add-fields — Functional overview

> **Corrected (int, 2026-10-05, confirmed live, admin UI):** the claim below that adding a unique
> field to a table with data is **rejected with an error message** is only confirmed for the raw
> API contract (per source) - it is **not what the admin UI does**. Live test on `kbprobeFieldTest`
> (1 data row, existing field `kbprobeEditMe` already unique): added a new field
> `kbprobeUniqueWithData` with **Is Unique** toggled to `true` and Field Length `5`, clicked
> **Save & Close**. The save **succeeded** with no error banner at all - but the new field was
> written with **Is Unique = false** (confirmed both by the red X icon in Manage Fields and by
> reading the live `<select id="IsUniqueConstraint_N">` value after reopening the row in edit
> mode: `false`). **The admin UI silently drops the unique flag instead of rejecting the save or
> showing the documented message** when the table already has data. The message
> "The field cannot be added or modified with a UNIQUE constraint after data has been inserted
> into the custom table." was never observed on screen during this test. Not yet re-verified
> against the raw API endpoint directly (bypassing the admin UI) to see whether the API itself
> still returns that message, or whether the admin's own client-side/server-side handling for this
> screen silently strips the flag before or after the API call.
>
>

> **Screenshot banner (2026-10-08).** Admin evidence for this action (previously captured):
>
>
>
>

## 1. What it is

Adding fields creates new columns on a custom table. Each field has a type (Text, Text Area, Number, Boolean, or Date and Time), a code (the internal identifier), a display name, a length (for text and number types), a display order, and optionally a unique constraint. Fields can be added one at a time or several at once. Adding a field physically alters the underlying data table in the database.

## 2. Where you do it

- **Admin:** Dev Center > Custom Tables > open a table > Fields tab > click "Add Custom Field".
- **API:** `POST /v1/custom-table-fields` with a JSON array of field objects.
- **Webstore:** Not available.
- **Commerce Portal:** Not available.
- **B Store:** Not available.

## 3. Who can do it

Any admin user whose role includes access to Dev Center > Custom Tables can add fields. There is no separate permission for adding fields versus editing the table. Non-admin users cannot add fields.

## 4. Step by step

### In the admin

1. Open a custom table from Dev Center > Custom Tables.
2. On the Fields tab, click **"Add Custom Field"**. A new empty row appears in the grid.
3. Choose a **Field Type** from the dropdown (Text is the default).
4. Enter a **Field Code** (letters and numbers only, no spaces or special characters).
5. Enter a **Field Name** (the label users will see).
6. Optionally set **Is Unique** to true (only one field per table can be unique).
7. Enter a **Field Length** (for Text, Text Area, or Number types; not needed for Boolean or Date and Time).
8. Enter a **Display Order** number.
9. Repeat steps 2-8 to add more fields in the same save.
10. Click **Save**. The page refreshes showing the updated field list with a success message.

### Via API

Send a POST request with a JSON array of field objects. One or many fields can be created in a single call.

## 5. What is allowed and what is not

- The custom table must be saved (have a table key) before fields can be added.
- **Field Code** must contain only letters and numbers (A-Z, a-z, 0-9). No spaces, hyphens, underscores, or special characters. Maximum 100 characters. It must be unique within the table (the check ignores upper/lower case — "name" and "Name" are treated as the same). The code "ID" is reserved and cannot be used.
- **Field Name** can contain any characters, up to 100 characters.
- **Field Length** must be a positive whole number for Text and Text Area fields, and must not exceed the maximum set in Global Settings (typically 4000 for Text and 8000 for Text Area). For Number fields, it must be in "precision,scale" format (e.g. "18,2"), where precision is greater than zero and scale is between zero and the precision. Boolean and Date and Time fields do not have a configurable length.
- **Display Order** is required. Any integer is accepted. Duplicates are allowed. No range is enforced.
- **Only one field per table** can be marked as unique. If more than one field in a single request is set as unique, the request is rejected.
- A unique field is documented to be rejected outright when added to a table that already has data
 rows. **Confirmed live (admin UI, int, 2026-10-05): this is not what happens in the admin.** The
 save succeeds, but the new field is silently saved with Is Unique = false instead - no error is
 shown. See the correction note at the top of this file. If the table is empty and a different
 field is already marked as unique, the old unique constraint is removed and the new one takes its
 place (not retested live in this session).
- There is no hard limit on the number of fields a table can have. The knowledge base recommends a maximum of 15 columns, but this is a guideline only — no code enforces it.
- Fields can be added to a table that already has data. Existing rows will have empty (null) values for the new columns.

## 6. Messages you may see

| Message | When it appears |
|---|---|
| Success notification (update message) | After fields are saved successfully |
| "Field Code Already Exist" | When the field code matches an existing field in the same table (case-insensitive) |
| "Multiple fields cannot be set as Unique." | When more than one field in the request has the unique flag set |
| "The field cannot be added or modified with a UNIQUE constraint after data has been inserted into the custom table." | Documented for the API when trying to add a unique field to a table that already has data. **Not observed in the admin UI (confirmed live, int, 2026-10-05)** - the admin silently saves the field as non-unique instead; see correction note at top of file |
| "The field code 'ID' is reserved and cannot be used. Please choose a different code." | When the field code is "ID" |
| "Input value must not exceed the maximum character limit of {max}." | When the field length exceeds the global maximum for that type |
| "Input value must not exceed the maximum limit of precision: {p} and scale: {s}." | When the numeric precision or scale exceeds the global maximum |
| "FieldLength for field '{code}' must be a positive integer." | When the field length is zero, negative, or not a number (for Text/Text Area) |
| "The requested table does not exist" | When the table key in the request does not match any table |
| "ErrorSetUniqueFieldType" (admin JS) | When trying to set unique on a Boolean or Date and Time field in the browser |
| Error notification (failed to create) | When an unexpected error occurs during save |

## 7. How it differs

### By field type

| Field type | Length required | Unique allowed | SQL column created |
|---|---|---|---|
| Text | Yes (positive integer) | Yes | Variable-length text column |
| Text Area | Yes (positive integer) | No (admin JS blocks it) | Variable-length text column; very long values use maximum-length storage |
| Number | Yes ("precision,scale") | Yes | Decimal column |
| Boolean | No (set to "0" automatically) | No | True/false column |
| Date and Time | No (set to "0" automatically) | No | Date and time column |

### When the table has data

- New non-unique fields can still be added. Existing rows get empty values.
- Unique fields are documented as rejected with a message (API). **Confirmed live in the admin UI
 (int, 2026-10-05): the field is saved anyway, with Is Unique silently forced to false** - no
 rejection message is shown.

### When the table is empty

- All field types and configurations are allowed.
- If a unique field already exists and a different unique field is added, the old one loses its unique constraint automatically.

## 8. What can be combined

- Multiple fields can be added in a single save (admin) or a single API call.
- Only one field per table can have the unique constraint. The system enforces this both per request and across existing fields.

## 9. What it changes elsewhere

- A physical column is added to the table's data storage. Any existing data rows receive empty values for the new column.
- If replacing a unique constraint on an empty table, the old field's unique constraint is removed from both the data storage and the field definition.
- The field definition is recorded so it appears in the field list, imports, exports, and anywhere the table's structure is read.

## 10. Quick answers

**Q: Can I add more than one field at a time?**
Yes. In the admin, click "Add Custom Field" multiple times to add rows, then Save. Via the API, send an array with multiple field objects.

**Q: What characters can I use in a Field Code?**
Letters (A-Z, a-z) and numbers (0-9) only. No spaces, hyphens, underscores, or special characters. The code "ID" is reserved.

**Q: What is the maximum field length for a Text field?**
It depends on the Global Settings value for "Custom Table Max Field Length For Text", which defaults to 4000 characters. This can be changed by an administrator.

**Q: Can I add a unique field to a table that has data?**
Documented as no, with the message "The field cannot be added or modified with a UNIQUE constraint
after data has been inserted into the custom table." **Confirmed live in the admin UI (int,
2026-10-05): the admin does not show this message or reject the save** - it saves the field with
Is Unique silently reset to false instead. See the correction note at the top of this file.

**Q: Is there a limit on how many fields a table can have?**
There is no hard limit in the system. The knowledge base recommends a maximum of 15 columns, but this is not enforced.

**Q: What happens to existing data when I add a field?**
Existing rows get empty (null) values for the new field. No default value is applied.

**Q: Can a Field Code start with a number?**
Yes. Unlike the table key (which must start with a letter), a field code like "123" passes validation.

**Q: Is the Field Code case-sensitive?**
The code is stored as entered, but the duplicate check is case-insensitive. You cannot have both "Name" and "name" as field codes in the same table.

## 11. For developers

See `03-frontend-admin.md` for the admin screen and browser validation, `06-api.md` for the API endpoint and all error responses, `07-functions.md` for the back-end call tree and every validation, and `08-database.md` for the ALTER TABLE operation and field storage.

## Fields and options

Fields and controls on the **Add Custom Field** row of the Manage Fields grid (`/CustomTable/CustomTableFieldList?tableKey={tableKey}`):

| Field / control | Options / behaviour | Where the value comes from |
|---|---|---|
| Field Type | dropdown: `Text`, `Text Area`, `Number`, `Boolean`, `Date And Time` (5 options on a new row) | fixed field-type enum |
| Field Name | free text, max 100 | user input (display label) |
| Is Unique | dropdown true/false; **disabled on a new, unsaved row** until the field is first saved | unique constraint flag |
| Field Length | Text / Text Area: positive integer (capped by Global Settings); Number: `precision,scale`; hidden for Boolean / Date And Time | user input, gated by `CustomTableMaxFieldLengthFor*` |
| Display Order | integer | user input |
| Action | per-row edit + delete icons | n/a |

## Screenshot verification (2026-10-08)

Grid screen: `/CustomTable/CustomTableFieldList?tableKey={tableKey}` (path only; ids as `{tableKey}`).

| Screenshot | Shows | Result |
|---|---|---|
| `screenshots/01-admin-add-field-works-with-data-present.png` | Add Custom Field accepted on a table that already has data rows | ✅ Verified — previously captured (2026-10-05); not re-captured this pass, consistent with INT facts |
| `screenshots/02-admin-field-length-exceeds-global-setting-error.png` | Field length over the Global Settings ceiling is rejected with the length error | ✅ Verified — previously captured (2026-10-05); not re-captured this pass |
| `screenshots/03-admin-field-added-successfully-table-has-data.png` | Field saved successfully, success notification, grid refreshed with data present | ✅ Verified — previously captured (2026-10-05); not re-captured this pass |
| `screenshots/06-unique-field-silently-reset-false-with-data.png` | A new unique field on a table with data saves with Is Unique silently forced to `false` | ✅ Verified — previously captured (2026-10-05) live on int |

New-row `Is Unique` being disabled until first save is ✅ Verified on INT (2026-10-08, read-only; see `../field-types/01-functional.md`).
