---
name: commerce-returns
description: Znode returns and RMA - the Return/Cancellation equivalence, order and line-item eligibility with quantity math, return and line-item statuses, the exact Return Total and Voucher allocation formulas, the order fields frozen while a return is open, and the order snapshot taken at placement. Use when working on returns, refunds, RMA configuration or return eligibility.
user-invocable: false
---

# Znode Returns / RMA

Verified against the Znode KB (Creating A Return · Managing Returns · Eligibility Criteria), 2026-09-23.

> **There is no difference between a Return and a Cancellation.** Line items that are **shipped** are Return items; line items that are **not shipped** are Cancellation items. One feature, one screen, one set of rules.

## Initiation

| Initiator | Where | Reason For Return? |
|---|---|---|
| Admin / CSR | `OMS > Orders` → Create Return icon, or Manage Order → Create Return | **Yes — step 3** |
| Registered buyer | Track Order, Order History, or Returns History (login required) | **No** — notes only |
| Guest buyer | Track Order only | **No** — notes only |

Admin can also create a return *as* a registered buyer by impersonating from `Customers > Users > Manage User`. Submitting always creates the return, shows a Return Receipt, and emails both the admin and the buyer.

A single order can have **multiple** returns.

## RMA duration (return window)

Configured at `Admin > System Settings > RMA Configuration`. Checked **per line item**, by line item status:

- Line item **Submitted** → measured from the **Order Date**
- Line item **Shipped** → measured from the **Shipped Date**; falls back to Order Date when no shipping date exists

## Statuses

| Status | Level | Notes |
|---|---|---|
| Submitted | Return + line item | Default on creation |
| In Review | Return + line item | Informational only — no workflow effect |
| Received | Return + line item | Informational only |
| Approved | Return + line item | Terminal for the return |
| Rejected | Return + line item | Terminal |
| Refund Processed | Return | Selectable **only** after the return was saved as Approved |

**Selecting Approved** requires either *all* line items Approved, **or** at least one Approved with every remaining one Rejected.
**Selecting Rejected** requires *all* line items Rejected.

Once Approved or Rejected is saved, the return is locked, and approved line items with their confirmed quantities are **removed from the order's Products Ordered list** (visible in both Admin and the storefront Order Receipt).

> ⚠️ **"Partially Approved" is a KB contradiction.** *Managing Returns* never offers it as a selectable status — the all/some-approved case is just **Approved**. But *Eligibility Criteria* lists `Partially Approved` among the complete statuses and in the eligibility rules. Treat it as **derived state, not a selectable status**, and confirm against the data model before relying on it.

**Complete:** Approved · Partially Approved · Refund Processed · Rejected
**Incomplete:** Submitted · Not submitted · In Review · Received

## Line-item status semantics

- **Approved** — the **Confirmed Qty** out of the **Expected Qty** is approved. Quantities not confirmed are *conceptually rejected* and are **not shown in the UI**.
- **Rejected** — all expected quantities rejected. Confirmed Qty is **reset to Expected Qty** and the input is disabled. (Counterintuitive, but that is the documented behaviour.)
- **Return Shipping** unchecked → that line's shipping amount moves into **Return Charges**, i.e. it is *not* refunded.

## Eligibility

Znode checks the **order** first, then requires at least one eligible **line item**.

**An order is NOT eligible when any of these hold:**

- Status is Cancelled or Failed
- Every line item has passed its RMA duration
- No line item has status Shipped or Submitted
- The order has no line items
- All line items and quantities already sit in **incomplete** return(s) as Expected Qty
- All line items and quantities already sit in **completed** return(s) as Confirmed Qty with line item status Approved

**Line-item quantity math:**

- Quantities held in an **incomplete** return are locked out — only the remainder is eligible.
  *5 ordered, 3 in an incomplete return → 2 eligible. 5 in an incomplete return → line item not eligible at all.*
- Quantities **rejected** in a completed return become eligible again.
  *5 ordered, 3 rejected in a completed return → all 5 eligible again.*
- Approved returns consume only the **Confirmed** quantity.
  *10 ordered; completed return with 7 Expected / 6 Confirmed Approved → **4** eligible.*
- When a line item sits in both a complete and an incomplete return, both rules combine.

## Return Summary and Return Total

| Field | Meaning |
|---|---|
| Subtotal | Sum of return line item totals |
| Shipping | Sum of return line item shipping amounts |
| Tax | Tax on the line item total **and** on the line item shipping total |
| Discount (subtotal) | Sum of all line item and order discounts |
| CSR Discount | Calculated CSR discount |
| Shipping Discount | Sum of all shipping discounts |
| Return Charges | Non-refunded shipping **plus the tax calculated on that shipping**, for every line whose Return Shipping is unchecked |

```
Return Total = Subtotal + Shipping + Handling Charges + Tax
             - Discount(Subtotal) - CSR Discount - Shipping Discount - Return Charges
```


## Voucher allocation

The voucher is refunded **first**, the remainder goes to the payment source.

Because an order can carry several incomplete returns, the Voucher Amount for a return is **calculated only once that return is Approved**:

```
if (VoucherRemainingOnOrder >= ReturnTotal)  VoucherAmountForReturn = ReturnTotal
else                                          VoucherAmountForReturn = VoucherRemainingOnOrder

Refunded to payment source = Return Total - Voucher Amount
```

Voucher Amount is never subtracted from the Order Total — it is treated as a payment method. It cannot be increased automatically, only reduced when `Order Total − Return Charges` falls below it, and that reduction is **not reflected** in the applied-vouchers list under the Voucher input.

> **Znode does not refund automatically.** Refunds are processed manually outside the system, and vouchers are **not** credited back — eligible vouchers must be updated by hand.

## Order fields frozen while a return is open

Until **every** return on the order is complete (Approved / Refund Processed / Rejected), admin cannot change:

Order Status · Shipping Type · Shipping Address zip code · Coupon · Voucher · Tax Exemption · CSR Discount · Line Item Status

## Snapshot taken at order placement

Returns calculate from values frozen at placement, never live values:

Line-item unit price · **included child quantities for every bundle product** · Out Of Stock Options value · shipping amount · tax amount · tax rate (custom tax only) · every line item / order / CSR / shipping discount amount per applied discount · order-level *Calculate Tax On The Discounted Price* · *Include Shipping In Taxes* · handling charges · voucher amount per applied voucher · applied discount types.

Product edits made later never flow into an existing order or its returns.

## Addresses

- **Shipping To** — the default **warehouse** address of the store (where returned items are delivered)
- **Shipping From** — the buyer's shipping address on the order

## Notifications

| Trigger | Template |
|---|---|
| Return created | admin + buyer notification |
| Any status change saved | `ReturnOrderStatusNotificationForCustomer` |
| Status changed to **In Review** | `ReturnRequestNotificationForCustomer` |
| Refund processed | `RefundProcessedNotificationForCustomer` |
| New return, admin-facing | `NewReturnOrderNotificationForAdmin` |

## KB source

- [Managing Returns](https://support.znode.com/support/solutions/folders/43000598179)

## Related
`commerce-orders` · `commerce-promotions-and-pricing`


For return and refund business rules, use the Znode Knowledge Base article above; where it is silent, mark the answer as unconfirmed.
