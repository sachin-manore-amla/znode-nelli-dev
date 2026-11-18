# Page Builder in Admin: paths, flow, actions and limits

What this answers: where administrators open Page Builder, the screen layout, the page types, the buttons (Save for Preview, Publish, Back) and what each does, and which fixed pages exist.
Confidence: KB "Page Builder - Introduction", "Commerce Pages configuration", "Webstore Customization Guide" use cases 5 to 7, release notes (read in full, 80); Webstore source for page codes (90).

## Where to open it

| Page type | Admin path |
|---|---|
| Commerce pages (fixed) | CMS > Store Experience > (store) > Manage Store > Commerce Pages; or CMS > Store Experience, store list, Page Builder icon |
| Header and footer | CMS > Store Experience > (store) > Sections > Header / Footer |
| Content pages | CMS > Pages > Content Pages, Page Builder icon in the Actions column, or Edit > Page Builder tab/button |
| Store theme, logo, favicon, Dynamic Styles | CMS > Store Experience > (store) > General Settings |
| Themes list | CMS > Site Themes |

Screen layout: left panel lists components (Layout, UI Widgets, Znode Widgets) with the Outline at the bottom; centre is the styled preview (header and footer shown, not editable on that page); right panel shows the attributes of the selected widget. All components are responsive for desktop, tablet and mobile.

## Fixed commerce pages and their predefined components

| Page | Component | Editable on the page |
|---|---|---|
| Product | Product Details Page | none |
| Category | Product Listing Page | Categories, Facets, Reviews, SKU switches (Yes/No) |
| Brand List | Brand List Page | Hide Brand Names (Yes/No) |
| Brand Details, Blog List, Blog Details, Store Locator, Cart, Checkout | respective page widget | none |
| Contact Us, Feedback | page widget | Heading, Description |
| Maintenance | Maintenance | text through the Rich Text Widget |
| Quick Order | Quick Order | heading, tabs (Search, Paste Multiple), instructions, step texts, button labels |
| Track Order | Order Status | heading, Add to Cart and Clear All Items button labels |
| Forgot Password | Forgot Password | heading, description, Submit and Cancel labels |
| Sign In | Login | form heading, sign-in button, new account heading, description and button, checkout as guest description and button |
| Create An Account | Signup | register form heading, signup and cancel buttons, existing account heading, login now button |

Rules for predefined components (KB): always present and visible; cannot be deleted or duplicated; only the fields above are editable; extra widgets can go above or below only. "Checkout as Guest" visibility follows the store settings Login to see Price and Inventory and Login Required, not the editor. The editor shows the email field regardless of the store's User Registration Method; the storefront follows the flag.

In the source, the page code for these pages is fixed in code (`PAGE_CODES`), so a new commerce page cannot be added by configuration.

## Actions

| Button | Effect |
|---|---|
| Save for Preview | pushes to the preview environment and saves a draft |
| Publish | pushes to preview and production |
| Back | discards unsaved changes and returns; you start over next time |
| Preview | shows the page in the preview pane |
| Locale selector (header) | switches the content locale (since 10.6.0.0) |
| Version history | list of Draft and Published (Live) versions; restore loads a version on the canvas |

The editor warns about unsaved changes when you leave ("You forgot to save your changes...").

## Limits and guidance

- 25 to 30 widgets per page recommended, soft limit 35 (KB "UI Widgets").
- Dynamic Widget: third-party HTML, CSS and JavaScript. Keep scripts small, avoid heavy libraries, limit DOM depth and animation, defer non-critical scripts (KB guidelines).
- Rich Text Widget: WYSIWYG for lists and links; HTML, CSS and JavaScript still allowed.
- Widgets disabled in CMS are not rendered on the storefront (fix in 10.2.0.0).

## Behaviour to know

| Behaviour | Version |
|---|---|
| Flex component renamed Container; side-specific borders for Heading and Container | 10.4.0.0, 10.9.1.0 |
| Page JSON of existing pages updated automatically when a new Page Builder release ships | 10.4.0.0 |
| Cart and Check-Out in Page Builder | 10.4.1.0 |
| Multi-locale editing | 10.6.0.0 |
| Hide Brand Names attribute | 10.9.0.0 |
| Puck 0.21.1 (plugin rail, resizable sidebars, outline navigation, slot architecture) | 10.9.1.0 |
| Track Order, Quick Order, Forgot Password pages | 10.11.1.0 |
| Sign In and Create an Account pages | 10.12.0.0 |
| "Page Builder Application URL" setting removed from Global Settings | 10.8.1.0 |
| Newer features need a current Storefront version (10.12.1.0 note) | 10.12.1.0 |
