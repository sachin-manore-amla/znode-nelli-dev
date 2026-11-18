# Concepts, vocabulary and limits

What this answers: what a custom table is, the words used everywhere, when to use one and when not, the advisory limits, and where the KB and the product disagree.

## What it is

1. Your own table, created in Dev Center without a developer: a **Table Key**, a **Table Name**, then **fields** (columns), then **rows** (records).
2. Stored as a real SQL table with real columns and constraints, not a JSON blob.
3. Read and written through Admin, the Dynamic Data Table API, or CSV import.
4. Every table gets an automatic whole-number row id called `Id`. You never create it and cannot name a field `Id`.

Example: `Regions` (`RegionCode`, `RegionName`) and `Vendors` (`VendorCode`, `RegionCode`). Znode does not link them: you fetch both and join in your own code.

## The two pairs people confuse

| | Table Key | Table Name |
|---|---|---|
| Is | the identifier | the display label |
| Used in | API routes, the CSV import target, code | Admin screens |
| Rule | starts with a letter, then letters and digits, max 100 | starts with a letter; letters, digits, single spaces, underscores, hyphens; max 100 |
| Editable later | **No** | Yes |

| | Field Code | Field Name |
|---|---|---|
| Is | the column name | the display label |
| Used in | API payloads, **CSV header** | Admin screens |
| Rule | letters and digits only, not all digits, max 100, not `Id` | required, max 100 |
| Editable later | **No** | Yes |

The commonest import mistake is putting Field Names in the CSV header: `Store Code` fails, `StoreCode` works.

## Other terms

| Term | Meaning |
|---|---|
| Field Type | The kind of data: `Text`, `TextArea`, `Number`, `Numeric`, `Boolean`, `datetime`. Never editable after save. |
| Field Length | The size limit; for `Numeric` the string `"precision,scale"`, for example `"10,2"`. |
| Display Order | Order of fields on screen (admin default 500). Not stored order. |
| Is Unique | At most one field per table; makes that field the business key. |
| System table | A table shipped by Znode, flagged system-defined. See `system-tables.md`. |
| Template | The empty CSV with correct headers that you download before an import. |

## When to use a custom table

Good fits (all from the KB's Limitations and Fair Usage article):

1. Temporary or transitional data, such as mapping legacy ids to new ids during a migration.
2. External reference mapping: ERP customer id to Znode customer id, external product id to SKU.
3. UI-level data extensions: a "Special Handling Note", a priority label, internal remarks.
4. Small mappings: customer to tag, product to label, region to attribute.
5. Basic business rules: flags, thresholds, eligibility such as free shipping above a value.
6. Configuration and lookup data: customer type codes, order status lists, Gold/Silver/Bronze segments.
7. Lightweight reporting inputs: tags for filtering reports.
8. Feature flags and conditional controls: express checkout eligibility, special discount access for selected customers.

Poor fits:

1. Large or fast-changing data, or data expected to grow a lot.
2. Anything that needs relationships between datasets or reports across tables.
3. Real-time or transactional data, high-frequency integration data.

## Advisory limits (KB) versus enforced limits (product)

| Item | KB advice | Enforced by the product? |
|---|---|---|
| Columns | avoid more than 15; recommended 10 to 15 | **No** |
| Rows | about 50,000 for 5 to 6 columns, fewer with more columns | **No**. Tested reliably to 100,000 records on the Product Information Overrides table (KB). |
| Import frequency | avoid several per hour; prefer batches | **No** |
| Joins, foreign keys, composite keys | not supported | Not available at all |
| Text | up to 4,000 characters | The ceiling is a Global Setting; the Admin form accepts up to 4,000 for it; absent if blank |
| Text Area | up to 8,000 characters | The ceiling is a Global Setting; the Admin form accepts up to 8,000 for it; absent if blank. Lengths above 4,000 are stored as unlimited text |
| Number | "up to 38 digits (38/38)" | True of `Numeric`; `Number` is a 32-bit integer |
| Concurrent imports | only one at a time | **Not enforced** in the import path as observed: treat concurrent imports as unsafe |
| Table count | "keep limited" | No cap |

Exceeding an advisory limit degrades performance (more storage, slower queries, slower API responses) rather than failing a request. The KB asks for periodic cleanup and archiving.

## Where the KB and the product differ

| KB says | Product (observed, source) |
|---|---|
| Text Area 8,000 | The figure matches the largest value the Global Setting form accepts; the field validation itself has no fixed 4,000 or 8,000 limit and applies only the configured setting |
| Field types: Text, Text Area, Number, Boolean, Date and Time | Six types; "Number" on screen creates `Numeric`; the integer `Number` type cannot be created; the date type value is lowercase `datetime` |
| Field Length is optional | Required for Text, TextArea, Numeric (and, if you try, Number) |
| "Number is required" on records | No mandatory-field rule is enforced on insert or import (only the unique field must be present) |
| Only Field Name and Display Order editable | Field Length and Is Unique are editable too (Is Unique not once rows exist) |
| One import at a time | No lock found |
| Delete Record path listed under Add New | Wrong path in the KB; deletion is from the row list |
| One configurable setting ("Text Area value") | Three settings: Text, TextArea, Numeric |

Where they differ, tell the customer the product behaviour and cite the KB URL.

## Sources

- KB: Managing Custom Tables https://support.znode.com/support/solutions/articles/43000757107-managing-custom-tables
- KB: Custom Tables - Limitations & Fair Usage Guidelines https://support.znode.com/support/solutions/articles/43000782807-custom-tables-limitations-fair-usage-guidelines
- Published spec: Dynamic Data Table API (apidocs.znode.com, "Dynamic Table Data API")
