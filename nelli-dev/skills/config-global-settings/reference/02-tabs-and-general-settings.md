# Global Settings tabs: general, session, security, scheduler groups

What this answers: which tab holds which Global Setting (label, key, type, default, effect, apply rule), for everything outside customization and data extension.
Customization and data-extension settings are in `03-customization-settings.md`.

Admin path for all of them: `System Settings > Global Settings`, then the tab. Scope: global only (one value for the whole platform) unless the row says a store override exists.
Defaults: "code fallback" means the value the product uses when the setting has no saved value and no default (verified in the product source, 2026-10-15). A KB default is marked (KB).
Apply: "Save" means a Save is enough (section 3 of `01-how-settings-apply.md`). Secrets are listed by name only.

## 1. Tab list

| Tab (setting group) | What it holds | Section below |
|---|---|---|
| General | Storage unit, date and time format, display and server time zone, price and inventory round off, current environment | 2 |
| General Settings (technical group) | Swagger, debug mode, import buffer, task timeouts, password and session values, Google keys, support email | 3 |
| URL Management | Admin Console and API domain URLs | 2 |
| Locales, Currencies, Countries | System reference data enabled for stores | 2 |
| Promotions and Coupon Settings | Promotion and coupon combination rules | 4 |
| Maintenance | Take all stores offline | 4 |
| Two Factor Authentication Settings | Admin sign-in 2FA and the mail server used to send codes | 5 |
| User Login and Session Settings | Authentication cookie and login token life | 5 |
| API and Security Settings | Content security policy, IDOR validation, XSS validation | 5 |
| SEO Validation Settings | Switch off SEO URL validation | 4 |
| Checkout Session Settings | Checkout timer | 4 |
| Google Map Settings | Google Map key and map id | 3 |
| Scheduler groups: Quote Expiration, Cart Data Purge, Abandoned Cart Data Purge, Audit Log Purge, Terminate Stuck Process, Global Voucher Settings, Previous Purchases Settings, Inventory Stock Notification | Enable switch, trigger time, frequency and cron per job | 6 |
| Import/Export Settings, Global Product Settings, Custom Table Settings, Event Subscription Settings, Search Settings | See `03-customization-settings.md` | - |
| AI Content Generation Settings, PDF Settings, Visual Editor Settings, User Activity Logging, Artifi (customizable product) settings | Integrations and logging | 7 |

Not every tab is visible in every deployment; a group appears when its settings exist in the database. If a setting named here is not on your screen, report it.

## 2. General tab, URL Management, reference data

| Setting (label) | Type and values | Default | Effect | Apply |
|---|---|---|---|---|
| Storage Unit | KB or MB | not stated (KB article) | Unit used to show media file sizes | Save |
| Date Format, Time Format | Format strings | not stated | How the Admin and Webstore show dates and times | Save |
| Display Time Zone | Time zone list | not stated | Time zone used to display Admin and Webstore data | Save |
| Server Time Zone | Time zone list | not stated | Time zone in which the platform stores dates (it is stored as `SavedTimeZone`; UTC when missing) | Save |
| Price Round Off | Whole number of decimals | per environment | Decimals kept for prices and order amounts | Save (the store screens read it for the order amount decimals; module guide) |
| Inventory Round Off | Whole number of decimals | per environment | Decimals for quantity on hand, re-order level and unit of measure | Save |
| Current Environment | Environment name | none | Label shown in the Admin and Webstore header on every environment except Production | Save |
| Default Currency, Default Culture, Default Weight Unit, Default Country | Chosen from enabled reference data | per environment | Copied into a newly created store. Existing stores keep their own values. Default Dimension Unit is always `CM` on a new store | Save; read when a store is created |

Behaviour to know:

- Display Time Zone and Server Time Zone are different settings. A mismatch is the usual reason for "the date is off by some hours".
- Changing a default currency or culture does not change existing stores.

## 3. General Settings (technical group) and Google Map

