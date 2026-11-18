# Environment variable names and purposes

What this answers: which environment variables the Webstore and Page Builder apps read, what each is for, and where it applies. Names only, never values.
Confidence: names read from the Webstore source (90); descriptions for the first group are from the KB "Webstore Customization Guide" and "Webstore Development & Page Builder Setup Guide" (80). Defaults are from the source where stated.

Rules: set server variables for `webstore`, and for `page-builder` when shared code reads them. `NEXT_PUBLIC_*` values are public. Restart after changing.

## Core (KB documented)

| Name | Purpose |
|---|---|
| `API_URL` | base URL of the gateway used for all API calls (most used variable) |
| `API_DOMAIN` | domain registered on the backend; with `API_KEY` it forms the Basic token. Not an endpoint |
| `API_V2_DOMAIN` | domain for version 2 of the API (KB) |
| `API_KEY` | domain key paired with `API_DOMAIN` |
| `NEXTAUTH_URL` | base URL for NextAuth callbacks |
| `NEXTAUTH_SECRET` | NextAuth secret (KB). The source also reads `SECRET`, `REFRESH_SECRET`, `ACCESS_SECRET`, `NEXT_ENCRYPTION_SECRET`; confirm which your version needs from the `.env` template |
| `WEBSTORE_DOMAIN_NAME` | public domain of the Webstore (also links Page Builder to the Webstore) |
| `DEFAULT_THEME` | fallback theme when the store returns none |
| `APP_NAME` | `WEBSTORE` or `PAGE_BUILDER`; changes behaviour (page cache, maintenance redirects, store lookup by host or by store code) |
| `NEXT_PUBLIC_PAYMENT_MANAGER_URL` | payment manager URL, browser-exposed |
| `NEXT_PUBLIC_GEO_CODE_URL`, `NEXT_PUBLIC_GOOGLE_MAP_API_KEY` | geocoding and maps, browser-exposed |
| `LOGGING_METHOD` | `FILE` or `CONSOLE` |
| `CACHE_MEMORY`, `STORAGE` | cache storage type; `STORAGE` is `file`, `redis` or `cdn` (KB) |
| `ENABLE_CACHE` | `true` enables the Next data cache for tagged API calls; anything else disables it |
| `REDIS_CONNECTION_STRING` | Redis for caches and cross-pod eviction |
| `IS_DEBUGGING` | `true` reads page JSON from local files; development only |
| `NODE_TLS_REJECT_UNAUTHORIZED` | `0` disables TLS validation; development only |
| `ZNODE_DEBUG_TOKEN` | secret for the debug routes; separate value per environment |
| `ZNODE_REVALIDATE_TOKEN` | shared secret for the token revalidation routes (must equal the API setting `WebstoreWebhookSecret`) |
| `ENABLE_PAGE_BUILDER_SIGNUP_LOGIN` | `true` renders login and signup through Page Builder |
| `ENABLE_PAGE_BUILDER_TRACK_QUICK_ORDER_FORGOT_PASSWORD` | `true` renders track order, quick order, forgot password through Page Builder |
| `ENABLE_ANON_PAGE_CACHE`, `ANON_PAGE_CACHE_MAX_TOTAL_BYTES`, `ANON_PAGE_CACHE_L2_ENABLED` | anonymous page cache switches (KB); defaults off, 268435456 bytes, off |

## Present in the source, not in the KB articles read

| Name | Purpose (from reading the code) |
|---|---|
| `ENABLE_PAGE_CACHE` | caches page structures and widget data |
| `ENABLE_REAL_TIME_PRICING` | set `false` to skip live price refresh on product list and details |
| `ANON_PAGE_CACHE_TTL_MS`, `_STALE_TTL_MS`, `_MAX_ENTRIES`, `_MAX_BODY_BYTES`, `_PURGE_ON_REVALIDATE` | anonymous cache sizing and behaviour |
| `ANON_PAGE_CACHE_WARM_URLS`, `_WARM_ONCE`, `_WARM_INTERVAL_MS`, `_WARM_HOST`, `_WARM_CONCURRENCY`, `_WARM_CATEGORY_LIMIT`, `_WARM_LOCK_TTL_MS` | pre-rendering at boot |
| `ANON_PAGE_CACHE_L2_KEY_PREFIX`, `_L2_TIMEOUT_MS`, `_L2_LOCK_*`, `_L2_COMPRESSION`, `_L2_COMPRESSION_MIN_BYTES` | shared Redis tier tuning |
| `CDN_CACHE_SMAXAGE_S`, `CDN_CACHE_SWR_S`, `CDN_CACHE_RSC` | CDN cache-control headers |
| `PORTAL_CACHE_TTL_MS`, `PORTAL_CACHE_MAX_ENTRIES`, `PORTAL_CACHE_NEGATIVE_TTL_MS` | in-memory store data cache |
| `REDIS_SENTINEL_ENABLED`, `REDIS_SENTINELS`, `REDIS_SENTINEL_MASTER_NAME`, `REDIS_MASTER_NAME`, `REDIS_PASSWORD` | Redis sentinel setup |
| `CACHE_EXPIRY`, `CACHE_DEBUG_LOG`, `NEXT_PRIVATE_DEBUG_CACHE` | cache expiry and debugging |
| `WEB_CONCURRENCY` | number of worker processes (default 1) |
| `PORT`, `HOSTNAME`, `KEEP_ALIVE_TIMEOUT_MS`, `IS_INGRESS_ENABLED` | server binding and keep-alive (default timeout 65 s) |
| `API_FETCH_TIMEOUT_MS` | timeout for API calls |
| `BUILD_ID` | stable build id for chunk names (falls back to the git short hash) |
| `IS_301_REDIRECT` | `true` enables stored 301 redirects in middleware |
| `ENABLE_IFRAME_COOKIES` | secure, same-site settings so the editor works inside the Admin iframe outside production |
| `NEXT_PUBLIC_SPREEDLY_PLUGIN_URL` | Spreedly payment script URL |
| `ECOMMERCE_DATA_LAYER_MODE`, `NEXT_PUBLIC_ECOMMERCE_DATA_LAYER_MODE` | analytics data layer mode |
| `TRADECENTRIC_COOKIE_TTL` | punch-out cookie lifetime |
| `ENABLE_INFO_LOG`, `DISABLE_CONSOLE_LOG` | logging switches |
| `PORTAL_DOMAIN_NAME`, `CLIENT_ID`, `CLIENT_SECRET` | read in the source; purpose not confirmed (see GAPS) |

## Not environment variables (differs from the KB)

`NEXT_PUBLIC_RECAPTCHA_SITE_KEY` and `RECAPTCHA_SECRET_KEY` (KB reCAPTCHA article) are not read anywhere in the source. reCAPTCHA keys are store settings in Admin. See `kb-vs-product.md`.
