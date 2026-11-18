# check-rows-exist — functional

Action: Check whether a custom table holds any data rows.




> **Corrected (int, 2026-10-05, confirmed live):** the earlier claim below - that the presence of
> data disables field management entirely - is **wrong** and has been corrected. Tested directly
> on `APIBulkInsert` (one data row): added a new ordinary (non-unique) Text field, saved it
> successfully ("Record updated successfully", confirmed by reopening the table), then deleted
> that same field (no confirmation dialog - the row is simply removed from the grid, unlike
> deleting a whole table) and saved again, also successful. **Adding and deleting ordinary fields
> works regardless of whether the table has data.** What actually cannot change once a field
> exists is its **field code and type** (shown disabled/greyed) - that is a permanent property of
> the field itself, unrelated to the row-count check this file is about. The real,
> data-dependent restriction - confirmed by `add-fields/01-functional.md`, which this file's
> step-by-step below did not previously match - is narrower: **a field cannot be added or
> modified with the UNIQUE constraint once the table has data** (message: "The field cannot be
> added or modified with a UNIQUE constraint after data has been inserted into the custom
> table."). See `add-fields/screenshots/` for the add/delete-with-data evidence.

---

## 1. What it is

This action checks whether a custom table contains any data rows. It is a read-only check that returns a simple yes or no answer. The admin uses it in several places to decide what the user can do next.

---

## 2. Where you do it

This check is not something you trigger directly — it happens automatically in the admin in three situations:

- **Custom Table list page** — when you hover over the delete icon for a table, the system checks whether the table has data.
- **Custom Table detail page (export)** — when you click Export, the system checks whether there is any data to export.
- **Custom Table detail page (field list)** — when the edit page loads, the system checks whether the table has data. This does **not** disable adding or deleting ordinary fields (confirmed live) - it only affects whether a **new or edited field can carry the UNIQUE constraint**.

It is also available as an API endpoint for any integration that needs to know whether a table has data.

Not available in the webstore, Commerce Portal or B Store.

---

## 3. Who can do it

Any authenticated user with access to the admin or the API gateway can trigger this check. There is no role-specific restriction on the API endpoint itself.

---

## 4. Step by step

### On the list page (delete hover)

1. You hover over the delete icon next to a custom table.
2. On the first hover, the system silently calls the API to check if the table has rows.
3. If the table has rows, the delete icon becomes clickable and opens a confirmation popup.
4. If the table has no rows, the delete icon does not open the popup.
5. On subsequent hovers, the system remembers the first result and does not call the API again.

### On the detail page (export)

1. You click the Export button.
2. The system checks if the table has data.
3. If the table has no data, you see the message: "No Data Available to Export."
4. If the table has data, the export proceeds.

### On the detail page (field list)

1. You open a custom table for editing.
2. The system checks if the table has data.
3. **Adding and deleting ordinary (non-unique) fields is not affected either way** - confirmed
 live on a table with data: a new field was added and saved, then deleted and saved again,
 both successfully, with no confirmation prompt on delete.
4. If the table has data, a field **cannot** be added or edited with the UNIQUE constraint turned
 on - that specific save is rejected with "The field cannot be added or modified with a UNIQUE
 constraint after data has been inserted into the custom table." (see `add-fields/01-functional.md`).
5. An existing field's **code and type** are always disabled for editing once the field exists,
 whether or not the table has data - that restriction is about the field itself, not the table's
 row count.

---

## 5. What is allowed and what is not

- Any table key that exists can be checked. The check works for both custom tables and system tables.
- The table key must start with a letter and contain only letters and numbers (no spaces, hyphens or special characters). If it does not, the check is rejected.
- The table key cannot be longer than 100 characters.
- If you check a table key that does not exist, the API returns an error saying the table does not exist.

---

## 6. Messages you may see

| Message | When it appears | When it does not appear |
|---|---|---|
| "No Data Available to Export." | When you try to export a table that has no data rows | When the table has at least one data row |
| "The requested table does not exist" | When the API is called with a table key that has no matching table definition | When the table key maps to a real table |
| "Table Key cannot exceed 100 characters." | When the table key is longer than 100 characters | When it is 100 characters or fewer |
| "The Table Key must start with a letter and contain only alphanumeric characters..." | When the table key contains special characters or starts with a number | When the table key is valid |

---

## 7. How it differs

- **Tables with data vs without**: Field add/delete is **not** locked by data presence (confirmed live) - only a field's UNIQUE constraint is. The check also determines whether the export proceeds or shows an error.
- **Custom tables vs system tables**: Both use the same API endpoint and the same check logic. The admin has separate controllers for custom and system tables, but they both call the same underlying API.
- **First hover vs subsequent hovers**: On the list page, the API is called only on the first hover over each delete icon. The result is cached on the icon element.

---

## 8. What can be combined

No settings or flags control this behaviour. It is a straightforward data-presence check.

---

## 9. What it changes elsewhere

Nothing. This is a read-only check. It does not modify any data, timestamps or state.

---

## 10. Quick answers

**Q1. Who can call this API?**
Any authenticated user via the gateway. No role-specific restriction.

**Q2. Is this admin-only or available to any authenticated user?**
Any authenticated user can call the API endpoint. The admin UI is the only built-in surface that uses it.

**Q3. Where is it used?**
Three places in the admin: delete-hover on the list page, export check on the detail page, and field-list disable on the detail page.

**Q4. Does the admin call this before showing the delete confirmation?**
Yes — on the first hover over the delete icon, it calls the API silently (no loading spinner).

**Q5. What HTTP method and path?**
`GET /v1/custom-tables/{tableKey}/record-exists`

**Q6. What are the request parameters?**
`tableKey` in the route path. Must be alphanumeric, start with a letter, max 100 characters.

**Q7. What does it return when rows exist?**
200 with `{ "IsSuccess": true }`.

**Q8. What does it return when no rows exist?**
200 with `{ "IsSuccess": false }`.

**Q9. What if the table does not exist?**
404 with an error message: "The requested table does not exist."

**Q10. Can a table with no fields have rows?**
No. A table with no user-defined fields has a physical table but only an auto-generated identity column, so it will have zero data rows.

**Q11. What is the full response model?**
`TrueFalseResponse` with one field: `IsSuccess` (boolean).

**Q12. How does it check — COUNT or EXISTS?**
EXISTS. This is efficient even for tables with millions of rows because it stops at the first row found.

**Q13. What validation is performed?**
Required, max length 100, and a regex requiring alphanumeric characters starting with a letter.

**Q14-15. What error for invalid or non-existent table key?**
Invalid format: 400 with a validation message. Non-existent: 404 with "The requested table does not exist."

**Q16. Does it distinguish "no fields" from "fields but no rows"?**
No. Both return `IsSuccess: false`.

**Q17. Physical table or metadata count?**

**Q18. Any settings that affect it?**
None.

**Q19. Any permissions beyond authentication?**
None.

**Q20. Does it modify any data?**
No. Entirely read-only.

**Q32. Does the admin UI call this endpoint?**
Yes, via `GET /CustomTable/IsRecordExists?TableKey=...` which internally calls the API.

**Q33. What does the admin do with the result?**
On the list page: links the delete icon to the confirmation popup (true) or leaves it unlinked (false). On the field list: disables field controls (true) or leaves them active (false).

**Q34. Synchronous or asynchronous?**
Asynchronous AJAX call with no loading spinner.

**Q35. What if the API call fails?**
The admin agent swallows the exception and returns false — same behaviour as "no rows." The delete icon stays unlinked and field controls stay active.

**Q36. What if the physical table is missing but metadata exists?**
The EXISTS query fails with a SQL error. The API returns 500.

**Q37. Is it performant for large tables?**
Yes — EXISTS stops at the first row.

**Q38. What about invalid input (0, negative, non-alphanumeric)?**
Table key is a string, not numeric. Non-alphanumeric values are rejected by the regex (400). Empty values cause the service to return false without querying.

**Q39. Table just created with fields but no records?**
Returns `IsSuccess: false`.

**Q40. Can it be called for system tables?**
Yes. The same API endpoint works for both. No system-table guard.

**Q41. What if the table is locked or being imported into?**
The SQL query may time out. The exception is rethrown and the API returns 500.

**Q42. Is there a gateway route?**
Yes — covered by the Ocelot catch-all `/v1/custom-tables/{everything}`.

---

## 11. For developers

See `03-frontend-admin.md` for the admin MVC action and TypeScript call, `06-api.md` for the API endpoint contract and curl, `07-functions.md` for the back-end call tree and line-by-line detail, and `08-database.md` for the SQL and tables.

---

## Screenshot verification (2026-10-08)

This action is API/behavioural — it is not a screen the user opens directly; it drives admin UI decisions. The two screenshots were captured in an earlier pass and are not re-captured here. The `record-exists` check itself (`GET /custom-tables/{tableKey}/record-exists`) is behavioural and was not re-run live in this read-only pass.

| Screenshot | Shows | Status |
|---|---|---|
| 01-admin-table-with-data-row.png | A custom table that holds one data row (APIBulkInsert) | ⚠️ Not verifiable — row-level data not re-queried in this read-only pass |
| 02-admin-manage-fields-table-has-data.png | Manage Fields on that table: adding/deleting ordinary fields is not locked by data; only existing field codes are disabled | ⚠️ Not verifiable — field add/delete behaviour not re-run in this read-only pass |

Path-only URL (admin): `/CustomTable/IsRecordExists?TableKey={tableKey}` · (API): `/custom-tables/{tableKey}/record-exists`

## Fields and options

| Element | Type | Values / behaviour | Notes |
|---|---|---|---|
| TableKey | input (not user-typed here) | read from the grid row / current edit-page key | passed to the check |
| IsRecordExist (result) | boolean | `true` when the physical table has at least one row, else `false` | `false` also returned on any swallowed error |
| Delete-icon hover (list) | trigger | links the delete icon to the confirm popup when rows exist | called once per icon per page load |
| Export (detail page) | trigger | blocks with "No Data Available to Export." when no rows | |
| Field-list load (detail page) | trigger | gates only whether a field can carry the UNIQUE constraint | ordinary field add/delete is not locked |