| Label | Key | Type | Code fallback | Effect | Apply |
|---|---|---|---|---|---|
| Enable Swagger | `EnableSwagger` | Yes/No | `true` | Exposes the Swagger page of the API | Save |
| Is Debug Mode | `IsDebugMode` | Yes/No | not read by the shared reader | Debug behaviour of the Admin | Save |
| Generic Parser Import Max Buffer Size | `GenericParserImportMaxBufferSize` | Number | not set | Buffer size of the import file parser | Save |
| Task Scheduler Request Timeout (In millisecond) | `TaskSchedulerRequestTimeout` | Number | `600000` | Timeout of scheduler HTTP calls | Save |
| Support Email | `ZnodeSupportEmail` | Text | empty | Support contact address | Save |
| Order OverDue Amount Round Off Length | `OrderOverDueAmountRoundOffLength` | Number | `7` | Decimal length for the overdue amount | Save |
| Grid Paging Start Value | `GridPagingStartValue` | Number | `10` | Default page size of Admin grids; the Admin keeps the chosen size in the session | Save; the Admin reads it once per process, so a new value can need an Admin restart (module guide, not re-tested) |
| Notification Messages IsFadeOut | `NotificationMessagesIsFadeOut` | Yes/No | not set | Whether Admin messages fade out | Save |
| Session Warning Time | `SessionWarningTime` | Number | not set | When the Admin warns about session end | Save |
| Generate Images | `GenerateRuntimeImages` | Yes/No | `true` | Generate image sizes at run time | Save |
| Max File Size, Max Size For Video | `MaxFileSize`, `MaxSizeForVideo` | Number | not set | Upload limits for the media manager | Save |
| Maximum Invalid Password Attempts | `MaxInvalidPasswordAttempts` | Number | `5` | Failed sign-ins before an account locks | Save |
| Reset Password Link Expiration (In Days) | `ResetPasswordLinkExpirationDuration` | Number | `24` (the product reads the value as given; the label says days, the fallback is 24) | How long a reset link is valid | Save |
| Additional Attributes | `AdditionalAttributes` | Text, comma list | `ColorSwatch, Color, UPC, Size, SizeChart, ColorFamily, ImageName, ColorSwatchReg, BackImageBlank, SubstrateID, IsPrimary` | Attribute codes included with published products | Save; republish products to refresh published copies |
| Allow Add On Quantity | `IsAllowAddOnQuantity` | Yes/No | `false` | Lets shoppers set quantity on add-ons | Save |
| Publish Catalog Connection Time | `PublishCatalogConnectionTime` | Number (minutes) | `30` (1800 s) | Time limit of a catalog publish | Save |
| Publish Portal Connection Time | `PublishPortalConnectionTime` | Number (minutes) | `5` (300 s) | Time limit of a store publish | Save |
| Purge Publish Portal Connection Time | `PurgePublishCatalogConnectionTime` | Number (minutes) | `30` (1800 s) | Time limit of the purge of published data | Save |
| Default Token Filters | `DefaultTokenFilters` | Text | `lowercase` | Search analyzer token filters | Save; re-index |
| Stem Exclusion Words | `StemExclusionWords` | Text | empty | Words excluded from stemming | Save; re-index |
| Enable Synonym Support in Search | `UseSynonyms` | Yes/No | `true` | Search synonyms | Save; re-index |
| Enable StopWords For Search Index | `EnableStopWordsForSearchIndex` | Yes/No | `true` | Stop words in the index | Save; re-index |
| Recommendation Model - Chunk Size / Time Limit (In Min) | `RecommendationModelChunkSize`, `RecommendationModelTimeLimit` | Number | `500`, `30` min | Recommendation model build | Save |
| Znode Report Folder Name, Report Server Dynamic Report FolderName | not named in the reader | Text | none | Reporting folders | Save |
| Azure Client Id, Azure Client Secret Id, Azure Tenanat Id, Subscription Id, Resource Groups, AzureProfile, AzureEndPoint | `AzureClientId`, `AzureClientSecret`, `AzureTenantId`, `AzureSubscriptionId`, `AzureResourceGroup`, `AzureProfile`, `AzureEndPoint` | Text | empty for ids; the other three have a built-in fallback | Platform cloud integration. Not for customization work; do not change | Save |
| Znode Gocoder Google API, Znode Google API Domain Key | not named in the reader | Text | none | Google geocoding keys | Save |
| Google Map Key, Google Map Id | `ZnodeGoogleMapKey`, `ZnodeGoogleMapId` | Text | empty | Store locator and map widgets | Save |
| Visual Editor Application URL | `VisualEditorAppURL` | Text | none | Address of the page builder opened from the Admin | Save |

