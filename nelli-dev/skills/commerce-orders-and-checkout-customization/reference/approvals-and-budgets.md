# Approvals, pending orders and budgets
What this answers: how orders are routed for approval, what pending orders and pending payments are, and budget limits.
Sources: KB approval and pending-order articles as summarised in the existing B2B skill (80); module guide catalogue (85). KB inconsistencies are flagged.

## Setup
1. Store: Stores > Manage > **Approval Management** (the KB also says Additional Attributes in an older article; prefer the tab). Enable, choose **Approval Type** and **Approval Level**, set "Set approval for Orders above ($)".
2. Payment methods: Is Approval Required on the relevant methods (Stores > Payment Method).
3. Users: Customers > Users > Manage > Approval Management for approval type per user and approver brackets.
4. **Save and Publish** the store, otherwise routing has no effect.
| Approval Type | Behaviour |
|---|---|
| Store | any payment; orders above the store limit need approval |
| Payment | only payment methods flagged for approval |
| User | amount at or above the minimum user bracket |
| Level | Single: store approvers; Multi: order goes to user-level approvers when amount >= minimum bracket "From", otherwise store approvers |
The threshold is the **order subtotal**, never the total. Up to 5 levels per user; each approver on one level only; top bracket uses Is No Limit. Storefront orders only (admin-placed orders bypass). Deferred methods (Purchase Order, Invoice Me, Charge on Delivery) are the usual trigger; the KB loosely also mentions budget ranges, so confirm on your environment.

## Flow
Submit for Approval replaces Place Order; the order becomes a pending order (status Pending Approval), payment is not captured; approvers act in My Account > Pending Orders (approve, reject, comment); final approval converts to a real order and sends confirmation; rejection notifies the shopper. Admin: OMS > Pending Orders (View, Convert to Order, notes). Payment capture or void happens on approve/reject. No automatic expiry is documented.

## Pending payments and Open Account Billing
Deferred-payment orders by a user with no Billing Account Number queue under OMS > Pending Payments until an admin assigns a number and accepts; accepted ones become pending orders. Applies to PO, Invoice Me, COD only.

## Budgets
Customers > Users > Manage > Additional Attributes > Budgets: Per Order Limit, Annual Order Limit (store sets the start month; blank = January). Exceeding blocks placement. Blank or 0 = no limit.

## Customization
Supported: all of the above. Customizable: notify approvers elsewhere (event on pending order is not documented; use order events plus API reads). Not supported: approval by custom condition (region, product category) without a platform change; use profiles/accounts plus thresholds, or block in Webstore source.
