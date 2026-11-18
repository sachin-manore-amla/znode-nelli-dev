# List Custom Tables — functional guide

> **Screenshots for this action (previously captured in an earlier pass; corroborated by INT facts 2026-10-08, admin store Amla, v10.14.4.0):**
>
>
>
>
>
>
>

> **Corrected and expanded (int, 2026-10-05, confirmed live):** this file previously said filter
> operators include "equals, not equals, contains, does not contain..." - **wrong**. The real,
> live-confirmed operator list (shown only after a column is chosen) is exactly four: **Contains**,
> **Is**, **Begins With**, **Ends With**. Also newly documented below from live testing: the
> **SYSTEM VIEW** picker (save/switch named grid views), the **TOOLS** dropdown (bulk Delete only),
> and the **COLUMNS** picker (toggle Created Date / Last Updated on or off; Table Key and Table Name
> are locked on). See screenshots 02-06 below.

## 1. What it is

The Custom Tables list page shows every custom table that has been created in the system. It is a paginated, sortable, filterable grid where administrators can see each table's key, name, creation date and last update date, and can reach the Edit or Delete actions for any table. System-defined tables (such as Product Information Overrides) are kept on a separate list and never appear here.

---

## 2. Where you do it

| Surface | Available | How to reach it |
|---|---|---|
| Admin | Yes | **Dev Center > Custom Tables** in the left menu |
| Webstore | No | Not available |
| Commerce Portal | No | Not available |
| B Store app | No | Not available |
| API only | Yes | Send a GET request to the custom-tables endpoint (see section 11) |

In the Admin, the page URL is `/CustomTable/List`.

---

## 3. Who can do it

Access depends on the admin user's role. The system checks whether the role includes the "Custom Table / List" menu permission.

| Condition | What happens |
|---|---|
| The user's role includes the Custom Tables menu permission | The menu item appears and the page loads normally |
| The user's role does not include the Custom Tables menu permission | The menu item is hidden — no error page, no access-denied message, just no link |
| The user is not logged in as an admin | Redirected to the login page |

There is no further permission check on the page itself or the underlying data call. Once you can reach the page, you see all custom tables. There is no per-table or per-user restriction on which tables appear.

At the API level, any caller that provides valid credentials receives data. There is no role or permission check on the endpoint — authentication alone is enough.

---

## 4. Step by step

1. In the Admin, open **Dev Center > Custom Tables** from the left menu.
2. The page loads with a grid showing the first page of custom tables (10 per page by default).
3. The heading reads "CUSTOM TABLES" and shows a badge with the total number of tables.
4. To **filter**, click **FILTER** above the grid. Choose a column from **Select Column** (only
 **Table Key** or **Table Name** are offered), then choose an operator - **Contains**, **Is**,
 **Begins With**, or **Ends With** (confirmed live; these four only) - type the value, and click
 **Apply Filter**. "Add Filter" adds a second condition row for a combined filter. See
 `screenshots/02-admin-filter-panel-column-operator.png`.
5. To **sort**, click the Table Key column header. An arrow icon shows the sort direction. Click
 again to toggle between ascending and descending. Table Key is the only sortable column (none of
 the other headers carry a sort link). See `screenshots/06-admin-sorted-table-key-asc.png`.
6. To **change page size**, use the page-size selector below the grid. Options are 10, 25, 50 and 100.
7. To **navigate pages**, use the page numbers or previous/next links below the grid.
8. To **edit a table**, click the Edit link in the Action column of that row.
9. To **delete a table**, click the Delete link in the Action column, or select one or more tables using the checkboxes and click the Delete button in the toolbar. Either way, a confirmation popup appears asking you to type the word "Delete" to proceed.
10. **SYSTEM VIEW** (top right): a saved-view picker. "All Views" / "System View" lets you switch
 between saved grid configurations; "Save view As" lets you name and save the current
 filter/sort/column combination as a new view, optionally "Make it public" so other admins can
 use it too. See `screenshots/03-admin-system-view-dropdown.png`.
11. **TOOLS** (top right): a dropdown with a single action, **Delete** - bulk-deletes whichever
 rows are checked via the row checkboxes, same confirmation flow as the per-row Delete link. See
 `screenshots/04-admin-tools-dropdown-bulk-delete.png`.
