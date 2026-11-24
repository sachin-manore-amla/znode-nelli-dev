---
name: review-webstore
description: Checklist for reviewing the Znode-specific parts of Webstore customization code (Next.js and TypeScript) - Webstore patterns, customization level and upgrade cost, BFF route authentication, caching and publish effects, Znode API usage, dependency compatibility, and deviations from the recommended customization levels. Not for general React or TypeScript style. Use when reviewing Webstore source, a Webstore diff, a widget, theme or BFF route.
user-invocable: false
---

# Review checklist: Webstore customization

Review only the developer's recorded Webstore project, and only the files the scope script (`nd_review_scope.py`) marked ZNODE-RELEVANT and you confirmed by reading. Generic React, TypeScript or Next.js review (style, naming, formatting, hooks idioms, general refactoring) is out of scope and is never raised, not even as a Suggestion. Every finding names the Znode rule or knowledge source it rests on (this checklist section, the Webstore knowledge reference, an API spec operation, or a knowledge skill). Read `webstore-customization` (the three levels and the ten facts), `quality-security-checks`, `quality-performance-checks`, and the reference files the change touches. Scanner output (`nd_review.py plan`) is leads; confirm each at its `file:line`.

## 1. Webstore patterns (Znode-specific only)
- BFF routes, API clients and widgets sit where the Webstore's own ones live and call the typed clients; a copy of a base component where a theme override or widget would do is a customization-level finding (section 2).
- Known behaviours of the Webstore build and the commands to verify a change are in `reference/build-test-and-known-behaviours.md`; a change that breaks the build is a Blocker. Locale strings belong in the message files.
- New logic has Jest tests (`quality-testing`).

## 2. Customization level and upgrade cost
- State the level of each change: 1 configure, 2 extend (widget, theme, new BFF route, new page, Custom API call), 3 change base source (`packages/base-components`, `packages/agents`, `packages/clients`, shared routes). Level 3 must be labelled a source customization with its upgrade-merge cost; a level 3 change where level 2 works is a Should fix.
- Files under shared package folders are flagged by the practice scan: list them as the upgrade-risk table.

## 3. Security and authentication
- Every BFF route handler checks the session or token before it returns or changes data; public routes are deliberate and carry no customer data. Ownership of ids in the request is checked against the signed-in user.
- No secret in browser code: nothing sensitive in `NEXT_PUBLIC_` variables, no token in `localStorage`, no gateway call with credentials from a `'use client'` file (call a server route).
- No `dangerouslySetInnerHTML` without sanitizing, no `eval`, no unvalidated redirect target; input validated on the server side.
- The revalidate and debug routes keep their token checks; `.env` files are not committed (the repo tracks some: report it, never read the values).

## 4. Performance and caching
- Server components and route handlers fetch in parallel what is independent; no request waterfall; no fetch inside loops.
- Caching: page and data caches respect personalization (anonymous versus signed-in); revalidation after a change is explained (`reference/caching-and-visibility.md`). Client bundles: no heavy imports in shared client components; lazy-load widgets.
- Lists are paged with a default and maximum page size; images sized.

## 5. API usage
- BFF routes call the typed clients with the right headers (`api-auth-and-headers`); routes and models match the API reference (`nd_query_spec.py op`); current API families, not the legacy v1.
- Errors and empty results handled and shown; timeouts bounded.

## 6. Dependencies and versions
- Lockfile present and committed; no `latest`, `*` or git/URL dependencies; Next.js, React and TypeScript versions as the Webstore release uses (`nd_dep_scan.py` lists them; the developer confirms against the release). Vulnerabilities need `nd_security_scan.py --audits` (network, approval).
- `patch-package` patches for third-party code are listed and justified.

## 7. Deviations from recommended practice
- Hand-rolled auth or session handling instead of the repo's; calls from the browser straight to the gateway; business rules duplicated in the Webstore that belong in a Custom API; edits to built output; a front end that bypasses the BFF.
- A need that only a Znode platform change could meet is reported as a platform change request, not worked around.

## Grading
- **Blocker:** unauthenticated route that exposes or changes customer data; secret exposed to the browser; XSS sink with unsanitized input; a platform-change recommendation; a change that breaks the build.
- **Should fix:** level 3 change where level 2 works; N+1 or request waterfalls on a hot path; floating or missing lockfile dependencies; wrong or legacy API usage; untested new logic.
- **Suggestion:** Low findings on Znode-specific points (for example a missing cache-tag note). Never style, naming or generic structure.
Below 85% confidence: mark `needs confirmation (NN%)`. Never write "secure": write "no Blocker found by these checks" and list what was not checked.
