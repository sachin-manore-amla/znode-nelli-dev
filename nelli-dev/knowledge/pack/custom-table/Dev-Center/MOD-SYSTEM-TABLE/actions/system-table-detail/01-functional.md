# System Table Detail

> **Screenshot verification (2026-10-08, LOCAL admin).** Opening the detail at
> `/SystemTable/EditSystemTable?tableKey=ProductInformationOverrides` returned **"A generic error
> occurred."** on this int DB, because the `ProductInformationOverrides` definition is **not seeded**
> (the list is empty). The detail form itself could **not** be reached live; the captured screenshot
> is the error state. ⚠️ Not verifiable: the editable Table Name form and the Manage Fields / Data
> buttons. See Corrections and `Dev-Center/ISSUES-FOUND.md`.
>
>
>
> v10.14.4.0) the `ProductInformationOverrides` row **is** seeded, so the detail screen renders
> fully: the read-only **Table Key** field, the editable **Table Name** ("Product Information
> Overrides"), the **MANAGE FIELDS / ADD A RECORD / Import / Export** buttons, the four Important
> Notes, and the inline data grid (519,964 records). The editable Table Name form and the buttons
> are therefore **✅ Verified** on INT (read-only, not saved). The local "generic error" state only
> reproduces where the row is absent.
>
>

## 1. What it is

The system table detail screen shows the metadata of a single system table and lets you rename its display name. It also provides access to the table's fields, data grid, import, and export.

## 2. Where you do it

In the admin, open **PIM > Product Information Overrides**, then click on a table row. This opens the detail screen at `/SystemTable/EditSystemTable?tableKey=ProductInformationOverrides`.

Not available on the webstore, Commerce Portal, or B Store app. The API equivalents are `GET v1/system-tables/{tableKey}` and `PUT v1/system-tables/{tableKey}`.

## 3. Who can do it

Any admin user with access to the PIM menu can view and edit the system table detail.

## 4. Step by step

### Viewing

1. Navigate to **PIM > Product Information Overrides**.
2. Click on a system table row.
3. The detail screen shows the table name, table key, description, and buttons for managing fields, data, import, and export.

### Renaming the display name

1. On the detail screen, change the Table Name field.
2. Click Save.
3. A success message appears: "Record updated successfully."
4. The table key cannot be changed — it stays the same even if you type a different value.

## 5. What is allowed and what is not

- You **can** change the display name (Table Name) of a system table.
- You **cannot** change the table key (the machine-readable identifier). The system silently ignores any change to this field.
- You **can** access the fields list, data grid, import, and export from this screen via buttons.

## 6. Messages you may see

| Message | When it appears | When it does not |
|---|---|---|
| "Record updated successfully" | After saving a valid name change | When save fails |
| "Failed to update" | When the save operation fails (API error) | When save succeeds |
| "The requested table does not exist" | When navigating to an invalid table key | When the table key is valid |
| "Id cannot be less than 1" | When the API receives a table ID of 0 or negative | Normal use |

## 7. How it differs

The system table detail screen is very similar to the custom table detail screen, with one key difference: the table key cannot be changed for system tables. For custom tables, both the name and key can be updated.

## 8. What can be combined

No combination or stacking rules apply.

## 9. What it changes elsewhere

Renaming a system table's display name updates the name shown in the list grid. It does not affect the physical table, the table key, the fields, or the data.

## 10. Quick answers

**Q: Can I rename a system table's key?**
No. Only the display name (Table Name) can be changed. The table key is protected and cannot be modified through the admin or API.

**Q: What tabs or sections does the detail screen have?**
The detail screen shows the metadata (name, key, description) and provides buttons for Manage Fields, Add Record, Import, and Export. The data grid is loaded inline on the same page.

**Q: What happens if I navigate to an invalid table key?**
You get a "The requested table does not exist" error.

**Q: Which APIs does the admin call?**
`GET v1/system-tables/{tableKey}` for metadata, `GET v1/custom-tables/{tableKey}/record-exists` for the record check, and `PUT v1/system-tables/{tableKey}` to save.

## 11. For developers

See `03-frontend-admin.md`, `06-api.md`, `07-functions.md`, `08-database.md`.

## Fields and options

| Field | Editable | Where the value comes from |
|---|---|---|

These are documented from the verified code (06-api.md / 07-functions.md); the form could not be rendered live because the row is missing on this DB.

## Screenshot verification (2026-10-08)

| Screenshot | Shows | Result |
|---|---|---|
| `screenshots/01-admin-detail-generic-error.png` | `/SystemTable/EditSystemTable?tableKey=ProductInformationOverrides` returns "A generic error occurred." (local DB, row absent) | ✅ Verified (error reproduced where the row is missing) |
| `screenshots/01-admin-system-table-detail-with-data-grid.png` | INT: the detail form (read-only Table Key, editable Table Name, MANAGE FIELDS / ADD A RECORD / Import / Export, Important Notes, inline data grid of 519,964 records) | 🔄 Updated: detail form and buttons now **✅ Verified** live on INT (viewed, not saved) |

Path-only URL of the screen: `/SystemTable/EditSystemTable?TableKey={tableKey}`.

## Corrections (2026-10-08)

| Previously documented | Live on int (2026-10-08) |
|---|---|
| Detail form renders the table name/key and the Manage Fields / Data buttons | 🔄 Updated: the local DB used in the first pass lacked the `ProductInformationOverrides` row, so the route returned **"A generic error occurred."** On **INT** the row exists and the detail form renders fully (read-only Table Key, editable Table Name, MANAGE FIELDS / ADD A RECORD / Import / Export, Important Notes, 519,964-record grid) — **✅ Verified** on INT 2026-10-08. |
| Local pass described the screen only from code | 🔄 Updated: INT confirms the Table Key field is **read-only** (`readonly` attribute) and the Table Name is editable, matching the code (the API skips key writes for system tables). |
