# Effect on the Webstore, publishing and caches
What a storefront sees from a UDF, what needs publishing, and what to clear when a value looks stale.
Use it before promising that a new field "shows on the site".

## What the Webstore reads

| Entity | How the Webstore gets it | What it does with it |
|---|---|---|
| Store | The store portal call returns `GlobalAttributes` (values only for fields that have one). The Webstore keeps the portal data in a server cache | Reads fixed codes (login required, login to see pricing, maintenance, content security policy, reCAPTCHA keys, address suggestion, shipping constraints, promotion section, TradeCentric, username rules, stock display). A custom field arrives in the data and is ignored |
| User | The user's attribute groups are fetched at checkout | Reads one fixed field (the shipping address suggestion switch in the Address Setting group) |
| Account | Returned in account data | Nothing custom is shown |
| Form | The form widget loads the form's groups and renders each field by type (Simple and Multi Select become options) | Fully dynamic. This is the one place where a new UDF shows on the storefront without code (Text, selects and others per the widget) |
| Content Container | Variant data includes the attribute values | Shown only by the theme code that renders the container (KB: a developer updates the theme to show the container) |
| Promotion, Brand, Order and others | Not read for display | Brand fields are never shown (module guide, 85) |

Verified in the Webstore source and the product source (90). Conclusion: for every entity except Form, showing a custom field needs Webstore source work (a labelled source customization, skill `webstore-customization`).

## Publishing

| Question | Answer | Source |
|---|---|---|
| Does saving a UDF value need a publish to be live? | KB: "Additional Attributes" and "Global Settings" are live immediately. The portal call reads the values live from the API | KB "What Requires Publishing" (80), source (90) |
| Which things do need publishing? | Store settings and store experience, containers, pages, banner sliders, blogs. Forms are live without publishing | KB (80) |
| Does a store publish carry the store UDFs? | The store publish writes a snapshot of the store's UDF values into the published store data (source). Which Webstore calls read that snapshot is not verified | Source (90) for the write; GAPS for the read |
| Specific store flags | KB says `Login To See Pricing and Inventory` and `Login Required` "require publishing store settings", and the warehouse stock display change applies after the store is published | KB (80) |
| Brand fields | Never published, never on the storefront | Module guide (85) |

Rule of thumb for a customer: change a store field, publish the store, then clear the cache and test on the Webstore. For a field you read only through the API, no publish is needed.

## Caches

- Saving values through the Admin raises cache-stale events named by entity and record (`Store_Id_<id>`, `Store_Code_<code>` form). The B Store save and some Store flags (address validation) also raise the portal-update event. Other Store fields refresh when the portal cache expires or is cleared (source, 90, and inference on the rest).
- The Webstore keeps portal data in memory per store and has a revalidation tag path. Use the Global Settings cache clear or the Webstore revalidate path when a value looks old (skill `config-global-settings`).
- API responses for these routes are cached by the API. A fresh read can be forced with the cache bypass flag described in the API reference.

## Customization guidance

- Store flag or constant for your own Webstore code: add a UDF on the Store entity, read it from the portal data by `AttributeCode` in your Webstore change, and document the publish and cache steps in the handover.
- Per-user or per-account value shown in the account area or at checkout: write the field with `PUT /v2/global-entity-attributes`, read it through the user or account response, and render it in your Webstore component.
- Never render a UDF value as raw HTML. The Admin encodes values on display. The Webstore must encode too unless the field is a WYSIWYG Text Area you control (see known-behaviours.md).
