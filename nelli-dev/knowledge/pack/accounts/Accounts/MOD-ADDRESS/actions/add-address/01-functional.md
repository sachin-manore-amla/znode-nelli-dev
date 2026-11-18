# Add an address

Files in this folder: 01 functional · 03 admin · 04 webstore · 05 Commerce Portal · 06 API · 07 functions · 08 database

This page is for everyone: support, testers, business analysts, new joiners. It uses everyday words. Developers will find the exact code, screens and data in files 02 to 08.


---

## 1. What it is

An address is a name, street, city, state, postal code, country and phone number that can be used for billing or shipping. You can add addresses to a **shopper** (a registered user) or to a **B2B account** (a company). All users of an account share the account's addresses.

Each address can be marked as the **default billing** address, the **default shipping** address, or both. It can also be marked as usable for billing, for shipping, or both, and as commercial or residential.

## 2. Where you do it

| Where | Menu or page |
|---|---|
| Admin: a shopper's addresses | Customers > Users > open the user > Addresses > Add New |
| Admin: an account's addresses | Customers > Accounts > open the account > Addresses > Add New |
| Admin: while creating an order or quote | Orders > Create Order > pick the store and customer > Add New (next to the shipping or billing address) |
| Admin: a brand-new account | Customers > Accounts > Add (the first address is part of the account form) |
| Webstore: address book | My Account > Address Book > Add Address |
| Webstore: checkout | Checkout > Shipping Address or Billing Address > Add New (the form opens by itself if nothing is saved yet) |
| Webstore: guest checkout | Checkout as a guest > fill in the shipping address |
| Commerce Portal | Edit Order > the "+" next to Ship To or Bill To |
| Integrations | the Znode APIs (see file 06) |

My Account > Account Information on the webstore lets an account Administrator **change** the account's own address. It does not add a new one.

## 3. Who can do it

B2B accounts have three roles: **Administrator**, **Manager** and **User**. Shoppers without an account and guests have no account role.

| Who | Webstore address book | Webstore checkout: add a new address | Webstore checkout: pick another saved address | Admin can add one for them on their Addresses page |
|---|---|---|---|---|
| Shopper without an account | Yes | Yes | Yes | Yes |
| Account Administrator | Yes (added to the account) | Yes (added to the account) | Yes | Yes (added to the account) |
| Account Manager | No (can only look) | No | Yes | No (no Add New button) |
| Account User | No (can only look) | No | No (the list is locked) | No (no Add New button) |
| Any other role name in an account | No | No | No | No |
| Guest | n/a | Yes | n/a | No (view only) |
| Store staff impersonating a Manager or User on the webstore | — | Yes, after confirming a pop-up | Yes, after confirming a pop-up | — |

Other rules about who:
- In the admin, the **account's own Addresses page** has no role rule: any admin staff member with permission to add account addresses can add one.
- In the admin **Create Order** screen, an address can be added for a customer of any role. For Managers and Users a pop-up first asks you to confirm.
- In the Commerce Portal, anyone who can open the order can add an address, as long as the order has a customer.
- Admin staff need the matching admin permission (for example "create address" for customers or accounts). Staff with the Admin role can do everything. Account roles (Administrator, Manager, User) cannot sign in to the admin at all.
- When the API's extra security setting is turned on, the API itself also refuses webstore requests from anyone but the account's Administrator (for account addresses) or the shopper themself (for personal addresses). When it is off, only the screens enforce the role rules.

## 4. Step by step

**Webstore address book**
1. Go to My Account > Address Book and click **Add Address**.
2. For your first address, both "Set as default shipping address" and "Set as default billing address" are already ticked and cannot be unticked.
3. Fill in the form. Choose the country first: the state list follows the country.
4. Click **Save Changes**. You see "Address created successfully." and return to the address book.

**Webstore checkout**
1. Click **Add New** under Shipping Address (or Billing Address). If you have no saved address, the form is already open.
2. Choose whether the address is also your billing address ("Same as Billing address"), whether it becomes your default, and whether to keep it ("Don't save this address for future use").
3. Click **Save Changes**. There is no success message; the new address is selected and shipping options refresh.

