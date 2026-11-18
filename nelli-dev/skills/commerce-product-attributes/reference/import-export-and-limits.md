# Import, export, limits and performance

What this answers: how attributes and attribute values are bulk loaded, what is not importable or exportable, and the limits and performance guidance that are enforced versus only advised.

## Import (System Settings > Imports)

Imports accept CSV or Excel (UTF-8 CSV recommended for special characters), run asynchronously and can only add or update, never delete. Bulk import does not fire platform events. (existing import guide and KB, 80)

| Import type | Create | Update | Key columns |
|---|---|---|---|
| Product Attribute | yes | no | `AttributeName`, `AttributeCode`, `AttributeType`, `DisplayOrder` |
| Attribute Default Value | yes | yes | `AttributeCode`, `AttributeDefaultValueCode`, `AttributeDefaultValue` |
| Product | yes | yes (match on SKU) | `ProductType`, `ProductName`, `SKU`, `IsActive` plus one column per attribute of the chosen family |

Rules for product import (module guide, 85):

- The family is chosen once per import (the `Family List` on `System Settings > Imports`), not per row. There is no family column. An existing SKU is moved to the chosen family.
- `Download Template` gives the family's columns, ordered by group display order, then attribute display order, then code. Columns the family lacks but the Default product family has are added.
- Create a new template when a family gets new attributes. A required attribute added to the family gives an import error for rows without it.
- Imports only use existing families. There is no import for families, groups or custom fields. Category import does not use group order.
- A custom import template can be created (KB: Creating a custom import template).
- V2: `GET /v2/imports/import-families/{importType}` lists families with templates; `POST /v2.1/imports/process-log/{importType}/{templateName}` starts an import; `GET /v2/imports/process-log-details/{importProcessLogId}` reads the error log.

Errors are exported from `System Settings > Export` (Failed Import Log Details). Built-in export of product data is not an Admin feature; use API reads.

Bulk edit of attribute values: `PIM > Products > Tools > Bulk Update` uses CSV with `SKU` plus attribute columns.

Option values (select attributes) can also be added in the Admin on the `Locale/Values` tab (each row saved with its own Save icon).

## Limits

| Item | Value | Enforced? |
|---|---|---|
| Attribute code, group code, family code length | 100 in the Admin (API family code up to 200) | Admin; API partly |
| Display order | 1 to 999 in the Admin | Admin only |
| Locale names, option names | 100 characters, no comma | Admin |
| Custom field code | 299 (Admin), 300 storage; keep under 100 for publish | Admin and storage |
| Custom field Text and Value | 300 each | Server |
| Number of attributes, groups, families, options | no limit stated in the KB | Not stated |
| Min and Max gram for ngram index settings | 1 to 99 | Admin |
| Variants per configurable product | KB sets no limit | Not stated |
| Max file size for File and Image attributes | set per attribute within the global maximum; defaults and maxima come from global settings (media attributes showed 20 MB, video 100 MB) | Admin |

## Performance guidance

Most of this is advice and inference, not an enforced limit. The KB gives no counts.

- Keep the number of attributes per family to what the product form needs: every family attribute is read when a product is opened, and every attribute with a value is published to every active locale of every store using the catalog.
- Each attribute flagged `Is used for facets` or `Is used in Search` adds index content and facet computation. Flag only what shoppers use.
- Prefer Simple or Multi Select for filterable values; free-text Text attributes are poor facets.
- Avoid attributes marked localizable unless the value really differs by language: each locale adds a published copy.
- Do not use custom fields for data on many products; they are per product, per language and cannot be bulk imported.
- A configurable product multiplies the published attributes by its variants; keep variant counts reasonable and check the product page speed after publish.
- Large imports and full catalog publishes are heavy; schedule them off-peak and let one finish before starting another (only one publish, import or export can run at a time on the module guide's environment: `A Publish or an Import or an Export is in progress. Only one Publish or Import or Export can be initiated at a time.`).
