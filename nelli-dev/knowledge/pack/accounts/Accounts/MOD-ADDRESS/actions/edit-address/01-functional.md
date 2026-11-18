# Edit an address

Files in this folder: 01 functional · 03 admin · 04 webstore · 05 Commerce Portal · 06 API · 07 functions · 08 database


---

## 1. What it is
Editing changes a saved address: the name on it, the street, city, state, postal code, country, phone, company, whether it is commercial or residential, and whether it is the default billing or shipping address. The address stays in the same address book: the shopper's own book, or the shared book of a B2B account.

In a few cases the product does not change the saved address but **saves a new one** with your changes (see section 5).

## 2. Where you do it

| Where | Menu or page |
|---|---|
| Admin: a shopper's address | Customers > Users > open the user > Addresses > Edit |
| Admin: an account's address | Customers > Accounts > open the account > Addresses > Edit |
| Admin: while creating an order or quote | Orders > Create Order > the Edit link next to the shipping or billing address |
| Admin: on an existing order | Manage Order (see change the address on an order) |
| Webstore: address book | My Account > Address Book > the pencil icon on an address |
| Webstore: checkout | Checkout > Shipping Address or Billing Address > Edit |
| Webstore: guest checkout | Checkout as a guest > edit the address you entered |
| Webstore: the account's own address | My Account > Account Information (account Administrators only) |
| Commerce Portal | Edit Order > Bill To (or Ship To) > edit |
| Integrations | the Znode APIs (file 06) |

## 3. Who can do it

| Who | Webstore address book | Webstore checkout | Admin can edit it on their Addresses page |
|---|---|---|---|
| Shopper without an account | Yes | Yes | Yes |
| Account Administrator | Yes (the account's shared address) | Yes | Yes (the account's shared address) |
| Account Manager | No (can only look) | No | No (the list is view only) |
| Account User | No | No | No |
| Any other role name in an account | No | No | No |
| Guest | n/a | Yes (their own checkout address) | No |
| Store staff impersonating a Manager or User on the webstore | — | Yes, after confirming a pop-up | — |

Other rules about who:
- On the admin **account's own Addresses page** there is no role rule: any admin staff member allowed to edit account addresses can do it.
- In admin **Create Order**, the address of a customer of any role can be edited. For Managers and Users a pop-up asks you to confirm first.
- In the **Commerce Portal**, anyone who can open the order can edit its customer's address; the customer's account role plays no part.
- Only account **Administrators** see My Account > Account Information; everyone else gets the "page not found" page.
- On the webstore, if a shopper types the address number of someone else's address into the page address, they get the "page not found" page.
- The API has an extra security setting that, when on, refuses webstore requests from anyone but the account's Administrator (account addresses) or the shopper themself (own addresses). It is **off on the development environment**. Admin and Commerce Portal edits of a shopper's own address are never checked by it.

## 4. Step by step

**Webstore address book**
1. My Account > Address Book, click the pencil on an address.
2. The form opens filled in. If the address is already your default billing or shipping address, that box is ticked and cannot be unticked.
3. Change what you need and click **Save Changes**. You see "Address updated successfully." and go back to the address book.

**Webstore checkout**
1. Click **Edit** under the shipping (or billing) address.
2. Change the address. "Same as Billing address" (or "Same as Shipping address") is ticked when the address is used for both.
3. Click **Save Changes**. There is no message; the address refreshes and shipping options update.

**Webstore Account Information** (Administrator)
1. My Account > Account Information. Account ID, External ID, the account phone and the account name are shown but cannot be changed.
2. Change the address fields and click **Save Changes**. You see "Record updated successfully.".

**Admin: a shopper's or an account's Addresses page**
1. Click **Edit** on a row. A side panel "Edit Address - …" opens.
2. Change the fields and click **Save**. The page reloads and shows "Record updated successfully.".

**Admin: Create Order** — click Edit next to the address (confirm the pop-up for a Manager or User), change it, click **Save**. You see "Address Saved Successfully." and the order uses the changed address. The default boxes are not shown here.

**Commerce Portal** — in Edit Order, open the edit form for the Bill To (or Ship To) address, change it, click **Save**.

## 5. What is allowed and what is not
- You cannot make an address stop being the default by editing it. Make another address the default instead (set default address).
- Ticking "default billing" (or "default shipping") while editing makes this address the default; the previous default stops being the default. For an account this applies to the whole account.
- On an **account** address, Commercial / Residential cannot be changed: the product keeps the value it had.
- Every field you save replaces the old value. A field that the screen or the integration does not send is **emptied**. For example, the Commerce Portal does not send the "Commercial" choice, the external ID or whether the address is active, so an edit there sets them to empty / not active / residential.
- The Commerce Portal also marks an address edited from **Ship To** as a shipping-only address, and one edited from **Bill To** as a billing-only address.
- The webstore saves a **new address** instead of changing the old one when:
 - you edit, at checkout, an address that is your default for both billing and shipping and untick "Same as Billing/Shipping"; the old address stays your default for both; the new address is added to your address book (not as a default) and is used for this order;
 - you are not in an account and edit, at checkout, an address used for both billing and shipping and untick "Same as …"; the new address holds your changes for one side, the old address stays as it was.
- In the admin order screens, editing an address that is used for both billing and shipping on an existing order splits it: the product saves a copy named "*name*_Copy" for the side you edited and the original keeps the other side.
- Addresses on placed orders are copies; editing the address book does not change them.
- The Commerce Portal Ship To edit form does not open today: the page asks for the address at a web address that does not exist on the server, so it shows an error message instead. The Bill To edit form opens normally.
- The Commerce Portal offers only the United States; an address in another country cannot be kept as it is when edited there.

