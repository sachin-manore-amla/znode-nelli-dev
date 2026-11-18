# System Tables vs Custom Tables

> **Screenshot verification (2026-10-08, LOCAL admin).** The menu separation was confirmed live:
> **Custom Tables** sit under **Dev Center > Custom Tables** (`/CustomTable/List`) and **System
> Tables** under **PIM > Product Info Overrides** (`/SystemTable/List`) - two separate menus and
> screens. Both lists are **empty (0 records)** on this int DB. The two captures below show each
> menu location and its empty grid.
>
>

## 1. What it is

This document explains how system tables differ from custom tables in Znode. Both use the same underlying technology, but system tables have restrictions that protect their structure. Currently, the only system table is "Product Information Overrides".

## 2. Where you do it

- **System tables** are under **PIM > Product Information Overrides** in the admin.
- **Custom tables** are under **Dev Center > Custom Tables** in the admin.
- They appear in separate menus and are managed through separate screens, but they share the same field and data management tools.

Neither is available on the webstore, Commerce Portal, or B Store app.

## 3. Who can do it

The same admin roles can manage both system and custom tables. There is no role-based distinction between them.

## 4. Step by step

Not applicable — this is a comparison, not a single action.

## 5. What is allowed and what is not

### What you CAN do with system tables (same as custom)
- Rename the table's display name
- View and edit field display names and display order
- Add, edit, and delete data records
- Import data from CSV
- Export data to CSV
- Bulk delete data records

### What you CANNOT do with system tables (different from custom)
- **Create a new system table.** System tables are pre-defined by the platform. There is no "Add" button, and no API route to create one.
- **Delete a system table.** There is no delete option in the admin. If you try to delete via the custom table API, you get the message "Deleting System Tables is not allowed".
- **Rename the table key.** The table key (e.g. `ProductInformationOverrides`) is fixed. Even if you send a new key in the rename API request, it is silently ignored for system tables.

### What is NOT restricted (perhaps surprisingly)
- Adding and deleting fields is **not blocked at the API level**. The field APIs do not check whether the table is system-defined. The admin UI may hide the controls, but the API allows it.

## 6. Messages you may see

| Message | When it appears | When it does not |
|---|---|---|
| "Deleting System Tables is not allowed" | Attempting to delete a system table via the custom table delete API | When using the system table admin (no delete option shown) |

## 7. How it differs

| Aspect | System Tables | Custom Tables |
|---|---|---|
| Location in admin | PIM > Product Information Overrides | Dev Center > Custom Tables |
| Can be created by users | No | Yes |
| Can be deleted by users | No | Yes |
| Table key can be renamed | No | Yes |
| Display name can be renamed | Yes | Yes |
| Fields can be managed | Yes (display name + order) | Yes (full control) |
| Data can be managed | Yes (add, edit, delete, import, export) | Yes (same) |
| Differentiated by | `IsSystemDefined = 1` | `IsSystemDefined = 0` |

## 8. What can be combined

A table is either system-defined or custom — it cannot be both. There is no setting to "promote" a custom table to a system table or vice versa. Changing the `IsSystemDefined` flag requires a direct database update.

## 9. What it changes elsewhere

The distinction affects:
- Which menu the table appears under in the admin
- Whether create/delete operations are available
- Whether the table key can be renamed
- How the "Enable Product Information Overrides" runtime setting applies (it controls the use of override data from the ProductInformationOverrides system table at product display time, not the table management itself)

## 10. Quick answers

**Q: Are system tables and custom tables stored in the same database table?**

**Q: Can a custom table become a system table?**
Not through the UI or API. The `IsSystemDefined` column is never written by any API method. Changing it requires a direct database update.

**Q: Do system tables use different API routes?**
For table-level operations (list, get, rename): yes, they use `v1/system-tables/`. For fields and data: no, they use the same `v1/custom-table-fields/` and `v1/custom-table-data/` routes.

**Q: How many system tables exist?**
Currently only one: "Product Information Overrides" (`ProductInformationOverrides`).

**Q: Are fields restricted on system tables?**
The admin may limit field editing to display name and order. At the API level, there is no restriction — the field APIs do not check `IsSystemDefined`.

**Q: Can I delete a system table by calling the custom table delete API?**
No. The delete method explicitly checks `IsSystemDefined` and returns "Deleting System Tables is not allowed".

**Q: What if I directly set IsSystemDefined=1 in the database for a custom table?**
The system would treat it as a system table — it would appear under PIM, and delete/key-rename would be blocked.

## 11. For developers

See `03-frontend-admin.md` for the admin UI differences, `06-api.md` for the API architecture, `07-functions.md` for the code paths that enforce the distinction, and `08-database.md` for the database structure.

## Fields and options

| Aspect | System Tables | Custom Tables | Confirmed live |
|---|---|---|---|
| Menu path | PIM > Product Info Overrides | Dev Center > Custom Tables | ✅ Verified (both menus) |
| List URL | `/SystemTable/List` | `/CustomTable/List` | ✅ Verified |
| Add button | none | `Add New` present | ✅ Verified |
| List toolbar | Filter + Search only | Filter + Search (+ Tools/Columns when rows exist) | ✅ Verified (both empty here) |

## Screenshot verification (2026-10-08)

| Screenshot | Shows | Result |
|---|---|---|
| `screenshots/01-admin-custom-tables-dev-center.png` | Custom Tables list under the Dev Center menu, with the Add New button | ✅ Verified |

Path-only URLs: `/CustomTable/List` and `/SystemTable/List`.
