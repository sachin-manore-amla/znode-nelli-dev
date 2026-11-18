# What requires publishing, and store caching

What this answers: which store related changes need a store, catalog or content publish, which are live after Save, and how long a saved store change can take to reach the storefront.
Sources: KB "What Requires Publishing" (read in full, 80), KB "Configuring General Store Information", "Configuring Additional Store Attributes", "Managing Stores" (read in full), product source and a development environment (2026-10).

## 1. The KB list

| Needs a publish to be live (KB) | Live immediately without a publish (KB) |
|---|---|
| Store Settings or Store Experience changes | Store Locations |
| Products, Categories, Catalogs, associated Media, SEO | Users, Admin Users, Sales Reps |
| Pages | Accounts |
| Containers | User Profiles |
| Banner Sliders | Pricing |
| Blogs and News | Inventory and Warehouses |
| | Email Templates |
| | Form Changes |
| | Promotions and Coupons |
| | Configuring a search profile |
| | Additional Attributes |
| | Global Settings |

## 2. Where the KB contradicts itself or the product

| Item | KB statement | Product observation | Answer to give |
|---|---|---|---|
| Store Settings | Needs a publish | Several flags are read live from the store detail the API returns (store features, maintenance). Theme, logo, favicon and title are read from the published store | Publish the store after changing theme, logo, favicon, title or anything under Store Experience. Flags: Save is enough, then allow the cache time in section 4 |
| Additional Attributes | Live immediately | The Additional Store Attributes article says Webstore Authorization (Login To See Pricing and Inventory, Login Required) and Warehouse Display Stock Levels need Store Settings published | Follow the specific article: publish the store for those two groups. Treat the others as live after Save |
| General tab | Not stated per field; six fields work with Save alone (Requires Manual Approval Of Every Order, Enable Cart Redirect, Enable Product Comparison, Enable Profile-Based Search, Enable Voice-Based Search, User Registration Method) | Store features are read live by the API | Save is enough for those six and for the store feature boxes. For other General fields, publish the store when the change is visible on pages |
| Global Settings | Live immediately | True for the Save step. Settings that feed the index need a publish or re-index | See `config-global-settings` |
| Product Listing options | Not listed | Admin changes need the Webstore cache cleared or a republish before they show (module guide) | Save, then clear the Webstore cache or publish |
| Promotions and Coupons | Live immediately | Calculated at cart time | No publish |
| Product overrides | Not listed | Override records need the product or catalog published after the record is saved | Publish products or the catalog |

## 3. Store publish (Stores > Stores > Publish)

| Item | Detail |
|---|---|
| Where | The Publish icon on the store row opens a dialog; click `Proceed` |
| Options | `Preview & production` or `Preview Only` (only when the Preview target is enabled in Global Settings > Publish Settings); optional check boxes for CMS content and for the catalog; `Publish Draft Products Only` is ticked by default when Catalog is ticked and publishes only products in Draft status |
| First publish | A new or copied store is in Draft publish status. Until the first publish the storefront answers "store not published" and the Store Mode column is blank |
| Preview | Preview needs a web address of type `WebstorePreview`, Preview enabled in Global Settings, and does not show unpublished changes, theme changes, store settings or global attributes |
| Publish status values | Not Published, Draft, Production, Preview, Publish Failed, Processing, Aborted, Publish Skipped (No Drafts) (the last label can differ by environment) |
| API | `GET /v2/portals/operations/status` reports the status of store publish and export operations |

## 4. How long a saved store change takes to show

Verified in the product source and on a development environment (2026-10).

| Layer | Lifetime of the old value | Cleared early by |
|---|---|---|
| API store by code answer (`GET /Portal/GetPortalByStoreCode/{storeCode}`) | 20 minutes (cache lifetime of the deployment) | A store save, but only when the store has a `WebStore` or `WebstorePreview` address; `?cache=refresh` on that call |
| API store by id answer, store list, feature list | Not cached | Not applicable |
| Webstore portal data | 15 minutes by default (`PORTAL_CACHE_TTL_MS`); 60 seconds for a miss (`PORTAL_CACHE_NEGATIVE_TTL_MS`) | The cache event posted to the Event Subscription URL with a matching secret (see `sdk-extension-settings`) |
| Webstore Next.js data cache | Until its own expiry or the same event | Same event |
| CDN or Cloudflare | Per the CDN rules | Store, CMS and settings publish clear Cloudflare (KB); Global Settings can clear it manually |
| Search index and published store copy | Until the next publish | Publish |

Behaviour to know:

- A store save shares one cache tag with every store's by-code answer, so one save can clear all of them.
- Copy Store and Delete Store send no cache event for the old answers.
- If the Event Subscription URL is empty, the Webstore is never told. Shoppers see a store change only after the Webstore cache lifetime.
- Changing the store flag does not need a catalog publish. Changing which products appear does.

## 5. Nelli-Dev decision guide for this file

| Question | Answer |
|---|---|
| I changed a store flag and the storefront did not change | Check in order: saved on the right store and locale, store publish if the KB says so for that group, Event Subscription URL and secret configured, wait up to 15 minutes or clear the Webstore cache |
| Do I need to publish the catalog after a store flag change | No. Only the store publish where required |
| Can my customization read store flags | Yes: `GET /v2/portals/{storeCode}` or `GET /v2.1/portals/{storeCode}/application/{type}` from the SDK or the Webstore data layer |
