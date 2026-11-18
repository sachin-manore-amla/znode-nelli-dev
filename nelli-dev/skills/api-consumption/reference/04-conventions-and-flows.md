# Conventions, errors and call order
Answers: paging, filters, sort, error handling, caching, size cautions and the order of calls for common flows.
Confidence: API reference guide pages read in a browser (85), KB (70).

## Paging, filter, sort
| Item | Syntax |
|---|---|
| Page | `pageIndex` (1-based, default 1), `pageSize` (default 10) |
| Filter | `filter={Field}~{Operator}~{Value}`; repeat `filter=` for AND; OR "when supported" |
| Sort | `sort={field}~{asc|desc}` (JSON form `{"field","direction":"ASC|DESC"}`) |
Operators: `cn` contains, `ncn` not contains, `eq`, `ne`, `ew` ends with, `sw` starts with, `lk` like, `nlk`, `gt`, `ge`, `lt`, `le`, `is`, `in`, `not in`, `bw` between. Some operators fail on some fields (for example `eq` or `in` on text for certain lists): test with real data. Field names are the response field names of the list. Routes are kebab-case with camelCase parameters in v2.
Cautions: avoid very large `pageSize`; always sort for stable paging; filter on indexed fields; expand parameters add cost.

## Success codes
200 GET and PUT, 201 POST create, 202 accepted for asynchronous work (imports, exports), 204 no content (also returned by some lists when nothing matches).

## Errors
| Status | Meaning |
|---|---|
| 400 | Invalid input or missing header. Body message names the field |
| 401 | Missing, invalid or expired credentials |
| 403 | Authenticated, not allowed (role) |
| 404 | Not found (also used for invalid template or locale in imports) |
| 409 | Conflict: duplicate, or a publish or export in progress |
| 429 | Rate limit: the reference lists it; platform limits are not documented, back off |
| 500, 502, 503, 504 | Server or upstream; retry with backoff for reads |
Body shape actually returned: JSON object with `ErrorMessage`, `ErrorCode`, and often `HasError`, `IsSuccess` and `StatusCode` (property casing follows the service, PascalCase in v1). The API reference guides show `success`, `errorCode`, `message`, `details`: do not code against that shape alone. Parse by status code first, then read `ErrorMessage` if present.
A 200 with an error in the body occurs on some legacy routes (for example the bulk product update route): check the body and logs.

## Caching and cost
Published reads are cacheable on the client by URL plus context headers; invalidate on publish or on events (`sdk-events-and-webhooks`). Never cache user-scoped responses across users. The API caches internally and invalidates through events: if the broker is down you can see stale data.

## Size and rate cautions
Import payloads: compress and base64 the CSV; keep files under 50 MB. API payload guidance 10 MB, real-time exchange payload 1 MB. No documented request-per-second limit: use concurrency of a few calls and backoff.

## Order of calls
| Flow | Sequence |
|---|---|
| Server sync | `POST /Token` then list calls with paging; refresh at 25 minutes |
| Storefront browse (headless) | Token (client) > store settings > published categories > published products by category or search (headers store, locale, publish state `Production`, catalog) |
| Shopper login | `POST /UserToken` with `StoreCode` > use the Bearer token for every call > refresh with `/RefreshJWTToken` |
| Cart and checkout | Commerce API: create or get cart (`classType` Carts) > add lines > calculate (Calculate operations return tax, shipping, promotions) > set addresses and shipping > payment > create order (`classType` Orders). Send `Znode-PortalCode`, locale and user headers on each call |
| Start a bulk import | `POST /v2.1/imports/process-log/{type}/{template}` > poll `GET /v2/imports/process-log-details/{id}` |
| Webhook registration | `POST /v2/events` > verify in Admin |
Exact operation names and bodies: look up each in the API reference (`api-catalog`); mark any operation you could not find as not verified.
