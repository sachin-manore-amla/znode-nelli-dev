# Multi-locale in Page Builder

What this answers: how content varies by locale in Page Builder, which widgets are locale-aware and where each locale's data is entered, the fallback rules and the limits.
Confidence: KB "Page Builder - Multi-locale" read in full (80); release note 10.6.0.0 (December 28, 2025); the source stores per-locale text for text-like widgets (90).

Navigation: CMS > Store Experience > Manage Experience (commerce pages) and CMS > Pages (content pages). A locale selector in the Page Builder header lists the locales; the default is the store's default locale. On CMS > Pages a locale dropdown lists active locales of all stores.

## Rules

- Page structure is identical in every locale. Only content (text, images, videos, bound records) differs. Deleting a widget in one locale deletes it in all.
- Attribute settings (sizes, alignment, flags) are shared across locales.
- Missing content in the active locale falls back to the default locale. If the default locale has no content but another locale does, the widget is hidden in the default locale (only Button Group and Newsletter still show; the editor canvas shows a no-content message).
- Widget labels and attribute names in the editor stay in English.
- A page must be published for locale content to show.

## Where each widget's locale content comes from

| Widget | Locale content entered |
|---|---|
| Text, Heading, Button Group, Text Image, Dynamic Widget, Rich Text | in Page Builder, with the locale selected (stored per locale in the widget) |
| Image, Video | different file and alt text per locale in Page Builder |
| Newsletter | label, placeholder, button text per locale; defaults translate on drop |
| Banner Slider, Offer Banner | CMS > Banner Sliders > gear action > locale dropdown on Manage Banner |
| Categories Carousel | PIM > Categories, locale dropdown |
| Products Carousel | PIM > Products, locale dropdown |
| Brands Carousel | PIM > Brands, locale dropdown |
| Ad Space, Homepage Promo | CMS > Containers: create a variant, edit it, change locale, add content |
| Link Panel | locale dropdown inside the link pop-up; menu items per locale |
| Form Widget | form attributes with Locales/Values (Dev Center > User-defined Fields, entity Form Builder), then CMS > Manage Forms |
| Fixed commerce pages | product, category, brand and blog data per locale in their modules; store locator, contact us and feedback text is handled in code (message files) |

## Developer notes

New widgets with editable text need their own per-locale handling (see `getUpdatedProps` in the configs `utils.ts`; recipe 1 in `webstore-customization`). New locales need message files and code lists (recipe 6 there).
