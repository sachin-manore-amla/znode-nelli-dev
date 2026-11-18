---
name: config-store
description: The Znode store (portal) configuration reference - every tab under Stores > Stores > Manage with its exact label, the General tab fields with defaults and messages, the seven store feature switches, the Additional Attributes groups (including the store level Enable Product Information Overrides, maintenance, two factor, content security policy and address validation), units and currency, product listing options, URLs, locales, SMTP, and a "what requires publishing" table with store cache timing. Load it when you need to know where a store level setting lives, what it defaults to, whether it needs a store publish, or why a saved store change does not show on the storefront. Do not use it for platform wide settings (config-global-settings) or for the feature to setting index (sdk-extension-settings).
user-invocable: false
---

# Znode Store Configuration

A store (portal) owns its catalog, theme, domains, profiles, price lists, payment and shipping associations and a set of flags. Settings live on the tabs of `Stores > Stores > Manage`. All tabs except General appear after the first Save. Tenancy and B Stores are in `config-stores-tenancy`.

## Use it / do not use it

| Use this skill when | Use another skill when |
|---|---|
| Finding which tab holds a store setting, its default, or its exact label | The setting is global (`config-global-settings`) |
| A store flag or attribute does not take effect on the storefront | Email templates and SMTP content (`config-notifications`) |
| Deciding whether a change needs a store publish | Payment, shipping, tax plugin setup (`sdk-provider-plugins`, `commerce-tax-shipping`) |

## The 10 facts that matter most

1. Exact tab labels in the product: General, URLs, Profiles, Price Lists, Brands, Inventory, Shipping Settings, Shipping Methods, Payment Settings, Storefront Payment Methods, Offline Payment Methods, Tax Settings, Countries, Locales, Product Listing options, SMTP or Advanced SMTP, SMS Notifications, Units, Analytics, Robots.txt, Additional Attributes, Approval Management, Commerce Portal Settings, B Store Settings. The KB uses older names (for example "Additional Store Attributes").
2. Store Code is required, letters and digits only, unique ignoring case, and cannot be changed after create. The API routes use it as `{storeCode}`.
3. A new or copied store is in Draft publish status. Until the first store publish the storefront reports the store as not published.
4. Seven store features exist (six visible check boxes): Enable Cart Redirect, Enable Product Comparison, Enable Profile Based Catalog, Enable Save For Later, Display Subcategory Products In Parent Category, Enable Add To Cart Option For Product Sliders, plus a hidden Address Validation. None is ticked on a new store. They are read live (no store publish).
5. Every Save deletes and re-inserts the store features. An API update must send the full feature list.
6. The store level `Enable Product Information Overrides` (Additional Attributes, Product Settings) only works when the Global Setting of the same purpose is also on. It is per locale and defaults to off.
7. Store save sends cache events only when the store has a `WebStore` or `WebstorePreview` address. Without one the API can answer from its 20 minute cache.
8. The Webstore keeps store data 15 minutes by default and is only told to refresh when an Event Subscription URL and matching secret are configured.
9. Global Enable Maintenance for All Stores beats the store flag Webstore Under Maintenance. Copy Store does not copy the maintenance flag.
10. The KB contradicts itself on publishing for Additional Attributes. Publish the store for Webstore Authorization and Warehouse stock display; treat other flags as live after Save plus cache time.

## Files

| Topic | File |
|---|---|
| Tab list, units, listing options, URLs rules, store API operations | `reference/01-store-tabs-and-api.md` |
| General tab fields, messages, store feature switches, copy rules | `reference/02-general-tab.md` |
| Additional Attributes groups and the store override switches | `reference/03-additional-attributes.md` |
| What requires publishing, store publish dialog, cache timing | `reference/04-what-requires-publishing.md` |

## What requires publishing (summary)

| Change | Needs |
|---|---|
| Theme, logo, favicon, title, Store Experience | Store publish |
| Products, categories, catalog, media, SEO | Catalog or product publish |
| Pages, containers, banner sliders, blogs | Content publish |
| Store feature boxes, manual approval, cart redirect, registration method | Save only (plus cache time) |
| Webstore Authorization, Warehouse stock display | Store publish (KB) |
| Maintenance flag | Save only; Webstore data cache up to 15 minutes |
| Product listing options | Save, then clear the Webstore cache or publish |
| Pricing, inventory, promotions, users, accounts, email templates | Live after Save (KB) |

Full table with conflicts: `reference/04-what-requires-publishing.md`.

## Nelli-Dev decision guide

| Request | Verdict and steps |
|---|---|
| Turn on product overrides for one store only | Supported. Store switch On on that store only, global switch On, publish the products, Webstore source reads the override fields. |
| Why does my store setting not show on the storefront | Saved on the right store and locale; store publish if required; Event Subscription URL and secret set; wait the 15 minutes or clear the Webstore cache; Webstore code reads the value. |
| Does this need a restart | Store settings never need a restart. Deployment values do (Webstore environment variables, SDK appsettings). |
| Add a flag per store for my customization | Customizable: Custom API SDK setting or a custom table keyed by store code. A new store attribute group is a platform change. |
| Configure a store by API | Supported for create, update and copy (v1 Multifront routes) and read through `GET /v2/portals/{storeCode}`. Send every feature on update. |
| Per store SMTP, SMS, CSP, 2FA | Supported on the store tabs. Secrets are entered in the Admin Console, never in code or documents. |
| Need a different Additional Attributes setting | Needs a platform change. |

## Verified against

KB articles (Configuring General Store Information, Store Set-up Guide, What Requires Publishing, Managing Stores, Configuring Additional Store Attributes), the store module guide, and the product source and a development environment (2026-10). Where they differ the product wins and the file says so.

## Related

`config-global-settings` · `sdk-extension-settings` · `config-stores-tenancy` · `config-notifications` · `commerce-catalog` · `sdk-provider-plugins`
