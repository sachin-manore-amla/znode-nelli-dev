# Manage Store tabs, what each holds, and the store API

What this answers: the exact tab names under Manage Store, which settings each tab holds, what must happen for each to reach the storefront, and which API operations read and write store settings.

Admin path: `Stores > Stores` (some builds and the KB label the parent menu `Stores & Reps`). Add Store shows only the General fields. All other tabs appear after the first Save (KB and product). The page title is `Manage {store name}`.

## 1. Tabs (left panel of Manage Store)

Labels verified in the product source (2026-10-15). The KB article names differ in places: the product label wins.

| Tab label | KB name | What it holds | Customization relevance |
|---|---|---|---|
| General | General | Identity, catalog, theme, email, order and quote defaults, feature check boxes, registration method, messages, order notification, SMTP method | Feature check boxes and defaults; see `02-general-tab.md` |
| URLs | URL | Web addresses of the store, type `WebStore` or `WebstorePreview`, one default per type | A domain must exist before the Webstore or Preview can serve the store |
| Profiles | Profiles | Profiles associated with the store | Decides prices and payment or shipping intersections |
| Price Lists | Price List | Price lists associated with the store and their precedence | Price resolution |
| Brands | not listed | Brands shown for the store | - |
| Inventory | Inventory | Warehouses associated with the store | Stock display |
| Shipping Settings | not listed | Shipping origin: use the warehouse address or a manual address | Rate calculation |
| Shipping Methods | Shipping Method | Associated shipping plugin configuration sets | One configuration set per plugin |
| Payment Settings | not listed | Payment settings of the store | - |
| Storefront Payment Methods | Payment Method | Payment plugin configuration sets for the storefront | Display name must be unique per store |
| Offline Payment Methods | not listed | Payment configuration sets for offline orders | - |
| Tax Settings | not listed | Tax classes and the default tax | Tax calculation |
| Countries | not listed | Countries available to shoppers | - |
| Locales | not listed | Locales of the store and the default locale | Locale scoped content |
| Product Listing options | not listed | Sort options and page size options, with a default page size | Shopper listing UX |
| SMTP or Advanced SMTP | SMTP | Which one shows depends on the General tab SMTP Authentication Method. SMTP is user name and password. Advanced SMTP is OAuth 2.0 | Email sending |
| SMS Notifications | not listed | Store SMS (Twilio) settings | - |
| Units | Units and currency | Weight unit, dimension unit, active currency, culture, currency suffix and a preview | Pricing display |
| Analytics | not listed | Tracking and tag settings | - |
| Robots.txt | not listed | Robots content and default page robot tag | SEO |
| Additional Attributes | Additional Store Attributes | Store level feature settings, one group each | The main customization switch area; see `03-additional-attributes.md` |
| Approval Management | not listed | Order approval routing for the store | B2B |
| Commerce Portal Settings | not listed | Default order and quote status for the Commerce Portal | Commerce Portal |
| B Store Settings | not listed | B Store settings; visible only when the B Stores module is enabled for the environment | See `config-stores-tenancy` |

Behaviour to know:

- The B Store Settings tab is controlled by a deployment setting of the Admin (`EnableBStoresModules`, default `false`). Customers cannot change it; it is part of the hosted environment.
- Klaviyo email marketing has a screen in the product but its tab link is not shown in the left panel of the version checked.
- Storefront Payment Methods and Shipping Methods store plugin configuration sets, see `sdk-provider-plugins`.

## 2. Units, product listing and URLs: the rules that surprise people

| Tab | Rule | Message |
|---|---|---|
| Units | Weight unit values: Lbs and Kgs. Dimension unit values: IN and CM. Culture list is filtered by the chosen currency. Currency suffix is set from the currency and cannot be edited | none |
| Units | A new store gets its currency, culture and weight unit from the Global Settings defaults. The dimension unit of a new store is always CM | none |
| Product Listing options | A sort or page option already associated cannot be associated twice | `Unable to associate Sort Item because some sort item is associated.` and `Unable to associate a page item because it is associated.` |
| Product Listing options | There must be exactly one default page option | `At least one option should be saved as default.` and `The default option cannot be unassigned` |
| Product Listing options | Without options the Webstore falls back to built-in sets: sort Default Sort, Sort by Name A to Z, Sort by Name Z to A; page sizes Show 8, 12, 16 (default), 32, 64 | none |
| Product Listing options | Price sort options are hidden when price sorting is not allowed for the list | none |
| URLs | Domain names are unique across all stores. The first domain of a type becomes the default whatever the check box says | `Domain names must be unique across all your stores.`, `Record created successfully.`, `Failed to create record.`, `Enter a valid URL.` |
| URLs | Name length up to 100 characters | form validation |

## 3. Store API operations

Source: public specification, checked 2026-10-15.

| Operation | Purpose | Notes |
|---|---|---|
| `GET /v2/portals/{storeCode}` | Store detail by code (Customer API) | Preferred for new work |
| `GET /v2.1/portals/{storeCode}/application/{type}` | Store detail as the Webstore reads it, including store feature values and attributes | `type` is the application type (`WebStore` or `WebstorePreview`). The older `v2/portals/{storeCode}/application/{type}` is deprecated |
| `GET /v2/portals/{storeCode}/robots-txt`, `GET /v2/portals/{storeCode}/product-feed` | Robots data and product feed of a store | |
| `GET/POST/PUT /v2/stores/{storeCode}/advanced-smtp` | Advanced SMTP (OAuth) settings of a store | Secret fields: never log |
| `GET /v2/search/{storeCode}/feature-settings`, `DELETE /v2/search/{storeCode}/feature-settings/delete` | Search feature settings of a store | |
| `GET /v2/portals/operations/status` | Status of store publish and export operations | |
| `GET /Portal/GetPortalByStoreCode/{storeCode}`, `GET /Portal/GetPortal/{portalId}`, `GET /Portal/GetPortalList` | Store read (Multifront API v1) | Legacy v1. `GetPortalByStoreCode` answers from a cache; see `04-what-requires-publishing.md` |
| `POST /Portal/CreatePortal`, `PUT /Portal/UpdatePortal`, `POST /Portal/CopyStore`, `POST /Portal/DeletePortal/{isDeleteByStoreCode}` | Create, update, copy, delete (Multifront API v1) | `UpdatePortal` rewrites the store feature rows every time; send the full set of features |
| `GET /Portal/GetPortalFeatureList` | Master list of store features | Returns every feature with value `false`. It does not say which a store has. Read the selected features from the store detail |
| `GET/PUT /Portal/GetPortalShippingInformation`, `UpdatePortalShipping`, `GetTaxPortalInformation`, `UpdateTaxPortal`, `GetRobotsTxt`, `SaveRobotsTxt`, `GetBStoreSetting`, `UpdateBStoreSetting`, `AssociateSortSettings`, `AssociatePageSettings` | Per tab settings | Legacy v1 |

Store level attribute values (the Additional Attributes tab) are saved through the user defined field style operations of the Admin. A documented v2 write route for a store attribute was not found; it is not in the public specification. Read them from the store detail routes above.

Auth and scoping: see `api-auth-and-headers`. Store scoped routes need the store (portal) context headers.
