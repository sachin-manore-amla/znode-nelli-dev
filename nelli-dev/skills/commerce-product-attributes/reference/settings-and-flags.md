# Settings and flags

What this answers: every setting or flag that changes how attributes, groups, families and custom fields behave, with where it is set, its level, default and what must happen for it to take effect.
Attribute behaviour itself is controlled mostly by the per-attribute flags (see attribute-types-and-rules.md); this file lists the surrounding settings.

## Per-attribute flags (level: attribute)

| Flag (Admin label) | Value | Default | Needs | API |
|---|---|---|---|---|
| `Required` | Yes/No | Yes on a new attribute in the model default; set per attribute | Applies on the next product save; locked for four system attributes | `IsRequired` on the attribute model |
| `Is Configurable` | Yes/No (Simple Select only) | No | New configurable products pick it up | `IsConfigurable`, also published |
| `Is Personalizable` | Yes/No (Text only) | No | Immediate in Admin; publish for the storefront | `IsPersonalizable`, published |
| `Is localizable` | Yes/No | No | Next save; publish | `IsLocalizable` |
| `Is Show On Grid` | Yes/No | per page | Immediate on the PIM list | `IsShowOnGrid` |
| `Is Comparable` | Yes/No | No | Publish | `IsComparable`, published |
| `Is used in Search` | Yes/No | No | Search profile and a full publish (publish-and-search-effects.md) | `IsUseInSearch`, published |
| `Is used for facets` | Yes/No (select types) | No | Full publish | `IsFacets`, published |
| `Unique Value` | on (Text) | off | Next save | validation rule |

## Platform settings that matter

| Setting | Admin path | Level | Default | Effect | Takes effect |
|---|---|---|---|---|---|
| Default locale and active locales | `Dev Center > Global Settings > Locales` | Global | one active locale (English) on a standard install | Decides the name languages offered for attributes, groups, families and the rows on custom fields. Items without a default-language name are hidden from lists and pickers. | After the settings cache timeout (default 20 minutes) |
| Publish Draft Products Only | `PIM > Catalogs > Publish` checkbox; catalog scheduler | Per publish | ticked (draft only) | Ticked: only Draft products are re-published and the live index is updated in place. Unticked: whole catalog, new search index. | Per publish |
| Catalog Index Settings (ngram, character filter, `Display Pricing and SEO Details of Products from Index`) | `PIM > Catalogs` index settings; PIM Index screen | Catalog / global `All` | global: ngram on Product Name and SKU, Min Gram 3, Max Gram 20 | Analysis of searchable fields | Full publish or `Create Index` |
| Search profile | `Marketing > Site Search > Search Profiles` (Searchable Fields with boost, and a Facets tab) | Profile (assigned to stores) | system default: Product Name, SKU, Brand | Which attributes are searchable and boosted, and which attributes are offered as facets | Profile published; read live (KB summary, 70) |
| Roles and permissions | `Dev Center > Roles & Access Rights` | Role | Admin role all | Read Only, Write, Edit, Delete per menu. Product and category attribute screens are separate menus; custom fields use the Products menu | Next request |
| Server time zone | `Dev Center > Global Settings > General` | Global | UTC | Dates written on saves | Next save |
| Enable Audit Log | `Dev Center > Global Settings > Audit Log Data Purge` | Global | off | No effect on these tables | |
| Custom publish procedures switch | `Dev Center > Custom SP` | Global | off | When on, a customer's own procedure replaces the copy step of publish; the shipped template does nothing so the index is built from old data | Next publish |
| Webstore data cache and revalidation | Webstore environment settings (`ENABLE_CACHE`, revalidate secret) | Webstore | cache on | Published product reads are cached until a publish revalidates; a wrong secret leaves caches stale | After revalidation |

(Module guide, 85; KB, 80. Admin paths follow the module guide wording; the KB uses "Global Settings" without the `Dev Center >` prefix in places.)

## What has no setting

No store, catalog, profile, currency, country or feature flag switches the attribute, group or family rules on or off. Families and groups are global to PIM, not per store. There is no global setting to enable product custom fields; the tab exists when the family carries the Custom Fields group.

## API visibility

The per-attribute flags are visible in the v1 attribute model and in the published attributes (`IsComparable`, `IsFacets`, `IsUseInSearch`, `IsConfigurable`, `IsPersonalizable`, `IsCustomField`, `IsSwatch`, `IsHtmlTags`). Platform settings are not exposed through the attribute APIs.
