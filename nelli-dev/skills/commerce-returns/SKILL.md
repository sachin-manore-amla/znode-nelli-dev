---
name: commerce-returns
description: Znode returns and cancellations (one feature, Return equals Cancellation) - who can start one and where, eligibility of orders and line items with the quantity rules, the RMA duration setting, return and line-item statuses and their rules, the Return Total and voucher allocation formulas, locked order fields, the values frozen at order placement, notification emails, what Znode does not do (no automatic refund, no automatic voucher credit) and the customization verdict per need. Load it for any return, cancellation, RMA, refund or return-eligibility requirement and when a Create Return button is disabled.
user-invocable: false
---

# Returns and cancellations

Sources: Znode Knowledge Base articles Creating A Return, Managing Returns, Eligibility Criteria For Creating Order Return/Cancellation Requests Via Returns, Understanding Default Email Templates (read in full 2026-11-23). No exported API spec for returns was available: API statements are unverified. A live shared FAQ "Returns & Refunds Answers" may override the KB for business rules: if your team has it, check Planned, Open or Tentative markers there first. Confidence 85 for KB behaviour; the KB itself has inconsistencies, listed below.

> A Return and a Cancellation are the same feature. **Shipped** line items are returns; **not shipped** line items are cancellations. One screen, one set of rules. (KB 85)

## Fourteen facts that matter
1. A single order can have **multiple returns**. (KB 85)
2. Who starts one: Admin users (guest or registered buyer), registered buyers (login required), admins impersonating a buyer (Customers > Users > Manage User), guest buyers (Track Order page only). (KB 85)
3. Admin entry: OMS > Orders, **Create Return** icon on the list, or the button on Manage Order. Reason For Return is asked on the admin form; buyers enter notes only. (KB 85)
4. Every create produces a Return, shows a Return Receipt and sends an email to the admin and the buyer. (KB 85)
5. **RMA duration** (Admin > System Settings > RMA Configuration) is checked per line item: Submitted items from the Order Date, Shipped items from the Shipped Date (Order Date if none). (KB 85)
6. Eligibility is checked at order level first, then at least one eligible line item must exist (`reference/eligibility-and-quantities.md`). (KB 85)
7. Return statuses: **Submitted** (default), **In Review**, **Received**, **Approved**, **Rejected**, **Refund Processed**. In Review and Received are informational only. (KB 85)
8. Approved needs all line items Approved, or at least one Approved and the rest Rejected; Rejected needs all Rejected; Refund Processed only after the return was saved Approved. Approved and Rejected are final once saved. (KB 85)
9. Approved line items and their confirmed quantities are removed from the order's Products Ordered list. (KB 85)
10. **Znode does not refund automatically.** The refund (Return Total minus Voucher Amount) is processed manually outside Znode; vouchers are not credited back automatically. (KB 85)
11. Totals use **values saved on the order at placement**, never live product data. (KB 85)
12. While any return on the order is incomplete, Order Status, Shipping Type, Shipping Address zip, Coupon, Voucher, Tax Exemption, CSR Discount and Line Item Status cannot be changed. (KB 85)
13. Return To address is the store's default warehouse; From is the buyer's shipping address on the order. (KB 85)
14. Customer details on a return are fixed at order placement; later user edits do not update it. (KB 85)

## KB inconsistencies to treat carefully
- "Partially Approved" is listed as a complete status in Eligibility Criteria but is not a selectable status in Managing Returns: treat as derived, confirm on your environment.
- Managing Returns says handling charges are not considered for returns while its Return Total formula includes them.
- Managing Returns uses "Return Processed" once where it means Refund Processed.
- Eligibility Example 3 (10 ordered, 7 expected, 6 confirmed, 4 eligible) subtracts the confirmed quantity: the article does not explain it.

## Nelli-Dev decision guide
| Requirement | Verdict | Route |
|---|---|---|
| Change the return window | Supported | RMA Configuration (days) |
| Let guests return | Supported | Track Order page Create Return |
| Require a reason from buyers | Needs platform change / unverified | Buyer form has notes only; capture a reason in your own Webstore UI and store it as a return note (route unverified) |
| Auto-approve returns | Customizable, unverified | Custom code calling the return update operation; find it in the API reference; not documented in the KB |
| Trigger the refund at the payment gateway | Customizable | The KB says refunds happen outside Znode; integrate your ERP or gateway on the Refund Processed status (use an event if documented, else polling; ask Znode) |
| Restore voucher balance automatically | Customizable, unverified | Update the voucher through its API after approval (`commerce-vouchers`) |
| Restocking fee or return label charge | Partly supported | Unchecking **Return Shipping** moves the line's shipping to **Return Charges** (not refunded); a custom fee is Customizable via a method override only where a hook exists (none for returns documented) |
| Block returns for certain products | Needs platform change | No product-level rule is documented; handle in your own storefront UI |
| Notification wording | Supported | Edit the five return templates (`reference/statuses-and-totals.md`, `config-notifications`) |
| Return reports | Customizable | Reports or API read of returns (`config-import-export`, reports articles not read) |
| Send return data to an ERP | Customizable | Events or webhooks (`sdk-events-and-webhooks`); a return event is not documented: ask Znode |

## Pitfalls
- Expecting Approved to pay anything: it only records the decision.
- Counting Expected instead of Confirmed quantity when computing what can still be returned.
- Changing the order (coupon, voucher, shipping type) while a return is open: it is locked.
- Editing a product and expecting existing returns to change.
- Disabling a line item that sits in an incomplete return (the KB says not to).

## Reference files
- `reference/eligibility-and-quantities.md` – order and line-item eligibility, RMA duration, quantity examples, entry points.
- `reference/statuses-and-totals.md` – statuses, line-item rules, Return Total, voucher allocation, saved order values, locked fields, shipping and tax rules, notifications, buttons.

Related: `commerce-orders`, `commerce-vouchers`, `commerce-promotions-and-pricing`, `commerce-tax-shipping`, `config-notifications`, `commerce-inventory`.
