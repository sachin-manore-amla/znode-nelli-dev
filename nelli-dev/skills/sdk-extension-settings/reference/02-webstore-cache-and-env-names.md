# Webstore caching, revalidation and environment variable names

What this answers: which Webstore environment variables control caching, page cache, CDN headers, revalidation and API calls, what each does and defaults to. Names and purposes only. Never copy values from an environment file into a document, ticket or chat.
Verified in the Webstore source (90) and the KB Webstore Customization Guide (80). Apply rule for every variable here: the Webstore process reads it at start, so a change needs a restart or redeploy of the Webstore.

## 1. Data and page cache

| Variable | Default | Effect |
|---|---|---|
| `ENABLE_CACHE` | unset means off; only the text `true` turns it on | Server side API response caching in the data layer |
| `CACHE_MEMORY` | `FILE` (KB: MEMORY or FILE) | `REDIS` selects the shared Redis cache handler for the Next.js cache |
| `CACHE_EXPIRY` | 3600 seconds in the Redis handler | Life of a cached entry |
| `STORAGE` | none | Cache backend choice: file, redis or cdn (KB) |
| `ENABLE_PAGE_CACHE` | off; `true` enables | Page builder page data caching for pages that are not dynamic |
| `PORTAL_CACHE_TTL_MS` | 900000 (15 minutes) | Life of store (portal) data in each Webstore process |
| `PORTAL_CACHE_NEGATIVE_TTL_MS` | 60000 | Life of a failed store lookup |
| `PORTAL_CACHE_MAX_ENTRIES` | 500 | Entries kept |
| `ENABLE_REAL_TIME_PRICING` | on unless the text is `false` | `false` stops the price refresh on list and detail pages |
| `API_FETCH_TIMEOUT_MS` | 30000 | Timeout of calls to the API |
| `CACHE_DEBUG_LOG` | off | Verbose cache log |

## 2. Anonymous page cache and CDN

| Variable | Default | Effect |
|---|---|---|
| `ENABLE_ANON_PAGE_CACHE` | off; `true` enables | Full page cache for guests |
| `ANON_PAGE_CACHE_TTL_MS`, `ANON_PAGE_CACHE_STALE_TTL_MS` | 60000, 600000 | Fresh and stale lifetime |
| `ANON_PAGE_CACHE_MAX_ENTRIES`, `ANON_PAGE_CACHE_MAX_BODY_BYTES`, `ANON_PAGE_CACHE_MAX_TOTAL_BYTES` | 500, 5 MB, 256 MB | Size limits |
| `ANON_PAGE_CACHE_L2_ENABLED` | off | Shared Redis layer |
| `ANON_PAGE_CACHE_L2_KEY_PREFIX`, `ANON_PAGE_CACHE_L2_LOCK_PREFIX`, `ANON_PAGE_CACHE_L2_TIMEOUT_MS`, `ANON_PAGE_CACHE_L2_LOCK_TTL_MS`, `ANON_PAGE_CACHE_L2_LOCK_WAIT_MS`, `ANON_PAGE_CACHE_L2_LOCK_POLL_MS`, `ANON_PAGE_CACHE_L2_COMPRESSION`, `ANON_PAGE_CACHE_L2_COMPRESSION_MIN_BYTES` | prefixes, 80 ms, 10000, 800, 50, on, 1024 | Redis layer tuning |
| `ANON_PAGE_CACHE_WARM_URLS`, `ANON_PAGE_CACHE_WARM_INTERVAL_MS`, `ANON_PAGE_CACHE_WARM_CATEGORY_LIMIT`, `ANON_PAGE_CACHE_WARM_CONCURRENCY`, `ANON_PAGE_CACHE_WARM_HOST`, `ANON_PAGE_CACHE_WARM_ONCE`, `ANON_PAGE_CACHE_WARM_LOCK_TTL_MS` | none, 0, 0, 3, store domain, on, 300000 | Cache warming |
| `ANON_PAGE_CACHE_PURGE_ON_REVALIDATE` | on; `false` opts out | Full purge on a broad content refresh |
| `CDN_CACHE_SMAXAGE_S`, `CDN_CACHE_SWR_S`, `CDN_CACHE_RSC` | 0 (off), 600, on | Public cache headers for anonymous pages; `CDN_CACHE_RSC=false` caches HTML only |