Behaviour to know:

- The label "Reset Password Link Expiration (In Days)" and the code comment disagree on the unit of the fallback. Test before relying on it.
- `PublishCatalogConnectionTime` is entered in minutes and used as seconds after multiplying by 60. A value of `0` or empty gives the fallback.
- Settings that feed the search index only change what shoppers see after the catalog index is rebuilt (publish catalog or Create Index).

## 4. Promotions, maintenance, SEO validation, checkout session

| Setting (label) | Key | Type, range | Default | Effect | Apply |
|---|---|---|---|---|---|
| Allow Promotion And Coupons Together | `IsAllowWithOtherPromotionsAndCoupons` | Yes/No | Yes (KB) | Yes: promotions and coupons can apply to one order. No: only one type applies | Save (live, no publish: KB) |
| Promotions With Exceptions | `AllowedPromotions` | Comma list of promotion classes | empty | Classes that may combine with coupons even when the switch above is No | Save |
| Calculate Tax On The Discounted Price | `IsCalculateTaxAfterDiscount` | Yes/No | not stated | Tax is computed on the discounted amount | Save |
| Enable Maintenance for All Stores | `EnableMaintenanceForAllStores` | Yes/No | `false` | Every store goes offline, whatever its own flag. Shoppers see the Maintenance page and receive status 503 (KB) | Save; takes effect "immediately" (KB); the Webstore keeps store data for up to 15 minutes unless the event subscription is configured |
| Disable SEO Validations | `DisableSeoValidations` | Yes/No | `false` (validation on) | No: SEO URLs are validated (up to 1000 characters; letters, digits, hyphen, underscore, slash, period; no leading or trailing slash; no reserved words). Yes: any value is accepted | Save; applies when a URL is created or edited, existing URLs are not re-checked |
| Enable Timer-Based Checkout Expiration | `TimerBasedCheckoutExpiration` | Yes/No | `false` | Turns on checkout session expiry | Save (dedicated cache cleared) |
| Checkout Session Timeout Duration (minutes) | `CheckoutSessionTimeoutDuration` | Number, 5 to 300 (KB) | 10 (KB) | Length of a checkout session. Expiry blocks payment and order placement and sends the shopper to the cart | Applies to new checkout sessions only (KB) |
| Checkout Session Expiry Warning Threshold (seconds) | `CheckoutSessionExpiryWarningThreshold` | Number | not set | When the countdown warning shows | Save |
| Hide Checkout Countdown | `HideCheckoutTimer` | Yes/No | `false` | Hides the timer in the Webstore | Save |
| Auto redirect to cart on checkout expiry | `AutoRedirectToCartOnCheckoutExpiry` | Yes/No | not set | Redirect behaviour at expiry | Save |
| Allow Zero Sales Price For Custom Pricing | `RespectZeroSalesPriceForCustomPricing` | Yes/No | `false` | Accept a price of 0 from an ERP or custom price source | Save (dedicated cache cleared) |

Behaviour to know:

- The Checkout Session tab is marked Beta in the KB.
- Promotion and coupon settings apply to the whole platform. There is no store-level override.

## 5. Sign-in, session and security

