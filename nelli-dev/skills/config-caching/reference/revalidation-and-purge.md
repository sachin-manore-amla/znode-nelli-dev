# Revalidation and purge
What this answers: which calls refresh the Webstore caches, how they are secured, how to verify caching and what each symptom means.
Sources: KB Secure Cache Revalidation Configuration; Storefront Performance and Caching Guidance (read 2026-11-23). Confidence 85.

## Secret
| Application | Name | Required |
|---|---|---|
| Webstore | `ZNODE_REVALIDATE_TOKEN` | yes |
| API | `WebstoreWebhookSecret` | yes |
The two values must be identical, environment-specific and random. The KB does not name the request header the API uses to send it ("confirm in the source code or with Znode support"); the guidance article shows `x-secret` for calls you make yourself.

## Routes
| Route | Use |
|---|---|
| `POST /api/revalidate-with-token` | normal refresh after a publish event; updates data tiers on all pods |
| `POST /api/revalidate-all-with-token` | full reset: revalidates every tagged response and deletes every key in the cache store; recovery only |
| `POST /api/anon-cache/purge` (header `x-secret`) | guest page cache; empty body clears all (this worker, sibling workers, other pods, Redis); `{"path":"/category/5602"}` clears all variants of one URL |
| `/api/revalidate`, `/api/revalidate-all` | deprecated, unauthenticated, temporary: do not use |
Purge result: `purged: true`, `entriesCleared`, `broadcast` (`cluster`, `redis`, `l2`). Errors: 403 wrong secret; empty 404 no token configured; 503 not running under the custom server.

## Deployment checklist (from the KB)
1. Generate the secret. 2. Set it on the Webstore. 3. Set the same on the API. 4. Verify match. 5. Deploy. 6. Restart if your process requires. 7. Validate a revalidation. 8. Confirm unauthorized requests get 401. Needs no database change.

## Refresh timing
| Tier | Refreshes | Action |
|---|---|---|
| Data cache | immediately | automatic |
| Page structure | immediately | automatic |
| Guest pages | within TTL (60 s) | purge if urgent |
| CDN | within `s-maxage` | purge if urgent |

## Verify
```
curl -s -o /dev/null -D - -H "Accept-Encoding: gzip" https://<store-domain>/ | grep -i -E "x-anon-cache|cache-control"
curl -s -o /dev/null -D - -H "Cookie: CartId=1" https://<store-domain>/ | grep -i x-anon-cache
```
First run MISS then HIT; second command BYPASS.

| Observation | Meaning |
|---|---|
| no `x-anon-cache` header | guest page cache off, or app not on the custom server |
| MISS every time | not a clean 200 HTML, over size, or requests differ in host, device, encoding, locale or query |
| `x-anon-cache-tier: L2` | served from Redis |
| `public, s-maxage=...` | CDN caching on |
| `private, no-store` | personalized, excluded or stale; CDN must not keep it |

## Troubleshooting
| Symptom | Cause and fix |
|---|---|
| Publish visible to buyers, not to guests | guest cache or CDN holds the page: wait for TTL or purge |
| Logged-in buyer sees a guest page | missing CDN cookie bypass rule |
| One visitor sees another's content | personalized public page cached: exclude its path, `no-store` its data |
| Content differs between pods | caches not shared: Redis settings; check `cache-eviction` subscription log |
| Revalidation 401 | token missing or different |
| Revalidation 500 | pod cannot reach Redis |
| Pods restart under load | lower `ANON_PAGE_CACHE_MAX_TOTAL_BYTES` or `WEB_CONCURRENCY`, add memory |
| Intermittent 502 | `KEEP_ALIVE_TIMEOUT_MS` below the load balancer idle timeout |
Debug aids: `CACHE_DEBUG_LOG=true` (briefly); log lines `[anon-cache] purged n entries`, `Subscribed to Redis channel: cache-eviction`, `data evicted with tag`; `/api/debug` with a debug-token header for named client functions.

## Security notes
Only the POST purge handler should be reachable from outside; secure or remove any validation-only GET handler and restrict diagnostic routes at ingress. Never put the token in a URL.
