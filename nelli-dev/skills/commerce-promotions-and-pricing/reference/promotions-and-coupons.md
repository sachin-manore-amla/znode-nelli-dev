# Promotions and coupons
What this answers: promotion types, fields, scoping, coupon modes, stacking, BOGO and the settings that change behaviour.
Sources: KB Configuring a Promotion, Managing Promotions and Coupons, Unique Coupon Code Generation Scenarios, Configuring BOGO (read, 80); product source for the type list (95).

## Admin
Menu: **Marketing > Promotions and Coupons**. Tabs: Promotion Information (Promotion Code, Name, Description, Start Date, End Date, Display Order), Discount Information (Discount Type, Store, Profile, Discount Amount, Minimum Quantity, Minimum Order Amount, targets), Coupon Information.
Profile: one, several (since 9.7.4) or **All Profiles** (disables the others). Store: one or all.

## Promotion types (built in)
| Group | Types |
|---|---|
| Line item | Amount/Percent Off Product, Brand, Category, Catalog, X if Y purchased (fields Product To Discount, Required Product, Product Quantity) |
| Order | Amount/Percent Off Order |
| Shipping | Amount/Percent Off Shipping; Shipping With Carrier; Amount Off Shipping With Carrier Under Weight |
| Price display | Amount/Percent Off Displayed Product Price (changes the shown price in the catalog), Call For Pricing (hides price, shows a message) |
| BOGO | Amount Off BOGO, Percent Off BOGO |
| Custom | Sample Custom Promotion Class (off by default) and your own types (`promotion-extension-sdk.md`) |
Category promotions are evaluated at category level regardless of catalog.

## Coupons
Tick **Requires a Coupon** to reveal Promotion Message, coupon code, Available Quantity, Is Unique, Is Allowed With Other Coupon.
| Mode | Behaviour |
|---|---|
| Without coupon | Applied automatically in the cart |
| Normal code | One shared code; Available Quantity caps uses |
| Unique codes | Generated batch; fields Custom Coupon (Pre Text or Post Text), Coupon Code Format, Coupon Code Length, Initial Quantity **1 to 99,999** |
Messages: "Enter Available Quantity between 1-99999." / "Please enter Available Quantity". **Generate Coupons** is disabled until the promotion is saved. Saving a unique-coupon promotion with no codes shows "Please generate coupon codes to continue."; leaving shows "Are you sure you want to leave this page?". Generating more codes adds to the pool; existing codes are untouched. The coupon grid shows Coupon Code, Used, Activate; summary shows Total, Used, Unused.
A second coupon is blocked by default; it works only if "Is Allowed With Other Coupon" is on for both.

## BOGO (Discount Information)
Fields: For Each Qty Bought (BO), Discount Qty (GO), Maximum Applicable Sets, When Buying (product, category, brand), Get Discounts On (product, category, brand). A set is BO plus GO quantity; total discount is the per-set discount times the sets (capped by Maximum Applicable Sets). Not supported: BOGO import, group or bundle products. Multiple discounted lines: the least-discount line is used. Interplay with other promotions is not documented.

## Global settings
Dev Center > Global Settings > Promotions and Coupons: **Allow Promotions And Coupons Together**, exceptions list for promotions allowed with others, **Calculate Tax On Discounted Price** (tax on price after discount). These are honoured when an order is **created**, not when a discount is applied while managing an existing order. See `config-global-settings`.

## Behaviour to know
- Promotions re-run on add/remove item, quantity change, coupon change, viewing the cart, checkout, shipping method change.
- Shipping promotions after placement apply only when the shipping method or address changes.
- 10.10: adding or modifying promotions, coupons and vouchers on Manage Order (Admin) is disabled; existing ones stay visible.
- A promotion with a date range ends at its End Date; a Display Order value orders application.
- Unique coupon codes are single use.
- Exports: promotions and coupons can be exported (Admin tools).

## API
Core API v2 / v1: create, get, update, delete promotion; promotion attributes per discount type; associate targets; coupon list/get; generate coupons; activate/deactivate coupons. Cart-level apply/remove discount is on the Commerce API (`api-catalog`). Look up exact routes with `nd_query_spec.py`.
