# Record grid — Functional

> **Screenshots (2026-10-08).** Captures of the record grid (previously captured in an earlier pass).
>
>

## 1. What it is

The record grid displays all data rows stored in a custom table. It is the main view for browsing, sorting, filtering and paging through custom table records. From this grid you can add, edit and delete records.

## 2. Where you do it

- **Admin**: Dev Center > Custom Tables > open a table > Data tab. The grid loads automatically.
- **Webstore**: Not available.
- **Commerce Portal**: Not available.
- **B Store**: Not available.
- **API**: Records can be retrieved directly through the Custom Table API without the admin interface.

## 3. Who can do it

Any admin user who can access the Dev Center > Custom Tables menu can view the record grid. There is no record-level or field-level permission check — if you can open the table, you can see all its data. API consumers need a valid Znode API authentication token.

## 4. Step by step

1. Navigate to Dev Center > Custom Tables in the admin.
2. Click Edit on a table row.
3. The Data tab loads automatically, showing the record grid.
4. The grid displays one column per field defined on the table, ordered by each field's Display Order.
5. Use the paging controls at the bottom to navigate through pages (default page size is 10).
6. Click a column header to sort by that column.
7. Use the filter controls to narrow down records.
8. From the grid, each row's Action column has three icons (confirmed live, int, 2026-10-05 - not
 previously documented): a **View** (eye) icon that opens a read-only "RECORD DETAILS" popup
 listing every field and its value with only a Back button (no edit controls); an **Edit**
 (pencil) icon that opens the full edit form (see `../edit-record/01-functional.md`); and a
 **Delete** (trash) icon for single-record delete. Select multiple rows via checkboxes and use the
 toolbar Delete button for bulk delete. See `screenshots/01-admin-record-details-view.png`.

## 5. What is allowed and what is not

- Any admin user with access to the Dev Center > Custom Tables menu can view the grid. There is no separate permission for viewing records.
- The internal row Id column is hidden from the grid.
- Column headers show the field's display name, not the field code.
- Boolean values are shown as "Yes" or "No".
- DateTime values are shown as returned by the API, with no special formatting.
- Number values are shown as returned by the API, with no special formatting.
- Any column name can be used for sorting. Sorting by a column name that does not exist on the table causes an error.
- Any column name can be used in a filter. Filtering by a column name that does not exist causes an error.

## 6. Messages you may see

| Message | When it appears | When it does not |
|---|---|---|
| "No records found." (confirmed live, int, 2026-10-05 - corrected; previously documented as an empty grid with no message) | The table has no records | The table has at least one record. See `screenshots/02-admin-empty-grid-no-records-found.png` |
| "The requested table does not exist" | The table key in the URL does not match any table | The table key is valid |
| "Model cannot be null." | The table key is empty | A table key is provided |

## 7. How it differs

- The grid content depends entirely on which fields are defined on the table. Each table has its own set of columns.
- The default sort is by the internal Id column in ascending order.
- The default page size is 10 records.
- When the page number exceeds the total number of pages, the grid shows an empty result (no error).

## 8. What can be combined

Not applicable. The record grid is a read-only view.

## 9. What it changes elsewhere

Viewing the record grid does not change anything. It is a read-only operation. No audit log entry is created for viewing records.

## 10. Quick answers

**Q: Which columns does the grid show?**
All custom fields defined on the table, ordered by Display Order. The internal row Id is hidden.

**Q: What are the column headers — field codes or display names?**
Display names (the human-readable name, not the internal code).

**Q: How are Boolean values shown?**
As "Yes" or "No".

**Q: What is the default page size?**
10 records per page.

**Q: What is the default sort?**
By the internal Id column, ascending.

**Q: Can I sort by any column?**
Yes. Sorting by a non-existent column causes a server error.

**Q: Can I filter by any column?**
Yes, using standard Znode filter operators (equals, not equals, contains, starts with, ends with, greater than, less than, and others).

**Q: What happens when the table has zero records?**
The grid shows empty — no error message.

**Q: What happens when pageIndex exceeds the total pages?**
An empty result is returned (no error).

**Q: Is there a performance limit on the number of records?**
No hard limit is enforced. The grid uses server-side paging, so only one page of records is loaded at a time.

**Q: Are records cached?**
The API may cache results, but every grid load triggers a fresh call from the admin to the API.

**Q: Can the grid be accessed directly by URL?**
Yes, using the pattern `/CustomTable/GetCustomTableDataList?tableKey={tableKey}`.

**Q: What APIs are there to retrieve records?**
Five endpoints: (1) GET records with field metadata (paged), (2) GET one row by id, (3) GET records alias (no /records suffix), (4) GET one row by id alias (/rows/{rowId}), (5) GET rows by unique-field value.

**Q: What status codes does the list API return?**
200 with data, 204 when empty, 400 for bad requests (empty table key), 404 when the table does not exist, 500 for server errors (e.g. invalid filter column).

**Q: What does the get-by-id API return when the row does not exist?**
A 404 error with the message "No records were found for the requested row id."

**Q: What does the get-by-id API return when the row id is less than 1?**
A 404 error with the message "Id cannot be less than 1."

## 11. For developers

See `03-frontend-admin.md` for the admin screen, call tree and selectors; `06-api.md` for all five API endpoints with curls and data maps; `07-functions.md` for the back-end workflow and service logic; `08-database.md` for the dynamic SQL and table structure.

## Fields and options

Record grid as verified live on INT (store Amla, example table `testabhi`, fields name / Number / Address, TableId 90):

| Element | What it shows / does | Verified source |
|---|---|---|
| Grid columns | One column per table field (for `testabhi`: name, Number, Address) plus an Action column | INT grid capture |
| Record rows | Each data row (e.g. Alex / 1 / Texas, Id 3; Divi / 23 / Delhi, Id 4); internal Id hidden from the column set | INT grid capture |
| View (eye) action | Opens read-only "RECORD DETAILS" popup, Back only — `/CustomTable/GetCustomTableData?TableKey={tableKey}&Id={id}` | INT grid capture |
| Edit (pencil) action | Opens the edit form — `/CustomTable/EditCustomTableData?TableKey={tableKey}&Id={id}` | INT grid capture |
| Delete (trash) action | Opens the delete confirmation (`#PopUpConfirm`) | INT grid capture |
| Toolbar | Filter, Search box, Columns, Tools, System View | INT grid capture |
| Paging | Show 10 / 20 / 50 / 100; footer "Showing 1 - 2 of 2" | INT grid capture |
| Empty state | Grid body shows "No records found." when the table has no rows | INT empty-grid capture |

## Screenshot verification (2026-10-08)

| Screenshot | Shows | Result |
|---|---|---|
| 01-admin-record-details-view.png | The per-row View popup "RECORD DETAILS" listing each field and value (Back only) | ✅ Verified (previously captured) |
| 02-admin-empty-grid-no-records-found.png | The grid for a table with no rows, showing "No records found." | ✅ Verified (previously captured) |

Path-only URL: `/CustomTable/GetCustomTableDataList?tableKey={tableKey}` (record grid data list; ids shown as {placeholders}).
