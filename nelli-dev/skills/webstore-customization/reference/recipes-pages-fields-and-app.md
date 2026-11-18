# Recipes: pages, fields, locales, reCAPTCHA, cart and checkout, environment variables

What this answers: how to add a page, show an extra field on a product card or the product page, add a locale, reuse reCAPTCHA, change cart or checkout UI, and add an environment variable, with the verdict for each.
Confidence: verified in the Webstore source (90) plus KB articles read in full (80). "Not run" marks steps traced in code only.

## Recipe 1: new page

Choose first:

| Need | Verdict | How |
|---|---|---|
| Marketing or content page an admin can edit | Supported | CMS > Pages > Add New (Store, Page Code, Page Name, Is Active, Locale, SEO fields, activation dates), then the Page Builder icon in the Actions column. Only published pages render. The catch-all route `[locale]/[...slug]/page.tsx` serves it by SEO URL |
| Page with its own code and logic (for example `/dealer-portal`) | Customizable (level 2) | new route folder |

Code-only page:
1. Create `apps/webstore/src/app/[locale]/<route>/page.tsx` (server component). Load text with `fetchMessages([...namespaces])` and wrap in `NextIntlClientProvider` as `cart/page.tsx` does. The root layout already supplies the header, footer, theme, session and styles.
2. Fetch data in the server component through an agent, or in a client component through a BFF route.
3. A page code that Page Builder manages (`PAGE_CODES` in `packages/page-builder/src/constants/constants.ts`) must exist as a Commerce Page in Admin; you cannot add new commerce page codes. A code-only page is not editable in Page Builder.
4. If the page is personal (account-like), require a session in the page and in its API routes. In `apps/webstore/src/middleware.ts` the `AUTH_ROUTES`/`EXCLUDED_PATHS` lists in `packages/constants/src/app.ts` control the login pages; store-level "Login Required" redirects to `/login` automatically.
5. Anonymous page cache: `apps/webstore/server.js` never caches `/api`, `/_next`, cart, checkout, account, login, logout, register, welcome, impersonation, punchout, quick-order, saved-cart, order, quote, error, maintenance or revalidate paths, nor any request with a session or cart cookie. A new personal page outside those prefixes would be cached for anonymous visitors when `ENABLE_ANON_PAGE_CACHE=true`: add its prefix to `EXCLUDED_PATHS` in `server.js` (level 3 edit) or name the route under an excluded prefix.
6. Add the route to Cloudflare bypass rules if it is personal (see `caching-and-visibility.md`).

## Recipe 2: add a field to the product page

| Need | Verdict | How |
|---|---|---|
| Name and value pairs for a product, shown as text | Supported | PIM > Products > Product Detail > Custom Fields tab > Add Custom Fields > Save, then publish. They show on the base B2B product page in a tab called Additional Information. Use a custom code that is not an existing attribute code (KB). Source: attributes with the custom-field flag are collected in `getAttributesAsTabs` (`packages/agents/src/product/product.ts`) |
| Long description, specification, shipping information | Supported | product attributes (these three feed the tabs) |
| Value from a custom table or another system | Customizable | recipe 4 below |
| New layout for existing data | Customizable | theme override of the product details page widget (see `recipes-widgets-and-themes.md` 3b) or edit `ProductBasicInfo` (level 3) |

Data on the page: `getProductInformation` (`packages/agents/src/product/product.ts`) returns `productBasicDetails` (with `attributes` and `dynamicAttribute`), `configurableProducts` and `tabList`; `ProductDetailsPage` in `packages/base-components/src/components/page-widget/product-details-page` composes breadcrumbs, basic info, tabs, link products and recently viewed. The product page is rendered per variant through URL parameters (see `repo-layout-and-data-flow.md`).

## Recipe 3: add a field to the product card (list)

1. First check whether the shipped card already shows it: price, image, name, SKU and reviews (switches on the Product List Page widget), and product highlights (`highlightList`), which admins configure.
2. List items carry an `attributes` array (`IProduct`), but which attributes are present depends on what is published and indexed for listing. Verify the attribute arrives in the list response on a store before designing the card (see `commerce-product-attributes`, `commerce-search-seo`).
3. If the value is present: copy the card into a theme (the bundled theme has `packages/bstore/src/components/product/product-card/ProductCard.tsx`), add the field, and use the theme's product list page widget (the page-widget override is recipe 3b in `recipes-widgets-and-themes.md`, not run). Editing `packages/base-components/src/components/common/product-card/ProductCard.tsx` instead is level 3.
4. If the value is not present or comes from elsewhere: fetch it for the visible SKUs through one batched BFF route (not one call per card) and merge client-side.

## Recipe 4: show a custom table or Custom API value on the product page

1. Create or confirm the Custom API endpoint or Custom Table API operation (`sdk-custom-tables`, `sdk-custom-api`).
2. Client, agent, BFF route, browser wrapper as in `bff-routes-and-clients.md`.
3. Add a small client component (for example `ProductExtraInfo`) that takes the SKU and calls the wrapper. Place it either as a widget in a theme or in a copied product details page. Pass the SKU from `productBasicDetails.sku`; for a configurable product the SKU changes with the selected variant because the page re-renders with a new URL.
4. Handle loading, empty and error states. Cache on the Custom API side or with a short tagged cache; anonymous HTML can be cached by the page cache, so keep personal values out of server-rendered HTML.

## Recipe 5: change the cart or checkout UI

