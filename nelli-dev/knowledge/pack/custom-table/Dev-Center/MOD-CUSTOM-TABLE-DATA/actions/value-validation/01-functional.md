# Value validation — Functional

> **Screenshots (2026-10-08, INT admin — new captures).** 🔄 Updated. Verified read-only on INT
> (fields name / Number / Address, TableId 90). The **client-side required validation is now
> verified**: the unique field `name` is marked required and clearing it shows **"Input is Required."**
> inline and blocks submit with no server call. Length/type validation for custom-table values is
> enforced server-side and still could not be exercised under the read-only remit, so it stays
> ⚠️ Not verifiable.
>
>
>

## 1. What it is

Value validation is the set of rules that check whether a field value is acceptable before it is saved to a custom table. It runs whenever a record is added, edited, imported, or inserted through the API. Different layers enforce different rules — the admin form, the API service, and the database each catch different kinds of invalid data.

## 2. Where it happens

- **Admin form**: When you add or edit a record, the form itself prevents some invalid values before you submit (for example, you cannot type a negative sign or a decimal point into a Number field).
- **API**: When the API receives a create or update request, it checks that unique fields are not empty and that number values fit within the allowed precision and scale.
- **Database**: When the value is written to the database, the column definition enforces data type, length, and uniqueness.
- **Import**: When records are imported via CSV, validation is handled by a stored procedure, not by the same API code.

## 3. Who is affected

Anyone who adds, edits, or imports records into a custom table is subject to value validation. This includes admin users, API consumers, and import processes.

## 4. Rules by field type

### Text

- Any text value is accepted.
- Maximum length is determined by the field's configured length. If the field has a length set, the database column is created as `NVARCHAR({length})` and values exceeding it are rejected by the database.
- If no length is configured, the column may be `NVARCHAR(MAX)` with no practical limit.
- No special character restrictions, no HTML sanitization, and no XSS filtering are applied at any layer.
- Text is optional — empty values are allowed.

### TextArea

- Same as Text, but the database column is always `NVARCHAR(MAX)`, so there is no database-level length limit.
- The maximum length can be configured through a global setting (Custom Table Settings in Admin > System Settings > Global Settings), but this is enforced only on the admin form, not at the API level.
- TextArea is optional — empty values are allowed.

### Number

- Must be a valid decimal number.
- On the admin form, negative values and decimal points are blocked. Through the API, both are accepted.
- Precision and scale are configured as the field's length in the format "precision,scale" (for example, "10,2" means up to 10 total digits with 2 decimal places). Values exceeding this are rejected by the API with the message: "The numeric value should fall within the range of ({precision},{scale})".
- If no precision/scale is configured, any number is accepted at the API level.
- Number is optional when not marked as unique. An empty Number value is set to null in the database.
- When a Number field is marked as unique, it must have a non-zero, non-empty value.

### Boolean

- On the admin form, Boolean is presented as a dropdown with two choices: "NO" (false) and "YES" (true). No other value is possible.
- Through the API, no validation is performed on Boolean values. Any value is passed to the database, where the BIT column accepts 0, 1, and null.
- The default value for a new record is "NO" (false).

### DateTime

- On the admin form, a date picker control is used.
- Through the API on record creation, the value is converted using the server's culture. An unparseable date causes a server error.
- Through the API on record update, no date conversion is performed — the value is passed directly to the database.
- DateTime is optional — empty values are allowed (stored as null).

## 5. Unique field rules

- If a field is marked as unique, its value must not be empty or whitespace. The error message is: "FieldValue is required for Unique Field: {field name}".
- If a numeric unique field has a value of 0, it is treated as empty. The error message is: "Input is required."
- If the value duplicates an existing record's unique value, the database rejects the insert or update. The error is a raw SQL unique constraint error.
- Uniqueness checking against existing records is done by the database constraint at write time, not by a pre-check query in the API service.
- There is no check before saving: a value already used in a unique field is caught only when the record is saved, and the save is refused. (The "does this table have records" check the admin makes elsewhere looks only at whether the table is empty, not at individual values.)
- Uniqueness is typically case-insensitive (depends on database collation).
- Only one null is allowed in a unique column (SQL Server UNIQUE constraint behaviour).

## 6. Messages you may see

| Message | When it appears | When it does not |
|---|---|---|
| "FieldValue is required for Unique Field: {field name}" | A unique field was left empty or whitespace | The unique field has a value |
| "Input is required." | A numeric unique field was set to 0 | The numeric unique field is non-zero |
| "The numeric value should fall within the range of ({precision},{scale})" | A number exceeds the configured precision or scale | The number fits |
| "A record with this unique key already exists. Please ensure that the value entered for the unique key column is distinct." | Admin form: a unique value already exists (on add only) | The unique value is new, or on edit |
| "Failed to create." / "Failed to update record." | Admin form: any server-side error including unique violation on edit | No error |
| Raw SQL unique constraint error | API: duplicate unique value at database level | No duplicate |
| SQL truncation or conversion error | Value exceeds column length or wrong type at database level | Value fits |

