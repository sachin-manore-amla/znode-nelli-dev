# Voucher Admin, import and API status
What this answers: the exact forms, fields and rules for creating, importing, editing, redeeming and reviewing vouchers.
Sources: KB Configuring a Voucher, Managing Vouchers, Managing Returns, Understanding Default Email Templates (read 2026-11-23). The import column list below comes from the earlier Nelli-Dev skill that read the KB Managing Vouchers folder; the current Managing Vouchers article says the import columns are **not described**, so treat the import column list as 60 and check the downloaded template.

## Create form (OMS > Vouchers > Add New, or user record > Voucher tab)
| Field | Rule |
|---|---|
| Voucher Number | auto, unique |
| Voucher Name | text |
| Store Name | the store the voucher belongs to (one store) |
| Voucher Amount | 0.01 to 999999, not 0 |
| Start Date | not earlier than today |
| Expiration Date | when it expires |
| Is Active | enables or disables use |
| Restrict Voucher To A Customer | limits use to one customer |
| Customer Name | assigned customer; **Search** finds existing buyers and customers; **Add New Customer** creates one and assigns the voucher |
| Would You Like To Email The Customer? | sends the "New Voucher Issued For Customer" template |

## Import
System Settings > Import > Voucher: download the template, fill it, upload. Recommended for bulk. Columns recorded earlier (verify against the template): StoreCode (required), VoucherNumber (10 alphanumeric, blank = generated), VoucherName (100), VoucherAmount, RemainingAmount (equal to the amount at import), RestrictVoucherToCustomer (0/1), IsActive (0/1), Username (required when restricted). An existing voucher number updates, otherwise it creates (earlier note, unverified in the current article). Import error handling: `config-import-export`.

## Manage screen
Read-only: Store Name, Voucher Number, Voucher Name, Start Date. Editable: Expiration Date, Voucher Remaining Amount. Customer Information shows Account Name and "Username | First Name Last Name". Additional Attributes shows custom fields created under Dev Center User Defined Fields (`config-global-attributes`).
Actions on the grid: Edit, **Deactivate** (stops future use), **Delete** (blocked once applied to an order or used).

## Restriction behaviour
- Restricted: only the assigned customer; others get "Please enter a valid voucher."
- Not restricted: any buyer, several buyers can share the balance; the first redeemer appears as the customer.
- No customer at creation: the first successful redeemer is associated and cannot be changed; an administrator can then enable the restriction.

## Redemption at checkout
Voucher section: enter the number, Apply. The applied line shows Amount Used, Voucher Name, Expiration Date and time, Voucher Number. Rejections: invalid, expired, inactive, restricted to another customer, insufficient balance.

## Usage history
Recorded: order redemptions, balance adjustments, administrative changes. A balance update creates a note only (no View action). Search, filters, saved views and column selection exist but may be more limited than the main grid.

## Emails
| Template (display name) | When |
|---|---|
| New Voucher Issued For Customer | when the email option is on at creation |
| Remaining Voucher Balance | after a voucher is used on an order |
| Reminder To Use The Voucher Balance Before It Expires | before expiry; reminder days are a store setting under Additional Store Attributes (earlier note, unverified in the articles read) |
Macros for these templates: `#CustomerName#`, `#StoreName#`, `#CardNumber#` (the voucher number), `#VoucherName#`, `#StartDate#`, `#ExpirationDate#`, `#Amount#`, `#Remaining Amount#`, `#VoucherAmountUsed#` (see `config-notifications`).

## Returns and orders
Voucher refunded first on a return; amount computed only after the return is Approved; never restored automatically; locked on the order while a return is open. Formula: `commerce-returns`.

## API
No exported spec was available for vouchers. The platform has voucher operations (list, create, update, delete, usage history, balance by user); their names, routes and request shapes were **not confirmed**. Find them with `nd_query_spec.py` or the API reference (`api-catalog`), prefer the v2 family, and mark each `VERIFIED (apidocs page)` only after reading its page.
