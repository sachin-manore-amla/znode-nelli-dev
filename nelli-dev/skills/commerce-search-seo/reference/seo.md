# SEO
What this answers: SEO fields and defaults, URL key rules, the validation setting, 301 redirects, robots.txt.
Sources: KB Managing SEO, Managing Product SEO, Manage SEO Validation Settings, Managing 301 Redirects, Editing the Robots.txt File for a Store (read 2026-11-23). Category SEO and Content Page SEO articles not read (assumed similar, unverified). Confidence 85.

## SEO fields per entity (Marketing > SEO Setup > Products, Categories, Content Pages; Edit)
Per store, localizable (follows store locales): Locale, Name (display), **SEO Title**, **SEO Description**, **SEO Keywords** (optional; engines ignore meta keywords), **SEO-Friendly Page Name**, **Is Redirect**, **Canonical URL** (defaults to the SEO-friendly URL), **Robot Tag** (INDEX FOLLOW, NOINDEX NOFOLLOW, NOINDEX FOLLOW, INDEX NOFOLLOW).

## Default SEO Settings (Marketing > SEO Setup > Default SEO Settings Level)
Select Store Name. Nine fields: SEO Product / Category / Content x Title / Description / Keyword. Used when an entity has no SEO values.
| Variable | Value | Where |
|---|---|---|
| `<NAME>` | product name, category name or content page title | all |
| `<PRODUCT_NUM>` | product number | products only |
| `<SKU>` | SKU | products only |
| `<BRAND>` | brand | products only |
Category and content defaults accept `<NAME>` only. Text can wrap variables ("Shop now for <NAME>"). The article's field help mentions "Product Code" with no matching variable: verify. **Saving an empty default writes empty content into the storefront HTML.**

## URL key rules
- Letters and numbers plus `_`, `-`, `/` (the global setting article also lists `.`); must not start or end with `/` (the stricter reading is safer); maximum 1000 characters when validation is on.
- Must not equal a reserved keyword exactly: content, product, blog, brand, account, cart, check-global-cache, checkout, compare-product, contactus, feedback, forgot-password, highlight, login, multi-factor-authentication, order, order-status, pending-order, punchout (written punch-out in one article), quick-order, quote, reset-password, return, search, signup, store-locator, validate-impersonation-session, validate-single-sign-in, write-review, maintenance, category. Plurals or longer forms are fine ("product-list").
- If no URL is entered the product URL uses its Product ID.

## Disable SEO Validations (System Settings > Global Settings > SEO Validation Settings)
No (validation on) is the default and recommended. Yes accepts any value, including reserved keywords. Applies to PIM Product, PIM Category, CMS Content Pages, SEO Setup Product, Category, Content Pages. Validation runs only when a URL is created or updated; existing URLs are not changed. Save after toggling.

## Is Redirect
On: visitors of the previous URL are redirected to the new URL. Off: they get the 404 page. Example: "Fuses/Guy-Wire-Steel-Strand" renamed to "Guy-Wire-Steel-Strand".

## 301 URL Redirects (Marketing > SEO Setup > 301 URL Redirects)
Add New, Edit, Delete. Fields: **URL Redirect From**, **URL Redirect To** (Znode-specific paths; **internal URLs only**), **Enable this Redirection**. **Publish the store** after any change. Import of redirects: not covered.

## Robots (Stores and Reps > Stores > Manage > Robots.txt)
Robots Content (crawl rules) and **Default Page Level Robot Tag**: None (follow Robots Content), INDEX FOLLOW, NOINDEX NOFOLLOW, NOINDEX FOLLOW, INDEX NOFOLLOW. A page-level tag overrides the store default.

## Publishing
SEO edits on products and categories need the product, catalog or store publish; redirects need a store publish (`commerce-publish-pipeline`). With "Display Pricing and SEO Details of Products from Index" on for a catalog, changes to SEO need a Full Catalog Publish.

## Customization
Meta tags from rules: default settings with variables. Dynamic meta tags from external data: Webstore customization of the page metadata (`webstore-customization`). Bulk SEO changes: import or API (unverified routes). Structured data, sitemaps: not documented in the articles read.