12. **COLUMNS** (top right): a picker to show/hide grid columns. **Table Key** and **Table Name**
 are locked on (greyed out, always shown); **Created Date** and **Last Updated** can be toggled
 off. There are no additional hidden columns beyond these four. See
 `screenshots/05-admin-columns-dropdown.png`.

If there are no custom tables (for example on a fresh installation), the grid is empty and the count shows zero.

---

## 5. What is allowed and what is not

- Any admin whose role includes the Custom Tables menu permission can view the full list. There is no way to restrict which tables a particular admin sees.
- Only Table Key can be sorted. Table Name, Created Date and Last Updated cannot be sorted by clicking their headers.
- You can filter by Table Key or Table Name, but not by Created Date or Last Updated.
- You can sort by only one column at a time. Multi-column sorting is not supported.
- The filter is case-insensitive — searching for "test" and "TEST" returns the same results.
- There is no upper limit on page size at the API level (any positive number is accepted), but the Admin grid offers only 10, 25, 50 and 100.
- Page index must be 1 or higher. Sending 0 or a negative number results in an error.
- System-defined tables are always excluded from this list. The system enforces this automatically and the caller cannot override it.
- Viewing the list is read-only. It does not create, change or delete anything.

---

## 6. Messages you may see

| Message | When it appears | When it does not appear |
|---|---|---|
| "CUSTOM TABLES" (page heading with count badge) | Always, when the page loads | — |
| "No records found." (confirmed live, int, 2026-10-05) | When no custom tables exist, or the current filter matches nothing | When at least one table matches |
| "The selected table(s) may have data associated with it. Proceeding with this action will delete the table and its associated data (if any). To confirm the deletion, please type 'Delete' in the text box below:" | When you click Delete on a row or select tables for bulk delete | When you are only viewing or filtering |
| "Confirm Delete" (popup title) | Same as above — the delete confirmation popup | — |
| "Invalid keyword entered, please try again." | When you type something other than "Delete" in the confirmation popup and try to submit | When you type "Delete" correctly |

If the underlying service is unreachable or returns an error, the page shows an empty grid with no error message. The error is logged internally but not displayed to the user.

---

## 7. How it differs

### By role

All admin roles that have the Custom Tables menu permission see the same list with the same columns and the same data. There is no role-based difference in what is displayed.

The Add button appears only if the user's role also includes the "Create Custom Table" permission. If it does not, the button is hidden but the rest of the page works normally.

### By surface

This page exists only in the Admin. There is no equivalent in the Webstore, Commerce Portal or B Store.

### System tables versus custom tables

The list shows only custom tables (user-created). System-defined tables appear on a separate page and use a separate endpoint. The two lists use the same underlying service but with a different flag.

---

## 8. What can be combined

- Filtering and sorting can be used together. Apply a filter, then sort the results by Table Key.
- Filtering and paging work together. When you apply a filter, the page resets to page 1.
- The grid remembers your last filter when you return to the page in the same session (stored in a browser cookie).

There are no settings or flags that change how filtering, sorting or paging behave on this page.

---

## 9. What it changes elsewhere

Nothing. Viewing the Custom Tables list is a pure read operation. It does not write to any table, clear any cache, trigger any event, send any notification or affect any other part of the system.

---

## 10. Quick answers

**Q1: Who can access the Custom Tables list page in Admin — which roles are required?**
Any admin role that includes the "Custom Table / List" menu permission. The menu item is hidden for roles without it.

**Q2: What menu path leads to the Custom Tables list?**
Dev Center > Custom Tables.

**Q3: Is the list accessible outside the Admin?**
Only via the API. There is no list page in the Webstore, Commerce Portal or B Store.

**Q4: What does a user without permission see?**
The menu item is hidden. There is no 404 or access-denied page — the link simply does not appear.

**Q5: Can a Sales Rep, CSR or Commerce Portal user see the Custom Tables list?**
No. The page is Admin-only and requires the Custom Tables menu permission.

**Q6: Is there an API-only way to list custom tables?**
Yes. A GET request to the custom-tables endpoint returns the same data, with paging, sorting and filtering via query parameters.

**Q7: Does a fresh install have zero tables?**
Yes. All custom tables are user-created. A fresh installation has none.

**Q8: What columns are shown in the grid?**
Checkbox (for bulk select), Table Key, Table Name, Created Date, Last Updated, and Action (Edit / Delete links).

