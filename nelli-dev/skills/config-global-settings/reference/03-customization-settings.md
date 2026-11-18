# Global Settings for customization and data extension

What this answers: the settings that decide how custom tables, product information overrides, events, publish, index, import and export behave, with exact keys, defaults, ranges, and what a change needs.
Facts tagged: product source (verified 2026-10-15), module guide, KB article, or inference.

## 1. Custom Table Settings

Admin path: `System Settings > Global Settings > Custom Table Settings`. Scope: global only. There is no store-level or per-table override.

| Label on screen | Key | Type | Seeded default | Allowed range in the form | Effect |
|---|---|---|---|---|---|
| Text (under "max") | `CustomTableMaxFieldLengthForText` | Whole number, required | `100` | 1 to 4000 | Largest `FieldLength` accepted for a Text field |
| Text Area (under "max") | `CustomTableMaxFieldLengthForTextArea` | Whole number, required | `100` | 1 to 8000 | Largest `FieldLength` accepted for a Text Area field |
| Number (under "max") | `CustomTableMaxFieldLengthForNumber` | Text `precision,scale`, required | `10,2` | not validated in the form | Largest precision and scale accepted for a decimal (`Numeric`) field |
| Text (under "default") | `CustomTableDefaultFieldLengthForText` | Whole number, required | `50` | 1 to 4000 | Length pre-filled when a user adds a Text field in the Admin |
| Text Area (under "default") | `CustomTableDefaultFieldLengthForTextArea` | Whole number, required | `100` | 1 to 8000 | Pre-filled length for Text Area |
| Number (under "default") | `CustomTableDefaultFieldLengthForNumber` | Text `precision,scale`, required | `10,0` | not validated | Pre-filled precision and scale |

Sources: seeded values and form ranges verified in the product source (2026-10-15); the "max" behaviour verified in the field validation code.

Rules (exact messages):

| Situation | Message | Where it appears |
|---|---|---|
| Text or Text Area length above the setting | `Input value must not exceed the maximum character limit of {max}.` | In the `FieldValidationMessages` of the field in the 400 response, not in the top-level error message |
| Length is not a positive whole number | `FieldLength for field '{code}' must be a positive integer.` | Same place |
| Numeric length has no scale | `FieldLength for field '{code}' must include both precision and scale (e.g., "10,2").` plus ` The configured maximum is {max}.` when a maximum is set | Same |
| Numeric length not two integers | `Invalid format for numeric field '{code}'. Use 'precision, scale' (e.g., "10,2").` | Same |
| Precision 0 or scale outside 0..precision | `FieldLength for field '{code}' is invalid: precision must be > 0 and scale must be between 0 and precision.` | Same |
| Precision or scale above the setting | `Input value must not exceed the maximum limit of precision: {p} and scale: {s}.` | Same |

Behaviour to know:

- The number in the message is the configured setting, so two environments can answer differently for the same request.
- An empty setting removes the ceiling (the checks are skipped). The Admin form marks the settings required and seeds a value, so an empty value only happens when it was cleared by other means. If you want a limit, make sure the value is saved.
- Existing fields are not re-validated when a setting is lowered. Only new fields and edits are checked.
- A Text Area length above 4000 is created as unlimited text. The setting itself is capped at 8000 in the form. The public limits article states Text up to 4000 and Text Area up to 8000 (KB, consistent with the form ranges).
- The Manage Fields screen falls back to 4000, 8000 and `38,38` for the default pre-fill if a default setting has no value. These are screen fallbacks, not API limits.
- Boolean and Date And Time fields take no length and no setting.
- The module has no other setting. Table key length (100), table name length (100) and the grid page sizes are fixed.
- Fair-usage guidance (KB, advice only, not enforced): keep to 10 to 15 columns, about 50,000 records for 5 to 6 columns, no joins, foreign keys or composite keys, avoid frequent imports.
- Apply: Save. The field validation reads the settings through the shared cache, so it follows section 3 of `01-how-settings-apply.md`.
- API exposure: the settings are not returned by the Custom Table API. Read them with `GET /v2/global-settings/code/CustomTableSettings` (public specification, Customer API). Exposure by that route is inferred from the operation summary, not tested.

Conflict note: an earlier internal note said the code rejects Text Area lengths above 4000 and that a blank setting means a ceiling of 4000, 8000 and `38,38`. The product source does not do that: no hard 4000 rejection exists in the validation, and blank means no check. The product wins.

