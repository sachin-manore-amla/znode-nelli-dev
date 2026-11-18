# Field types

> **Screenshot banner (2026-10-08, INT admin, read-only).** The FIELD TYPE dropdown was reached read-only on INT via an Add Custom Field row; all five options were confirmed verbatim (see Corrections and Screenshot verification below). Nothing was saved.
>
>

## 1. What it is

When you add a field to a custom table, you choose one of five field types. The field type determines what kind of data the field can hold, what input control appears when entering data, and how the field is stored.

## 2. Where you do it

In the admin: Dev Center > Custom Table > (select a table) > Fields tab. The field type is selected from a dropdown on each field row.

Not available on the webstore, Commerce Portal, or B Store app.

## 3. Who can do it

Anyone with access to the Custom Table section in the admin. There is no separate permission for field types.

## 4. Step by step

1. Open the fields tab for a custom table.
2. Add a new field row.
3. Select the field type from the dropdown.
4. Enter a field length (for Text, Text Area, and Number fields).
5. Save.

## 5. What is allowed and what is not

- There are exactly five field types: Text, Text Area, Number, Boolean, and Date And Time. The list is fixed and cannot be configured.
- Once a field is saved, its type cannot be changed. The dropdown is locked for existing fields.
- A table can have fields of different types — there is no limit on the mix.
- The field type affects whether a field can be marked as unique: only Text and Number fields can be unique.

### The five field types

**Text** — A single-line text field. You enter a field length (number of characters). The maximum length can be limited by a global setting. The data is stored as text up to the length you specify.

**Text Area** — A multi-line text field. You enter a field length. If the length is more than 4000 characters, the storage switches to an unlimited-length format. The maximum length can be limited by a separate global setting.

**Number** — A decimal number field. Instead of a simple character count, you enter a precision and scale (for example, "10,2" means up to 10 digits total with 2 after the decimal point). Precision must be greater than zero, and scale must be between zero and the precision. A separate global setting can limit the maximum precision and scale.

**Boolean** — A true/false field. No field length is needed. The field stores one of two values (true or false). When unique is set, only one true, one false, and one empty value can exist.

**Date And Time** — A date and time field. No field length is needed. The field stores a date and time value. The time zone depends on what is entered — there is no automatic conversion.

## 6. Messages you may see

| Message | When it appears | When it does not |
|---|---|---|
| "FieldLength for field '{name}' must be a positive integer." | Text or Text Area field with a missing, zero, or negative length | Number, Boolean, Date And Time fields |
| "Input value must not exceed the maximum character limit of {max}." | Text or Text Area field length exceeds the global setting maximum | When no maximum is configured |
| "FieldLength for field '{name}' must include both precision and scale (e.g., \"10,2\")." | Number field length is not in "precision,scale" format | Text, Boolean, Date And Time fields |
| "Invalid format for numeric field '{name}'. Use 'precision, scale'." | Number field precision or scale is not a valid number | When format is correct |
| "FieldLength for field '{name}' is invalid: precision must be > 0 and scale must be between 0 and precision." | Number field precision is zero or scale is out of range | When values are in range |
| "Input value must not exceed the maximum limit of precision: {p} and scale: {s}." | Number field exceeds the global setting maximum | When no maximum is configured |

## 7. How it differs

- **By field type and length settings:** When the global settings for maximum field length are not configured (as on the development environment), no maximum is enforced — you can enter any positive length for Text and Text Area, and any valid precision/scale for Number.
- **By field type and unique constraint:** Only Text and Number fields can be marked as unique. For Boolean and Date And Time, the unique constraint option is not available.
- **Text vs Text Area storage:** Both store text, but Text Area fields with a length over 4000 characters use an unlimited-length storage format, while Text fields always use a fixed-length format.

## 8. What can be combined

Any combination of field types in a single table is allowed. There is no setting that restricts the mix.

## 9. What it changes elsewhere

