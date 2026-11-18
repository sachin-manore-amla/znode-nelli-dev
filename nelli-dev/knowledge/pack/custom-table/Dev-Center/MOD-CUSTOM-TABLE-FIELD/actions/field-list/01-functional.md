# field-list — Functional overview

> **Screenshot banner (2026-10-08).** The field list is the Manage Fields grid (previously captured):
>
>

## 1. What it is

The field list shows every column (field) that has been defined for a custom table. It is the starting point for managing a table's structure — from here an administrator can see each field's type, code, name, length, display order, and whether it has a unique constraint. Fields can be added, edited, or deleted from this same screen.

## 2. Where you do it

- **Admin:** Dev Center > Custom Tables > open a table > the Fields tab loads automatically.
- **Webstore:** Not available.
- **Commerce Portal:** Not available.
- **B Store:** Not available.

The field list is only accessible through the admin panel.

## 3. Who can do it

Any admin user whose role includes access to the Dev Center > Custom Tables menu can view the field list. There is no separate permission for viewing fields versus viewing the table itself. Users without the required role do not see the Custom Tables menu item at all.

Non-admin users (webstore customers, Commerce Portal users, B Store app users) cannot view the field list in any way.

## 4. Step by step

1. In the admin, go to **Dev Center > Custom Tables**.
2. Click a table name to open it for editing.
3. The **Fields** tab loads, showing a grid of all defined fields.
4. The grid displays seven columns: Field Type, Field Code, Field Name, Is Unique, Field Length, Display Order, and Action.
5. An "Add Custom Field" button at the top allows adding new fields.
6. Each existing row has a delete button in the Action column.

## 5. What is allowed and what is not

- The custom table must be saved (it must have a table key) before the field list can be viewed. If the table has not been saved yet, the fields section is not accessible.
- There is no limit on how many fields can be shown. The knowledge base recommends a maximum of 15 columns per table, but this is a guideline only — the field list displays all fields regardless of count.
- Viewing the field list does not change any data. It is a read-only operation.

## 6. Messages you may see

| Message | When it appears | When it does not |
|---|---|---|
| (No explicit empty-state message) | When the table has zero fields, the grid body is simply empty | When the table has at least one field |
| Error / not-found message | When the table key does not exist or is invalid | When the table key is valid |

## 7. How it differs

### When the table has data rows

When the table already contains data records:
- Existing fields' **Field Type** and **Field Code** become read-only (greyed out, cursor shows "not allowed").
- Existing fields' **Is Unique** checkbox is disabled.
- Newly added field rows remain fully editable.
- This prevents structural changes that could break existing data.

### When the table is empty

> **Corrected (int, 2026-10-05, confirmed live):** "all fields are fully editable, type included" was
> wrong. An existing field's **Field Code** is locked (`readOnly`/disabled) **regardless of whether
> the table has data** - this matches `edit-field/01-functional.md`'s "Field Code cannot be changed
> after creation", which is correct and unconditional. **Field Type** is a separate case: its
> `<select>` is not HTML-disabled on an empty table, but it is dynamically pruned down to **only the
> field's current type as an option** - so there is no way to actually pick a different type through
> the UI, confirmed by inspecting the control's own option list (`[{"value":"Text","text":"Text"}]`
> for a Text field). The practical result is the same lock as `edit-field` describes, implemented
> differently (restricted options, not `disabled`) rather than the "fully editable" behaviour
> previously claimed here. See `screenshots/01-admin-field-list-empty-table.png`.
>
> Name, Length, Display Order and Is Unique remain editable on an empty table, as previously stated.

### Field type affects the display

- For **Boolean** and **Date and Time** fields, the Field Length column is blank (these types have no configurable length).
- For **Text**, **Text Area**, and **Numeric** fields, the Field Length column shows the configured value.

## 8. What can be combined

No combination or stacking rules apply to the field-list view. It is a display-only action.

## 9. What it changes elsewhere

Nothing. Viewing the field list is purely a read operation. No audit log entry, no timestamp update, no cache invalidation occurs.

## 10. Quick answers

**Q: Where do I see the fields of a custom table?**
Open the table in Dev Center > Custom Tables; the Fields tab loads automatically showing all defined fields.

**Q: Can I sort or filter the field list?**
No. The grid is a static editable table. Fields appear in the order they were created (by internal ID). There is no column-header sorting or search.

**Q: Is there a maximum number of fields shown?**
No hard limit. All fields for the table are displayed. The knowledge base recommends up to 15 columns, but this is not enforced.

**Q: What does "disabled until the table is saved" mean?**
The field list requires the table to have been saved at least once (so it has a table key). Before that first save, the fields section cannot be accessed.

**Q: Does viewing the field list write anything?**
No. It is entirely read-only.

**Q: Why are some fields greyed out?**
When the table already has data rows, existing fields' type and code become read-only to prevent structural changes that could break the data.

**Q: What are the field types shown?**
Text, Text Area, Number (Numeric), Boolean, and Date and Time (datetime).

**Q: What does the "Is Unique" column show?**
A checkbox indicating whether the field has a unique constraint. Only one field per table can be marked as unique.

## 11. For developers

See `03-frontend-admin.md` for the admin screen details, `06-api.md` for the API endpoint, `07-functions.md` for the back-end call tree, and `08-database.md` for the database table and query.

## Fields and options

The Manage Fields grid (`/CustomTable/CustomTableFieldList?tableKey={tableKey}`) is an inline-editable grid. Columns shown per field row:

| Column | Shows / behaviour | Where the value comes from |
|---|---|---|
| Is Unique | dropdown true/false; enabled for existing fields | unique constraint flag |
| Field Length | characters (Text/Text Area) or `precision,scale` (Number); blank for Boolean / Date And Time | field length |
| Display Order | integer order | field display order |
| Action | per-row edit + delete icons | n/a |

An **Add Custom Field** button sits above the grid. Example `testabhi`: `name` (Text, Is Unique true, length 5, order 500), `Number` (Number/stored `Numeric`, length `12,2`, order 500), `Address` (Text, length 5, order 500).

## Screenshot verification (2026-10-08)

Grid screen: `/CustomTable/CustomTableFieldList?tableKey={tableKey}` (path only; ids as `{tableKey}`).

| Screenshot | Shows | Result |
|---|---|---|
| `screenshots/01-admin-field-list-empty-table.png` | Manage Fields grid for a table with no fields (empty grid body, Add Custom Field button present) | ✅ Verified — previously captured; grid columns verified against INT facts (2026-10-08, read-only) |

Grid column set (FIELD TYPE, Field Code, Field Name, Is Unique, Field Length, Display Order, Action) and the Add Custom Field button are ✅ Verified on INT (2026-10-08, read-only; `testabhi` table). Nothing was saved.
