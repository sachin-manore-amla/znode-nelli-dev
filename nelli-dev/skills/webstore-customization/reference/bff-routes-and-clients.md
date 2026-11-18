# BFF routes, clients, headers and how to add a route

What this answers: how a Webstore component reaches a Znode or Custom API through the Webstore server, which headers are added, how caching options work, and the exact steps to add a new route and client.
Confidence: verified in the Webstore source (read 2026-10-15). Header names are the strings in the source; the meaning of each on the API side is in skill `api-auth-and-headers`.

## The pattern

`apps/webstore/src/app/api/<name>/route.ts` exports `GET`, `POST`, `PUT` or `DELETE`. There are about 80 route folders (account, cart, checkout, payment, search, quick-order, punch-out, page-builder, revalidate and others). Each handler:

1. reads the store context with `getPortalHeader()` (store code, locale, theme, publish state; looked up from the request host name through a global cache),
2. reads the signed-in user with `getSavedUserSession()` (from the session cookie),
3. calls an agent in `packages/agents`,
4. answers with `sendSuccess(data, message)` (JSON `{ status: "success", message, data }`) or `sendError(message, statusCode)` (plain text body).

Browser code calls these through `httpRequest()` in `packages/base-components/src/http-request/base.ts`, which returns `jsonResponse.data`, sends `cache: "no-store"`, and adds the encrypted checkout reference and tax-exempt headers from session storage when present.

Which routes need a signed-in user: each route checks for itself. Typical pattern (account routes): `const user = await getSavedUserSession(); if (!user?.userId) return sendError("...", 403)`. A helper `validateApis` in `apps/webstore/middlewares/api-auth.ts` lists `/api/account` and `/api/email-friend` as authenticated prefixes, but nothing in the source calls it, so it does not protect anything. Do not rely on it; check the session in every new private route. The middleware does apply to `/api` calls for maintenance mode, store checks and the admin-only account routes (`ADMIN_RESTRICTED_PATHS.API` in `packages/constants/src/app.ts`).

## Headers the Webstore adds to every Znode call

Built in `packages/clients/src/znode-client/V2/base.ts` (`getApiHeaders`, also used by the `custom` client):

| Header | Value |
|---|---|
| `Authorization` | `basic` plus a base64 of the domain name and domain key, from `API_DOMAIN` and `API_KEY` |
| `Znode-PortalCode` | store code |
| `Znode-LocaleCode` | active locale (cookie `NEXT_LOCALE`, default `en-US`) |
| `Znode-PublishState` | `Preview` or `Production` according to the store's publish state |
| `Znode-DomainName` | store host name |
| `Znode-UserId`, `Znode-AccountId`, `Znode-AccountCode` | signed-in user and account (user id and account id omitted for guests in `getApiHeaders`; `getUserApiHeaders` sends 0) |
| `Z-Request-Context` | encrypted `{StoreFront};{userId};{crsUserId}` value (the API side uses it to tie the call to a user; purpose is my inference from the format) |
| `Accept` / `Cache-Control` | `text/plain` / `no-store` |
| `Content-Type` | `application/json-patch+json` for POST and PUT |

Consequences for customizers:

- The domain key never reaches the browser. Do not move Znode calls into client components.
- A Custom API behind the same gateway receives these headers. Validate them on the Custom API side as in `sdk-custom-api` and `quality-security-checks`; never trust a user id sent in a request body.
- Calling an API without the portal headers returns empty data, not an error (see `api-auth-and-headers`).
- How a non-Webstore client should build `Z-Request-Context` is not documented; ask Znode before depending on it (see `webstore-headless-api`).

## Clients and API versions

