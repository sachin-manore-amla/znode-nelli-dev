---
name: config-admin-customization
description: How to customize the Znode Admin Console without changing core code - Dev Center > Admin Customizations (custom pages in the menu and custom sections inside 20 supported entity screens, content type URL or RawHTML/iFrame, macros, role gating, sequence), the Custom API SDK route that serves the page (Custom.Admin.Core, CustomAdmin controllers and views, CORS, Basic auth header), limits, validation messages, security behaviour and the verdict guidance (custom page vs custom section vs Custom API-backed page vs platform change). Load it for any request to add a screen, tab, panel or extra field area to the Admin Console, or when a custom page or section does not show, is blank or is blocked.
user-invocable: false
---

# Admin Customization (custom pages and sections)

Verified against the Admin product source and the Custom API SDK (October 2026) and the KB articles listed in `reference/sources.md`. Tags: **[S]** product source (90+), **[KB]** KB article read in full (80), **[I]** inference (<50, said so).

## What it is
A built-in feature at **Dev Center > Admin Customizations** that adds your own content to the Admin Console:

| Term | Meaning |
|---|---|
| **Custom Page** | A new entry in the Admin menu (under **Custom Pages**) that opens your content. |
| **Custom Section** | Your content added to an existing entity screen (for example **Stores > Manage Store**) as an extra tab or side-panel link. |
| **Content Type** | `URL` (Admin fetches the address and shows the returned HTML) or `RawHTML Or iFrame` (Admin shows the HTML you paste, which may contain an `<iframe>` tag). |
| **Macro** | A `#Name#` placeholder in Content Details that Admin replaces with the current store, product, user and so on. |

Page and section are fixed at creation. You cannot convert one into the other. [KB][S]

## The 10 facts that matter
1. Screens are added with configuration, not code. The content itself comes from a URL you host (normally the Custom API SDK, see `reference/custom-api-route.md`) or from HTML you paste. [S]
2. **20 entities** accept sections: Stores, B Stores, Sales Rep, Store Location, Users, Accounts, Guest Users, User Profile, Pricing Engine, Inventory, Warehouse, Vendors, Products, Category, Brands, Add-on Groups, Promotions and Coupons, Product Highlights, Site Search, Power BI Reports. Orders, Commerce Portal, CMS pages and the Dev Center screens are **not** in the list. [KB][S]
3. For content type `URL`, the **Admin server** fetches the address and injects the returned HTML into the page. It is not an iframe. The request carries a Basic `Authorization` header built from the Admin's API domain name and key. Point it only at a host you control. [S]
4. Macro values reach your page **Base64-encoded** (then URL-encoded). Decode them. [KB][S]
5. Only roles of type **Admin** can be picked. Users in the Admin role see every page and section; others see only those given to their roles. Choosing **All Roles** also covers roles created later. [S][KB]
6. Code: letters and digits, starts with a letter, at most 25 characters, unique (not case sensitive), not editable later. Sequence 1 to 100 (default 99). [S]
7. Only the first nine custom pages are listed in the left menu; a **Show More** link opens the full list. [S, I on exact count]
8. Content Details accepts almost anything. The KB says validation of HTML and URL is limited, so treat every page as trusted code. [KB]
9. A custom form that posts to your host needs your host allowed in the Custom API's CORS list **and** in the Admin Content Security Policy (default `form-action 'self'`, limited `frame-src`). [KB][S]
10. There is no export, import or promotion feature. Pages are per environment; recreate them in each one. [I: none found in KB or source]

## When to use / not use
| Need | Use |
|---|---|
| A new screen with data from your ERP or custom tables | Custom Page with URL to a Custom API SDK admin page |
| Extra fields or a panel on an existing entity | Custom Section on that entity; for stored values prefer Additional Attributes/custom tables behind it |
| Static help text or a link list | Custom Page with RawHTML |
| Change or hide a built-in field, column, button, validation | **Needs platform change** (no hook exists) |
| A section on Orders, Commerce Portal, CMS pages, Dev Center screens | Not supported entity: **Needs platform change**; offer a Custom Page as workaround |

## Nelli-Dev decision guide
| Request | Verdict | How |
|---|---|---|
| "Add a screen in Admin that shows data from our ERP" | Customizable | Custom Page, content type URL, Custom API SDK page that calls the ERP; access via roles. `reference/custom-api-route.md` |
| "Add tabs on the account page" | Customizable | One Custom Section per tab, Entity Type `Accounts`, macro `#AccountID#`. Each section is one extra link in the account side panel. `reference/entities-and-macros.md` |
| "Show ERP credit limit on the store screen" | Customizable | Section on `Stores` with `#StoreCode#`; read-only is safest |
| "Limit a role to certain menus" | Supported | `config-roles-permissions`; custom pages follow the roles you tick |
| "Add a section to the Order screen in Admin" | Needs platform change | Orders is not an entity; workaround is a Custom Page |
| "Run our own validation when an admin saves a product" | Needs platform change here | Use Method Override or events (`sdk-method-overrides`, `sdk-events-and-webhooks`) |
| "Make the page appear the moment I save" | Supported with a caveat | Sign in again for other users, see `reference/security-and-limits.md` |
| "Copy pages from UAT to production" | Not available | Recreate manually, or script the Admin Customization API (legacy v1) with the developer's approval |

Always add: the page is customer code running in the admin (security review, `quality-security-checks`), and hosted environments need the Custom API deployed in the same network as the Znode API.

## Reference files
- `reference/pages-and-sections.md` - screens, fields, exact labels, messages, role gating, sequence
- `reference/entities-and-macros.md` - the 20 entities, macro names per entity, how values arrive
- `reference/custom-api-route.md` - Custom.Admin.Core, registration calls, controller and view pattern, deploy
- `reference/security-and-limits.md` - limits, CSP/CORS, trust model, behaviours to know, KB vs product
- `reference/admin-api.md` - the Admin Customization API operations (legacy v1)
- `reference/sources.md` - KB URLs and release notes

## Related
`config-roles-permissions` · `sdk-custom-api` · `sdk-conventions` · `quality-security-checks` · `config-global-settings` · `config-stores-tenancy`
