# Field types, accepted values and length rules

What this answers: which field types exist, what each needs and accepts, the three Global Settings that cap length, and the rules for field codes, names, unique and display order. Values below were fired against a Znode 10 development environment (2026-10-05) and confirmed in the product source.

## The six field types

The **value** is what an API caller must send (case-sensitive). The **label** is what Admin shows. They differ.

| Send this value | Admin label | Stored as | Needs `FieldLength`? |
|---|---|---|---|
| `Text` | Text | text of length n | Yes |
| `TextArea` | Text Area | text of length n | Yes |
| `Number` | *(not offered)* | 32-bit whole number | Required by validation, but the type cannot currently be created (see below) |
| `Numeric` | **Number** | decimal(precision, scale) | Yes, as `"precision,scale"` |
| `Boolean` | Boolean | true/false | No |
| `datetime` | Date And Time | date and time | No |

Three traps:

1. **`datetime` is lowercase.** `DateTime` and `Date And Time` fail (`FieldType` is capped at 10 characters, so `Date And Time` fails on length first).
2. **The Admin "Number" option creates `Numeric`**, a decimal, not an integer.
3. **A `Number` field cannot be created** through the API on the builds tested (HTTP 500, with or without `FieldLength`), and Admin never offers it. For whole numbers use `Numeric` with scale 0, for example `"10,0"`. Columns of type `Number` that already exist (created on earlier builds) still work, with the value rules below.

An unrecognised type value (`text`, `Text Area`, `DateTime`) is refused with HTTP 400. The only reason given is a raw database message, found inside the field list (`FieldValidationMessages`), not in the top-level `ErrorMessage`.

## Accepted values per type (API insert and update)

### Text and TextArea

| Value | Result |
|---|---|
| shorter than or equal to the length | accepted (the limit is inclusive) |
| longer than the length | rejected |
| empty | accepted |
| leading or trailing spaces | **kept**: `"A "` and `"A"` are different values (matters for a unique field) |
| apostrophes | accepted safely |
| HTML or script text | stored as-is, never encoded: whatever renders it must encode it |

Note: on the single-record API insert/update, text length is enforced by the database column (a too-long value fails with a database error), while import and bulk calls validate it and give a clear per-row message.

### Number (whole number, existing columns only)

Range is the 32-bit integer range, about plus or minus 2.1 billion. Negative accepted. `1.5`, `1e3`, `abc` rejected. Empty is NULL. Surrounding spaces are trimmed. `FieldLength` does not limit the value.

### Numeric (decimal)

`FieldLength` is `"precision,scale"`: precision is total digits, scale is digits after the point. For `"6,2"` the largest value is `9999.99`.

| Value | Result |
|---|---|
| `12.34`, `1234.56`, `-12.34`, `0` (stored `0.00`) | accepted |
| `12345.6` (too many digits before the point), `12.345` (too many decimals), `abc` | rejected: *The numeric value should fall within the range of (6,2)* |
| empty | accepted, stored NULL |

Rules: maximum precision and scale 38; scale must not exceed precision (`"2,10"` is refused at field creation); the Global Setting for Numeric can lower the ceiling.

### Boolean

| Value | API insert/update | CSV import |
|---|---|---|
| `true`, `false` in any casing, `1`, `0` | accepted | accepted |
| any other non-zero number such as `-1`, `2` | accepted and stored as True (do not rely on it) | rejected |
| empty | accepted, stored NULL (a third state) | accepted, NULL |
| `yes`, `no`, `Y`, `N` | **rejected** | `Yes` and `No` **accepted** (import normalises them) |
| anything else | rejected with a generic message | rejected: *Input value must either be True/1/Yes or False/0/No.* |

### datetime

| Value | Result |
|---|---|
| `2026-01-31`, `2026-01-31T10:20:30` | accepted (date alone gets midnight) |
| `01/31/2026` (US order) | accepted |
| `31-01-2026` (day first) | **rejected** |
| `2026-13-01`, `not a date` | rejected |
| empty, API insert | stored as **`1900-01-01`**, not NULL |
| empty, CSV import | NULL |

Send `yyyy-MM-dd` or ISO `yyyy-MM-ddTHH:mm:ss`. A report that filters by date will pick up the 1900 rows.

## Length and the Global Settings

Admin path: **System Settings > Global Settings > Custom Table Settings**. Platform-wide: no per-store override, and the Custom Table API does not return them (read them with the Global Settings API, `GET /v2/global-settings/code/CustomTableSettings`, from the public spec: not tested).

Six settings, verified in the product source (2026-10-15):

