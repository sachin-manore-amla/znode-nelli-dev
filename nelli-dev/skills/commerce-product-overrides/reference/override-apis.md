# Override APIs

What this answers: the operations under `v2/productoverrides`, their headers, request and response shapes and limits, and which API to use for what.
All are in the Core API v2 reference (the `Customer` family of the exported spec).

## Authentication and headers

Standard API authentication through the gateway (see `api-auth-and-headers`). Search routes also need context headers. No role check beyond authentication.

| Header | Routes | Rule |
|---|---|---|
| `Znode-PortalCode` | all GET routes | required; store code |
| `Znode-LocaleCode` | all GET routes | required; locale code |
| `Znode-AccountCode` | all GET routes | optional; account code |

## Operations

| Method and route | Purpose | Key inputs | Notes |
|---|---|---|---|
| `POST /v2/productoverrides` | Create one record | body below | 201 with `ProductOverrideResponseModel`; 400 on empty body or over-length field |
| `PUT /v2/productoverrides` | Update records matching a filter | body (fields to set) plus filter in the query string, for example `?SKU=eq=PRODUCT-1&StoreCode=eq=DemoStore` | 404 `No record found.` when nothing matches |
| `DELETE /v2/productoverrides` | Delete records matching a filter | filter in the query string | 200 `BooleanResponse`; 404 when nothing matches. Hard delete. |
| `GET /v2/productoverrides/{sku}` | Override details for one SKU | query `catalogCode` (required) | returns `ProductOverrideDetails[]` with `SKU`, `AlternateSku`, `AlternateProductName`, `AlternateShortDescription`, `AlternateLongDescription`; 400 if either flag is off; 404 `Invalid SKU.` if the SKU is not in the published catalog |
| `GET /v2/productoverrides/multiple-products/{skus}` | Same for several SKUs | comma-separated SKUs, `catalogCode` | at most 32 SKUs per request; route text up to 9,600 characters |
| `GET /v2/productoverrides/full-text-search/{keyword}` | Full-text search with overrides applied | `catalogCode`, `CategoryCode`, `IsFacetList`, `RefineBy`, `UseSuggestion`, `expand`, `filter`, `sort`, `pageIndex` (default 1), `pageSize` (default 10) | |
| `GET /v2/productoverrides/hydrated-search` | Typeahead search | `keyword` and the same context | 400 `This setting is disable for the portal id:{portalId}` when the store's typeahead recommendations setting is off |
| `GET /v2/productoverrides/hydrated-search-with-facets` | Typeahead search with facets | keyword 3 to 100 characters | |
| `GET /v2/productoverrides/suggestions/{keyword}` | Keyword suggestions | `catalogCode` (letters, digits, `_`, `-`, up to 100) | |
| `GET /v2/productoverrides/hydrated-suggestions` | Popular searches, products, categories | `catalogCode`, `profileId` | |
| `GET /v2/productoverrides/category-facets` | Category facets for a keyword | context | |

Search routes return the normal search data with the four alternate values mapped in. When overrides are disabled for the store they return standard results and no error (except the two single/multi-SKU routes above).

## Create and update body

All fields are optional text, but at least one must have a value.

```json
{
  "LocaleCode": "en-US",
  "StoreCode": "DemoStore",
  "AccountCode": "ACC001",
  "SKU": "PRODUCT-1",
  "AlternateSku": "ALT-1",
  "AlternateProductName": "Override Product Name",
  "AlternateShortDescription": "Override short description",
  "AlternateLongDescription": "Override long description"
}
```

Create response record: `ProductOverrideId` plus the same eight fields. The API does not check that the store, account, SKU or locale exist.

## Limits and gaps in the API

- Sorting and pagination of the single and multiple-SKU routes are not supported: responses can be large and unsorted; sort and page on the client. (KB)
- Maximum 32 SKUs per multiple-SKU call. (product source, 90)
- Filters on update and delete use field names in the query string; use the exact API field names shown in the spec, nothing else.
- Variants with no category are not returned by the SKU routes. (KB)
- The search routes are marked for storefront use with server caching on, so a change may not show instantly after a publish. (product source, 85; cache duration not verified)

## Which API for what

| Need | Use |
|---|---|
| Create, change or delete records from code | `POST`, `PUT`, `DELETE /v2/productoverrides` |
| Read all records, bulk load, export | Custom Table data API with table key `ProductInformationOverrides` (see `sdk-custom-tables`) |
| Show overrides to shoppers | `GET /v2/productoverrides/...` read routes, called by the storefront |
| Product text without overrides | `GET /v2/published-products/{publishProductId}` |

Differences: the dedicated create/update/delete routes write the record directly; the Custom Table data path writes through the generic custom table service and may also mark the product's publish state. Both end up in the same table, so a record created either way needs the same full catalog publish. (module guide, from source, 85)

Release notes: 10.8.0.0 improved the suggestions and full-text routes (account/store scoping, accurate counts) and made duplicate records return a clearer conflict error.
