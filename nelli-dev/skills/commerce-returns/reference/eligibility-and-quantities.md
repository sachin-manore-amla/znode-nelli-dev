# Eligibility and quantities
What this answers: whether an order or line item can be returned, and how many units.
Sources: KB Eligibility Criteria For Creating Order Return/Cancellation Requests Via Returns; Creating A Return (read 2026-11-23). Confidence 85.

## Entry points
| Who | Where |
|---|---|
| Admin | OMS > Orders: Create Return icon; Manage Order: Create Return button |
| Registered buyer | Track Order: Create Return; Orders History: Create Return icon; Returns History: Create Return |
| Guest buyer | Track Order only |
| Admin as buyer | Customers > Users > Manage User (impersonate) |
If ineligible: admin sees a notification; registered buyer sees the button disabled or a notification (by page); guest sees it disabled.

## Create steps
Admin: Create Return > review **Available Qty**, enter **Return Qty** (Return Summary calculates) > Reason For Return > Return Notes (optional) > Submit.
Registered buyer: log in > entry point > choose Order Number (unless from Returns list) > quantities > notes > **Submit Return**.
Guest: Track Order > track > Create Return > quantities > notes > Submit Return.
Outcome: a Return, a Return Receipt, an email. The Reason For Return list values and receipt contents are not described.

## Vocabulary
- **RMA duration**: days after ordering or shipping within which a return can be requested; Admin > System Settings > RMA Configuration. Submitted items count from Order Date; Shipped items from Shipped Date, else Order Date.
- Only items in the Products Ordered section of Manage Order are considered.
- Return status groups: **Complete** = Approved, Partially Approved, Refund Processed, Rejected. **Incomplete** = Submitted, Not submitted, In Review, Received.

## Order is NOT eligible when
- status is Cancelled or Failed;
- all line items are past their RMA duration (by line item status);
- no line item is Shipped or Submitted;
- the order has no line items;
- every quantity of every line item sits in incomplete returns as Expected Qty;
- every quantity of every line item sits in completed returns as Confirmed Qty with status Approved.

## Line-item rules
1. Status must be Shipped or Submitted.
2. Submitted items need RMA duration (from Order Date) not expired.
3. Quantities in an incomplete return (Expected Qty) are excluded; only the remainder is eligible.
4. Quantities rejected in a completed return become eligible again.
5. When a line is in both complete and incomplete returns, rules 3 and 4 combine.

## Examples (from the article)
| Ordered | Situation | Eligible |
|---|---|---|
| 5 | 3 in an incomplete return | 2 |
| 5 | all 5 in an incomplete return | 0 |
| 5 | all 5 in a completed Rejected return (confirmed 5) | 5 |
| 5 | 3 in a completed Rejected return | 5 |
| 10 | 7 in a completed Approved return, 7 expected, 6 confirmed | 4 (10 minus 6 confirmed; the article does not explain) |

## Debugging a disabled Create Return
Check order status, line item statuses, RMA duration, and open returns holding the quantity. A line item that is neither Shipped nor Submitted (for example Failed) never qualifies.
