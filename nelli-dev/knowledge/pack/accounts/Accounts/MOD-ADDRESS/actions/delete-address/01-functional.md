# Delete an address

Files in this folder: 01 functional · 03 admin · 04 webstore · 06 API · 07 functions · 08 database


---

## 1. What it is
Deleting takes an address out of an address book: a shopper's own book or the shared book of a B2B account. The address disappears from the address book, from checkout and from the admin lists. Orders already placed with it keep their copy of the address.

Behind the scenes the address itself is kept but no longer belongs to anyone; only one integration call removes the address completely (section 5).

## 2. Where you do it

| Where | Menu or page |
|---|---|
| Admin: a shopper's addresses | Customers > Users > open the user > Addresses > the delete icon on a row, or tick rows and choose Delete |
| Admin: an account's addresses | Customers > Accounts > open the account > Addresses > the delete icon, or tick rows and choose Delete |
| Webstore | My Account > Address Book > the trash icon on an address, or open the address (pencil) and click "Delete this address" |
| Integrations | the Znode APIs (file 06) |

Not available at webstore checkout, for guests, in admin Create Order or Manage Order, or in the Commerce Portal.

## 3. Who can do it

| Who | Webstore | Admin can delete it on their Addresses page |
|---|---|---|
| Shopper without an account | Yes | Yes |
| Account Administrator | Yes (removes it from the account for everyone) | Yes (removes it from the account) |
| Account Manager | No | No (view only) |
| Account User | No | No |
| Any other role name in an account | No | No |
| Guest | No | No |

- On the admin account's own Addresses page there is no role rule: any admin staff member allowed to delete account addresses can do it.
- The API itself never checks who is asking on a delete; only the screens decide.

## 4. Step by step
**Webstore**: My Account > Address Book > click the trash icon on an address that is not a primary address. You see "Address deleted successfully." and the list refreshes. From the edit page, "Delete this address" does the same and takes you back to the address book.

**Admin**: open the Addresses tab, click the delete icon on a row and confirm "Are you sure, you want to delete this record?", or tick several rows, choose Delete and confirm "Are you sure you want to delete the selected record(s)?". You see "Record deleted successfully.".

## 5. What is allowed and what is not
- **A default (primary) billing or shipping address cannot be deleted.** Make another address the default first. On the webstore the trash icon is not even shown on a primary address.
- If you select several addresses in the admin and one of them is a default, the others **are deleted anyway**, and you see the error message.
- Deleting from an account removes the address for every user of the account.
- One integration call (`v2/addresses-bulk`) removes the address row itself; it does not check defaults and refuses addresses that still belong to a shopper, account, store, warehouse, vendor or price list.
- Deleting never changes orders already placed.

## 6. Messages you may see

| Message | Where | When it appears | When it does not |
|---|---|---|---|
| "Address deleted successfully." | Webstore | deleted | |
| "Default addresses can not be deleted. Set some other address as your default address and then try again." | Webstore (edit page) | the address is the default for both billing and shipping | other addresses |
| "Default shipping addresses can not be deleted. Set some other address as your default shipping address and then try again." / the billing version | Webstore (edit page) | the address is the default shipping (or billing) address | |
| the text "Address.errorDeleteAddress" (a message key with no text) | Webstore | the delete failed (for example the address is not yours) | on success |
| "Record deleted successfully." | Admin | deleted | |
| "Default shipping/billing address can not be deleted. Set some other address as default shipping/billing address and then try again." | Admin Users page | **any** error from the server, not only a default address | success, or nothing deleted |
| "Failed to delete the selected record." | Admin Users page | the server deleted nothing | |
| "Default billing address or default shipping address could not be deleted. Set some other address as the default billing address or the default shipping address and then try again." | Admin Accounts page | **any** failure, including nothing deleted | success |
| "Failed to delete the record." | Admin | no row was selected | |
| "Default billing or shipping address cannot be deleted." / "Is Default Billing or is Default Shipping can not be deleted." / "Default Billing or Default Shipping can not be deleted." | API | a default address was in the request | |
| "Failed to delete Address due to associations." | API (bulk) | the address still belongs to a shopper | |

## 7. How it differs
- **By role** — section 3.
- **With or without an account** — with an account the webstore and admin remove the address from the account's shared book; without, from the shopper's own book.
- **By country, setting or store** — no difference: delete reads no setting and no country.

## 8. What can be combined
- Several addresses can be deleted at once in the admin and through the integration calls; the webstore deletes one at a time.

## 9. What it changes elsewhere
- The address disappears at once from the address book, checkout drop-downs, the admin lists and the Commerce Portal Ship To / Bill To lists (for an account: for every user of the account).
- An "address deleted" event is sent for each address removed.
- Placed orders are not changed.

## 10. Quick answers
- **Why can't I delete this address?** It is a primary (default) address. Set another address as primary first.
- **Which API does the webstore call?** "Account / Delete Account Address" for account users, "WebStoreAccount / Delete Address" for shoppers without an account.
- **Which API does the admin call?** "Customer / Delete Customer Address" for a shopper without an account; "Account / Delete Account Address" for an account's addresses and for an Administrator's user page.
- **Is the address gone from the database?** No, only its link to the book. Only the v2 bulk call removes the row.
- **Can a Manager delete an account address?** No.

## 11. What could not be settled
- The deletes themselves were not run on the development environment: the environment holds every DELETE call for a person's approval, and the POST deletes were run only with ids that do not exist.
- Whether the admin row link with the double slash (account Administrator's user page) reaches the delete action needs a browser check.
- The exact text next-intl shows for the missing webstore message was read from the library's default, not seen on screen.

## 12. For developers
03 admin, 04 webstore, 06 API, 07 functions, 08 database.
