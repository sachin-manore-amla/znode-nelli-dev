# System Table List

> The System Table list was captured live. Menu path is **PIM > Product Info Overrides** (confirmed).
> On this int DB the grid is **empty - count `0`, "No records found."** - no system table is seeded.
> The **Filter** panel offers only the **Table Key / Table Name** columns and exactly four operators
> (**Contains, Is, Begins With, Ends With**). There are **no Tools or Columns dropdowns** on this
> screen (unlike the Custom Table list). See the embeds and Corrections below.
>
>
>

## 1. What it is

The system table list shows all system-defined tables in Znode. System tables are pre-defined tables that come with the platform and cannot be created or deleted by users. Currently, the only system table is "Product Information Overrides".

## 2. Where you do it

In the admin, go to **PIM > Product Information Overrides**. This opens the system table list grid.

The system table list is not available on the webstore, Commerce Portal, or B Store app. It can also be accessed via the API endpoint `GET v1/system-tables`.

## 3. Who can do it

Any admin user with access to the PIM menu can view the system table list. No additional permission is required beyond standard admin access.

## 4. Step by step

1. Log in to the admin.
2. Navigate to **PIM > Product Information Overrides**.
3. The grid shows all system tables with their names.
4. Use the paging, sorting, and filtering controls to find a specific table.
5. Click a table row to open its detail view.

## 5. What is allowed and what is not

- You **can** view the list of system tables and use sorting, filtering, and paging.
- You **cannot** add a new system table from this screen. There is no "Add" button.
- You **cannot** delete a system table from this screen. The toolbar has no delete option.
- You **cannot** perform any bulk actions. The tool menu is empty.

## 6. Messages you may see

No messages appear on this screen under normal use. The grid simply displays the list, or shows an empty grid if no system tables exist.

## 7. How it differs

System tables and custom tables share the same underlying database table, but they appear in different places:
- System tables are listed under **PIM > Product Information Overrides**.
- Custom tables are listed under **Dev Center > Custom Tables**.

The system table list has no create or delete actions, while the custom table list allows both.

## 8. What can be combined

There are no combination or stacking rules for the system table list. It is a simple read-only grid.

## 9. What it changes elsewhere

Viewing the system table list does not change anything. It is a read-only operation.

## 10. Quick answers

**Q: How many system tables exist?**
Currently only one: "Product Information Overrides" (ProductInformationOverrides).

**Q: Can I add a new system table?**
No. System tables are pre-defined by the platform. There is no create action in the admin or API.

**Q: Can I delete a system table?**
No. The admin has no delete option, and the API explicitly blocks deletion with the message "Deleting System Tables is not allowed".

**Q: Where is the system table list?**
PIM > Product Information Overrides in the admin.

**Q: Is there paging, sorting, and filtering?**
Yes. The grid supports all three through standard filter helpers.

**Q: Which API loads the list?**
`GET v1/system-tables`. The API automatically filters to show only system-defined tables.

**Q: Do system tables share the same database table as custom tables?**

## 11. For developers

See `03-frontend-admin.md` for the admin call tree, `06-api.md` for the API contract, `07-functions.md` for the service logic, and `08-database.md` for the database details.

## Fields and options

| Control | Options (verbatim) | Where the values come from |
|---|---|---|
| Filter > Select Column | `Select Column`, `Table Key`, `Table Name` | fixed grid-column list of the System Table list view |
| Filter > operator (after a column is chosen) | `Contains`, `Is`, `Begins With`, `Ends With` | shared Znode grid filter component - same four as the Custom Table list |
| Search... | free text | client-side quick filter over the loaded grid |

No SYSTEM VIEW, TOOLS or COLUMNS dropdowns are present (the System Table tool menu is empty - `SystemTableAgent.SetToolMenu`).

## Screenshot verification (2026-10-08)

| Screenshot | Shows | Result |
|---|---|---|
| `screenshots/01-admin-system-table-list.png` | Product Information Overrides list, count `0`, "No records found.", Filter + Search only | ✅ Verified |
| `screenshots/02-admin-filter-panel.png` | Filter panel: Select Column (Table Key / Table Name) and operators Contains / Is / Begins With / Ends With | ✅ Verified |

Path-only URL of the screen: `/SystemTable/List`.

## Corrections (2026-10-08)

| Previously documented | Live on int (2026-10-08) |
|---|---|
| (implied) grid has Tools / bulk and Columns controls like the Custom Table grid | 🔄 Updated: the System Table list has **only Filter and Search** - no Tools or Columns dropdown. |
