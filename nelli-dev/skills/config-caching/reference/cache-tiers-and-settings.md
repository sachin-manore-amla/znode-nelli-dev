# Cache tiers and settings
What this answers: every Webstore cache tier, the variables that switch it, defaults, sizing, and the CDN and Cloudflare rules.
Sources: KB Storefront Performance and Caching Guidance; Znode Storefront Caching Architecture and Performance Guide; Cloudflare Cache Rules & Purge Configuration; Webstore Customization Guide (read 2026-11-23). Confidence 85. These are Webstore environment variables, not Admin screens.

## Tiers
| Tier | Holds | Shared across pods | Switch |
|---|---|---|---|
| CDN | guest HTML, RSC payloads | yes | `CDN_CACHE_SMAXAGE_S` > 0 (default 0) |
| L1 page cache | rendered HTML per worker | no | `ENABLE_ANON_PAGE_CACHE=true` |
| L2 page cache | same HTML, gzip, in Redis | yes | `ANON_PAGE_CACHE_L2_ENABLED=true` plus Redis |
| Portal cache | store settings, theme, metadata, 301 redirects | cleared on every pod via Redis | always on; `PORTAL_CACHE_TTL_MS` (15 min) |
| Page structure | Page Builder JSON | yes with `STORAGE=REDIS` | `ENABLE_PAGE_CACHE=true` |
| Data cache | tagged fetch responses | yes with `CACHE_MEMORY=REDIS` | `ENABLE_CACHE=true` |
| Request de-duplication | identical in-flight GETs | no | always on; `API_FETCH_TIMEOUT_MS` (30 s) |
Other cache variables seen in the Webstore Customization Guide: `CACHE_MEMORY` (MEMORY or FILE style), `STORAGE` (file, redis, cdn), `REDIS_CONNECTION_STRING`.

## Guest page cache
- Served by the Webstore's custom server. Only guests (no session, no cart) are served from it.
- Never cached: requests with the five personal cookies; excluded paths (api, _next, cart, checkout, account, login, logout, register, welcome, impersonation, punchout, quick-order, saved-cart, order, quote, error, maintenance, revalidate, with or without locale); non-GET; static files; error renders; pages over 5 MB.
- Result header `x-anon-cache`: HIT, STALE, MISS, BYPASS. From Redis: `x-anon-cache-tier: L2`. Stale copies go out as `private, no-store`.
- Settings and defaults: `ANON_PAGE_CACHE_TTL_MS` 60000; `ANON_PAGE_CACHE_STALE_TTL_MS` 600000; `ANON_PAGE_CACHE_MAX_ENTRIES` 500; `ANON_PAGE_CACHE_MAX_BODY_BYTES` 5 MB; `ANON_PAGE_CACHE_MAX_TOTAL_BYTES` 256 MB per worker; `ANON_PAGE_CACHE_L2_TIMEOUT_MS` 80; `ANON_PAGE_CACHE_L2_LOCK_TTL_MS` 10000.
- Memory is roughly `WEB_CONCURRENCY` times the per-worker limits: size pods for it.

## Multi-pod Redis recipe (from the guidance article)
```
REDIS_CONNECTION_STRING=<redis url>
CACHE_EXPIRY=<seconds>
ENABLE_CACHE=true
CACHE_MEMORY=REDIS
ENABLE_PAGE_CACHE=true
STORAGE=REDIS
ENABLE_ANON_PAGE_CACHE=true
ANON_PAGE_CACHE_L2_ENABLED=true
ANON_PAGE_CACHE_WARM_HOST=<public store host>
ZNODE_REVALIDATE_TOKEN=<secret>
```
Always set `CACHE_EXPIRY` with `STORAGE=REDIS`. With Sentinel list `REDIS_SENTINELS` and keep `REDIS_MASTER_NAME` equal to `REDIS_SENTINEL_MASTER_NAME`. Do not use `STORAGE=FILE` with several pods.

## Sizing and warm-up
- `WEB_CONCURRENCY` = CPU cores per pod. `KEEP_ALIVE_TIMEOUT_MS` (default 65000) must exceed the load balancer idle timeout or you see intermittent 502. Behind an ingress set `IS_INGRESS_ENABLED=true`.
- Warm-up after deploy: `ANON_PAGE_CACHE_WARM_URLS`, `ANON_PAGE_CACHE_WARM_CATEGORY_LIMIT`, `ANON_PAGE_CACHE_WARM_CONCURRENCY` (3). Warm categories, not products. The warm host must be the public store host because host is part of the key.
- Stable asset caching: set `BUILD_ID` in CI; `DISABLE_CONSOLE_LOG=true` in production.

## CDN
- `CDN_CACHE_SMAXAGE_S` above zero marks guest HTML `public, s-maxage=<n>, stale-while-revalidate=<CDN_CACHE_SWR_S>` (default 600) with `Vary: Accept-Encoding`. Personalized or excluded pages are `private, no-store`. RSC payloads included unless `CDN_CACHE_RSC=false`.
- Required: CDN rule to bypass cache for requests carrying any of the five personal cookies.
- Do: keep the query string in the cache key; respect origin `Cache-Control`. Do not: force-cache HTML or strip query strings.

## Cloudflare rules (article defaults, evaluated top to bottom)
1. HTML: eligible, edge TTL 2 hours, serve stale while revalidating.
2. Static content (js, css, png, jpg, svg, webp, gif, ico, jpeg for your store domain): edge TTL 1 hour.
3. Bypass /cart, /checkout, /my-account, /account.
4. Bypass when cookie contains the session or cart cookies, or path contains login.
5. Bypass non-GET.
6. Bypass the Admin host.
7. Bypass /api/auth, /login, /signin.
All seven should be Active; rules 2 and 6 need your host values; verify cookie names before enabling rule 4.
Admin side: Stores > Additional Attributes > Cloudflare Setting: **Enable Cloudflare**, **Zone ID**; plus API token (Cloudflare My Profile > API Tokens), account email, API base URL. Every purge flushes the whole zone (cold cache afterwards: plan publishes for low traffic). A wrong Zone ID can make purges fail or clear the wrong zone.

## Not documented
Admin-side API response caching, its lifetimes and how to clear it; any Admin button other than Cloudflare's Cache Management mention.
