# The three customization levels and the decision rules

What this answers: which of the three levels a storefront requirement belongs to, the rules for choosing, what each level costs at upgrade time, and what to say in the proposal.
Confidence: KB "Webstore Customization Guide" and "Configuring a Site Theme" (read in full) for the documented mechanisms; the merge-cost column is my assessment from the code layout (inference).

## Vocabulary people confuse

| Term | Meaning |
|---|---|
| Component | a React building block in the Webstore source (button, header, product card) |
| Widget | a component registered with Page Builder so an admin can drag it onto a page; has a config file (editable fields, defaults) and a render file |
| Page widget | a widget that is a whole commerce page (Product Details Page, Cart Page...); fixed, not draggable |
| Znode widget | a widget bound to Admin data (banner slider, product carousel, ad space...) |
| UI widget | a presentation widget (text, heading, button group, container) |
| Theme | in Admin, a named parent/child theme assigned to a store; in code, a theme package plus a Page Builder theme config plus a Tailwind theme, all keyed by the same lower-case name |
| Dynamic Styles | CSS typed in Admin (Store Experience) that overrides the starter theme's CSS variables; no deployment |

## Level 1: configure (Supported)

Use when Admin can do it. Nothing is deployed from your repo.

| Need | Where |
|---|---|
| Colours, radii, fonts through CSS | CMS > Store Experience > General Settings > Dynamic Styles; publish the store |
| Theme selection | CMS > Store Experience > General Settings > Theme; themes are listed in CMS > Site Themes |
| Page layout of any commerce page or content page | Page Builder (skill `webstore-page-builder-and-themes`) |
| New content pages, SEO, scheduling | CMS > Pages |
| Header and footer | Page Builder header and footer editors |
| Product extra info on the PDP | PIM > Products > Product Detail > Custom Fields (Additional Information tab) |
| Product highlights on cards | product highlights (see `commerce-catalog`) |
| Multi-locale content | Page Builder locale selector |
| Caching, Cloudflare | Global Settings cache management; Store > Additional Attributes > Cloudflare Setting |

## Level 2: extend (Customizable)

Additive code in your Webstore repository. The KB documents: custom widgets (`ComponentConfig` plus render file registered in `base-components-config.ts`), theme packages (scaffold with Nx, `override-component-list.ts`, `root-config.ts`, `page-config-map`, registered in `get-config.ts`), and Tailwind themes. The product source adds requirements the KB does not list (second loader `get-layout-config.ts`, the `IComponentProps` type, Tailwind wiring in both apps); see `kb-vs-product.md`.

| Extension | Typical effort | Touches shared files |
|---|---|---|
| New UI widget | hours | `base-components-config.ts`, `types/page-builder.ts` |
| New theme with styling only | hours to a day | `get-config.ts`, `get-layout-config.ts`, two Tailwind configs, `tsconfig.base.json` |
| Theme that replaces widgets | days | the above plus the theme's own config files |
| Theme that replaces a page widget (product details, list, cart, checkout) | days to weeks, you own a copy of that page's component tree | the theme only, after wiring its page map |
| New BFF route plus client, agent, wrapper | hours | `custom/index.ts` and `http-request/index.ts` exports |
| New route-based page | hours | one new folder under `apps/webstore/src/app/[locale]/` |

## Level 3: change base source (Customizable, labelled as source customization)

Editing files that exist in the product: `packages/base-components/**`, `packages/agents/**`, `packages/clients/**`, existing routes in `apps/webstore/src/app/**`, `apps/webstore/server.js`, middleware, shared constants.

Costs and risks to state in the proposal:

- Every upgrade of the Webstore source can conflict with your edits. Release notes show frequent changes in cart, checkout, page builder and cache code (for example 10.4.1.0 added Cart and Check-Out pages to Page Builder, 10.7.0.0 moved to Next 15 and React 19, 10.9.1.0 upgraded the Puck editor).
- Code that changes totals, taxes, shipping or inventory rules in the UI will disagree with the API. Keep rules in the API.
- The checkout page is a single large page widget (`packages/base-components/src/components/checkout`); adding a step means editing it, which is level 3.

## Decision rules

1. Ask: can an admin do it with Page Builder, Dynamic Styles, a store setting or a custom field? Then Supported. Say how.
2. Is it new presentation that can be a widget placed on a page? Level 2 widget.
3. Does it need a different look across the whole store? Level 2 theme. Colours only: Dynamic Styles first (Supported), Tailwind theme second.
4. Does it replace how a commerce page is built (list, details, cart, checkout)? Level 2 theme override if the page widget can be replaced as a whole; otherwise level 3.
5. Does it need data that Znode does not return? Add a Custom API endpoint (`sdk-custom-api`) and a BFF route; never read databases from the Webstore.
6. Does it change money, stock or rules? Not a Webstore change: API, method override, plugin, or events.
7. Prefer the smallest diff: a theme copy beats editing base; a new file beats an edit; a wrapper beats a fork.
8. State the Znode version and the Webstore commit in the proposal, and label level 3 changes "customization of source, not a supported extension point".

## What to put in the proposal for level 2 and 3

| Item | Content |
|---|---|
| Files added / files edited | separate lists; edited shared files carry upgrade risk |
| Both apps | the change must build in `webstore` and `page-builder` |
| Admin steps | theme creation, store theme selection, publish store, page publish |
| Cache steps | what must be refreshed (see `caching-and-visibility.md`) |
| Tests | lint, build, a manual path through the page in preview and production state |
| Rollback | switch the store's theme back, or remove the widget from pages before removing code (the KB states that every widget used in a page must be registered) |
