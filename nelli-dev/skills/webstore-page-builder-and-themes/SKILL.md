---
name: webstore-page-builder-and-themes
description: The Znode V10 Page Builder as seen by administrators and developers - where it is in Admin (CMS > Store Experience, CMS > Pages), the commerce pages and content pages it edits, the widget catalogue (layout, UI, Znode and page widgets) with their editable attributes, Save for Preview versus Publish, version history, multi-locale content, themes (CMS > Site Themes, parent and child themes, Dynamic Styles CSS variables, Tailwind themes, theme registration) and the Puck editor version and upgrade notes. Use when a requirement is about page layout, widgets, store look and feel, themes, content pages, locale content in Page Builder, or why a page or widget does not appear. Code-level steps for new widgets and themes are in webstore-customization.
user-invocable: false
---

# Page Builder and themes

Page Builder is a drag-and-drop editor (the Puck editor) that Admin opens in an embedded view. It edits two kinds of pages and the store header and footer. What it can render is defined by the widget registry in the Webstore source, so every limit an admin hits is either a setting here or a code change in `webstore-customization`.

Sources: KB articles "Page Builder - Introduction", "- Layout Widgets", "- UI Widgets", "- Znode Widgets", "- Multi-locale", "Commerce Pages configuration", "Configuring a Site Theme", "Dynamic Styles & Using Theme Dynamic Colors", "Managing the Store Experience", "Puck Plugin Upgrade (v0.21.1)", release notes 10.0.0.0 to 10.14.0.6 (all read), checked against the Webstore source (stamp 10.14.0.0).

## Ten facts that matter most

1. Entry points: CMS > Store Experience > choose the store > Commerce Pages (fixed pages: product, category, brand list, brand details, store locator, blog list, blog details, contact us, feedback, maintenance, cart, check-out, forgot password, track order, quick order, sign in, create an account), header and footer sections, and CMS > Pages > Content Pages (Page Builder icon in the Actions column).
2. A commerce page has one fixed page widget. Admins cannot delete, duplicate or move it; they edit its few fields and add widgets above or below. Cart and Check-Out came in 10.4.1.0; track order, quick order and forgot password in 10.11.1.0; sign in and create an account in 10.12.0.0.
3. Save for Preview pushes to preview and keeps a draft; Publish pushes to preview and production. Only published pages render for shoppers.
4. Widget groups in the panel: Layout (Container, Column, Vertical Space), UI Widgets (Text, Heading, Button Group, Text Image, Dynamic, Rich Text), Znode Widgets (Banner Slider, Offer Banner, Categories Carousel, Products Carousel, Brands Carousel, Ad Space, Homepage Promo, Image, Video, Newsletter, Link Panel, Form Widget, Content Block). Custom widgets appear only if developers add them.
5. Znode widgets are bound to Admin records (banner sliders, containers, forms, categories, products, brands). Their data is configured in those modules, then selected through the widget's gear icon.
6. A widget with no data shows a configuration message; after configuring, publish the page.
7. Page structure is the same in every locale; only content (text, images, videos, bound records) varies per locale, with fallback to the default locale.
8. Themes: CMS > Site Themes lists themes (ID, Name, Is Parent, Is System Defined, Parent). New themes are child themes of the B2B base theme. The store picks one under Store Experience > General Settings > Theme.
9. Quick style changes: Dynamic Styles CSS (General Settings) overriding the CSS variables of the starter theme; publish the store afterwards.
10. The editor is Puck 0.21.1 (upgraded from 0.17.4 in 10.9.1.0). Existing page JSON is migrated automatically; custom widgets must use slots instead of drop zones.

## Reference files

| Need | File |
|---|---|
| Admin paths, edit flow, actions, limits | `reference/admin-page-builder.md` |
| Every widget, its attributes, data source, empty message | `reference/widget-catalogue.md` |
| Themes, Dynamic Styles variables, Tailwind, registration | `reference/themes-and-styling.md` |
| Content pages, publish, versions, visibility | `reference/content-pages-publish-and-versions.md` |
| Multi-locale behaviour | `reference/multi-locale.md` |
| Puck version, upgrade impact, JSON migration | `reference/puck-and-upgrades.md` |
| Writing a widget or theme in code | skill `webstore-customization` |

## Nelli-Dev decision guide

| Requirement | Verdict | How |
|---|---|---|
| Rearrange the home page, add banners, carousels, promos | Supported | Page Builder on the home page (Commerce Pages) or header/footer |
| Add content around the product details, category, cart, checkout, login, sign up pages | Supported | widgets above or below the fixed page widget |
| Change labels and headings on contact us, feedback, quick order, track order, forgot password, login, signup | Supported | editable attributes of the page widget; locale-specific per locale |
| Show or hide category list, facets, reviews, SKU on the category page; hide brand names | Supported | Product List Page and Brand List attributes |
| Remove or reorder built-in sections inside the product page, cart or checkout | Needs code | theme page-widget override (Customizable) or base edit (source customization) |
| Embed a third-party script or form | Supported with care | Dynamic Widget (HTML, CSS, JavaScript) or Rich Text Widget; follow the performance guidance in the widget file |
| Brand colours, fonts, radii | Supported | Dynamic Styles variables |
| A different design system for one store | Customizable | new theme (child theme in Admin plus code) |
| New widget type | Customizable | code, `webstore-customization` recipe 1 |
| New commerce page code | Needs platform change | commerce page codes are fixed; use a content page or a code-only route |
| Page limit above about 35 widgets | Not advised | KB recommends 25 to 30 widgets per page, soft limit 35 |
| Different page layout per customer group | Supported partly | content pages can be tied to a profile (KB); commerce pages are per store |
| Edit page JSON by hand | Not advised | structure is versioned and migrated by the product |
