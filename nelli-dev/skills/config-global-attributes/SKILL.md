---
name: config-global-attributes
description: Znode user-defined fields (also called global attributes, additional attributes or the Dynamic Schema) - custom fields defined per entity type (Store, Account, User, Content Container, Form, Promotion, Voucher, Brand, Order and about 30 more) to store extra data without code. Covers attribute types and validation, groups, families and entity links, the Admin screens, the Core v2 API for fields and values, how values reach the Webstore, publishing and caches, import and export, security and limits, and a decision guide against PIM attributes and Custom Tables. Use when a requirement says "add a field to the account, user, store, form, promotion or voucher", when a value is missing on a screen or API response, or before choosing where to store extra data.
user-invocable: false
---

# User-defined fields (global attributes)

## What it is
A UDF is a custom field defined once for an entity type. Each record of that type (one store, one account, one user) then holds its own value. Admin menu: `Dev Center > User-defined Fields` (Attributes, Attribute Groups, Attribute Families, Entity Attributes). API name: global attributes (Core v2). Values are edited on the record under `Additional Attributes` (or in a section of the edit screen).

Do not confuse it with: PIM product or category attributes (`commerce-product-attributes`), product custom fields, and Custom Tables (`sdk-custom-tables`).

## Use it when / do not use it when
- Use: one extra value per store, account, user, promotion, voucher, order, page, banner, brand, container, form and the other entity types.
- Do not use: per product or category data (PIM), rows or lists (Custom Table), anything that must be searched or filtered on the site, anything the product must act on without code.

## The 10 facts that matter most
1. Three blocks: attribute (field), group, family. A field only shows when it is in a group the entity uses. Order: field, labels (and options), group, family, `Entity Attributes`.
2. Entity type, attribute type and code are fixed at creation. Admin code rule: letters and digits, start with a letter, 100 characters at most.
3. Ten types in Admin: Text, Text Area, Number, Date, Yes/No, Simple Select, Multi Select, Label, File, Image. Rules per type are in `reference/attribute-types-and-rules.md`.
4. About 30 entity types. The live list is `GET /v2/global-entities` or the Entity Type list on the Add screen. Product, Category and Media are not among them.
5. Core v2 can create fields, labels, options, groups, families and entity links, and read and write values. It cannot edit a field definition and its value write cannot clear a value.
6. `PUT /v2/global-entity-attributes` checks only that the field and record exist, Date and Number parse, and select values are real option codes. Required, length, pattern, range and uniqueness are not checked. Validate in your code.
7. The Webstore does not show a custom UDF by itself. Only Forms render dynamically. Everything else needs Webstore source work.
8. Values are live for the API. Store flags may need a store publish and a cache clear. Forms need no publish.
9. UDF values are not covered by the XSS validation of release 10.13.1.0. Encode on output.
10. Exports of Promotions and Vouchers can include UDF columns. Voucher and B2B customer imports read UDF columns. Other imports do not.

## Decision guide (Nelli-Dev verdicts)

| Requirement | Verdict | Pointer |
|---|---|---|
| PO approval code on the account | Supported (store and edit). Customizable if approval logic must use it | Account UDF, `reference/customization-decisions.md` |
| Delivery instruction on the user | Supported to store, Customizable to show in the Webstore | User UDF plus Webstore source change |
| Extra store attribute shown in the footer | Customizable | Store UDF, render from portal data, publish store, clear cache |
| Extra fields on a custom form | Supported | Form Builder entity, attach groups to the form |
| A field on a promotion | Supported to store. Discount logic is Customizable | Promotion UDF, promotion extensibility |
| Something per product | Use PIM | `commerce-product-attributes` |
| Structured reference data or per-record rows | Use Custom Table | `sdk-custom-tables` |
| Search or facet on a custom field | Not a UDF feature | PIM attribute or Needs platform change |
| New entity type for UDFs | Needs platform change | Platform Change Request |
| Clear a value through the API | Restricted until verified | Use the Admin |

More examples and the step list: `reference/customization-decisions.md`.

## Open questions (unverified, see the maintainers GAPS list before promising)
- Whether assigning a group on `Entity Attributes` alone makes it show on a record, or the entity's family must also contain it.
- Which Webstore calls read the published store UDF snapshot.
- Where the Pending Order and Line Item entities show their fields.
- Whether `UserDefinedField` can be selected on the webhook screen.

## Reference files
| File | Answers |
|---|---|
| `reference/concepts.md` | Vocabulary, UDF versus PIM versus Custom Table, what a UDF does not do |
| `reference/attribute-types-and-rules.md` | Types, options, defaults, swatches, validation, messages, create and delete errors |
| `reference/groups-and-families.md` | Menu paths, group and family rules and messages, how an entity or container picks its family |
| `reference/entities-and-where-fields-appear.md` | Entity list, Admin screens, `EntityCode` per entity for the API |
| `reference/api-and-values.md` | Every Core v2 operation, write rules, where values appear on responses, SDK client, events |
| `reference/storefront-and-publish.md` | Webstore reads, publishing, caches |
| `reference/settings-and-flags.md` | System fields, flags, import and export, XSS, limits, release notes |
| `reference/known-behaviours.md` | Surprises, KB versus product differences |
| `reference/customization-decisions.md` | Verdict table and decision steps |

Related skills: `commerce-product-attributes`, `sdk-custom-tables`, `api-catalog`, `config-global-settings`, `config-store`, `webstore-cms`, `commerce-b2b-accounts`, `config-import-export`, `sdk-events-and-webhooks`, `sdk-capability-registry`.
