# System Table Fields

> **Screenshot verification (2026-10-08, LOCAL admin).** Opening the field list at
> `/SystemTable/SystemTableFieldList?tableKey=ProductInformationOverrides` returned **"A generic
> error occurred."** on this int DB, for the same reason as the detail screen - the system table is
> not seeded. ⚠️ Not verifiable: the field grid (field code / display name / data type / length /
> display order). The captured screenshot is the error state. See Corrections and `ISSUES-FOUND.md`.
>
>
>
> **🔄 Update (2026-10-08, INT admin).** On **INT** the field grid renders. It lists **9 fields**,
> all **`Text`** type, all with the **Field Code read-only** and **Field Length read-only**, and
> **no "Add Custom Field" button** — confirming system-table fields cannot be added or modified from
> the admin. ✅ Verified live (viewed, not saved). The fields in display order are: Locale (len 50),
> SKU / "PIM SKU" (50), StoreCode / "Store Code" (100), CatalogCode / "Catalog Code" (100),
> AccountCode / "Account Code" (100), AltSKU / "Alt SKU" (50), AltProductName / "Alt Product Name"
> (100), AltShortDescription / "Alt Short Desc" (300), AltLongDescription / "Alt Long Desc" (500).
>
>

## 1. What it is

The system table fields screen lets you view and edit the field display names and display order for a system table's columns. The underlying column names, data types, and lengths cannot be changed because system tables are platform-defined.

## 2. Where you do it

In the admin, go to **PIM > Product Information Overrides**, click a system table to open it, then click the **Manage Fields** button. This opens the field list at `/SystemTable/SystemTableFieldList?tableKey=ProductInformationOverrides`.

Not available on the webstore, Commerce Portal, or B Store app. The fields can also be read via the API endpoint `GET v1/custom-table-fields/{tableKey}`.

## 3. Who can do it

Any admin user with access to the PIM menu can view and edit system table field display names. No additional permission is required beyond standard admin access.

## 4. Step by step

1. Log in to the admin.
2. Navigate to **PIM > Product Information Overrides**.
3. Click the system table row to open its detail view.
4. Click **Manage Fields**.
5. The field grid shows all columns: field code (read-only), display name (editable), data type (shown), max length (shown), and display order (editable).
6. Edit the display name or display order as needed.
7. Click **Save**. A success message confirms the update.

## 5. What is allowed and what is not

- You **can** change a field's display name (the label shown in the admin grid and forms).
- You **can** change a field's display order (the order columns appear in the grid).
- You **cannot** add a new field to a system table through the admin. The admin does not expose add-field for system tables.
- You **cannot** delete a field from a system table through the admin. The admin does not expose delete-field for system tables.
- You **cannot** change a field's data type or maximum length. These are defined by the database schema and are read-only in the admin.
- You **cannot** rename the underlying database column name (field code). Only the display name can be changed.

**Important**: At the API level, there is no restriction on adding or deleting fields for system tables. The field APIs (`v1/custom-table-fields`) do not check whether the table is system-defined. The restrictions above are enforced only by the admin interface.

## 6. Messages you may see

| Message | When it appears | When it does not |
|---|---|---|
| Update success message | After saving field edits successfully | When no changes are made |
| Error message from API | When the save fails (e.g. validation error) | On successful save |

## 7. How it differs

System table fields and custom table fields use the **same API endpoints** (`v1/custom-table-fields`). The difference is only in the admin:
- System tables route through `SystemTableController` under PIM > Product Information Overrides.
- Custom tables route through `CustomTableController` under Dev Center > Custom Tables.
- The admin may hide the add/delete field controls for system tables, but the API does not enforce this.

## 8. What can be combined

There are no combination or stacking rules for field management. Each field's display name and display order are independent.

## 9. What it changes elsewhere

- Changing a field's display name affects how the column header appears in the data grid and in import/export templates.
- Changing display order affects the column order in the data grid.
- Neither change affects the actual data stored in the table or how products use override values at runtime.

## 10. Quick answers

