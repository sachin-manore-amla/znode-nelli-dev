# Address validation (recommended address)

Files in this folder: 01 functional · 03 admin · 04 webstore · 06 API · 07 functions · 08 database


## 1. What it is
When it is switched on, the product checks a new or changed address with the US Postal Service before saving it. On the webstore the shopper sees "Please confirm your Address." with a suggested address; in the admin order screens a wrong address is refused with a message.

Only **United States** addresses are checked. Addresses in every other country are accepted as typed.

## 2. Where it happens
| Where | When |
|---|---|
| Webstore checkout (shipping or billing, signed-in or guest) | on Save, when the store setting "Enable Address Validation" is on |
| Webstore address book (add or edit) | on Save, when "Enable Address Validation" **and** "Validate Addresses in Address Book Page" are on |
| Admin Create Order, Create Quote, Manage Order (adding or editing the customer's address) | on Save, when the store feature "Address Validation" is on |
| Admin Users / Accounts address pages, Account Information, Commerce Portal | never |

## 3. Who
Everyone who saves an address on those screens; role, account and user type make no difference.

## 4. Step by step (webstore)
1. Fill in the address and click **Save Changes**.
2. If the US Postal Service suggests something different, a pop-up shows what you typed and the "Recommended address".
3. Click **Use recommended address** to save the suggestion, or **Keep the entered address** (when offered) to save what you typed. Closing the pop-up saves nothing.
4. If the address matches exactly, it is saved straight away with no pop-up.

## 5. What is allowed and what is not
- "Keep the entered address" is offered only when the store setting "Allow User to Override Address" is on — or when there is no suggestion at all. Otherwise you must take the suggestion (or close and fix the address).
- **Every non-US address shows the pop-up with "No validated address was found…"** on the webstore when validation is on; "Keep the entered address" then saves it unchanged.
- If the validation service cannot be reached or is not set up for the store, the webstore shows the same "No validated address was found" pop-up.
- In the admin there is no suggestion: a wrong US address is refused and must be corrected by hand.
- Saving through the APIs directly never validates.
- Only the USPS plugin provides address validation. UPS checks US addresses only while calculating shipping rates (an invalid one gets no UPS rate); FedEx, Avalara and Vertex do not validate addresses.

## 6. Messages you may see
| Message | Where | When it appears | When it does not |
|---|---|---|---|
| "Please confirm your Address." | Webstore pop-up | validation is on and the address differs from the suggestion, or there is no suggestion | exact match; validation off |
| "No validated address was found. Please review the address again, or continue with the existing address if it is correct." | Webstore pop-up | no suggestion: non-US address, USPS found nothing, or the service failed | a suggestion exists |
| "Your Shipping Address is not a valid address. Please enter a valid address to continue." | Admin order pop-up | the store feature is on and USPS says the address (ZIP, state or city) is wrong without a reason | feature off; non-US addresses |
| "Please enter valid address." / "Please enter Street address" / "Address1 is limited to a maximum of 100 characters." (and the Address2, City, State code, Postal code variants) | Admin order pop-up | USPS did not find the address / no street / a field is too long | |
| "Failed to update record." | Admin order pop-up | the validation call itself failed | |

## 7. How it differs
- **By country** — US only; others always pass.
- **By setting** — section 2 and section 5; all settings are per store.
- **the development environment today** — all webstore switches are off, the admin feature is mapped to no store, and the Shipping Manager has no store set up for USPS validation, so no validation happens on the development environment.

## 8. What can be combined
"Validate Addresses in Address Book Page" only works together with "Enable Address Validation".

## 9. What it changes elsewhere
Using the recommended address saves the USPS street, city, state, ZIP and country instead of what was typed. Nothing else changes; shipping and tax are calculated later from the saved address.

## 10. Quick answers
- **Does Znode validate Canadian addresses?** No. On the webstore a Canadian address gets the "No validated address was found" pop-up (when validation is on) and can be kept as typed.
- **Which API does the webstore call?** Shipping Manager "shipping-gateway / address / validate", which calls the USPS plugin.
- **Which API does the admin call?** "Shipping / Is Shipping Address Valid".
- **Can UPS or FedEx validate addresses?** Not for saving addresses.
- **Why does every address show the pop-up?** The store's validation is on but the USPS validation is not configured for that store, or the address is not in the US.

## 11. What could not be settled
- A real USPS suggestion could not be produced live: on the development environment no store has the USPS validation configuration mapped (the automation suite adds it only while its own tests run).
- "Shipping / Is Shipping Address Valid" answers 500 on the development environment for every address; the exact error inside was not visible.

## 12. For developers
03 admin, 04 webstore, 06 API, 07 functions, 08 database. Not available in the Commerce Portal.