## 2. Product Information Overrides

| Property | Global switch | Store switch |
|---|---|---|
| Label | Enable Product Information Overrides | Enable Product Information Overrides |
| Key | `EnableProductInfoOverrides` | `EnableProductInformationOverrides` |
| Admin path | `System Settings > Global Settings > Global Product Settings` (the KB also shows it in the Product Feed section) | `Stores and Reps > Stores > Manage > Additional Store Attributes > Product Settings` |
| Level | Global | Per store, per locale |
| Type, default | Yes/No, seeded `false`; code fallback `false` | Yes/No, no default, treated as `false` |
| Apply | Save, then publish products or catalogs so the override data is indexed | Save; the store value is cached and cleared on save |
| API | Same routes as section 5 of the how-settings-apply file | Store attribute routes of the Customer API |

Combined rule (verified in the product source): overrides are used in search only when the global switch AND the store switch are both on.

| Global | Store | "Product Overrides" button on the product page | Override index built at publish | Search returns override data |
|---|---|---|---|---|
| On | On | Visible | Yes | Yes |
| On | Off | Visible | Yes (built, unused) | No |
| Off | On | Hidden | No | No |
| Off | Off | Hidden | No | No |

What the switches do not do (verified in the product source):

- The create, update and delete routes of product overrides and the system table screens work regardless of both switches.
- The store switch does not hide the button and does not stop the index being built.
- Saving override records through the API does not mark the product as Draft and does not flag the record for a catalog level publish. Publish the product itself to pick the record up (module guide).
- First use needs a full publish (KB).
- The store help text says shoppers see override data "provided the required customizations are applied at the Storefront level". The Webstore source must read the override fields for them to appear.

## 3. Global Product Settings (and product feed)

| Label | Key | Type | Default | Effect | Apply |
|---|---|---|---|---|---|
| Product Feed Record Count | `ProductFeedRecordCount` | Whole number | Code fallback `50000`. KB says the allowed range is 1 to 10000 and recommends `10000` | Records processed per product feed run. Blank in the Google feed means do not split into files | Save |
| Fetch Published Products - Chunk Size | `PublishProductFetchChunkSize` | Whole number | `10000` | Chunk size when published products are fetched | Save |
| Allow Zero Sales Price For Custom Pricing | `RespectZeroSalesPriceForCustomPricing` | Yes/No | `false` | Accept 0 from a custom price | Save |
| Enable Product Information Overrides | `EnableProductInfoOverrides` | Yes/No | `false` | See section 2 | See section 2 |

Behaviour to know: the Google feed attribute mapping is read from a setting named `GoogleFeedAttributeMapping` (comma list, Google name first, `|` lists sources to try in order, `#SKU`, `#Name`, `#CategoryName` address the product row). No Admin field is created for it by the product setup, so it has no screen. It can only be supplied through the Global Settings API (section 5 of `01-how-settings-apply.md`), and that path was not tested. Confirm with Znode before relying on it.

## 4. Event Subscription Settings (cache events to the Webstore)

| Label | Key | Type | Default | Effect | Apply |
|---|---|---|---|---|---|
| Event Subscription URLs | `WebhookSubscriptionUrl` | Text, comma separated absolute http or https addresses | empty | Every cache event the API raises is posted to each URL. This is how the Webstore drops its caches after a save or publish | Save |

- This is not the Custom API event webhook (`Dev Center > Webhook Settings`). See `sdk-extension-settings` for that.
- The post carries `EventType: "Cache"`, an event name and a payload of key and tags. The secret header is sent only when a shared secret is set in the API configuration and the URL contains `/revalidate` or `/anon`. The Webstore compares it with its `ZNODE_REVALIDATE_TOKEN`. A mismatch gives 401 and nothing is cleared.
- With the setting empty, the Webstore is not told. Store data changes then show after the Webstore portal cache lifetime (15 minutes by default) and published page data after its own cache lifetime.
- Timeout of each post is 5 seconds by default (`WebhookRequestTimeoutInSeconds`, deployment setting). A failed post is logged and not retried.

## 5. Publish and index settings

