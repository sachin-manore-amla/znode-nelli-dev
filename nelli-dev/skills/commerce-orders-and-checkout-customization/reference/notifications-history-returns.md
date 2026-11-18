# Order notifications, history and returns configuration
What this answers: which emails fire for order events, how to change them, how history works, and where returns are configured.
Sources: KB Managing Orders, Email and SMS templates (80); module guides (85); method override hooks (95).

## Emails and SMS
Admin: CMS > Email & SMS Templates; enable per store at Tools > Configure Email & SMS Notification (Add New area, Is Active). A template not enabled for a store sends nothing. Per-store SMTP at Stores > Manage > SMTP (From Email Address required; Turn Off Emails disables all). SMS: Twilio only, Stores > Manage > SMS Notifications.
Order-related templates: Order Receipt / Store Order Receipt, Order Placed Notification (admin), Shipping Receipt, Tracking Links, Cancelled Order Receipt, Resend Order Receipt, Vendor Receipt, Product Key Order Receipt; approvals (Pending Order Approval, Approved, Rejected, Status Notification, Billing Account Number Added); quotes (acknowledgement, new request, in review, approved, rejected, status, converted); returns (new return for admin, request for customer, status, refund processed); vouchers (issued, remaining balance, reminder); low inventory.
Macros use `#Name#` (for example `#StoreName#`, `#OrderId#`, `#ReceiptText#`, `#TrackingNumber#`). A store-specific variant is a cloned template pointed to by the store's area row.
Triggers: placing, saving shipping (Shipped with tracking), Resend Confirmation Email, cancel, approval steps, quote and return events. Commerce Portal statuses with "send email" send the status email. Order notification alerts: all orders or above an amount to set addresses.
Customization: edit templates (Supported); change receipt text or totals table programmatically (`BindEmailTemplateDetailsStarted`, `SetTotalSectionInEmailTemplateCompleted`); alter or suppress the Commerce Portal admin email (`SendEmailCPAdministratorCompleted`); send your own email on an Order Created/Updated event (Customizable). Template sources: see `config-notifications`.

## History and notes
Order History on Manage Order lists every admin change and notes from admins and customers; an Add Note action exists; API: add order note, note list, create history entry. Commerce Portal has Notes/Log (add, edit, delete, export CSV/Excel). Customers see customer-visible notes. History cannot be rewritten by hooks.

## Returns
Return and cancellation are one feature (shipped lines are returns, unshipped lines cancellations). Configuration: System Settings > RMA Configuration (return window measured from order date for Submitted lines, shipped date for Shipped lines), reasons for return, return statuses, store setting to enable return requests from the webstore. Statuses: Submitted, In Review, Received, Approved, Rejected, Refund Processed. Full rules in `commerce-returns`. Customization: return status emails (templates), return history, return events not documented.

## Inventory touch points
Stock is validated at add to cart and checkout (min/max quantities, out-of-stock option); see `commerce-inventory`.
