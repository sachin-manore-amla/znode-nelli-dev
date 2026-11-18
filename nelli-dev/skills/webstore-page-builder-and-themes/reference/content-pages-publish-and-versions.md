# Content pages, publish, versions and visibility

What this answers: how a content page is created and edited, what makes a page visible, how Save for Preview and Publish differ, how version history behaves, and where KB articles disagree.
Confidence: KB "Webstore Customization Guide" use cases 5 to 7 and "Page Builder - Multi-locale" (80); "Configuring a Content Page" is an older article (70, partly stale); Webstore source (90).

## Create a content page

CMS > Pages > Add New. Fields (Customization Guide): Store, Page Code, Profile (if applicable), Page Name, Is Active, Locale(s). SEO: Page Title, SEO Title, SEO Keywords, SEO Description, Additional Meta Information, SEO-Friendly URL, Redirect setting, Canonical URL, Robot Tag. Activation Date and optional Expiration Date. Save, then use the Page Builder icon in the Actions column (after the first save a Page Builder tab also appears). When creating a page the default global locale is preselected and not editable; change the locale on the edit screen.

The older article "Configuring a Content Page" lists a Template field, preview flags in a configuration file and a Content tab with containers. The Customization Guide and Page Builder articles describe the current flow without templates; treat the old article as legacy text.

## Visibility rules

| Rule | Detail |
|---|---|
| Only published pages render on the storefront | KB |
| Store and Profile | a page shows only for its store and, when set, its profile |
| Is Active | must be on |
| Activation and Expiration dates | the page is visible between them |
| Locale | content per locale; default locale is the fallback |
| SEO URL | the storefront resolves the page through its SEO URL; an unknown URL or an expired or unavailable content page gives the not-found page (source) |
| Versions | each save creates version history; every widget used on a page must be registered (KB) |

## Save and publish

| Action | Result |
|---|---|
| Save for Preview | preview environment updated; version record status Draft |
| Publish (after preview) | Draft becomes Published (Live) |
| Publish directly | one Published (Live) version |
| Restore a version | loads it on the canvas; you still publish |
| Multi-locale edits | one version record covers all locales edited before saving |

After publishing, the Webstore is told to refresh caches (the Page Builder publish event and related ones). Shoppers on production see the change after revalidation and any CDN or anonymous-cache lifetime (skill `webstore-customization`, caching file). "Changes will appear immediately on the Webstore" in the KB holds only when caching is off or purged.

## Containers, banners and blogs next to Page Builder

Content Containers have their own editor and variants (Ad Space, Homepage Promo); Banner Sliders and Blog/News use their own Admin screens. Page Builder places them through widgets. See `webstore-cms`.
