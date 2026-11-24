---
name: commerce-search-seo
description: Znode storefront search and SEO - what the PIM and CMS indexes hold and when they rebuild, search profiles (searchable fields and boost, relevance ranking, query type, operator, autocorrect), facets, triggers, synonyms, Boost and Bury, keyword redirects, Did You Mean, typeahead and other Search Settings, how ranking works, then SEO fields, default SEO substitution variables, URL key rules and the Disable SEO Validations setting, 301 redirects and robots.txt, with the customization verdict per need and what needs a publish or reindex. Load it for any search relevance, facet, suggestion, synonym, redirect, URL, meta tag or robots requirement and when a search or URL change does not show.
user-invocable: false
---

# Search and SEO

Sources: Znode Knowledge Base articles Configuring A Search Profile, Managing Search Profiles, Managing PIM Index, Managing CMS Content Search Index, Configuring Facets, Configuring Triggers, Managing Synonyms, Managing Boost and Bury, Managing Keyword Redirects, Configuring and Managing - Did You Mean (DYM), Managing Search Settings, Typeahead Search on the Storefront, Understanding How Znode Search Ranks Results, Elasticsearch Configuration Used During Indexing, Managing SEO, Managing Product SEO, Managing 301 Redirects, Editing the Robots.txt File for a Store, Manage SEO Validation Settings, Managing Products (read 2026-11-23). Not read: How Search Results are Sorted, Search Suggestions, Elasticsearch searching and definitions, Configuring Custom URLs, Search Activity Reports, Managing Category SEO, Managing Content Page SEO. No exported API spec for search or SEO was available. Confidence 85 unless marked.

## How search works in one paragraph
Znode search runs on Elasticsearch. Published catalog data is indexed into a **PIM index** per catalog (a Production URL index and a Preview URL index). The storefront uses the catalog's **default search profile** (or the system-defined profile) against the current index. CMS pages and Blog/News pages can have a **CMS content index** per store. Ranking uses the Okapi BM25 algorithm (term frequency, inverse document frequency, document length), then boosts, buries and relevance ranking from the profile.

## Fifteen facts that matter
1. Publishing a catalog creates its PIM indexes; **Create Index** (Marketing > Site Search > Manage PIM Indexes) rebuilds; **Create Schedule** schedules a rebuild. (KB 85)
2. Searchable fields are product attributes with **Is Used in Search** = TRUE. (KB 85)
3. Only the profile marked **Default** is used on the storefront; edits to other profiles change nothing. A catalog without a profile uses the system-defined profile (Product Name, SKU, Brand; Multi-Match Cross; AND; no autocorrect). (KB 85)
4. Edits to the default profile appear only after the index is rebuilt (publish the catalog, or Create/Update the Index). (KB 85)
5. New profile defaults: fields Product Name and SKU, relevance ranking NA, Multi-Match Cross, AND, autocorrect No. Boost Score 1 to 999. (KB 85)
6. **Autocorrect is not supported with Multi-Match Cross**; allowed corrections 0 for keyword length 0-2, 1 for 3-5, 2 above 5. (KB 85)
7. Relevance ranking options: Price, Rating, Total Reviews, ascending or descending. (KB 85)
8. Facets: profile > Facets tab > Associate Facets > save > **publish the search profile**; order follows each attribute's Display Order. (KB 85)
9. Triggers (profile > Triggers): User Profiles (multi-select) plus optional Keywords; Add New, Edit, Delete. Trigger types are not listed. (KB 70)
10. Synonyms (Marketing > Site Search > Synonyms): single-direction or bidirectional (default); no single or double quotes (index creation fails); **Publish Synonyms** starts index creation; a catalog publish does not publish synonyms. (KB 85)
11. Boost and Bury (Marketing > Site Search > Boost & Bury): Boost Value 1.01 to 999 promotes, 0.01 to 0.99 demotes, 1 no effect; start 00:00, end 23:59; Pause and Restart; per catalog. No publish step is documented. (KB 80)
12. Keyword redirects: per catalog, Keywords and URL (path or full URL). Matching rules and priority are not documented. (KB 80)
13. **Did You Mean**: off by default; enabled per PIM index (PIM Index Settings > Search Behavior); Maximum Suggestions up to 5; attributes Product Name, SKU, Brand with Use In Search = Yes; **any change requires a full index rebuild**; shown only when enabled, zero results and suggestions exist. (KB 85)
14. Search Settings (Marketing > Search Settings; All Stores default, store override): Enable Voice Search, Enable Barcode Scanning & Search, Enable CMS Search, Enable Hydrated Search, Enable Enhanced Typeahead Search. Typeahead needs at least 3 characters. (KB 80)
15. SEO URLs: **SEO-Friendly Page Name** rules and the **Disable SEO Validations** global setting (Global Settings > SEO Validation Settings); changing a URL redirects the old one only if **Is Redirect** is on, else 404. (KB 85)

