---
name: commerce-brands-and-reviews
description: Znode brands (the Brand attribute value plus the brand manager page, the three-step creation order, product and store association, Brand Tools, storefront brand pages, brand hero image) and product reviews and ratings (Default Customer Review Status moderation, review fields, editing, storefront display, search relevance by rating and review count) with the API status and the customization verdict for each need. Load it for any brand page, brand filter, brand import, review moderation, rating display, review-based sorting or "reviews do not show" requirement.
user-invocable: false
---

# Brands and product reviews

Sources: Znode Knowledge Base articles Managing Brands, Adding a Brand, Associating Brands to a Store, Managing Product Reviews, Editing a Product Review, Configuring A Search Profile, Configuring Product SEO, Znode Storefront Caching Architecture and Performance Guide, Storefront Development folder (Configure a Hero Image for Brand Pages: listed, **not read**) (read 2026-11-23). No exported API spec for brands or reviews was available: API statements are unverified. Confidence 85 for Admin behaviour.

## Brands in one paragraph
A brand is two things: a value of the product attribute **Brand** (the thing assigned to products) and a **brand manager page** (landing page with brand information and associated products). A product can be associated only after both exist. Shoppers see each brand's landing page; admins choose which products it features. (KB 85)

## Brand facts
1. Menu: **PIM > Brands**. New brand names are added by editing the values of the product attribute **Brand**. (KB 85)
2. Creation order: (1) PIM > Product Attributes > Attributes > Attribute Code: Brands > **Locale/Values** tab: Brand Code, Display Order, Label, Save; (2) PIM > Brands > **Add New** (brand manager page; the individual fields are not listed in the article); (3) Brands > Edit > **Associated Products** tab > Associate Products > Save. (KB 85)
3. **Brand Tools**: Delete (permanent), Activate (show on the webstore), Deactivate (hide). (KB 85; the article's descriptions mention "products" but the actions apply to selected brands: treat as unverified wording)
4. **Associating brands to a store**: Stores and Reps > Stores > Manage > Brands > **Associate Brands**. It limits the Brands page and product detail pages of that store to the associated brands. Brand order follows the **Display Order** on the Manage Store screen (the Display Order column and field were removed from the Brands list and the Add/Edit Brand screen). Publish need not documented. (KB 80)
5. A search profile can match brand: the system-defined profile searches Product Name, SKU and Brand; brand is also in the default ngram fields. (KB 80, see `commerce-search-seo`)
6. Brand bulk import (columns, SEO fields, logo, custom values) exists in the platform but the Managing Brands article does not describe it; use the import template (`config-import-export`) and treat columns as unverified.
7. Brand pages: a hero image can be configured (article "Configure a Hero Image for Brand Pages" exists; **not read**, unverified).
8. Brand data is shared reference data in the storefront data cache and refreshes on publish events (`config-caching`).

## Review facts
1. Admin: **Marketing > Product Reviews**: edit or remove a review. (KB 85)
2. Moderation is a store setting: **Manage Store > General tab > Default Customer Review Status**: **Publish Immediately**, or **Do Not Publish Require Moderator Approval**. Reviews show on the product detail page only when published or approved. (KB 85)
3. Edit screen fields: Product Name (not editable), Headline, Comments, Username, User Location, Rating, Review Status, Created Date (not editable). The article does not say the others are editable nor list the status values: Published and Pending are expected but **unverified**. Buttons: Save, Save & Close. (KB 80)
4. A review is feedback on a product the customer purchased (KB definition); whether the platform enforces a purchase check is **not documented**.
5. Review and rating data feeds search: a search profile's relevance ranking can sort by **Rating** (average) or **Total Reviews**. A review update triggers cache invalidation of the product pages named in the event tags. (KB 85)
6. Not documented: how the average rating is computed, spam or abuse controls, bulk status change screens, an events or API surface for reviews.

## Nelli-Dev decision guide
| Requirement | Verdict | Route |
|---|---|---|
| Brand landing pages with logo and description | Supported | PIM > Brands; hero image article for the page header (read it first) |
| Limit a store to some brands | Supported | Associate Brands for the store |
| Brand filter on category pages | Supported | Brand attribute as a facet in the search profile (`commerce-search-seo`) |
| Import 500 brands | Supported (check template) | Brand import |
| Brand-specific content block (shipping notice per brand) | Customizable | Page Builder or CMS container targeted to the brand page, or a Webstore component reading published brand data (`webstore-customization`) |
| Hold reviews until approved | Supported | Do Not Publish Require Moderator Approval; approve in Marketing > Product Reviews |
| Show stars and count in a custom component | Customizable, unverified API | Read through the Webstore data layer (published product data) or the review operations in the API reference: confirm in the reference first |
| Only verified buyers may review | Not documented / Needs platform change | Block in your own UI or a custom endpoint wrapper; the platform check is not documented |
| Spam filtering, CAPTCHA on the review form | Customizable | CAPTCHA pattern from the KB "Implementing the Znode ReCaptcha feature on any additional pages" (listed, not read) |
| Send an email when a review arrives | Not documented | No review template in the default template list read; custom code via events if one exists (ask Znode) |
| Sort search by rating | Supported | Search profile relevance ranking: Rating or Total Reviews |
| Change how the average is calculated | Needs platform change | Not configurable as documented |

## Pitfalls
- Creating the brand page but not the Brand attribute value (or the reverse): products cannot be associated.
- Expecting new brands to appear without store association when a store is restricted to associated brands.
- Moderation set to publish immediately on a store that needs approval (default may differ per store).
- Reviews not appearing: check the status and the store's Default Customer Review Status, then the publish and cache layers (`commerce-publish-pipeline`, `config-caching`).
- Disabled or inactive brands still referenced by products in custom components.

## Reference files
- `reference/brands.md` – steps, fields, tools, store association, import and SEO notes.
- `reference/reviews.md` – moderation, edit screen, storefront and search effects, gaps.

Related: `commerce-catalog`, `commerce-product-attributes`, `commerce-search-seo`, `config-import-export`, `config-caching`.
