# Brands
What this answers: how to create, associate, show and hide brands, and what is known about import, SEO and the API.
Sources: KB Managing Brands, Adding a Brand, Associating Brands to a Store (read 2026-11-23). Confidence 85 unless marked.

## Create (three steps, order matters)
| Step | Path | Fields and actions |
|---|---|---|
| 1 Brand name | PIM > Product Attributes > Attributes > Attribute Code: Brands > Locale/Values tab | Add New; Brand Code, Display Order, Label; Save |
| 2 Brand manager page | PIM > Brands > Add New | brand details (fields not listed in the article); Save reloads with an **Associated Products** tab |
| 3 Associate products | PIM > Brands > Edit > Associated Products > Associate Products | select one or many; Save |
Rule: products can be related only after steps 1 and 2.

## Manage
- PIM > Brands lists brands. Brand Tools: Delete (permanent), Activate, Deactivate.
- Store scope: Stores and Reps > Stores > Manage > Brands > Associate Brands limits the Brands page and PDP to associated brands. Order follows the store's Display Order.
- Add brand pages to site navigation yourself if you want them linked (not in navigation by default: earlier note, unverified).

## SEO
Brand pages have SEO fields (title, description, keywords, friendly page name). The SEO rules for reserved words and URL keys are in `commerce-search-seo`; note that **brand** is a reserved keyword, so a brand SEO name must not equal it exactly.

## Import
A Brands import type exists (System Settings > Import). Columns recorded earlier by a person who read the KB: Brand Code (alphanumeric, starts with a letter), IsActive, SEOFriendlyPageName (unique across SEO entities), BrandDescription (up to 300 characters; no script or style content, which the web application firewall blocks), SEO keywords and description, SEOTitle, URLKey, BrandLogo (a file name already in the media library), Custom1 to Custom5. **Unverified in the articles read today**: confirm with the downloaded template.

## Hero image
KB "Configure a Hero Image for Brand Pages" is listed in Storefront Development; not read: read it before promising a layout.

## API
No exported spec. Published-brand read operations exist in the platform (list and by brand code) but names and routes were not confirmed: look up in the API reference and mark unverified until read.

## Customization notes
- Brand data is part of published catalog data: custom components should read it server-side with the platform cache tags so publish events refresh it (`config-caching`).
- A brand can be a facet or a search field (`commerce-search-seo`).
