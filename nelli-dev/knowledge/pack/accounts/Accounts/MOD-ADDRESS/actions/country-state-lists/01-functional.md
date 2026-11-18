# Country and state lists on the address forms

Files in this folder: 01 functional · 03 admin · 04 webstore · 05 Commerce Portal · 06 API · 07 functions · 08 database


## 1. What it is
Every address form has a Country list and a State list. They decide which countries and states can be picked.

## 2. Where
All address forms: webstore address book, checkout and Account Information; admin Users, Accounts and order screens; Commerce Portal Edit Order.

## 3. Who
Everyone who can open the form; roles make no difference (on Account Information only Administrators see the countries, because only they can edit there).

## 4. What you see
- **Countries**: the countries set up for the store **and** active in the system, with the store's default country first and preselected.
- **States**: the active states of the chosen country, alphabetical. Changing the country reloads the states.
- **Commerce Portal**: always only "United States" and a fixed list of US states.

## 5. What is allowed and what is not
- A country that is not set up for the store cannot be picked on that store.
- If a country has no states, the webstore saves the address without a state, but the admin cannot save it ("State/Province/Region is required.").
- The server does not check the country or state when an address is saved: through the APIs any text is accepted. Only the customer-address import checks them.
- What is saved is the short code (for example "US", "NY").

## 6. Messages
| Message | Where | When |
|---|---|---|
| "Country is Required." / "State/Province/Region is required." | Admin | nothing chosen, or the country has no states |
| "Country is required." / "State is required." | Webstore Account Information | not chosen |
| "Postal/ZIP code is not valid." / "Postal code is not valid." | Webstore / Admin | the postal code does not fit the chosen country (webstore: US, CA, IN, GB and a general pattern; admin: US and IN only) |

## 7. How it differs
- **By store** — each store has its own country list and default.
- **On the development environment** — every store's default is the United States; all offer Canada; several add the United Arab Emirates and Afghanistan; some Germany.
- **Commerce Portal** — US only, whatever the store says.

## 8. What can be combined
—

## 9. What it changes elsewhere
Changing which countries a store offers (store setup, MOD-GEO) changes these lists for new forms at once; saved addresses keep what they have.

## 10. Quick answers
- **Why can't I pick Canada in the Commerce Portal?** Its list is fixed to the United States.
- **Where does the webstore country list come from?** "PortalCountry / Get Associated Country List" for the store.
- **Where do the states come from?** "State / List", filtered by country and active.

## 11. For developers
03 admin, 04 webstore, 05 Commerce Portal, 06 API, 07 functions, 08 database. The country and state masters are MOD-GEO.
