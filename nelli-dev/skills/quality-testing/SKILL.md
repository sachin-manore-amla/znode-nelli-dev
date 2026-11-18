---
name: quality-testing
description: How Nelli-Dev writes and runs tests for a customization - xUnit for Custom API SDK code (the SDK has no test project), Jest/Nx for the Webstore, integration tests against the customer's hosted environment through the gateway, regression runs and the test evidence format. Use in the Test phase and when drawing up the test plan.
user-invocable: false
---

# Testing a customization

## What exists (verified 2026-10-09)

- **Custom API SDK** (`master` @ `7e30a61`): no test project. Create one next to the code, for example `Custom.Api.Core.Tests` (xUnit), reference the project under test, and mock the Znode clients and `IZnodeLogging`.
- **Webstore** (`qat` @ `f90ca894d`): Nx workspace with Jest (about 60 spec files) and scripts `npx nx test <project>`, `npx nx lint <project>`, `npx nx build <project>`, where the app projects are `webstore` and `page-builder`.

## Levels

| Level | Tool | Covers | Runs against |
|---|---|---|---|
| Unit | xUnit (SDK), Jest (Webstore) | Service logic, calculations, mapping, validation, components | Nothing external (mocks) |
| Integration | xUnit or `curl.exe` scripts through the gateway | The custom endpoint end to end, including the Znode calls it makes | The customer's hosted development environment |
| Functional | Playwright (Webstore flows) or scripted calls | The acceptance criteria as a shopper or integrator sees them | Hosted development environment |
| Regression | Existing suites + the flows next to the change | Nothing that worked before broke | Both |

## Writing the test plan

1. One or more **Must-Pass** cases per acceptance criterion; trace each to the criterion id.
2. Negative and boundary cases: empty, null, maximum sizes, wrong types, expired or missing token.
3. **Authorization and ownership cases:** another shopper's/account's id must be refused (see `quality-security-checks`).
4. Multi-store, locale, currency, and B2B account cases where the requirement touches them.
5. Data cases: records that exist before the change must still behave.
6. Mark the level, who automates it, and which need test data.

## Rules for execution

- **Build first, then test.** Record the exact commands in `test-results.md`.
- **Tests that change data** (create/update/delete on the hosted environment) need the developer's approval of that exact set, and clean up what they create or use clearly marked test records.
- **Only the gateway the developer gave** (recorded with `nd_env.py`, confirmed non-production) is ever called. Run `nd_env.py check` before the first integration run and report the result; if it is unreachable or credentials are not set, say so and stop that level rather than guessing.
- **Never use production** or real customer data; never put credentials in test files (read `ZNODE_API_BASIC` / `ZNODE_API_TOKEN` from the environment).
- A failing test is evidence: fix the cause or report it; never weaken a test to pass.
- Run the unchanged baseline first when the environment is shared, so an environmental failure is not blamed on the change.

## Evidence format (`test-results.md`)

| Case | Level | Command | Result | Evidence (log path or output excerpt) |
|---|---|---|---|---|

End with totals, failures with their cause, cases not run and why, and the line `Checked: ...` (see the document templates).

## Related

`sdk-conventions` · `quality-security-checks` · `quality-performance-checks` · `webstore-customization`
