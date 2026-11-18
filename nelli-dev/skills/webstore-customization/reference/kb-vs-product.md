# Where the KB Webstore Customization Guide differs from the Webstore source

What this answers: the exact differences between the KB articles (Webstore Customization Guide, Development and Setup Guide, Configuring a Site Theme, reCAPTCHA, New Locale, Troubleshooting, Cloudflare, Revalidation) and the Webstore source (stamp 10.14.0.0, read 2026-10-15). The product wins.
Correction to earlier Nelli-Dev guidance: the KB does document supported mechanisms (custom widgets, theme packages, Page Builder editing, Tailwind themes). They are valid; the gaps below are about missing steps and stale names.

## Confirmed as documented

| KB statement | Source check |
|---|---|
| Widget = config file plus render file under `packages/page-builder/src/configs/base-config/widgets/{type}/` | true; types are `ui-widgets`, `znode-widgets`, `page-widgets`, each widget in its own kebab-case folder |
| Register in `.../base-config/config/base-components-config.ts` | true (file is `.ts`, the KB prose says `.tsx` once) |
| Theme config folder with `config/root-config.ts`, `override-component-list.ts`, page config map and `widgets/` | true (`bstore-config`) |
| `extendConfig` with `addOrOverrideComponents`, `removeComponentKeys`, `addComponentToCategories`, `disabled` | true (`extend-config.tsx`) |
| `addComponentToCategories` is needed or a new widget is not visible | true |
| Category keys `uiWidgets`, `layoutWidgets`, `znodeWidgets` | true |
| `get-config.ts` maps theme name to root config, falls back to base | true, theme name lower-cased |
| Fixed commerce pages edited in Admin: CMS > Store Experience > Page Builder icon; content pages CMS > Pages | true (KB "Commerce Pages configuration" lists 17 predefined pages) |
| Puck 0.17.4 to 0.21.1, `migrateLegacyPageStructure` in `packages/page-builder/src/utils/common.ts`, called by the editor and the page renderer | package version 0.21.1 confirmed; migration code is in `utils/common.ts` and used by `PageEditor` and `PageRender` (both `migrateLegacyPageStructure` and `migrateLegacyData` exist there; the page renderer calls `migrateLegacyData`) |
| Locale files, `LOCALES`, routing, middleware, `de-DE` example | true for the Page Builder app; `LOCALES` is `["en-US", "fr-FR"]` |
| Revalidation routes `/api/revalidate-with-token`, `/api/revalidate-all-with-token`, secret `ZNODE_REVALIDATE_TOKEN` | true; header name is `x-secret` (the KB does not name it) |

## Differences and omissions

