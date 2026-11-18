# General tab: every field, default, rule and message

What this answers: the exact fields of Add Store and Manage Store > General, their defaults, limits, messages and effect, including the store feature check boxes.
Defaults were seen on a development environment admin on 2026-10-08 (module guide, tagged 90) unless marked KB.

## 1. Fields

| Field (as shown) | Default | Rules and exact messages | Effect |
|---|---|---|---|
| Brand Name | empty | Required, up to 100 characters. `Brand Name is required.` | Brand column of the store list |
| Store Name | empty | Required, up to 100 characters, not unique. `Store Name is required.` | Internal name; title of the Manage Store page |
| Store Code | empty | Required, letters and digits only, up to 100, unique ignoring case, read-only after create. `Store Code is required.`, `Only alphanumeric characters are allowed.`, `Store Code already exists.` | The key used by the API (`{storeCode}` routes) and in tags and URLs. It cannot be renamed |
| Catalog | empty (`Select Catalog`) | Required, one published catalog. `Catalog is required.` | Products the store sells |
| Theme | empty (`Select Theme`) | Required. Changing it opens `Please Confirm`; switching theme deletes the theme configuration of the previous theme. `Theme is required.` | Storefront look. The first CSS of the theme is used; the CSS is changed later on Manage Store |
| Enable Secure Socket Layer (SSL) For This Store | unticked | - | Store URL gets `https://` |
| Administrator's Email | empty | Comma separated list, valid addresses. `Please enter a valid Email Address.` If left blank the From Email Address of the store SMTP is used; if both are blank customers receive no emails | Sender and contact of store emails |
| Sales Department Email | empty | Valid address | Shown to customers |
| Customer Service Email | empty | Required. `Customer Service Email is required.` | Shown to customers |
| Sales Department Phone Number, Customer Service Phone Number | empty | Required, free text. `Sales Department Phone Number is required.`, `Customer Service Phone Number is required.` | Shown to customers |
| Default Customer Review Status | `Do Not Publish. Require Moderator Approval` on the Add form | Choices: that or `Publish Immediately` | Whether new reviews show at once |
| Order Status | `SUBMITTED` | List is the statuses of the Orders class and differs per environment. Ticking manual approval switches it to `Pending Approval` and locks it | Status of new orders |
| Require Manual Approval Of Every Order | unticked | - | Every new order waits for approval. Live on Save, no store publish (KB) |
| Default Quote Status | `SUBMITTED` | Quotes class statuses. Not saved by Add Store; set it on Manage Store after create | Status of new quotes |
| Enable Cart Redirect | unticked | - | After sign in the shopper lands on the cart when it has items. Live on Save (KB) |
| Enable Product Comparison | unticked | - | Compare icon on product cards. Live on Save (KB) |
| Enable Profile Based Catalog (KB: Enable Profile-Based Search) | unticked | - | A shopper with a profile browses the profile catalog. Live on Save (KB) |
| Enable Save For Later | unticked | - | Save for later link in the cart |
| Display Subcategory Products In Parent Category (KB: Enable Inheritance of Child Category products to Parent Category) | unticked | - | Parent category pages and search include child category products |
| Enable Add To Cart Option For Product Sliders | unticked | - | Add to Cart and View Details buttons in product carousels |
| User Registration Method | `Self Registration With No Email Verification` | Choices add `Self Registration With Email Verification` and `Self Registration With Admin Approval`. Live on Save (KB) | How shoppers register |
| SMTP Authentication Method | `Advanced SMTP` | Choices `Advanced SMTP` or `SMTP`; the help line changes to describe which one all outbound mail uses | Which SMTP tab shows |
| In-Stock Message, Out-Of-Stock Message, Back-Order Message | empty | Free text | Inventory texts |
| Enable Order Notification | unticked | Shows Order Amount and Email Address. Unticked empties both at save | Alert for large orders |
| Order Amount | empty | 0.01 to 999999. `Enter an Order Amount between 0.01 and 999999.` | Alert threshold |
| Email Address (order notification) | empty | Comma list up to 500 characters. `Please enter a valid Email Address.` | Alert recipients |
| Copy Content Based On (Add only) | `None` | None or one store | Copies content pages and messages from that store |

## 2. The store feature check boxes

The six boxes plus one hidden feature are a fixed master list of seven store features. A store has a feature on when it is ticked. Source: product source and a development environment (2026-10-09).

| Feature (label) | On | Off |
|---|---|---|
| Enable Cart Redirect | Shopper lands on the cart after sign in, two factor sign in or impersonation when it has items | Lands on the home page (or the store's login redirect page) |
| Address Validation (hidden) | Quote address validation path and the storefront address validation flag. There is no screen to set it; use the Address Validation settings group on Additional Attributes | Not validated |
| Enable Product Comparison | Compare icon on product cards | No icon |
| Enable Profile Based Catalog | Profile catalog browsing and profile aware cart, user and order reads | Store catalog |
| Enable Save For Later | Link on each cart line and the Saved For Later list (signed in users only) | Hidden |
| Display Subcategory Products In Parent Category | Child products included on parent pages and search | Parent only |
| Enable Add To Cart Option For Product Sliders | Buttons on carousels | Hidden |

Behaviour to know:

- A new store has no feature ticked. A copied store copies the source store's features.
- Every Save of the store deletes and re-inserts the feature rows, even if nothing changed. An API caller that sends `UpdatePortal` without the feature list probably switches all features off (inference from the delete and re-insert behaviour).
- The values are read live by the API. No store publish is needed; the storefront shows the change when its caches clear (section 4 of `04-what-requires-publishing.md`).
- Barcode scanner, voice search and CMS page search are no longer store features. They are controlled by search settings (`Marketing > Site Search > Search Settings`: Enable Barcode Scanner, `EnableBarcodeSpecificSearch`, `BarcodeScannerLicenseKey`). The 10x Webstore reader does not use the licence key.
- Defaults that come from Global Settings and are not on the form: currency, culture, weight unit, country, first active locale. Dimension unit is `CM`.

## 3. Rules about changing a store

| Rule | Detail |
|---|---|
| Store code is immutable | Changing it through the API is refused |
| A new store is inactive, not approved and in Draft publish status | Store Mode is blank until the first publish |
| Copy Store copies features, SMTP (as it is), units, locales and recommendation settings but not the maintenance flag | A copy of a store under maintenance starts live |
| Store save sends cache events only when the store has a `WebStore` or `WebstorePreview` address | With no address the old answer can be served until the cache lifetime ends |
| Order Status list differs per environment | Do not hard code ids in a customization; read the list |
