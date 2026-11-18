# Vouchers
What this answers: what a voucher is, how it differs from a coupon, fields, redemption, import and rules.
Source: KB Managing Vouchers folder and Managing Orders (80); 10.10 release notes (80). Gift cards were replaced by vouchers in 9.6.

## Voucher versus coupon
| | Voucher | Promotion/coupon |
|---|---|---|
| Nature | prepaid balance, partly usable | rule-based discount |
| Counted as | a payment (never reduces Order Total) | a discount (reduces Order Total) |
| Scope | one store only | one or all stores, by profile |
| Issued | admin, one at a time (or import) | admin, bulk codes |

## Admin
**OMS > Vouchers > Add New**: Voucher Number (auto, unique, not editable), Voucher Name, Store Name, Voucher Amount, Start/Expiration Date, Is Active, Restrict Voucher To A Customer, Customer Name, Email The Customer?. Also activate/deactivate, delete, usage history.
Storefront: My Account > Vouchers (amount, remaining, dates, usage history). At checkout vouchers assigned to the shopper are offered; anyone with the number can enter it.
Import: System Settings > Imports > Vouchers. Columns: StoreCode (required), VoucherNumber (10 alphanumeric, blank = generated), VoucherName (100), VoucherAmount (0.01 to 99999), RemainingAmount (must equal amount at import), RestrictVoucherToCustomer (0/1), IsActive (0/1), Username (required when restricted).
Notification templates: new voucher issued, remaining balance after use, reminder before expiry (reminder days per store).

## Rules and surprises
- Balance is **not** restored automatically on cancel or return; update vouchers by hand.
- On a return the voucher is consumed first (see `commerce-returns`).
- On a saved order vouchers cannot be removed; unsaved changes allowed. In 10.10 Manage Order voucher add/modify is disabled.
- Vouchers do not stack with the same voucher twice.
- Balance lookup API: voucher balance by user name; history by voucher; create/update/delete.

## Customization
Vouchers cover prepaid balance. For store credit from an ERP, create/update vouchers by API or import; there is no voucher hook. Event on voucher change: not documented.
