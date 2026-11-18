# Publish and search effects

What this answers: which attributes reach the storefront and search, what needs a publish or re-index, and how the Webstore uses attribute flags.
Facts tagged: product source or development environment (90), module guide (85), KB read in full (80), inference (under 50).

## What publish does

PIM data is a draft. Shoppers see the published copy. KB: "Products must be published before they appear on the Storefront." Publishing updates the product in all catalogs that contain it. A saved attribute value, custom field, attribute group, family or flag change is not visible to shoppers until the product or catalog is published. (KB, 80; module guide, 85)

Published per product: every attribute the product uses, regardless of flags. Each published attribute carries its code, name, value, type, display order and the flags `IsUseInSearch`, `IsFacets`, `IsComparable`, `IsHtmlTags`, `IsPersonalizable`, `IsCustomField`, `IsConfigurable`, `IsSwatch`. (module guide, from source)

| Included | Notes |
|---|---|
| Attributes with a value | The family's default value fills in when the product has none |
| Simple / Multi Select | The selected options, or the default option when none is selected. A configurable parent also carries its variants' options |
| Media (Image, File) | As full addresses |
| Link attributes | As a list of SKUs |
| Personalizable attributes | Published even when empty |
| Product custom fields | As text attributes marked custom field (see the known issue in product-custom-fields.md) |
| Category attributes | Published with the categories, not with the product |

Left out: an attribute with no value and no family default. Whole product left out: no Product Type value; configurable, bundle or grouped with no child; (draft publish only) a product not in Draft; an inactive product is removed. Locales: every active locale of every store using the catalog; a missing locale value falls back to the default locale; a catalog in no store publishes the default locale only.

## What needs a publish

| Change | Needs | Basis |
|---|---|---|
| New or changed attribute value on a product | Product or catalog publish. The product becomes Draft on save, so a draft-only publish picks it up | module guide, 85 |
| Custom field add, edit, delete | Same (the product is marked Draft) | module guide, 85 |
| Change an attribute definition: flags (`Is used in Search`, `Is used for facets`, `Is Comparable`), option labels, swatches, names | A full catalog publish (inference: an attribute edit does not mark products Draft, so a draft-only publish skips them; not verified) | inference, 50 |
| Add or remove an attribute, group or family assignment | Same as above; values are kept when removed | module guide, 85 |
| Change a product's family | Save marks the product Draft; publish it | module guide, 85 |
| Locale label of a family or group | Never reaches the storefront | module guide, 85 |
| Group or family display order | Not used by publish or the storefront | module guide, 85 |
| Search profile settings (field boosts, triggers) | Read live; no publish for the profile itself, but attributes must be in the published data. The KB for tag search says: the attribute needs `Is Used In Search` on, to be in the search profile, and the profile published | KB, 80 |
| Analyzers, synonyms, ngram and index settings | Take effect only with a new index (full catalog publish or index re-create) | module guide, 85 |
| Catalog index setting `Display Pricing and SEO Details of Products from Index` | A full publish | KB, 80 |

KB "What Requires Publishing" (https://support.znode.com/support/solutions/articles/43000757211-what-requires-publishing) lists products, categories, catalogs, media and SEO as needing publish and does not mention attributes, groups, families or custom fields.

## Search and facets

- The product page and the search document carry every published attribute.
- Facet copies are made only for attributes with `Is used for facets` (Simple Select or Multi Select). Which facets a store shows is also set per search profile on the Facets tab (`Marketing > Site Search > Search Profiles`); facets publish with the search profile publish, and each facet's order follows the attribute's own Display Order (KB summary, 70).
- Search copies are made only for Simple Select or Multi Select attributes that are in a search profile with `Is used in Search`. Text-type attributes with `Is used in Search` are included in text search per the KB; confirm per profile.
- Known defect recorded by the module guide: with no search-profile mapping and two or more attributes in the default index setting, no search or facet copies were made on the build checked. Always verify facets after the first publish.
- Searchable fields have ngram settings on `Product Name` and `SKU` by default (global index setting `All`: Min Gram 3, Max Gram 20); the KB (Managing PIM Index) does not say whether changing `Is used in Search` needs a re-index. Rebuild with `Create Index` or `Create Schedule` on the PIM Index screen if results look stale.
- Index creation and publish status: release 10.8.0.0 changed catalog index status to Started, Processing, Completed.

## How the Webstore uses attribute flags

- Compare: attributes with `Is Comparable` appear in comparison (`GET /v2/published-products/{productSKUs}/compare-products`).
- Filters: the Webstore's facet and search calls use attributes with `Is used for facets` (the facet route is not in the exported public specification; confirm in the API reference).
- Product page tabs are built from three fixed attributes (Product Specification, Shipping Information, Long Description) plus `Additional Information` from custom fields; other attributes appear where the theme template renders them. (Webstore source, 90)
- Variant selectors and swatches come from `IsConfigurable` and `IsSwatch`.
- Personalization renders a text input for personalizable Text attributes; Add to Cart waits until it is valid.

## Cache

The Webstore keeps published product reads in its data cache until a publish triggers revalidation, so a published change may need the revalidate call to be configured (`webstore-customization`, KB: Secure Cache Revalidation Configuration).