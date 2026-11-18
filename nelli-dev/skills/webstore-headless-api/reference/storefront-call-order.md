# Call order for common storefront flows

What this answers: the order of API calls for store bootstrap, category and product lists, search, product detail with variants, cart, checkout and order placement, based on what the shipped Webstore does, with a mark showing whether each operation is in the public spec.
Confidence: routes read from the Webstore clients (90); "spec" column checked against the public Core v2 (Customer) and Commerce spec files on 2026-10-15 (90 for presence). Request and response fields: read each operation with `nd_query_spec.py op <family> "<route>"`; they are not reproduced here.

Every call carries the store context headers (`api-families-auth-and-errors.md`). Commerce routes are shown relative to `commerceapi/v1`.

## 1. Store bootstrap

| Step | Call | Spec |
|---|---|---|
| Store settings, theme, locale, flags | `GET v2/portals/{storeCode}` | yes |
| Application settings of a type | `GET v2.1/portals/{storeCode}/application/{type}` | v2 route `v2/portals/{storeCode}/application/{type}` yes |
| Menu categories | `GET v2/published-categories` | yes |
| Category by code or id | `GET v2/published-categories/{categoryCode}`, `GET v2/published-categories/id/{categoryId}` | list yes; the two by-key routes are used by the Webstore, not confirmed in the spec |
| Robots | `GET v2/portals/{storeCode}/robots-txt` | yes |

Cache these per store and locale; refresh on store or catalog publish.

## 2. Category list, search

| Step | Call | Spec |
|---|---|---|
| Products of a category | `GET v2/published-products/{catalogCode}/categorycodes/{categoryCodes}` (spec); the Webstore calls `GET v2/published-products` with filters | spec route yes; Webstore route not found in the public spec |
| Full-text search with facets | `GET v2/search/{searchKeyword}/full-text-search` | yes |
| Typeahead | `GET v2/search/{searchKeyword}/hydrated-typeahead-full-text-search` | yes |
| Live prices for visible SKUs | `GET v2/search/{skus}/products-pricing` (the Webstore refreshes prices this way when real-time pricing is on) | yes |

## 3. Product detail

| Step | Call | Spec |
|---|---|---|
| Product | `GET v2/published-products/{publishProductId}` | yes |
| Product by SKU | `GET v2/published-products/sku/{productSKU}` | Webstore route; not found in the public spec |
| Attributes | `GET v2/published-products/{sku}/attribute` | yes |
| Variants of a configurable product | `GET v2/publish-products/{publishProductId}/configurable-variants`, `GET v2.1/published-products/{parentProductSKU}/configurable-products` (also v2.2) | yes |
| Inventory | `GET v2.2/published-products/{publishedProductIds}/inventory` | yes |
| Price | through the search pricing route above or the cart price route `GET carts/price/{sku}/{quantity}` | pricing yes |
| Validate before add | `POST v2/published-products/validate-product` | yes |
| Compare | `GET v2/published-products/{productSKUs}/compare-products` | yes |

The Webstore re-reads the product when the shopper picks a variant (new parent id, codes and values in the URL). A headless front end calls the variants route instead of re-rendering a page.

## 4. Account

| Step | Call | Spec |
|---|---|---|
| Sign up | `POST v2/users` | yes |
| Log in | `POST v2.1/users/login` | yes |
| Addresses | `POST v2/addresses`, `GET/PUT/DELETE v2/addresses/{addressId}` | create yes |
| Forgot, change password | `POST v2/users/forgot-password`, `POST v2/users/change-password` | Webstore routes |

## 5. Cart

| Step | Call | Spec |
|---|---|---|
| Find or start the active cart | `GET {classType}/active-class-number` with class type `carts` | yes |
| Add item | `POST carts/add-to-cart` (a v1.1 route also exists) | yes |
| List items | `GET {classType}/item-list/{classNumber}` | yes |
| Change quantity, remove | `PUT {classType}/{classNumber}/quantity/{itemId}`, `DELETE {classType}/{classNumber}/delete-item/{itemId}`, `DELETE {classType}/remove-all/{classNumber}` | Webstore routes |
| Totals | `GET carts/calculate-cart/{classNumber}` | yes |
| Coupon or voucher | `POST calculate/apply-discount/{classNumber}`, `DELETE calculate/remove-discount/{classNumber}` | apply yes |
| Estimate shipping | `GET {classType}/shipping-estimates/{cartNumber}/{postalCode}` | yes |
| Guest to user | `POST carts/merge-cart` | yes |
| Validate | `GET carts/validate-cart/{cartNumber}` | Webstore route |

## 6. Checkout and order

| Step | Call | Spec |
|---|---|---|
| Convert cart to checkout | `{classType}/convert/{classNumber}/{targetClassType}` | Webstore route |
| Addresses and shipping choice | `PUT shippings/order-shipment`; remove with `DELETE shippings/remove-shipping/{classNumber}` | order-shipment yes |
| Payment | `POST payments` / `PUT payments`; payment manager and plugin calls for tokenization (`commerce-checkout-payments`) | yes |
| Validate checkout | `GET checkout/validate-checkout/{classNumber}` | yes |
| Place order | `POST {classType}/place-order/{classNumber}` with class type `checkout` (or `quotes`) | yes |
| Receipt | `GET {classType}/receipt-details/{classNumber}` | Webstore route |
| Track order (guest) | `GET orders/order-tracking-details/{classNumber}/{emailAddress}` | yes |

Business rules the Webstore enforces around this flow (copy them): a purchase order payment needs a purchase order number; when the order total is above zero a payment configuration must be present; if placing the order fails after an online payment, the payment is voided or refunded; reCAPTCHA is validated on the server for guest and logged-in checkout when the store flags are on.

## Notes

- Some Webstore routes are not in the public spec files. Build only on operations you confirm in the API reference; ask Znode about the others (GAPS).
- A custom front end must replicate the quirks the Webstore handles: one active cart per user and store, checkout reference per browser tab, profile-based shipping and payment methods, login-to-see-price stores (prices zero until login), B Store rules.
- Call count per page is a performance budget (`quality-performance-checks`); batch where the API allows it.
