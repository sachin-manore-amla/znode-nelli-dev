# Fields, scoping keys and rules

What this answers: every override field with its CSV header and API name, which fields form the key, length limits, what is validated and the exact messages.
Read it before importing data or calling the create and update APIs.

## Fields

| Admin label (as shown) | CSV header (field code) | API field name | Required in KB | Notes |
|---|---|---|---|---|
| Locale | `Locale` | `LocaleCode` | Yes | Locale code such as `en-US`. Free text. |
| PIM SKU | `SKU` | `SKU` | Yes | The original product SKU. Free text. |
| Store Code | `StoreCode` | `StoreCode` | Yes | The store's code, for example `DemoStore`. Free text. |
| Catalog Code | `CatalogCode` | not in the create/update body | no | Shown on some builds only (a ninth field). See gaps. |
| Account Code | `AccountCode` | `AccountCode` | No | Empty means "all accounts of the store". |
| Alt SKU | `AltSKU` | `AlternateSku` | No | Display only. |
| Alt Product Name | `AltProductName` | `AlternateProductName` | No | |
| Alt Short Desc | `AltShortDescription` | `AlternateShortDescription` | No | |
| Alt Long Desc | `AltLongDescription` | `AlternateLongDescription` | No | |

Observed in the Admin (module guide, build 10.14.5.0, 2026-10-13): the form and `Manage Fields` list nine text fields (eight on an older environment), none unique, and the field code and field length boxes are read-only. All fields are free-text boxes: there is no store, locale or account drop-down, and no "required" mark on the form. (module guide, 85)

## Scoping key and uniqueness

- The record is identified in practice by SKU + Store Code + Locale + Account Code. (KB read in full, 80)
- Nothing enforces uniqueness. A second record with the same four values is saved silently, in the Admin, by import and by API. (product source, 90)
- With duplicates, the override APIs fail with: `An error occurred while retrieving product override data due to multiple entries found in the custom table...` The API reference says that when several exist "one of those entries" is returned: observed behaviour depends on the endpoint, so treat duplicates as a defect to prevent. Release 10.8.0.0 made the duplicate error clearer.
- Editing the record in the Admin allows changing every field including SKU, store, locale and account (none is locked). Last write wins; there is no concurrency check.

## What is and is not validated

| Check | Where | Result |
|---|---|---|
| Referential check of SKU, store, locale, account, catalog | none on save | any text accepted. A record that matches no product, no active locale, no store or a store not on the catalog being published is ignored at publish with no message. |
| At least one field has a value | API create | `Model can not be null.` (status 400) |
| Field length | API create and update | `Input for {field} cannot exceed the maximum character limit of {max}.` (400). The limits are the `Field Length` values in `Manage Fields`. The Alt SKU length is not checked by the API. |
| Filter present | API update and delete | Update: `At least one filter parameter and model parameter must be provided.` Delete: `At least one filter parameter must be provided.` |
| Nothing matched | API update, delete | Update: `No record found.` (404). Delete: `No product override records match the specified filters.` (404) |
| `Please select at least one record.` | Admin grid, Tools > Delete with nothing ticked | popup titled `ERROR!!` with OK |
| `Confirm Delete?` | Admin grid delete | Ok / Back; delete is permanent (hard delete) |
| Save result | Admin | `Record created successfully.` / `Record saved successfully.` / `Deleted successfully.`; failures `Failed to create the record.` / `Failed to update.` |

(Messages: product source and module guide, 90 and 85.)

## Length limits

The Admin and API enforce the `Field Length` shown in `Manage Fields`. Observed values on the module-guide environment (build 10.14.5.0): Locale 50, PIM SKU 50, Store Code 100, Catalog Code 100, Account Code 100, Alt SKU 50, Alt Product Name 100, Alt Short Description 300, Alt Long Description 500. The storage behind them is wider, so a long value can fit storage and still be refused by validation. Check your own environment's `Manage Fields` before importing long text. Changing the lengths is part of the restricted schema (see limits-and-known-behaviours.md). (module guide, 85)

## Blank alternate fields

Only fields with a value are stored. At read time, a blank alternate name, short description or long description falls back to the base product's value; a blank alternate SKU leaves the original SKU. (product source, API reference, 90)
