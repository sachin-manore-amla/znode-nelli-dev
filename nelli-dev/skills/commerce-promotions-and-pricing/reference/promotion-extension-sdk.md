# Promotion Extension SDK
What this answers: how to write, deploy and register a custom promotion type, the contract, and its limits.
Sources: KB Promotion Extensibility Developer Guide (read in full, 80); SDK package members and product source (95).

## When
Use only when no built-in type, price list or coupon expresses the rule. Verdict Customizable. Not for changing the order promotions are applied in, or taxes.

## Contract
- Package `Znode10.Libraries.Promotions.SDK` (sample uses 10.0.0-rc-01, a release candidate) and `Znode10.Libraries.Extensions.Observability` for logging. .NET 8, a **separate class library** (not the API project).
- Class derives `CartPromotionTypeBase`, decorated `[PromotionExtension(typeof(CartPromotionTypeBase))]` (without it the loader ignores the class).
- Constructor sets `Name`, `Description`, `ClassName` (unique; must equal the Admin Class Name, **case-sensitive**).
- Override `PromotionCalculateResult Calculate(int? couponIndex, IReadOnlyList<IPromotionInfo> allPromotions)`. Never return null. Set `IsApplied = true` or the result is ignored.
- Result members: `OrderLevelDiscount`, `ShippingLevelDiscount`, `LineItemDiscounts` (dictionary keyed by cart item index), `CouponResult` (`IsValid`, `IsApplied`, `Message`).
- Helpers on the base: `GetCartSubTotal()`, `GetCartQuantity()` (line quantities plus selected group-product quantities; add-ons not counted), `GetQuantityOrdered(productId)`, `IsDiscountApplicable(...)`, `CreatePromoDiscount(decimal amount, DiscountLevelCode level)`, `CreateCouponDiscount(code, amount, level)`. Amounts are **absolute currency amounts**: compute percentages yourself. Optional `PreSubmitOrderProcess()` (return false to flag the order as not submittable on the Engine order path) and `PostSubmitOrderProcess()`.
- Context: `Context.Cart` (`SubTotal`, `PortalId`, `ProfileId`, `UserId`, `OrderId`, `CartItems`, `Coupons`, `GetTotalItemCount()`, `GetMaximumApplicableDiscountOnLineItem(...)`), `Context.PromotionBag` (configuration: promotion id/name/message/type, `PromoCode`, `Discount`, minimum quantities/amount, coupon flags, BOGO quantities), `Context.Helper` (promotion product ids, brand codes, category ids, catalog ids, SKUs, shipping codes), `ServiceProvider` (dependency injection, for `IExtensionLogger`).
- Promotion-level user-defined attributes are on `IPromotionInfo.Attributes` (items of `allPromotions`; filter with `Context.GetPromotionsByType("Cart", ClassName, allPromotions, "PromotionId")`). The KB sample reads `Context.PromotionBag.Attributes[...]`; `IPromotionBag` has **no** `Attributes` member in the package: follow the package. (conflict: product wins)
- Shopper data: ids only (`UserId`, `ProfileId`, `PortalId`, `OrderId`). No account, account group or customer attribute members.
- Member sets can differ between package versions (the platform source has `ShippingCost` and extra members on `IPromotionCart` that rc-01 lacks). Check your package.

## What the engine does with the result
The bridge builds the context, calls `Calculate`, then applies the result: line discounts are added per line (with audit entries and the displayed price updated), the order-level discount is distributed to lines by the engine, shipping discount is capped by remaining shipping. If the promotion has a coupon and the entered coupon does not match, the bridge skips your code. `IsAnyPromotionApplied` is set.

## Lifecycle and deployment
1. Build (Release). Only the extension DLL is deployed.
2. `znode connect <your own token>`; `znode deploy extension "<csproj path>"` (one project) or a folder of projects. Never paste the token into files.
3. **Sync**: Admin > Extension Observability > Sync (loads or reloads). Deployment alone does not activate. The sync result lists loaded projects and promotions; a failure returns an error message.
4. Register: Dev Center > Promotion Settings > Promotion Types > Add: Name, Description, Class Name (exact), Status Active. A class found in code but not yet registered can be registered from the list.
5. Create the promotion: Marketing > Promotions and Coupons, choose the new type, set stores, profiles, dates, Display Order, active.
6. Logs: Admin > Extension Observability > Execution Logs (`IExtensionLogger`: information, warning, error; resolve it inside `Calculate`, not the constructor).
7. Update: change, build, deploy, Sync, test. Roll back: redeploy the previous version and Sync; deactivate the promotion first.
`extension.manifest.json` beside the project carries name, version, platform range and supported contract; its role in Sync is not documented.

## Limits and guidance
- Runs in the cart/checkout request path, on every cart change: no remote or database calls, exit early, stateless, thread-safe, no per-item logging in loops, no personal data in logs.
- Not documented: maximum promotions, timeouts, thread-safety guarantees.
- Engine behaviour not verified live in the worked example: stacking with caps, display of the discount line, currency decimals.
- Fixed numbers (percent, threshold) in code need a redeploy to change; use promotion attributes read through `IPromotionInfo` for admin-editable values only after confirming they are exposed in your version.
- Profile scoping and Minimum Quantity/Order Amount on the promotion screen still apply to custom types as configured (whether Admin shows all fields for custom types is not documented).

## Registry
Verified member list: `registry/promotion-extension.json`.
