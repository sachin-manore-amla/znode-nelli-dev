# Build, lint, test commands and known behaviours

What this answers: the commands to run, build and check the Webstore, how Page Builder preview is opened locally, and behaviours that surprise people.
Confidence: commands from the KB (80) and the source scripts (90); behaviours verified by reading the source unless marked "not run".

## Setup

Prerequisites (KB): Node.js 18 or later, npm or Yarn, Git, Visual Studio Code. The source's own dependency set targets Node versions that support Next 15; use a current LTS if 18 fails (not run). Get the source through the Znode CLI ("How to Install and Set Up Znode CLI"), then `npm install` (a `postinstall` step applies `patch-package` patches). Fill `apps/webstore/.env` and `apps/page-builder/.env` (names in `environment-variables.md`).

## Commands

| Task | Command |
|---|---|
| Run Webstore (dev, Turbopack) | `npx nx dev webstore` (or `npm run webstore:dev`) |
| Run Page Builder (dev) | `npx nx dev page-builder` (or `npm run page-builder:dev`) |
| Production build | `npx nx build webstore`, `npx nx build page-builder` (or `npm run build` for all) |
| Run production build | `npx nx start webstore` (the apps also have a custom `server.js`; the container image runs it) |
| Lint | `npx nx lint webstore`, `npx nx lint page-builder`, or `npm run lint` (all projects except `page-builder-lib` and `clients`) |
| Unit tests | `npx nx test <project>`; Jest is configured, but the source contains one spec file (cache package), so write your own |
| Clear Nx cache | `npx nx reset` |
| Format | `npm run prettier` |
| Spell check | `npx cspell --config cspell.json <files>`; add legitimate words to `cspell.json` |

Both apps default to port 3000; the second one Next starts picks another port, or set `PORT`. KB writes both as 3000.

## Open the editor locally

`http://localhost:<port>/en-US/page-builder?url=header&theme=base&publishState=preview&themeCode=base&storeCode=<StoreCode>&pageCode=Header` (KB). Query parameters: `url` (page or section), `theme`, `publishState` (`preview` or `published`), `themeCode`, `storeCode`, `pageCode`. The source also accepts `contentPageCode`, `contentPageId`, `versionNumber`, `mode`. A store domain entry must exist for routing and preview.

## Commit hook

`.husky/commit-msg` runs, in order: spell check on staged files, `npm run lint`, `npm run build`, and commitlint. commitlint extends the `jira` preset (the message must follow a Jira-key style). Change `commitlint.config.ts` to your own convention. If a step fails the commit is aborted. Fixes: run each step by hand, add words to `cspell.json`, fix lint.

## Lint rules worth knowing

Double quotes, semicolons, no `console` calls, no `any`, no unused variables (prefix with `_`), hooks rules as errors, max 500 lines per function and 1000 per file, `@nx/enforce-module-boundaries` as a warning.

## Known behaviours

| Behaviour | Detail |
|---|---|
| Type errors do not fail the webstore build | `ignoreBuildErrors` is true for `webstore`, not for `page-builder` |
| Widgets missing from the editor | usually not listed in a category (`addComponentToCategories` for a theme, or the base `categories` list), or the theme is not in `get-config.ts` (KB troubleshooting agrees) |
| Theme override not applied | KB: override missing from `root-config.ts`; source: for page widgets the base page map is spread after the theme list (see `recipes-widgets-and-themes.md` 3b) |
| Component not rendering in the Webstore | not registered or wrong alias; confirm the `@znode/...` alias exists in `tsconfig.base.json` |
| Editor crashes after adding a widget | undefined props in render; use defaults and defensive code (KB) |
| Hydration mismatch | server and client output differ (browser-only APIs, non-deterministic rendering) (KB) |
| Edits in the editor not visible in local Webstore preview | KB: both `.env` need `IS_DEBUGGING=true`; Webstore needs `ENABLE_CACHE` off; restart both. The cache folder must be writable |
| "Enable the Publish button" step | KB says set `ENABLE_EDIT_WIDGET: true` in `packages/page-builder/src/constants/visual-editor.ts`. In the source that flag controls whether default page widgets can be deleted or duplicated and whether the editor header slot is shown; I found no Publish button gating (see GAPS) |
| Page widgets cannot be moved or inserted | `permissions` in their configs; delete and duplicate depend on that flag |
| Missing static assets | return a proper error status since 10.11.1.0 (release note) |
| Old page JSON | migrated on read; Puck 0.21.1 converts Dropzone zones to slots automatically on both editor and storefront |
| Different content per pod | caused by missing Redis or missing revalidation on a pod (see caching file) |
| `override-mapper.ts` | lists the bundled theme but nothing imports it |
| `@znode/data-providers` alias | points to a package that does not exist |
| Hard-coded locale id map and `lang` attributes | see locale recipe |
| Sitemap and robots | served by routes under `api/sitemap` and `api/robots` through rewrites in `next.config.js` |

## Verdict guidance for reviews

- A pull request that edits `packages/base-components`, `agents` or `clients` is level 3: list each edited file and its upgrade risk.
- A new route without a session check on private data is a security finding (`quality-security-checks`).
- Secrets in `NEXT_PUBLIC_*`, or domain key use in client code, are blockers.
- New code that calls Core API v1 needs a documented reason.
- Tests: lint and both builds are mandatory; add Jest tests for new pure functions and agents (`quality-testing`).
