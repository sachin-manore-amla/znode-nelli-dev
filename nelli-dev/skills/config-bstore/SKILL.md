---
name: config-bstore
description: Znode B Stores - lightweight child stores that B2B owners and managers create and run themselves under a parent store - what they are, how admins enable and configure them (parent store B Store Settings, Stores > B Stores), what an owner or manager can customize in the B Store app (settings, design, content, products, users), storefront behaviour, the B Store REST v2 API and the B Store GraphQL endpoint, and verdicts. Load it for any request to create a self-service sub-store, limit a sub-store's catalog, brand it, manage its users, or integrate with B Store data.
user-invocable: false
---

# B Stores (self-service child stores)

Tags: **[S]** source/spec (90+), **[KB]** KB read in full (80), **[M]** catalogue/module guide (map or 85), **[I]** inference.

## What it is
A **B Store** is a child store of a regular (parent) store with its own subdomain, catalog selection, price list, design, content and users. Users with the **Owner** or **Manager** role create and run B Stores from a separate **B Store app**, opened from the storefront (**My Account > Manage Stores**) or embedded in the Admin. Two terms: **parent store** (regular store that allows B Stores) versus **B Store**; **Owner** (creates and configures, can duplicate) versus **Manager** (runs a store, cannot create). [KB][M]

## The 10 facts that matter
1. Admin enables the feature per parent store: **Stores > Manage > B Store Settings**: **Enable B Stores**, **Request B Store Page**, **Is Auto Approved**, **B Store Domain**, theme and CSS. These cannot be changed through the store's General tab. [S][M]
2. A B Store works for shoppers only when **Approved**, **Active** and inside its open/close dates. [KB]
3. New stores created in the app start inactive; approval is by an admin or by auto-approve. [M][KB]
4. Catalog: chosen from catalogs associated with the parent; optional hand-picked categories/products (**Do you want to specify products?**). Price list is chosen from those associated with the parent. [KB][S]
5. Theme: owner sets logo, favicon, colours and CSS only; the **B Store Starter Theme** hides parent elements (vouchers, promotions section on cart/checkout, multi-warehouse block, SKU on cards). [KB]
6. No quick order or order templates on a B Store; Place Order and checkout are blocked when the store does not allow orders; guests cannot request quotes. [M]
7. Owner/Manager roles are separate flags (**Is Owner**, **Is Manager**) per user and B Store, not Znode roles. [KB][S]
8. REST: `/v2/b-stores/...` (Core family, B Store spec); GraphQL: `/bstore-graphql/v1`, `/bstore-graphql/admin/v1`, `/bstore-graphql/storefront/v1` through the gateway. [S]
9. The B Store app's Orders and Quotes pages run on built-in sample data; use the Admin B Store Users tab for real order history. [M] (KB describes a working list: product wins.)
10. Deleting a B Store needs its associated items removed first: `B Store cannot be deleted until all associated items are removed.` [S]

## Nelli-Dev decision guide
| Request | Verdict | How |
|---|---|---|
| Create a self-service sub-store for a dealer | Supported | Enable B Stores on the parent; owner creates it. `reference/admin-configuration.md`, `reference/bstore-app-and-storefront.md` |
| Restrict the sub-store to 50 products | Supported | Specify products. |
| Own look for the sub-store | Supported for logo, colours, CSS; Customizable beyond via a custom theme [I] | `reference/bstore-app-and-storefront.md` |
| Extra fields on a B Store record | Supported | Additional Attributes tab (Stores) |
| Extra tab in the Admin B Store screen | Customizable | Custom section, entity `B Stores` (`config-admin-customization`) |
| Order management for B Store owners | Needs platform change | Orders/Quotes pages not wired |
| Change what GraphQL returns or add fields | Needs platform change | No extension source for customers [I] |
| Sync B Stores from an ERP/CRM | Customizable | `reference/api-and-graphql.md` with the B Store REST operations |

## References
`reference/admin-configuration.md` · `reference/bstore-app-and-storefront.md` · `reference/api-and-graphql.md`

## Related
`config-stores-tenancy` · `config-store` · `commerce-b2b-accounts` · `config-roles-permissions` · `config-admin-customization`
