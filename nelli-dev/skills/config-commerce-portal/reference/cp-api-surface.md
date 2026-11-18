# Commerce Portal API surface and the Custom API route
Answers: which Commerce API operations an integrator may use, how classType works, how to call them from the Custom API SDK, and what it cannot do.
Tags: [S] source/spec, [I] inference.

## Base and auth
Gateway path `/commerceapi/v1` (also `/v1.1`), JWT via the gateway; user context headers as in `api-auth-and-headers`. Family: Commerce API (`api-catalog`). [S]

## classType
Path segment `{classType}`; spec values: `Orders`, `Carts`, `SaveForLaters`, `SavedCarts`, `OrderTemplates`, `Quotes`, `ApprovalRoutings`, `Returns`, `Checkout`. [S]

## Public (non-deprecated, non-Internal) operations
| Method and route | Purpose |
|---|---|
| `GET /{classType}` | paged list |
| `GET /{classType}/bulk-details`, `DELETE /{classType}/bulk` | many |
| `GET/PUT /{classType}/{classNumber}` | details / update all |
| `GET /{classType}/{classNumber}/id`, `/items`, `/count` | id, lines, count |
| `PUT /{classType}/{classNumber}/status` | status by code |
| `PUT /{classType}/{classNumber}/items/status`, `/quantities`, `/attributes`, `/personalization` | line updates |
| `PUT /{classType}/{classNumber}/line-items/{lineItemId}/custom-data`, `PUT .../bulk-line-item-customdata` | line custom data |
| `POST /{classType}/{classNumber}/copy`, `PUT .../convert/{targetClassType}`, `POST /{classType}/{classNumber}/orders` | copy, convert, place order |
| `PUT /{classType}/{classNumber}/finalize-details`, `/finalize-number` | finalize |
| `POST .../emails`, `.../notification-emails` | emails |
| `POST /calculate/{classNumber}/discounts`, `DELETE` same | coupons, vouchers |
| `GET /{classType}/class-status-list` | statuses for a class |
| `GET /approval-routings/{classNumber}/approvers`, `/{classType}/{classNumber}/approver-comments` | approvals |
| `GET /orders/{classNumber}/tracking`, `POST /logs`, `POST /{classType}/empty-class`, `POST /{classType}/add-line-items` | misc |
Operations marked **Internal** (classes, statuses, flags, order types, status buttons, user roles) serve the Admin and Commerce Portal; do not build on them. Routes marked Deprecated have replacements above. [S]

## From the Custom API SDK
The SDK registers the Commerce clients (`ICommerceCollectionsClient`). Sample: `CustomPortalController.GetOrderList` sets explicit headers (`Znode-UserId`, `Znode-PortalCode`, `Znode-LocaleCode`, `Znode-PublishState`) and calls `GetListByClassType("Orders", filters, sorts, 1, 50)`; `CustomCPController.GetCartItemList` calls `GetItemListByClassType("Carts", cartNumber)`. [S]

## Limits
- No documented way to add fields or tabs to Commerce Portal screens, or hooks on status change other than events (`sdk-events-and-webhooks`) and method overrides (`sdk-method-overrides`). [S, I]
- Line custom data and attribute updates store extra values per line; whether Commerce Portal displays them is not verified. [I]
- Admin-side config has no public API. Verdict: configure in Admin; Needs platform change for programmatic config.
