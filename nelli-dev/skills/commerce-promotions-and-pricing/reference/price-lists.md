# Price lists
What this answers: how price lists work, how Znode picks the price, dates, tiers, associations, import and API.
Sources: KB Configuring a Price List, Managing Price Lists, Znode Pricing Approaches (read in full, 80); product source for resolution order (95).

## Admin
Menu: **OMS > Pricing Lists**. Grid: Code, Price List Name, Currency, Currency Culture, Activation Date, Expiration Date, Action (Edit, Copy, Delete). Buttons: Add New, search by Code or Name.
Edit screen tabs: **Associated Products** (SKU, Product Name, Retail Price, Sales Price, Activation Date, Expiration Date), **Associated Stores**, **Associated Profiles**, **Associated Users**, **Associated Accounts**. A list need not price every SKU: small lists are how sale and special pricing work.
Fields: Code (unique, used by imports), Name, Currency, Currency Culture (formatting; the store currency settings control display), Activation/Expiration Date.
Import: **Select Template**, Browse a `.csv`, Import. Only `.csv` is accepted; file size and row limits are not published. See `config-import-export` for error handling.
Delete is permanent; a list can be copied. Expired lists are ignored.

## Price types per SKU
| Type | Rule |
|---|---|
| Tier price | Quantity-based price; wins when the ordered quantity matches a tier |
| Sale price | Overrides retail on product pages |
| Retail price | Default |

## Which list applies (resolution)
1. User price lists, if any.
2. The user's account price lists (only the user's own account, never the parent).
3. The user's profile price lists.
4. The store's price lists.
Within a level: sort by precedence number (lowest first); skip a list outside its dates; look the SKU up in the list; skip a price record outside its own dates; if not found, move to the next list, then the next level. The KB pricing article does not state this order ("not stated, see Pricing Guide"); the order above is verified in the product source.
Store and store-profile associations are also editable at Stores > Manage > Price Lists (store tab and profile tab), including precedence.

## Behaviour to know
- Two date ranges: list and record. A live list can contain an expired record.
- Changing a price does not change orders already placed (prices are stored at placement).
- Publishing: price data reaches the storefront through publish/search index refresh; after bulk price changes publish the catalog or the store as your process requires (see `commerce-catalog`).
- Currency: a list has one currency; a store prices in its store currency, so associate lists of the right currency.
- Promotional "Amount/Percent Off Displayed Product Price" promotions change the displayed price after list resolution (see promotions reference).
- Limits (lists per store, SKUs per list) are not published.

## API
Price list and SKU price operations (create/get/update/delete list, copy, SKU prices, tier prices, associations of stores, profiles, accounts, users with precedence, export) exist in the Core API v2 and the older v1 families; look them up with `nd_query_spec.py` and prefer v2 (`api-catalog`). Precedence is set per association.

## Customization routes
| Need | Route |
|---|---|
| ERP-owned prices | Scheduled import or API sync of price lists; unit price cannot be overridden at calculate time |
| Per-customer price list assignment from your system | Association API calls (account, user, profile) |
| Price visible only after login | Store setting (see `config-store`) |
