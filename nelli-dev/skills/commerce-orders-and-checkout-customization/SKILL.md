---
name: commerce-orders-and-checkout-customization
description: What can be configured or customized in the Znode cart, checkout and order lifecycle - storefront checkout composition and the payment and shipping method visibility intersection rules, order statuses and edit rules, Commerce Portal order statuses, flags, types, teams and classes, approval routing and pending orders, budgets, custom data on orders (Additional Information fields, external id, user-defined field entities), email and SMS notifications on order events, order history and notes, returns configuration pointers, and every extension point (method overrides, events, Custom API, promotion extensions, Webstore source). Load it for requirements such as "add a field to the order", "block checkout in a condition", "route orders for approval", "change order status flow", or "send an email when an order changes".
user-invocable: false
---

# Orders and checkout customization

## Vocabulary
| Term | Meaning |
|---|---|
| Order, Quote, Pending order | Different records: an order is placed; a quote is a priced request; a pending order waits for approval or a billing account number |
| Order status | Admin order state (Submitted, Shipped...). In Commerce Portal statuses are configurable data |
| Profile | Controls payment and shipping methods, catalog, price list for a shopper segment |
| Account | Company: decides catalog, prices, addresses, approvals |

## Ten facts that matter
1. Storefront checkout is a fixed Next.js page; its sections are shipping address, billing address, shipping method, shipping constraint, payment, then cart review, promo section (store setting), CSR discount (impersonation), and **Additional Information** (two fixed fields). (Webstore source 90)
2. Additional Information has exactly **Job/Project Name** (100 characters) and **Additional Information** (500 characters). There is no configurable custom-field list on the checkout page. (source 90; the KB suggests more examples, source wins)
3. Payment and shipping methods shown = store methods intersected with the shopper's profile methods; no overlap shows the store methods; profile methods without store methods show nothing. (KB 80)
4. Admin order status can be changed to any status, except while an incomplete return exists; Canceled triggers refund processing. (KB 80)
5. Approval routing: threshold on **order subtotal**, type Store/Payment/User, level Single/Multi, storefront orders only, Save **and Publish** the store. (KB 80)
6. Budget limits (per order, annual) block placement; they do not route to approval. (KB 80)
7. Commerce Portal has configurable order statuses (with flags such as allow editing, send email, require completeness), order flags, order types, quick status buttons, class change buttons, owners and followers. (module guide 85)
8. Order emails depend on templates **enabled per store**; a status in Commerce Portal can send an email when "send email" is on. (KB 80)
9. No method override or event can stop an order being placed. Hooks exist for totals, tax identity and receipt text only (`sdk-method-overrides`).
10. The shopper's checkout call path is a Webstore BFF route (`/api/place-order`) that validates the checkout session and reCAPTCHA then calls the Commerce API; adding a rule there is a **source customization**. (source 90)

## Reference files
- `reference/checkout-flow-and-visibility.md`
- `reference/order-lifecycle-and-commerce-portal.md`
- `reference/approvals-and-budgets.md`
- `reference/order-data-and-custom-fields.md`
- `reference/notifications-history-returns.md`
- `reference/extension-points.md`

## Nelli-Dev decision guide
| Requirement | Verdict | Route |
|---|---|---|
| Add a text field to checkout (for example gift message) | Customizable (source) | Store it in the Additional Information text or change the Webstore checkout component and BFF route; label as source customization. Persisting a new field on the order record is not supported without a platform change; keep it in the 500-character text or a Custom API record keyed by order number |
| Add a field to the order | Needs checking | Reuse Job/Project Name, Additional Information, External ID; a user-defined field entity for orders exists in the platform but Admin/API exposure was not confirmed (`GAPS`); otherwise a custom table keyed by order number |
| Block checkout when a condition fails (credit hold, restricted region) | Customizable (source) | Condition check in the Webstore BFF place-order route and checkout page against a Custom API; approval routing is the supported alternative ("route to approver") |
| Require approval above an amount | Supported | Approval Management (subtotal threshold) |
| Different payment methods per customer group | Supported | Profile payment methods |
| Hide a shipping method for a country | Supported | Destination Country restriction on the method |
| Change a total after calculation | Customizable | `CommerceCalculateCompleted` |
| Add an order status or change the flow (Commerce Portal) | Supported | System Settings > Commerce Settings > Order Statuses, buttons |
| Change the statuses of the Admin OMS order list | Needs platform change | Fixed list in OMS orders |
| Email on status change | Supported / Customizable | Template per store; Commerce Portal status "send email"; custom email by event + your sender |
| Push orders to ERP | Customizable | Order Created event, or ERP connector (`sdk-custom-api`) |
| Rename or reorder checkout sections | Customizable (source) | Webstore checkout component |
| Auto-assign orders to a team (Commerce Portal) | Supported | Order types with default user groups, owners, followers |
| Custom order number format | Supported | Order Classes number format (Commerce Portal) |
| Guest checkout on/off | Supported | Store setting Guest Checkout |

Related: `commerce-promotions-and-pricing`, `sdk-provider-plugins`, `sdk-method-overrides`, `commerce-returns`, `commerce-b2b-accounts`, `config-notifications`, `commerce-inventory`, `sdk-events-and-webhooks`.
