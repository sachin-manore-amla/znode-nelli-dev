---
name: review-sdk
description: Checklist for reviewing Custom API SDK customization code (C#) - quality and maintainability, SDK compatibility and registration, authentication and ownership, performance, API usage, dependency and version compatibility, and deviations from the recommended customization practice. Use when reviewing SDK code, an SDK diff, or an SDK extension.
user-invocable: false
---

# Review checklist: Custom API SDK customization

Review only the developer's recorded SDK project. Znode core services are never in scope and never the recommendation: the fix is always an SDK-side or supported-extension change.
Read `sdk-conventions`, `sdk-custom-api` and the registry entry of the extension point the code uses (`nd_registry.py show <id>`), and `quality-security-checks` / `quality-performance-checks`. Scanner output (`nd_review.py plan`) is leads; confirm each at its `file:line`.

## 1. Quality and maintainability
- Layering as in the samples: model, service interface and implementation, controller that injects the interface only; no business logic in the controller; no data access in the controller.
- Names and folders follow the surrounding code; no dead code, copy-pasted blocks or commented-out code; methods small enough to test.
- Catch blocks log with the SDK logger and either rethrow or return a defined error; no empty catch; `throw;`, not `throw ex;`.
- Tests: new logic has xUnit tests with the Znode clients mocked (the SDK ships no test project: its absence is a Suggestion, an untested new service is a Should fix).

## 2. SDK compatibility and implementation patterns
- Every new service and every Znode client it injects is registered in the dependency registration; an unregistered service fails at run time.
- The code uses the extension point the way its registry entry documents (event consumer, method-override receiver, promotion extension, custom endpoint, data exchange processor, plugin). Check the contract: request and response envelope, required fields, return values (for method overrides, `SkipExecution` semantics), timeouts.
- New endpoints that must be reachable through the gateway are present in the Ocelot route file; routes do not collide with existing ones; versioned route prefix is consistent.
- Typed Znode clients, not hand-built HTTP to the Znode API root. No reflection into or copying of Znode core types that are not part of the SDK.
- Template weak spots are not copied into new code (new `HttpClient` per call, `.Result`, open CORS): see `sdk-conventions`. If the change touches the same files, say so; do not demand a rewrite of template code outside the change.

## 3. Security and authentication
- Every endpoint authenticates; `[AllowAnonymous]` only where the requirement says public, and then no customer data.
- Ownership: every caller-supplied id (account, order, user, portal, cart) is checked against the caller's own context before the record is read or changed. The scanner flags candidates; read each action.
- Tenancy: portal or store context is taken from the authenticated context, not trusted from the request.
- Input validated and bounded (length, range, count); no string-built SQL; customer-owned tables only for direct data access.
- Secrets: none in code or logs; configuration through the host's configuration, not constants. Webhook and method-override receivers validate the shared secret. CORS restricted to the storefront origin(s).
- Errors returned to the caller are generic; details are logged.

## 4. Performance
- No remote or data call inside a loop (N+1); independent calls not awaited one after another; no `.Result`, `.Wait()` or `GetAwaiter().GetResult()`.
- Pagination with a default and a maximum page size on every list; no overfetching; cache stable lookups with an explicit lifetime and invalidation, and say what the cache keys include (store, profile, user).
- Count the Znode calls per user action (the call-budget table of `quality-performance-checks`).

## 5. API usage
- Routes, methods and models match the API reference for the developer's environment (check with `nd_query_spec.py op`); current API families, not the legacy v1 where a current one exists; headers and authentication as in `api-auth-and-headers`.
- Status codes and error handling for each Znode call; timeouts and retries are bounded.

## 6. Dependencies and versions
- All `Znode10.*` / `Znode.*` packages at one version, matching the developer's Znode release; no floating versions or unexpected pre-releases; target framework as the SDK host's. `nd_dep_scan.py` lists them; whether they match the release is for the developer to confirm with the release notes. Vulnerabilities need `nd_security_scan.py --audits` (the developer approves network use).

## 7. Deviations from recommended practice
- A requirement met by core-service changes, copied core code, or edited NuGet packages is a Blocker: the supported route is an SDK extension point, a method override, an event, a custom table or configuration (`meta-customization-landscape`).
- Customization that bypasses Znode (direct writes to Znode tables, ad hoc scheduled jobs against core data) is a Blocker unless the registry marks it supported (`direct-data-access`, customer-owned tables only).

## Grading
- **Blocker:** a confirmed Critical or High security finding; missing authentication or ownership check; an unregistered service or broken contract (will not run); a core-change recommendation; data loss.
- **Should fix:** Medium findings; N+1 or blocking calls on a hot path; wrong or legacy API usage; mixed or floating Znode package versions; untested new logic.
- **Suggestion:** Low findings, naming, structure, template spots outside the change.
Below 85% confidence: mark `needs confirmation (NN%)`. Never write "secure": write "no Blocker found by these checks" and list what was not checked.
