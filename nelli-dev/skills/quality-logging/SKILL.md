---
name: quality-logging
description: The Znode logging standard - TraceLevel semantics and decision tree, what must always be logged versus what must never be logged, the component tags, IZnodeLogging usage and the common anti-patterns. Use when adding logging to a controller, cache or service, or when reviewing whether a diff logs correctly.
user-invocable: false
---

# Znode Logging Standard

| Layer | Framework | Interface |
|---|---|---|
| Znode API (core) | **log4net** | `IZnodeLogging` / `ZnodeLoggingHelper` |
| ASP.NET Core host | `Microsoft.Extensions.Logging` + log4net adapter | — |
| Azure Functions | `Microsoft.Extensions.Logging` | `ILogger<T>` |
| Telemetry (optional) | Application Insights | log4net appender |

Sinks: MongoDB (primary), SQL `ZnodeActivityLog` (audit), optional App Insights. An SMTP alert appender fires on `Error`.

## Trace levels

Znode uses `System.Diagnostics.TraceLevel`, **not** log4net's `Level`.

| Value | log4net | When |
|---|---|---|
| `Error` (1) | ERROR | Unhandled exceptions, unrecoverable failures. Triggers the email alert appender |
| `Warning` (2) | WARN | Expected failure the caller handles — `ZnodeAuthorizationException`, concurrency races |
| `Info` (3) | INFO | Lifecycle events: startup, cache invalidation, job completion, config change |
| `Verbose` (4) | DEBUG | Method entry/exit, resolved values, branch taken |
| `Off` (0) | — | Rarely used; prefer deleting the call |

> `LogMessage(message)` with no level **defaults to `Verbose`**.

```
Completely broken, needs attention?        -> Error
Degrades gracefully but unexpected?        -> Warning
Significant lifecycle/state/business event?-> Info
Method entry, branch, resolved value?      -> Verbose   (required, not noise)
```

## The non-obvious rule

**Happy-path logging at `Verbose`/`Info` is expected and required.** It is the primary way to diagnose production issues without a debugger. Every public method should log its entry parameters and key outcomes at `Verbose`. Do not strip these in review — missing them is the finding.

## Must always be logged

| What | Level |
|---|---|
| Method entry + parameters | Verbose |
| Full request model, `HelperUtility.ToJSON(request)` | Verbose |
| Cache hit / miss | Verbose |
| Service or cache return summary | Verbose |
| Resolved IDs (portal, locale, catalog, user) | Verbose |
| Business rule triggered / branch taken | Info |
| State change (create/update/delete) | Info |
| Background job, cache invalidation | Info |
| `ZnodeAuthorizationException` | Warning (full exception object) |
| Any `ZnodeException` / `Exception` | Error (full exception object — **never** `.ToString()`) |

## Must never be logged

Passwords and password hashes · payment tokens, card numbers, CVVs · OAuth tokens, API keys, JWT bearer values · SMTP credentials · private encryption keys · full SSN or government IDs.

Everything else — names, addresses, IDs, amounts, flags, enum values — **should** be logged.

## Components

Pass `ZnodeLoggingEnum.Components.X.ToString()`; it tags the record so MongoDB can be filtered by domain.

`OMS` (orders, cart, checkout, quotes, returns) · `PIM` (products, publish, categories, catalogs, attributes) · `Admin` (users, admin auth, admin portal) · `Webstore` (storefront controllers) · `Shipping` (rate calls, carriers) · `"Diagnostics"` (startup health checks).

> No fitting component? **Add a value to the enum** — never pass a free-form string.

## Anti-patterns

- Logging an exception with `.ToString()` instead of the exception object
- Free-form component strings instead of the enum
- Stripping `Verbose` happy-path logs as "noise"
- Logging any item from the never-log list
- Catch blocks that swallow without logging
- `Error` level for conditions the caller is expected to handle (use `Warning`)

## KB source

- [Application Logs, Diagnostics & Maintenance](https://support.znode.com/support/solutions/folders/43000598159)

> Standard is code/agent-derived; the KB folder covers the admin-facing log tooling.

## Extension libraries (promotion extensions and similar) use a different logger

Code in an extension library (for example a promotion extension built on `Znode10.Libraries.Promotions.SDK`) logs through `IExtensionLogger` (`Znode.Libraries.Extensions.Observability.Services`), obtained from `ServiceProvider`. It has **no Verbose level**, so the Verbose rules above do not apply there. Verified members (package `Znode10.Libraries.Extensions.Observability` 10.0.0-rc-01, read by reflection 2026-10-10):

- `LogInformationAsync(extensionName, className, method, message, correlationId = "")`
- `LogWarningAsync(extensionName, className, method, message, correlationId = "")`
- `LogErrorAsync(extensionName, className, method, Exception exception, executionTimeMs = 0, correlationId = "")` and `LogErrorAsync(ExtensionLog log, Exception exception)`
- `BeginLog(extensionName, className, method, correlationId = "")` and `CommitAsync(ExtensionLog log)`

Rules: log counts, ids and amounts only (never customer data or secrets); a log call must never break the calculation (wrap the error log in its own try/catch and do not await it in a hot path); treat an information log on every evaluation as noisy and keep it to decisions that matter.

## Related
`sdk-conventions`
