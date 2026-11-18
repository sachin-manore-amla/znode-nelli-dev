---
name: webstore-customization
description: Every way to customize the Znode V10 storefront (the Webstore, a Next.js app in an Nx monorepo, and its Page Builder app) - what to configure in Admin, what to add through widgets and themes, and what means changing base source - with the repo layout, the BFF route pattern, data flow, step-by-step recipes, caching and visibility rules, environment variable names, build and lint commands, and a decision guide of storefront requirements with verdicts. Use for any question or request about changing storefront UI or behaviour, adding a page, widget, theme, route, locale or field, or making a Webstore change appear on the live store. Replaces webstore-customization.
user-invocable: false
---

# Webstore customization

The Webstore source is one Nx monorepo with two Next.js 15 apps: `apps/webstore` (the storefront) and `apps/page-builder` (the visual editor that Admin opens for CMS > Store Experience and CMS > Pages). They share the packages under `packages/`. Knowledge Base: "Webstore Customization Guide" (documents widgets, themes, Page Builder pages and Tailwind). Verified against the Webstore source (version stamp 10.14.0.0 (read 2026-10-15).

## The three levels (pick the lowest that works)

| Level | What you do | Verdict to give | Upgrade-merge cost |
|---|---|---|---|
| 1. Configure | Admin settings, Page Builder editing of commerce pages and content pages, Dynamic Styles CSS variables, product Custom Fields, header and footer, locales | **Supported** (no code) | none |
| 2. Extend | New Page Builder widgets, a theme package (theme-level widgets and page overrides, Tailwind theme), new BFF routes, new pages, calls to a Custom API | **Customizable** (documented mechanism, code in your Webstore repo; the KB documents widgets and themes, the route and page recipes follow the repo patterns) | low to medium: new folders plus a few registration lines in shared files |
| 3. Change base source | Edit `packages/base-components`, `packages/agents`, `packages/clients`, shared routes in `apps/webstore` | **Customizable, labelled "customization of source, not a supported extension point"** | high: every edit can conflict on upgrade |

Rule: never write code for something level 1 does. Prefer a theme copy over editing base files when only presentation changes. Put business rules that must hold on list, cart and checkout in the API or Custom API, not in UI components (see `sdk-capability-registry`).

## Ten facts that matter most

1. Almost every storefront page is rendered from Page Builder page JSON. The page JSON is fetched per store and page code and rendered with a config chosen by theme name and page type (`packages/page-builder/src/configs/get-config.ts`).
2. Commerce pages (product, category, brand, blog, store locator, contact us, feedback, cart, checkout, quick order, track order, forgot password, login, signup, maintenance) are fixed page widgets. Admins edit only their limited fields and add widgets above or below. They cannot delete, duplicate or move them.
3. Theme name comes from the store's Theme setting in Admin (CMS > Store Experience > General Settings); `DEFAULT_THEME` is only the fallback. Theme keys are matched in lower case.
4. Registering a new widget needs a config file, a render file, a registration line and (for the base config) a key in the `IComponentProps` type. The widget must be listed in a category through `addComponentToCategories` or it does not show in the editor.
5. Registering a new theme needs registration in **two** loaders (`get-config.ts` and `get-layout-config.ts`) plus Tailwind theme wiring in both apps. The KB lists only the first. See `reference/kb-vs-product.md`.
6. The browser never calls Znode directly. Components call `/api/...` routes of the Webstore (BFF); the route calls an agent; the agent calls a typed client; the client adds the auth and context headers.
7. Both apps must be built and deployed with your widget or theme code, because both import the same configs.
8. A change shows on the live store only after the right cache layer is refreshed (publish from Admin, revalidation call, CDN purge). See `reference/caching-and-visibility.md`.
9. `typescript.ignoreBuildErrors` is true in the webstore Next config only. A type error does not fail `nx build webstore` but does fail `nx build page-builder`, which imports the same widget code. Run lint and a type check yourself.
10. Husky runs spell check, lint, a full build and a Jira-style commit message check on every commit. Adjust `commitlint.config.ts` for your own ticket scheme.

## Where to read next

| Need | File |
|---|---|
| Folders, packages, page flow, data flow | `reference/repo-layout-and-data-flow.md` |
| BFF route pattern, headers, how to add a route, Custom API call | `reference/bff-routes-and-clients.md` |
| Decision rules, level 1 / 2 / 3 detail | `reference/levels-and-decision-rules.md` |
| Widget, theme, override, route, page, locale recipes | `reference/recipes-widgets-and-themes.md`, `reference/recipes-pages-fields-and-app.md` |
| Caching, revalidation, CDN, "why is my change not visible" | `reference/caching-and-visibility.md` |
| Environment variable names and purposes | `reference/environment-variables.md` |
| Commands, lint, tests, known behaviours | `reference/build-test-and-known-behaviours.md` |
| Where the KB and the product source differ | `reference/kb-vs-product.md` |
| Widgets, Page Builder admin steps, themes, locales | skill `webstore-page-builder-and-themes` |
| Using Znode from another front end | skill `webstore-headless-api` |

## Nelli-Dev decision guide (storefront requirements)

| Requirement | Verdict | Route |
|---|---|---|
| Change colours, button radius, fonts, header colour | Supported | Dynamic Styles CSS variables (CMS > Store Experience > General Settings > Dynamic Styles), publish store |
| Change heading, description or button text on contact us, feedback, login, signup, quick order, track order, forgot password | Supported | Page Builder commerce page attributes |
| Show or hide categories, facets, reviews, SKU on the product list page | Supported | Product List Page attributes in Page Builder |
| New landing or marketing page | Supported | CMS > Pages content page + Page Builder widgets |
| Extra product field on the product page (name and value) | Supported | Product Custom Fields; shown on the Additional Information tab. See `reference/recipes-pages-fields-and-app.md` |
| Reorder or add banners, promos, carousels around the PDP/PLP/cart/checkout | Supported | Page Builder widgets above or below the page widget |
| New widget (for example a testimonial block) | Customizable | `reference/recipes-widgets-and-themes.md` recipe 1 |
| Widget that shows data from a Custom API or custom table | Customizable | widget plus a new BFF route (recipe 4); widgets with built-in data binding need a handler entry (recipe 1 note) |
| Change the product card or list layout | Customizable (level 2 theme) | theme copy of the list page widget; editing the base card is level 3 |
| Show a custom table value on the PDP | Customizable | BFF route to a Custom API or Custom Table API client, small component placed in a theme PDP or a widget; verify caching |
| Replace the cart UI or change the cart layout | Customizable, high effort | theme override of the Cart Page widget (copy of the cart page component) |
| Add a custom checkout step or field | Customizable at source level (level 3) | checkout is one large page widget; call Custom API from a new BFF route; keep totals and validation in the API |
| New store theme or brand look | Customizable (documented) | theme package, Tailwind theme, theme registration; CSS-only variants are Supported |
| New locale | Supported plus code | Admin locale + message files + locale list, recipe 6 |
| Add reCAPTCHA to another form | Customizable | reuse the shared component and server check, recipe 7; keys are Admin store settings |
| Different front end entirely (React, mobile) | Customizable, outside the Webstore | `webstore-headless-api` |
| Change how prices, tax or shipping are computed | Not a Webstore change | `sdk-method-overrides`, `commerce-tax-shipping`, `commerce-promotions-and-pricing` |
| Edit Znode Admin screens or core APIs | Needs platform change | out of scope |
