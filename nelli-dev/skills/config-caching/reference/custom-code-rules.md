# Rules for customization code
What this answers: how a Webstore customization or BFF route must fetch, tag, cache and invalidate data.
Sources: KB Storefront Performance and Caching Guidance; Znode Storefront Caching Architecture and Performance Guide; Customizing Storefront Data Retrieval (read 2026-11-23). Confidence 85. File names are those of the customer's Webstore source as the KB names them; check them in your clone.

## Decide whether to cache (in order)
1. Not the same for every visitor: never cache (`no-store`, exclude the path).
2. Changed by a Znode publish: tag it with the platform cache tags.
3. Changes without a publish: fetch fresh per request.
4. Otherwise: safe as static reference data.
For public pages ask whether guests can accept a delay of the page TTL plus CDN `s-maxage`; if not, exclude the path or purge after each change.

| Data | Shared cache | Method |
|---|---|---|
| Catalog, categories, brands, content, CMS widgets, store settings | yes | cache tags (`FilterCollection`, `generateTagName`) |
| Guest HTML of public pages | yes | automatic |
| Buyer-specific prices and stock | no | live pricing, `no-store` |
| Cart, checkout, orders, quotes, addresses, account | no | `cache: "no-store"`; paths already excluded |
| Anything read from session, cookies or per-visitor headers | no | `no-store`; exclude path if public |

## Tag pattern
Create a `FilterCollection`, add `FilterKeys.CacheTags` with `FilterOperators.Contains`, build the value with `generateTagName` from `CACHE_KEYS.PORTAL`, `CACHE_KEYS.DYNAMIC_TAG`, the store code and an operation name, and pass the filter list to the client call. The client turns the filter into Next.js tags (each prefixed `webstore`, plus `webstoreGlobal`) and never sends it to the back end. With `ENABLE_CACHE=true`, tagged server calls use `force-cache`; untagged or browser calls are not cached.
Use the **same `CACHE_KEYS` key and ID combination** the baseline agents use, so the same publish event refreshes your data. Do not tag data that publish events do not cover unless your back end triggers revalidation.

## Custom Redis or BFF caching
Use only when data comes from an external service, needs aggregation, is shared across requests, cannot be page-cached, or a custom BFF fetches the same thing repeatedly. Every custom cache must: use store-specific key prefixes; define a TTL; define an invalidation strategy; **fail open** (a cache outage degrades to live retrieval, never to an application error).
Key format: `{app}:{environment}:{storeId}:{entity}:{identifier}:{facet}:{version}`, for example `znode:prod:12:product:SKU-1234:pricing:v2`.
Prefer CDN caching before adding Redis.

## Performance rules for customizations
| Rule | Guidance |
|---|---|
| Fetch on the server | call agents from Server Components; pass props to client components |
| Parallelize independent calls | `Promise.all` |
| Avoid client waterfalls | one API route returning everything beats chained browser calls |
| Use the platform fetch wrapper | timeout, GET de-duplication, debug logging |
| Keep `"use client"` at leaves | client components ship their import tree |
| Lazy-load heavy UI | `next/dynamic` for dialogs, scanners, quick views |
| Use shared image components | built on `next/image`; always set dimensions |
| Bound in-memory caches | TTL and size cap; one copy per worker |
| Agents return safe defaults | a failed call must not fail the page; error renders are never page-cached |
| Mark baseline edits | changes to shared files such as the excluded-paths list need a `// CUSTOM: <reason>` comment |

## Adding an API call (outline from the KB example)
Types; client function (headers, cache option, fetch wrapper with an operation name); agent that tags the call and returns `{ ..., hasError: true }` on failure; Next.js route with `sendSuccess` / `sendError` and a 401 when customer data is requested without a session; browser helper; `"use client"` component plus locale messages; optional widget-data entry marked `// CUSTOM:` only for data identical for every visitor; run the agents' unit tests.

## Page Builder notes
Page cache key covers page, publish state, locale, account and profile. Page and widget handlers should return shared data only; the per-request step still adds live prices, stock, cart and header.

## Checklist before shipping
Keys scoped by store; TTL and invalidation path set; cart, checkout, payment and personalized data live; fail open on cache errors; CDN bypass for the five personal cookies; public pages with per-visitor content excluded and marked.
