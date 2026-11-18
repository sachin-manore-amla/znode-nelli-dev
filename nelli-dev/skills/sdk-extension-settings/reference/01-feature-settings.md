# Settings per customization feature (detail)

What this answers: for each customization feature, the setting that turns it on or limits it, where it lives, level, default, effect and what applying it takes. "Verified" tags: P = product source or development environment (90), M = module guide (85), K = KB article read in full (80), S = KB summary (70), I = inference (below 50, said so).
"No configurable setting" is stated where the product has none.

## 1. Custom Tables (P, M, K)

| Setting | Path | Level | Default | Effect | Apply |
|---|---|---|---|---|---|
| Max field length Text, Text Area, Number | `System Settings > Global Settings > Custom Table Settings` | Global | 100, 100, `10,2` seeded | Ceiling on new fields and edits | Save |
| Default field length Text, Text Area, Number | same tab | Global | 50, 100, `10,0` | Pre-fill of the Add Field form | Save |
| Turn custom tables on or off | none | - | - | No configurable setting. Access is by role permission (`Custom Table / List` menu, `Create Custom Table`) | Role change |
| Table key and table name length | none | - | 100 each | Fixed limits, no configurable setting | - |
| Change events for records | the event flag in section 3 | Global | on in seeded environments | Record created, updated, deleted events when events are enabled | See section 3 |
| Export file storage and event bus of the Custom Table service | service deployment settings | Platform | per deployment | Znode operated; not customer configurable | Restart by Znode |

Details and messages: `config-global-settings/reference/03-customization-settings.md`.

## 2. Product Information Overrides (P, M, K)

| Setting | Path | Level | Default | Effect | Apply |
|---|---|---|---|---|---|
| Enable Product Information Overrides (`EnableProductInfoOverrides`) | `Global Settings > Global Product Settings` | Global | off | Button on the product page, override index built at publish | Save, then full catalog publish |
| Enable Product Information Overrides (`EnableProductInformationOverrides`) | `Stores > Stores > Manage > Additional Attributes > Product Settings` | Store, per locale | off | Search uses override data for that store | Save |
| Override records | `PIM > Product Information Overrides` or the override API | Data | none | Alternate SKU, name, short and long description per SKU, store code, locale code (and account code) | Publish. KB: first time and after every change run a full catalog publish with "Publish Draft Products Only" not selected |
| Record routes gated by the switches | none | - | - | No: create, update, delete and the system table screens work with both switches off | - |

Behaviour to know: the override index is not visible in the Admin; Publish History shows only the main catalog publish time, so allow extra time; saving a record through the API does not set the product to Draft; the Webstore must be customized to display override data.

## 3. Events and webhooks (P, K)

| Setting | Path | Level | Default | Effect | Apply |
|---|---|---|---|---|---|
| Events feature flag `ZnodeFeatureFlashEvents` | No Admin screen found | Global | On in a seeded environment (row present with the sub value `true`); off when the row is missing or the sub value is not `true` | Master switch. Off means no Custom API event is published and an info log says so | Read on every event, no cache. No restart |
| Webhook Settings | `Dev Center > Webhook Settings > Manage Webhook Settings` | Per module and event | no webhook | Fields: Event Module, Event Name (Created, Updated, Deleted), Is Active, Webhook Url, Verify, Authorization. Module and event cannot be edited after create | Save clears the event cache. Duplicate error: `WebHookURL is already configured for this event.` Verify success: `The URL is verified successfully.` |
| Default consumer | Custom API SDK event consumer over RabbitMQ | Deployment | all enabled events processed | Receives every enabled event without a webhook | SDK redeploy |
| Webhook request timeout `WebhookRequestTimeoutInSeconds` | API deployment setting | Platform | 5 seconds | Post abandoned after N seconds; failure logged, not retried | Znode operated |
| Event Subscription URLs `WebhookSubscriptionUrl` | `Global Settings > Event Subscription Settings` | Global | empty | Cache events sent to the Webstore (not Custom API events) | Save |
| Shared secret `WebstoreWebhookSecret` and Webstore `ZNODE_REVALIDATE_TOKEN` | API deployment setting and Webstore environment variable | Platform | empty | Header `x-secret` must match or the Webstore answers 401 | Restart of the service that changed |
| Retry for the RabbitMQ consumer | SDK `EventBus` keys `RetryCount`, `RetryInterval`, `EventRetry` | SDK deployment | sample `2`, `200`, `true` | Consumer retry. Units are not stated by the KB | SDK restart |
| CORS for webhooks | SDK key `ZnodeAdminURLCorsPolicy` (the KB says required only for webhooks) | SDK deployment | none | Allows the Admin origin to reach the Custom API (for the Verify call) | SDK restart |
| Per module switches | none | - | - | No configurable setting: events cannot be limited per module except through the webhook rows above | - |
| Bulk imports | none | - | - | No events are raised by bulk import (K, existing skill) | - |
| Global Settings save | none | - | - | A save raises a "User Defined Field, Updated" event for the settings entity (P) | - |

