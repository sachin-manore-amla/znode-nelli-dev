---
name: sdk-custom-tables
description: Everything about Znode V10 Custom Tables and System Tables - what they are for and not for, the Dev Center screens, field types and the exact values each accepts, the Global Settings that cap field length, every rule and message, the 30-operation Dynamic Data Table API, CSV import and export, the system table behind Product Information Overrides, how SDK and Webstore code reads a custom table, design recipes and the behaviours that surprise people. Use whenever a requirement needs extra structured data, a mapping or lookup list, a feature flag, an ERP id cross-reference, or any question mentions custom tables, table keys, field codes, or the custom table API.
user-invocable: false
---

# Znode Custom Tables

A Custom Table lets an administrator define a small table of their own (a key, a name, columns called fields) and fill it with rows, through Dev Center, the API or a CSV import. No code is needed to create or fill one. Znode stores it as a real table with real columns, so a unique field is a true uniqueness guarantee.

**It is for reference data, mappings, lookups, flags and light extensions.** The KB says so directly: custom tables are not a relational database and are not for core business data. Nothing in the storefront reads a custom table by itself: showing its data on a page needs a custom endpoint, a Webstore change, or one of the built-in features that use a system table.

Verified on a Znode 10 development environment (2026-10-05 and 2026-10-08, 10.14.x builds), in the product source, in the public KB and in the published API spec. Behaviour changes between releases (see `reference/known-behaviours.md`, release notes): confirm on the customer's version before promising an edge case.

## The ten facts that matter most

1. **Table Key** is the identifier: starts with a letter, letters and digits only, up to 100 characters, **never editable**. **Table Name** is the label: editable. Choose the key as a permanent name.
2. **Field Code** is the column name and the CSV header: letters and digits only, not all digits, up to 100, never editable, `Id` is reserved. **Field Type** is never editable either.
3. Six field types exist: `Text`, `TextArea`, `Number` (whole number), `Numeric` (decimal), `Boolean`, `datetime` (lowercase). The Admin dropdown shows five and its "Number" label creates `Numeric`. **A `Number` field cannot be created at all today** (the API fails with a server error): use `Numeric` with scale 0.
4. **One unique field per table**, only on Text or Number, and it cannot be added once the table has rows. A unique field is the right business key; the automatic `Id` row number is not stable across re-imports.
5. **No joins, no foreign keys, no composite keys.** Join in your own code. No row limit and no column limit are enforced; the KB advises at most 15 columns and about 50,000 rows for a 5 to 6 column table, and no more than one import an hour.
6. **Global Settings cap field length** (three "max" settings for Text, TextArea and Numeric, plus three "default" pre-fill settings): a blank "max" means NO ceiling, not "off". The KB's 4,000 and 8,000 are the largest values the Admin form accepts for Text and Text Area.
7. **Imports are CSV, headed by Field Codes, and upsert on the unique field** (blind insert, so duplicates, if the table has no unique field). Partial failures still report success: read the import log. Export is asynchronous and produces a ZIP of CSV parts.
8. **The API accepts any authenticated caller for every operation** (no per-role checks). Never expose it to a browser. Put your own endpoint with its own authorization in front of it.
9. **System tables** are shipped tables flagged as system-defined. The one that ships is `ProductInformationOverrides`; it cannot be deleted and feeds the storefront. See `commerce-product-overrides`.
10. **Deleting a table, a field or all rows is permanent**, with no undo and no reference check.

## Where to read next

| Need | File |
|---|---|
| What it is, vocabulary, when to use it, fair-usage limits, KB vs product | [reference/concepts-and-limits.md](reference/concepts-and-limits.md) |
| Field types, accepted values, lengths, Global Settings | [reference/field-types-and-values.md](reference/field-types-and-values.md) |
| Dev Center screens, step by step, roles and permissions | [reference/admin-screens.md](reference/admin-screens.md) |
| The API: 30 operations, shapes, errors, status codes | [reference/api.md](reference/api.md) |
| CSV import and export | [reference/import-export.md](reference/import-export.md) |
| System tables and Product Information Overrides | [reference/system-tables.md](reference/system-tables.md) |
| Using a custom table from Custom API SDK and Webstore code | [reference/using-from-code.md](reference/using-from-code.md) |
| Every message and when it appears | [reference/messages.md](reference/messages.md) |
| Recipes and anti-patterns | [reference/design-patterns.md](reference/design-patterns.md) |
| Behaviours to know, version notes | [reference/known-behaviours.md](reference/known-behaviours.md) |

## Nelli-Dev decision guide

| Requirement | Verdict | Why and how |
|---|---|---|
| Map ERP customer or product ids to Znode ids | **Supported** | A custom table with a unique key field; fill by import. KB lists it as a recommended use. |
| A lookup list (regions, store codes, tags, segments) used by custom code | **Supported** for storage, **Customizable** for use | Table is configuration; reading it from a storefront or a calculation needs a custom endpoint or Webstore change. |
| A feature flag or eligibility list (special discount access for selected customers) | **Supported** for the data, **Customizable** for the behaviour | Store the customer ids in a table; the discount logic that reads it is a promotion extension or method override: confirm that code can reach the table (see `using-from-code.md`). If the rule can be a price list on an account or profile, that is Supported with no table. |
| An extra field on one existing record (product, account, user, store) | **Not this**: use PIM attributes (`commerce-product-attributes`) or Global Attributes / user-defined fields (`config-global-attributes`) | A custom table row is a separate record; a field on the entity shows in the entity screens and APIs. |
| Different product name or description per store, account or locale | **Supported**: `commerce-product-overrides` | The system table already exists. |
| Large, fast-changing or transactional data; data needing relationships or reporting across tables | **Not supported by design** | Use your own database behind a Custom API endpoint, or an ERP integration. |
| Direct SQL access to the custom table's database | **Not supported** | The KB says the Custom API has no direct database or Entity Framework access. Use the Dynamic Data Table API. |
| Change what a system table does, or create a new system table | **Needs platform change** | System-defined cannot be set through any endpoint. |

## Related

`commerce-product-overrides` · `config-global-attributes` · `commerce-product-attributes` · `sdk-custom-api` · `sdk-conventions` · `api-catalog` · `api-auth-and-headers` · `config-import-export` · `sdk-extension-settings`
