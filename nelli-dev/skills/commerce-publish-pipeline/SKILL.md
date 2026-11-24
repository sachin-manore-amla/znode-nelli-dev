---
name: commerce-publish-pipeline
description: Why a saved change in Znode Admin does not show on the storefront and what publishing is - the draft versus published model, the publish actions for catalog, category, product, store, content container, search profile, synonyms and 301 redirects, publish options (Preview and Production, Preview Only, Publish Draft Products Only), how to check progress, what refreshes caches after a publish, and how customization code should trigger or wait for a publish. Load it for any "I saved it but the storefront still shows the old value" problem, and before designing a customization that changes catalog, product, price, SEO, content or search data.
user-invocable: false
---

# Publish pipeline (what publishing is and how customizations should treat it)

Sources: Znode Knowledge Base articles Managing Catalogs, Configuring a Catalog, Editing a Catalog Name and Index Settings, Managing Stores, Managing Products, Configuring General Product Information, Managing a Content Container, Managing Synonyms, Managing Search Profiles, Managing PIM Index, Managing 301 Redirects, Znode Storefront Caching Architecture and Performance Guide, Storefront Performance and Caching Guidance (all read 2026-11-23). No exported API spec for publish operations was available: every API statement below is marked unverified.

## What publishing is
Admin edits are saved as working data. The storefront reads **published** data (and the search index built from it). Until a publish runs, shoppers keep seeing the last published version. Publishing is therefore the step that makes a change visible; it is not the same as saving. (KB 85: "Products must be published before they appear on the Storefront"; "Any updates to Product and Category data are only visible in published catalogs".)

## Eleven facts that matter
1. A catalog must be published before its products show on the webstore. PIM > Catalogs > **Publish**, then **View** to check progress. Duration depends on the number of categories and products. (KB 85)
2. Catalog and store publish offer a target: **Preview & production** or **Preview Only**. (KB 85)
3. **Publish Draft Products Only** is checked by default: only draft products are published. Uncheck it to publish every product in the catalog. (KB 85)
4. A **category** publish (right-click the category folder > Publish) publishes only the category settings, not its products. (KB 80)
5. A **product** publish (Publish icon in the product list, or Publish on the edit page) updates the product in every catalog it belongs to. Products are also published by a full catalog publish. (KB 85)
6. A product that is sold on its own and also a child, variant, bundle child or add-on needs its own publish, and its parent products must be published too, or the parent page may not show the change. (KB 80)
7. A **store** publish (Stores & Reps > Stores > Publish) has check boxes for **CMS content** and **Catalog** besides the target. Store settings changes (for example the primary catalog) need a store publish. (KB 85)
8. Changes to the catalog's **index settings**, to **stores, price lists or SEO** that feed indexed pricing, need a **Full Catalog Publish**; a PIM index creation alone is not sufficient. (KB 85: Editing a Catalog Name and Index Settings)
9. **Search profile edits, facets and synonyms** are published separately (Publish the search profile; **Publish Synonyms**). Publishing a catalog does not publish synonyms. (KB 85)
10. **301 redirects**: publish the store after creating, updating or deleting a redirect. (KB 85)
11. **Content containers** are Draft after any edit; publish the container before its variants. Editing a variant also sets the container to Draft. (KB 85)

## Where each kind of change needs a publish
| You changed | Publish | Reference |
|---|---|---|
| Product data, attributes, images, SEO of a product | Product publish, or catalog publish | `reference/publish-actions.md` |
| Category data | Category publish (settings only), or catalog publish | same |
| Catalog name, catalog index settings, price lists tied to indexed prices | Full catalog publish | same |
| Store settings, primary catalog, CMS content of the store | Store publish | same |
| Content container or variant | Container publish | same |
| Search profile, facets | Publish the search profile or rebuild the PIM index | `commerce-search-seo` |
| Synonyms | Publish Synonyms | `commerce-search-seo` |
| 301 redirect | Store publish | same |
| Voucher, inventory quantity, review status, tax rule, shipping method | No publish documented: these are read live. Product detail pages show inventory in near real time; listing pages may lag because of caching (KB 80) | `commerce-inventory`, `commerce-vouchers`, `config-caching` |

## After a publish: what refreshes and what does not
Publish events refresh the storefront data caches and page-structure caches automatically; the guest page cache and any CDN are **not** purged automatically and keep old copies until their time-to-live ends unless you purge. Details, timings and the purge call: `config-caching` and `reference/publish-and-caches.md`. (KB 85: Storefront Performance and Caching Guidance)

## Nelli-Dev decision guide
| Requirement | Verdict | Route |
|---|---|---|
| "Saved change not visible on the storefront" | Supported (diagnosis) | Walk the table above; confirm the publish ran (catalog View); then check the guest page cache and CDN (`config-caching`) |
| Make a nightly import of products visible without an admin | Customizable | Import the data (`config-import-export`), then trigger a publish. A publish API route exists in the platform but no exported spec was available to confirm it: look it up in the API reference (`api-catalog`, `nd_query_spec.py`) and label it unverified until confirmed |
| Know when a publish finished, from custom code | Customizable, unverified | Events and webhooks (`sdk-events-and-webhooks`): the KB lists modules such as User, Order and Product with Created, Updated, Deleted, and says the full event list is in a spreadsheet that was not readable. A dedicated "publish completed" event is **not documented**: say so, ask Znode support |
| Publish only the products I changed | Supported | Product publish, or catalog publish with Publish Draft Products Only checked |
| Publish on a schedule | Supported for content containers (Scheduler action, one-time scheduler). For catalogs the KB mentions a scheduler that updates catalog products but does not link it to the Publish action: unverified | `reference/publish-actions.md` |
| Instant visibility of a change for guests | Customizable | Purge step in the runbook, shorter cache times, or excluding the page (`config-caching`) |
| Change what publish does internally | Needs platform change | Not a customer extension point |

## Pitfalls
- Treating "saved" as "live". Add the publish step to every runbook and every customization that writes catalog data.
- Publishing a parent but not a standalone child (or the reverse): the page shows stale data.
- Unchecking Publish Draft Products Only on a large catalog without planning: all products publish.
- Expecting a catalog publish to publish synonyms, search profile edits or CDN content.
- Spurious "bug" reports from comparing Page Builder **preview** (reads current content) with the storefront (published only).

## Reference files
- `reference/publish-actions.md` – each publish action, options, progress, ordering and scheduling.
- `reference/publish-and-caches.md` – what each cache does on publish and how a customization waits for fresh data.

Related: `commerce-catalog`, `config-caching`, `commerce-search-seo`, `webstore-page-builder-and-themes`, `sdk-events-and-webhooks`.