| Change | Verdict | How |
|---|---|---|
| Text, headings, banners around cart or checkout | Supported | Cart and Check-Out commerce pages in Page Builder (since 10.4.1.0): add widgets above or below the fixed page |
| Hide or show built-in sections (promotions, estimated shipping, vouchers) for a B Store | Supported | B Store starter theme behaviour (KB "B Store Starter Theme") |
| New layout of the cart page | Customizable | theme override of the Cart Page widget; the render file shows the shape: `CartPageRender` passes `cartPagePortalDetails` and `user` to `CartPage` in `packages/base-components/src/components/page-widget/cart-page` (the theme copies `CartPage` and the cart components it needs) |
| Extra checkout field or step | Customizable, level 3 | `packages/base-components/src/components/checkout/Checkout.tsx` and its submodules (shipping, payment, additional information, submit actions, cart review); send the extra data to a Custom API through a new BFF route and keep validation in the API |
| Change payment, tax, shipping calculation | not a UI change | `commerce-checkout-payments`, `sdk-provider-plugins`, `sdk-method-overrides` |

Warnings: checkout uses a per-tab checkout reference stored in session storage and sent as an encrypted header on every `httpRequest` call (`packages/constants/src/checkout.ts` constants); keep calls on `httpRequest` so the header is added. Place order validates the order total server-side (`placeOrder` in `packages/agents/src/checkout/checkout.ts`) and voids the online payment when order creation fails; do not bypass it.

## Recipe 6: new locale

KB "Configuration of New Locale in webstore" (written for the Page Builder app, example `de-DE`) read in full, extended with the storefront steps found in the source.

| Step | Where |
|---|---|
| Enable the locale for the store | Admin (store locale settings; see `config-store`). Not verified here |
| Add the code to the list | `packages/constants/src/i18n.ts`, array `LOCALES` (the source has `["en-US", "fr-FR"]`). Keep `FALLBACK` as `en-US` unless the new locale must become the app default (`FALLBACK` plus `DEFAULT_LOCALE` in `packages/constants/src/settings.ts` and `app.ts`) |
| Messages | create `apps/webstore/messages/<locale>.json` and `apps/page-builder/messages/<locale>.json` from `en-US.json` with the same namespaces and keys; the file name must equal the locale code exactly; missing keys fall back to the default locale messages |
| Locale id mapping | `getLocaleID` in `packages/utils/src/server/portal/portal-headers.ts` holds a fixed map (en-US 1, fr-FR 2, de-DE 3, es-ES 4, be-BE 5); a locale not in the map falls back to the store's cached locale id. Check the id matches the Admin locale |
| Routing and middleware | no change: routing reads `LOCALES`; an unsupported locale prefix such as `/es-ES` redirects to the fallback locale |
| HTML language attribute | the webstore root layout writes `<html lang="en" ...>` and the Page Builder layout `lang="en-US"`; derive it from the route locale for accessibility and SEO (level 3 edit, KB recommends it) |
| Test URLs | `/<locale>?storeCode=<code>`, `/<locale>/page-builder?storeCode=<code>`, `/<locale>/<slug>?storeCode=<code>`; keep `storeCode` while navigating |

Content in the new locale (widget text, banners, categories, products) is entered in Admin per locale (skill `webstore-page-builder-and-themes`, multi-locale).

## Recipe 7: add reCAPTCHA to another form

The KB article "Implementing the Znode ReCaptcha feature on any additional pages" differs from the source; the source wins (see `kb-vs-product.md`).

1. Use the shared component `packages/base-components/src/components/common/recaptcha/Recaptcha.tsx`. Props: `onVerify(verified, token?)`, `recaptchaRef` (a `react-google-recaptcha` ref), `siteKey`, `saveToken` (when true, pass the token to your endpoint instead of verifying in the browser), `dataTestSelector`. It is invisible: it executes on mount and calls `onVerify`.
2. The site key comes from the store's ReCaptcha settings (Store > Additional Attributes). Pages obtain it from `getLoginSettings()` (`recaptchaDetails`) or the equivalent settings call. It is not read from an environment variable in the source.
3. In your BFF route call `validateRecaptchaForProtectedEndpoint(token, options)` from `@znode/agents/recaptcha` inside the protected endpoint (not in the browser). Options: `isFormCaptcha: true` uses the store flag for contact and feedback style forms; `isCheckout: true` uses the checkout flags (logged-in user or guest); default uses the login flag and skips the check for a trusted device cookie. If the relevant store flag is off the call returns valid.
4. Return the shared error code `ERROR_CODE.RECAPTCHA_VERIFICATION_FAILED` (see `contact-us/route.ts`) and show it as the existing forms do.
5. Never trust a token verified only in the browser. The browser path `verifyRecaptcha` posts to `/api/recaptcha-verify`.
6. A new flag for your form means a new store attribute, which needs the Admin attribute framework; reuse `IsCaptchaRequired` (contact and feedback) when possible.

## Recipe 8: add an environment variable

1. Read it on the server with `process.env.NAME` in an agent, route or server component. Names starting with `NEXT_PUBLIC_` are inlined into the browser bundle at build time; never put secrets there.
2. Add the name (no value) to your `.env` template and documentation, and set it in the deployment for the `webstore` app, and for `page-builder` if code that both apps share reads it.
3. Restart the process: values are read when the Node process starts (`server.js` reads cache variables once at boot).
4. Do not read variables at module load in code shared with the browser.
