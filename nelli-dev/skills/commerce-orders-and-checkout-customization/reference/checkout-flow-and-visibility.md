# Checkout flow and method visibility
What this answers: what the storefront checkout contains, which settings change it, and exactly which payment and shipping methods appear.
Sources: Webstore source (90); KB Create An Order From the Storefront, Managing Shipping Methods (80).

## Composition (Webstore)
Left column: addresses (guests sign in or continue as guest), **Shipping Method**, shipping constraint (ship completely or partially), **Payment**. Right column: cart review, **promo section** (shown only when the store's cart setting enables it and not for quotes), **CSR discount** (only for impersonating admins), **Additional Information** (Job/Project Name max 100, Additional Information max 500, both optional, not shown to guests per the KB). A checkout timer ends the session and returns to cart. Place Order calls the BFF route `/api/place-order`, which checks the checkout session, runs `validate-checkout`, validates reCAPTCHA, then calls the Commerce API `place-order`. Quotes use a different branch (no checkout session).
After placement: receipt page, confirmation email (Order Receipt template), admin email (Order Placed Notification), order in OMS > Orders and Order History. Unit prices, line shipping and tax, tax rates, discount allocations, handling and voucher amounts are stored at placement.
Prerequisites: products in the store catalog, at least one shipping method, at least one payment method (or a voucher), Guest Checkout enabled for guests.

## Settings that change checkout
| Setting | Where | Effect |
|---|---|---|
| Guest Checkout | store settings | Shows "Continue as Guest" |
| Requires Manual Approval Of Every Order | Store Settings > General | Every order waits for admin approval |
| Order Status (default) | Store Administration > Store Settings > General Settings > Order Status | initial status on the receipt and in OMS |
| Order notification alerts | store | email for all orders or above an amount to set addresses |
| Approval Management | store | Submit for Approval replaces Place Order |
| reCAPTCHA for checkout | store/global | blocks place order when failed |
| Enable Address Validation | store (USPS) | validation step on addresses |
| Promo section | store cart settings | shows/hides coupon entry |
| Price rounding, tax after discount | global settings | totals |

## Payment and shipping method visibility
Methods must be associated with the store. Then, with profiles:
| Store | Profile(s) | Shown |
|---|---|---|
| A,B,C,D | none | A,B,C,D |
| A,B,C,D | C,D | C,D |
| A,B,C,D | E,F (no overlap) | A,B,C,D |
| A,B,C,D | X: A,P,Q and Y: C,D,G,H | A,C,D |
| none | A,B | none |
Shipping also applies destination country/state/postal restrictions, the method's Enable flag, and rates above zero for carrier types. Payment methods also need an active configuration set with Display Setting on. Role rules for addresses: B2B Administrator sees, adds, edits all account addresses; Manager sees and selects but cannot edit; User only defaults.

## Customization points
Webstore component and BFF route (source customization); Custom API for pre-checks; method override for totals; promotion for discounts; plugins for providers. Nothing server-side vetoes placement except approval routing, budgets, inventory rules and payment failure.
