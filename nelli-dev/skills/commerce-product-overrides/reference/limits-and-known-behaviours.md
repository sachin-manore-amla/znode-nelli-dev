# Limits, behaviours to know, version notes and KB differences

What this answers: the tested limits, the surprising behaviours (stated neutrally), how the system table is protected, and where the Knowledge Base and the product differ.

## Limits

| Limit | Value | Enforced? |
|---|---|---|
| Records | Tested and reliable up to about 100,000. Beyond that indexing and search can slow or operations can fail. | Advised, not enforced (KB, release 10.6.2.0) |
| SKUs per `multiple-products` call | 32 | Enforced (product source) |
| Field lengths | The `Field Length` values in `Manage Fields` | Enforced by Admin and by create/update API (not for Alt SKU in the API) |
| Sorting and pagination of SKU lookups | Not supported | n/a |
| Elasticsearch tuning | KB recommends tuning (shards, queries, resources) for very large tables | Advice |

## Behaviours to know

| Behaviour | Detail |
|---|---|
| No validation on save | Any text is accepted for SKU, store, locale, account. A mismatch shows only as "override not applied". Check codes against the product, store and locale lists before import. |
| Duplicates | Silent on save; error at read. Release 10.8.0.0 returns a clearer conflict error. |
| Orphans | Deleting a product, store or locale does not delete its override records. They are skipped at publish. |
| Draft status | KB: adding or editing does not move the product to Draft. Product source: an Admin save of a record does set the product and its parents to Draft; the API save does not. Either way, run a full catalog publish. |
| Delete is permanent | Single and bulk delete are hard deletes; the override stays in search until the next full catalog publish. |
| Product-level publish | A product publish fetches override records for the whole catalog, not just that product, and the finishing step resets the pending flag for all catalogs. Concurrent publishes of different catalogs can therefore affect each other's pending overrides. (module guide, from source, 85; verify before relying on it) |
| Variants without a category | Variants linked to a parent but not to a category are not returned by the override APIs and are not found by default search. Link the variant to a catalog category. |
| Stock Webstore | Does not call override routes (see publish-indexing-and-fallback.md). |
| Publish History | Does not show override indexing time. |
| Alternate SKU | Display only; not independently searchable. |
| Grid search | An apostrophe in the grid filter broke the saved view on one build. |
| Admin add/edit | Failed on one development build (10.14.5.0) with `Failed to create.` / `Failed to update record.`; delete worked. |

## The system table `ProductInformationOverrides`

- It is a Custom Table flagged system-defined: it ships with Znode and cannot be deleted from the Admin or the Custom Table API (`Deleting System Tables is not allowed`, returned with status 404).
- You may read it, add, edit and delete rows, import and export. (custom table module guide, 85)
- The KB says the UI cannot delete it but direct database access can, and that this causes data loss or malfunction. Customers should not have or use direct database access.
- Changing its schema or field details (adding fields, renaming field codes, changing lengths) is restricted: other parts of Znode read it on a fixed layout. The KB: "Adding new fields to this custom table is restricted" and "Changing the existing override schema or field details causes functional failure".
- Metadata lengths differ from the physical column widths; validation follows the metadata.
- There are undocumented system-table endpoints in the custom table API (list, get, PUT edit). Do not use the PUT to alter this table's fields.

## Version notes

| Version | Date | Change |
|---|---|---|
| 10.6.2.0 | 23 Jan 2026 | Feature introduced with the known limitations above |
| 10.8.0.0 | 4 Mar 2026 | Clearer duplicate conflict error; suggestions API accurate counts and account/store scoping; full-text override search respects `Znode-AccountCode`; override data publishes reliably with base product data |

## Knowledge Base versus product (product wins)

KB article: https://support.znode.com/support/solutions/articles/43000778646-how-to-setup-product-information-overrides

| Topic | KB says | Product shows | Evidence |
|---|---|---|---|
| Draft status | Adding or editing overrides does not change publish status to Draft | Admin save marks the product and parents Draft; API save does not | module guide, from source |
| Required fields | SKU, Locale Code, Store Code required | The form shows no required mark and the API requires only that one field has a value | module guide, product source |
| Fallback with account | (not stated) | API reference says account falls back to store-level; code does an exact match | product source vs API reference |
| Length limits | Not stated | Field lengths come from `Manage Fields` | product source |
| CSV layout | Not stated | Header `Locale,SKU,StoreCode,AccountCode,AltSKU,AltProductName,AltShortDescription,AltLongDescription` | module guide |
| Storefront | "Storefront shows overrides when the required API implementation is in place" | The stock Webstore does not call the override APIs | Webstore source |
| Catalog Code | Not stated | A ninth field appears on some builds | module guide |
