---
name: api-consumption
description: How to call Znode APIs from a custom or headless application - the API families and their gateway route prefixes, authentication (Basic client credentials versus JWT, the token endpoints and their bodies, expiry and refresh), context headers (portal, locale, publish state, user, account) and what happens when they are missing, paging, filter and sort syntax, error shapes, the Custom API route key convention, call order for common flows, v1 legacy versus v2 and Commerce, and size and rate cautions. Use when building a headless storefront, a server integration, a mobile app, or when a call returns 401, 400 or empty data.
user-invocable: false
---

# Consuming Znode APIs

## What it is
Every Znode API call goes through one **gateway** that authenticates it and routes it by path prefix to the service that owns the operation. Your app talks only to the gateway. Terms people confuse: *Basic* (client name and key, server-to-server) versus *JWT Bearer* (token from the token endpoints, recommended); *v1* (legacy routes with PascalCase names) versus *v2 and v2.1* (kebab-case routes) versus *Commerce API* (orders, carts, quotes, returns); *context headers* (`Znode-PortalCode` and friends) versus *auth headers*.

## Use / do not use
| Need | Verdict |
|---|---|
| Headless storefront, mobile app, partner integration | Supported: gateway APIs with JWT |
| Server job reading or writing Znode data | Supported: Basic or JWT from a server, secrets server side |
| New work on legacy v1 routes | Do not recommend; use v2 or Commerce. v1 only where no v2 operation exists (say so) |
| Browser code holding client credentials | Not acceptable: never expose client keys in client-side code |
| Calling a Znode service directly, bypassing the gateway | Not supported for customers |

## The facts that matter most
1. All APIs accept `Authorization: Basic <base64>` or `Authorization: Bearer <jwt>`. HTTPS only.
2. Basic value is base64 of `clientName:clientKey` (the older `clientName|clientKey` form is also accepted). The client must exist for your tenant; ask Znode Support or your DevOps contact how to create or rotate one.
3. JWT: `POST /Token` body `{"ClientName","ClientKey"}` returns `Token`, `RefreshToken`, `HasError`. User token: `POST /UserToken` body adds `StoreCode`, `UserName`, `UserPassword`. Refresh: `POST /RefreshJWTToken` body `{"RefreshToken"}`. Revoke: `POST /RevokeToken`. These four routes need no Authorization header.
4. Defaults: access token 30 minutes, refresh token 30 days (platform settings; the KB agrees).
5. Context headers: `Znode-PortalCode` (store), `Znode-LocaleCode`, `Znode-PublishState` (`Production` or `Preview`), `Znode-UserId` (`0` for guest), `Znode-AccountId` or `Znode-AccountCode`, `Znode-CatalogCode`, `Znode-ProfileId`, `Znode-DomainName`. Which ones an operation needs is on its API reference page.
6. A JWT with a user sets `Znode-UserId` itself; do not send a different user id.
7. Lists use `pageIndex` (1-based), `pageSize` (default 10), `filter={Field}~{op}~{value}` (repeat for AND), `sort={field}~{asc|desc}`.
8. Custom endpoints you deploy are reached through the same gateway under routes you add to the Custom Ocelot file with route key `customapi`.
9. Errors: HTTP status plus a JSON body with `ErrorMessage` and `ErrorCode` (often `HasError`, `StatusCode`). The documentation page shows a different generic shape: code on the status.
10. Published (customer-facing) product, brand and category APIs read the last **published** snapshot; Draft APIs read the working copy.

## Decision guide for Nelli-Dev
| Requirement | Verdict and approach |
|---|---|
| Headless app calls (catalog, cart, checkout) | **Supported.** Server-side BFF holds the client credentials, obtains a user JWT after login, sends context headers, calls published APIs for browsing and Commerce API for cart and order. Cache catalog reads |
| Mobile app login | Supported: `POST /UserToken` through your BFF; store only the refresh token securely |
| Server sync job | Supported: Basic or `/Token`, page through lists, back off on 429 and 5xx |
| Enrich an API response (add fields from another system) | Customizable: a custom endpoint that calls the Znode API and adds data (GET changes apply after the Znode call, POST before). Changing the Znode response itself is a platform change |
| Call returns empty data | Check the context headers first (reference 02) |
| 401 | Missing or expired token, wrong client, or the route needs the other auth type (reference 01) |
| Need an API Znode does not expose | Needs platform change: raise a request; do not use database access |
| Bulk reads for reporting | Page with `pageSize` at most 100 to 500, filter server side; for files use export or Data Exchange (`config-import-export`) |

## Reference files
- `reference/01-auth.md` Basic and JWT, token endpoints, errors, refresh, security
- `reference/02-headers-and-context.md` every context header, defaults, behaviour when missing
- `reference/03-gateway-and-families.md` API families, route prefixes, versions, custom routes
- `reference/04-conventions-and-flows.md` paging, filters, sort, error shapes, caching, call order for common flows, cautions

Related: `api-catalog` (which operation), `api-auth-and-headers`, `sdk-custom-api`, `quality-security-checks`.