| # | KB says | Source shows | Effect |
|---|---|---|---|
| 1 | Register a theme in `get-config.ts` only ("Key Rule") | a second loader, `get-layout-config.ts`, picks the header and footer config per theme, and each theme has `root-config-layout.ts` and `page-config-layout-map.ts` | skipping it leaves header and footer on the base config |
| 2 | Theme folder `maxwell-config` has `config/page-config-map.tsx` "optional page-level overrides" | the bundled theme's `page-config-map.tsx` is imported by nothing; the theme `root-config.ts` imports the **base** `retrieveData`, and base page entries are spread after theme entries | a theme's page-widget override (product details, list...) does not apply unless you rewire `root-config.ts`. KB's own template has the same import |
| 3 | `Grid: GridConfig` is "just the Config" | the base config is typed by `IComponentProps` in `types/page-builder.ts`; a new key must be added there | type check fails otherwise (webstore build ignores type errors; page-builder build does not) |
| 4 | Theme Tailwind plugin `tailwindcss-themes`, file `tailwind.config.ts`, config in "Webstore or Page Builder" | package is `tailwindcss-themer`; both apps' `tailwind.config.js` contain `themes: []`; theme file is `tailwind.config.js`; the bundled theme's Tailwind file and `global.css` are not wired | styling does nothing until both apps list the theme |
| 5 | Theme picked by `DEFAULT_THEME=maxwell` | the theme comes from the store (Admin Theme setting); `DEFAULT_THEME` is only the fallback | set the store's theme in Admin |
| 6 | Packages `theme1-components`, `custom-theme1-components`, `custom-theme2-components`; aliases `@znode/<theme>` and `@znode/<theme>/server` | only `packages/bstore`; aliases `@znode/bstore/ui-widgets/*`, `page-widgets/*`, `components/*`, `tailwind-config/*` | follow the bundled theme |
| 7 | Scaffold with `npx nx g @nx/next:lib packages/<theme>` | not run; the existing theme has no `project.json` targets and no `index.ts` entry | likely fine; verify aliases after scaffolding |
| 8 | Husky `pre-commit` and `pre-push` hooks | only `.husky/commit-msg`, which runs spell check, lint, build and commitlint | commits are slow; CI workflows exist for dev and release |
| 9 | Enabling Publish button: set `ENABLE_EDIT_WIDGET: true` in `visual-editor.ts` | flag only affects default page widget permissions and the editor header slot; no Publish gating found | do not rely on it; verify on a store |
| 10 | Real-time preview: `ENABLE_CACHE=false`; troubleshooting article: `ENABLE_CACHE=true` | any value other than `true` disables the data cache; `IS_DEBUGGING=true` switches page JSON to local files | KB articles contradict each other |
| 11 | reCAPTCHA: `Recaptcha.tsx` at `packages/base-components/src/Recaptcha/`, util at `packages/utils/src/recaptcha.ts`, import `@our-org/...`, v3 invisible, keys in `NEXT_PUBLIC_RECAPTCHA_SITE_KEY` and `RECAPTCHA_SECRET_KEY` | component at `packages/base-components/src/components/common/recaptcha/Recaptcha.tsx`, `react-google-recaptcha` invisible widget, no `utils/recaptcha.ts`, keys are store settings, server check `validateRecaptchaForProtectedEndpoint` | follow the source (recipe 7) |
| 12 | Cloudflare rule 4 cookie `_Secure-next-auth.session-token`, four cookies | cookie is `__Secure-next-auth.session-token`; `CopiedCartNumber` is also personal; excluded paths are broader | adjust rules |
| 13 | Cloudflare rule 3 path `/my-account` | no such route; account pages are under `/account` | harmless |
| 14 | Webstore Customization Guide env table: `NEXTAUTH_SECRET` | source middleware reads `SECRET` for the token; `NEXTAUTH_SECRET` is also read | confirm from the `.env` template |
| 15 | Guide says Widget catalog includes `Card`, `Hero`, `Logo`, `Flex`; Znode widgets list lacks Brands Carousel, Link Panel, Form Widget, Content Block | `Card`, `Hero`, `Logo` exist as folders but are commented out of the base config; `Flex` is registered as `Container`; Brands Carousel, Link Panel, Form Widget, Content Block are registered | use the catalogue in `webstore-page-builder-and-themes` |
| 16 | Guide: pre-defined themes `base`, "dark-mode" | the only theme code in the source is `bstore` plus the base fallback | n/a |
| 17 | Setup guide: "Access Page Builder at http://localhost:3000" and Webstore on 3000 | both default to 3000 | set `PORT` |
| 18 | Setup guide: Webstore tech "Redis ... caching" and `STORAGE` values `file`, `redis`, `cdn` | cache package has file and Redis integrators | `cdn` value not seen |
| 19 | Locale article: add locale in `LOCALES` and message file | the Webstore also has `getLocaleID` with a fixed id map and a hard-coded `<html lang="en">` | see locale recipe |
| 20 | Puck article: `PageEditor.tsx` and `PageRender.tsx` invoke the migration | confirmed for both | none |

The older `webstore-customization` skill is stale: it says Next.js 14, Page Builder on :3001, layout JSON stored in a database, and lists Card, Hero and Logo as available; it omits Content Block, the Container rename and the second theme loader. Use this skill instead.
