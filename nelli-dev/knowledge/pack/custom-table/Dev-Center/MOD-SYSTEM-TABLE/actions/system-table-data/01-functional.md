# System Table Data

> **Screenshot verification (2026-10-08, LOCAL admin).** Navigating directly to
> `/SystemTable/GetSystemTableDataList?tableKey=ProductInformationOverrides` rendered the page chrome
> and the data partial's **"No records found."** text. The full inline data grid (with Add Record,
> Import, Export, Download Template, bulk delete) loads inside the detail/edit view, which errors on
> this DB (the table is not seeded), so those controls are ⚠️ Not verifiable here. See `ISSUES-FOUND.md`.
>
>
>
> **🔄 Update (2026-10-08, INT admin).** On **INT** the inline data grid renders inside the detail
> view with **519,964 records** and the full toolbar (**MANAGE FIELDS, ADD A RECORD, Import,
> Export**). ✅ Verified live (viewed, not saved/created/deleted). The grid columns observed are:
> **Locale, PIM SKU, Store Code, Catalog Code, Account Code, Alt SKU, Alt Product Name, Alt Short
> Desc, Alt Long Desc, Action**. The local "No records found." state only reflects the un-seeded
> local DB.
>
>

## 1. What it is

System table data is the set of records stored in a system table. For the "Product Information Overrides" system table, each record represents an alternate product name, description, or SKU for a specific combination of SKU, store, account, and locale. You can add, edit, delete, import, and export data records.

## 2. Where you do it

In the admin, go to **PIM > Product Information Overrides**, click the system table to open it. The data grid loads inline on the edit view. From there you can:
- View and filter records in the grid
- Click **Add Record** to create a new row
- Click a row to edit it
- Select rows and use bulk delete
- Click **Export** to download all records as CSV
- Click **Import** to upload a CSV file of records
- Click **Download Template** to get a sample CSV

Not available on the webstore, Commerce Portal, or B Store app. Data can also be managed via the API endpoints under `v1/custom-table-data/`.

## 3. Who can do it

Any admin user with access to the PIM menu can view, add, edit, delete, import, and export system table data. No additional permission is required beyond standard admin access.

## 4. Step by step

### Adding a record
1. Open the system table detail view.
2. Click **Add Record**.
3. Fill in the fields (SKU, StoreCode, AccountCode, Locale, AltProductName, etc.).
4. Click **Save**. A success message confirms the creation.

### Editing a record
1. Click a row in the data grid to open it.
2. Edit the field values as needed.
3. Click **Save**. A success message confirms the update.

### Deleting a single record
1. Click the delete icon on a row.
2. Confirm the deletion in the dialog.
3. A success message confirms the deletion.

### Deleting multiple records
1. Select rows using checkboxes.
2. Click the bulk delete button.
3. Confirm in the dialog ("Ok" to proceed).
4. A success message confirms the deletion.

### Exporting data
1. Click **Export** on the system table detail view.
2. A CSV file downloads with all records.

### Importing data
1. Click **Import** on the system table detail view.
2. Optionally click **Download Template** to get the expected CSV format.
3. Upload a CSV file matching the template columns.
4. Click **Import**. The system processes the file and reports the result.

## 5. What is allowed and what is not

- You **can** add, edit, and delete records freely.
- You **can** bulk delete multiple selected records.
- You **can** import data from a CSV file.
- You **can** export all data to a CSV file.
- You **cannot** undo a deletion. Deleted records are permanently removed.
- Adding a record with duplicate key values (e.g. the same SKU + StoreCode + AccountCode + Locale combination, if a unique constraint exists) will fail with an error.

## 6. Messages you may see

| Message | When it appears | When it does not |
|---|---|---|
| Record creation success | After successfully creating a new record | When creation fails |
| Unique key constraint error | When adding a record that duplicates an existing key combination | When the key combination is unique |
| Failed to create | On a general creation error | On success |
| Record saved success | After successfully editing a record | When edit fails |
| Failed to update | On a general edit error | On success |
| Delete success | After successfully deleting a record | When deletion fails |
| Delete error | When deletion fails or parameters are invalid | On success |

## 7. How it differs

