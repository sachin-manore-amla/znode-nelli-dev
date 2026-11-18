---
name: sdk-data-exchange
description: Znode Commerce Connector Data Exchanges (multi-step exchanges with API, SFTP, Blob and Znode Import steps, authentication types, Credential Vault variables, mapping functions, scheduling, event and callback triggers, execution history, notifications, limits), custom processors (IBaseProcessor and the legacy ProcessData processor) and the deprecated legacy ERP connector with its touch points. Use when a requirement says sync, integrate, import nightly, push orders to an ERP, real-time price or inventory, or run a job on a schedule.
user-invocable: false
---

# Data Exchange (Commerce Connector) and the legacy ERP connector

## What it is
A **Data Exchange** is a configured integration that moves data between Znode and another system (ERP, CRM, PIM, file server, any HTTP API). It is configured in the Admin Console, not in code. A **step** is one transmission (API, SFTP, Blob or Znode Import). A **processor** is optional customer code that runs around a step. The **legacy ERP connector** is the Znode 9 style module (one active connector, touch points) that Data Exchanges replace.

Two terms people confuse: *Data Exchange* (Commerce Connector, new work) and *ERP connector / touch point* (legacy, deprecated). A *Scheduled Data Exchange* is the schedule record for an exchange; the *exchange* is the definition.

## Use it when / do not use it when
| Requirement | Verdict |
|---|---|
| Pull data from an ERP API, SFTP or Blob on a schedule into Znode | Supported (configuration only) |
| Push an order or account change to an ERP when it happens | Supported (event-triggered exchange), see reference 03 |
| Real-time price or inventory on the product page | Supported (callback exchange), with the limits in reference 03 |
| A transformation the mapper cannot express | Customizable (custom processor), reference 05 |
| New work on the legacy ERP connector | Do not recommend. Deprecated, one active connector only |
| Sub-5-minute polling, millions of rows in one run, guaranteed delivery with retries | Not provided by the module (no dead-letter queue, no retry UI). Say so |

## The facts that matter most
1. Admin path: **Dev Center > Commerce Connector** with Data Exchanges, Scheduled Data Exchanges, Credential Vault, Notification Configuration, Dashboard. The screens are a Commerce Connector application shown inside the Admin (verified in product source; KB 70-80).
2. New exchanges are **multi-step** only. Two-step exchanges are legacy (editable, copyable from the library) (KB, release 10.10.1.0).
3. Step transmission modes: **API, SFTP, BLOB, Znode Import**. Znode Import calls the platform import (same templates as System Settings > Imports) so validation and logs are the import's.
4. API authentication types: **Basic, OAuth 2.0, Bearer, Custom** (Custom added later; API mode only).
5. Secrets and URLs go in the **Credential Vault** as variables used as `{{Var.Name}}`. Vault works only with multi-step exchanges.
6. Scheduling: only **enabled, active** exchanges with **Trigger Execution (HTTP) off** can be scheduled. Frequency One-Time or Recurring (cron). Recommended: do not go below 5 minutes.
7. Real-time: **event** (push) and **callback** (pull) triggers need Trigger Execution (HTTP) on; those exchanges cannot be scheduled.
8. Imports through Znode Import never delete. Product and other data written are Draft until published (reference 05 of config-import-export).
9. Custom processors: `IBaseProcessor` (before and after each step, multi-step) or the legacy `ProcessData` class (two-step). Deployed with the Znode CLI. No log viewer for processors.
10. KB articles contradict each other on custom processors in multi-step exchanges. The release notes for 10.13.1.0 add them, the SDK ships a sample: **supported**. Reference 07.

## Decision guide for Nelli-Dev
| Requirement | Verdict and approach |
|---|---|
| Nightly ERP product sync | **Supported.** Multi-step exchange: API (or SFTP/Blob) source with Reiterate paging, then Znode Import (Product) destination, scheduled daily. Map only ERP-owned columns. Publish afterwards (import does not publish). Processor only if a transformation is needed. |
| Prices or inventory from a file nightly | **Supported.** SFTP or Blob source to Znode Import (Pricing, Inventory). Inventory every 15 minutes, prices every 4 hours is the documented guidance. |
| Push order to ERP on placement | **Supported.** Event exchange on Order Created. The event carries codes only, so a first step fetches the order, later steps post it. If the ERP call must succeed before checkout completes, that is **not** what an event does (it runs after). Use a method override or custom endpoint instead (sdk-method-overrides). |
| Real-time stock on the product page | **Supported with limits.** Callback exchange (Get Real Time Inventory). Runs inline: target under 2 s, ERP latency under 500 ms; cache short. If the ERP is slow, schedule a sync instead. |
| Run any job on a schedule | If the job is "call an API, move data": Supported (exchange). If it is arbitrary code with no data movement: **Not provided.** There is no generic customer job runner; use an external scheduler that calls Znode APIs. |
| Sync customers or accounts | Supported through Znode Import types Customer, Account (see config-import-export). |
| Transform data in a way functions cannot | Customizable: processor, reference 05. |
| Custom ERP only reachable by a driver or database | Needs a bridge service that exposes an API; Data Exchange needs API, SFTP or Blob. |
| Anything on the legacy ERP connector | Recommend migrating to Data Exchange. Legacy is deprecated. |

## Reference files
- `reference/01-admin-screens.md` menu paths, every field of the base definition, list actions, notifications, dashboard
- `reference/02-steps-auth-mapping.md` step modes and their fields, authentication, pagination, Znode Import types, mapping functions, macros, Credential Vault
- `reference/03-triggers-realtime.md` event and callback triggers, event modules, prerequisites, performance targets
- `reference/04-scheduling-limits.md` scheduling, history, notifications, volume limits, known limitations, release history
- `reference/05-custom-processors.md` IBaseProcessor guide, legacy ProcessData, deployment, registration
- `reference/06-legacy-erp-connector.md` touch points, scheduler, settings, Custom API plumbing, deprecation
- `reference/07-kb-vs-product.md` conflicts and which source wins

Related: `config-import-export`, `sdk-events-and-webhooks`, `sdk-extension-framework`, `sdk-custom-api`.
