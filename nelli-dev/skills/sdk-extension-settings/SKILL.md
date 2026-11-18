---
name: sdk-extension-settings
description: Index of which setting turns on or limits each Znode customization feature - Custom Tables, Product Information Overrides, events and webhooks (enable flag, Webhook Settings page, event subscription URLs, CORS), method overrides, extensions and Extension Observability sync, Admin Customization pages, Data Exchange and Commerce Connector (schedule, credential vault), the legacy ERP connector, the Custom API SDK host settings (names only), Commerce Portal and B Store flags, payment shipping and tax plugin configuration sets, and Webstore cache and revalidation environment variables (names only). Each row gives the setting, admin path, level, default, effect and what applying it takes, and says "no configurable setting" where there is none. Load it in the Architecture phase of any customization and whenever a question is "which setting enables or limits feature X". Details live in the config-global-settings and config-store skills.
user-invocable: false
---

# Which setting controls which customization feature

Use this table first, then open the detail file. If a feature is not in the table, say that no setting was found; never invent one.

Legend: apply = what must happen after the change. Save = Save in the Admin Console. Publish = product, catalog or store publish. Restart = restart of the service whose file changed.

## The index

| Feature | Setting (name) | Admin path or location | Level | Default | Effect | Apply | Verified |
|---|---|---|---|---|---|---|---|
| Custom Tables: field length ceiling | `CustomTableMaxFieldLengthForText`, `...ForTextArea`, `...ForNumber` | Global Settings > Custom Table Settings | Global | 100, 100, `10,2` | Rejects longer new fields and edits | Save | source |
| Custom Tables: form pre-fill | `CustomTableDefaultFieldLengthForText`, `...ForTextArea`, `...ForNumber` | same tab | Global | 50, 100, `10,0` | Pre-fills Add Field | Save | source |
| Custom Tables: on or off | none | role permissions | - | - | No configurable setting | - | module guide |
| Product Information Overrides | `EnableProductInfoOverrides` | Global Settings > Global Product Settings | Global | off | Override index at publish, product page button | Save, then full catalog publish | source, KB |
| Product Information Overrides per store | `EnableProductInformationOverrides` | Manage Store > Additional Attributes > Product Settings | Store, locale | off | Search uses overrides for the store | Save | source |
| Events feature | `ZnodeFeatureFlashEvents` | no Admin screen found | Global | on when seeded | Master switch for Custom API events | none (read on each event) | source |
| Event webhook | Webhook Settings rows | Dev Center > Webhook Settings | Module and event | none | POST to your URL | Save | source, KB |
| Cache events to the Webstore | `WebhookSubscriptionUrl` | Global Settings > Event Subscription Settings | Global | empty | Webstore drops caches | Save | source |
| Webhook timeout | `WebhookRequestTimeoutInSeconds` | API deployment | Platform | 5 s | Abort slow webhook | Znode operated | source |
| CORS for webhooks, consumer retry | `ZnodeAdminURLCorsPolicy`, `RetryCount`, `RetryInterval`, `EventRetry` | Custom API SDK appsettings | SDK | sample values | Verify call, retry | Restart SDK | KB |
| Method overrides | Method Override rows | Dev Center > Method Override | Per method | none | Hook runs only when the row is active | Save | source |
| Method override global switch | none | - | - | - | No configurable setting | - | source |
| Promotion extensions | Promotion Type: Name, Description, Class Name, Status | Dev Center > Promotion Settings > Promotion Types | Per type | none | Registers a class by exact name | Save, then Extension Observability Sync | KB |
| Extension sync | `Sync` button | Extension Observability | Platform | - | Loads the deployed DLL | Click Sync | KB |
| Admin Customization pages | Status, roles, sequence | Admin Customization > Manage | Per record | Enabled | Page or section visible to roles | Save | KB |
| Data Exchange schedule | cron or on demand | Commerce Connector > Data Exchanges | Per exchange | on demand | Runs the exchange | Save | module catalogue, KB |
| Credential Vault | Global Variables | Commerce Connector > Credential Vault | Platform | none | `{{Var.Name}}` in definitions | Save | KB |
| Legacy ERP connector | active connector, touch point schedule | Dev Center > Commerce Connector > Legacy ERP Connector | Platform | one active | Runs touch points | Save | KB |
| Custom API SDK host | appsettings keys | SDK repository | SDK | per file | Gateway, auth, broker, cache | Restart SDK | source |
| Commerce Portal defaults | default order and quote status | Manage Store > Commerce Portal Settings | Store | empty | Portal defaults | Save | module guide |
| B Store | B Store Settings tab | Manage Store | Store | tab hidden | Visible only when the module is enabled for the environment | Znode operated | source |
| Payment, shipping, tax plugins | configuration sets | System Configuration plugin pages, store tabs | Per store | none | Provider fields per store | Save | module guide |
| Webstore caching and revalidation | `ENABLE_CACHE`, `ENABLE_PAGE_CACHE`, `ENABLE_ANON_PAGE_CACHE`, `PORTAL_CACHE_TTL_MS`, `ZNODE_REVALIDATE_TOKEN` and others | Webstore environment | Webstore | see file | Cache lifetimes, revalidation | Restart Webstore | source |
| XSS, IDOR, CSP | `SkipXssValidation`, `EnableIdorValidation`, content security policy | Global Settings > API and Security Settings | Global | see `config-global-settings` | Request validation and policy | Save (XSS: recycle) | source |

