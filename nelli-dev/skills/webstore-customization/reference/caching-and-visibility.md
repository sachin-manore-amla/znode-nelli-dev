# Caching, revalidation, CDN purge and "why is my change not visible"

What this answers: which cache layers sit between a change and the shopper, how each is refreshed, what a developer must do so a code or content change shows, and the checklist for stale pages.
Confidence: Webstore source (90) for layers and variables; KB "Secure Cache Revalidation Configuration", "Cloudflare Cache Rules & Purge Configuration", "Managing and Configuring the Cache" read in full (80). Defaults are from the source unless stated.

## Layers, from the browser inward

| # | Layer | Scope | Enabled by | Refreshed by |
|---|---|---|---|---|
| 1 | CDN edge (for example Cloudflare) | anonymous HTML and static files | your CDN rules; the Webstore sends `Cache-Control: public, s-maxage=<n>, stale-while-revalidate=<m>` for anonymous cacheable HTML only when `CDN_CACHE_SMAXAGE_S` is above 0 (`CDN_CACHE_SWR_S` default 600; `CDN_CACHE_RSC=false` limits it to HTML). Personal or excluded responses get `private, no-store` | CDN TTL, or purge: automatic full-zone purge on catalog publish, product publish and store publish when Cloudflare is configured; manual purge from Global Settings > Cache Management |
| 2 | Anonymous page micro-cache in `server.js` | whole HTML of anonymous GET pages, per pod (L1 memory) and optionally shared in Redis (L2) | `ENABLE_ANON_PAGE_CACHE=true` (default off); `ANON_PAGE_CACHE_L2_ENABLED=true` for the shared tier | TTL `ANON_PAGE_CACHE_TTL_MS` (default 60000 ms), then served stale up to `ANON_PAGE_CACHE_STALE_TTL_MS` (default 10 minutes) while one background render refreshes it; purge on broad revalidation (`ANON_PAGE_CACHE_PURGE_ON_REVALIDATE`, default on) or `POST /api/anon-cache/purge` |
| 3 | Page structure and widget data cache | page JSON and hydrated widget data for home, category, product, layout, content pages and widgets | `ENABLE_PAGE_CACHE=true` (not documented in the KB) | storage `STORAGE` (`file`, `redis`, `cdn` per the KB; source uses the cache package with file or Redis); evicted by revalidation events |
| 4 | Next data cache for API calls | server fetches that pass a `CacheTags` filter | `ENABLE_CACHE=true` | `revalidateTag` from the revalidation routes (tags are prefixed `webstore`, plus `webstoreGlobal`) |
| 5 | Store (portal) data cache, in memory | store settings, theme, domain lookup per host | always on; `PORTAL_CACHE_TTL_MS` default 15 minutes, `PORTAL_CACHE_MAX_ENTRIES` 500, `PORTAL_CACHE_NEGATIVE_TTL_MS` 60 s | cleared on every revalidation request and by a Redis eviction message to every pod |
| 6 | Admin API cache and Admin "webstore cache" | API-side | Global Settings > Cache Management (Is Active, Is full-page Cache Active, Full Page Cache Duration in seconds, Is Webstore Cache Active, which cannot be unchecked) | Refresh Cache; Refresh the Entire Webstore Cache (choose domains); Refresh Cloudflare Cache (domains with Cloudflare enabled) |

Cache keys for page structures include page code, account, publish state (production, draft, preview), locale and profile, so profile-based and account-based content is cached separately.

## How a publish reaches the Webstore

1. In Admin, publishing (store, catalog, product, banner slider, content container, Page Builder page, manual "refresh webstore cache") raises a cache event. The API calls the Webstore: `POST /api/revalidate-with-token` (one event) or `POST /api/revalidate-all-with-token` (everything). The call carries the shared secret in the `x-secret` request header.
2. The Webstore accepts the call only if `ZNODE_REVALIDATE_TOKEN` is set and equals the header; otherwise HTTP 401. The API side setting is `WebstoreWebhookSecret`; both values must be identical (KB "Secure Cache Revalidation Configuration").
3. The handler revalidates tags, clears the portal cache and publishes a Redis eviction message so every pod clears its in-memory portal and page data. Event names handled: `PortalPublishEvent`, `PortalUpdateEvent`, `VisualEditorPublishEvent`, `CategoryPublishEvent`, `ProductPublishEvent`, `CatalogPublishEvent`, `BannerSliderPublishEvent`, `ContentContainerPublishEvent`, `CustomerReviewUpdateEvent`, `ProductInventoryUpdateEvent`, `ProductPriceUpdateEvent`, `ManuallyRefreshWebStoreCacheEvent`. Per-product, price and inventory events do not flush the anonymous page cache; the four broad events (store publish and update, Page Builder publish, manual refresh) do.
4. The older routes `/api/revalidate` and `/api/revalidate-all` still exist and are deprecated; in the source `/api/revalidate` does not check the token. Plan to switch the API to the token routes and block the old ones at the gateway or CDN (KB: they will be removed).
5. A separate token, `ZNODE_DEBUG_TOKEN`, protects the debug routes.