| Setting (label) | Key | Type, range | Default | Effect | Apply |
|---|---|---|---|---|---|
| Authentication Cookie Timeout | `AuthenticationCookieExpireTimeSpan` | Number | not set | Admin cookie life | Save; affects new sign-ins |
| Sliding Session Timeout | `AuthenticationSlidingExpiration` | Yes/No | not set | Extends the cookie on activity | Save |
| Login Token Expiration Duration | `LoginTokenExpirationDuration` | Number | `24` | Life of a login token | Save |
| Enable Two-Factor Authentication (Admin Console) | `Enable2FAForAdminConsole` | Yes/No | `false` | A 6 digit code is mailed after the password check | Save (dedicated cache cleared) |
| Two Factor Authentication Code Timeout | `Codetimeout2FA` | Number | KB: 10 minutes, range 1 to 360. The product label says seconds | Life of a code | Save |
| Two Factor Authentication Session Timeout | `SessionTimeout2FA` | Number | KB: trusted device 2 days, range 1 to 365 | Trusted device period | Save |
| Limit on Consecutive Failed Attempts (2FA) | `FailureLoginAttempts2FA` | Number | KB: 3 | Attempts before lockout | Save |
| Temporary Lockout Period (2FA) | `TemporaryLockoutPeriod2FA` | Number | KB: 30 minutes | Lockout length | Save |
| SMTP Server, SMTP Port, SMTP Server User Name, SMTP Server Password, From Display Name, From Email Address, Enable SSL for SMTP | `SMTPServer`, `SMTPPort`, `SMTPServerUserName`, `SMTPServerPassword`, `SMTPFromDisplayName`, `SMTPFromEmailAddress`, `SMTPEnableSSLforSMTP` | Text, Number, Yes/No | empty, SSL `false` | Mail server used only to send 2FA codes to Admin users. Store mail uses the store SMTP tab | Save |
| Store-level 2FA (Enable Two-Factor Authentication, code timeout, session timeout, failed attempts, lockout) | `Enable2FAForStore`, `CodeTimeoutStore2FA`, `SessionTimeoutStore2FA`, `FailureLoginAttemptsStore2FA`, `TemporaryLockoutPeriodStore2FA` | as above | `false` | Store override for shopper sign-in. Set on Manage Store, Additional Store Attributes | Save |
| Content Security Policy (storefront), key `GlobalContentSecurityPolicy` | Text area, directives, up to 7,000 characters with the store policy | none | Appended to the system policy. Needs a directive such as `default-src`, `script-src` or `connect-src` before a URL. Message: `CSP must include a directive like default-src, script-src, or connect-src before the URL.` | Save; "immediately" (KB) |
| Content Security Policy (Admin), key `AdminContentSecurityPolicy` | Text area | none | CSP of the Admin Console | Save; "immediately" (KB) |
| Enable IDOR Validation | `EnableIdorValidation` | Yes/No | `false` | Ownership checks on supported APIs (today the Cart APIs). Unauthorized access gives 403. A request without the `Z-Request-Context` header falls back to the existing authorization. Guests are not affected. Needs a Webstore version that sends the header | Save (dedicated cache cleared) |
| Enable XSS Validation | `SkipXssValidation` (the key name is the inverse of the label) | Yes/No | `true` in the seed | The stored value `true` means XSS validation is on (source). The KB says Yes bypasses validation. The product source wins, but test it on your environment | Needs an API recycle to be sure (section 3 of `01-how-settings-apply.md`) |
| Enable Audit Log | `EnableAuditLog` | Yes/No | Yes | Record user actions and system changes | Save |

Behaviour to know:

- The Content Security Policy message is exact and appears when the directive is missing.
- Per-store policy text on Manage Store, Additional Store Attributes, Security is combined with the global one. The combined text must stay within 7,000 characters or storefront features can break (KB).

## 6. Scheduler groups

All scheduler groups follow the same shape: an enable switch, a trigger time, a frequency (only `Recurring` is accepted by the product) and a cron expression. Saving re-registers the job without a restart. If both a trigger time and a cron expression exist, the KB does not say which wins; use the cron expression and leave the trigger time at its default.

