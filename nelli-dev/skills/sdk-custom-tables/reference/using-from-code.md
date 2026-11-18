# Using a custom table from Custom API SDK and Webstore code

What this answers: how customization code reads or writes a custom table, what is verified in the SDK, and what to confirm before relying on it.

## The rule

Custom tables are reached **through the Dynamic Data Table API**, never through direct database access. The KB's API Customization Guide states that the Custom API has no direct database or Entity Framework access (the SDK template contains a data-access helper that appears to contradict this: treat it as unsupported for Znode data).

## From the Custom API SDK (verified)

The SDK template already wires a custom table client:

- The `Znode10.CustomTable.Client` package is referenced by `Custom.Api.Core` (template pins `10.0.0-rc-01`).
- `CustomDependencyRegistration` registers it: `builder.Services.AddScoped<ICustomTableClient, CustomTableClient>();`
- The sample `CustomService` injects `ICustomTableClient` and returns the list: `return _customTableClient.GetCustomTables(null, null, 1, 10);` (filters, sorts, page index, page size) giving a `CustomTableDetailListResponse`. Errors are logged under the CustomTable component with `ZnodeLoggingEnum.Components.CustomTable` and an empty response is returned.
- The package ships the request and response models (verified by inspection of later builds): `CreateCustomTableDetailRequestModel`, `CreateCustomTableFieldRequest`, `EditCustomTableRequestModel`, `EditCustomTableFieldRequest`, `CustomTableFieldDataModel`, `CustomTableCreateFieldDataModel`, `CustomTableUpdateFieldDataModel`, `CustomTableBulkDataModel`, `ImportCustomTableModel`, `ExportModel`, `DownloadModel`, `SystemTableDetailModel`, and the response wrappers (`CustomTableDataListResponse`, `CustomTableFieldListResponse`, `CustomTableDetailResponse`, `TrueFalseResponse`, ...).

**Not verified:** the full member list of the client interface for the version your SDK pins. The `10.0.0-rc-01` package was not available to inspect, and later packages ship only the models. Before generating code against any client method other than `GetCustomTables`, read the package version in use (reflection or the IDE), or fall back to a typed HTTP call to the documented route. Do not invent method names.

## Pattern: a custom endpoint backed by a custom table

1. Add a service and controller in `Custom.Api.Core` as in `sdk-conventions` (interface, service, controller, registration).
2. The service reads the table through the client (or a typed HTTP client to `/v1/custom-table-data/{tableKey}/unique/{value}` or `/records`).
3. **Authorize in your endpoint.** The table API trusts any authenticated caller, so check that the shopper may see that row (their own account, store or customer id) before returning it.
4. **Return only the fields needed.** Do not return the whole `/records` payload: it contains every row and the schema.
5. **Cache** lookup data with a bounded lifetime and a stated invalidation rule (see `quality-performance-checks`): `/records` returns all rows unpaged and a Webstore page should not call it per request.
6. Log ids and counts only.

## From the Webstore

The Webstore does not read custom tables itself. To show a value on a page: UI component -> Webstore BFF route handler -> your Custom API endpoint -> custom table. Keep the secret and the API credentials on the server side (BFF), never in client code. See `webstore-customization`.

## From other extension points

| Extension | Can it read a custom table? |
|---|---|
| Event consumer (SDK) | Yes, with the client or an HTTP call (the SDK host has the client registered). Events are raised for single-row custom table changes only (see `api.md`). |
| Method override receiver (SDK) | Yes, as a normal endpoint. Keep it fast: it sits in the request path of a Znode operation. |
| Promotion extension | **Not verified.** The promotion context exposes only ids and a service provider. Whether a client can be resolved from it, and the cost of a remote call inside a calculation, has not been confirmed. Prefer passing the data some other way, or ask Znode. |
| Data exchange processor | Yes, it can call APIs (see `sdk-data-exchange`). |

## Writing to a custom table from code

Use the single-row routes if other systems must be notified (they raise events); use bulk routes or a data exchange for volume (no events). Make writes idempotent by keying on the unique field and using the upsert behaviour of import or bulk-update. Remember that update replaces the row: send every value.

## Security notes

- No encryption at rest is documented for custom table data; do not store secrets or card data. Treat personal data with care and avoid it unless required.
- Values are stored as sent: HTML and script text is not encoded. Encode when rendering.
- Never expose the Dynamic Data Table API or its credentials to a browser.
- Table deletion is permanent: restrict who holds credentials that can call DELETE.

## Sources

SDK sample code (`Custom.Api.Core` dependency registration and `CustomService`), package inspection, KB API Customization Guide (43000761402), observed behaviour 2026-10.
