# Themes, Dynamic Styles and Tailwind

What this answers: the Admin theme screens, parent and child themes, the Dynamic Styles CSS variables an admin can override, the four theme customization scenarios, and how a code theme is wired.
Confidence: KB "Configuring a Site Theme", "Dynamic Styles & Using Theme Dynamic Colors", "Managing the Store Experience", "Webstore Customization Guide" (read in full, 80); wiring checked in the Webstore source (90).

## Admin: CMS > Site Themes

Columns: ID, Name, Is Parent (a parent theme is a base for child themes), Is System Defined, Parent. Search by theme name or id; filter. Add New: Theme Name and Theme Code are mandatory; the parent theme is selected automatically; Save & Close shows a confirmation. Znode 10 uses theme inheritance: the supplied B2B theme is the base parent and customer work goes into child themes (custom branding, styling, page-level changes) for easier upgrades.

Assign a theme: CMS > Store Experience > (store) > General Settings > Theme. Other fields there: Website Title, Website Description, Website Logo, Favicon, Dynamic Style.

## Dynamic Styles (Supported, no deployment)

CMS > Store Experience > (store) > General Settings > Dynamic Style: add CSS, Save & Close, then publish the store (from Stores or Store Experience). The CSS is injected into the page head for that store (the Webstore removes control characters and script tags from it). Znode recommends moving permanent changes into the theme CSS and removing the temporary overrides.

Starter theme variables (names from the KB and the source; defaults differ slightly between them, so read the source file `packages/base-components/src/tailwind-config/global.css` for your version):

| Group | Variables |
|---|---|
| Header | `--header-bg` |
| Footer | `--footer-bg`, `--footer-primary-text`, `--footer-secondary-text` |
| Navigation | `--navigation-bar-bg`, `--navigation-text` |
| Buttons | `--primary-btn-bg`, `--secondary-btn-bg`, `--primary-btn-text`, `--secondary-btn-text`, `--btn-border`, `--btn-border-radius` |
| Cards | `--card-border`, `--card-radius` |
| Inputs | `--input-border`, `--input-radius` |
| Extra | `--mega-menu-bg`, `--mega-menu-link`, `--ticker-bg`, `--loader-color` |
| General | `--primary` (category and brand headings), `--secondary` (background fill), `--accent` (radio buttons, checkboxes), `--success`, `--error`, `--hover`, `--link`, `--breadcrumbs-text`, `--separator` |

The source also defines `--border-color`, `--widget-edit-bar`, `--impersonation-bar-bg`, `--widget-color`, `--focus-outline-color`, `--focus-outline-width`, `--focus-outline-radius`. Use `:root { ... }` in Dynamic Styles.

## The four customization scenarios (KB "Theme Customization")

| Scenario | Use when | Approach | Verdict |
|---|---|---|---|
| Styling only | colours, fonts, buttons, spacing, radius, dark mode | Tailwind theme config or CSS variables, no components | Supported (Dynamic Styles) or Customizable (Tailwind theme) |
| New styling and new pages, same functionality | landing, marketing, content, campaign pages | Page Builder pages, themed styling, optional new UI widgets | Supported, widgets Customizable |
| Full theme | unique branding, layouts, navigation, new widgets, multi-brand | new theme configuration, scaffolded package, theme widgets, base overrides, Tailwind theme, registration | Customizable |
| New styling, pages and changed functionality | custom checkout, product page behaviour, validation, integrations | custom theme plus overridden components, modified rendering, extended APIs | Customizable with source changes |

## Code theme wiring (summary)

Use the same lower-case name everywhere: Admin Theme Code or Name, the key in both theme loaders, and the Tailwind theme `name` and selector `[data-theme='<name>']` (the root layout sets this attribute on the html element). Tailwind uses `tailwindcss-themer`; both apps' Tailwind configs ship with an empty `themes` list. Full steps and the gaps in the KB: skill `webstore-customization` (recipes and `kb-vs-product.md`).

## B Store starter theme (KB)

Same experience as the parent store with exceptions: no colour changes by default; the home page shows the header message, the parent store's banner slider, banner title and subtitle and featured categories from the B Store catalog; the category page hides the 3-up promo slider, SKU, ratings and reviews and highlights; the product page hides the promo slider and the multi-warehouse inventory block; the cart hides the cart content container, promotions and estimate shipping; checkout hides additional info, vouchers and promotions.
