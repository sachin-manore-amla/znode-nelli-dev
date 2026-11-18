# B Store REST v2 API and GraphQL
Answers: which operations read and write B Stores, and what the GraphQL surface offers and requires.
Tags: [S] spec and source, [M] module guide, [I] inference.

## REST (B Store spec, v2)
| Method and route | Purpose |
|---|---|
| `GET/POST /v2/b-stores`, `GET/PUT /v2/b-stores/{portalId}` | list, create, read, update |
| `POST /v2/b-stores/delete`, `POST .../{portalId}/copy`, `POST .../{portalId}/publish` | delete, copy, publish |
| `GET/POST /v2/b-stores/{portalId}/contact-details` | contact |
| `GET/POST /v2/b-stores/{portalId}/theme` | design |
| `GET /v2/b-stores/{storeCode}/users/{userId}/access-url` | link into the B Store app |
| `POST /v2/b-stores/validate-token` | validate access token |
| `GET/PUT /v2/b-stores/parent-portal/{parentPortalId}/catalogs` and `/catalog/{catalogId}` | available catalogs |
| `GET/PUT .../parent-portal/{parentPortalId}/price-list` and `/price-list/{priceListId}` | price lists |
| `GET .../parent-portal/{parentPortalId}/domain-name` | parent domain |
| `POST .../parent-portal/{parentPortalId}/users/{userId}/registration` | request access |
| `GET .../users/{userId}/stores`, `POST .../users/{userId}/setup` | user's stores, create with design |
| `POST /v2/b-stores/{portalId}/users/{userId}/set-activation` | activate/deactivate |
| `GET/PUT /v2/b-stores/users/{userId}/roles`, `/stores`, `PUT .../access` | owner/manager flags and access |
Auth: gateway JWT (`config-roles-permissions/reference/api-authentication.md`). [S]

## GraphQL
Gateway path `/bstore-graphql/{...}`; endpoints `/bstore-graphql/v1` (unified), `/bstore-graphql/admin/v1`, `/bstore-graphql/storefront/v1`. Admin schema operations need role Admin, B Store Owner or server-to-server access; storefront uses customer tokens. Errors arrive as HTTP 200 with `errors[]` and `extensions.code` (for example `FIELD_ACCESS_DENIED`, `BSTORE_NOT_FOUND`, `BSTORE_VALIDATION`, `BSTORE_UPLOAD_ERROR`). Limits: page size 100, query depth 10; multipart uploads need header `GraphQL-Preflight: 1`. [S][M]
Capabilities (catalogue): B Store list and details, create, copy, update settings, activate, domain suffix and subdomain check; catalogs, price lists, category tree and category products with included flag; design get/update, upload and remove media; customers list/create/update/lock/remove/reset password/bulk import with run logs; token validation; cache flush and diagnostics. Exact field names: read the schema by introspection from your environment (not verified here). [M][I]

## Customizing
You can read and drive B Stores through the REST and GraphQL operations from the Custom API SDK or an integration. You cannot add fields or resolvers to the hosted GraphQL service. Verdict: reading and driving is Supported/Customizable; schema extension is a platform change. [I]
