# Entity types and where the fields appear
Which entity types can carry user-defined fields, where each one shows them in the Admin, and the code the API wants for each.
Use it to answer "can I add a field to X?" and to find the screen where a value is typed.

## The entity list

The Knowledge Base lists 28 entity types for UDFs (article "Dynamic Schema - User Defined Fields, Groups, and Families", read in full, 80):
Account, Banner, Blog/News, Brand, BStore, Catalog, Content Containers, Email SMS Template, Form Builder, Global Setting, Inventory, OMS, Page, Payment Type, Price List, Price List Item, Product Highlight, Product Review, Promotion, RMA Configuration, SEO, Shipping Type, Store, Store Location, User, User Profile, Voucher, Warehouse.

The product source also creates entity types for Order, Quote, Pending Order, Return, Line Item, and the line items of an order, a quote and a return, and the Admin shows UDF sections on the Order, Quote and Return screens (verified in source, 90). The Knowledge Base list does not name them. The live list on your environment is `GET /v2/global-entities` or the `Entity Type` list on the `Add` attribute screen. That list is the truth for your environment.

Not supported: Product, Category and Media. They use PIM and Media attributes (skill `commerce-product-attributes`). Cart, Shopper session, Address and Custom Table records have no UDF entity type (not found in the product source).

Entities that carry settings of the product itself (Store, User, Account, Global Setting) already hold system-defined fields. See settings-and-flags.md.

## Where the values are edited in the Admin

Three patterns exist (KB: "Entity Tab, Entity Section, Entity List View Action Icon").

| Pattern | What you see | Entities (verified in the Admin source unless marked) |
|---|---|---|
| Left-panel link `Additional Attributes` | A page `Manage <entity>` with one tab per group, a `Save` / `Save & Close` pair and a back link | Store, User, Account, B Store, User Profile, Promotion, Product Highlight, Page, Blog/News, Brand, Inventory, Warehouse, Price List, Shipping Type, Store Location |
| Section on the edit screen | The groups appear inside the screen, below the standard fields, and are saved with the record | Email Template, Voucher, Payment option, Price list item (add or edit a SKU price), Product review, RMA configuration, SEO (store SEO settings), Banner, Order (manage order), Quote (manage quote), Return (manage return) |
| Pop-up from the list | An `Additional Attributes` pop-up opened from a row action | Catalog (catalog list) |
| Content Container variants | The groups of the container's family show on the variant edit screen, for the default variant and for each associated variant | Content Containers |
| Form definition | Groups or single fields are attached to the form. A shopper fills them when submitting | Form Builder |

Not verified in the Admin source: where the Pending Order and Line Item entities show their fields (GAPS).

## Menu paths

| Entity | Path to the record, then the fields | Source |
|---|---|---|
| Account | `Customers > Accounts > Manage Account > Additional Attributes` | KB (80) and Admin source |
| User | `Customers > Users > (user) > Additional Attributes` | KB (80) and Admin source |
| Store | `Stores and Reps > Stores > (store) > Additional Attributes` (KB title: Additional Store Attributes) | KB (80) and Admin source |
| Content Container | CMS area, `Content Containers`, then the container and its variant | KB "Creating a New Content Container" (80) |
| Form | `CMS > Manage Forms`, edit the form, add global attributes or attribute groups | KB "Creating and Managing Custom Forms" (80) |
| Promotion | `Marketing`-area promotion list, open the promotion, `Additional Attributes` | Admin source (90) |

On the page that edits the values:
- One tab per group, ordered by the group display order. A group with no fields is hidden.
- When no group is set up for the entity: `No records found.`
- `Save` and `Save & Close` need the `User-defined Fields > Attributes` write permission. Without it the link or the buttons are not drawn (module guide, brand entity, 85).
- Required or invalid field: the tab is highlighted and the notification shows `A few required fields are missing. Please complete them to save successfully.`
- Required File or Image with no file: `Please select file.`
- After a successful save: `Record updated successfully.` (v1 Admin save). The service text is `Entity Attribute saved successfully.`
- Values are saved in the default language when the screen has no language switch (brand screen, module guide 85). Localizable fields on entities that do have a language selector save per language.
- Last save wins. The screen does not warn if another admin changed the record in between (module guide, 85).

## API code for each entity (PUT /v2/global-entity-attributes)

The write call needs `EntityType` and `EntityCode` for every value. The code means different things for each entity (API reference text, source):

| EntityType | EntityCode |
|---|---|
| Store | Store code |
| Account | Account code |
| User | User id (number) |
| ContentContainers | Container key |
| Promotion | Promo code |
| PriceList | List code |
| PriceListItem | SKU |
| Inventory | SKU |
| Warehouse | Warehouse code |
| ShippingType | Shipping code |
| Catalog | Catalog code |
| ProductHighlight | Highlight code |
| Page | Page code |
| UserProfile | Profile id |
| Brand | Brand code |
| BlogNews | Blog or news code |
| StoreLocation | Store location code |
| Order | Order number |
| Quote | Quote number |
| Voucher | Card number |
| Banner | Banner slider locale id |
| EmailSMSTemplate | Template name |
| SEO | Store SEO setting id |
| PaymentType | Payment type code |
| RmaConfiguration | RMA configuration id |
| ProductReview | Review id |
| Return | Return number |
| OrderLineItems, QuoteLineItems, ReturnLineItems | The line item id |
| Form Builder | Portal id must be greater than 0 (API reference) |

Entity names are compared with spaces removed and ignoring case on the write call, so `PriceList` and `Price List` both work there. Creating an attribute needs the name as the entity list shows it (with spaces), compared ignoring case.

## Per-entity notes that matter to a customization

| Entity | Note |
|---|---|
| Account | Account built-in fields on the same screen: Voucher Expiration Reminder Email (In Days), Business Identification Number (used by AvaTax VAT), Price List Inheritance for Parent Accounts. They are system-defined fields. Custom groups appear beside them (KB, 80). The account read call returns the values as `Attributes` |
| User | Built-in groups: Budget, Open Account Billing Details, Address Setting, Power BI Settings, Global Order Settings (Delegates and Managers, comma-separated, not validated against real users) (KB, 80). The user read call returns custom values as `AdditionalAttributes`. The Webstore reads the user's address-setting field at checkout |
| Store | Holds many product settings (Cloudflare, login requirements, budget, 2FA, CSP, reCAPTCHA, warehouse stock display, address validation, quotes, returns, TradeCentric, vouchers, shipping, billing, product message, maintenance). Add your own groups beside them. The store portal call returns the values as `GlobalAttributes` (KB, 80; source) |
| B Store | Same pattern as Store, saved against the B Store. The save refreshes the portal cache |
| Content Containers | Family is chosen per container. File and Image fields work. Variants hold their own values |
| Form Builder | The form shows the attached fields in the group and field display order. A required Email Address field is needed for the acknowledgement email (KB, 80). Form changes are live without publishing (KB "What Requires Publishing", 80) |
| Promotion | Groups can be limited to a promotion type (see groups-and-families.md). Promotion list export can include the UDF columns (see settings-and-flags.md) |
| Voucher | Edit screen section. Voucher list export and voucher import support the fields |
| Order, Quote, Return | Sections on the manage screens. Values are per order, quote or return. Whether a value is copied from the quote to the order is not verified (GAPS) |
| Global Setting | Not for customer data. These hold the product's global settings (see `config-global-settings`) |
