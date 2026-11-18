# Open a Custom Table

> **Screenshots for this action (previously captured in an earlier pass; corroborated by INT facts 2026-10-08, admin store Amla, v10.14.4.0):**
>

## 1. What it is

Opening a custom table shows its details and its data on one screen. The page displays the table's key (which cannot be changed) and its name (which can be edited), along with buttons to manage fields, add records, import data and export data. The table's data rows load automatically in a grid below.

## 2. Where you do it

- **Admin:** Dev Center > Custom Tables > click the **Edit** (pencil) icon on a table row.
- **Webstore:** Not available.
- **Commerce Portal:** Not available.
- **B Store:** Not available.
- **API:** GET a single table's details by its table key. A second call checks whether the table has any data rows.

## 3. Who can do it

Any admin user who has access to the Custom Tables section under Dev Center can open a table. There are no role-based restrictions beyond menu access.

## 4. Step by step

1. Go to **Dev Center > Custom Tables**. The list of custom tables appears.
2. Click the **Edit** icon on the row for the table you want to open.
3. The edit page loads. It shows:
 - **Table Key** — the unique identifier set when the table was created; it cannot be changed. On a custom table the input may render as an enabled text box (it is read-only/disabled only for system tables), but any edit is ignored by the API.
 - **Table Name** in an editable field.
4. Below the name, four buttons appear:
 - **Manage Fields** — opens a separate page where you add, edit or remove columns.
 - **Add Record** — takes you to the page for adding a new data row.
 - **Import** — opens the import dialog.
 - **Export** — starts an export of the table's data.
5. The data grid loads automatically at the bottom, showing the table's existing rows. The grid supports pagination.

## 5. What is allowed and what is not

- The table key cannot be changed after the table is created. On a custom table the input may render enabled (read-only/disabled only for system tables), but the API copies the route key back and ignores any edit — the key is immutable.
- If the table has no fields defined yet (no columns), clicking **Add Record** or **Import** shows a popup note instead of navigating. The note tells you to add at least one unique field before adding records. Click OK and you are taken to the appropriate page.
- System-defined tables (used internally by Znode) are not returned when you look up a custom table by key. They are managed separately under System Tables.

## 6. Messages you may see

| Message | When it appears | When it does not appear |
|---|---|---|
| Popup "Note" with a description about needing a unique field | When you click Add Record or Import and the table has no fields (or no data rows yet) | When the table already has fields and records |
| "Key not found" error | When the table key in the URL does not match any custom table | When the key is valid |

## 7. How it differs

- **Custom tables vs. system tables:** The edit page only shows custom tables (not system-defined ones). System tables have their own separate endpoint and screen.
- **Tables with fields vs. without:** If no fields have been added yet, the Add Record and Import buttons are guarded by a popup warning. The Export button and the data grid still appear but will show nothing.

## 8. What can be combined

This is a read-only page load. It does not interact with other features like promotions, coupons or user management.

## 9. What it changes elsewhere

Opening a table changes nothing. It is a read-only operation. The only side effect is that the API response may be cached for subsequent requests.

## 10. Quick answers

**Q: Can I change the table key on the edit page?**
No. The table key field is read-only. It is set once when the table is created.

**Q: Are fields shown on the same page as records?**
The edit page shows the records grid and buttons. Fields are managed on a separate page reached via the Manage Fields button.

**Q: What happens if I open a table that does not exist?**
The API returns a "Key not found" error (404). The admin shows an error notification.

**Q: Does opening a table update any timestamp?**
No. This is a read-only operation. No timestamps are changed.

**Q: What does the "record exists" check do?**
It checks whether the physical database table for this custom table has at least one data row. The result controls whether the Add Record and Import buttons work directly or show a warning popup first.

**Q: Can I open a system table from the custom tables screen?**
No. System tables are filtered out by the API. They have their own separate endpoint and admin page.

**Q: How does the data grid load?**
It loads via an automatic background request (AJAX) as soon as the page opens. It is a separate call from the two API calls that fetch the table metadata and the record-exists flag.

## 11. For developers

See the technical files in this folder:
- `03-frontend-admin.md` — admin screen, call tree, view model
- `06-api.md` — API contracts for GET table and GET record-exists
- `07-functions.md` — every back-end method, line by line
- `08-database.md` — tables read, queries executed

---

## Screenshot verification (2026-10-08)

The screenshot was captured in an earlier pass and is not re-captured here; it is corroborated against the verified INT facts (admin store Amla, v10.14.4.0, 2026-10-08).

| Screenshot | Shows | Status |
|---|---|---|
| 01-admin-open-table-detail.png | Edit screen: heading "Table Key {tableKey}", General Information (Table Key, Table Name), Custom Table Data with a MANAGE FIELDS button, Save & Close / Back | ✅ Verified — Edit screen layout, headings and MANAGE FIELDS match INT |

Path-only URL: `/CustomTable/EditCustomTable?TableKey={tableKey}`

## Fields and options

| Field / control | Type | Editable | Behaviour | Notes |
|---|---|---|---|---|
| Table Key | text box | Renders enabled on custom tables, but **immutable** 🔄 | identifies the table; cannot be changed (API copies the route key back) | read-only/disabled input only for **system** tables; editing has no effect (see Corrections + `06-api.md`) |
| Table Name | text box | Yes | display name | starting value from the GET response |
| MANAGE FIELDS | button | — | → `/CustomTable/CustomTableFieldList?tableKey={tableKey}` | add/edit/remove columns |
| Add Record | button | — | add a data row (guarded by a "Note" popup when the table has no fields) | hidden until applicable |
| Import | button | — | open the import dialog (same "Note" guard) | |
| Export | button | — | export the table's data | blocked with "No Data Available to Export." when empty |
| Save & Close | button | — | save and return to the list | |
| Back | button | — | → `/CustomTable/List` | |

## Corrections (2026-10-08)

| Item | Was documented as | Verified on INT (2026-10-08) | Mark |
|---|---|---|---|
| Table Key control state on the Edit screen | "always read-only" (implied the input is disabled) | On a **custom** table the Table Key renders as an **enabled** input (read-only/disabled only for **system** tables) | 🔄 Updated |
| Whether the Table Key can actually be changed | n/a | **No** — immutable. The custom-table input renders enabled, but the API copies the key from the URL back onto the record and ignores any edit (`06-api.md`, `07-functions.md`, ISSUES-FOUND #6). | ✅ Verified |
