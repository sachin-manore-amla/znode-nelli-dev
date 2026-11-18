# Recipes: widgets, themes and component overrides

What this answers: step-by-step procedures for a new widget, a new theme, overriding a widget or a page widget, and a widget that shows custom data, with the exact files and the checks that the KB leaves out.
Confidence: KB "Webstore Customization Guide" read in full (80) checked against the Webstore source (90). Steps marked "not run" were traced in code but not executed on a running store.

Paths are relative to the Webstore repository root. `<configs>` means `packages/page-builder/src/configs`.

## Recipe 1: new widget in the base config

KB Use Case 1. Result: the widget appears in the Page Builder panel for every theme that has no override.

1. Pick the category: `ui-widgets` (presentation), `znode-widgets` (data widgets bound to Admin data; a custom widget is better placed in `ui-widgets`), or layout. The panel groups are `layoutWidgets`, `uiWidgets`, `znodeWidgets`.
2. Create `<configs>/base-config/widgets/ui-widgets/<kebab-name>/` with `<Name>Config.tsx` and `<Name>Render.tsx`. Existing widgets (for example `text/TextConfig.tsx`) are the pattern:
   ```tsx
   export type IGridConfig = { columns?: number };
   export type IGridRenderProps = IGridConfig & IRenderProps;
   export const GridConfig: ComponentConfig<{ props: IGridConfig }> = {
     fields: { columns: { label: "Number of Columns", type: "number", min: 1 } },
     defaultProps: { columns: 3 },
     label: "Grid",
     render: (props: IGridRenderProps) => <GridRender {...props} />,
   };
   ```
   `IRenderProps` comes from `types/page-builder`. Field types used in the source: `text`, `textarea`, `number`, `select`, `radio`, `object` (with `objectFields`), `custom`, `slot`.
3. Register it in `<configs>/base-config/config/base-components-config.ts`: import the config, add `Grid: GridConfig` under `components`, **and** add `"Grid"` to the right array under `categories` (`layoutWidgets`, `uiWidgets` or `znodeWidgets`). A widget that is in `components` but in no category does not show in the editor.
4. Add the key to the `IComponentProps` interface in `packages/page-builder/src/types/page-builder.ts` (`Grid: IGridConfig;`). The base config is typed by `IComponentPropsWithoutPages`, so an unknown key fails the type check (not run).
5. Optionally export it from `widgets/ui-widgets/index.ts` like the others.
6. If the widget has editable text that should vary by locale, follow `getUpdatedProps` in `<configs>/utils.ts`: the built-in text widgets keep a `locale` map per locale code and add a handler in `widgetHandlers`. Without it the text is the same in every locale.
7. Run `npx nx dev page-builder`, open a page in the editor (see `build-test-and-known-behaviours.md` for the preview URL), drag the widget, save, then view the page in the Webstore.
8. Build both apps (`npx nx build page-builder`, `npx nx build webstore`) and lint.

Notes:

- A custom widget's fields are edited in the editor's right panel. The gear icon with an Admin pop-up (select banner, associate products) exists only for the built-in Znode widgets that are bound to Admin widget records.
- Do not set `hasConfigurable: true` or a `widgetKey` on a custom widget: those fields tie a widget to Znode CMS widget records, which you cannot create.
- Existing pages that already contain the widget keep their saved props. If you later rename or remove a prop, add a JSON migration (below) or keep the old prop.
- Data in the widget: if the widget needs data, the safest pattern is to fetch it from the component through a BFF route (recipe 4). Server-side hydration exists for built-in widgets through `widgetHandlers` in `packages/page-builder/src/utils/prepared-content-item.ts` (a map from `config.id` to an agent call). A custom entry in that map plus a `config` prop with `type: "Widget"` should work (not run); it is a shared-file edit and needs a non-empty `widgetKey` or the hydration step skips the widget.

## Recipe 2: new theme (documented as "Use Case 2")

Result: a store assigned this theme loads its own widget set and styling.

Admin part (KB "Configuring a Site Theme"):
1. CMS > Site Themes > Add New. Enter Theme Name and Theme Code (both mandatory); the parent theme is selected automatically (the B2B theme is the base parent). Save & Close.
2. CMS > Store Experience > choose the store > General Settings: choose the Theme. Publish the store.

Code part:
3. Scaffold the package: `npx nx g @nx/next:lib packages/<theme>`. KB answers: stylesheet `scss`, bundler `none`, linter `eslint`, unit test runner `none`. Compare with `packages/bstore`, the bundled theme: `src/components/widgets/ui-widgets`, `src/components/widgets/page-widgets`, `src/components/<domain>`, `tailwind-config/tailwind.config.js`, `tsconfig.json`, `tsconfig.lib.json`, `.eslintrc.json`, `project.json`.
4. Add aliases to `tsconfig.base.json` (copy the four `@znode/bstore/...` lines):
   `@znode/<theme>/ui-widgets/*`, `@znode/<theme>/page-widgets/*`, `@znode/<theme>/components/*`, `@znode/<theme>/tailwind-config/*`. The KB also lists `@znode/<theme>` and `@znode/<theme>/server`; the bundled theme has neither.
5. Create `<configs>/<theme>-config/` with the same files as `bstore-config`:
   - `config/override-component-list.ts`: `export const addOrOverrideComponents: IComponents = { MyWidget: MyWidgetConfig }`
   - `config/root-config.ts`: copy `bstore-config/config/root-config.ts` and add `addComponentToCategories: [{ categoryKey: "uiWidgets", componentKeys: ["MyWidget"] }, ...(selectedConfig.addComponentToCategories ?? [])]` (mandatory: without it the widget is not visible in the editor; the bundled theme omits it).
   - `config/page-config-map.ts(x)`: page-level overrides (recipe 3b).
   - `config/root-config-layout.ts` and `config/page-config-layout-map.ts`: the header and footer editor configs (copy from `bstore-config`).
   - `widgets/...`: your widget config and render files.
