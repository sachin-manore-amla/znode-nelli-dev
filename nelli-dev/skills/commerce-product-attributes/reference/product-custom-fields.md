# Product custom fields

What this answers: what a product custom field is, how to add, edit and delete one, its rules and messages, how it reaches the storefront, and why it is not a substitute for an attribute.

## What it is

A free-form `Key: Value` line added to one product, for example `Warranty: 2 years`. Each field has a **Custom Code** (identifier, unique within the product), an optional **Display Order**, and for each active language a **Text** (the label) and a **Value**. Custom fields are not PIM attributes: nothing is set up under Product Attributes first, adding one creates no attribute, and a field belongs to its single product only. (KB read in full, 80; module guide, 85)

Use a custom field for occasional, one-off information on a few products. Use an attribute when many products share the field or you need a type, validation, facet, comparison, search or a variant.

## Admin steps

1. `PIM > Products`, open a saved product (Edit Product), left tab `Custom Fields`.
2. Click `Add a Custom Field`. Fill `Custom Code`, `Display Order` (optional), and `Text` and `Value` for the default language (other languages optional). `Save`.
3. Edit: row `Manage > Edit` (the code is greyed out). Delete: row `Manage > Delete` or `Tools > Delete`.
4. Publish the product or its catalog (see below). The KB step list: add, save, publish.

The tab exists only on Edit Product of a saved product whose family carries the system group `Custom Fields`. Never on Add Product or Copy Product. It works the same for every product type and state. Every add, edit or delete marks the product Draft. (module guide, development environment, 85)

Rights: Read Only shows the tab, Write adds, Edit edits, Delete deletes, set per role on the Products menu in Roles & Access Rights. No store or catalog scoping exists.

## Rules and messages

| Rule | Admin | API |
|---|---|---|
| Custom Code required | `Custom Code is required.` | not required (one empty code per product allowed) |
| Code format | `Only alphanumeric characters are allowed and the code must start with a letter.` | no format check |
| Code length | `Please enter less than 300 characters.` (299 max) | over 300: `An error occurred while saving the entity changes. See the inner exception for details.` |
| Unique within the product | `The code you've entered is already in use within the Custom Fields or Product Attributes. Kindly select a unique code.` (case and trailing spaces ignored) | same text, status 500 |
| Not equal to any attribute code (product or category, system ones included) | same message; enforced since release 10.5.0.0 | same |
| Display Order | `Display Order should be between 1 and 999`; `Enter a whole number` | no range check |
| Default-language Text and Value | `This field is required.` | if both empty on add, filled with the Custom Code |
| Text or Value length | up to 300 each | over 300 gives the entity-changes error |

Behaviour to know (module guide, 85, verified on a development environment 2026-10-11 unless noted):

- Update through the API has no duplicate or attribute-code check, so a rename can create a clash; update is a full replace and a property left out is written empty.
- HTML or script in Code, Text or Value is stored as typed and shown as HTML on the product page. Do not let untrusted users write custom fields; see `quality-security-checks`.
- A code of 101 to 299 characters is allowed by the Admin but breaks the publish of the whole batch. Keep codes under 100 characters.
- Display Order is not used to order the fields on the product page.
- Clearing one language's text in the Admin edit pop-up does not remove it (rows with an empty Text or Value are dropped before send).
- Admin edit of a field whose stored code breaks the format rules can report success without saving (only fields created through the API can have such codes).
- Import and export: there is no custom field import template and no export column; the only bulk route is one API call per field.

## Storefront

The Webstore product page builds an `Additional Information` tab from published attributes flagged as custom fields, one `Text: Value` line each, and omits the tab when there are none (Webstore source, 90). The KB says the tab appears automatically on the default B2B theme once published.

Observed difference: on the released code checked, publishing removed the custom-field entries from the published catalog attributes, so the product call returned none and the tab did not appear (module guide, 2026-10-11, recorded as a known product issue; fixed on that development environment later but not in the released code the guide read). Confirm on your own environment, with a published test product, before promising the tab to a customer. Also only the default language's Value is shown, in every language.

Search: custom fields are published as text attributes marked custom field. They are not facets or comparable, and no flag exists to put them in search.

## API (legacy v1 only)

| Operation | Route |
|---|---|
| Add | `POST /Products/AddCustomField` |
| List for a product | `GET /Products/GetCustomFieldList` |
| Get one | `GET /Products/GetCustomField/{customFieldId}` |
| Update (full replace) | `PUT /Products/UpdateCustomField` |
| Delete (comma list of ids) | `POST /Products/DeleteCustomField` |

These are in the legacy Core v1 reference only; no v2 or Commerce operation exists for custom fields. Per the API catalog rule, mark any dependency on them "legacy v1, no preferred alternative found". Only the API credentials decide access: protect them. Reading published custom fields for shoppers: `GET /v2/published-products/{publishProductId}` returns them in `Attributes` with `IsCustomField` true.

## When not to use custom fields

| Need | Better |
|---|---|
| Same extra field on many products | A product attribute in a group and family |
| Filter, facet, compare or search by it | A product attribute with the flags |
| Structured or validated value, typed number or date | A product attribute |
| A value per customer per product, or per order | A Custom Table with a custom endpoint |
| Shown differently per store | Product Information Overrides if it is name or description; else a Custom Table |
