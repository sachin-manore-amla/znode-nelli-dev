# API authentication
Answers: how an application or a user obtains a token, token lifetimes, Basic versus JWT, and the messages.
Tags: [S] gateway source, [KB] KB read in full, [I] inference. Complements `api-auth-and-headers`.

## Gateway token operations
| Route | Body | Result |
|---|---|---|
| `POST /Token` | `ClientName`, `ClientKey` | `Token`, `RefreshToken` for the application |
| `POST /UserToken` | `ClientName`, `ClientKey`, `StoreCode`, `UserName`, `UserPassword` | token for a user |
| `POST /RefreshJWTToken` | `RefreshToken` | new tokens |
| `POST /RevokeToken` | `AccessToken`, `RevokeReason` | revokes |
All are anonymous routes. Messages: `ClientName and ClientKey are required fields.`, `ClientName, ClientKey, UserName and UserPassword are required fields.`, `RefreshToken is required field.`, `AccessToken is required field.`, `Unauthorized! Please check the Authorization Header.` [S]
Client name and key are the domain name and API key of a store URL, given by Znode for the environment. Never store them in source (`quality-security-checks`).

## Lifetimes
Access token 30 minutes, refresh token 30 days by default (`JWTExpirySpan`, `JWTRefreshExpirySpan`; deployment setting). [S][KB]

## KB versus product
KB "Headless API Consumption" says `POST /token` with form-encoded content and does not list body fields; the product reads a JSON body with the fields above. Product wins. The KB shows `Authorization: Bearer <token>` on every call and a response with `token`, `refreshToken`, `hasError`. [KB][S]

## Basic versus JWT
- Customer-facing and Commerce API calls: JWT bearer through the gateway.
- Server-to-server between Znode services and the Custom API SDK admin pages: Basic header whose decoded value is `<domain name>|<domain key>` (`config-admin-customization`). [S]
- Other v2 operations: `POST /v2/auth/portals-tokens`, `PUT /v2/auth/update-token`, `GET /v2/auth/validate-tokens/{refreshToken}`, `POST /v2/auth/revoke-tokens`, `POST /v2/auth/revoke-user-token`, `POST /v2/users/login-token/{userName}`, `POST /v2/users/validate-login-token` are internal plumbing; do not build on them. [S, I]
Commerce Portal gets a gateway token with the client name and key before sign-in and refreshes it on 401. [M]
