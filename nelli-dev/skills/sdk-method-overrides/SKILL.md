---
name: sdk-method-overrides
description: The Znode Method Override feature (Dev Center > Method Override), a synchronous webhook that Znode calls from inside a core method so your service can change a calculation result, change receipt or email content, or replace default behaviour. Covers the real list of overridable hooks (six in 10.x), how to register one in Admin, the exact request and callback envelope (ResponsePayload, ExtendedRequestPayload, WebHookURL, SecretKey, SkipExecution), timeouts and failure behaviour, security, testing and when to choose a method override instead of an event, a promotion extension, a price list or a plugin. Load it for any requirement such as "change a total after calculation", "adjust shipping or tax result", "customise the order receipt or quote email body", or "override a tax customer code".
user-invocable: false
---

# Znode Method Overrides

## What it is
A **method override** is a registered HTTP endpoint that Znode calls **synchronously** at a fixed point inside a core operation. Your endpoint receives the data, may change it, and may tell Znode to skip its default step (`SkipExecution`). It is not a compiled plugin and not a dependency-injection replacement. All logic lives in your own service (normally the Custom API SDK).

Vocabulary people confuse:
| Term | Meaning |
|---|---|
| Method override | Synchronous, in the request path, can change the result. Admin: Dev Center > Method Override |
| Event / webhook (see `sdk-events-and-webhooks`) | After the fact, asynchronous, cannot change the result |
| Promotion extension (see `commerce-promotions-and-pricing`) | A custom discount type, runs inside promotion calculation |
| Plugin (see `sdk-provider-plugins`) | A payment, shipping or tax provider |

## The ten facts that matter
1. Only **six hooks** exist in 10.x (`reference/hook-catalogue.md`). No hook, no override: that is a platform change request. (verified in product source, 95)
2. Registration is one webhook per hook, in **Dev Center > Method Override**; the list of modules and methods in the Add form is the authoritative list for your version. (95)
3. A hook is **inactive until a webhook is registered and active**. With none, Znode runs its default logic. (95)
4. Znode POSTs a JSON envelope; your reply must be the same envelope with `EventPayload` (changed request), `ResponsePayload` (new response) and `SkipExecution`. (95)
5. For the two calculation hooks, **returned totals are applied only when `SkipExecution` is `true`**. With `false` they are ignored. (95)
6. Only the **Overridden* fields** in the response model are read back. The request carries more fields than can be changed (`reference/hook-catalogue.md`). (95)
7. The call has a **client timeout of 5 seconds** by default (a platform setting you do not control on a hosted environment). On timeout, error, or an unparseable reply Znode **continues with its default result**; the shopper sees no error. (95)
8. Znode sends your configured **Authorization value exactly as typed** in the `Authorization` header. With none configured it sends a placeholder Basic value. **Your service must validate it**; the SDK sample does not. (95)
9. The override applies to **all stores**; the payload carries the store identifier so you branch yourself. (KB 80)
10. Several URLs separated by commas are called **in order**, each receiving the previous reply's `EventPayload`; only the last reply is used. (95)

## When to use / not use
| Requirement | Verdict |
|---|---|
| Change cart/checkout totals after Znode calculated them (shipping, discount, subtotal, total) | Customizable: `CommerceCalculateCompleted` (storefront) or `CPCommerceCalculateCompleted` (Commerce Portal) |
| Change the tax customer code or user used for tax calls | Customizable: `InitiateTaxCalculationCompleted` |
| Rewrite order/quote receipt or email body or total section | Customizable: the Quote and EmailNotification hooks |
| Change a **line-item unit price** | Not possible by override (not read back). Use a price list; see `commerce-promotions-and-pricing` |
| Add a new discount rule | Use a promotion extension, not an override |
| React to an order being placed (send to ERP) | Use an event, not an override |
| Intercept any method not in the six | Needs platform change |

## Nelli-Dev decision guide
| Requirement | Verdict and route |
|---|---|
| Add a handling surcharge to shipping on the storefront | Customizable. `CommerceCalculateCompleted`, return `OverriddenShippingCost` (or `OverriddenShippingHandlingCharges`) with `SkipExecution=true`. State that tax is not recalculated afterwards |
| Change a total after calculation | Same hook, `OverriddenTotal`. Warn that you must keep Subtotal, Discount, Shipping and Total consistent yourself |
| Force the order total from an ERP quote | Customizable with risk: a network call in the shopper's path; 5 s limit; cache |
| Add a per-line shipping or discount amount | `OverriddenItems` (`ShippingCost`, `CustomShippingCost`, `DiscountAmount` per `CartItemId`) |
| Send a customer code to Avalara/Vertex | `InitiateTaxCalculationCompleted`, return `CustomerCode` (wins over `UserId`) |
| Skip tax calculation entirely | `InitiateTaxCalculationCompleted` with `SkipExecution=true` skips the tax step. Confirm with the customer: no tax recorded |
| Edit order confirmation email text | `BindEmailTemplateDetailsStarted` / `SetTotalSectionInEmailTemplateCompleted` (Quote module) or an email template change first (Supported) |
| Hook for "block checkout" | Not an override hook. See `commerce-orders-and-checkout-customization` |

## Reference files
- `reference/hook-catalogue.md`: every hook, where it fires, fields read back.
- `reference/request-and-callback.md`: envelope fields, chaining, timeout, failure behaviour, ordering.
- `reference/admin-registration-and-api.md`: Dev Center steps, fields, messages, API routes.
- `reference/building-a-receiver.md`: SDK receiver, secret check, worked code, testing.
- `reference/override-vs-alternatives.md`: choosing, limits, surprises.

Related: `sdk-custom-api`, `sdk-events-and-webhooks`, `quality-security-checks`, `quality-performance-checks`.
