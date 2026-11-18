# Publish, indexing, fallback and matching

What this answers: what must be published for an override to take effect, how the override index relates to the catalog index, and exactly how a record is chosen or skipped.
Includes the point where the API documentation and the product code disagree.

## What a publish does

- Override data is indexed automatically at the end of a catalog publish or a product publish, only when the global flag is on. There is no separate "publish overrides" action. The store flag is not checked at publish. (product source, 90)
- The index is named `override_<catalog index name>`, one per catalog. It is not visible or manageable in the Admin: no status or health is shown, and it cannot be created or refreshed by hand. (KB read in full, 80)
- Search reads the normal catalog index and the override index together. If no override data exists the base index is used.

## What needs a publish

| Change | Needs | Notes |
|---|---|---|
| First use of overrides | A full catalog publish with `Publish Draft Products Only` unticked | Builds the override index. A draft-only publish does not. (KB, 80) |
| Add, edit or delete a record | A full catalog publish | The product is not necessarily marked Draft, so a "draft products only" publish may not pick it up. Do not rely on Draft status as the signal. (KB limitation table) |
| Delete a record | A full catalog publish | The override stays in search until then. |
| Turn the global flag on or off | Flag applies to publish; re-publish after enabling | |
| Turn the store flag on or off | No publish; store flag is read at search time (cached) | |
| A new store assigned to a catalog | Full catalog publish (inference) | A record only reaches a catalog through the store's catalog association. |

Publish History shows only the main catalog publish time; override indexing time is not tracked, so allow extra time after a publish before checking search. The first publish takes longer because the catalog is fully re-indexed. (KB)

## Records skipped at publish

A record is dropped silently when any of these is true: the SKU is not a PIM product, the locale code does not match an active locale, the store code does not match a store, or the store is not associated with the catalog being published. Variants that are not linked to a category are excluded too (see limits file). (module guide, product source, 85)

## Matching logic at read time

| Header | Meaning |
|---|---|
| `Znode-PortalCode` | store code. Required on search routes (400 if missing). |
| `Znode-LocaleCode` | locale code. Required (400 if missing). |
| `Znode-AccountCode` | account code. Optional. When absent, the lookup is for store-level records. |

What the product code does (product source read, 90): it filters override records by exact StoreCode, LocaleId and AccountCode. When no account code is sent the account filter is the empty-account marker, which is how a store-level record is stored. If no record matches, the original product data is returned. There is no second query for a store-level record when an account is supplied.

What the API reference says (API reference, 70): when an account code is supplied and no record exists for that account, the store-level record is returned.

Conflict: the two differ. Until Znode settles it, assume exact match and, if an account-specific rule must fall back to the store rule, add records for the account explicitly or perform the fallback in your own code (call once with the account, once without). Test with your own data on your version. Release 10.8.0.0 changed full-text override search to respect the `Znode-AccountCode` header.

## Fallback order for the displayed text

1. Override record for store + locale + account (alternate fields that are filled).
2. A blank alternate field falls back to the product's own value for that locale.
3. If the product has no value for that locale, the default locale's product value is shown. (KB, 80)

Only the four fields are affected. Price, inventory, images and attributes are untouched. A look-up by alternate SKU returns 404; use the original SKU. When several records exist for the same combination the result is undefined (see rules).

## What the stock Webstore does

The Webstore source contains a generated client for the override search operations, but no page or agent calls it. The product page uses the published product API, search uses the normal full-text search route, typeahead uses the standard suggestion routes, category listing uses the category products route, and the cart and checkout read normal product values. So on the stock Webstore the shopper sees product data, not overrides. The release notes say the same: storefronts need the override APIs implemented, otherwise default product data is shown. (Webstore source, search 2026-10-15, 90; release notes, 80)

For a customization that wants overrides on the storefront, the Webstore must call `GET v2/productoverrides/...` with the store, locale and account headers instead of (or after) the standard calls. This is a source customization of the Webstore, not a supported extension point; cache the result per store, locale and account and keep it inside the API call budget (see `quality-performance-checks`).
