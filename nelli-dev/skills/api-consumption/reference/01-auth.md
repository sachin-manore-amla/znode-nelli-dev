# Authentication
Answers: the two auth modes, the token endpoints with bodies and messages, lifetimes, and security rules.
Confidence: gateway source (90), API reference pages read in a browser (85), KB headless article (75).

## Modes
| Mode | Header | Use |
|---|---|---|
| Basic | `Authorization: Basic <base64(clientName:clientKey)>` | Server to server. Controlled by a gateway setting (private token authorization) |
| JWT Bearer | `Authorization: Bearer <token>` | Recommended; required for user-scoped calls. Controlled by a gateway setting (JWT authorization) |
Other prefixes are rejected. The gateway validates the client against the configured client list (name and key match) or validates the JWT (signature, issuer, audience, lifetime with one second skew). The API reference states the same two modes for every family.

## Token endpoints (gateway, no Authorization header needed)
| Route | Body (JSON) | Result |
|---|---|---|
| `POST /Token` | `ClientName`, `ClientKey` | `Token`, `RefreshToken`, `HasError` (client-level token, JWT version 1) |
| `POST /UserToken` | `ClientName`, `ClientKey`, `StoreCode`, `UserName`, `UserPassword` | Same, with user claims (version 2): the gateway then sets user, store and role headers for downstream calls |
| `POST /RefreshJWTToken` | `RefreshToken` | New token pair |
| `POST /RevokeToken` | `AccessToken` (and an optional reason) | Revokes |
The KB headless article says to POST form-encoded to `/token`; the gateway reads a **JSON body**. Product wins. Guest users: the user-token route needs a store code for a guest ("StoreCode is required for the guest user.").
Validation messages (400): `ClientName and ClientKey are required fields.`; `ClientName, ClientKey, UserName and UserPassword are required fields.`; `RefreshToken is required field.`; `AccessToken is required field.`
Failure: 401 with `Unauthorized! Please use correct credentials to generate token or check the Authorization Header.` or `Unauthorized! Please check the Authorization Header.`; error code 498 is used for an invalid token.
Request without valid auth: 401 `You are unauthorized to access this resource. Please check your token credentials.` with `ErrorCode` 401.

## Lifetimes
Access token 30 minutes, refresh token 30 days (gateway settings, KB agrees). Refresh before expiry; a 500 on refresh was fixed in 10.14.0.6.

## Which routes skip authentication
Token routes, health, swagger pages, a few static assets. Everything else needs auth.

## Rules
- Keep client name and key on a server. Rotate periodically. Never log tokens.
- One client per integration so one can be revoked alone.
- A JWT carries the user: do not trust a user id supplied by the browser; take it from the token.
- Order Details and similar user data were hardened in 10.14.0.6 (authorization required): always send a token.
- Gateway adds `Znode-UserId` from the JWT; with Basic you must send `Znode-UserId` yourself where an operation requires it (guest `0`).