## What a developer must do so a change shows

| Change | Needed |
|---|---|
| Widget or theme code | deploy both apps; then publish the store or the page so revalidation clears cached page JSON and widget data; hard refresh for static files (chunk names include the build id, so a new build changes them) |
| New or changed BFF route, agent, client | deploy; no cache involved unless you added `CacheTags` |
| Page Builder content | Save for Preview shows in preview; Publish pushes to preview and production (Commerce Pages article). Production visitors see it after revalidation and after the anonymous cache TTL (default 60 s plus stale window) |
| CSS in Dynamic Styles | save, then publish the store (KB) |
| Product, price, inventory data | publish or wait for events; shown per the table above |
| New environment variable | restart the process |
| Locale files | rebuild and redeploy (files are imported at build) |

## Troubleshooting stale content

1. Preview or production? Production is a separate published copy; check the publish state of the store and of the page.
2. Did the API reach the Webstore? Webstore log shows "request data for revalidation received from API". A 401 means a token mismatch (`ZNODE_REVALIDATE_TOKEN` vs `WebstoreWebhookSecret`), a missing header, or no token configured on the Webstore.
3. Several pods: without Redis (`REDIS_CONNECTION_STRING`, or `REDIS_SENTINEL_ENABLED=true` with sentinel settings) each pod keeps its own caches and clears only itself unless every pod receives the call.
4. Anonymous page cache: is the URL under an excluded prefix, does the visitor have a session or cart cookie (`next-auth.session-token`, `__Secure-next-auth.session-token`, `CartId`, `CartNumber`, `CopiedCartNumber`)? Cached copies carry no cookies.
5. CDN: purge the zone or the URL; check the rule order (KB lists seven rules; bypass rules must come after the cache rules).
6. Real-time development: set `IS_DEBUGGING=true` in both apps (reads page JSON from local files) and `ENABLE_CACHE=false` in the webstore (KB). The KB troubleshooting article says `ENABLE_CACHE=true` for the same purpose; the source treats any value other than `true` as "no data cache", so `false` is the safe setting.
7. Check `CACHE_DEBUG_LOG`, `NEXT_PRIVATE_DEBUG_CACHE` for cache logging (names read in the source).

## Cloudflare (KB, 7 rules) and how it matches the source

Rules, in order: (1) HTML eligible, edge TTL 2 hours ignoring origin headers, strong ETags, serve stale while revalidating; (2) static assets (js, css, png, jpg, svg, webp, gif, ico, jpeg) edge TTL 1 hour; (3) bypass `/cart`, `/checkout`, `/my-account`, `/account`; (4) bypass when cookies `next-auth.session-token`, `_Secure-next-auth.session-token`, `CartId`, `CartNumber` are present or the path contains `login`; (5) bypass non-GET; (6) bypass the Admin host; (7) bypass `/api/auth`, `/login`, `/signin`. Admin setup: Store > Additional Attributes > Cloudflare Setting: Enable Cloudflare (default No) and Zone ID; connection details (API token, account email, API base URL, Zone ID) in the Webstore environment configuration. Every catalog, product and store publish purges the entire zone, so the first requests after a publish hit the origin.

Differences to apply (product wins): the cookie is `__Secure-next-auth.session-token` (two underscores), the Webstore also treats `CopiedCartNumber` as personal, and the source excludes more personal paths (`quick-order`, `order`, `quote`, `saved-cart`, `punchout`, `impersonation`, `logout`, `register`, `welcome`). Add them to rules 3 and 4 if anonymous visitors can reach them. The names of the environment variables the Webstore uses for the Cloudflare connection are not in the source I read (see GAPS); take them from the KB deployment instructions or ask Znode.

## Rules of thumb for customizations

- Do not cache personal data in server-rendered HTML; the anonymous cache serves one copy to everyone without a session.
- A custom client call with no `CacheTags` is never cached; add tags only when the data is the same for every visitor and you wire the tag to a publish event.
- Keep widget data that varies by user in client-side fetches.