| Setting | Admin path | Key or label | Default | Effect | Apply |
|---|---|---|---|---|---|
| Publish Settings (Production and Webstore Preview targets) | `System Settings > Global Settings > Publish Settings` | one row per target with an enable icon | Production on and cannot be disabled; Preview on in the standard seeds, off in the B2B seed | When Preview is off the publish dialog has no Preview option, no preview copy and no preview index are built | Immediate for new publishes; re-publish to build a missing preview copy |
| Display Pricing and SEO Details of Products from Index | `PIM > Catalogs > Index Settings` (per catalog) | checkbox | off | Storefront list pages read price and SEO details from the index instead of live calls | Needs a catalog publish |
| Cart validation after publish | feature registry setting `IsShoppingCartValidationRequired` | `True` or `false` | `false` in upgraded environments, `True` in the pilot seed | After each publish, cart lines of removed or deactivated products get an error | Read at publish time; no Admin screen was traced for it |
| Terminate stuck publish and other processes | `Terminate Stuck Process(es)` tab | see section 6 of `02-tabs-and-general-settings.md` | on, 60 minutes | Ends processes in progress longer than the limit | Save |
| Index settings (Ngram, Min Gram 3, Max Gram 20, Character Filter) | `PIM > Catalogs > Index Settings`, global row "All" or per catalog | KB | Min Gram 3, Max Gram 20, Ngram on Product Name and SKU | Search index tokenisation | Publish the index settings, then rebuild with Create Index or a catalog publish. Message: `A value between 1 and 99 is allowed` |
| Search settings group | `Search Settings` tab | `SearchIndexChunkSize` (fallback `500`), `ElasticSearchMaxTotalFields` (fallback `5000`), `ElasticSearchIndexReplicaCount` (fallback `0`) | as shown | Index build size and field ceiling | Save; re-index |

Behaviour to know:

- The publish dialog options "Publish Draft Products Only" (ticked by default) and Preview and Production versus Preview Only come from these settings and the catalog state.
- Messages that mention Production and Preview only appear when Preview is enabled.
- Settings that change index content never act on products already indexed until they are published or re-indexed again.

## 6. Import and Export settings

Admin path: `System Settings > Global Settings > Import/Export Settings`. Scope: global.

| Label | Key | Type | Code fallback | Effect | Apply |
|---|---|---|---|---|---|
| Import - Chunk Size | `ZnodeImportChunkLimit` | Whole number | `1000` | Rows processed per import batch | Save |
| Import Timeout (In Min) | `ZnodeImportTimeOut` | Whole number, minutes | `500` seconds when empty or 0, otherwise minutes times 60 | Time allowed for an import | Save |
| Export - Chunk Size | `ZnodeExportChunkLimit` | Whole number | `50` | Records per export batch | Save |
| Enable Exported File Purge | `EnableSchedulerForDeleteExportFiles` | Yes/No | on | Deletes old export files | Save (job re-registered) |
| Purge - Exported File (In Days) | `ExportFileDeletionDuration` | Whole number | `30` | Age at which export files are removed | Save |
| Scheduler Frequency, Trigger Time, Cron Expression - Exported File Purge | `DeleteExportSchedulerType`, `DeleteExportSchedulerTriggerTime`, `DeleteExportSchedulerCronExpression` | Text | `Recurring`, `12:00:00 AM`, `*/5 * * * *` | Schedule of the purge | Save |
| Generic Parser Import Max Buffer Size | `GenericParserImportMaxBufferSize` | Whole number | not set | Parser buffer for large files | Save |

Behaviour to know: no setting turns import or export on or off. Bulk import operations do not raise change events (see `sdk-extension-settings`).

## 7. Nelli-Dev decision guide for this file

| Need | Answer |
|---|---|
| Limit custom table field length | Supported. Set the three Custom Table Settings max values, with a real number each time. Existing fields stay. |
| Change the length pre-filled in the Add Field form | Supported: the three default settings. |
| Turn on product overrides for one store only | Supported. Global switch On, store switch On for that store only, leave the other stores Off, then publish the products. Webstore code must read the override fields. |
| Overrides saved but not shown | Check in order: global On, store On for that store and locale, product or catalog published after the record was saved, Webstore customization reads the fields, Webstore cache lifetime. |
| Webstore does not refresh after a publish | Check `WebhookSubscriptionUrl` and the matching secret. Without them expect the cache lifetimes in section 4. |
| Need a setting that does not exist | Needs a platform change for a Global Setting. Customizable alternatives: a custom table row, or an appsettings value in the Custom API SDK host. |