**Admin: a shopper's Addresses page**
1. Open the user, then Addresses, then **Add New**. A side panel opens.
2. Fill in the form and click **Save**. The page reloads and shows "Record created successfully."

**Admin: an account's Addresses page** — the same, from the account.

**Admin: Create Order** — click **Add New** next to the shipping or billing address, fill in the pop-up, click **Save**. You see "Address Saved Successfully." and the order uses the new address.

**Commerce Portal** — in Edit Order click "+" next to Ship To or Bill To, fill in the pop-up, click **Save**.

## 5. What is allowed and what is not

- Only the account's **Administrator** can add or change the account's addresses on the webstore. Managers and Users can see them but not change them.
- A Manager can choose another saved account address at checkout. A User cannot; the choice is locked to the default.
- A shopper in an account never gets a personal address book on the webstore or in the admin. Every address they add goes to the account and is shared with the whole account.
- The Commerce Portal is the exception: it saves a new address to the **shopper**, even when the shopper belongs to an account. Such an address is not shown in the account's list.
- An address saved with "Don't save this address for future use" is used for that order only. It does not appear in any address book.
- Guests cannot be given addresses from the admin.
- An account shopper cannot receive personal addresses through the customer-address import.
- The Commerce Portal offers only the United States.

## 6. Messages you may see

| Message | Where | When it appears | When it does not |
|---|---|---|---|
| "Address created successfully." | Webstore address book | the address was saved | at checkout (no message there) |
| "Failed to update address." | Webstore address book and checkout | the save failed for any reason, including a refusal by the API | on success |
| "Postal/ZIP code is not valid." | Webstore | on Save, when the postal code does not match the country's pattern | while typing or when leaving the field; it clears as soon as you change the code |
| "Postal/ZIP code is required." / "Postal/ZIP code cannot be longer than 10 characters." | Webstore | empty / more than 10 characters | |
| "First name is required.", "Last name is required.", "Phone number is required.", "Street address is required.", "City is required.", "Display name is required." | Webstore | the field is empty or only spaces, when you leave it or click Save | Display name is not asked of guests |
| "Phone Number can not exceed 30 characters." | Webstore | more than 30 characters | |
| "Email is required." / "Please enter a valid email address." | Webstore guest checkout | e-mail empty or badly formed | logged-in shoppers (no e-mail field) |
| "Please add a shipping address before saving the billing address." | Webstore guest checkout | a guest saves the billing address first | once a shipping address exists |
| "Please confirm your Address." pop-up, with "Use recommended address" and "Keep the entered address" | Webstore | address checking is turned on for the store (and, for the address book, also for the address book) and the address needs confirming | checking is off; or a US address matches exactly |
| "No validated address was found. Please review the address again, or continue with the existing address if it is correct." | Webstore pop-up | address checking is on and no suggestion was found — this always happens for addresses outside the US | |
| "The shopper/customer belongs to the User (B2B) role. Would you still like to proceed with updating the address?" (and the Manager version) | Webstore checkout while store staff impersonate | staff click Add New or Edit for a Manager or User | normal shopper sessions |
| "Record created successfully." | Admin Users and Accounts | the address was saved | |
| "Failed to create." | Admin Users and Accounts | the save failed (on the account page this covers every failure, including a refusal) | |
| "Default Billing and Shipping Addresses must be selected for all New Customers." | Admin Users | only if the API reports invalid data; today's API does not do this for default flags | normal saves |
| "Postal code is not valid." | Admin | when you leave the postal code field, for **United States and India only** | every other country, including Canada |
| "Address Name is required.", "First Name is required.", "Last Name is required.", "Address Line 1 is required.", "Country is Required.", "State/Province/Region is required.", "City is required.", "Postal Code is required.", "Phone Number is required." | Admin | the field is empty | |
| "The shopper/customer belongs to the “Manager(B2B)” role. Would you still like to proceed with updating the address?" (and the User version) | Admin Create Order | adding from the drop-down for a Manager or User customer | Administrators and shoppers without an account; the first-address Add New |
| "Your Shipping Address is not a valid address. Please enter a valid address to continue." | Admin Create Order | the store's address checking feature is on and the address fails the check | feature off; addresses outside the US always pass |
| "Address Saved Successfully." | Admin Create Order | saved | |
| "Failed to update record." | Admin Create Order | anything in the save went wrong (for example the store could not be read) | on success |
| "Postal code is invalid" | Commerce Portal | the postal code has anything other than digits and hyphens | |
| "Please enter valid Phone Number" | Commerce Portal | anything other than digits, "+" and "-", or more than 20 characters | |
| "Access denied. You are not authorized to access this resource." | API | the API's extra security setting is on and the caller is not allowed (see section 3) | setting off |