| Group | Enable key | Other keys | Code fallbacks |
|---|---|---|---|
| Quote Expiration Settings | `EnableQuoteExpirationScheduler` | `SchedulerFrequencyQuoteExpiration`, `CronExpressionQuoteExpiration` | on, `Recurring`, `0 0 * * *` |
| Cart Data Purge Settings | `EnableSchedulerForCartPurge` | `PurgeCartOlderThan`, `CartPurgeTriggerTime`, `CartPurgeSchedulerType`, `CartPurgeCronExpression` | on, 30 days (1 to 999), `12:00:00 AM`, `Recurring`, `0 3 * * *` |
| Abandoned Cart Data Purge (guest carts) | `EnableSchedulerForGuestCartPurge` | `PurgeGuestCartOlderThan` and trigger, type, cron keys | seed default 30 days |
| Audit Log Purge Settings | `EnableAuditLogPurge` | `AuditLogRetentionMonths` (1 to 60 per KB), `AuditLogPurgeTriggerTime`, `AuditLogPurgeSchedulerType`, `AuditLogPurgeCronExpression` | on, 12 months, `12:00:00 AM`, `Recurring`, `0 3 * * *` |
| Terminate Stuck Process | `EnableTerminateStuckProcess` | `TerminateStuckProcess` (minutes), `TerminateProcessSchedulerType`, `TerminateProcessCronExpression` | on, 60 minutes (0 gives 60), `Recurring`, `0 * * * *` |
| Global Voucher Settings | `EnableSchedulerForVoucherReminderEmail` | `SchedulerFrequencyForVoucherReminderEmail`, `VoucherEmailSchedulerTriggerTime`, `VoucherEmailSchedulerCronExpression` | on, `Recurring`, `12:00:00 AM`, `*/30 * * * *` |
| Previous Purchases Settings | `EnablePreviousPurchasesSync` | `PreviousPurchasesSyncSchedulerType`, `PreviousPurchasesSyncCronExpression`; store flag `EnablePreviousPurchasesWebstore` | on, `Recurring`, `0 0 * * *` |
| Inventory Stock Notification Settings | `EnableStockNotice` | `StockNoticeSchedulerType`, `StockNoticeCronExpression`, `DeleteAlreadySentEmails`, `DeletePendingEmails` | on, `Recurring`, `* * * * *` |
| User registration attempt scheduler | `EnableSchedulerForUserRegistrationAttempt` | type, trigger time, cron | on, `Recurring`, `0 0 * * *` |
| Payment token deletion scheduler | `EnableSchedulerForDeletePaymentAuthToken` | type, trigger time, cron | on, `Recurring`, `0 */1 * * *` |
| Cart checkout cleanup | `EnableCartCheckoutExpireProcess` | `CartCheckoutCleanupProcessSchedulerType`, `CartCheckoutCleanupProcessCronExpression` | on, `Recurring`, `0 3 * * *` |

Behaviour to know:

- The scheduler service must be running for a job to fire (KB).
- Cron expressions use five fields. The product runs cron in the server local time zone for jobs it creates itself; the One Time start check uses the Display Time Zone.
- Turning off a purge switch stops deletion whatever the other values say (KB).

## 7. Integrations and logging

| Setting | Key | Default | Effect | Apply |
|---|---|---|---|---|
| Enable AI Content Generation | `EnableAIContentGeneration` | off | Shows AI text generation in the Admin | Save |
| Generative AI API Key, Endpoint, Model | `GenerativeAIAPIKey`, `GenerativeAIAPIEndpoint`, `GenerativeAIModel` | key empty; model fallback `gemini-1.5-flash`; endpoint fallback is the public generative language models address | Provider call settings. The key is a secret | Save |
| PDF Generation License Key, License ID | `PDFLicenseKey`, `PDFLicenseId` | key empty; id fallback `DEMO` | PDF library licence. The key is a secret | Save |
| Enable UserActivity for all store | `EnableUserActivityLogging` | `false` | Shopper activity logging | Save |
| Customizable Product Base URL, Batch Endpoint, Image Path | `CustomizableProductBaseURL`, `CustomizableProductBatchEndpoint`, `CustomizableProductImageURL` | empty | Customizable product (Artifi) integration | Save |
| Enable CC API Calls | `EnableCCAPICalls` | `false` | Allows calls to the Commerce Connector API from the Admin | Save |

## 8. Nelli-Dev decision guide for this file

| Need | Verdict |
|---|---|
| Change the session, 2FA, CSP, XSS, IDOR or maintenance behaviour | Supported by configuration. Ask the customer to change it in the Admin Console, never by code. |
| Allow an extra script source on the storefront | Supported: store Security CSP or the global CSP. Check the 7,000 character limit. |
| Change when a purge job runs | Supported: enable switch and cron expression on the group's tab. |
| A setting needed by a customization does not exist | Needs a platform change if it must be a Global Setting. Alternative that is Customizable: a custom table or an SDK appsettings value. |
