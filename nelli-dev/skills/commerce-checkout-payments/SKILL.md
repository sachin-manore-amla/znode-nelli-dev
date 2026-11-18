---
name: commerce-checkout-payments
description: The Znode storefront checkout flow step by step, guest versus authenticated checkout, manual order approval, payment method types and the profile-store intersection rule that decides which payment methods appear. Use when debugging checkout, adding a payment method, or when a payment option is missing at checkout.
user-invocable: false
---

# Znode Checkout & Payments

## Checkout steps

Single-page progressive flow on the storefront:

| Step | What happens |
|---|---|
| Shipping Address | Enter or select a saved address. Optional USPS validation via *Enable Address Validation* |
| Billing Address | Separate from shipping |
| Shipping Method | Methods configured for the store (via plugin) |
| Voucher | Apply a voucher as a form of payment |
| Payment Type | Select a method and enter details |
| Promotions | Add or remove promotion/coupon codes |
| Additional Order Information | Custom order-level fields (e.g. PO number) |
| Order Review & Summary | Review totals |
| Place Order | Submit; lands on the Order Receipt page |

**Order Receipt** offers: view/print receipt, open in Order History, Submit Feedback, Continue Shopping.

## Backing API

Commerce Portal API owns checkout:

- `GET /checkout/validate-checkout/{classNumber}` — snapshot and validate the checkout state
- `POST /{classType}/place-order/{classNumber}` — finalise placement
- `GET /carts/calculate-cart/{classNumber}`, `POST /Calculate/{orderId}` — totals
- `POST /calculate/apply-discount/{classNumber}` / `DELETE /calculate/remove-discount/{classNumber}`

Place Order orchestrates Tax Manager → Shipping Manager → Payment Manager, then writes the order. A declined payment returns 422 and no order is written.

## Guest vs authenticated

| Aspect | Guest | Authenticated |
|---|---|---|
| Account required | No | Yes |
| Data captured | Email, name, phone, addresses | Full profile, saved addresses, order history |
| Admin visibility | `Customers > Guest Users` | `Customers > Users` |
| Conversion | Admin can convert guest → registered by assigning a username | n/a |
| Profile-driven customisation | None | Profiles control payment methods, shipping methods, price lists and catalogs |

## Manual order approval ("Validate Checkout")

`Store Settings > General > Requires Manual Approval Of Every Order` puts **every** submitted order into **Pending** until an admin approves it. This is distinct from B2B Approval Routing — see `commerce-b2b-accounts`.

## Payment method types

Payment methods are installed as **plugins**, configured with Configuration Sets, then associated to stores.

| Plugin | Type |
|---|---|
| Charge on Delivery (COD) | Native — collected on delivery |
| Purchase Order (PO) | Native — buyer supplies a PO number |
| Invoice Me | Native — buyer invoiced after the order |
| Spreedly | External gateway (credit card, ACH, …) |
| Braintree | External gateway |
| Custom | Implement `IPaymentPlugin` |

Reference table `ZnodePaymentType` covers CreditCard, PurchaseOrder, ACH, GiftCard, WireTransfer, PayPal, NetTerms, ApplePay.

### Which methods show at checkout — KB-confirmed

Payment methods are created in **Dev Center > Payment Methods**, then associated per store at `Stores and Reps > Stores > Manage > **Webstore Payment Methods**`. Only associated methods can appear.

The system **intersects** the buyer's profile method(s) with the store's:

| Store methods | Profile methods | Shown |
|---|---|---|
| A, B, C, D | none | A, B, C, D |
| A, B, C, D | C, D | C, D |
| A, B, C, D | E, F (no overlap) | A, B, C, D — store fallback |
| A, B, C, D | X: A,P,Q + Y: C,D,G,H | A, C, D — union of intersections |
| **none** | A, B | **none** |

The last row is the trap: **profile methods alone show nothing** — the store must have methods configured. The same intersection rule governs shipping methods.

Pre-defined payment **types**: Credit Card · Purchase Order · PayPal · Invoice Me · Amazon Pay · COD. Offline methods are managed separately (`Managing Store Offline Payment Methods`).

## Payment Manager operations

`POST /v1/plugin/{pluginIdentifier}/` + `authorize` · `capture` · `purchase` · `refund` · `void` · `verify` · `store` · `bank-account`. Saved cards and tokens under `/credit-card-details/{customerGuid}` and `/token`. Transaction lookups under `/transaction-status-details/{transactionId}` and `/transactions/{transactionGuid}/validate`.

Authorize-not-capture flows are completed from the Admin order screen with the **Capture Payment** button.

## KB source

- [Managing Payment Methods](https://support.znode.com/support/solutions/folders/43000598834)
- [Znode Starter Theme - Commerce Pages](https://support.znode.com/support/solutions/folders/43000598161)

## Related
`commerce-orders` · `sdk-provider-plugins` · `commerce-b2b-accounts`