| Client alias | Folder | Talks to |
|---|---|---|
| `@znode/clients/v2` | `packages/clients/src/znode-client/V2` | Core API v2 (`v2/...` and `v2.1/...` routes: published products, published categories, search, users, portals, addresses, content pages, widgets) |
| `@znode/clients/cp` | `.../commerce` | Commerce API (`commerceapi/v1/{classType}/...`: carts, checkout, place order, orders, returns, payments, shippings, order templates) with `classType` values such as `carts`, `checkout`, `quotes` |
| `@znode/clients/v1` | `.../V1` | Core API v1 (legacy). The Webstore still uses it in places (shopping cart, order, quote, customer). Do not copy it for new work; use v2 or Commerce (see `api-catalog`) |
| `@znode/clients/payment`, `/shipping-manager` | `.../payment-manager`, `.../shipping-manager` | payment and shipping manager services |
| `@znode/clients/custom` | `.../custom` | your own Custom API (see below) |

Client files are generated-style code: each function builds the URL from `process.env.API_URL`, calls `customFetch`, and maps status codes. Responses come back in PascalCase and agents convert with `convertCamelCase` / `convertPascalCase`.

## Caching options on client calls

`addCacheOption` (V2 `base.ts`):

| Situation | Result |
|---|---|
| `ENABLE_CACHE` is not `true`, or the call is in the browser | no Next data cache (`cache: "no-store"`) |
| `ENABLE_CACHE=true`, server call, filter list contains a `CacheTags` entry | `cache: "force-cache"` with Next cache tags prefixed `webstore` plus `webstoreGlobal`; the identity headers are normalised so anonymous callers share one cache entry |
| `ENABLE_CACHE=true`, server call, no `CacheTags` | `revalidate: 0` |

So a custom client call is never cached unless you pass a `CacheTags` filter and `ENABLE_CACHE=true`. Tag-based entries are evicted by the revalidation routes (see `caching-and-visibility.md`).

## Recipe: add a BFF route that calls a Custom API endpoint

1. Add a client function in `packages/clients/src/znode-client/custom/<feature>/<feature>.ts`. Copy the shape of `user-activity/user-activity.ts`: `const baseUrl = process.env.API_URL`, build the URL, `headers: await getHeaders("GET" | "POST", String(baseUrl))`, `customFetch(url, options, "<name>")`, and map status codes. Export it from `custom/index.ts`. The Custom API route must be reachable through the gateway (an Ocelot route in your Custom API project, see `sdk-custom-api`).
2. Add an agent `packages/agents/src/<feature>/<feature>.ts` (and `index.ts`) that calls the client, converts case, catches errors, logs with `logServer.error(AREA.X, errorStack(error))`, and returns a safe default.
3. Add the route `apps/webstore/src/app/api/<feature>/route.ts`:
   ```ts
   import { sendError, sendSuccess } from "@znode/utils/server";
   import { getMyFeature } from "@znode/agents/my-feature";
   export async function GET() {
     try { return sendSuccess(await getMyFeature()); }
     catch (error) { return sendError("Failed to load feature. " + String(error), 500); }
   }
   ```
   (Do not return the raw error text to the browser in production code; log it and send a generic message.)
4. Add a browser wrapper in `packages/base-components/src/http-request/<feature>/` using `httpRequest<T>({ endpoint: "/api/<feature>" })`, export it from the folder `index.ts` and from `http-request/index.ts`.
5. Call the wrapper from a client component, or call the agent directly from a server component.
6. If the route needs a signed-in user, read it with `getSavedUserSession()` and answer 403 when there is none. Never accept a user id from the request body.
7. Run `npx nx lint webstore` and `npx nx build webstore`.

## Rules for new routes

| Rule | Why |
|---|---|
| Keep secrets in server env vars, never `NEXT_PUBLIC_*` | `NEXT_PUBLIC_*` values are in the browser bundle |
| Validate input and ownership in the Custom API, not only the route | the route is reachable by anyone who can reach the store |
| One API call per interaction where possible | each hop adds latency; see `quality-performance-checks` |
| Do not call Core API v1 for new work | see `api-catalog` |
| Use `sendSuccess` / `sendError` | browser wrappers expect `{ data }` |
