# Product types and how they use attributes

What this answers: how simple, configurable, bundle and grouped products use attributes and families, and the rules for configurable attributes and variants.

## Summary

| Type | Attributes | Special rules |
|---|---|---|
| Simple | Values for all attributes of its family | None. Can be a variant of a configurable product, or a child of a grouped or bundle product. |
| Configurable | Parent holds the shared attributes; the attributes chosen as configurable are hidden on the parent form and each variant holds its own value | Needs a family with at least one attribute that has `Is Configurable` set. Family and the chosen configurable attributes are locked after save. |
| Bundle | Same as simple; children are simple products associated on the `Bundle Product` tab | A bundle with no child is not published |
| Grouped | Same as simple; children on the `Grouped Product` tab | A grouped product with no child is not published |

(KB read in full, 80; module guide, 85)

## Configurable products

Steps, as in the Admin:

1. `PIM > Products > Add New`, choose the `Attribute Family`, set `Product Type` to `Configurable Product`.
2. If the family has no attribute with `Is Configurable` set, the popup `Error!!` shows: `Family must have at least one configurable attribute which can be use to create a configurable product.` and the `Variants` tab is hidden.
3. Otherwise `Select Configurable Attributes` opens, with one tick box per configurable attribute, none ticked. Tick at least one and `Save`. With nothing ticked: `Select at least one configurable attribute which can be use to create a configurable product.`
4. On the `Variants` tab, associate products that have a value for every chosen attribute (normally simple products).

Rules (module guide, verified on a development environment 2026-10-09, 85):

- Only attributes with `Is Configurable` = Yes are offered. The Admin offers `Is Configurable` only on Simple Select attributes; an attribute of another type set through the API would still be offered (no server check). Do not do that.
- Minimum one configurable attribute, no maximum. The KB sets no variant limit.
- The look-alike (same combination) check is only in the Admin popup (rows greyed). The save and the API do not check for duplicate combinations, so integrations must.
- A product can be a variant of more than one parent. Inactive products can be candidates.
- If a configurable attribute is later turned off or deleted, the stored choice remains and still feeds publishing: do not delete or retype an attribute used by variants.
- A required configurable attribute is not asked for on the parent.
- Display order of the options in the storefront comes from the attribute value display order and the attribute display order.
- A configurable product with no variant is not published (publish-and-search-effects.md).
- `Display Variants On Grid` applies only to configurable products; `Typical Lead Time` only to simple products. (KB)

Storefront: configurable options are read from the published product's `ConfigurableAttribute` and `SelectValues` (`GET /v2.2/published-products/{parentProductSKU}/configurable-products`, `GET /v2/published-products/{sku}/attribute`), and `IsConfigurable` and `IsSwatch` flags in each attribute control the variant selectors and swatches. Release 10.8.0.0 made configurable variants on the grid sort by their defined attributes (for example size, colour) and custom sort rules.

## Product type and family

A family is not tied to a product type. The type is a field in the family's Product Info group and cannot be changed after the product is saved. A saved configurable product's family is locked; other types allow a family change in the Admin (the KB says no, the product allows it).

## Attributes that every type carries

System-defined attributes (for example SKU, Product Name, Product Type, Is Active, Shipping settings) are in the default family and cannot be removed from a group or family, deleted or made optional where locked. `SKU` becomes read-only after the product is created.
