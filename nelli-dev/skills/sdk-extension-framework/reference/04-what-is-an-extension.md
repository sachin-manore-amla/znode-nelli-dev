# What is an extension and how each kind is registered
Answers: which customizations are extensions, the contract each implements and the Admin step that registers it.

| Kind | Contract / package | Deployed with | Registered in Admin | Observability |
|---|---|---|---|---|
| Promotion type | Class deriving `CartPromotionTypeBase` marked `[PromotionExtension(typeof(CartPromotionTypeBase))]`, package `Znode10.Libraries.Promotions.SDK`, logic in `Calculate()` returning `PromotionCalculateResult` | `znode deploy extension` then Sync | Dev Center > Promotion Settings > Promotion Types > Add Promotion Type: Name, Description, **Class Name** (must equal the class name exactly, case-sensitive), Status Active; optional user-defined fields. Then Marketing > Promotions > Create Promotion with that type | Extension Observability (logs: Information, Warning, Error) |
| Commerce Connector processor | `IBaseProcessor` (package Commerce Connector SDK) | `znode deploy extension` | Exchange: Custom Processing Required, Processor File Name; processor name and class name in Commerce Connector configuration | None (use platform logs) |
| Custom API (endpoints, consumers, ERP touch points, plugins) | SDK application | `znode deploy CustomAPISDK <env>` | Routes in the Custom Ocelot file; webhooks in Webhook Settings; ERP connector in Legacy ERP Connector | Platform logs |
| Admin customization pages | Controllers and views in `Custom.Admin.Core`, view path `Engine.Custom.Api\CustomAdmin\Views\{Controller}\{Action}.cshtml` | `znode deploy CustomAPISDK` | Dev Center > Admin Customizations > Add New: choose Page or Section, enter the custom URL in Content Details, assign role access, Save. Section macros `#userid#`, `#useremailaddress#`, `#roleid#`, `#rolename#` are passed Base64-encoded in the query string. Add the Admin URL to `ZnodeAdminURLCorsPolicy` | Platform logs |
| Webstore | Next.js source | `znode deploy WebStoreSDK` | none | Platform logs |

## Promotion extension notes (KB, 75)
Context: `Context.PromotionBag` (admin settings, user-defined attributes, coupons, promotion name, promo code), cart items, subtotal, quantity, coupons, and the cart's user, profile, portal and order ids; services through the service provider; SDK helpers for product, category, brand and catalog lookups. Account or account-group data is not described: only ids. Keep the class library separate from the API project; only deploy code that builds.
Promotion setup after deploy: Sync, verify the extension is listed without load errors, add the type, create the promotion (Promotion Name, dates, Priority, Active, Stores, Customer Profiles, coupon settings: Coupon Code, Expiration Date, Available Quantity, Maximum Usage, Unique Coupon).

## Custom API limits (KB)
No direct database or Entity Framework access (the SDK template contains data-access projects: do not rely on them); changes to Znode's own APIs go through a support ticket; host in the same network as the Znode API. Extension processors and promotion types run inside Znode, so a slow or failing extension affects the user path.

## Verdicts
Anything that fits the table is Customizable. Anything that needs a hook that is not in the table (a new promotion scope, a checkout step, a built-in API behaviour) is **Needs platform change** unless a method override covers it (`sdk-method-overrides`).
