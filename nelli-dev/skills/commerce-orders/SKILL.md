---
name: commerce-orders
description: Znode order statuses and the typical state flow, the fulfillment steps, partial fulfillment and split shipping, and the key order fields. Use when changing an order status, implementing fulfillment or shipment logic, or tracing where an order is stuck.
user-invocable: false
---

# Znode Order Lifecycle & Fulfillment

Admin path: `OMS > Orders`. The backing service is the Commerce Portal API — see.

## Order statuses

| Status | Meaning |
|---|---|
| Submitted | Placed by the customer |
| Order Received | Acknowledged |
| Pending Approval | Awaiting approval routing |
| Pending Payment | Payment not yet captured |
| In Progress | Being processed |
| In Production | Manufacturing/assembly |
| Waiting To Ship | Ready but not shipped |
| Sending | In transit |
| Invoiced | Invoice generated |
| Shipped | Shipped, at least partially |
| Canceled | Cancelled; triggers automatic refund processing |
| Failed | Processing failed |

Transitions are **not hard-coded** — an admin may pick any status from the dropdown, with these constraints:

- If an **incomplete Return** exists, the order status cannot change until every return reaches a terminal state. The same lock blocks **Shipping Type** — see the full 8-field list in `commerce-returns`.
- Selecting **Canceled** triggers refund processing (formula below).
- **When every line item on an order has been returned, the order status changes to Canceled automatically.**

### Cancellation refund

```
if (at least one completed + Approved Return exists)
     Final refund = Order Total - Handling Charges - Return Charges
else Final refund = Order Total

To the payment source = Final refund - Voucher Amount
```

Vouchers are **not** credited back automatically — eligible vouchers must be updated by hand.

### Saving an edited order

After editing, compare the new `Order Total − Voucher Amount` against the old:

- **Increased** → a payment method must be selected and the difference paid before the order saves.
- **Decreased** → a refund is initiated for the reduced amount.

### Edit locks on line item shipping

The line item shipping amount cannot be edited when the **line item** status is `Failed` or `Shipped`, or when the **order** status is any of: Canceled · In Production · In Progress · Invoiced · Order Received · Pending Payment · Sending · Waiting To Ship.

Changing the **Shipping Type**, the **shipping-address zip code**, or a **line item shipping amount** strips every shipping discount from the order and recalculates line shipping and shipping promotions against current values. The Shipping Type dropdown offers only methods common to both the **store** and the customer's **user profile**.

## Typical state flow

```
Submitted -> Order Received
  ├─ (Approval Routing) -> Pending Approval -> [Approved] -> Order Received
  └─ (Payment Hold)     -> Pending Payment  -> [Captured] -> Order Received

Order Received -> In Progress / In Production -> Waiting To Ship
  ├─ -> Shipped   (per-line-item quantities)
  ├─ -> Invoiced
  └─ -> Sending

Terminal: Canceled | Failed
```

## Fulfillment

1. `OMS > Orders > View`
2. Per line item in **Products Ordered**: set Line Item Status to **Shipped** and enter the shipped quantity
3. Enter the **Tracking Number** in Store Order Information
4. Save — triggers the order confirmation email (or use **Resend Confirmation Email**)
5. Generate a **Packaging Slip** or **Invoice** from the Tools dropdown (Packaging Slip requires Shipped status)
6. Use **Capture Payment** for authorize-not-capture flows

## Partial fulfillment / split shipping

Fully supported — any subset of line items can ship at any time. The **Shipping constraints** field lets customers specify *Ship Completely* vs *Ship Partially*. On a split ship, shipping charges and discounts are divided **proportionally** between shipped and non-shipped quantities.

## Key order fields

| Field | Description |
|---|---|
| Tracking Number | Manually entered carrier tracking number |
| Transaction ID | Payment gateway transaction ID |
| Tax Transaction Number | Unique tax service transaction ID |
| Purchase Order Number | Buyer-supplied PO reference |
| External ID | Association with an external/ERP system |
| In Hands Date | Customer's expected delivery date |
| Order History | Full audit log of admin changes and notes |

## Commerce Portal operations

`POST /Orders/CompleteOrder` · `POST /Orders/DuplicateOrder` · `POST /orders/reorder` · `GET /Orders/ValidateOrder/{orderId}` · `PUT /Orders/Status` · `PUT /Orders/Owner` · `PUT /Orders/Followers` · `GET /orders/order-tracking-details/{classNumber}/{emailAddress}` · `GET /Invoice/GenerateInvoice/{orderIds}`.

Line items: `PUT /LineItems/Status`, `PUT /LineItems/Price`, `PUT /lineitems/quantity`, `POST /LineItems/SendLineItems/{orderId}/{lineItemIds}`, `POST /LineItems/DuplicateLineItem`.

Shipments: `/shippings` — get by orderId, update shipment, remove shipping.

## KB source

- [Managing Orders](https://support.znode.com/support/solutions/folders/43000598175)
- [Managing Pending Orders and Payments](https://support.znode.com/support/solutions/folders/43000598176)

## Related
`commerce-checkout-payments` · `commerce-returns`