| Label | Setting (attribute code) | What it does | Seeded value | Range the Admin form accepts |
|---|---|---|---|---|
| Text, "max" | `CustomTableMaxFieldLengthForText` | largest Text `FieldLength` accepted | 100 | 1 to 4000 |
| Text Area, "max" | `CustomTableMaxFieldLengthForTextArea` | largest TextArea `FieldLength` accepted | 100 | 1 to 8000 |
| Number, "max" | `CustomTableMaxFieldLengthForNumber` | largest Numeric precision and scale, as `"precision,scale"` | `10,2` | not validated |
| Text, "default" | `CustomTableDefaultFieldLengthForText` | length pre-filled when adding a Text field in Admin | 50 | 1 to 4000 |
| Text Area, "default" | `CustomTableDefaultFieldLengthForTextArea` | pre-filled TextArea length | 100 | 1 to 8000 |
| Number, "default" | `CustomTableDefaultFieldLengthForNumber` | pre-filled Numeric precision and scale | `10,0` | not validated |

The seeded values apply to a fresh environment; an environment can hold other values. The KB's figures (Text 4,000, Text Area 8,000, Number 38/38) match the largest values the form allows, not a fixed limit.

1. **They are upper bounds, not switches.** A blank value removes the ceiling: the check is skipped. To limit field size, enter a value.
2. The message names the configured value: *Input value must not exceed the maximum character limit of N* (observed on one build as *...the character limit of N*). Two environments can legitimately differ. Existing fields are not re-checked after a setting is lowered; only new fields and edits are.
3. `FieldLength` must be a positive integer for Text and TextArea: *FieldLength for field '{code}' must be a positive integer.* For Numeric: *must include both precision and scale (e.g., "10,2")*, *Invalid format for numeric field...*, or *precision must be > 0 and scale must be between 0 and precision*.
4. Ceilings that always apply: the Admin form accepts a Text setting up to 4000 and a Text Area setting up to 8000; Numeric precision and scale are at most 38. **There is no hard 4000 rejection for Text Area in the field validation:** a Text Area length above 4000 is created as unlimited text.
5. Suggested values to give a customer who wants limits: Text 500, TextArea 4000, Numeric `18,4` (an opinion, not a Znode default).
6. An older in-house note said the code rejects Text Area above 4000 and that blank settings fall back to 4000, 8000 and `38,38`. The product source does not do that (checked 2026-10-16): blank means no check.

## Field code, name and other field rules

| Property | Rule | Message |
|---|---|---|
| Field Code | required; max 100; letters and digits only; not all digits | *The Field Code is required.* · *Field Code can not exceed 100 characters.* · *Only alphanumeric characters are allowed.* |
| Field Code `Id` | reserved (case-insensitive) | *The field code 'ID' is reserved and cannot be used. Please choose a different code.* |
| Field Code duplicate in the table | refused (case-insensitive) | *Field Code Already Exist* |
| Field Name | required; max 100 | *The Field Name is required.* · *Field Name can not exceed 100 characters.* |
| Field Type | required; max 10 characters | *The Field Type is required.* · *The Field Type can not exceed 10 characters.* |
| Display Order | required, greater than 0 (Admin: 1 to 500) | *The Display Order is required.* · *Display order can not be less than one* · *Display Order should be between 1 and 500.* |

### Unique

| Rule | Detail |
|---|---|
| One unique field per table | *Multiple fields cannot be set as Unique.* |
| Allowed types | Text and Number in Admin; the Admin blocks Text Area, Boolean and Date And Time |
| Cannot be added once the table has rows | *The field cannot be added or modified with a UNIQUE constraint after data has been inserted into the custom table.* The Admin does not show this message: it silently saves the field with Is Unique off. |
| Can be turned off with data present | yes |
| Cannot be deleted while unique | *The field set as unique cannot be deleted.* (Admin) / *A unique field cannot be changed as data associated with the table.* (API). Remove the unique flag, then delete. |
| Unique value on a record | required: *FieldValue is required for Unique Field: {FieldCode}* and a unique numeric field cannot be 0 (*Input is required.*) |
| Long unique text | a unique text field longer than about 450 characters may be rejected by the database (key size) |

### What can change after save

| Property | Editable? |
|---|---|
| Field Code | No (the Admin locks it; the API does not stop it and it can corrupt data: do not) |
| Field Type | No (same) |
| Field Name | Yes |
| Field Length | Yes, within the ceilings; shrinking below existing data fails |
| Display Order | Yes |
| Is Unique | Yes, but locked in Admin and refused once the table has rows (turning it off is allowed) |

Deleting a field removes that column's data for every row, permanently. Deleting the last field empties the table (the structure and `Id` remain). A field code is free to reuse after deletion.

## Worked example

| Field code | Field name | Type | Length | Example |
|---|---|---|---|---|
| `StoreCode` | Store Code | `Text` (unique) | `50` | `LONDON01` |
| `StoreName` | Store Name | `Text` | `100` | `London Bridge` |
| `Notes` | Notes | `TextArea` | `500` | `Opens late on Thursdays` |
| `SeatCount` | Seat Count | `Numeric` | `10,0` | `48` |
| `FloorArea` | Floor Area | `Numeric` | `8,2` | `123.45` |
| `IsOpen` | Is Open | `Boolean` | none | `true` |
| `OpenedOn` | Opened On | `datetime` | none | `2026-01-31` |

Create fields with a JSON **array**, even for one field (see `api.md`).
