# Statuses, totals and rules
What this answers: how a return is managed in Admin, the status rules, the money formulas and the notifications.
Sources: KB Managing Returns; Understanding Default Email Templates (read 2026-11-23). Confidence 85; inconsistencies marked.

## Manage a return
OMS > Returns (list for all stores; columns and filters not described) > **View** > edit > **Save Return** > confirmation pop-up > Ok. Other buttons: Return History (logs admin changes), Print (return receipt), Back.
Non-editable: Return Date, Return No., Return Created By, Order No., Total Return Quantity, Amount (Return Total), Payment Method.

## Return status
| Status | Rule |
|---|---|
| Submitted | default |
| In Review, Received | informational, no workflow |
| Approved | all line items Approved, or at least one Approved and the rest Rejected; final once saved |
| Rejected | all line items Rejected; final once saved |
| Refund Processed | only after the return was saved Approved; refund = Return Total minus Voucher Amount to the payment source; processed manually outside Znode |

## Line item
- Status: Submitted (default), In Review, Received, Approved, Rejected.
- **Approved**: applies to **Confirmed Qty** out of **Expected Qty**; unconfirmed units are treated as rejected and not shown.
- **Rejected**: all expected units; Confirmed Qty resets to Expected Qty and is disabled.
- **Return Shipping** checkbox: unchecked moves the line's shipping to **Return Charges** (not refunded).
- A line item must not be disabled while it is in an incomplete return.

## Return Summary
Fields: Subtotal, Shipping, Tax, Discount (subtotal), CSR Discount, Shipping Discount, Return Charges, Return Total, Voucher Amount.
- Subtotal: sum of line totals. Shipping: sum of line shipping. Tax: on line total plus line shipping. Discount: line and order discounts. Return Charges: non-refunded shipping plus tax on it.
```
Return Total = Subtotal + Shipping + Handling Charges + Tax
             - Discount(Subtotal) - CSR Discount - Shipping Discount - Return Charges
```
(The KB also says handling charges are not considered for returns: inconsistent; verify with a test return.)

## Voucher allocation
Voucher is refunded before the payment source and only computed once the return is Approved:
```
if (voucher remaining on order >= Return Total)  voucher amount = Return Total
else                                             voucher amount = voucher remaining on order
Refunded to payment source = Return Total - voucher amount
```
Voucher is a payment method, not subtracted from the Order Total; it never increases automatically, only decreases when Order Total minus Return Charges falls below it; the applied-voucher list under the Voucher input does not show that reduction. Balances are not restored automatically: update vouchers by hand (`commerce-vouchers`).

## Values frozen at order placement
Unit price; included child quantities of bundles; Out Of Stock Options value; line shipping, tax and (custom tax only) tax rate; every line, order, CSR and shipping discount; order settings Calculate Tax On The Discounted Price and Include Shipping In Taxes; handling charges; voucher amount per voucher; applied discount types.

## Locked while a return is open
Order Status, Shipping Type, Shipping Address (zip), Coupon, Voucher, Tax Exemption, CSR Discount, Line Item Status.

## Shipping and tax rules on the order (Managing Returns)
- Line shipping cannot be edited when the line status is Shipped or Failed. Setting Shipped enables shipped quantity input.
- "Ship Separately" at product level was removed; any line can ship separately; handling still applies to the whole order. Split shipments divide shipping and shipping discounts; no extra handling.
- Changing line shipping amount, Shipping Type or zip removes all shipping discounts and recalculates from the method's saved values.
- Taxes recalculate in real time from the tax settings saved on the order.

## Notifications (display names; edit in CMS > Email & SMS Templates, `config-notifications`)
| Trigger | Template |
|---|---|
| Any saved status change | Return Order Status Notification For Customer |
| Status set to In Review and saved | Return Request Notification For Customer |
| New return (admin) | New Return Order Notification for Admin |
| Refund processed | Refund Processed Notification For Customer |
Macros: status template `#StoreName#`, `#OrderId#`, `#CustomerName#`, `#QuoteStatus#`; refund template `#StoreName#`, `#ReturnNumber#`, `#UserFullName#`. The article says creating a return also emails admin and buyer.

## Not documented
Reason For Return list values, grid columns and filters, return API routes, return events, automatic refund.