The field type determines the physical column type on the underlying data table. Changing the field type after creation is not supported (the admin locks it). If attempted directly through the API, it could alter the column type, which may cause data loss or errors with existing data.

## 10. Quick answers

**Q: What are the available field types?**
Text, Text Area, Number, Boolean, and Date And Time.

**Q: Can I change a field's type after it is saved?**
No. The admin locks the field type dropdown for existing fields. The API does not enforce this restriction, but changing the type through the API could cause data errors.

**Q: What is the maximum length for a Text field?**
It depends on the global setting "CustomTableMaxFieldLengthForText". If not configured, there is no enforced maximum. → Full detail: settings/custom-table-max-field-length-for-text.md

**Q: What is the maximum length for a Text Area field?**
It depends on the global setting "CustomTableMaxFieldLengthForTextArea". If not configured, there is no enforced maximum. Text Area fields with a length over 4000 use unlimited storage. → Full detail: settings/custom-table-max-field-length-for-text-area.md

**Q: What format does the Number field length use?**
"precision,scale" — for example, "10,2" means up to 10 digits with 2 decimal places. The maximum is governed by the global setting "CustomTableMaxFieldLengthForNumber". → Full detail: settings/custom-table-max-field-length-for-number.md

**Q: Do Boolean and Date And Time fields need a length?**
No. Length is ignored for these types.

**Q: Is the list of field types configurable?**
No. The five types are hardcoded in the admin.

**Q: Can a table have fields of different types?**
Yes, with no restrictions.

**Q: Which field types can be marked as unique?**
Only Text and Number.

## 11. For developers

See `03-frontend-admin.md` for admin dropdown and TypeScript behavior, `06-api.md` for API constants and validation, `07-functions.md` for the call tree and function details, `08-database.md` for SQL type mapping and DDL generation.

## Fields and options

The Field Type dropdown offers exactly **five** options (fixed list; the dropdown could not be
expanded live, values are from the verified code):

| Option (verbatim) | Length input | Can be Unique | Where it comes from |
|---|---|---|---|
| `Text` | field length (characters) | Yes | fixed field-type enum |
| `Text Area` | field length (characters; >4000 switches to unlimited storage) | No | fixed field-type enum |
| `Number` | `precision,scale` (e.g. `10,2`) | Yes | fixed field-type enum |
| `Boolean` | none | No | fixed field-type enum |
| `Date And Time` | none | No | fixed field-type enum |

The list is fixed and cannot be configured; for an existing field the dropdown is locked.

## Screenshot verification (2026-10-08)

Screen: `/CustomTable/CustomTableFieldList?tableKey={tableKey}` (path only; ids as `{tableKey}`).

| Screenshot | Shows | Result |
|---|---|---|
| `screenshots/01-admin-add-field-row-field-type-options.png` | New Add Custom Field row FIELD TYPE dropdown listing all five options verbatim: `Text`, `Text Area`, `Number`, `Boolean`, `Date And Time` | 🔄 Updated — newly captured read-only on INT (2026-10-08); supersedes the earlier "not verifiable" note |
| `screenshots/01-admin-add-field-row-field-type-options.png` | Is Unique dropdown disabled on the new, unsaved field row | 🔄 Updated — newly captured read-only on INT (2026-10-08) |

The five field types and the disabled Is Unique on a new row are ✅ Verified on INT (store Amla, v10.14.4.0). Nothing was saved.

## Corrections (2026-10-08)

| Was | Now | Evidence |
|---|---|---|
| "⚠️ Not verifiable live in this pass … no table could be seeded (transient SQL write failure on int)." | The FIELD TYPE dropdown **was** reached read-only on INT; the five options were confirmed verbatim and Is Unique was seen disabled on the new row. | `screenshots/01-admin-add-field-row-field-type-options.png`, INT admin 2026-10-08 |
| Five options "from the verified code; the dropdown could not be expanded live". | ✅ Verified live on INT (read-only): `Text`, `Text Area`, `Number`, `Boolean`, `Date And Time`. | same screenshot |
