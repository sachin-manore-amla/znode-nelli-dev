---
name: commerce-vouchers
description: Znode vouchers (the successor of gift cards) - what a voucher is and how it differs from a coupon, the three ways to create one (OMS, import, user record), every Admin field and rule, restriction to a customer, storefront redemption and Voucher History, usage history, notification emails, deletion and return behaviour, and the customization verdict for common voucher requirements (store credit from an ERP, bulk issue, balance lookup, voucher events). Load it for any gift card, store credit, prepaid balance or voucher requirement, and when a voucher is rejected at checkout.
user-invocable: false
---

# Vouchers (gift cards and store credit)

Sources: Znode Knowledge Base articles Configuring a Voucher, Managing Vouchers, Managing Returns, Understanding Default Email Templates (read 2026-11-23); `commerce-promotions-and-pricing` for the coupon comparison. **No API spec for vouchers was available**: the API section is unverified and says so. Confidence 85 for Admin and storefront behaviour (KB read in full), 50 for anything about API or events.

## What a voucher is
A voucher is an admin-issued value that a shopper redeems at checkout, tracked by a **Remaining Amount**. The KB calls vouchers "also called Gift Cards" and lists broad business uses (welcome offers, compensation, B2B customer-specific credit, free shipping, a gift-card store model where the voucher is the only way to pay). The checkout and returns articles treat a voucher as a **payment-like balance, not a discount**: it is never subtracted from the Order Total. (KB 80; the broader promotional wording in Configuring a Voucher and the payment-like wording in Managing Returns are not fully consistent: when design depends on it, test on your environment and record the result.)

## Voucher versus coupon
| | Voucher | Promotion / coupon |
|---|---|---|
| Nature | stored value, partly usable, balance tracked | rule-based discount |
| Reduces Order Total? | no (treated like a payment) | yes |
| Scope | one store (the Store Name field) | one or all stores, by profile |
| Issued | one at a time in Admin, by import, or from a user record | rules plus shared or unique codes |
| Lifecycle | start and expiry date, deactivate, balance | start and end date |

## Ten facts that matter
1. Three ways to create: **OMS > Vouchers > Add New**; **System Settings > Import > Voucher** (template, bulk); **Accounts & Users > Users > Manage User > Voucher tab > Add New** (linked to that user automatically). (KB 85)
2. All vouchers appear under OMS > Vouchers regardless of how created. (KB 85)
3. **Voucher Number** is auto-generated and unique. Voucher Number, Voucher Name, Store Name and Start Date cannot be changed after creation; **Expiration Date** and the remaining amount can. (KB 85)
4. **Voucher Amount** cannot be 0; the KB range is 0.01 to 999999. **Start Date** cannot be earlier than today. (KB 85; an older note gives 99999 for import: check the import template)
5. **Restrict Voucher To A Customer** on: only the assigned customer can redeem; others see "Please enter a valid voucher." Off: any buyer can redeem until the balance is zero or it expires. (KB 85)
6. A voucher created without a customer is associated with the **first customer who redeems it**, permanently; an admin can then switch on the restriction. (KB 85)
7. Vouchers assigned to the logged-in customer can apply automatically at checkout; the buyer can remove them. Anyone with the number can type it in the Voucher section and select Apply. (KB 85)
8. Redemption fails for: invalid, expired, inactive, restricted to another customer, insufficient balance (message wording not documented, except the restricted case). (KB 85)
9. A voucher applied to any order cannot be deleted: "Voucher(s) are applied to some orders and therefore cannot be deleted." Use **Deactivate** to stop use. (KB 85)
10. On a return, the voucher is refunded **first**; the balance is **not** restored automatically, update vouchers by hand (`commerce-returns`). (KB 85)

## Admin screens (summary; fields in `reference/admin-and-import.md`)
- Grid: OMS > Vouchers with Search (by voucher name), Filter, System View, Tools (bulk actions), Columns. Columns: Store Name, Voucher Number, Voucher Name, Voucher Amount, Start Date, Expiration Date, Remaining Amount, Customer Name, Is Active, Action.
- Voucher Management screen: read-only Store Name, Voucher Number, Voucher Name, Start Date; editable Expiration Date and Voucher Remaining Amount; Customer Information (Account Name, Customer Name, Restrict Voucher To A Customer, email option); Additional Attributes from user-defined fields.
- Usage history: order redemptions, balance adjustments and administrative value changes; columns Order Number, Customer Name, Username, Created Date, Notes, Amount Used, Action (View only for redemptions).
- Storefront: My Profile > Voucher History (Voucher Number, Voucher Name, Transaction Amount, Remaining Amount, Start Date, Expiration Date, Action).
- Emails (store templates, see `config-notifications`): New Voucher Issued For Customer (only when "Would You Like To Email The Customer?" is on), Remaining Voucher Balance (after use), Reminder To Use The Voucher Balance Before It Expires.

## Nelli-Dev decision guide
| Requirement | Verdict | Route |
|---|---|---|
| Welcome or compensation credit for one customer | Supported | Voucher restricted to that customer, email option on |
| Thousands of vouchers from a campaign list | Supported | Voucher import template |
| Gift card store (buyers can only pay with an assigned voucher) | Supported | The KB describes it: assign the voucher, remove traditional payment methods for that storefront type (`commerce-checkout-payments`) |
| Voucher valid only above an order value | Not documented as a voucher field | Use a promotion with a minimum order amount, or confirm with Znode support whether a voucher setting exists; B2B example in the KB is customer-specific vouchers with a minimum order value described as a use case, not a field |
| Store credit owned by an ERP, synced to Znode | Customizable, unverified | Create and update vouchers through the API or import from your integration (`config-import-export`, `sdk-data-exchange`). Find the voucher operations in the API reference (`nd_query_spec.py`); the exact routes were not confirmed here |
| Show remaining balance in a custom page | Customizable, unverified | A voucher read operation (user balance or voucher history) is expected in the API; confirm in the reference before use |
| Restore balance automatically on cancel or return | Needs platform change | The KB says the balance is not restored automatically; manual update or a custom job calling the update operation |
| Event when a voucher changes | Not documented | The KB event modules named are User, Order, Product; ask Znode support (`sdk-events-and-webhooks`) |
| Custom voucher rule (for example one use per week) | Needs platform change | No voucher hook is documented; a promotion extension or a method override does not apply to vouchers |
| Voucher email text | Supported | Edit the three templates (`config-notifications`) |
| Edit a voucher on a placed order in Manage Order | Limited | Voucher changes on saved orders are restricted (Managing Returns: voucher is locked while a return is open) |

## Pitfalls
- Expecting the voucher to reduce the Order Total or tax base.
- Forgetting the store scope: a voucher cannot span stores.
- Leaving "restrict to a customer" off for a customer-specific credit: anyone with the number can spend it.
- Assuming a refund restores the voucher.
- Deleting a used voucher (blocked) instead of deactivating it.
- Importing with RemainingAmount different from VoucherAmount (the earlier note says they must match at import: verify with the template).

## Reference files
- `reference/admin-and-import.md` – creation forms, fields, grid, import, history, emails, restrictions, API status.

Related: `commerce-promotions-and-pricing`, `commerce-returns`, `commerce-checkout-payments`, `config-notifications`, `config-import-export`.