**Q9: What is the default sort?**
No default sort is configured. The data arrives in internal database order (by primary key, ascending).

**Q10: Which columns are sortable?**
Only Table Key. Table Name, Created Date and Last Updated are not sortable.

**Q11: Can the user sort by Table Name, Created Date or Last Updated?**
No. Only Table Key supports sorting.

**Q12: Which columns are filterable?**
Table Key and Table Name. Created Date and Last Updated are not filterable from the grid.

**Q13: Is the filter case-sensitive?**
No. All filtering is case-insensitive.

**Q14: What filter operators are available?**
Exactly four (confirmed live, int, 2026-10-05): **Contains**, **Is**, **Begins With**, **Ends With**.
Not the larger set previously assumed here.

**Q15: Is filtering live (as you type) or on submit?**
On submit. You must press Enter or click the search button.

**Q16: What happens when the filter matches nothing?**
**Corrected (int, 2026-10-05, confirmed live):** not an empty grid with no message - a filter/search
matching nothing shows **"No records found."** (the shared Znode grid component's standard empty
text, same as the record grid's). The count badge also correctly updates to `0` for the filtered
result. See `screenshots/07-admin-no-records-found-filtered.png`.

**Q17: Can you clear the filter?**
Yes. Clear the filter inputs and resubmit to return to the full list.

**Q18: What is the default page size?**
10 rows per page.

**Q19: What page sizes are available?**
10, 25, 50 and 100.

**Q20: Does the page show a total count?**
Yes. The heading includes a badge showing the total number of matching tables.

**Q21: Does paging reset when a filter or sort is applied?**
Yes. Applying a filter resets to page 1.

**Q22: What date format is used?**
Dates are displayed as year-month-day hour:minute:second (e.g. 2026-01-15 09:30:00).

**Q23: Are dates shown in UTC or local time?**
The dates are stored and returned as-is from the database. No time-zone conversion is applied.

**Q24: What actions are available per row?**
Edit and Delete. There are no other per-row actions (no View, Clone or similar).

**Q25: Is there a bulk-select checkbox?**
Yes. The first column is a checkbox for selecting multiple tables for bulk delete.

**Q26: Is there an Add button?**
Yes, if the user's role has the Create Custom Table permission. It appears at the top of the page.

**Q27: What happens if the API or service is unreachable?**
The page shows an empty grid with no error message. The error is logged internally.

**Q28: Does the list show soft-deleted or inactive tables?**
There is no soft-delete or active/inactive concept for custom tables. All custom tables appear.

**Q29: Is there a maximum number of tables the list can handle?**
No hard limit. The grid supports standard paging for any number of rows.

**Q30: Does the list include tables created via the API?**
Yes. Tables created through the API and through the Admin appear in the same list.

**Q31: Does the Custom Table list share anything with the System Table list?**
Both use the same underlying service and response structure. The only difference is that the custom-table list excludes system-defined tables and the system-table list includes only system-defined tables.

**Q32: Does the list endpoint appear as a picker or dropdown in any other module?**
No.

**Q33: Does the gateway cache the list response?**
The gateway is a pure pass-through. Caching happens inside the Custom Table microservice (in memory, keyed by the exact combination of filter, sort, page and page size).

**Q34: Does viewing the list cause any writes (audit log, last-accessed)?**
No. The action is completely read-only.

**Q35: Does the API require specific headers like DomainId or UserId?**
No. The endpoint requires only valid authentication credentials. No domain or user headers are needed for listing.

**Q36: What does the API return when there are zero tables?**
A 204 (No Content) response with an empty body.

**Q37: What does the API return for invalid page index or page size?**
A 400 (Bad Request) error if the value is less than 1.

**Q38: What does the API return for an invalid sort column?**
A 500 (Internal Server Error).

**Q39: What does the API return for an invalid filter operator?**
A 404 (Not Found) with an error message about invalid filter format.

**Q40: Are filter values protected against injection?**
Yes. All filter values are parameterized. Raw values are never concatenated into queries.

**Q41 (KB verification): KB says "all the created custom tables will be displayed" — is it paged?**
Yes, it is paged (default 10 per page). The KB description is simplified; in practice the list is paginated.

**Q42 (KB verification): KB says columns are Table Key, Table Name, Created Date, Last Updated, Action — still accurate?**
Yes, plus a bulk-select checkbox column that the KB does not mention.

**Q43 (KB verification): KB says only Edit and Delete actions — any others?**
No. Edit and Delete are the only per-row actions, matching the KB.

**Q44 (KB verification): KB says menu is Dev Center > Custom Tables — still accurate?**
Yes.

**Q45 (KB verification): KB does not mention search/filter — does it exist?**
Yes. The page has a structured filter bar for Table Key and Table Name that the KB does not document.

**Q46 (KB verification): KB does not mention sorting — does it exist?**
Yes. Table Key is sortable. The KB does not document this.

**Q47 (KB verification): KB does not mention paging — does it exist?**
Yes. Standard paging with selectable page sizes (10, 25, 50, 100). The KB does not document this.

---

## 11. For developers

Technical details — controller actions, service methods, API contracts, query parameters, response fields, database schema, caching and the full call tree — are in the companion files:

- **03-frontend-admin.md** — the Admin page, grid columns, view, call tree and resource strings
- **06-api.md** — the API endpoint contract, request/response fields, curl examples and verification queries
- **07-functions.md** — every method on the path, line by line, from controller to repository
- **08-database.md** — the table schema, indexes, generated queries and read-only SQL examples

There is no webstore, Commerce Portal or B Store surface for this action, so 04, 05 and 05b files are not created.

---

## Screenshot verification (2026-10-08)

Screenshots were captured in an earlier pass and are not re-captured here; they are corroborated against the verified INT facts (admin store Amla, v10.14.4.0, 2026-10-08) where those facts cover the screen.

| Screenshot | Shows | Status |
|---|---|---|
| 01-admin-custom-tables-list.png | "CUSTOM TABLES" heading with count badge (74), grid columns (Table Key / Table Name / Created Date / Last Updated / Action), Add New, toolbar | ✅ Verified — heading, count, columns and Add New match INT |
| 02-admin-filter-panel-column-operator.png | Filter panel: Select Column + operator | ✅ Verified — Filter opens a column + operator panel on INT |
| 03-admin-system-view-dropdown.png | System View picker (saved grid views) | ✅ Verified — System View dropdown present on INT |
| 04-admin-tools-dropdown-bulk-delete.png | Tools dropdown with bulk Delete | ✅ Verified — Tools dropdown offers bulk delete on INT |
| 05-admin-columns-dropdown.png | Columns show/hide picker | ✅ Verified — Columns dropdown present on INT |
| 06-admin-sorted-table-key-asc.png | Grid sorted by Table Key ascending | ✅ Verified — Table Key is the sortable column on INT |
| 07-admin-no-records-found-filtered.png | "No records found." empty state after a non-matching filter | ⚠️ Not verifiable — empty-filter state not re-run in this read-only pass |

Path-only URL: `/CustomTable/List` (sorted link: `/CustomTable/List?sort=TableKey&sortdir=ASC`)

## Fields and options

| Element | Type | Values / behaviour | Notes |
|---|---|---|---|
| Table Key | grid column | sortable + filterable; links to Edit (`/CustomTable/EditCustomTable?TableKey={tableKey}`) | the only sortable column |
| Table Name | grid column | filterable | not sortable |
| Created Date | grid column | `yyyy-MM-dd HH:mm:ss` | toggle via Columns |
| Last Updated | grid column | `yyyy-MM-dd HH:mm:ss` | toggle via Columns |
| Action | grid column | Manage menu → Edit / Delete | per row |
| Filter operators | dropdown | Contains, Is, Begins With, Ends With | shown only after a column is chosen |
| Search | text box | free text | toolbar |
| Columns | dropdown | toggle Created Date / Last Updated | Table Key + Table Name locked on |
| Tools | dropdown | bulk Delete | acts on checked rows |
| System View | dropdown | All Views / Save view As / Make it public | saved grid views |
| Page size | selector | 10 / 20 / 50 / 100 🔄 (default 10) | see Corrections |
| Add New | button | → `/CustomTable/CreateCustomTable` | create a table |

## Corrections (2026-10-08)

| Item | Was documented as | Verified on INT (2026-10-08) | Mark |
|---|---|---|---|
| Grid page-size options | 10, 25, 50, 100 | Show selector offers **10 / 20 / 50 / 100** (count shown as "Showing 1 - 10 of 74", page "1 / 8") | 🔄 Updated |
