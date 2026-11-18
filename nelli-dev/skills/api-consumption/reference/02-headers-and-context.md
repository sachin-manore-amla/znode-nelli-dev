# Context headers and what happens when they are missing
Answers: which headers scope a request, their meaning and behaviour when absent.
Confidence: API reference descriptions (85), product source (90). Behaviour differs per operation: the operation page is the authority.

| Header | Meaning | Missing or wrong |
|---|---|---|
| `Znode-PortalCode` (alias `Znode-StoreCode` on some routes) | Store (portal) code | Where an operation resolves the store: 400 `Please check the PortalCode.`; unknown code: 400 `Please check storeCode`. Some validators use the message `Znode-PortalCode header is required.` |
| `Znode-LocaleCode` | Locale such as `en-US` | Operations that resolve it explicitly: 400 on invalid code (`Please check localeCode.`); otherwise the **default locale** is used. Invalid codes are rejected early since 10.14.0.0 |
| `Znode-PublishState` | `Production` (published, live) or `Preview` (draft, admin preview) | Falls back to the state mapped from `Znode-DomainName`, then to the system default publish state. Wrong value is ignored and the default is used. `Preview` is for admin preview, not for new storefront features |
| `Znode-UserId` | Acting user; `0` for guest | Required by user-scoped operations (the import start call returns 400 when it is not greater than 0). JWT fills it |
| `Znode-AccountId` / `Znode-AccountCode` | B2B account context for pricing, catalogs, payment methods | Store-level data is returned |
| `Znode-CatalogCode` | Catalog | Needed by catalog-scoped published reads |
| `Znode-ProfileId` | Profile controlling price tiers, catalog visibility | Needed when the catalog is not tied to a store |
| `Znode-DomainName` | Store domain without protocol | Used by older v1 and webstore calls to find the store |
| `Device-Id`, `User-Agent` | Device context for activity and trusted devices | Optional |
Gateway-added headers for user tokens: `Znode-JwtEnabledRequest`, `Znode-JWT-PortalCode`, `Znode-JWT-UserRoleName`, `Znode-JWT-UserId`. Do not send these; the gateway sets them.
Commerce API pages describe `PortalCode`, `LocaleCode`, `PublishedState`, `UserId` and allow `*` as a wildcard (all stores, locales or both publish states) on list reads. `*` is not valid on writes.

## Typical symptoms
| Symptom | Likely cause |
|---|---|
| 200 with empty list | Wrong store, locale or publish state; data not published; catalog not assigned to the store |
| 400 `Please check the PortalCode.` | Header missing on an operation that requires it |
| Prices differ from the storefront | Missing `Znode-UserId`, `Znode-AccountId` or profile context |
| Draft values returned | `Znode-PublishState: Preview` or a Draft API used |
| 401 after minutes | Access token expired (30 minutes) |
Existing guidance in other skills that says a missing portal header always gives an empty response is not true for operations that validate the header: both happen, depending on the operation.
