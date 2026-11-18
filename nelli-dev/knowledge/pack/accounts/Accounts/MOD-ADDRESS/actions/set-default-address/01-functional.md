# Set the default (primary) billing and shipping address

Files in this folder: 01 functional · 03 admin · 04 webstore · 05 Commerce Portal · 06 API · 07 functions · 08 database


---

## 1. What it is
Every address book has one **default billing** address and one **default shipping** address (the webstore calls them "Primary Billing" and "Primary Shipping"). They are preselected at checkout, in admin Create Order and in the Commerce Portal. One address can be both.

For a B2B account the defaults belong to the account, so they are the same for every user of the account.

## 2. Where you do it

| Where | How |
|---|---|
| Webstore address book | "Set as Primary Shipping" / "Set as Primary Billing" under an address; or the "Set as default shipping / billing address" boxes when adding or editing |
| Webstore checkout | the "Set as default" box when adding or editing an address |
| Admin: a shopper's or an account's Addresses page | the boxes "This address is my default billing address" / "This address is my default shipping address" in the add or edit panel |
| Admin: Create Order | the default box of the side you add (shipping or billing) |
| Commerce Portal | the two default boxes in the add / edit address window of Edit Order |
| Integrations | send the default flags when creating or updating an address; read an account's defaults with the "default billing / shipping address" calls |

## 3. Who can do it

| Who | Webstore | Admin can change it for them |
|---|---|---|
| Shopper without an account | Yes | Yes |
| Account Administrator | Yes (for the whole account) | Yes (for the whole account) |
| Account Manager / User / other role | No | No on their Addresses page (view only); yes on the account's own Addresses page |
| Guest | No choice: the address entered for shipping becomes their default shipping address, and the billing one their default billing address | No |

## 4. Step by step
**Webstore address book**: under an address, click **Set as Primary Shipping** (or **Set as Primary Billing**). You see "Primary Shipping Address changed." (or "Primary Billing Address changed.") and the Primary cards at the top change.

**Admin**: open the address, tick the box, click **Save**. You see "Record updated successfully." (or "Record created successfully." for a new address).

## 5. What is allowed and what is not
- There is only one default per side in each book. Choosing a new default automatically removes the old one.
- **A default cannot be switched off.** The box of an address that is already the default is ticked and locked, everywhere. To change it, make another address the default.
- A default address cannot be deleted.
- The **first** address is made the default automatically on the webstore (both sides from the address book, the side you are filling at checkout) and in the admin for a shopper without an account and in admin Create Order. On an account's admin Addresses page it is only the default if you tick the box.
- A one-time address at checkout ("Don't save this address for future use") never becomes a default, unless it is your very first address.
- Guests can end up with more than one default: their older addresses are never cleared.
- In the Commerce Portal, ticking a default on an address of a customer who belongs to an account does not remove the default from the account's other addresses, so the account can end up with two defaults.
- The integration call `v2/addresses` never removes older defaults.

## 6. Messages you may see

| Message | Where | When it appears | When it does not |
|---|---|---|---|
| "Primary Billing Address changed." | Webstore | the address is now the primary billing address — also after "Set as Primary Shipping" on an address that already was the primary billing address | |
| "Primary Shipping Address changed." | Webstore | the address is now primary shipping (and is not primary billing) | when it is also primary billing (see above) |
| "Failed to update address." | Webstore | the change failed | |
| "No records found." | Webstore address book | the book has no primary shipping (or billing) address | |
| "Record updated successfully." / "Failed to update record." | Admin | saved / failed | |
| "The requested data is not available." | API (read defaults) | the account has no default of that side, or does not exist | |

## 7. How it differs
- **By role** — section 3.
- **With or without an account** — with an account the default is shared by all users of the account; without, it is the shopper's own.
- **By country, store or setting** — no difference; defaults are not tied to a country or store.

## 8. What can be combined
- The same address can be default billing and default shipping at the same time. Choosing "Set as Primary Shipping" on the primary billing address makes it both.
- At checkout, "Same as Billing address" copies the default choice to the other side.

## 9. What it changes elsewhere
- Checkout preselects the new defaults the next time it loads, for every user of the account.
- Admin Create Order and the Commerce Portal preselect them too.
- The default address cannot be deleted until another address takes its place.

## 10. Quick answers
- **How do I remove the default from an address?** You can't directly; make another address the default.
- **Which API does "Set as Primary" call?** It reads the address ("WebStoreAccount / Get Address") and saves it back with the flag ("WebStoreAccount / Update Account Address").
- **Is there an API to read an account's default addresses?** Yes: `v2/accounts/{accountId}/default-billing-address` and `.../default-shipping-address`.
- **Why did I see "Primary Billing Address changed." after choosing shipping?** The address already was the primary billing address; the message checks billing first.

## 11. What could not be settled
- "Set as Primary" was not run live (it needs a signed-in shopper). The flag-moving rule is also recorded by the automation workflow suite on the development environment.

## 12. For developers
03 admin, 04 webstore, 05 Commerce Portal, 06 API, 07 functions, 08 database.
