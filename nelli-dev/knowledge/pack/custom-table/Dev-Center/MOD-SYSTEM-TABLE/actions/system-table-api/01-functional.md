# System Table API

> **Screenshot verification (2026-10-08).** ⚠️ Not verifiable by screenshot - this action documents
> the `v1/system-tables` API endpoints and has **no dedicated admin screen**. The admin that calls
> these routes (the System Table list / detail) was captured in the sibling actions; on this int DB
> those screens are empty or error because `ProductInformationOverrides` is not seeded, so the
> endpoints were not exercised in this pass. The endpoint contract is in 06-api.md.

## 1. What it is

The system table API provides three endpoints to list, view, and rename system tables. System tables are platform-defined tables that cannot be created or deleted through the API. Currently, the only system table is "Product Information Overrides".

## 2. Where you do it

These are API-only endpoints at `v1/system-tables`. The admin calls them behind the scenes. There are no webstore, Commerce Portal, or B Store equivalents.

Field and data operations use the shared custom table API routes (`v1/custom-table-fields/` and `v1/custom-table-data/`) which are documented in the system-table-fields and system-table-data actions.

## 3. Who can do it

Any caller with a valid Znode API bearer token can use these endpoints. No additional permission attribute is specific to system tables.

## 4. Step by step

### List system tables
Call `GET v1/system-tables` with optional paging, sorting, and filtering parameters. The API automatically filters to show only system-defined tables.

### Get one system table
Call `GET v1/system-tables/{tableKey}` with the table's key (e.g. `ProductInformationOverrides`). Returns the table's ID, key, and display name.

### Rename a system table
Call `PUT v1/system-tables/{tableKey}` with a body containing the table ID and the new display name. Only the display name is updated; the table key cannot be changed.

## 5. What is allowed and what is not

- You **can** list all system tables.
- You **can** get the detail of a specific system table by its key.
- You **can** rename a system table's display name.
- You **cannot** create a new system table. No POST route exists.
- You **cannot** delete a system table. No DELETE route exists. If you attempt to delete via the custom table delete API, it is explicitly blocked with the message "Deleting System Tables is not allowed".
- You **cannot** change the table key of a system table. The PUT endpoint silently ignores any table key value in the request body.

## 6. Messages you may see

| Message | When it appears | When it does not |
|---|---|---|
| "Deleting System Tables is not allowed" | Attempting to delete a system table via the custom table delete API | When using only system table routes (no delete route) |
| "Id cannot be less than 1." | PUT with TableId less than 1 | When a valid TableId is provided |
| "The requested table does not exist" | GET with a tableKey that does not exist or is not system-defined | When a valid system table key is used |
| Model null error | PUT with an empty request body | When a valid body is provided |
| Update failure | PUT when the database save fails | On successful save |

## 7. How it differs

The system table API uses **separate routes** (`v1/system-tables/`) from the custom table API (`v1/custom-tables/`), but they share the same service class (`CustomTableService`). The key differences:
- System table routes pass `isSystemDefined=true` to the service.
- The list endpoint automatically filters to system tables only.
- The PUT endpoint prevents table key changes for system tables.
- No create or delete routes exist for system tables.

Calling the custom table edit endpoint on a system table works but allows table key changes, which the system table edit endpoint specifically prevents.

## 8. What can be combined

There are no combination rules for the system table API. Each endpoint operates independently.

## 9. What it changes elsewhere

- Renaming a system table changes its display name in the admin grid and detail views.
- It does not affect the physical table name, the data, or any runtime behavior.
- The table key remains unchanged, so all field and data operations continue to work.

## 10. Quick answers

**Q: Can I create a system table via the API?**
No. There is no `POST v1/system-tables` route. System tables are platform-defined.

**Q: Can I delete a system table via the API?**
No. There is no `DELETE v1/system-tables` route. The custom table delete API explicitly blocks system tables.

**Q: Can I rename the table key?**
No. The PUT endpoint silently ignores the table key in the body when updating a system table.

**Q: What is the difference between v1/system-tables and v1/custom-tables?**
`v1/system-tables` filters by `IsSystemDefined=true` and has only GET and PUT (no POST or DELETE). `v1/custom-tables` filters by `IsSystemDefined=false` and has full CRUD.

**Q: Do system tables use stored procedures?**

**Q: What authentication is needed?**
Standard Znode API bearer token. No system-table-specific permissions.

**Q: How many system tables exist?**
Currently one: `ProductInformationOverrides` (CustomTableDetailId=2).

## 11. For developers

See `03-frontend-admin.md` for the admin-to-API mapping, `06-api.md` for the full API contract, `07-functions.md` for the service logic, and `08-database.md` for the database details.

## Fields and options

| Endpoint | Purpose | Notes |
|---|---|---|
| `GET v1/system-tables` | list system-defined tables | returns empty on this int DB |
| `GET v1/system-tables/{tableKey}` | get one system table | errors for `ProductInformationOverrides` here (row absent) |
| `PUT v1/system-tables/{tableKey}` | rename the display name only | key write is skipped for system tables |

These are API-only; there is no screen to capture. ⚠️ Not verifiable live in this pass.

## Screenshot verification (2026-10-08)

| Screenshot | Shows | Result |
|---|---|---|
| (none) | API-only action - no dedicated admin screen | ⚠️ Not verifiable |

See the sibling actions (system-table-list, system-table-detail) for the admin screens that call these routes.
