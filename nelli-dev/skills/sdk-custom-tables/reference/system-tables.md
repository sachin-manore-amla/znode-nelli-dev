# System tables

What this answers: what a system table is, what you may and may not do to one, the three system-table routes, and the one that ships (Product Information Overrides).

## What a system table is

A custom table that Znode ships, flagged system-defined. It uses the same storage, field types and row endpoints as any custom table. It exists so a Znode feature can use the custom table machinery.

| | |
|---|---|
| Table Key shipped | `ProductInformationOverrides` (Table Name: Product Information Overrides) |
| Purpose | override product text per store, per account and per locale without changing the product |
| Where you manage it | PIM > Product Information Overrides in Admin (not Dev Center > Custom Tables) |
| Full feature guide | `commerce-product-overrides` |

System tables do not appear in `GET /v1/custom-tables` or on the Custom Tables list. They are listed by `GET /v1/system-tables`.

## What you may and may not do

| Action | Allowed? | Notes |
|---|---|---|
| Read the table, its fields and rows | Yes | the ordinary endpoints work |
| Add, edit, delete rows; import and export | Yes | the intended use |
| Rename it (display name) | Possible, not advised | `PUT /v1/system-tables/{tableKey}` changes the display name only; leave it as shipped |
| Add or remove fields | Not blocked, **do not** | other parts of Znode read it on a fixed layout; the KB for Product Information Overrides warns that changing its schema causes functional failure |
| Delete the table | **No, always refused** | *Deleting System Tables is not allowed* (HTTP 404, a wrong status for a business rule; a bulk delete containing a system table is refused too) |
| Create your own system table | **No** | `IsSystemDefined` cannot be set through any endpoint; this is a platform change |

## The three system-table routes

In the product, not in the published spec:

| Method | Route | Purpose |
|---|---|---|
| GET | `/v1/system-tables` | list system tables (response is double-encoded JSON: parse twice). A filter that matches nothing returns 200 with an empty list. |
| GET | `/v1/system-tables/{tableKey}` | one system table's details. An unknown key: 404 *The requested table does not exist*. A **custom** table's key returns 200 with an empty model. |
| PUT | `/v1/system-tables/{tableKey}` | edit the display name |

Take care with the neighbouring routes: field routes (`/v1/custom-table-fields`) and `PUT /v1/custom-tables/{tableKey}` have no system-table guard, so a careless call can alter the shipped table. Never send a system table's key or id there.

## Product Information Overrides, in brief

| Column | Meaning |
|---|---|
| `Locale` | locale code, for example `en-US` |
| `SKU` | the original product SKU (required) |
| `StoreCode` | the store code (required) |
| `AccountCode` | optional: an account-specific override |
| `AltSKU`, `AltProductName`, `AltShortDescription`, `AltLongDescription` | the alternate values (all optional) |

1. A record should be unique on SKU, store code, locale and account code. The KB says a duplicate returns an error, but the product source shows no check on save: a duplicate saves silently and fails later at search time. Validate before you import. See `commerce-product-overrides`.
2. The feature is **disabled by default** and needs both the global and the store-level Enable Product Information Overrides setting (see `commerce-product-overrides`).
3. Adding or updating a row through the single-row API marks the product's publish state, so a **full catalog publish** (not "Publish Draft Products Only") is needed before overrides appear.
4. **Validation uses lengths recorded in the table's metadata, which are smaller than the real column widths** (for example SKU is validated at 50 although the column holds 300; StoreCode 100 vs 200; the description fields 300 and 500 although the columns are unlimited). A 200-character SKU is therefore refused although the column could hold it.
5. Tested reliably to 100,000 records (KB); large tables affect the search index (shard sizing).

## Sources

Verified on a development environment (2026-10-05) and in source; KB How to Setup - Product Information Overrides https://support.znode.com/support/solutions/articles/43000778646-how-to-setup-product-information-overrides (the KB itself does not document the system-table routes).
