# Changing the address on an existing order or quote

Files in this folder: 01 functional · 03 admin · 06 API · 07 functions · 08 database


## 1. What it is
After an order (or a quote) exists, staff can change its shipping or billing address. Depending on the screen or call, this changes the order's own copy of the address, the old order record, or the saved address itself.

## 2. Where
| Where | How |
|---|---|
| Admin Manage Order | open the order, edit or change the shipping or billing address, save, then submit the order changes |
| Commerce Portal Edit Order | pick a different Ship To / Bill To and save the panel (choosing addresses) |
| Integrations | "Order / Update Order Address", "v2 customers / {order number} / order-address", "AccountQuote / Update Quote Shipping Address" |
| Webstore | not available after the order is placed |

## 3. Who
- Admin staff with the order permissions. For a B2B **User** or **Manager** customer, a pop-up asks to confirm before the address form opens.
- Commerce Portal users who can edit the order (the order's status must allow editing).
- The integration calls do not check who is calling.

## 4. Step by step (admin)
1. Open the order and click the address you want to change (not possible while a return is pending).
2. Change the address (the default boxes are not shown) and save.
3. The order's totals and shipping are recalculated on screen; shipping is recalculated when the state or postal code changed.
4. Submit the order changes to keep them.

## 5. What is allowed and what is not
- In the admin, saving the address also updates the saved address in the customer's (or account's) address book.
- When the store's address check is on, an invalid US address is refused.
- The v2 "order-address" call updates the **saved address**, not the order's copy, even though it takes an order number.
- The quote call overwrites the saved address the quote uses and recalculates the quote; it needs display name, names, street, country code, state, city, postal code and phone, and a known country code.
- An address that is used for both billing and shipping can be split into a "*name*_Copy" address when it is changed from an order.

## 6. Messages
| Message | Where | When |
|---|---|---|
| "The shopper/customer belongs to the “User(B2B)” role…" / "…“Manager(B2B)” role…" | Admin | opening the address of a User or Manager customer |
| "Your Shipping Address is not a valid address. Please enter a valid address to continue." | Admin | address check on, invalid US address |
| "Failed to update record." | Admin | any error |
| "Display Name is required." … "Phone Number is required.", "Invalid Country Code.", "Quote not found.", "Invalid Quote Id." | API (quote) | missing fields, unknown country or quote |
| "Address Id cannot be less than 1." | API (v2 order-address) | no address id |

## 7. How it differs
By surface only (sections 2 and 5); country matters only for the US address check and the quote's country-code check.

## 8. What can be combined
Shipping and billing can be changed separately or set to the same address.

## 9. What it changes elsewhere
- Order totals, shipping and tax are recalculated.
- Where the saved address is updated (admin, v2 order-address, quote), the change also shows in the address book of the customer or account.

## 10. Quick answers
- **Does changing the address on an order change the customer's address book?** In the admin, yes; in the Commerce Portal, no (it copies the chosen address into the order).
- **Which API updates only the order's copy?** The Commerce API "shippings / order-shipment" and "payments" calls.

## 11. What could not be settled
- None of these calls was run live.
- How the admin's final "submit order changes" writes the address is part of the order module (MOD-ORDER) and was not traced here.

## 12. For developers
03 admin, 06 API, 07 functions, 08 database. Not available on the webstore; the Commerce Portal part is in checkout-address-selection.
