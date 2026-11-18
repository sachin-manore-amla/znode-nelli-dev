# Webstore repo layout and data flow

What this answers: what each folder and package in the Webstore source is for, and how a storefront page gets from the browser to Znode and back.
Confidence: verified in the Webstore source (stamp 10.14.0.0, read 2026-10-15); package purposes are from reading the code, the KB gives only short descriptions.

## Stack

| Item | Version in the source | Note |
|---|---|---|
| Next.js | 15.5.9 (App Router) | the KB article for the 10.7.0.0 release says Next 14 to 15, Nx 19 to 22, React 19 |
| React | 19.2.3 | |
| Nx | 22.3.3 | project targets are inferred by the Nx plugins (`dev`, `build`, `start`, `lint`, `test`) |
| Tailwind CSS | 3.4.3 with `tailwindcss-themer` | the KB article names `tailwindcss-themes`; the source uses `tailwindcss-themer` |
| Page Builder editor | `@puckeditor/core` 0.21.1 | see skill `webstore-page-builder-and-themes` |
| Auth | `next-auth` 4 | session cookie names appear in the Cloudflare rules |
| i18n | `next-intl` 3 | locale prefix mode "as needed" |
| Cache | Next data cache, Redis (optional), in-memory page cache | see `caching-and-visibility.md` |

## Top level

| Path | Purpose |
|---|---|
| `apps/webstore` | the storefront: `src/app/[locale]/...` pages, `src/app/api/...` BFF routes, `middleware.ts`, a custom `server.js` (Node server with cluster mode and an anonymous page cache), `messages/<locale>.json` |
| `apps/page-builder` | the editor and preview app opened inside Admin: `src/app/[locale]/page-builder/page.tsx` (query parameters `url`, `storeCode`, `pageCode`, `publishState`, `contentPageCode`, `versionNumber`), its own `src/app/api/...` routes for widget data and publishing, `messages/<locale>.json` |
| `packages/` | shared libraries (below) |
| `patches/` | `patch-package` patches applied after `npm install` (one patch for `react-quill`) |
| `.husky/commit-msg` | hook that runs spell check, lint, build and commit message validation |
| `tsconfig.base.json` | the `@znode/...` path aliases |
| `.env.webstore`, `.env.page.builder` (root) | environment files for the Docker build; the Dockerfile copies the app's own `.env` into the image, so local runs read `apps/webstore/.env` and `apps/page-builder/.env` |
| `.github/workflows` | CI workflows (dev and release tag); replace with your own pipeline |

## Packages

| Package | Alias | What is in it |
|---|---|---|
| `base-components` | `@znode/base-components/...` | all React UI: `components/account`, `cart`, `checkout`, `product`, `page-widget/*` (the page widgets), `znode-widget/*` (data widgets), `layout-components` (header, footer), `common/*` (button, modal, input, image, recaptcha), `http-request/*` (browser fetch wrappers for `/api/...`), `stores` (Zustand), `tailwind-config` (base Tailwind preset and `global.css` with the CSS variables) |
| `agents` | `@znode/agents/*` | server-side functions, one folder per domain (`product`, `cart`, `checkout`, `portal`, `widget`, `login`, `recaptcha`, `revalidate`, `visual-editor` and more). They call the clients, convert case, shape data and log |
| `clients` | `@znode/clients/v1`, `v2`, `cp`, `payment`, `shipping-manager`, `custom` | typed HTTP clients. `V1` and `V2` for the Core APIs, `commerce` (alias `cp`) for the Commerce API, `payment-manager`, `shipping-manager`, and `custom` (the place for your own Custom API clients; it ships with one example, user activity) |
| `page-builder` | `@znode/page-builder/...` | the editor engine: `configs/` (widget configs, theme configs, loaders), `page-editor`, `page-render`, `page-layout`, `utils/get-page*.ts`, `lib/migrations`, `constants` |
| `bstore` | `@znode/bstore/...` | the bundled B Store theme: its own product list and product details page widgets, product card, a Button and a Card widget, and a Tailwind theme file |
| `cache` | `@znode/cache` | file or Redis cache abstraction and the eviction pub/sub |
| `utils` | `@znode/utils/...` | server helpers (`getPortalHeader`, headers, auth, `sendSuccess`/`sendError`, case converters) and client helpers (translation hook, encryption) |
| `types` | `@znode/types/*` | shared TypeScript types |
| `constants` | `@znode/constants/*` | constants: header names, locale list, error codes, cache keys and event names, settings |
| `logger` | `@znode/logger` | client and server logging (file or console) |

