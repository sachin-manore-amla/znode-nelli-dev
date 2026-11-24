# Publish and cache effects
What this answers: what refreshes automatically when a publish runs, what does not, and what customization code must do so its data is fresh too.
Sources: KB Storefront Performance and Caching Guidance, Znode Storefront Caching Architecture and Performance Guide, Cloudflare Cache Rules & Purge Configuration, Secure Cache Revalidation Configuration, Customizing Storefront Data Retrieval (read 2026-11-23). Confidence 85 (read in full; not verified in a running environment).

## What a publish triggers
When content, catalog or store settings publish, Znode sends a cache event to the Webstore. One call to the revalidation route updates the data caches on every pod.

| Cache | After publish |
|---|---|
| Tagged data cache (catalog, product, category, content, store settings) | Refreshed immediately (tag-based) |
| Page-structure cache (Page Builder JSON) | Cleared immediately for the affected store, product, category or layout |
| Portal cache (store settings, theme, 301 redirects) | Refreshed on publish, provided the publish event uses the revalidation token and Redis is configured in multi-server setups |
| Guest page cache | **Not** purged automatically; refreshes within its TTL (60 s default) unless purged |
| CDN | **Not** purged automatically; within the configured cache time plus stale-while-revalidate, unless purged |
| Cloudflare zone (if enabled) | Purged automatically on Catalog Publish, Product Publish and Store Publish (whole zone) |

Which page structures a publish event clears:
- Portal publish or update, Visual Editor publish, manual "refresh webstore cache": all store structures plus cart, checkout, quick order, track order, forgot password, sign-up, login.
- Product publish, price, inventory or review update: the product pages named in the event tags.
- Category publish, price, inventory or review update: the category pages named.
- Banner slider or content container publish: structures under the `str_` prefix.
- Catalog publish: header and footer layout structures and catalog page keys.

## Requirements for the refresh to work
- Same revalidation secret on the API side (`WebstoreWebhookSecret`) and every Webstore pod (`ZNODE_REVALIDATE_TOKEN`); mismatch gives HTTP 401.
- Redis reachable from every pod in every environment that receives publish events (the route publishes an eviction message on Redis; a pod that cannot reach Redis returns 500).
- Use the authenticated routes (`/api/revalidate-with-token`, `/api/revalidate-all-with-token`); the older unauthenticated ones are deprecated.

## What customization code must do
| Your data | Do |
|---|---|
| Data that Znode publish events cover (catalog, product, category, brand, content) | Tag the call with the platform cache keys (`CACHE_KEYS`) exactly as the baseline agents do, so the same publish event refreshes it |
| Data from your own system that no Znode publish touches | Fetch per request, or have your back end call the revalidation route when that data changes |
| Cart, checkout, orders, account, buyer-specific prices | Never cache (`no-store`) |
| A public page that varies per visitor | Exclude its path from the guest page cache and the CDN |

## Waiting for a publish from custom code
No "publish finished" event or status API was documented in the KB. Options, none verified in a spec:
1. Poll the publish status the Admin shows (catalog **View**) manually in a runbook.
2. Allow for the cache windows (guest page 60 s, CDN s-maxage) before testing the storefront.
3. Treat any plan that depends on an exact completion signal as "Customizable, needs confirmation from Znode support".

## Tests to run after a publish-dependent customization
1. Publish, then request the page logged out and logged in.
2. Confirm the response header `x-anon-cache` (HIT, MISS, STALE, BYPASS) and `Cache-Control` as described in `config-caching`.
3. Repeat after a purge if urgent.