System table data and custom table data use the **same API endpoints** and **same service code**. There is no difference in how data is handled. The only visual differences are:
- System table data is accessed from PIM > Product Information Overrides.
- Custom table data is accessed from Dev Center > Custom Tables.
- The grid filter cookie uses a `ZnodeSystemTableData_` prefix for system tables.

## 8. What can be combined

There are no combination or stacking rules for data records. Each record stands independently.

## 9. What it changes elsewhere

- Adding or editing product override records may affect how products display in the webstore, depending on whether the "Enable Product Information Overrides" runtime setting is active.
- If no override record exists for a product's SKU/store/account/locale combination, Znode falls back to the base product data.
- The override data is consumed at product display time, not at the point of editing the system table.

## 10. Quick answers

**Q: Can I add records to a system table?**
Yes. Adding records works the same as for custom tables.

**Q: Can I delete records from a system table?**
Yes. Both single and bulk delete are available. Deletion is permanent.

**Q: Can I import data from a CSV file?**
Yes. Download the template first to get the correct column format, then upload your CSV.

**Q: What format does the export use?**
CSV.

**Q: What happens if I import a duplicate record?**
If the table has a unique key constraint, the import will report an error for that row.

**Q: Does editing override data take effect immediately?**
It depends on the runtime configuration. The override data is stored immediately, but whether it is consumed at product display depends on the "Enable Product Information Overrides" setting.

**Q: Is the data stored as columns or as key-value pairs?**

**Q: What fields are available for ProductInformationOverrides?**
Confirmed live on INT (2026-10-08), the data grid columns are: **Locale, SKU (shown as "PIM SKU"), StoreCode, CatalogCode, AccountCode, AltSKU, AltProductName, AltShortDescription, AltLongDescription**. (An earlier draft listed "ElasticSearchEvent" and omitted "CatalogCode" — that was wrong; see Corrections.)

**Q: Are there any limits on how many records I can add?**
No specific limit beyond database capacity. The import has no documented maximum row or file size limit specific to system tables.

## 11. For developers

See `03-frontend-admin.md` for the admin call tree, `06-api.md` for the API contract, `07-functions.md` for the service logic, and `08-database.md` for the database details.

## Fields and options

| Data grid aspect | Value | Where it comes from |
|---|---|---|
| Record columns | Locale, PIM SKU, Store Code, Catalog Code, Account Code, Alt SKU, Alt Product Name, Alt Short Desc, Alt Long Desc, Action (confirmed live on INT) | the Product Information Overrides field definitions |
| Empty-grid text | `No records found.` | shared Znode grid component (confirmed live on local) |
| Record count (INT) | `519964 records found.` | the live `ProductInformationOverrides` data on INT |
| Row actions / toolbar | MANAGE FIELDS, ADD A RECORD, Import, Export (✅ Verified live on INT); per-row View / Edit / Delete and bulk Delete | the detail/edit view |

## Screenshot verification (2026-10-08)

| Screenshot | Shows | Result |
|---|---|---|
| `screenshots/01-admin-data-no-records.png` | the data-list partial rendering "No records found." (local DB) | ✅ Verified (empty state) |
| `screenshots/01-admin-system-table-data-grid-populated.png` | INT: the populated data grid (519,964 records) inside the detail view, with the MANAGE FIELDS / ADD A RECORD / Import / Export toolbar and all 9 data columns | 🔄 Updated: populated grid + toolbar now **✅ Verified** live on INT (viewed, not mutated) |

Path-only URL of the screen: `/SystemTable/EditSystemTable?TableKey={tableKey}` (grid loads inline); the data partial is `/SystemTable/GetSystemTableDataList?tableKey={tableKey}`.

## Corrections (2026-10-08)

| Previously documented | Live on INT (2026-10-08) |
|---|---|
| Populated grid and toolbar "⚠️ Not verifiable - the parent edit view errors on this DB" | 🔄 Updated: that was a local-DB limitation. On **INT** the grid renders with 519,964 records and the toolbar (MANAGE FIELDS, ADD A RECORD, Import, Export) — ✅ Verified. |
| FAQ listed data fields as "…AltLongDescription, and **ElasticSearchEvent**" and omitted CatalogCode | 🔄 Updated: INT data columns are Locale, PIM SKU, Store Code, **Catalog Code**, Account Code, Alt SKU, Alt Product Name, Alt Short Desc, Alt Long Desc; there is no "ElasticSearchEvent" column in the grid. |
