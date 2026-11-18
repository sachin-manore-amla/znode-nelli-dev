---
name: commerce-product-overrides
description: Product Information Overrides, the Admin feature that shows a different product name, descriptions or SKU per store, account and locale without duplicating the product. Covers the two enable flags and their Admin paths, the override record fields and scoping, the PIM > Product Information Overrides screens, CSV import and export, the full-catalog-publish rule, fallback behaviour, the v2 override APIs, tested limits, the ProductInformationOverrides system table, and what the stock storefront does and does not do with overrides. Use when a requirement says "different product name or description per store, account or locale", when overrides do not show up, or before recommending a custom table or endpoint for per-store product text.
user-invocable: false
---

# Product Information Overrides

An override record says: for product SKU X, in store S, locale L (and optionally account A), show this alternate name, short description, long description or SKU. It changes what search and the override APIs return. It does not change the product, its price, its inventory, or any order or quote.

## Use / do not use

| Use it for | Do not use it for |
|---|---|
| Different product name or description per store, account or locale | Different price (use price lists, see `commerce-promotions-and-pricing`) |
| Account-specific alternate SKU or name (B2B part numbers) | Different stock, images, attributes, SEO fields or categories per store |
| Bulk load of per-store text by CSV | Storing a value per customer per product (use a Custom Table) |
| | Anything that must be saved on the order (overrides are display data only) |

Two terms people confuse: the **override record** (a row in the `ProductInformationOverrides` system table) and the **override index** (a separate search index built at publish). Saving a record does not update the index.

## The 10 facts that matter most

1. Disabled by default. Both flags must be on: `Global Settings > Global Product Settings > Enable Product Information Overrides` and, per store, `Store Settings > Additional Attributes > Product Settings > Enable Product Information Overrides`. Either off means base product data. (KB read in full, 80)
2. Records live under `PIM > Product Information Overrides` (the `ProductInformationOverrides` system table). Required: SKU, Locale Code, Store Code. Optional: Account Code and the four alternate fields. (KB read in full; verified in product source, 90)
3. Nothing is validated against master data on save. Any SKU, store, locale or account text is accepted; a record that matches nothing is silently ignored at publish. (product source, 90)
4. There is no unique rule. A duplicate of SKU + Store + Locale + Account saves without warning and later causes an error at search time. (KB, product source, 90)
5. Changes reach search only after a full catalog publish. The first use needs a full publish with `Publish Draft Products Only` unticked, because it builds a separate index named `override_<catalog index name>`. (KB read in full, 80; module guide, 85)
6. The match is exact on store, locale and account. A store-level record has an empty account. In the product code, a request whose `Znode-AccountCode` header has no account-specific record gets the original product data, although the API reference says it falls back to the store-level record. Test this on your version (see reference/publish-indexing-and-fallback.md). (product source 90 versus API reference 70: conflict)
7. The stock Webstore does not call the override APIs. Its product page, search, listing and cart use normal product data, so overrides have no storefront effect until a customization calls `v2/productoverrides`. (Webstore source, 90)
8. The product page's `Product Overrides` button is a read-only list. Add, edit and delete happen only on the PIM screen, by import, or by API. (KB, module guide)
9. Tested up to about 100,000 records. Sorting and pagination are not supported on the override APIs. Variants not linked to a category are excluded. (KB read in full, 80)
10. Adding fields to the system table or changing its schema is restricted and breaks the feature. It cannot be deleted from the Admin. (KB, custom table docs)

## Where to read more

| File | Answers |
|---|---|
| `reference/concepts-and-enablement.md` | what it is, the two flags, the combined behaviour matrix, who can do what |
| `reference/fields-scoping-and-rules.md` | every field, scoping keys, lengths, validation messages, uniqueness |
| `reference/admin-screens-and-import-export.md` | the PIM grid, add/edit form, product modal, CSV template, import and export steps |
| `reference/publish-indexing-and-fallback.md` | what a publish does, what needs a re-publish, fallback and matching logic |
| `reference/override-apis.md` | the `v2/productoverrides` operations, headers, request and response shapes |
| `reference/limits-and-known-behaviours.md` | limits, surprises, version notes, KB versus product differences |
| `reference/customization-decisions.md` | requirement-to-verdict table, Custom Table or endpoint alternatives, how a customization consumes overrides |

## Nelli-Dev decision guide

| Requirement | Verdict | Reason and answer |
|---|---|---|
| Different product name or description per store | Supported | Enable both flags, add records, run a full catalog publish. Then the storefront must call the override APIs (next row). |
| Show those overrides on the stock Webstore PDP, search and listing | Customizable (source customization) | The stock Webstore does not call them. A Webstore change that reads `v2/productoverrides` is needed. Label it a source customization with upgrade-merge risk. |
| Account-specific name or SKU for a B2B account | Supported (data) / Customizable (display) | Account Code is a record key. Display needs the same Webstore call, with the `Znode-AccountCode` header set. |
| Different name per locale | Supported | Locale Code is a key. Without an override the product's own locale text is used, then the default locale. |
| Different price, stock, image or SEO URL per store | Restricted | Overrides cover only name, short description, long description and SKU. Use price lists or inventory per warehouse for those. |
| Add a new override field (for example "marketing tagline") | Needs platform change | The override table schema is system-defined; adding or changing fields breaks the feature. Use a separate Custom Table plus a custom endpoint instead. |
| Store a value per customer per product (note, favourite size) | Customizable via Custom Table | Not an override use. Create a custom table keyed by customer and SKU and expose it with a custom endpoint. |
| Make an override show instantly after edit | Needs platform change | A full catalog publish is required. A scheduled publish is the workaround. |
| Enforce one record per SKU/store/locale/account | Customizable | No platform rule. Validate before import, or put the check in a custom endpoint in front of the create call. |
| Show the original and alternate name together in the Admin | Supported | The product page `Product Overrides` button lists records read-only. |
