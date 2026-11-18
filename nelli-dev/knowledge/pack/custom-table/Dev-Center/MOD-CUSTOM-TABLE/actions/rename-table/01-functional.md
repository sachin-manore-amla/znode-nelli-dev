# Rename Table — Functional

> **Screenshots for this action (previously captured in an earlier pass; corroborated by INT facts 2026-10-08, admin store Amla, v10.14.4.0):**
>
>

## 1. What it is

Renaming a custom table changes its display name — the friendly label that appears in the admin and in lists. The table's internal key (used to identify it everywhere, including the physical database storage) stays the same and cannot be changed. Only the display name is updated.

## 2. Where you do it

- **Admin**: Dev Center > Custom Tables > select a table > Edit. The Table Name field is editable; the Table Key field is shown but cannot be changed.
- **API**: Send a PUT request to the custom tables endpoint with the table key in the URL and the new name in the body.
- **Webstore**: Not available.
- **Commerce Portal**: Not available.
- **B Store**: Not available.

## 3. Who can do it

Any admin user who has access to the Custom Tables section can rename a table. There is no special permission check for renaming — access is controlled by the admin menu and role configuration.

| Role | Can rename |
|---|---|
| Admin with Custom Tables menu access | Yes |
| Admin without Custom Tables menu access | No (cannot reach the page) |

## 4. Step by step

1. Open the Edit page for the custom table (by clicking its name in the list, or navigating directly with the table key).
2. Change the Table Name field to the new name.
3. Click Save.
4. A success message appears: "Record updated successfully."
5. The page reloads showing the Edit form with the updated name.

## 5. What is allowed and what is not

- The table name must start with a letter.
- The table name can contain letters, numbers, underscores and hyphens.
- Spaces are allowed between words, but not at the start or end.
- The table name cannot be blank.
- The table name cannot exceed 100 characters.
- The table key cannot be changed. On a custom table the Table Key input may appear as an enabled text box (it is read-only/disabled only for system tables), but any edit is ignored — the API copies the key from the URL back onto the record, so the key is immutable (see `06-api.md` / `07-functions.md`).
- Two tables can have the same display name (uniqueness is not enforced).
- Renaming a table does not affect its physical storage, its fields, or any data in it.

## 6. Messages you may see

| Message | When it appears | When it does not appear |
|---|---|---|
| "Record updated successfully." | After saving the Edit form, whether or not the update actually succeeded behind the scenes | Never hidden — always shown if the form is valid |
| "Failed to update record." | When the form fails validation (e.g. blank name, invalid characters) | When the form passes validation |
| "The Table Name field is required." | When the name is left blank (API only) | When a name is provided |
| "Table Name can not exceed 100 characters." | When the name is longer than 100 characters (API only) | When the name is within limits |
| "The Table Name must start with a letter and can contain only alphanumeric characters, spaces between words, underscores, and hyphens." | When the name has invalid characters or format (API only) | When the name matches the allowed pattern |
| "The TableId is required." | When calling the API without a table id | When a table id is provided |
| "Id cannot be less than 1." | When calling the API with a table id of zero or negative | When a valid positive id is used |
| "The requested table does not exist" | When calling the API with a table id that does not match any table | When the id matches an existing table |

## 7. How it differs

- **System tables** use a separate endpoint but the same back-end logic. The difference is that for system tables, the key write is skipped entirely (it would not change anyway since the key comes from the URL).
- There are no differences by role, user type, account, country or store — the rename behaves the same for all admin users.

## 8. What can be combined

There are no settings that control or restrict the rename action specifically. No feature flags gate this behaviour.

## 9. What it changes elsewhere

- Renaming a table only changes the display name stored in the table definition record. It does not affect:
 - The physical database table (which is based on the key, not the name).
 - Any field definitions belonging to the table.
 - Any data rows in the table.
 - Any templates or other entities that reference the table (they reference by id, not by name).
- No event, webhook or audit log entry is created by the rename.
- The modified-by and modified-date fields may or may not update, depending on whether there is a database-level mechanism (trigger or interceptor) to set them — the application code does not set them explicitly.

## 10. Quick answers

**Can I change the table key?**
No. The table key is set when the table is created and cannot be changed afterwards. Only the display name can be renamed.

**Does renaming affect the physical table or its data?**
No. The physical table name is based on the key, not the display name. All fields and data remain untouched.

**Can two tables have the same name?**
Yes. There is no uniqueness check on the display name. Two tables can share a name as long as their keys are different.

**What happens if the API returns an error but I used the admin screen?**
The admin always shows "Record updated successfully." after a valid form submission, even if the back-end update failed. This is the current behaviour.

**What characters are allowed in the table name?**
The name must start with a letter. It can contain letters, numbers, underscores and hyphens. Spaces are allowed between words but not at the start or end. Maximum 100 characters.

**Does the rename create an audit trail?**
No audit log or event is generated. The modified-by and modified-date may update depending on database-level mechanisms, but the application does not set them explicitly.

**What happens if I rename to the same name?**
The update runs normally and succeeds. There is no "no change" detection.

**Can two users rename the same table at the same time?**
Yes — last write wins. There is no concurrency protection.

**Is there a setting that controls whether rename is allowed?**
No. There is no feature flag or setting specific to the rename action.

## 11. For developers

See the technical files for full detail:
- `03-frontend-admin.md` — the admin Edit page, controller, agent and call tree.
- `06-api.md` — the PUT endpoint, request/response, curl and data map.
- `07-functions.md` — every method line by line, validations table, workflow.
- `08-database.md` — the table written, physical table impact, verify SQL.

---

## Screenshot verification (2026-10-08)

Screenshots were captured in an earlier pass and are not re-captured here; they are corroborated against the verified INT facts (admin store Amla, v10.14.4.0, 2026-10-08).

| Screenshot | Shows | Status |
|---|---|---|
| 01-admin-rename-table-name-edited.png | Table Name field edited on the Edit screen | ✅ Verified — Table Name is an editable input on INT |
| 02-admin-rename-table-saved-in-list.png | Renamed table reflected in the list after Save & Close, Last Updated bumped | ⚠️ Not verifiable — a real save was not performed in this read-only pass |

Path-only URL: `/CustomTable/EditCustomTable?TableKey={tableKey}`

## Fields and options

| Field / control | Type | Editable | Rules | Notes |
|---|---|---|---|---|
| Table Name | text box | Yes | starts with a letter; letters, numbers, underscores, hyphens, spaces between words; not blank; max 100 | not unique |
| Table Key | text box | Renders enabled on custom tables, but **immutable** 🔄 | cannot be changed — API copies the route key back | input is read-only/disabled only for system tables; editing it has no effect (see Corrections + `06-api.md`) |
| Save & Close | button | — | saves and returns to the list; shows "Record updated successfully." | |
| Back | button | — | → `/CustomTable/List` | |

## Corrections (2026-10-08)

| Item | Was documented as | Verified on INT (2026-10-08) | Mark |
|---|---|---|---|
| Table Key control state on the Edit screen | "always read-only" (implied the input is disabled) | On a **custom** table the Table Key renders as an **enabled** input (read-only/disabled only for **system** tables) | 🔄 Updated |
| Whether the Table Key can actually be changed | n/a | **No** — it is immutable. Even though the custom-table input renders enabled, the API copies the key from the URL back onto the record and ignores any edit (`06-api.md`, `07-functions.md`, ISSUES-FOUND #6). The old "cannot be changed" statement is behaviourally correct. | ✅ Verified |