Authorization header: the `Authorization` field is optional and carries an API key or token. The webhook payload carries `znode-multifront/1.0` for request whitelisting (K).

## 4. Method overrides (P, K partial)

| Setting | Path | Level | Default | Effect | Apply |
|---|---|---|---|---|---|
| Method Override list | `Dev Center > Method Override` (menu text may read "Method Override Settings") | Per method | no override | Fields: Method for Override (module and method), Webhook URL, Authorization, Active, Verify | Save clears the method override cache (P) |
| Global feature flag | none | - | - | No configurable global switch: an override runs only when its row is active | - |
| Methods that can be overridden | the Method for Override list | Platform | - | Seeded methods seen in the product: `CommerceCalculateCompleted` (cart calculation), `InitiateTaxCalculationCompleted`, `SetTotalSectionInEmailTemplateCompleted`, `BindEmailTemplateDetailsStarted`, `SendEmailCPAdministratorCompleted`. The module catalogue lists quote and order receipt methods. Use the dropdown as the truth | - |
| Failure behaviour | none | - | - | Any error, a missing row, an inactive row or a null response falls back to normal processing. Calls over 2 seconds log a warning | - |
| Execution limit | none | - | - | No configurable timeout setting was found for method overrides. Treat the hook as synchronous in the shopper path | - |

## 5. Extensions and Extension Observability (K, P)

| Setting | Path | Level | Default | Effect | Apply |
|---|---|---|---|---|---|
| Promotion Types | `Dev Center > Promotion Settings > Promotion Types` | Per type | none | Fields: Name, Description, Class Name, Status. Class Name must match the class in code exactly (case sensitive) | Save |
| Extension Sync | `Extension Observability` page, button `Sync` | Platform | - | Reloads deployed extensions. "Deployment alone does not activate the extension" (K) | Click Sync after every deployment |
| Execution logs | `Extension Observability > Execution Logs` | - | - | Read only logs with filters | - |
| Extension deployment | Znode CLI `znode deploy extension` | - | - | Uses a connection token | - |
| Extension host settings (extension folder, platform version, hot reload, observability store) | Commerce Portal API deployment | Platform | hot reload only in Development | Znode operated. No customer setting | Restart by Znode |
| Class name registration | the Promotion Type row plus the class attribute and base class in code | - | - | See `sdk-capability-registry` | - |

## 6. Admin Customization pages (K)

| Setting | Path | Level | Default | Effect |
|---|---|---|---|---|
| Admin Customization pages and sections | `Admin Customization > Manage`, `Add New` then `New Page` or `New Section` | Per record | none | Page fields: Code (cannot change), Name, Content Type (iFrame or Raw HTML, or URL), Content Details, Select Roles, Sequence Number, Status. Section fields add Entity Type |
| Status | Enable Page toggle, bulk enable, disable, delete in the Tools menu | Per record | Enabled for pages | Hidden when disabled |
| Roles | Select Roles, All Roles includes future roles | Per record | none | Full Access with Delete, Full Access without Delete, No Access. Denied message `Access Denied, Please contact Site Administrator.` |
| Limits | none | - | - | Maximum number of records not stated. HTML and URL content have limited validation. No global setting |
| Apply | - | - | - | Reflected immediately after saving (K). Needs the Admin Customizations and Manage Pages permissions |

## 7. Data Exchange (Commerce Connector) and the legacy ERP connector (K, S)