## Files

| Topic | File |
|---|---|
| Every row in detail, with exact fields and messages | `reference/01-feature-settings.md` |
| Webstore cache, CDN and environment variable names | `reference/02-webstore-cache-and-env-names.md` |
| Global Settings detail | the `config-global-settings` skill |
| Store settings and publish rules | the `config-store` skill |

## The 10 facts that matter most

1. Custom Tables have no on or off setting. Only length ceilings and defaults exist, and they are Global Settings.
2. Product overrides need both the global and the store switch, and a full catalog publish after every record change (KB).
3. Events are on by default in a seeded environment, but there is no Admin screen for the master flag. Webhook rows and consumers decide who gets events.
4. Event Subscription URLs are cache events for the Webstore, not Custom API events.
5. A method override has no global switch. A missing, inactive or failing row means normal processing.
6. Deploying an extension does nothing until Extension Observability Sync is clicked.
7. Promotion Type Class Name is case sensitive and must match the class.
8. Admin Customization pages are live after Save. Roles decide who sees them.
9. Credential Vault variables work with multi step data exchanges only (KB). Deleting one in use fails runs.
10. Webstore variables are read at process start. Never put values in documents.

## Nelli-Dev decision guide

| Question | Answer |
|---|---|
| Turn on product overrides for one store only | Supported: store switch On for that store, global On, full catalog publish, Webstore source reads the fields. |
| Limit custom table field length | Supported: save the three max settings with explicit numbers. |
| Why does my new setting not show on the storefront | Level (global or store), publish if needed, Event Subscription URL and secret, store and Webstore cache lifetimes, Webstore code reads it. |
| Does this need a restart | Global or store setting in the Admin: no. Webstore variable or SDK appsettings: yes, that service. |
| Add a setting for my customization | Customizable: SDK appsettings, a custom table, or an Admin Customization page. A new Global Setting or store attribute is a platform change. |
| Stop events for one module | No configurable setting. Filter in your consumer, or deactivate the webhook row. |
| Slow method override hurting checkout | No configurable timeout. Keep the hook fast or remove the row. Needs a platform change for a limit. |
| Enable events in an environment where they are off | Needs Znode. No Admin screen was found. |

## Related

`config-global-settings` · `config-store` · `sdk-events-and-webhooks` · `sdk-method-overrides` · `sdk-custom-api` · `sdk-custom-tables` · `sdk-capability-registry` · `sdk-provider-plugins`
