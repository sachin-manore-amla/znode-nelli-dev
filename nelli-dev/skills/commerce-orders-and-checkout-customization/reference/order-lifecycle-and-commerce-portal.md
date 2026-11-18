# Order lifecycle, statuses and Commerce Portal configuration
What this answers: order statuses and edit rules in Admin, and the configurable order model of Commerce Portal (statuses, flags, types, classes, teams, permissions).
Sources: KB Managing Orders (read, 80); module guides and catalogue for Commerce Portal (85, scope only).

## Admin order (OMS > Orders)
Statuses listed in the KB: Canceled, Failed, In Production, In Progress, Invoiced, Order Received, Pending Approval, Pending Payment, Sending, Shipped, Submitted, Waiting To Ship (meanings are not defined by the KB). Any status may be picked except while an incomplete return exists (all returns must be Approved, Refund Processed or Rejected). Canceled runs refund processing: with an approved completed return, refund = Order Total - Handling - Return Charges - Voucher Amount; otherwise Order Total - Voucher Amount; refunds go to the original payment source; vouchers are not refunded. If every line is returned the order becomes Canceled. Product code recognises system statuses such as Submitted, Shipped, Returned, Canceled, Pending Approval, Failed.
Editable: default order status, Job/Project Name, In Hands Date, Shipping Constraints, Shipping Type, Tracking Number, addresses, payment status for offline methods. Read-only: store, date, order number, payment method, transaction id, tax transaction number, purchase order number, external id, customer name/email/phone at placement.
Edit rules: total up (Order Total - Voucher) requests a new payment, down refunds automatically (online payments); changed payment method refunds the old one and requests the new; not supported: change quantities, delete lines, line handling charges, remove voucher after save. Line shipping cannot be edited when the line is Failed or Shipped or the order is Canceled, In Production, In Progress, Invoiced, Order Received, Pending Payment, Sending or Waiting To Ship. Fulfilment: set the line Shipped with a shipped quantity; split shipping divides shipping and discounts proportionally; handling charge applies once. Packaging slip needs Shipped; Capture Payment for authorize-only orders; Resend Confirmation Email; Print.

## Commerce Portal (order desk)
Menu in System Settings > Commerce Settings. All configurable, with API (Commerce Portal API):
| Object | What you configure | Effect |
|---|---|---|
| Order Statuses | code, name, display order, colours; attributes: allow editing, send email, require completeness, working/not shipped, trigger finalized date, set order lines; order classes; **quick status buttons** (text, target status, order, permission) | Status change can email, can lock editing, can complete the order |
| Order Flags | code, names (unchecked, checked, overridden), can override, override user groups | Checklist items; open flags block statuses that require completeness |
| Order Types | name, default flags, default user groups | Applied when creating or changing the type |
| Order Classes | next number, digit length, number format macros; class change buttons (when status is, to class, set status to) | Numbering and moving a record between cart, quote, order, pending order |
| Teams | owner, followers, user groups | Assign, unassign, follow; visibility views |
| Permissions | roles: create, change prices, change line status, set any status, cancel, CSR discount, see all or group orders | Gate each action |
Statuses and flags are data you add; the status list of Admin OMS orders is fixed. Order notes/log in Commerce Portal can be added, edited, deleted, exported.
Custom attribute storage: the Commerce Portal order carries an order attribute collection; see `order-data-and-custom-fields.md`.

## Customization verdicts
Add a status or button: Supported (Commerce Portal). Automate transitions: use events plus the Commerce API status update. Different numbering: Supported. Anything in OMS order grid statuses: platform change.
