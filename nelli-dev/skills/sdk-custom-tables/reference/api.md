# The Dynamic Data Table API (custom tables)

What this answers: every operation, what it takes and returns, how rows are shaped, the error formats and the status codes you will really see.

Source of the operation list: the published API reference ("Dynamic Table Data API", https://apidocs.znode.com/docs/custom-table-api). 30 operations. Observed behaviour: a Znode 10 development environment, 2026-10-05, confirmed in the product source. The spec file for scripted checks is `nd-knowledge/specs/custom-table.json` (`nd_query_spec.py op custom-table "<route>"`).

## 1. Calling it

- Base: your API gateway host. Paths below start with `/v1/`.
- Authentication: every request needs `Authorization`. The API reference says Basic or JWT Bearer; JWT is recommended; HTTPS only (plain HTTP is blocked). Missing, invalid or expired credentials are rejected with 401. See `api-auth-and-headers`.
- Send `Content-Type: application/json` and `Accept: application/json`.
- Keep the credentials in your environment, never in code or chat. Example (PowerShell):

```powershell
curl.exe -s "https://<gateway>/v1/custom-tables?pageSize=10" -H "Authorization: Basic $env:ZNODE_API_BASIC" -H "Accept: application/json"
```

- **No per-role or ownership check exists on this API.** Any caller with valid credentials can read, change or delete any table. Do not call it from a browser; wrap it in your own endpoint.

## 2. Operations

### Tables

| Method | Route | Purpose |
|---|---|---|
| GET | `/v1/custom-tables` | list custom tables (filter, sort, paging). System tables are excluded. |
| POST | `/v1/custom-tables` | create (`tableKey`, `tableName`) |
| GET | `/v1/custom-tables/{tableKey}` | one table's details |
| PUT | `/v1/custom-tables/{tableKey}` | rename (only the name changes) |
| DELETE | `/v1/custom-tables/{tableKeys}` | delete one or several (comma-separated keys) |
| POST | `/v1/custom-tables/bulk-delete` | delete several in one call (per-key result) |
| GET | `/v1/custom-tables/{tableKey}/record-exists` | does the table hold rows? **`IsSuccess: true` means rows exist** |

### Fields

| Method | Route | Purpose |
|---|---|---|
| GET | `/v1/custom-table-fields/{tableKey}` | list a table's fields |
| POST | `/v1/custom-table-fields` | create fields: body is a **JSON array** |
| PUT | `/v1/custom-table-fields` | update fields: body is an array; each needs `FieldId` |
| DELETE | `/v1/custom-table-fields/{fieldCode}/{tableKey}` | delete one field (note the order: field code first) |

### Rows

| Method | Route | Purpose |
|---|---|---|
| POST | `/v1/custom-table-data` | **insert a row** (field code and value pairs). The reliable insert. |
| PUT | `/v1/custom-table-data` | update a row by `Id` (send every value: treat it as a replace) |
| PUT | `/v1/custom-table-data/{tableKey}/{rowId}` | update a row addressed in the route |
| GET | `/v1/custom-table-data/{tableKey}/records` | all rows plus the field definitions (what the Admin grid uses) |
| GET | `/v1/custom-table-data/{tableKey}` | rows with filtering, sorting and paging |
| GET | `/v1/custom-table-data/{tableKey}/{rowId}` | one row in form shape (accepts `rowId` 0 for an empty form) |
| GET | `/v1/custom-table-data/{tableKey}/rows/{rowId}` | one row as a flat object of values (`rowId` at least 1) |
| GET | `/v1/custom-table-data/{tableKey}/unique/{uniqueValues}` | find a row by the unique field's value |
| POST | `/v1/custom-table-data/{tableKey}/insert` | insert exactly one row: body is a JSON **array of one object** |
| POST | `/v1/custom-table-data/{tableKey}/bulk-insert` | insert many rows (array of flat objects) |
| PUT | `/v1/custom-table-data/{tableKey}/bulk-update` | update many rows (needs a unique field) |
| DELETE | `/v1/custom-table-data/{tableKey}/{rowId}` | delete one row |
| DELETE | `/v1/custom-table-data/{tableKey}/{rowIds}/bulk` | delete rows by id list |
| DELETE | `/v1/custom-table-data/{tableKey}/{columnName}/{columnValue}/bulk` | delete every row where a column equals a value |
| DELETE | `/v1/custom-table-data/{tableKey}` | delete **all** rows (the filter parameter is required by the spec; the table stays) |

### Import and export

| Method | Route | Purpose |
|---|---|---|
| GET | `/v1/custom-table-data/{tableKey}/table-template` | the CSV template (headers are Field Codes) |
| POST | `/v1/custom-table-data/import` | start an import: see `import-export.md` for the real contract |
| GET | `/v1/custom-table-data/{tableKey}/export` | queue an export |
| GET | `/v1/custom-table-data/{tableName}/download` | download an export (takes the table **name**, not the key) |

System tables have three routes that are in the product but not in the published spec: see `system-tables.md`.

Query parameters on list and read operations (from the spec): `filter` (array), `sort` (object), a page index, `pageSize`; `records` and `export` also take `expand`; `records` takes `publishState`.

## 3. Request shapes

Create a table:
```json
{ "TableKey": "Regions", "TableName": "Regions" }
```

Create fields (always an array):
```json
[ { "TableKey": "Regions", "FieldCode": "RegionCode", "FieldName": "Region Code",
    "FieldType": "Text", "FieldLength": "50", "DisplayOrder": 1, "IsUniqueConstraint": true } ]
```
Required: `TableKey`, `FieldCode`, `FieldName`, `FieldType`, `DisplayOrder`, `FieldLength` (as text). Since 10.12.1.0 the field API no longer needs `TableId`.

Insert a row (code and value pairs):
```json
{ "TableKey": "Regions",
  "CustomTableFieldDataList": [ { "FieldCode": "RegionCode", "FieldValue": "EAST" },
                                { "FieldCode": "RegionName", "FieldValue": "East region" } ] }
```
The published spec marks `tableId` required for this body; inserts worked on the development environment without it. Include it if your version insists.

Update a row: same shape plus `"Id": <row id>`.

Bulk insert, bulk update and the single `/insert`: a flat array keyed by field code, for example `[ { "RegionCode": "NORTH", "RegionName": "North region" } ]`. Three row shapes exist in the API (code/value pairs, flat objects, and the form shape on reads): do not mix them up. A bare object where an array is required fails.

## 4. Responses to know

- **Insert** returns 201 and the new row with its `Id`: keep it if you will update or delete. Field metadata echoed in that response (`FieldId: 0`, `FieldLength: null`) is not real: read the schema from the fields endpoint or from `/records` (`CustomTableFields`).
- **`/records`** returns **every row, unpaged** (page size is the maximum integer) plus `CustomTableFields`. Entries with `FieldId: 0` and the code `TableKey` are not real columns: filter them out. Use `GET /v1/custom-table-data/{tableKey}` with paging for large tables.
- **Update** returns 201 on the development builds (the spec says 200). **Delete** returns `{"IsSuccess": true}`.
- **Some GET responses are double-encoded JSON** (a JSON string that contains JSON): `/records`, `/record-exists`, `/v1/custom-table-fields/{tableKey}` and the system-table routes were observed this way. Parse once, and if the result is a string parse again. Create, update and delete responses are plain JSON. Re-check on your version.
- Only the unique field gives you a stable key. The row `Id` can change when a table is re-imported: never store it in another system. Look rows up with `/unique/{value}`.

## 5. Errors

Two shapes:

```json
{ "ErrorCode": 400, "HasError": true, "CustomModelState": { "TableKey": "The Table Key field is required." } }
```
```json
{ "ErrorCode": 10, "HasError": true, "ErrorMessage": "Deleting System Tables is not allowed" }
```
Field-level failures echo the field with a message inside the list:
```json
{ "CustomTableFieldsList": [ { "FieldCode": "Notes", "FieldValidationMessages": "Input value must not exceed the maximum character limit of 100." } ],
  "ErrorCode": 400, "HasError": true }
```
Read all three places: `ErrorMessage`, `CustomModelState`, and `FieldValidationMessages` inside the list. Exact texts are in `messages.md`.

## 6. Status codes you will actually see

| Code | When |
|---|---|
| 200 | successful GET, PUT, DELETE |
| 201 | successful create, and (observed) a successful row update |
| 400 | validation failure, malformed body, duplicate table key (*Table Key Already Exist*, case-insensitive; the spec says 409) |
| 401 | authentication missing or invalid |
| 404 | table or row does not exist, and (observed) deleting a system table |
| 500 | unhandled errors, including a bare object where an array is required (some bodies give a 400 that names no field: `{"ErrorCode":400,"ErrorMessage":[{"":"cannot be null"}]}`) and any `Number` field creation |

The published spec also lists 207, 409 and 422 on some operations. They were not seen in testing. Handle them if they appear, but do not depend on them.

## 7. Events

Single-row create (POST `/v1/custom-table-data`), single-row update and single-row delete raise a `CustomTableData` event (Created, Updated, Deleted). Bulk insert, bulk update, bulk delete, import, and delete by value or filter do **not** raise events (product source, 2026-10). If an integration must react to custom table changes, use the single-row routes or poll.

## Sources

Published API reference and spec; KB https://support.znode.com/support/solutions/articles/43000757107-managing-custom-tables; observed on a development environment (2026-10-05); release notes 10.12.1.0 and 10.14.0.0 (stricter request validation, so some of the observed 500s may now be 400s: re-check on the customer's version).