## 6. Messages you may see

| Message | Where | When it appears | When it does not |
|---|---|---|---|
| "Address updated successfully." | Webstore address book | the change was saved | at checkout (no message there) |
| "Failed to update address." | Webstore address book and checkout | the save failed for any reason | on success |
| The field messages of adding ("First name is required.", "Postal/ZIP code is not valid.", …) | Webstore | same rules as adding (see add address) | |
| "Please confirm your Address." pop-up | Webstore | address checking is on for the store (and for the address book, also on for the address book) | checking off |
| "The shopper/customer belongs to the User (B2B) role. Would you still like to proceed with updating the address?" (and Manager) | Webstore checkout while staff impersonate | staff click Edit for a Manager or User | normal shopper sessions |
| "Record updated successfully." | Webstore Account Information | the save worked | |
| "Account information updated successfully." shown as a **red error** | Webstore Account Information | the save did not return an address | on success |
| "Address line 1 is required.", "Phone number is required.", "Country is required.", "State is required.", "City is required.", "Postal/ZIP code is required.", "Address Name cannot exceed 100 characters." | Webstore Account Information | the field is empty / too long | |
| "Record updated successfully." | Admin Users and Accounts | saved | |
| "Failed to update record." | Admin Users, Accounts and Create Order | anything went wrong, including a refusal; the server's own reason is not shown | on success |
| "Note : This address has not been saved for future use in the customer's address book" | Admin edit panel | the address is a one-time address | normal addresses |
| "The shopper/customer belongs to the “User(B2B)” role. Would you still like to proceed with updating the address?" (and Manager) | Admin Create Order | Edit for a Manager or User customer | Administrators and customers without an account |
| "Your Shipping Address is not a valid address. Please enter a valid address to continue." | Admin Create Order | the store's address checking feature is on and the address fails (US only) | feature off; non-US addresses |
| "Address Saved Successfully." | Admin Create Order | saved | |
| An error message with the web error text | Commerce Portal | loading or saving failed (always for Ship To edit today) | |
| "Access denied. You are not authorized to access this resource." | API | the security setting is on and the caller is not allowed | setting off (the development environment) |
| "The page cannot be displayed. Make sure you are authorized to view this page." | API (webstore update) | the address number does not exist | |
| "Combination of account code and addressId is not valid." | API (account update) | the account given has no addresses at all | |

## 7. How it differs
- **By role** — section 3.
- **Shopper with or without an account** — with an account, the webstore and the admin change the account's shared address and moving a default affects every user of the account; without, only the shopper's own book is affected.
- **By country** — the same country, state and postal-code rules as adding apply on each screen (add address, section 7). The server does not check the country, state or postal code on an edit.
- **By setting**
 - Store "Enable Address Validation" (and "Validate Addresses in Address Book Page" for the address book): the recommended-address pop-up also appears when you save an edit.
 - "Enable Shipping Address Suggestion", when it is on for the store **and** for the shopper: the Edit button at checkout is hidden.
 - Store feature "Address Validation": admin Create Order checks the changed address (US only).
 - The API security setting (section 3).

## 8. What can be combined
- One address can be both the default billing and the default shipping address; editing keeps both.
- Each book has one default billing and one default shipping address; a new default replaces the old one — except for guests, and except when an account address is edited from the Commerce Portal (then the account's other addresses keep their defaults, and the account can end up with two defaults).

## 9. What it changes elsewhere
- An edited account address changes at once for every user of the account: in their address book, at checkout, in the admin and in the Commerce Portal lists.
- At checkout the edited shipping address refreshes shipping options and prices.
- Each edit sends an "address updated" event and, where set up, a message to the connected ERP system; neither blocks the save.
- Placed orders keep the address they were placed with.

## 10. Quick answers
- **Which APIs does the admin call to edit an address?** "Customer / Update Customer Address" for a shopper without an account; "Account / Update Account Address" for an account's address (also from an Administrator's user page). The webstore calls "WebStoreAccount / Update Account Address" for everything (and "Account / Update Account Address" from Account Information). The Commerce Portal calls "Customer / Update Customer Address". Details in file 06.
- **Can a Manager edit the account's address on the webstore?** No. Only the Administrator. Staff impersonating a Manager can, after a confirmation.
- **Why did my edit create a new address?** You edited, at checkout, a default or both-sides address and unticked "Same as …" (section 5).
- **Why can't I untick "default"?** A default can only move to another address; it cannot be removed by editing.
- **Why did Commercial change to Residential after an edit in the Commerce Portal?** The Commerce Portal does not send that choice, so the saved address loses it.
- **Does editing an address change past orders?** No.

## 11. Knowledge base and product
| Knowledge base says | How it behaves |
|---|---|
| "A user can edit or add an address from the webstore only if they have the Admin role. In all other cases, the add and edit buttons are hidden." (Managing Account Addresses, KB 43000756871) | Matches for account users. Shoppers without an account can always edit. |
| Account addresses are inherited by all users of the account (KB 43000756871) | Matches: an edit shows for every user of the account. |

## 12. What could not be settled
- The checkout cases that save a new address were read from the code; they were not run live (they need a signed-in shopper).
- The Commerce Portal edit was read from the code; the save was not run live (it needs a real order).
- Screens were not checked in a browser in this run (sign-in is done by a person).

## 13. For developers
Technical detail: 03 admin, 04 webstore, 05 Commerce Portal, 06 API, 07 functions, 08 database.
