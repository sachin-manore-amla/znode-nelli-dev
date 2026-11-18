# Concepts and enablement

What this answers: what a Product Information Override is, the two enable flags with exact Admin paths, and what happens for each combination.
Also who can use it and what version introduced it.

## What it is

- A record in the system table `ProductInformationOverrides`, managed on `PIM > Product Information Overrides`.
- It lets one SKU present different Product Name, Short Description, Long Description and SKU by store, locale and optionally account, with no duplicate product.
- It is a display and search feature. The alternate values are not stored on the product, order or quote. (KB, read in full, 80)
- Introduced in release 10.6.2.0 (January 23, 2026). Release 10.8.0.0 (March 4, 2026) added fixes: a clearer conflict error for duplicate records, accurate product counts and account/store scoping in the suggestions API, full-text override search that respects the `Znode-AccountCode` header, and more reliable publishing of override data. (release notes read, 80)

Vocabulary people confuse:

| Term | Meaning |
|---|---|
| Override record | One row in the `ProductInformationOverrides` system table |
| Override index | A separate search index `override_<catalog index name>`, built only by a full catalog publish |
| Alternate SKU | A display value. It is not independently searchable: the API answers 404 when you look up by the alternate SKU; look up by the original SKU |
| System table | A Custom Table that ships with Znode and is flagged system-defined (see the custom table skill) |

## The two flags

| Flag | Admin path | Level | Default | Effect |
|---|---|---|---|---|
| Enable Product Information Overrides (global) | `Global Settings > Global Product Settings > Enable Product Information Overrides` | Global | Off | Shows the `Product Overrides` button on the product page. Lets publish build the override index. Required for search to apply overrides. |
| Enable Product Information Overrides (store) | `Store Settings > Additional Attributes > Product Settings > Enable Product Information Overrides` | Store | Off | Lets search return override data for that store. Not read by publish. |

Exact flag behaviour (product source, 90):

| Global | Store | Product page button | Publish builds override index | Search and `GET v2/productoverrides/{sku}` apply overrides |
|---|---|---|---|---|
| On | On | Shown | Yes | Yes |
| On | Off | Shown | Yes (built but unused) | No: falls back to standard product data silently |
| Off | On | Hidden | No | No |
| Off | Off | Hidden | No | No |

Other facts:

- Creating, editing, deleting, importing and exporting records works whatever the flags say. The Admin list page is always reachable.
- Only the two single-SKU APIs (`GET v2/productoverrides/{sku}` and `GET v2/productoverrides/multiple-products/{skus}`) return an error when overrides are disabled: `Please ensure the Product Information Override flag is enabled in both Store Settings and Global Settings.` (status 400). The search APIs fall back silently.
- The store flag is read per store and cached for the API cache timeout (default 20 minutes on the module-guide environment), so a change can take up to that long to show. (module guide, 85)
- Changing the global flag may be applied once at load by the services; if a flag change does not take effect, restart or wait for the cache timeout. Not verified on every build (gap).

## Who can do what

| Surface | Who | Notes |
|---|---|---|
| Admin grid and form | Admin users with access to the `PIM > Product Information Overrides` menu | The Admin role always can. Other roles need the menu permission for Add and Edit. (module guide, dev environment 2026-10-09) |
| Product page `Product Overrides` button | Any admin who can open the product, when the global flag is on | Read-only |
| `v2/productoverrides` API | Any caller with valid API credentials | No further role check. Search routes also need portal and locale headers. |
| Commerce Portal, B Store app | Nobody | No override screen exists |
| Shoppers | See overrides only where the storefront code calls the override APIs | The stock Webstore does not (see publish-indexing-and-fallback.md) |

## Where an override applies

Search results, typeahead and suggestions, category facets, and the single/multiple-SKU override lookups, all through `v2/productoverrides`. Supported for all product types and their add-ons (KB). Third-party integrations are not affected.
