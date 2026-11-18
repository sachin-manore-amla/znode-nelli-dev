# Shipping address suggestion (search your addresses at checkout)

Files in this folder: 01 functional · 03 admin · 04 webstore · 06 API · 07 functions · 08 database


## 1. What it is
A search box at webstore checkout, "Search For Shipping Address", that lets a shopper with many saved addresses find one by typing part of a name, street, city, postal code, phone and so on, and pick it as the shipping address.

Separately, the API has "search location" calls that search the **store's own addresses** (store locations), and an "update search address" call. No screen uses them.

## 2. Where
Webstore checkout and the quote page, shipping side only. Not in the admin or the Commerce Portal.

## 3. Who
| Who | Gets the search box |
|---|---|
| Signed-in shopper, when the store setting **and** the shopper's own setting "Enable Shipping Address Suggestion" are both on | yes |
| Everyone else (either setting off, guests) | no |
Account roles make no difference to the box itself.

## 4. Step by step
1. At checkout, under Shipping Address, type at least 3 characters in "Search For Shipping Address" (hint: "Location Name, City, Zip, etc.").
2. Matching saved addresses appear; click one to make it the shipping address. "No address matched your search" when nothing matches.
3. "Recipient Name" shows the name on the chosen address.

## 5. What is allowed and what is not
- Only the shopper's own saved addresses (or the account's, for account users) are searched; nothing is fetched from the server while typing.
- While the search box is on, the **Edit** button at checkout is not shown. "Add New" is still there for those allowed to add.
- The store setting alone is not enough: the shopper's own user setting must be on as well. The Knowledge Base article on store attributes ("Configuring Additional Store Attributes", Address Settings) says the store setting is enough; the article on user attributes ("Configuring Additional User Attributes", Address Setting) describes the user setting. Today both are required (04 §1.5).
- Only on the shipping address at checkout and on the quote page. The address book (list and Add / Edit form) and the billing address never show it.
- The Enable Centralized User Login setting makes no difference to the rule; with it on, the shopper's own setting is shared by all stores the shopper uses, and the admin user page says "The information shown on this page is same across stores."

## 6. Messages
| Message | When |
|---|---|
| "No address matched your search" | 3 or more characters typed and nothing matches |
| "Search term must be between 3 and 300 characters long." | API (v2 search location) with a term shorter than 3 or longer than 300 |
| "Portal Id can not be less than 1" | API search location with no valid store |

## 7. How it differs
By the two settings only. On the development environment the store setting is on for two stores (7 and 28) but no shopper has the user setting on, so nobody sees the box today.

## 8. What can be combined
The search box and the address drop-down work together: either can choose the address.

## 9. What it changes elsewhere
Choosing an address from the box is the same as choosing it in the drop-down: shipping options and prices refresh. Nothing is saved to the address book.

## 10. Quick answers
- **Does the search call an API?** No, it searches the list already on the page.
- **Where are the settings?** Store: **Stores > Stores**, edit the store, **Additional Attributes**, tab **Address Settings**, **Enable Shipping Address Suggestion**. Shopper: **Accounts & Users > Users**, edit the user, **Additional Attributes**, tab **Address Settings**, **Enable Shipping Address Suggestion** (not available for guest users). Both are Yes/No and No by default (03).
- **What do the "search location" APIs search?** The store's addresses (store locations), not shoppers' address books.

## 11. For developers
04 webstore, 06 API, 07 functions, 08 database. Store locations themselves belong to MOD-STORE-LOCATOR.
