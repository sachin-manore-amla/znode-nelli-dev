# View the address book

Files in this folder: 01 functional · 03 admin · 04 webstore · 05 Commerce Portal · 06 API · 07 functions · 08 database


## 1. What it is
The address book is the list of saved addresses of a shopper, or of a B2B account (shared by all its users), with the primary (default) billing and shipping addresses marked.

## 2. Where you see it
| Where | Page |
|---|---|
| Webstore | My Account > Address Book |
| Admin | Customers > Users > open the user > Addresses; Customers > Accounts > open the account > Addresses |
| Admin order screens | the shipping and billing drop-downs of Create Order and Manage Order |
| Commerce Portal | the Ship To and Bill To drop-downs of Edit Order (there is no address book page) |
| Integrations | the address list calls (file 06) |

## 3. Who sees what
| Who | What the list shows | Can change it |
|---|---|---|
| Shopper without an account | their own addresses | yes |
| Account Administrator | the account's addresses | yes |
| Account Manager / User / other role | the account's addresses | no (view only, on the webstore and in the admin) |
| Guest | no address book | — |
| Admin staff | any user's or account's list | depends on the customer (as above) and on their admin permissions |

A shopper who belongs to an account never sees a personal address book; any address saved on them personally (for example from the Commerce Portal or some integrations) is not listed anywhere on the screens.

## 4. What the webstore page shows
- **Primary Shipping** and **Primary Billing** at the top ("No records found." when there is none).
- **All Addresses**: one card each, with the address name, the person's name, company, street, "city, state, country, postal code" (state and country as short codes, e.g. "NY, US") and the phone.
- For those allowed: Add Address, the pencil (edit), the trash (delete, only on non-primary addresses) and "Set as Primary Shipping / Billing".
- All addresses on one page, no paging.

## 5. Rules
- Which list you get depends only on whether the shopper belongs to an account.
- The admin list shows the newest address first; the webstore shows them in the order they are stored.
- The webstore list is refused by the server if it would contain another shopper's address.
- With the API's security setting on, only the shopper themself (or a member of the account) can read the list from the webstore; it is off on the development environment.

## 6. Messages
| Message | Where | When |
|---|---|---|
| "No records found." | Webstore | no primary address of that side |
| "Note: The information shown on this page is same across all stores. Unless an account is associated with a selected store." | Admin user Addresses | the global setting "Allow Global User Creation" is on |
| "The page cannot be displayed. Make sure you are authorized to view this page." | API | the user list would include another user's address |
| "Account Code is invalid" / "Addresses are not associated with respective username." / "Please check user name." | API (v2) | unknown account code / user has no addresses / unknown user name |

## 7. How it differs
By role and account only (section 3). Country, store and settings do not change the list (except the admin note above).

## 8. What can be combined
—

## 9. What it changes elsewhere
Nothing; viewing writes nothing.

## 10. Quick answers
- **Which API does the webstore call for the address book?** "Account / Address List" for account users, "WebStoreAccount / Get User Address List" otherwise.
- **Which API does the admin call?** "Customer / Address List" for a user without an account, "Account / Address List" for accounts and account users.
- **Can a Manager see the account's addresses?** Yes, but cannot change them.
- **Why doesn't an address I added for an account user show up?** It was saved on the user personally (Commerce Portal or a v2 user call); screens list only the account's addresses for account users.

## 11. For developers
03 admin, 04 webstore, 05 Commerce Portal, 06 API, 07 functions, 08 database.
