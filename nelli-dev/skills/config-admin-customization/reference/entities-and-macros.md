# Supported entities and macros
Answers: which entity screens accept a custom section, which macros each offers, and how macro values reach your page.
Tags: [S] product source, [KB] KB read in full.

## Entities (Entity Type dropdown)
Same list in the KB and the product. [KB][S]

| Entity Type | Screen the section is added to | Macros (besides the five common ones) |
|---|---|---|
| Stores | Stores > Manage Store side panel | `#StoreCode#`, `#PortalID#` |
| B Stores | B Store manage side panel | none listed |
| Sales Rep | Sales rep manage panel | `#AdminUserID#` |
| Store Location | Store locator manage panel | `#StoreLocationCode#`, `#EntityID#` |
| Users | Customer/user manage panel | `#AdminUserID#` |
| Accounts | Account manage panel | `#AccountID#` |
| Guest Users | Guest user manage panel | `#GuestUserID#` |
| User Profile | Profile manage panel | `#ProfileID#` |
| Pricing Engine | Price list panel (for example Edit Pricing) | `#PriceListID#` |
| Inventory | Inventory panel | `#InventoryID#` |
| Warehouse | Warehouse panel | `#WarehouseID#` |
| Vendors | Vendor screen | `#PimVendorID#` |
| Products | PIM product side panel | `#ProductID#` |
| Category | PIM category panel | `#CategoryID#` |
| Brands | Brand panel | `#BrandID#` |
| Add-on Groups | Add-on group panel | `#PimAddonGroupID#` |
| Promotions and Coupons | Promotion panel | `#PromotionID#` |
| Product Highlights | Highlight panel | `#HighlightID#`, `#LocaleID#`, `#HighlightCode#` |
| Site Search | Search configuration panel | none |
| Power BI Reports | Power BI page | `#ReportType#` |

The panels were confirmed in the product source for Stores, B Stores, Accounts, Products, Category, Vendors, Add-on Groups, Brands, Promotions, Highlights, Site Search, Power BI, Profiles, Inventory, Pricing, Warehouse, Store Locator and Users. Sales Rep and Guest Users share the user panels; not confirmed one by one [I]. Some KB text says "Some entities may not be available in all releases". [S][KB]

Common macros on every entity: `#userid#`, `#username#`, `#useremailaddress#`, `#roleid#`, `#rolename#` (the current admin user). The KB lists four of these (`#userid#`, `#useremailaddress#`, `#roleid#`, `#rolename#`); the product also offers `#username#`. Pages (not sections) get only the common macros. [S][KB]

## Using macros
- Put them in the **Content Details** address or HTML exactly as the screen shows them. Replacement is case sensitive. Example from the screen help: `https://{URL}?storecode=#StoreCode#` passes the actual store code. [S]
- Query-string parameter names you read in your controller are your own choice; the SDK sample reads `StoreCode` and `PortalID`. [KB][S]
- The value is **Base64 of the text, then URL-encoded**. Decode it in your page or controller (the SDK sample has a helper that does this). [S][KB]
- For HTML content the same values are also kept in the browser's session storage under the key `zn_<macro name>` (value Base64). The SDK sample page reads them with a small helper (`MacroValue`). [S]
- A macro is only filled when the screen has a value. Opening a section outside a record (for example a list) is not possible; sections always open for one record. [I]

## Behaviour to know
- Products, Category and Promotions and Coupons sections appear as tabs that keep the active-tab styling; other entities show a plain side-panel link. [S]
- Macros are resolved when the panel is drawn, so a record change needs a reload of the section. [I]
- Only ids and codes are passed. Anything else (name, price, status) your page must read through APIs with the id. [S]