## 7. How validation differs by surface

- **Admin form**: strictest for Number (blocks negatives and decimals), Boolean (dropdown only), and field length (client-side check). Less strict for unique field duplicates (pre-check is advisory, not blocking).
- **API single insert/update**: validates unique field emptiness and numeric precision/scale only. Does not validate text length, Boolean values, or DateTime format (except on Create).
- **Bulk insert/update API**: validates table and column existence only. Does not run `ValidateCustomField`.
- **CSV import**: delegated entirely to a stored procedure with its own validation rules.
- **Database**: enforces column type, length, and unique constraints. This is the ultimate enforcement for all surfaces.

## 8. What can be combined

Not applicable.

## 9. What it changes elsewhere

Validation does not change data. It either allows the value through or blocks the save with an error.

## 10. Quick answers

**Q: Is Number input required?**
On the admin form, the Number field restricts input to non-negative whole numbers. Through the API, Number is optional (empty values are stored as null) unless the field is marked as unique.

**Q: Can I enter negative numbers?**
Not through the admin form. Through the API, yes.

**Q: Can I enter decimals?**
Not through the admin form. Through the API, yes — as long as the value fits within the field's precision and scale.

**Q: Is the unique check done before or during the save?**
During the save, by the database constraint. The form does not check for duplicates before it is submitted.

**Q: What happens when the API receives a text value longer than the field length?**
The API does not check text length. The database rejects the value when the INSERT or UPDATE runs.

**Q: What happens when the API receives an invalid date?**
On create: a server error (500). On update: the value is passed to SQL, which may reject it.

**Q: Are Boolean values validated?**
On the admin form, only "YES" and "NO" are possible. Through the API, no validation occurs — any value is passed to the database.

**Q: Does import use the same validation as the API?**
No. Import uses a stored procedure with its own validation logic.

**Q: What is the order of validation checks?**
Unique field emptiness is checked first, then numeric precision/scale. If both pass, the value goes to SQL, where column constraints are the final check.

**Q: Can two records both have a null unique value?**
No. SQL Server's UNIQUE constraint allows only one null.

## 11. For developers

See `03-frontend-admin.md` for client-side validation attributes; `06-api.md` for which endpoints run which checks; `07-functions.md` for the validation method signatures, line by line, and the cross-surface comparison table; `08-database.md` for column types and constraints.

## Fields and options

Record-value validation messages (from verified code; a real validation error could not be triggered
live because no table/record could be seeded):

| Validation | Message (verbatim) | Where it comes from |
|---|---|---|
| Required field empty | field-level required message | the field's required flag |
| Over-length Text / Text Area | "Input value must not exceed the maximum character limit of {max}." | global max-field-length setting |
| Wrong Number format | "Invalid format for numeric field '{name}'. Use 'precision, scale'." | Number field precision/scale rules |
| Unique constraint violated | "...unique key constraint..." (`Admin_Resources.ErrorCustomTableUniqueKeyConstraint`) | the field's unique flag |

## Screenshot verification (2026-10-08)

| Screenshot | Shows | Result |
|---|---|---|
| 00-admin-record-grid-populated.png | The populated `testabhi` record grid (name / Number / Address, 2 rows) the validation was tested against | ✅ Verified |
| 01-admin-edit-record-form.png | The Edit Record form with Divi's values and the required (`*`) unique field `name` | ✅ Verified |
| 02-admin-required-field-client-validation-error.png | The inline "Input is Required." error after clearing `name`; submit blocked, no server call | ✅ Verified (client-side required validation) |
| server-side length / type validation | Needs a real save to trigger; not exercised under the read-only remit | ⚠️ Not verifiable |

Path-only URL: `/CustomTable/EditCustomTableData?TableKey={tableKey}&Id={id}` (the edit form where the required-field validation fires; ids shown as {placeholders}).

## Corrections (2026-10-08)

| Was documented as | Corrected to | Evidence |
|---|---|---|
| "⚠️ Not verifiable live in this pass" — no table could be seeded, so no validation could be observed | Client-side required validation **is** verified: the unique field `name` shows "Input is Required." inline and blocks submit; only server-side length/type validation remains ⚠️ Not verifiable | New INT captures 00/01/02 against seeded table `testabhi` (2026-10-08) |