## What needs a publish or reindex
| Change | Needed |
|---|---|
| Product data, searchable attribute | Catalog or product publish; new attribute-in-search needs profile publish |
| Profile fields, boost, query settings | Rebuild index (publish catalog or Create/Update the Index) |
| Facets | Publish the search profile |
| Synonyms | Publish Synonyms |
| DYM, ngram or character filter settings | Full index rebuild; publishing new index settings creates the index |
| CMS pages or Blog | Publish; CMS index updates automatically when Enable CMS Based Search is on, or Create Index |
| 301 redirect | Publish the store |
| Typeahead | Products published, indexing done, Typeahead enabled; product changes may need re-indexing |
See `commerce-publish-pipeline`.

## Nelli-Dev decision guide
| Requirement | Verdict | Route |
|---|---|---|
| Find products by part number with typos | Supported | SKU in searchable fields with boost; ngram on Product Name and SKU is a default; autocorrect (not with Cross) |
| Search custom attribute (colour code) | Supported | Mark attribute Is Used in Search; add to profile; rebuild index |
| Rank by newest or margin | Not documented | Relevance ranking offers Price, Rating, Total Reviews only; other signals need Boost and Bury per keyword or a platform change |
| Boost a brand for a keyword | Supported | Boost and Bury with trigger keyword |
| Different search per customer segment | Supported | Triggers with User Profiles; profile-based catalogs |
| Redirect "warranty" to a page | Supported | Keyword Redirects |
| Facets for a custom attribute | Supported | Attribute facet association, then publish the profile |
| Replace the search engine or ranking algorithm | Needs platform change | Not an extension point |
| Custom search results page UI | Customizable | Webstore customization reading the search API (`webstore-customization`, `api-consumption`) |
| Meta tags per product from rules | Supported | Default SEO Settings with substitution variables |
| Custom URL structure (/p/sku) | Supported within the key rules | SEO-Friendly Page Name; disabling validation allows any value (use sparingly) |
| Bulk SEO update | Customizable | Import (`config-import-export`) or API; routes unverified |
| Sitemap generation | Not documented | Not covered by the articles read: ask Znode |
| Search analytics | Partly | Search Activity Reports exists (not read) |

## Pitfalls
- Editing a non-default profile and expecting an effect.
- Forgetting to rebuild or publish after profile, DYM or synonym changes.
- Autocorrect with Multi-Match Cross (not supported).
- Quotes in synonyms (index creation fails; previous synonyms stay live).
- Saving blank Default SEO Settings: empty tags are written into the HTML.
- URL keys equal to reserved words (content, product, brand, cart, checkout, account, order, search, return, category and others); plural forms are fine.
- Product edit without publish: neither SEO nor search sees it.
- KB inconsistency: the Indexing article gives ngram length 1 to 40, the PIM Index article gives defaults Min Gram 3 and Max Gram 20: read the PIM index settings screen on your environment.

## Reference files
- `reference/search-configuration.md` – index, profile, facets, triggers, synonyms, boost and bury, redirects, DYM, typeahead, settings, ranking.
- `reference/seo.md` – SEO fields, defaults, URL rules, validation setting, 301 redirects, robots.txt.

Related: `commerce-catalog`, `commerce-product-attributes`, `commerce-brands-and-reviews`, `commerce-publish-pipeline`, `config-caching`, `webstore-cms`.
