# Concepts and vocabulary: User-defined fields (global attributes)
What a user-defined field is, the words people confuse, and how it differs from PIM attributes, product custom fields and Custom Tables.
Read this first, then the other reference files.

## One feature, four names

| Name you will meet | Where | Same thing? |
|---|---|---|
| User-defined field (UDF) | Admin menu `User-defined Fields`, Knowledge Base | Yes, the Admin name |
| Global attribute | API routes (`global-attributes`), Knowledge Base, API reference | Yes, the API name |
| Additional Attributes | Left-panel link or tab on an entity screen | The screen where the values of the UDFs of one record are edited |
| Dynamic Schema | Knowledge Base overview article | The umbrella name for attributes, groups and families (it also covers Product, Category and Media attributes) |

Verified: menu name from the product source; KB "Dynamic Schema Overview" (80).

## The three building blocks

| Block | What it is | Rule |
|---|---|---|
| Attribute (field) | One field: a code, a type, flags, labels, optional validation, optional default values | Belongs to exactly one entity type, chosen at creation, never changed afterwards |
| Attribute group | A named container of attributes of one entity type. It becomes a tab or section on the entity screen | A group holds attributes of its own entity type only |
| Attribute family | A set of groups for one entity type | Decides which groups a record shows; used mainly for Content Containers and Forms (see groups-and-families.md) |

Plus the link that makes a field visible: an entity type is associated with groups (Admin screen `Entity Attributes`). A field that is not in a group that is associated with the entity type is never shown.

## Entity and record

- Entity type = a kind of object that can carry UDFs (Store, Account, User, Promotion and others, see entities-and-where-fields-appear.md).
- Record = one store, one account, one promotion and so on.
- A UDF is defined once per entity type. Each record then holds its own value (and one value per language when the field is localizable).

## How it differs from the alternatives

| Need | Use | Why |
|---|---|---|
| Extra data about a store, account, user, promotion, order, voucher, page, banner and the other entity types | UDF | Built in, no code, shown in Admin, readable and writable through the Core v2 API |
| Extra data about a product or category, shown on the product page, filter, search, compare | PIM product or category attribute (skill `commerce-product-attributes`) | UDFs do not exist for products and categories; the PIM attribute system is separate and is published with the product |
| A one-off name and value on a single product | Product custom field (Additional Information tab) | Per product, plain text |
| A table of reference rows, many records with several columns (for example a list of dealer codes, a lookup of shipping surcharges) | Custom Table (skill `sdk-custom-tables`) | UDFs hold one value per field per record. They are not a place for lists of rows |
| Behaviour (calculation, workflow, integration) | Custom API SDK extension (skill `sdk-custom-api`) | A UDF only stores data. Nothing acts on a custom field unless you write code or the product already reads that field |

## What a UDF does not do (read this before promising a customer anything)

1. It stores and returns data. The Admin shows an input for it. Nothing else in the product changes because a new UDF exists.
2. The Webstore does not show a custom UDF on its own. It receives the values in its data calls, but only reads the field codes it was built for (see storefront-and-publish.md). Showing a new field needs Webstore source work.
3. The product does not use UDFs of an entity in its own business rules (pricing, tax, shipping, approval, search). The exceptions are the built-in system UDFs of the Store, Account, User and Global Setting entities, which hold product settings. Do not edit or delete those (see settings-and-flags.md).
4. A UDF is not a search facet and is not indexed for site search.

Evidence: product source (verified 2026-10); module guide (85).