## 3. Revalidation and security

| Variable | Effect |
|---|---|
| `ZNODE_REVALIDATE_TOKEN` | Must equal the secret the API sends. Revalidation routes: `/api/revalidate-with-token`, `/api/revalidate-all-with-token`, `/api/revalidate`, `/api/revalidate-all`, `/api/anon-cache/purge`. Mismatch gives 401 and nothing is cleared |
| `ZNODE_DEBUG_TOKEN` | Protects the debug routes. Leave unset or secret in production |
| `NEXTAUTH_SECRET`, `NEXT_ENCRYPTION_SECRET`, `SECRET`, `REFRESH_SECRET`, `ACCESS_SECRET`, `CLIENT_ID`, `CLIENT_SECRET`, `API_KEY` | Secrets. Names only |
| `NEXTAUTH_URL` | Base URL for sign in callbacks |

## 4. Connection, runtime and feature switches

| Variable | Default | Effect |
|---|---|---|
| `API_URL`, `API_DOMAIN`, `API_V2_DOMAIN`, `WEBSTORE_DOMAIN_NAME`, `PORTAL_DOMAIN_NAME` | none | Where the API and the store domains are |
| `NEXT_PUBLIC_PAYMENT_MANAGER_URL`, `NEXT_PUBLIC_SPREEDLY_PLUGIN_URL` | none | Payment service addresses exposed to the browser |
| `REDIS_CONNECTION_STRING`, `REDIS_SENTINEL_ENABLED`, `REDIS_SENTINELS`, `REDIS_MASTER_NAME`, `REDIS_SENTINEL_MASTER_NAME`, `REDIS_PASSWORD` | none | Redis connection: secrets |
| `WEB_CONCURRENCY` | 1 | Worker processes |
| `KEEP_ALIVE_TIMEOUT_MS` | 65000 | HTTP keep alive |
| `IS_INGRESS_ENABLED` | off | Behind an ingress |
| `IS_301_REDIRECT` | off | `true` enables 301 redirect handling in the middleware |
| `ENABLE_IFRAME_COOKIES` | production always on | Cookies for page builder iframe use |
| `ENABLE_PAGE_BUILDER_SIGNUP_LOGIN`, `ENABLE_PAGE_BUILDER_TRACK_QUICK_ORDER_FORGOT_PASSWORD` | off | Render those pages through Page Builder |
| `ECOMMERCE_DATA_LAYER_MODE`, `NEXT_PUBLIC_ECOMMERCE_DATA_LAYER_MODE` | `ua` | Analytics data layer mode: `ua`, `ga4` or `both` |
| `TRADECENTRIC_COOKIE_TTL` | 7200 seconds | TradeCentric cookie life |
| `LOGGING_METHOD` | `FILE` | `FILE` or `CONSOLE` |
| `DISABLE_CONSOLE_LOG`, `ENABLE_INFO_LOG`, `IS_DEBUGGING`, `DEFAULT_THEME`, `APP_NAME`, `NODE_ENV`, `PORT`, `HOSTNAME`, `NEXT_PUBLIC_GEO_CODE_URL`, `NEXT_PUBLIC_GOOGLE_MAP_API_KEY` | various | Logging, debug, theme, runtime, map settings |

## 5. Caching map for "my change does not show"

| Change | Layers that can hold the old value | Fix |
|---|---|---|
| Store flag | API by code answer (20 min), Webstore portal data (15 min) | Event Subscription URL plus matching secret, or wait, or clear |
| Published product, catalog, category | Next.js data cache, page cache, anonymous page cache, CDN | Publish; revalidation through the Event Subscription URL; Global Settings > Cache Management purges the CDN |
| Global setting | Rarely stored in the Webstore | Save; see `config-global-settings` |
| Webstore source change | Build output | Rebuild and restart |

Cloudflare (KB): publishing a catalog, product or store, or a manual purge under `Global Settings > Cache Management`, flushes the whole zone. Store attributes needed: Enable Cloudflare Yes and the Zone ID.
