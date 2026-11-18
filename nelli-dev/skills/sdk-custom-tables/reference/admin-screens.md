# Dev Center screens, step by step

What this answers: where each custom table action lives in Admin, the exact steps and labels, the quirks, and who can do what.

KB paths (as documented): Dev Center > Custom Tables > Add New / Manage Field > Add Custom Fields / Edit Custom Table > Add a Record / Import / Export. Admin Console, Znode V10.

## 1. The list: Dev Center > Custom Tables

| Element | Notes |
|---|---|
| Heading | "CUSTOM TABLES" with the total count |
| Add New | opens the create form |
| Columns | Table Key, Table Name, Created Date, Last Updated, Action |
| Row actions | Edit, Delete (behind the Manage icon) |
| Bulk actions | tick rows, open the bulk dropdown, Delete |
| Grid features | System View picker, Columns picker, saved filters, page sizes 10, 25, 50, 100 (shared Admin grid features) |

System tables are **not listed here** (filtered out). Find them through the system-tables API or the feature that owns them.

## 2. Create a table

1. Dev Center > Custom Tables > **Add New**.
2. Enter **Table Key** (required, starts with a letter, letters and digits, max 100) and **Table Name** (required, max 100).
3. Click **Save & Close** (the visible primary button) or **Save** (inside the caret dropdown). The table exists now.
4. **Manage Fields** is disabled until the table is saved.

Messages: *The Table Key field is required.* · *Table Key can not exceed 100 characters.* · *The Table Key must start with a letter and contain only alphanumeric characters (A-Z, a-z, 0-9). Spaces and special characters are not allowed.* · *The Table Name field is required.* · *Table Name can not exceed 100 characters.* · *The Table Name must start with a letter and can contain only alphanumeric characters, spaces between words, underscores, and hyphens.* · *Table Key Already Exist* (case-insensitive) · *Record created successfully.*

Admin URL trap for anyone deep-linking: the working pages are `/CustomTable/List`, `/CustomTable/CreateCustomTable`, `/CustomTable/EditCustomTable?TableKey=<key>`, `/CustomTable/CustomTableFieldList?tableKey=<key>`, `/CustomTable/GetCustomTableDataList?tableKey=<key>`. `/CustomTable/Create` is a 404. Reach Edit by clicking through from the list (it can redirect if you arrive directly).

## 3. Rename a table

Edit (row action), change **Table Name**, Save & Close. The Table Key box is read-only. *Record updated successfully.* appears after any save of the form, even when the back end failed, so confirm the new name on the list.

## 4. Manage fields: Dev Center > Custom Tables > Manage Fields

1. A table with no fields already shows **one blank editable row**. Fill it. Clicking Add Custom Field first leaves the blank row behind and the save fails with *Field Code is required.*
2. Each row: Field Type (dropdown), Field Code, Field Name, Is Unique (Yes/No), Field Length (default 50), Display Order (default 500).
3. **Save & Close.** After saving you stay on the Manage Fields page (since 10.12.1.0).
4. Saved fields: Field Type and Field Code are read-only; Is Unique is locked once the table has rows.
5. Delete a field with the row's delete control: it removes the column and its data. No bulk delete for fields.

Dropdown labels and the values they send: Text -> `Text`, Text Area -> `TextArea`, **Number -> `Numeric`**, Boolean -> `Boolean`, Date And Time -> `datetime`. The whole-number `Number` type is not offered.

## 5. Records

**Add:** Edit Custom Table > **Add a Record**. The form has one input per field named after the Field Code. Save & Close. Messages: *Record created successfully.* · *A record with this unique key already exists. Please ensure that the value entered for the unique key column is distinct.* · *Failed to create.* · *You cannot save an empty record. Please enter a value in at least one field before saving.* Admin form specifics: Number inputs reject negatives and decimals; Boolean is a Yes/No dropdown; client-side messages for length (*Input cannot exceed the maximum character limit of N.*) and numeric range.

If the table has no unique field, clicking Add a Record or Import shows a **Note** popup about needing a unique field. Whether it blocks or only warns on your version: check on screen.

**Edit:** the row list > edit link. *Record saved successfully.* After saving you land on the Edit Table screen, not the row list.

**Delete:** a row's delete control (grid confirm) or tick rows and use bulk Delete (*Are you sure you want to delete the selected record(s)?*). *Please select at least one record.* if none ticked.

## 6. Delete a table

Two paths with different friction:

| Path | Confirmation |
|---|---|
| Row action menu > Delete | the ordinary grid confirm |
| Tick rows > bulk dropdown > Delete | a dialog: *The selected table(s) may have data associated with it. Proceeding with this action will delete the table and its associated data (if any). To confirm the deletion, please type 'Delete' in the text box below:* Type `delete` (any casing). Anything else: *Invalid keyword entered, please try again.* |

Results: *Record deleted successfully.* · *Failed to delete the record.* **Deleting a table deletes its data. No undo, no reference check.**

## 7. Import and export (on the Edit Custom Table screen)

See `import-export.md`. Import panel: Download Template, choose a `.csv`, Import, then View Import Logs. Export queues a background export; download it from the Export screen (Dev Center > Export, type Custom Table).

## 8. Who can do it

| Actor | Access |
|---|---|
| Admin user | needs the Dev Center > Custom Tables menu role. Toolbar buttons also depend on permissions: the list permission, **Create Custom Table** (Add New), and the bulk delete action. No role: the menu item is hidden. |
| API caller | any authenticated caller (Basic or JWT through the gateway) can run every operation. No role or ownership check. |
| Webstore, Commerce Portal, B Store users | no screen or action |

## 9. Behind the screens

Every Admin action calls the same API as in `api.md`: list -> `GET /v1/custom-tables`, save -> `POST` or `PUT`, fields -> `/v1/custom-table-fields`, rows -> `/v1/custom-table-data`. If the gateway or the service is down, the Admin shows an empty or failed screen rather than a clear error.

## Sources

KB Managing Custom Tables (43000757107); product behaviour verified on a development environment and in source (2026-10); release notes 10.12.1.0, 10.13.0.0, 10.14.0.0, 10.14.0.6 (https://support.znode.com/support/search?term=custom+table).
