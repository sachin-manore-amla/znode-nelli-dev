# Concepts and vocabulary

What this answers: what the attribute, group and family objects are, how they relate, the four attribute systems that are easy to confuse, and where each is managed.

## The hierarchy

```
Attribute Family      chosen on the product; decides which groups and attributes the product form shows
  Attribute Group     a section (tab) of the product form; holds attributes
    Attribute         one field: a type, flags, locale names, options
```

A product stores values for attributes. The family only decides which fields the product page offers and which attributes' defaults publish. It does not hold values. (KB read in full, 80; module guide, 85)

## Four systems that are confused

| System | What it is for | Admin path | Scope | API |
|---|---|---|---|---|
| Product attributes | Structured product data: description, specs, filters, variants | `PIM > Product Attributes > Attributes` (also `Attribute Groups`, `Attribute Families`) | All products that use the attribute's family | Core v1 (legacy) create/edit; v2 read of published values |
| Category attributes | Same idea for categories | `PIM > Category Attributes > Attributes` | Categories | Same route family with a category flag |
| Product custom fields | An ad-hoc `Key: Value` line on one product | `PIM > Products >` product `> Custom Fields` tab | One product only | Core v1 (legacy) only |
| User-Defined Fields / Global attributes | Extra data on users, accounts, stores, orders, content forms and similar | `Dev Center > User-Defined Fields` | Entity level | Core v2 `v2/global-attributes` and related routes |

Two terms people confuse:

- **Attribute vs custom field.** An attribute is defined once, put in a group and family, and then every product of the family can hold a value; it supports types, validation, locales, facets, comparison and search. A custom field is created per product with no definition, has only a text key and value per language, and has none of those features.
- **Product attribute vs User-Defined Field.** UDFs (global attributes) are for non-product entities. They are a separate sub-system with their own groups and families, not covered in detail here.

## Where an attribute value comes from on the storefront

PIM values are copied into the published catalog at publish time. The storefront and the v2 published-product APIs read that published copy, not PIM. So a change in PIM is invisible to shoppers until publish. See publish-and-search-effects.md.

## Product types and attributes

| Product type | How attributes are used |
|---|---|
| Simple | Holds values for every attribute of its family |
| Configurable | The parent selects which `Is Configurable` attributes define its variants; each variant (a simple product) holds its own value for them. The parent product form hides those attributes. See product-types-and-attributes.md. |
| Bundle, Grouped | Use their family's attributes like a simple product; children are associated products |

The attribute family and product type are chosen when the product is created. The KB says both are locked after the first save. The module guide found that the family can in fact be changed on Edit Product for simple, grouped and bundle products (the form reloads; values of fields the new family lacks are kept, hidden, and still published), but it is locked for configurable products and on Copy Product. Product type cannot change after save. The product wins. (module guide, 85)

## Naming and codes (Admin rules, verified in product source, 90)

| Object | Code rule |
|---|---|
| Attribute `Code` | letters and digits only, must start with a letter, at most 100 characters, unique per kind (product or category). Locked after the first save. Attribute `Attribute Type` is also locked after the first save. |
| Attribute value (option) code | letters and digits only, unique within the attribute |
| Group `Group Code` | letters and digits, starts with a letter, at most 100, unique per kind (case ignored). Locked after save. |
| Family `Family Code` | Admin: starts with a letter, letters and digits, at most 100. API accepts more. Unique per kind. Read-only after create. |
| Custom field `Custom Code` | see product-custom-fields.md |
