# Publish actions
What this answers: where each publish action lives, its options, how to check it, and ordering rules.
Sources: KB Managing Catalogs, Configuring a Catalog, Editing a Catalog Name and Index Settings, Managing Stores, Managing Products, Configuring General Product Information, Managing a Content Container, Managing PIM Index, Managing CMS Content Search Index, Managing Synonyms, Managing Search Profiles, Managing 301 Redirects (read 2026-11-23). Confidence 80-85 unless marked.

## Catalog
- Admin: **PIM > Catalogs > Publish**; progress with **View**.
- Options: **Preview & production** or **Preview Only**; **Publish Draft Products Only** (checked by default).
- Covers the catalog, its categories and its products (subject to the draft-only option).
- A published catalog can be associated with any store, account or user profile; an unpublished catalog only with user profiles.
- Deleting a catalog: first move the store to another primary catalog (Store Settings > General > Catalog), publish the store settings, and publish the alternative catalog if needed.
- Copying a catalog does not copy schedulers or index settings.
- Publish history: the KB does not describe one. Status: the **View** action only.

## Catalog index settings
- Catalog > Edit name and index settings: toggle **Display Pricing and SEO Details of Products from Index** (off by default; needs a **Default Store**). Save keeps a draft; behaviour changes only after the catalog is published.
- Enabling or disabling the toggle needs a **Full Catalog Publish**. Changes to stores, price lists or SEO need a new full publish. Products added after publishing have no indexed pricing until the next publish; removed prices are not reflected until republish; a catalog name change shows only after publish.

## Category
- Right-click a category folder > **Publish**: only the category settings. Products associated with it are not published. (KB 80)
- Removing a category association from a product removes the derived catalog associations only after the product or the catalog is published.

## Product
- Publish icon in the product list, or the **Publish** button on the edit page (saves and publishes). Publishing during create or edit is optional.
- Publishing a product updates it in all catalogs it belongs to.
- Standalone child products (child, variant, bundle child, add-on that can be sold alone): publish them and the parents that reference them.
- Bulk publish: not described in the articles read; "Bulk Updating Products" was not read (unverified).
- Product edits that depend on search: tags are searchable only when the Tags attribute has **Is Used In Search**, is in the search profile, and the search profile is published.

## Store
- Stores & Reps > Stores > **Publish** icon; modal: target (Preview & production or Preview Only), **CMS content**, **Catalog**, **Publish Draft Products Only** (checked when Catalog is checked), then **Proceed**.
- The article says the store is published once all details are added. A **Store Mode** column is blank for a new store until it is published (Maintenance Settings article).
- Store publish is also required after 301 redirect changes.

## Content container
- List page **Publish** icon publishes all variants that have data for the locales. Edit screen has Save, Save & Close and Publish (Save and Save & Close do not publish).
- New container and variant start as Draft. Editing a variant makes the container Draft; editing the container leaves variants alone. Publish the container before its variants.
- Storefront picks the first match in this order: store+profile+selected locale, store+profile+default locale, store+any profile+selected locale, store+any profile+default locale, any store+any profile+selected locale, any store+any profile+default locale. The "any store, any profile, default locale" variant is mandatory.
- Scheduler: a one-time scheduler with start date and time runs only when Enabled; what it does exactly (publish or not) is not stated: unverified.

## Search objects
- PIM index: publishing a catalog creates its indexes (one for the Production URL, one for Preview). **Create Index** rebuilds; **Create Schedule** schedules a rebuild. Publishing new index settings creates an index with them.
- CMS content search index: updated automatically when CMS and Blog/News pages are published and **Enable CMS Based Search** is checked; **Create Index** does it manually.
- Search profile: edits to the default profile appear only after the search index is rebuilt (publish the catalog or use Create/Update the Index).
- Synonyms: **Publish Synonyms**; unpublished changes can take effect if an index is created under a new name.

## Ordering that avoids stale pages
1. Data (import or admin edits). 2. Product or catalog publish. 3. Search profile or synonyms publish if search config changed. 4. Store publish if store settings, redirects or CMS content changed. 5. Purge guest page cache and CDN if guests must see it now (`config-caching`).

## What is not documented (say "not documented", not "not supported")
- A publish history screen; a failure status or error list; a publish API route (unverified); an event emitted when a publish finishes; maximum publish duration.
