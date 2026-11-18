---
name: api-auth-and-headers
description: Znode authentication modes (inter-service Basic auth vs customer-facing JWT), the gateway JWT validation flow, and every Znode-* context header with what it resolves to. Use when a request returns 401/403, when calling one Znode service from another, or when an endpoint needs portal, locale or catalog scoping.
user-invocable: false
---

# Znode Authentication & Context Headers

## Authentication modes

| Layer | Mechanism | Notes |
|---|---|---|
| Inter-service (API → API) | **Basic auth** — `DomainName:DomainKey` Base64-encoded from `appsettings.json` | Recommended for all server-to-server calls |
| Customer-facing | **JWT Bearer token** | Only Webstore and custom-API projects are externally exposed |
| Commerce Portal | **JWT Bearer token** | the Commerce API is customer/sales-rep facing |

**Basic auth flow:** `DomainName` + `DomainKey` are combined and Base64-encoded into `Authorization: Basic {token}`. `HelperUtilityService.CheckAuthHeader(domainName, domainKey)` validates inbound requests.

**JWT flow:** issued at login, validated by ASP.NET Core middleware before any controller action. `Znode-UserId` and `Znode-AccountId` are populated from token claims by middleware and flow to all downstream calls.

## Gateway validation

```
Client -> Gateway (Ocelot/YARP) -> Znode.Libraries.Auth.ValidateToken(token)
  valid            -> claims (userId, portalCode, accountId, roles) injected as headers -> downstream API
  expired/invalid   -> 401 (ZnodeAuthenticationException)
  valid, no rights  -> 403 (ZnodeAuthorizationException)
```

## Context headers

| Header | Resolves to | Resolver |
|---|---|---|
| `Znode-PortalCode` / `Znode-StoreCode` | `PortalId` (int) | `IHelperUtilityService.GetPortalIdByPortalCode()` |
| `Znode-LocaleCode` | `LocaleId` | locale scoping for content |
| `Znode-CatalogCode` | `CatalogId` | product catalog scoping |
| `Znode-PublishState` | `Preview` / `Production` | selects the Elasticsearch index |
| `Znode-UserId` | current user | injected from JWT claims |
| `Znode-AccountId` | B2B account | injected from JWT claims |
| `Znode-DomainName` | store domain | V1 only |
| `Device-Id`, `User-Agent` | device/session context | activity log, MFA trusted devices |

Every endpoint returning portal-specific data requires the portal header. A missing or wrong `Znode-PortalCode` produces **empty responses, not errors** — a common and hard-to-spot bug.

> `Znode-PublishState` Preview is **deprecated in 10x** (legacy from 9x). Do not build new features that depend on it.


## Access control

- `[WebstoreAttribute]` restricts an endpoint to webstore-scoped calls — apply to anything that must not be callable from Admin or inter-service contexts.
- Two-factor auth for the Admin Console is configured under `Dev Center > Global Settings > Two-Factor Authentication`, with a per-store override in Additional Store Attributes.
- Secrets come from Azure Key Vault / `IConfiguration` — never hardcoded.

## KB source

- [API Development](https://support.znode.com/support/solutions/folders/43000594918)

> Code/spec-derived.

## Related
`config-stores-tenancy` · `config-global-settings`
