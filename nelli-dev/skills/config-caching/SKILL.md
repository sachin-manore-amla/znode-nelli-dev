---
name: config-caching
description: What Znode caches and where (browser, CDN, guest page cache, page-structure cache, portal cache, tagged data cache, request de-duplication, Cloudflare edge rules), how to clear or refresh after a change (publish, the revalidation and purge routes, Admin Cache Management, Cloudflare purge), the environment variables and Admin settings that control it, and the rules customization code must follow (tags, store-scoped keys, no-store for personal data, fail open). Load it for stale data after a publish, for logged-in users seeing guest pages, for any customization that fetches or caches data, and when sizing or configuring the Webstore cache.
user-invocable: false
---

# Caching (what is cached, how to refresh, what custom code must do)

Sources: Znode Knowledge Base articles Znode Storefront Caching Architecture and Performance Guide, Storefront Performance and Caching Guidance, Secure Cache Revalidation Configuration, Cloudflare Cache Rules & Purge Configuration, Customizing Storefront Data Retrieval, Webstore Customization Guide, Maintenance Settings, Managing General Global Settings (read 2026-11-23). Admin-side platform API caching is **not documented** in the KB: nothing here claims it. Confidence 85 for the Webstore part (read in full, not run); "not documented" is stated where the KB is silent.

## The seven layers (request order)
| # | Layer | Holds | Lifetime / switch |
|---|---|---|---|
| 1 | Browser cache | JS, CSS, fonts, images | per browser |
| 2 | CDN / edge | shared guest HTML and RSC payloads | `CDN_CACHE_SMAXAGE_S` > 0 (default 0 = off) |
| 3 | Middleware routing | routing decisions only | not cached |
| 4 | Portal cache | store settings, theme, metadata, domains, 301 redirects | always on, 15 min (`PORTAL_CACHE_TTL_MS`) |
| 5 | Guest page cache | rendered HTML of guest pages (L1 per worker, L2 Redis) | `ENABLE_ANON_PAGE_CACHE`, TTL 60 s, stale window 10 min |
| 6 | Page-structure cache | Page Builder page definitions | `ENABLE_PAGE_CACHE`, 1 hour default |
| 7 | Tagged data cache | server-side API responses | `ENABLE_CACHE=true`; tag-driven invalidation |
Plus request de-duplication (identical in-flight GETs merged; `API_FETCH_TIMEOUT_MS`, 30 s). Details: `reference/cache-tiers-and-settings.md`.

## Twelve facts that matter
1. Cart, checkout, payment state, customer carts, personal data, buyer-specific prices and live inventory are **never** shared-cached. (KB 85)
2. Logged-in visitors, and visitors carrying a cart cookie, bypass the guest page cache automatically; the cookies are `next-auth.session-token`, `__Secure-next-auth.session-token`, `CartId`, `CartNumber`, `CopiedCartNumber`. (KB 85)
3. Guest pages are cached per store host, device bucket, gzip support, `NEXT_LOCALE` cookie and full URL including query string. (KB 85)
4. A publish refreshes the data cache and page-structure cache at once; the guest page cache and the CDN are **not** purged by it. (KB 85)
5. Only the portal cache is always on. Confirm which tiers each environment enables. (KB 85)
6. Multi-pod setups need Redis (`STORAGE=REDIS`, `CACHE_MEMORY=REDIS`, `CACHE_EXPIRY` set). `STORAGE=FILE` is local to each pod. (KB 85)
7. Revalidation and purge calls are authenticated with a shared secret: `ZNODE_REVALIDATE_TOKEN` on the Webstore, `WebstoreWebhookSecret` on the API, identical. Wrong or missing secret returns 401 (403 on the purge route). (KB 85)
8. The Cloudflare zone is purged **entirely** on every Catalog, Product and Store publish if Cloudflare is enabled for the store. (KB 85)
9. A server-side API call is cached only if `ENABLE_CACHE=true` **and** it carries a cache-tags filter. Without tags it is fetched every time; browser calls are never cached. (KB 85)
10. Real-time pricing is overlaid on cached data per request unless `ENABLE_REAL_TIME_PRICING=false`. (KB 85)
11. Page Builder **preview** reads current content directly; the storefront shows published content after invalidation. Not a bug until publish and invalidation are verified. (KB 85)
12. The PDP updates inventory in near real time; the PLP can show cached inventory. (KB 80: Managing Inventory)

