---
name: commerce-product-attributes
description: The Znode PIM product attribute system end to end - attribute types and their validation options, the behaviour flags with exact Admin labels (Is Configurable, Is used for facets, Is used in Search, Is Comparable, Is Personalizable and more), attribute groups and families (creating, assigning, display order, what can and cannot be changed or deleted once in use), product custom fields, how the four product types use attributes, what is published to the storefront and search and what needs a publish, the attribute and published-product APIs, import and limits. Use when adding or debugging a product attribute, facet, family or custom field, or when a requirement asks to store, show or search extra product data.
user-invocable: false
---

# Product attributes, groups, families and custom fields

Scope: PIM product attributes (and the identical category attribute screens), groups, families and product custom fields. User-Defined Fields (global attributes under `Dev Center`) are a separate system, only pointed to here. Product text per store is `commerce-product-overrides`.

## What it is

An **attribute** is one product field (type, flags, names per language, options). A **group** is a section of the product form that holds attributes. A **family** is chosen on the product and holds groups; it decides which fields the product form shows. A **custom field** is a one-product `Key: Value` line that needs no definition. PIM values are copied to a published catalog at publish time; shoppers and the v2 APIs read that copy.

Two terms people confuse: an attribute (defined once, typed, searchable, shared by a family) versus a custom field (per product, text only, not searchable); and the PIM draft (what Admin edits) versus the published product (what the storefront reads).

## Use / do not use

| Use | Do not use |
|---|---|
| Attributes for shared product data, filters, comparison, variants | Custom fields for data on many products |
| Custom fields for one-off notes on a product | Attributes for a value per customer, per account or per order (use a Custom Table) |
| Families to shape the product form | Families as a store, role or product-type switch (they are none of these) |

## The 10 facts that matter most

1. Hierarchy is Family > Group > Attribute. An attribute that is in no group of the product's family never shows on that product. (KB, 80)
2. Eleven attribute types: Text, Text Area, Number, Date, Yes/No, Simple Select, Multi Select, Label, File, Image, Link. Type and Code are locked after the first save. (KB, product source, 90)
3. `Is Configurable` appears only on Simple Select; `Is used for facets` only on Simple and Multi Select; `Is Personalizable` only on Text and removes the attribute from groups. (product source, 90)
4. Everything reaches shoppers only through publish. Every attribute with a value is published, with its flags; changing a definition needs a full catalog publish. (module guide, 85; the last point is inference)
5. For search, `Is used in Search` is not enough: the attribute must be in a search profile that is published. Facets also need `Is used for facets`. (KB, 80)
6. Removing an attribute or group from a family never checks product values: the field disappears, values stay and still publish. Deleting a family is refused while any product or category value uses it. (module guide, 85)
7. System-defined attributes and groups cannot be deleted or removed. `Required` is locked for Is Active, SKU, Product Name, Shipping Cost. (KB, product source)
8. A product's family can be changed after save for simple, grouped and bundle products, contrary to the KB; configurable products and Copy Product lock it. (module guide, 85)
9. The management APIs for attributes, groups, families and custom fields exist only in the legacy v1 reference. v2 has published-product reads and `GET /v2/pim-attribute-groups`. (specifications, 90)
10. The stock PDP renders a fixed set of tabs. A new attribute shows only where a theme or component renders it, so "show it on the PDP" is a Webstore source customization. (Webstore source, 90)

## Reference files

| File | Answers |
|---|---|
| `reference/concepts-and-vocabulary.md` | hierarchy, the four systems, code rules, product types in brief |
| `reference/attribute-types-and-rules.md` | each type, each flag with its exact label, validation, options, messages, what cannot change |
| `reference/groups-and-families.md` | creating and managing groups and families, display order, what blocks what |
| `reference/product-custom-fields.md` | the Custom Fields tab, rules, messages, storefront reach, API |
| `reference/product-types-and-attributes.md` | simple, configurable, bundle, grouped and configurable attribute rules |
| `reference/publish-and-search-effects.md` | what is published, what needs publish or re-index, search and facet effects |
| `reference/api-and-sdk-usage.md` | operations (v1 legacy and v2), published shapes, customization access |
| `reference/import-export-and-limits.md` | imports, limits, performance guidance |
| `reference/settings-and-flags.md` | per-attribute flags and surrounding platform settings |
| `reference/known-behaviours.md` | surprises, version notes, KB versus product |
| `reference/customization-decisions.md` | mechanism chooser and the requirement-to-verdict table |

## Nelli-Dev decision guide

| Requirement | Verdict | Reason |
|---|---|---|
| Add a new product field shown on the PDP | Supported (data) / Customizable (display) | Attribute in a group and family plus publish; rendering outside the fixed tabs needs a Webstore change (source customization) |
| Search or filter by a custom attribute | Supported | Simple or Multi Select with `Is used for facets`, `Is used in Search`, search profile, full catalog publish |
| Make a field required, add validation, set a regular expression | Supported | Attribute `Required` and type rules; regex on Text |
| Show different product name per store | Supported | Use `commerce-product-overrides`; stock Webstore needs a call to the override APIs |
| Store a value per customer per product | Customizable | Custom Table and custom endpoint; attributes hold one value per product |
| Add a note to one product | Supported | Product custom field (verify the Additional Information tab on your environment) |
| Create or change attributes from an integration | Customizable (legacy v1) | Only v1 write APIs exist; no role check, so wrap with a custom endpoint that validates |
| Add a new attribute type or validation rule type | Needs platform change | Types and rule sets are fixed |
| Hide attributes from some users or roles on the product form | Needs platform change | Families are global, not role-aware |
| Attribute values that differ by store | Restricted | Attributes are global per product; use catalogs, overrides (text only) or a Custom Table |
| Immediate storefront effect after an attribute change | Needs platform change | Publish is required |
| Bulk load attribute values | Supported | Product import with the family template; imports fire no events |

Where a Custom Table or custom endpoint is better: per-customer, per-account or per-order data, reference tables looked up by SKU, and anything needing unique or required rules the attribute system cannot give. See `sdk-custom-tables` and `sdk-custom-api`.

## Related

`commerce-catalog` · `commerce-search-seo` · `commerce-product-overrides` · `config-import-export` · `api-catalog` · `webstore-customization`
