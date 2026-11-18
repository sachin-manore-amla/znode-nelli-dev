# Customization decisions for overrides

What this answers: given a requirement, which verdict to give and which mechanism to use (override, Custom Table, custom endpoint, Webstore change).
Use with the decision guide in SKILL.md.

## Choosing the mechanism

| Requirement shape | Mechanism | Verdict |
|---|---|---|
| Alternate product name, short or long description or SKU per store, locale or account | Product Information Overrides | Supported |
| That text must show on PDP, search, listing, cart | Overrides plus a Webstore change that reads `v2/productoverrides` | Customizable (source customization) |
| Some other per-store or per-account field on the product (tagline, spec sheet link) | Custom Table keyed by SKU + store (+ account) and a custom endpoint; Webstore reads the endpoint | Customizable |
| A value per customer per product | Custom Table keyed by customer and SKU; custom endpoint with ownership checks (`quality-security-checks`) | Customizable |
| Per-store product images, attributes, categories | Separate catalogs per store, or attributes in PIM | Supported (different feature) |
| Per-account price | Price lists (`commerce-promotions-and-pricing`) | Supported |
| New field on the override record | Not possible without changing a system table | Needs platform change |
| Overrides appear without a catalog publish | Not available | Needs platform change |

## How a customization consumes overrides

1. Confirm both flags are on for the store and that a full catalog publish has run since the last change (reference/publish-indexing-and-fallback.md).
2. In the Webstore source, call the override operation that matches the page: SKU lookups for PDP and cart lines (up to 32 SKUs per call), full-text search for results, suggestions and hydrated search for the header search box. Send `Znode-PortalCode`, `Znode-LocaleCode` and, for logged-in B2B users, `Znode-AccountCode`.
3. Do not call per product in a loop. Batch SKUs, cache by store, locale and account, and invalidate when a publish completes.
4. Merge: use the returned alternate value when it is not empty, else the product value.
5. Keep the order, quote and invoice on the original SKU and name; overrides are not stored there.
6. Write records with `POST/PUT/DELETE /v2/productoverrides` or the Custom Table data API from an integration; protect the integration credentials and validate SKU, store, locale and uniqueness yourself because the API does not.
7. Raise events or webhooks? Override changes raise no documented event (not verified; see gaps), so schedule the catalog publish yourself.

## When a Custom Table is the better answer

- The data is not product name, description or SKU.
- You need a value per user, order, cart line or per product-and-user.
- You need a unique key or required fields enforced (custom tables let you define unique fields and lengths; the override table is fixed).
- You expect more than about 100,000 records.

## When a custom endpoint is the better answer

- You need validation before write (existing SKU, active store, no duplicate).
- You need the account-to-store fallback that the product may not perform.
- You need to merge overrides with other data in one response for the storefront and keep the call count low.

Do not recommend direct database access for any of these.