## 7. How it differs

- **By role** — see the table in section 3.
- **Shopper with or without an account** — without an account, the address goes to the shopper. With an account, the admin and webstore put it in the account's shared list; the Commerce Portal and some APIs put it on the shopper.
- **By country**
 - Countries offered are the ones switched on for the store, with the store's default country first and preselected. On the development environment every store has the United States as default and also offers Canada; some add United Arab Emirates, Afghanistan or Germany.
 - The state list follows the country and shows only active states. Canada has 13 provinces and territories.
 - On the webstore, the postal code must match the country: US `12345` or `12345-6789`; **Canada `A1A 1A1` with a space** (`K1A0B1` is refused); India six digits not starting with 0; UK like `SW1A 1AA`; other countries a general pattern.
 - In the admin, only US and India postal codes are checked; Canada is not checked.
 - Address checking (the US postal service) only checks US addresses. Addresses in other countries are accepted as they are.
 - If a country has no states, the webstore saves the address without a state, but the admin cannot save it (the state is required).
- **By setting**
 - "Enable Address Validation" (store): turns on address checking at webstore checkout. Off by default; off on the development environment.
 - "Validate Addresses in Address Book Page" (store): also checks addresses added in the address book. Needs the first setting.
 - "Allow User to Override Address" (store): lets the shopper keep what they typed instead of the suggestion.
 - The store feature "Address Validation" turns on the check in admin Create Order.
 - "Enable Shipping Address Suggestion", when it is on for the store **and** for the shopper: shows a search box over the saved addresses at checkout and hides the Edit button there.
 - The API's security setting (explained in section 3).

## 8. What can be combined

- One address can be both the default billing and the default shipping address.
- Each address book has **one** default billing and **one** default shipping address. When you add a new default, the old one stops being the default automatically. Guests are the exception: their old defaults are not cleared.
- At checkout, "Same as Billing address" makes the new address both the shipping and the billing address.
- "Don't save this address for future use" cancels "Set as default", unless it is your very first address.
- The same address is never in both the account list and a shopper's list through the screens.

## 9. What it changes elsewhere

- An address added to an account appears straight away in the address book and at checkout for **every user of that account**, and in the admin on each of those users' Addresses page.
- A new default for an account becomes the default for all of the account's users (and the old default stops being the default for all of them).
- At checkout, a new shipping address refreshes the shipping options and prices. A new billing address updates the order's billing details.
- In admin Create Order, the new address is applied to the order and the totals and shipping are recalculated.
- Each new address sends a "created" event and, where set up, a message to the connected ERP system. These never block the save.
- Tax is calculated later from the order's addresses; adding an address does not calculate tax.
- For a guest, the guest record is created the moment the address is saved, before the order is placed (this matches the knowledge base).

## 10. Quick answers