| Setting | Path | Default | Effect |
|---|---|---|---|
| Data exchange definition | `Dev Center > Commerce Connector > Data Exchanges` | none | Source and destination types: API (Basic, OAuth 2.0, Bearer, custom), SFTP, Blob, Znode Import; mapping templates and macros |
| Schedule | Base definition and scheduler: on demand or cron | on demand | Cron expression of the exchange |
| Real time | Znode events (push) or callback (pull) | off | Needs the events flag in section 3 |
| Credential Vault | `Commerce Connector > Credential Vault` | none | Global Variables: Key, Value, `Mark As Secret (Value Will Be Hidden)`, Description. Referenced as `{{Var.VariableName}}` in URLs, headers, body and mapping. KB: works with multi step exchanges only. Deleting a variable in use can fail runs. Secrets are stored encrypted and hidden after save |
| Notification emails | Data Exchange notification templates | not stated | Error and info emails |
| Open Commerce Connector from Admin | Admin link | - | Needs `EnableCCAPICalls` (Global Settings, default `false`) as seeded (I: purpose inferred from the setting name) |
| Legacy ERP Connector | `Dev Center > Commerce Connector > Legacy ERP Connector`, then `<ERP Name> Configuration > Settings` | none | Only one connector active at a time. Touch point scheduler type default `Scheduled`; One Time (Start Date, Time, Enabled) or Recurring (Cron Expression, Enabled); Clock icon runs now |
| Connection fields of the ERP | per ERP | - | Vary by connector, not stated |

Behaviour to know: Data Exchange supersedes the legacy ERP connector. Run history and a dashboard exist. The KB general user guide does not state retry or limit settings.

## 8. Custom API SDK host (names only, P)

Keys the SDK host reads in its appsettings (no values here):

| Key | Purpose |
|---|---|
| `Logging.LogLevel.Default` | Log level |
| `ConnectionStrings.ZnodeMongoDBForLog` | Log store |
| `Caching.CacheType`, `Caching.RedisCacheConnectionString`, `Caching.CacheExpirationMinutes` | In memory or Redis cache |
| `EventBus.MessageBrokerService`, `ServiceBusConnectionString`, `RabbitMQConnectionString`, `RabbitMQManagementUrl`, `RabbitMQUserName`, `RabbitMQPassword`, `QueueName`, `RetryCount`, `RetryInterval`, `EventRetry` | Broker and retry |
| `appsettings.ZnodeApiGateway`, `ZnodeTenantManagerUri` | Gateway and tenant manager addresses |
| `ZnodeApiDomainName`, `ZnodeApiDomainKey`, `ZnodePaymentApiDomainName`, `ZnodePaymentApiDomainKey`, `ZnodePrivateKey` | Domain (Basic) auth and keys: secrets |
| `IsGlobalAPIAuthorization`, `EnableBasicAuthorization` | Authorization mode |
| `ZnodeAdminURLCorsPolicy`, `ZnodeCorsAllowedURLS` | CORS origins |
| `ClientLoggingKey`, `IsCustomLoggingEnabled` | Logging switches |
| `AssemblyLoadCacheDurationMinutes`, `ErpInstanceCacheDurationMinutes` | ERP touch point assembly and instance caches |
| `UseDynamicSwaggerJson`, `AllowedHosts` | Swagger and host filter |
| `ZnodeApiUriItemSeparator`, `ZnodeCommaReplacer`, `ZnodeApiUriKeyValueSeparator` | Query encoding helpers |

Apply: restart of the SDK host. Never commit values. Use the secret store of the environment.

## 9. Commerce Portal, B Store, plugins

| Feature | Setting | Path | Notes |
|---|---|---|---|
| Commerce Portal | Default order and quote status for the portal | `Manage Store > Commerce Portal Settings` | Per store, Save. The Commerce Portal always reads the Production publish state (a fixed value) |
| Commerce Portal | Order approval routing | `Manage Store > Approval Management` | Per store |
| B Store | B Store Settings tab | `Manage Store > B Store Settings` | Visible only when the B Stores module is enabled for the environment (deployment setting of the Admin, default off). No customer setting |
| B Store | Customized catalog and B Store access | B Store routes (`GET/PUT /v2/b-stores/users/{userId}/stores`) | Per user |
| Payment, shipping, tax plugins | Configuration sets | `System Configuration > Managing Payment Process Plugins`, shipping and tax plugin pages; associated on store tabs Storefront Payment Methods, Offline Payment Methods, Shipping Methods, Tax Settings | A set is created per plugin and associated per store. Display name unique per store: `This Payment Name already exists. Please enter a different Payment Name.` Association messages: `Associated successfully.`, `Unassigned successfully.` |
| Plugins | Plugin fields | From the plugin template (for example `UniqueName` labelled Configuration Code, `DisplayName`, gateway and key fields), `VaryBy` store | Stored as a set; secrets are entered in the Admin Console |
| Address validation | Configuration Set | Additional Attributes, Address Validation Settings | One set per store, USPS only |
