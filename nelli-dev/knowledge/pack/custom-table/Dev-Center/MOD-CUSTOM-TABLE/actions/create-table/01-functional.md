# Create Table -- Functional

> **Screenshots for this action (previously captured in an earlier pass; corroborated by INT facts 2026-10-08, admin store Amla, v10.14.4.0):**
>
>
>
>

## 1. What it is

Creating a custom table adds a new, empty data table to the system. You give it a key (a short identifier used internally) and a name (a friendly label). Once created, you can add fields (columns) to it and then use it to store custom data.

## 2. Where you do it

- **Admin:** Dev Center > Custom Tables > click "Add New". This opens the "Add Custom Table" form.
- **Webstore:** not available.
- **Commerce Portal:** not available.
- **B Store app:** not available.
- **API:** send a POST request to `/v1/custom-tables` with a table key and table name.

## 3. Who can do it

Access is controlled by the admin role's menu visibility. If the "Custom Tables" menu item is visible to a role, users with that role can create tables. There is no additional permission check.

## 4. Step by step

1. In the admin, go to Dev Center > Custom Tables.
2. Click "Add New". The "Add Custom Table" form opens.
3. Enter a **Table Key** -- this is the internal identifier. It must start with a letter and contain only letters and numbers (no spaces, no special characters). Maximum 100 characters.
4. Enter a **Table Name** -- this is the display name. It must start with a letter and can contain letters, numbers, underscores, hyphens, and spaces between words. Maximum 100 characters.
5. Click **Save**. If successful, the page redirects to the Edit page for the new table, where you can start adding fields. Or click **Save & Close** to return to the list.
6. The "Manage Fields" button is disabled on this form -- you must save the table first before adding fields.

## 5. What is allowed and what is not

- The table key must start with a letter and contain only letters and numbers. Spaces, underscores, hyphens and special characters are not allowed in the key.
- The table name must start with a letter. It can include letters, numbers, underscores, hyphens, and spaces between words.
- Both the key and name are required and limited to 100 characters each.
- The table key must be unique (checked without regard to upper/lower case). You cannot create two tables whose keys differ only in capitalisation.
- The table name does not need to be unique. Two tables can share the same display name.
- Leading and trailing spaces in the table key are removed automatically. Spaces in the table name are kept as entered.
- There is no limit on how many custom tables you can create.
- There is no list of reserved names. Any value that matches the format rules is accepted.
- No global setting controls table creation. The 100-character limits are fixed.

## 6. Messages you may see

| Message | When it appears | When it does not appear |
|---|---|---|
| "The Table Key field is required." | Table Key is left empty | Table Key has any value |
| "Table Key can not exceed 100 characters." | Table Key is longer than 100 characters | 100 or fewer characters |
| "Only alphanumeric characters are allowed and the Table Key must start with a letter." (admin UI, **confirmed live, int, 2026-10-05**; API message text may differ - see `06-api.md`) | Table Key contains spaces, hyphens, or other special characters, or starts with a number | Key starts with a letter and has only letters and numbers. See `screenshots/04-admin-invalid-key-format-error.png` |
| "The Table Name field is required." | Table Name is left empty | Table Name has any value |
| "Table Name can not exceed 100 characters." | Table Name is longer than 100 characters | 100 or fewer characters |
| "The Table Name must start with a letter and can contain only alphanumeric characters, spaces between words, underscores, and hyphens." | Table Name starts with a number or contains disallowed characters | Name matches the allowed format |
| "Table Key Already Exist" (confirmed live, int, 2026-10-05) | A table with the same key (ignoring case) already exists | The key is new. See `screenshots/03-admin-duplicate-table-key-error.png` |
| Success toast ("Record created successfully.") | Table created successfully | Any error occurred |
| Error toast ("Failed to create record.") | The system could not create the table | Creation succeeded |

## 7. How it differs

There are no differences by role, user type, account, country, or setting. The behaviour is the same for all admin users who can see the Custom Tables menu.

## 8. What can be combined

Not applicable. Table creation is a standalone action with no combination or stacking rules.

## 9. What it changes elsewhere

- A new metadata record is stored in the system tracking the table's key, name, and who created it.
- A new physical database table is created with a single auto-incrementing ID column. Fields are added separately afterward.
- The new table appears immediately in the Custom Tables list.
- There is no effect on search, publishing, or any other module.
- No notification, email, webhook, or audit log entry is generated.
- If the physical table creation fails after the metadata is saved, the metadata record remains but the table is not usable until the issue is resolved.

## 10. Quick answers

**Can I use spaces in the table key?**
No. The table key allows only letters and numbers, no spaces or special characters.

**Can I use spaces in the table name?**
Yes, spaces between words are allowed in the table name.

**Is the table key case-sensitive?**
The key is stored as you type it, but uniqueness is checked without regard to case. "MyTable" and "mytable" are considered the same key.

**Is there a limit on how many tables I can create?**
No. There is no coded or configured limit.

**Can I add fields right away?**
No. The "Manage Fields" button is disabled on the creation form. Save the table first, then add fields on the Edit page.

**What happens if I enter a duplicate key?**
You get an error: "Table Key Already Exist". The table is not created.

**Is the table name trimmed?**
No. Leading and trailing spaces in the table name are kept. The table key is trimmed.

**Are there any settings that control table creation?**
No. All limits (100-character maximum for key and name) are fixed in the code.

**What does the physical table look like when first created?**
It has a single column: an auto-incrementing integer ID. All other columns are added later as fields.

## 11. For developers

See `03-frontend-admin.md` for the admin screen, selectors, and call tree. See `06-api.md` for the API contract, curl, and verification SQL. See `07-functions.md` for the line-by-line code path. See `08-database.md` for the tables written and read.

---

## Screenshot verification (2026-10-08)

Screenshots were captured in an earlier pass and are not re-captured here; they are corroborated against the verified INT facts (admin store Amla, v10.14.4.0, 2026-10-08) where those facts cover the screen.

| Screenshot | Shows | Status |
|---|---|---|
| 01-admin-add-custom-table-form.png | "Add Custom Table" form reached from the list "Add New" button | ✅ Verified — Add New opens `/CustomTable/CreateCustomTable` on INT |
| 02-admin-add-custom-table-required-field-errors.png | Required-field errors on Save with both fields empty | ⚠️ Not verifiable — live validation not re-submitted in this read-only pass |
| 03-admin-duplicate-table-key-error.png | "Table Key Already Exist" error on a duplicate key | ⚠️ Not verifiable — live submission not re-run in this read-only pass |
| 04-admin-invalid-key-format-error.png | Invalid Table Key format error | ⚠️ Not verifiable — live submission not re-run in this read-only pass |

Path-only URL: `/CustomTable/CreateCustomTable` (reached from the list `Add New` button on `/CustomTable/List`)

## Fields and options

| Field / control | Type | Required | Rules | Notes |
|---|---|---|---|---|
| Table Key | text box | Yes | starts with a letter, letters + numbers only, max 100, unique (case-insensitive), trimmed | immutable after creation |
| Table Name | text box | Yes | starts with a letter; letters, numbers, underscores, hyphens, spaces between words; max 100 | not unique; spaces kept |
| Manage Fields | button | — | disabled on the create form | enabled only after the table is saved |
| Save | button | — | on success redirects to Edit page | |
| Save & Close | button | — | on success returns to the list | |
| Cancel | button | — | returns to `/CustomTable/List` | |
