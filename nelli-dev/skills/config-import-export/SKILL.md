---
name: config-import-export
description: Znode bulk import and export - every importable entity with its template columns, create versus update behaviour, statuses and the failed-row log, custom import templates, the asynchronous import API (v2.1), PIM bulk product update from CSV, bulk price and inventory loading, SKU rules, limits, the Admin export screens and what the export API supports. Use when a customer needs to load, update or extract data in bulk, schedule an import, or when an import fails or does not appear on the storefront.
user-invocable: false
---

# Bulk import and export

## What it is
**Import** loads CSV files into Znode using a **template** (a mapping of CSV headers to attribute codes) per **import type**. **Export** writes CSV or Excel files from Admin lists. Terms people confuse: *Imports* (System Settings > Imports, generic, can create) versus *Bulk Update* (PIM > Products > Tools > Bulk Update, products only, never creates) versus *Data Exchange* (Commerce Connector, can run an import on a schedule).

## When to use / not use
| Need | Verdict |
|---|---|
| One-off or periodic load of products, prices, inventory, customers, categories | Supported: Imports screen |
| Same, automatically on a schedule from an ERP or file server | Supported: Data Exchange with Znode Import destination (`sdk-data-exchange`) |
| Update an attribute on many existing products | Supported: Bulk Update (reference 03) |
| Call an API to start an import from your own job | Supported: v2.1 import API (reference 02) |
| Delete data in bulk | Not supported by import (add and update only, except Catalog-Category Add or Delete). Use Admin or delete APIs |
| Scheduling inside the Imports screen | Not provided. Use a Data Exchange or an external scheduler calling the API |
| Export products, categories, prices, inventory to a file through an API | Not provided by the v2 export API (see reference 04). Read through list APIs with paging |

## The facts that matter most
1. Admin path: **System Settings > Imports** (list, Add New, Manage Templates) and **System Settings > Exports**.
2. The Admin upload accepts only a file with a **.csv** extension (message: "Only select file with a .csv extension."). The KB says "CSV or Excel": the product wins. UTF-8 recommended.
3. Imports run **in the background** inside the API process. Statuses: `Started`, `Completed Successfully`, `Completed With Errors`, `Failed`.
4. Imports only **add or update**. They cannot delete or clear a value (an empty cell does not clear; Yes or No columns become No).
5. **One import or export at a time**; the v2.1 API returns 409 "Import cannot be initiated because a catalog or export publish process is already in progress." while a catalog or export publish runs.
6. Imported products are **Draft** until published. Bulk Update sets touched products to Draft.
7. Scheduled or API-started imports have no signed-in user; the platform records the first admin user (v2.1 requires a `Znode-UserId` header greater than 0).
8. Bulk import operations **do not raise** Znode events (KB).
9. Failed rows are kept in the import log: Row Number, CSV Column Name, CSV Column Data, Error Description; downloadable as CSV, Excel or PDF.
10. Reserved words cannot be CSV headers or values: `type`, `_id`, `_index`, `_source`, `query`, `sort`, `size`, `from`, `aggs`, `aggregations`. The product import's `ProductType` column is a required exception (KB inconsistency).

## Decision guide for Nelli-Dev
| Requirement | Verdict and approach |
|---|---|
| Import prices from a file | **Supported.** Pricing import with `PricelistCode`, `SKU`, `RetailPrice` (+ SalePrice, tier columns, dates). Price list must exist. Large loads: Data Exchange from SFTP or Blob |
| Import 50,000 products nightly | **Supported, not in the Imports screen.** Data Exchange, daily, Znode Import (Product), batches of 1,000 to 10,000 rows, files under 50 MB, then publish. Expect minutes; follow status in System Settings > Imports |
| Inventory sync every 15 minutes | **Supported** with Data Exchange; inventory key is SKU + WarehouseCode, one row per pair |
| Update one attribute across thousands of SKUs | **Supported:** Bulk Update (SKU + attribute codes) |
| Create configurable products by import | Supported in two imports: configurable product rows, then Product Association (variants must exist) |
| Delete products by file | **Not supported.** Customizable with an external script calling delete APIs after approval |
| Custom CSV layout | **Supported:** Manage Templates, create a template mapping your headers to attribute codes |
| Let shoppers upload an order file | Not an import feature; Customizable via Quick Order or a custom endpoint |
| Trigger something when a bulk import finishes | **Not supported as an event** (imports raise none). Poll the import log status or end the Data Exchange with a step |
| Export all products nightly to a partner | Supported from Admin (Export To CSV or Excel) only manually; for automation, Customizable: page the product list API from your own job |

## Reference files
- `reference/01-entities.md` every import type: key, create or update, required and optional columns, rules
- `reference/02-import-process.md` Admin steps, templates, statuses and logs, import API v2.1 and legacy, async behaviour, limits, SKU rules
- `reference/03-bulk-product-update.md` PIM Bulk Update from CSV, file rules and messages
- `reference/04-export.md` export screens, types, the export API, what is not exported
- `reference/05-kb-vs-product.md` conflicts and version notes

Related: `sdk-data-exchange`, `commerce-catalog`, `commerce-promotions-and-pricing`, `commerce-inventory`, `commerce-promotions-and-pricing`.