6. Register the theme in **both** loaders (the KB lists only the first):
   - `<configs>/get-config.ts`: `["<theme>", getMyThemeRootConfig]` in `themeConfigMap`.
   - `<configs>/get-layout-config.ts`: `["<theme>", getMyThemeLayoutRootConfig]` in its `themeConfigMap`. Without it the header and footer use the base layout config.
   The key must be the lower-case theme name that the store returns (the loaders call `toLowerCase()` on `params.theme`). Use the same string as the Theme Code or Name you created in Admin; confirm which one the store header returns on a development store (not run).
7. Wire Tailwind in **both** `apps/webstore/tailwind.config.js` and `apps/page-builder/tailwind.config.js`. They use `tailwindcss-themer` and ship with `themes: []`. Put your theme object there:
   ```js
   const myTheme = require("../../packages/<theme>/tailwind-config/tailwind.config");
   plugins: [themes({ themes: [myTheme] })]
   ```
   The theme file exports `{ name, selectors: ["[data-theme='<theme>']"], extend: { colors: {...} } }`. The root layout sets `<html data-theme="<lower-case theme>">`, which is what the selector matches. The bundled `bstore` theme's Tailwind file and `global.css` are not imported anywhere in the source, so they have no effect until you wire them.
8. Build and run both apps; assign the theme to a test store; publish the store; open a page.

## Recipe 3: override something

| Goal | How | Status |
|---|---|---|
| Replace a base widget (for example `Text`) for one theme | register the same key in the theme's `override-component-list.ts`; the theme's list is merged over the base | traced in `extend-config.tsx` and `root-config.ts` (the theme's list wins for non-page widgets) |
| (3a) Update an existing base widget for everyone | edit its `*Config.tsx` / `*Render.tsx`; no registration needed (KB Use Cases 3 and 4) | level 3 for base files |
| (3b) Replace a page widget (product details, list, cart, checkout...) for one theme | write the theme's page widget config and render files (the bundled theme does this for product details and product list), list them in the theme's `page-config-map`, and make the theme's `root-config.ts` read **its own** `retrieveData`-style lookup instead of the base one | not run. In the source the bundled theme's `page-config-map.tsx` is imported by nothing; its `root-config.ts` imports `retrieveData` from the base map, and the base map's entries are spread after the theme list, so a theme page override registered only in `override-component-list.ts` is replaced by the base page widget. Treat page-widget overrides as needing a test on a running store |
| Replace a component deep inside a page (product card, price block) | the theme must provide the whole chain between the page widget and that component (the bundled theme copies `ProductBasicInfo`, `ProductCard`, `ProductList`, `ProductView`), or edit the base component | copy cost is yours at every upgrade |
| Replace the login or signup form | pass `customOverrideComponent` to `LoginPageWrapper` / `SignupPageWrapper` in `apps/webstore/src/app/[locale]/login/page.tsx` and `signup/page.tsx` (currently `null`) | built-in hook, level 3 file edit |
| Remove a widget from the editor for a theme | `removeComponentKeys: [{ categoryKey, componentKeys: [...] }]` in the theme config or page map | `extendConfig` |

Header and footer: the header and footer editors use `get-layout-config.ts` and each theme's `page-config-layout-map`. Change them there, not in the content-page config.

## Recipe 4: widget that shows custom data

1. Create the Custom API endpoint (`sdk-custom-api`) and a client, agent and BFF route as in `bff-routes-and-clients.md`.
2. In the widget render component (`"use client"`), call the browser wrapper in an effect or with SWR (`swr` is a dependency), and render loading and empty states. Do not let a failed call break the page.
3. Keep the response small and cache-friendly. Remember page-level caches (`caching-and-visibility.md`): data fetched in the browser is always live; data fetched during server rendering can be cached for anonymous visitors.
4. In the editor the widget runs inside the Page Builder app, which has its own `/api` routes (`apps/page-builder/src/app/api`). A route that the widget calls must exist in **both** apps or the widget shows an error in the editor. Copy the route into `apps/page-builder/src/app/api/<feature>/route.ts` or render a placeholder when the editor is detected (`useIsEditing(puck)` in `packages/page-builder/src/utils/use-puck.ts`).

## Recipe 5: JSON migration when widget props change incompatibly

Page JSON has a version (`CURRENT_JSON_VERSION`, 2 in this source). `packages/page-builder/src/lib/migrations/MigrationPipeline.ts` runs registered `IVersionMigrator`s (`sourceVersion`, `targetVersion`, `migrate`). Add a migrator and bump `CURRENT_JSON_VERSION` only for structural changes to shared widgets; for your own widget prefer additive props with defaults. The KB says Znode updates page JSON automatically when a Page Builder release ships (10.4.0.0); that applies to Znode's own widgets.

## Recipe 6: Tailwind-only restyle

For colours and radii first use Dynamic Styles (no code). To style a new theme in code: define the theme object (recipe 2 step 7), use semantic classes from the base preset (`bg-primaryBtnBgColor`, `text-linkColor`, `rounded-cardBorderRadius`; the preset maps them to the CSS variables in `packages/base-components/src/tailwind-config/global.css`), and set the CSS variables inside `[data-theme='<theme>'] { ... }`. Extend rather than override Tailwind defaults (KB).
