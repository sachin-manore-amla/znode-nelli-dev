---
name: webstore-cms
description: Znode CMS content types - Store Experience, Content Pages, Content Containers with their default variant, draft/publish semantics and scheduler, Banner Sliders, Blog/News, forms and form builder, and locale-specific content rules. Use when authoring or debugging CMS content, container variants, banners, or custom forms.
user-invocable: false
---

# Znode CMS Content Types

| Concept | Description |
|---|---|
| **Store Experience** | The global presentation shell — theme, logo, favicon, header, footer, homepage layout, dynamic CSS. All pages inherit from it |
| **Content Page** | A standalone URL-routable page using a Page Template |
| **Content Container** | A reusable embeddable fragment with personalized variants — no URL |
| **Banner Slider** | A named set of image/text slides consumed by slider widgets |

## Content Pages

- Template required (developer-defined widget layout registered in code), then filled via widgets or Page Builder drag-and-drop.
- Per page: Store, User Profile, locale, SEO, activation/expiration dates.
- Versioning: Save → Draft, Publish → Live, with version history for rollback (`GET /v2/visual-editor/{pageType}/{pageCode}/versions`, `POST /v2/{pageType}/{pageCode}/restore/{versionNumber}`).
- Two built-in themes: **Default** and **B2B** (downloadable, customizable, uploadable).

## Content Containers

`CMS > Containers`. Fields: **Container Key** · Container Name · **Tags** · **Container Family** (defined under Global Attributes). **Container Key and Container Family cannot be changed after creation.**

### The default variant — KB-confirmed

A container **cannot be created** until data for the default variant — **"Any Store, Any User Profile"** — is supplied for the default locale. That variant **cannot be deactivated or deleted**. It is the guaranteed fallback.

### Variant fallback chain — ⚠️ unverified

One Container Key can hold many variants scoped by store, profile and locale, and the most specific match wins. This ordering comes from `Architecture.md` and is **not documented in the KB**; only the default-variant rule above is confirmed. Verify before relying on it:

| Priority | Scope |
|---|---|
| 1 | Specific Store + Specific Profile + Selected Locale |
| 2 | Specific Store + Specific Profile + Default Locale |
| 3 | Specific Store + Any Profile + Selected Locale |
| 4 | Specific Store + Any Profile + Default Locale |
| 5 | Any Store + Any Profile + Selected Locale |
| 6 | Any Store + Any Profile + Default Locale — mandatory fallback |

### Draft and publish semantics

- Creating a container **or** a variant sets status **Draft**.
- Editing **any variant** flips the **container** to Draft — but editing the container does **not** flip its variants.
- The **container must be published** for its variants to publish; publishing a container publishes every variant that has data for a locale.
- With multiple variants, publishing one leaves only that variant published; the rest inherit the container's status.

Referenced on pages via the **Ad Space** and **Homepage Promo** widgets.

### Container scheduler

Containers can be scheduled from the list's scheduler action: **TouchPoint Name** (auto-generated, type defaults to Scheduled) · **Scheduler Name** (set at creation, then immutable) · **One Time** setting with a start date/time · **Enabled** toggle.

## Content Page vs Content Container

| | Content Page | Content Container |
|---|---|---|
| Has URL | Yes | No |
| Personalization | Store + Profile | Store + Profile + Locale (variants) |
| Template | Required | Own rich-text content |
| Multi-locale | Per-locale content, same structure | Separate variant per locale |
| Reusability | Single page | Embeddable in many locations |

## Banner Sliders

A **Banner Slider** is the named group; a **Banner** is one slide. Per banner: image, alt text, URL, rich-text overlay, alignment, activation/expiration dates, locale. Can target All Users / Specific Accounts / Specific User Profiles. Must be associated with a Store Experience or CMS Page before publishing. Sliders can be shared across stores.

## Blog / News

Flat articles with Type = `Blog` or `News`. Per article: store, image, title, overview, tags, SEO, activation/expiration dates. Comments toggle per article. Storefront URLs `<domain>/blog` and `<domain>/news`. **No categories or author management** in V10.

## Forms

| Type | Built where | Submissions |
|---|---|---|
| Built-in (Contact Us, Feedback) | Pre-built in the starter theme | `OMS > Service Requests` |
| Custom | `CMS > Manage Forms` + Form Builder | `OMS > Form Submissions` |

Fields come from User-Defined Fields of entity type **Content Container**: Text · Multiline text · Dropdown · Checkbox · Radio · Date · File Upload · Email Address.

The **Form Widget** (v10.2.1.0+) embeds a custom form on any CMS page. Settings: Notification Email Address (comma-separated), Notification Email Template, Acknowledgement Email Template, Action On Form Submission (`Text Message` inline or `Redirect URL`), Submit Button Text.

> An `Email Address` field must be marked **required** for acknowledgement emails to send. Form changes require **publishing** to take effect.

Export: `OMS > Form Submission > Tools` → Excel/CSV (async; download from `System Settings > Export`).

## Localization

Localizable: Content Pages / Page Builder pages (all text, headings, buttons, images, video, rich text) · Content Containers (per-variant body) · Banner Sliders (image, alt text, text) · Categories, Products, Brands, Blog/News (name, description, SEO) · Form attribute labels and options.

**Prices are not locale-specific** — they are store-level currency. A store supports any number of locales (enable globally at `Dev Center > Global Settings > Locales`, associate at `Stores > Manage > Locales`, one default). Missing locale content falls back to the default locale. Currency is separate: one active currency per store, no conversion engine — multi-currency requires separate stores.

## KB source

- [Content Management (CMS)](https://support.znode.com/support/solutions/43000374861)
- [Managing Content Containers](https://support.znode.com/support/solutions/folders/43000598131)
- [Managing Content Pages](https://support.znode.com/support/solutions/folders/43000598132)
- [Creating and Managing Custom Forms](https://support.znode.com/support/solutions/folders/43000598127)

## Related
`webstore-customization` · `commerce-search-seo`