## How to refresh or clear (decision order)
| Situation | Action |
|---|---|
| Content, catalog or store settings changed | Publish (`commerce-publish-pipeline`); data and page-structure caches refresh automatically |
| Guests still see the old page | Wait for TTL (60 s) or purge: `POST https://<store-domain>/api/anon-cache/purge` with header `x-secret`; body `{"path":"/category/5602"}` for one URL, empty body for all |
| CDN still serves old HTML | Purge in the CDN (Cloudflare: Global Settings > Cache Management purges manually; the KB says nothing more about that screen) or wait for `s-maxage` |
| Pods disagree | Check shared Redis settings and the `cache-eviction` subscription log line per pod |
| Recovery from a bad state | `POST /api/revalidate-all-with-token` (revalidates all tagged responses and deletes every key in the cache store): expect a burst of back-end traffic; give the storefront its own Redis database |
| Revalidation 401 | token missing or different on a pod |
| Revalidation 500 | the pod cannot reach Redis |
Admin "clear cache" button or API cache-clear operation: the KB read does not describe one beyond Cloudflare's Cache Management mention. Label any such claim unverified.

## Admin settings that touch caching
| Where | Setting | Effect |
|---|---|---|
| Stores > (store) > Additional Attributes > Cloudflare Setting | **Enable Cloudflare** (default No), **Zone ID** | Automatic zone purge on Catalog, Product and Store publish; also needs API token, account email, API base URL |
| Global Settings > Cache Management | manual Cloudflare purge | stated in the Cloudflare article only |
| Global Settings > Promotions and Coupon Settings | stacking and tax-on-discount settings | the KB does not say a cache clear is needed after changing them |
| Dev Center > Global Settings > General | storage unit, date and time format, time zones, rounding, current environment | no cache or refresh behaviour documented |
Everything else (`ENABLE_CACHE`, TTLs, Redis, CDN seconds) is Webstore environment configuration, owned by whoever runs the Webstore.

## Nelli-Dev decision guide
| Requirement | Verdict | Route |
|---|---|---|
| Fetch Znode catalog data in a custom component and keep it fresh | Customizable | Server-side agent call with the platform cache tags so publish events refresh it (`reference/custom-code-rules.md`) |
| Cache data from my ERP | Customizable | Custom Redis cache only with store-scoped keys, explicit TTL, invalidation path, fail open; or fetch per request |
| Show buyer-specific price on a cached page | Customizable | Keep the shell cached, merge price per request (real-time pricing overlay) |
| Make a public page always fresh | Customizable | Add the path to the guest-cache exclusion list (mark `// CUSTOM:`), `no-store` its data |
| Purge guest cache when an external system changes data | Customizable | Your back end calls the purge or revalidate route with the secret |
| Change the cache architecture itself | Needs platform change | Bypassing the patterns raises security risk and upgrade cost (KB 85) |
| Clear the Znode API-side cache from custom code | Not documented | Ask Znode support; do not guess a route |

## Pitfalls
- Caching personalized or transactional data (cross-user leaks).
- Keys without store id (breaks tenant isolation and targeted invalidation).
- Caches without TTL or invalidation; middleware that does expensive work and defeats downstream caches.
- Forgetting the CDN rule that bypasses cache on the five personal cookies (response headers cannot express it).
- Stripping the query string from the CDN cache key, or edge rules that force-cache HTML.
- Calling the deprecated revalidate routes or putting the token in a URL path (lands in access logs).
- Sending `ZNODE_REVALIDATE_TOKEN` values from different environments.

## Reference files
- `reference/cache-tiers-and-settings.md` – each tier with variables, defaults, memory sizing, Redis recipe, CDN and Cloudflare rules.
- `reference/revalidation-and-purge.md` – routes, headers, responses, verification commands and troubleshooting.
- `reference/custom-code-rules.md` – decision rules, tag pattern, key format, performance rules for customizations.

Related: `commerce-publish-pipeline`, `webstore-customization`, `webstore-headless-api`, `quality-performance-checks`, `config-global-settings`.