- **Can I add an address for a user who belongs to an account?** On the webstore, only if that user is the account's Administrator, and the address goes to the **account** (shared by all its users). In the admin, only on the page of a user whose account role is Administrator, and it also goes to the account; for Managers and Users there is no Add New button — add it on the account's own Addresses page instead. In admin Create Order you can add one for any role (Managers and Users need a confirmation) and it goes to the account. The Commerce Portal and some APIs save it on the user personally, where the account's screens do not show it.
- **Which APIs does the admin call, and which does the webstore call?** Admin: "Customer / Create Customer Address" for a shopper without an account, and "Account / Create Account Address" for accounts (and for account users). Webstore: "WebStoreAccount / Create Account Address" for everything, which saves to the account when the shopper has one and to the shopper otherwise. Commerce Portal: "Customer / Create Customer Address". Full list in file 06.
- **Which message appears if the postal code is wrong for Canada?** Webstore: "Postal/ZIP code is not valid." when you click Save (Canada needs `A1A 1A1` with a space). Admin: none — Canadian postal codes are not checked, only required. Commerce Portal: Canada cannot be chosen. The API itself does not check postal codes.
- **Can a B2B User role add an address, or only an Administrator?** Only the Administrator on the webstore. Users and Managers can see the account's addresses but not add them. Only an admin, in Create Order, can add one on a User's behalf (after a confirmation).
- **If I add an address to an account, where does it show up?** In every account user's address book and checkout address lists on the webstore, on each user's Addresses page in the admin, and in the Commerce Portal Ship To / Bill To lists for that account's orders.
- **What happens to default billing and shipping?** The first address becomes the default automatically on the webstore and for admin shoppers without an account; on the account pages it is only the default if you tick it. Every later address is default only if ticked, and the previous default then stops being the default. Guests can end up with more than one default.
- **Which countries and states are offered, and where does the list come from?** The countries switched on for the store, default first (on the development environment: US default, plus Canada and a few others per store); the states of that country that are active. The Commerce Portal offers only the United States with a fixed list of US states.
- **Does the product check that an address is real?** Only when a store turns on address validation, and only for US addresses.
- **Is the address added to the account or to the user?** Admin and webstore: to the account when the user has one. Commerce Portal and the API "webstore-accounts / addresses" (v2): always to the user.

## 11. What the knowledge base says, and how the product behaves

| Knowledge base says | How it behaves |
|---|---|
| "A user can edit or add an address from the webstore only if they have the Admin role. In all other cases, the add and edit buttons are hidden." (Managing Account Addresses, KB 43000756871) | Matches. Only the account role Administrator sees them. |
| Manager: "Ability to modify the shipping address during checkout" | A Manager can choose another saved account address but cannot add or edit one. |
| User: "Place orders using the default account address only" / "Cannot modify the shipping address at checkout" | Matches for normal sessions. When store staff impersonate a User, they can change it after a confirmation. |
| "Navigate to: Customer > Users > Addresses tab. The administrator can add addresses for users from this section." (KB 43000756975) | True for users without an account and for account Administrators — and for the latter the address goes to the account. Managers and Users get a view-only list. |
| Account addresses are inherited by all users of the account (KB 43000756871) | Matches. |
| "The Address Details entered at the time of Account creation become the default Address for the Account." | Matches: both default boxes are ticked and locked when creating an account. |
| USPS address validation "Only United States addresses are validated. Non-U.S. addresses are saved without validation." (KB 43000786012) | Matches for the US postal service check. On the webstore, though, a non-US address with validation on shows the "No validated address was found" pop-up first; "Keep the entered address" is always offered there, and choosing it saves the address unchanged. |
| "Validate Addresses in Address Book Page … only applicable when the Enable Address Validation is set to Yes" | Matches. |
| Release note: "The 'Enable Address Validation' setting under Store settings has been deprecated." | The webstore still reads the store setting "Enable Address Validation" today; the older store feature of the same name is what the admin Create Order screen reads. |
| "The guest user record is created immediately when the guest address is saved during the checkout process, before the order is placed." | Matches. |

## 12. What could not be settled
- Address checking by the UPS, FedEx, AvaTax and Vertex plugins is covered in address-validation.
- The API's extra security setting is **off on the development environment** (read on 1 October 2026), so on the development environment only the screens enforce the role rules. Other environments can differ.
- What the screens show if the API returns an empty success; not reproducible without a write.
- The Quote screens were not traced separately; they use the same order screens and save the same way.
- In admin Create Order, which store number the pop-up sends with the new address. If it were empty the save would end in "Failed to update record."; this needs a browser to confirm.