Not present although the KB mentions them: `theme1-components`, `custom-theme1-components`, `custom-theme2-components`. The only theme package in the clone is `bstore`. The alias `@znode/data-providers` in `tsconfig.base.json` has no package behind it.

## Page flow (storefront)

```
Browser GET /en-US/<slug>
  middleware.ts: finds the store from the host name, sets locale and security headers,
                 redirects for maintenance, login required, unpublished store
  app/[locale]/layout.tsx: reads theme name, injects the store's Dynamic Styles CSS,
                 sets <html data-theme="<theme>">, renders header/footer from the "layout" page JSON
  app/[locale]/[...slug]/page.tsx (or cart/, checkout/, login/ ... folders):
        resolves the SEO URL to a page type, calls getPage(...) for the page JSON of the store
        -> hydrates each widget's data on the server (agents) -> <PageRender> with getConfig(theme, pageType)
```

- Page JSON comes from the Znode API (production or preview published copy). With `IS_DEBUGGING=true` the Webstore reads page JSON from local files in the cache folder instead (development only).
- `getPage` first checks a page-structure cache (key includes page code, account, publish state, locale and profile) and migrates old JSON forward (`CURRENT_JSON_VERSION`, 2 in this source).
- Widget data comes from handler maps in `packages/page-builder/src/utils/prepared-content-item.ts`: page handlers (product details, product list, brand, blog, store locator), widget handlers (banner slider, offer banner, categories, products carousel, brands carousel, ad space, home page promo, link panel, ticker, form, content block), and the header layout handler.
- Several routes are their own folders (`cart`, `checkout`, `login`, `signup`, `forgot-password`, `quick-order`, `order-status`...). They also render through Page Builder page widgets, except login, signup, forgot password, track order and quick order: those render through Page Builder only when `ENABLE_PAGE_BUILDER_SIGNUP_LOGIN` or `ENABLE_PAGE_BUILDER_TRACK_QUICK_ORDER_FORGOT_PASSWORD` is `true`, otherwise the built-in page renders.

## Data flow for an interaction

```
React component (client)        packages/base-components/src/components/...
  -> http-request wrapper        packages/base-components/src/http-request/<domain>/...   fetch("/api/...")
  -> BFF route handler           apps/webstore/src/app/api/<route>/route.ts
  -> agent                       packages/agents/src/<domain>/...
  -> typed client                packages/clients/src/znode-client/{V2,V1,commerce,custom,...}
  -> Znode gateway (API_URL)     headers added in clients/.../V2/base.ts (see bff-routes-and-clients.md)
```

Worked example (store locator): `getStoreLocator()` in `http-request/store-locator` fetches `/api/store-locator`; `api/store-locator/route.ts` calls `getStores(portalId)` in `agents/src/store-locator`; the agent calls a V2 client function and converts the PascalCase response to camelCase.

Server components (pages) skip the browser hop: they call agents directly.

## Variant selection on the product page (verified)

The configurable product picker is `packages/base-components/src/components/product/product-details/product-types/configurable-product-attribute/ConfigurableProductAttribute.tsx`. A swatch click does not call an API from the browser. It builds a URL with `parentProductId`, `codes`, `values`, `parentProductSKU`, `sku`, `selectedCodes`, `selectedValues` (plus the list facet parameters), calls `router.push`, and the server re-renders the page: `getProductInformation` sees `parentProductId` and loads the selected variant. Quick view uses `POST /api/configurable-product-quick-view` instead. The product attribute Display Variants on Grid switches between this swatch layout and a variant grid. Any custom picker must keep that URL contract or replace the server step too.