**Q: Can I add a new field to a system table?**
Not through the admin. The admin does not expose an add-field action for system tables. However, the API does not block it.

**Q: Can I delete a field from a system table?**
Not through the admin. The admin does not expose a delete-field action. The API does not block it either.

**Q: What can I change on a system table field?**
Only the display name and display order.

**Q: Are system table fields different from custom table fields at the API level?**
No. The same API routes (`v1/custom-table-fields`) handle both. There is no system-vs-custom check.

**Q: What fields does ProductInformationOverrides have?**
Nine fields, confirmed live on INT (2026-10-08): **Locale, SKU (display name "PIM SKU"), StoreCode, CatalogCode, AccountCode, AltSKU, AltProductName, AltShortDescription, AltLongDescription** — all `Text` type, all read-only in the admin. (An earlier draft of this file listed "ElasticSearchEvent" as a field and omitted "CatalogCode"; that was wrong — see Corrections.)

**Q: Does changing a field display name affect the data?**
No. It only changes the label shown in the admin. The underlying column name and data remain unchanged.

**Q: Is there a maximum number of fields?**
Not specific to system tables. The limit comes from the underlying database table column limits.

**Q: What happens if I set a display name to blank?**
The field API's validation rules apply (shared with custom tables).

## 11. For developers

See `03-frontend-admin.md` for the admin call tree, `06-api.md` for the API contract, `07-functions.md` for the service logic, and `08-database.md` for the database details.

## Fields and options

| Grid column | Editable | Live on INT (2026-10-08) | Where the value comes from |
|---|---|---|---|
| Field Type | No (locked) | Single option only, `Text`, for every field | fixed field type of the column |
| Field Name | Yes (editable input) | "PIM SKU", "Store Code", "Catalog Code", "Account Code", "Alt SKU", "Alt Product Name", "Alt Short Desc", "Alt Long Desc" | field display name |
| Is Unique | Dropdown (true/false) | `false` for every field | field unique-constraint flag |
| Field Length | No (read-only input) | 50 / 50 / 100 / 100 / 100 / 50 / 100 / 300 / 500 | field length / precision-scale |
| Display Order | Yes (editable input) | 1–9 (Locale=1 … AltLongDescription=9) | field display order |
| Action | — | **No row actions and no "Add Custom Field" button** | admin disables add/edit/delete for system tables |

Verified live on INT; the field-type dropdown carries only the current type as its sole option, and the Field Code / Field Length inputs are read-only.

## Screenshot verification (2026-10-08)

| Screenshot | Shows | Result |
|---|---|---|
| `screenshots/01-admin-fields-generic-error.png` | `/SystemTable/SystemTableFieldList?tableKey=ProductInformationOverrides` returns "A generic error occurred." (local DB, row absent) | ✅ Verified (error reproduced where the row is missing) |
| `screenshots/01-admin-system-table-fields-readonly.png` | INT: the 9-field grid, all `Text`, Field Code and Field Length read-only, Field Type locked to one option, Field Name and Display Order editable, no Add Custom Field button | 🔄 Updated: field grid now **✅ Verified** live on INT (viewed, not saved) |

Path-only URL of the screen: `/SystemTable/SystemTableFieldList?tableKey={tableKey}`.

## Corrections (2026-10-08)

| Previously documented | Live on int (2026-10-08) |
|---|---|
| Field grid renders the system table's columns | 🔄 Updated: the first pass hit a local DB without the `ProductInformationOverrides` row, so the route returned **"A generic error occurred."** On **INT** the grid renders and was ✅ Verified. |
| FAQ listed the fields as "…AltLongDescription, and **ElasticSearchEvent**" and omitted CatalogCode | 🔄 Updated: INT shows **9** managed fields including **CatalogCode** (display order 4); there is **no "ElasticSearchEvent" field** in the managed field grid. The FAQ has been corrected. |
| Field grid described without edit/lock state | 🔄 Updated: INT confirms Field Type is locked (single option), Field Code and Field Length are read-only, Field Name and Display Order are editable, and there is **no Add Custom Field button** for system tables — matching the admin restriction. |
