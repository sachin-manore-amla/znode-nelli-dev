# Gateway routing and API families
Answers: which path prefix reaches which service, which family to use, and how Custom API routes are added.
Confidence: gateway route configuration (90), API reference overview (85).

## Route prefixes (gateway)
| Prefix | Route key | Service |
|---|---|---|
| `/v2/...`, `/v2.1/...`, `/v2.2/...` | v2 core API | Core API v2 (catalog, accounts, stores, imports, events, users, SEO) |
| `/commerceapi/v1/...`, `/commerceapi/v1.1/...` | commerce portal API | Commerce API (orders, carts, quotes, returns, approval routings, order templates, extension status) |
| `/v1/custom-tables`, `/v1/custom-table-data`, `/v1/custom-table-fields`, `/v1/system-tables` | custom table | Dynamic Data Table API |
| `/v1/...` (payment) | payment manager | Payment API v1 |
| `/shippingmanager/v1`, `/taxmanager/v1` | shipping, tax managers | Used by Znode; not for storefront calls |
| `/graphql`, `/bstore-graphql` | GraphQL services | Storefront and B Store queries |
| `/dataexchanges/...` | Commerce Connector | Data Exchange service |
| `/extensions/...` | commerce portal API | Extension status and logs |
| `/CustomPortal/...` and routes you add | `customapi` | Your Custom API |
| `/api/user-activity` | function | Activity logging |
| `/utility/...`, `/tapi/...` | utility, tenant | Platform |
| anything else | multifront | Core API v1 (legacy, PascalCase routes such as `/Import/GetImportLogs`) |
Order matters: more specific prefixes win. The base URL of the gateway is given to you per environment (the API reference shows a sandbox example).

## Families (API reference)
| Family | Use |
|---|---|
| Core API v2 | General platform operations. Prefer for new work |
| Commerce API | Orders, quotes, carts, saved carts, save for later, order templates, approval routings, returns. One generic model: `classType` selects Orders, Carts, SaveForLaters, SavedCarts, OrderTemplates, Returns, Quotes, Approval routing. Headers `PortalCode`, `LocaleCode`, `PublishedState`, `UserId` |
| Dynamic Data Table API | Custom tables (`sdk-custom-tables`) |
| Payment API v1 | Transactions through payment plugins |
| Reports API | Sales, customer, product reports |
| ERP Touch Point API | Legacy ERP connector operations |
| Core API v1 | Legacy; documented separately |
Versions: v2.1 and v2.2 add operations next to v2 (for example `v2.1/users/{username}` returns all roles; `v2.1/imports/process-log/...` starts an import). Use the highest version that has the operation. A route that exists only in v1 is called out in the specification.
Class types in the Commerce API: pass `classType` as documented per operation; wrong class gives 400 or 404.

## Custom API routes
Your Custom API is deployed behind the same gateway. Add a route to the Custom Ocelot file:
```json
{ "DownstreamPathTemplate": "/MyController/MyAction",
  "UpstreamPathTemplate": "/MyController/MyAction",
  "UpstreamHttpMethod": [ "GET" ],
  "Key": "customapi", "SwaggerKey": "customapi", "Priority": 1 }
```
Rules: `Key` is `customapi` for all your routes (the same key family carries `customtable` copies for custom-table passthrough); give custom routes a priority above the Znode route they shadow; to wrap a Znode API, register the same upstream path as the Znode route with `customapi` so your code runs first. A catch-all `/CustomPortal/{everything}` is in the sample. Set `ZnodeApiDomainName` and related keys so the Custom API can call Znode. Deploy with `znode deploy CustomAPISDK` (`sdk-extension-framework`). Changes to the gateway itself are done by DevOps.
