---
name: webstore-headless-api
description: Using Znode as a headless back end from a separate front end (React app, mobile app, other storefront) - what the Knowledge Base says about headless API consumption, which API families to use (Core v2 and Commerce), authentication and context headers, the call order for product list and detail, search, cart, checkout and order placement as the shipped Webstore performs it, caching, CORS and rate-limit guidance, and what is not documented. Use when a requirement is "build our own front end", "call Znode from the browser or mobile app", or when deciding between modifying the Webstore and replacing it.
user-invocable: false
---

# Headless API consumption

Znode is a headless platform: the shipped Webstore is itself a client of the same APIs. A custom front end can replace it, or sit beside it. Sources: KB "Headless API Consumption" (read in full), "React App & API - Troubleshooting guidelines" (read in full), the public API reference and spec files (Core v2 "Customer" spec and Commerce spec, read 2026-10-15), and the Webstore source, which shows the real call order.

## Ten facts that matter most

1. Two families cover storefront work: the Core API v2 (catalog, search, store settings, users, addresses, CMS) and the Commerce API (carts, checkout, orders, returns, payments, shippings). Do not use Core API v1 for new work (`api-catalog`).
2. Everything goes through the API gateway; routes are kebab-case with camelCase parameters (KB best practices).
3. Store context is mandatory. Without the store code header, calls return empty data instead of an error (`api-auth-and-headers`).
4. The Webstore authenticates server to server with a Basic token (domain name and domain key) plus context headers, and never exposes the key to the browser. A browser or mobile app must not hold that key either: put a thin back end (a BFF) in front, as the Webstore does.
5. The KB describes customer-facing JWT: obtain a token, send `Authorization: Bearer <token>`; sample token lifetime 30 minutes and refresh 30 days (the sample settings `JWTExpirySpan` 30 and `JWTRefreshExpirySpan` 30). The KB says `POST /token` on the instance URL; I could not find that route in the public specs (see GAPS). The documented shopper login is `POST /v2.1/users/login` (the v2 route is deprecated).
6. Prices, inventory, tax, shipping and promotions are computed by the API. A custom front end displays and submits; it must not recompute them.
7. Cart and checkout are addressed by a class type and number: `commerceapi/v1/{classType}/...` with class types such as `carts`, `checkout`, `quotes`.
8. Place order is `POST /{classType}/place-order/{classNumber}` on the Commerce API, after cart validation and payment preparation. Payments run through the payment manager and plugins.
9. Publish state matters: shoppers read production data; preview needs a preview publish. Catalog, price and inventory changes reach the API after publish.
10. Page Builder pages are stored as JSON and rendered only by the Webstore stack (React with the Puck editor). A different front end can read content through the CMS APIs but cannot reuse Page Builder JSON without that renderer.

## Reference files

| Need | File |
|---|---|
| Families, auth, headers, tokens, errors | `reference/api-families-auth-and-errors.md` |
| Call order for product list, detail, search, cart, checkout, order | `reference/storefront-call-order.md` |
| Caching, CORS, rate limits, security, testing, KB gaps | `reference/caching-cors-security-and-gaps.md` |
| Customizing the shipped Webstore instead | skill `webstore-customization` |

## Nelli-Dev decision guide

| Requirement | Verdict | Route |
|---|---|---|
| Own React or mobile storefront | Customizable (outside the Webstore) | BFF plus Core v2 and Commerce APIs; effort is a full storefront (search, PDP, cart, checkout, account, payments, tax, SEO, CMS) |
| Add one custom page or widget to the existing store | Customizable | do it in the Webstore (`webstore-customization`), not headless |
| Embed catalog data in another site (read only) | Customizable | Core v2 published products, categories, search through a server-side proxy; mind caching and store headers |
| Call APIs straight from browser JavaScript | Not advised | would expose credentials; use a BFF. CORS behaviour of the gateway is not documented |
| Mobile app login | Customizable | `POST /v2.1/users/login` through a BFF, hold the returned token server-side or in the platform secure store |
| Reuse Page Builder pages in another front end | Needs platform change or your own renderer | JSON is Puck data; see fact 10 |
| Custom business endpoint needed by the front end | Customizable | Custom API SDK, reached through the gateway (`sdk-custom-api`) |
| Bypass the gateway or read the database | Not allowed | no customer path |
| New payment provider in a custom front end | Customizable | payment plugin (`sdk-provider-plugins`); the front end only collects tokens through the provider script |
| Need an operation that does not exist | Needs platform change | verify in the spec first (`api-catalog`) |
