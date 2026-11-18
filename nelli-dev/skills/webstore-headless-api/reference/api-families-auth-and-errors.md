# API families, authentication, headers and errors for a headless client

What this answers: which API and client packages a custom front end uses, how requests are authenticated, which headers a storefront call needs, and how to handle responses and errors.
Confidence: KB "Headless API Consumption" and "React App & API - Troubleshooting guidelines" (80); public Customer (Core v2) and Commerce specs (90 for operation presence); Webstore source for headers (90).

## Families and client packages

| Family | Use | Notes |
|---|---|---|
| Core API v2 | published products and categories, search, store and portal settings, users, addresses, CMS content, widgets | preferred; spec "Customer" |
| Commerce API | carts, checkout, orders, returns, payments, shippings, order templates | spec "Commerce", route prefix `commerceapi/v1` in the Webstore |
| Dynamic Data Table API | custom tables | `sdk-custom-tables` |
| Payment API (v1) | payment transactions | through the payment manager |
| Custom API | your own endpoints | `sdk-custom-api`, exposed through the gateway |
| Core API v1 | legacy | do not start new work on it |

KB lists client packages for .NET consumers: `Znode10.Engine.ApiV2.Client`, `Znode10.Engine.Api.Client`, `Znode10.Engine.CommercePortal.Client`, `Znode10.Payment.API.Client`, `Znode10.Engine.Custom.Api.Client` (generated client details come from your feed). For JavaScript the Webstore ships typed clients in its `packages/clients` folder; they are a usable pattern for your BFF.

## Authentication

| Mode | Use | Detail |
|---|---|---|
| Basic, server to server | your BFF to the gateway | `Authorization: basic <base64(domain|key)>` as the Webstore builds it from its configured domain name and domain key; keep both server-side |
| Bearer JWT, customer facing | shopper identity | KB: obtain a token, then `Authorization: Bearer <access token>` on every call. Sample response fields: `token`, `hasError`, `errorCode`, `errorMessage`, `refreshToken`, `refreshTokenExpiryTime`. Token expiry settings in the sample: `JWTExpirySpan` 30 (minutes), `JWTRefreshExpirySpan` 30 (days) |
| Shopper login | users | `POST /v2.1/users/login` (request `LoginRequestModel`, response `UserLoginResponseModel`); `POST /v2/users/login` is deprecated. Also in the spec: `POST /v2/users/login-token/{userName}` (generate a login token), `POST /v2/users/validate-login-token`, `POST /v2/auth/revoke-tokens`, `POST /v2/auth/revoke-user-token` |

The Customer spec's security scheme is a single `Authorization` header accepting `Basic {...}` or `Bearer {...}`. The Commerce spec describes API key authentication in the `Authorization` header and points to an Authentication Guide on the API reference site. Which scheme a given call needs is stated per operation; check `nd_query_spec.py op`.

Token endpoint: the KB shows `POST /token` on the instance URL. The Core v1 spec has `GET /Token/GenerateToken`. I found no `/token` route in the Core v2 or Commerce specs. Ask Znode which route issues customer tokens for your instance before building on it (GAPS).

## Context headers (what the Webstore sends)

| Header | Meaning |
|---|---|
| `Znode-PortalCode` | store code (required for store-scoped data) |
| `Znode-LocaleCode` | content locale |
| `Znode-PublishState` | `Production` or `Preview` |
| `Znode-DomainName` | store host name |
| `Znode-UserId`, `Znode-AccountId`, `Znode-AccountCode` | signed-in shopper and B2B account (omit for guests) |
| `Z-Request-Context` | encrypted caller context (`{StoreFront};{userId};{crsUserId}`); how a non-Webstore client builds it is not documented |
| `Content-Type` | `application/json-patch+json` for POST and PUT in the Webstore |

More on each: `api-auth-and-headers`. Do not trust identity fields sent by a browser: your BFF sets user and account from its own session.

## Making requests (KB)

Base URL, endpoints, methods, authentication, parameters, JSON bodies, rate limits and error codes must be read from the API reference (apidocs.znode.com). Status handling in the KB: 200 OK (GET, PUT), 201 Created (POST), 204 No Content (DELETE); 400 invalid input; 401 and 403 authentication or permission; 404 not found; 405 wrong method; 429 rate limited; 5xx server (log, show a generic message). Also check the response body: "Znode often provides specific validation details" and a 200 can still carry a logical error. Errors use a common error detail model.

Response casing: the Webstore converts PascalCase API responses to camelCase and requests back to PascalCase (`convertCamelCase`, `convertPascalCase`); expect to do the same.

## Best practices (KB)

Centralise API logic in services; handle errors gracefully; keep credentials in environment variables; validate responses; follow REST conventions; implement rate-limit handling and caching; kebab-case routes with camelCase parameters; use built-in paging and validation; use gateway-based token authentication; use Stoplight and Swagger documentation.
