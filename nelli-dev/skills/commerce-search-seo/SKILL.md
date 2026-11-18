---
name: commerce-search-seo
description: Znode Elasticsearch search configuration (what is indexed, the analyzer chain, search profiles, facets, typeahead modes, Did You Mean, triggers, keyword redirects, product highlights) and the SEO model (per-entity fields, substitution variables, URL key rules, robots.txt, redirects). Use when tuning search relevance, adding a facet, or working on SEO URLs and metadata.
user-invocable: false
---

# Znode Search & SEO

## What is indexed

| Index | Source | Updated |
|---|---|---|
| **PIM index** (per catalog) | Products, SKUs, attributes marked *Is Used in Search* | On catalog Publish (full or incremental). Two indexes per catalog: Production URL + Preview URL |
| **CMS index** (per store) | CMS pages, Blog/News articles | Automatically on publish when *Enable CMS Based Search* is on; also manual from `Marketing > Site Search` |

With CMS search on, a **Pages** tab appears alongside **Products** on storefront results.

## Analyzer pipeline (Standard Analyzer)

1. Character filter — strips `_ - / ( ) . :` etc.
2. Tokenizer — splits into word tokens
3. Lowercase
4. Synonyms — configurable expansion
5. Stopwords
6. **Ngram** on Product Name, SKU, Brand — min 3 / max 20 by default (partial-word matching)
7. **Shingle** — adjacent word pairs, speeds up phrase queries

## Search profiles

`Marketing > Site Search > Search Profiles`

| Option | Values |
|---|---|
| Searchable Fields | Any product attributes, each with a boost score 1–999 |
| Relevance Ranking | Price, Rating or Review Count (asc/desc) |
| Query Type | Multi-Match **Best** (all terms in one field) or **Cross** (terms across fields) |
| Operator | AND (all keywords) or OR (any) |
| Autocorrect | Fixes up to 2-character typos on keywords longer than 2 chars |

System default fallback: Product Name + SKU + Brand, Multi-Match Cross / AND / no autocorrect.

**Facets:** configured per search profile under the Facets tab. Display order comes from each attribute's own **Display Order**, not the association sequence. Facets publish as part of the search profile publish.

## Typeahead modes

| Mode | Behaviour |
|---|---|
| Default Typeahead | Products, brands, categories as you type; max 5 per group |
| Enhanced Typeahead | Suggestions become faceted filters; configurable Search Suggestions, Category Facets and a 3/6/9 product recommendation grid |
| Hydrated Search | Shown on first click before typing — My Searches, Popular Products/Brands/Searches/Categories. Driven by order data, refreshed by a configurable scheduler |
| Voice Search | Speech-to-text into the standard flow (needs a Google Speech API key) |
| Barcode Search | Scans a QR/barcode (needs a Dynamsoft licence key in `web.config`) |

## Did You Mean (DYM)

Spelling correction on **zero-result** searches, powered by Elasticsearch suggesters. Searching "diwalt" with no hits offers *Did you mean: dewalt?*; clicking re-runs the search.

Configured at the **PIM Index** level, not the search profile: `Marketing > Site Search > Manage PIM Indexes > [index] > PIM Index Settings > Search Behavior`.

| Setting | Notes |
|---|---|
| Enable Did You Mean | **Disabled by default** |
| Maximum Suggestions | up to **5**, ranked by relevance |
| DYM Attributes | Product Name · SKU · Brand — each must have `Use In Search = Yes` |

> **Any DYM configuration change requires a full PIM index rebuild (recreate)** — suggestion data is generated during indexing, so without a republish the change has no effect.

The "Did you mean:" block renders **only** when DYM is enabled, the search returned **zero** results, and valid suggestions exist.

## Triggers

`Marketing > Site Search > Search Profiles > Edit > Triggers` — associate one or more **User Profiles** with optional **Keywords** to control what surfaces on the storefront for those segments.

**Keyword redirects** (`Marketing > Site Search > Keyword Redirects`): a configured keyword sends the buyer to a specific URL instead of the results page.

**Product Highlights** (`Marketing > Product Highlights`): informational PDP labels ("Made in the USA"). Fields: Locale, Highlight Type, Display Order, Name, On-Click Behaviour (third-party URL or inline description). Supports attribute macros such as `<brand>`. Associated to products via the **Highlights** product attribute.

## SEO fields (products, categories, content pages)

`Marketing > SEO Setup`

| Field | HTML output |
|---|---|
| SEO Title | `<title>` |
| SEO Description | `<meta name="description">` |
| SEO Keywords | `<meta name="keywords">` |
| SEO-Friendly Page Name | URL slug |
| Canonical URL | `<link rel="canonical">` — defaults to the SEO-friendly URL |
| Robot Tag | `<meta name="robots">` — INDEX/FOLLOW, NOINDEX/NOFOLLOW, NOINDEX/FOLLOW, INDEX/NOFOLLOW |
| Is Redirect | TRUE = 301 from the old URL, FALSE = 404 |
| Locale | SEO settings are localizable per store locale |

### Default SEO Settings

`Marketing > SEO Setup > Default SEO Settings` — **scoped per store**, used whenever a product, category or content page has no SEO values of its own. Nine fields: **SEO Product / Category / Content** × **Title / Description / Keyword**.

Substitution variables are resolved at render time:

| Variable | Substitutes | Available on |
|---|---|---|
| `<NAME>` | Product name, category name or content page title | all three |
| `<PRODUCT_NUM>` | Product number | product pages only |
| `<SKU>` | Product SKU | product pages only |
| `<BRAND>` | Product brand | product pages only |

Category and Content defaults accept `<NAME>` only. Free text can be concatenated around a variable — `Shop now at mystore.com for <NAME>`.

> **Saving an empty default emits an empty meta tag.** Blank Default SEO Settings are written into the storefront HTML as empty values rather than being skipped.

## URL key rules

- Allowed characters: alphanumeric, `_`, `-`, `/`
- Must not begin or end with `/`
- Cannot match reserved system paths: `content`, `product`, `blog`, `brand`, `account`, `cart`, `checkout`, `compare-product`, `contactus`, `feedback`, `forgot-password`, `highlight`, `login`, `order`, `order-status`, `pending-order`, `punchout`, `quick-order`, and others. Plural variants (e.g. `products`) are allowed.
- Blank ⇒ Znode generates a URL from the entity's internal ID.

## Robots & redirects

- `Stores and Reps > Stores > Manage > Robots.txt` — free-text content plus a **Default Page Level Robot Tag**. A page-level tag overrides the store default.
- Per-entity redirect: the **Is Redirect** toggle on each entity's SEO tab.
- Global: `Marketing > SEO Setup > 301 URL Redirects`.

## KB source

- [Managing Site Search](https://support.znode.com/support/solutions/folders/43000598143)
- [Managing SEO](https://support.znode.com/support/solutions/folders/43000598142)

## Related
`commerce-catalog` · `commerce-product-attributes`
