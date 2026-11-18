---
name: config-global-settings
description: The Znode Global Settings reference (Admin Console System Settings > Global Settings, one tab per setting group) - every tab, the settings that govern customization and data extension (custom table field length limits, Enable Product Information Overrides, promotions and coupons, event subscription URLs, publish, index, import and export, XSS, IDOR and content security policy, scheduler jobs), the key, type, default and scope of each, whether a Save is enough or a publish, cache clear or restart is needed, and how to read them through the API. Load it when a question is "which setting controls X", "what does it default to", "does changing it need a publish or restart", or before recommending any change to a Global Setting. Do not use it for store level settings (config-store) or for the full feature to setting index (sdk-extension-settings).
user-invocable: false
---

# Znode Global Settings

Global Settings are platform-wide values edited at `System Settings > Global Settings`. Each tab is a group of settings. One value applies to every store. A few settings have a store level override (listed below). This skill never invents a setting: if a name is not in the reference files, say it was not found.

## Use it / do not use it

| Use this skill when | Use another skill when |
|---|---|
| A developer asks which Global Setting controls a behaviour, its default, range or apply rule | The setting is on a store (`config-store`) |
| A customization depends on a switch (overrides, events, custom table limits) | You need one table that lists the switch for each customization feature (`sdk-extension-settings`) |
| A change "did not take effect" | The problem is a cache or publish problem in the Webstore (`sdk-extension-settings`, section on caching) |

## The 10 facts that matter most

1. A Save on a Global Setting tab updates every API instance and the Admin through a cache message. No restart is the normal case (verified in the product source).
2. If the message broker is unreachable, instances keep the old value until the cache lifetime ends (20 minutes in the shipped configuration).
3. Settings that change the search index or published data (`EnableProductInfoOverrides`, index and attribute lists) need a product or catalog publish, or a re-index, before shoppers see anything.
4. `EnableProductInfoOverrides` (Global Product Settings, default `false`) and the store switch of the same name must both be on for search to use override data. The create, update and delete override routes ignore both.
5. The three custom table max settings are `CustomTableMaxFieldLengthForText` (seeded 100, form range 1 to 4000), `CustomTableMaxFieldLengthForTextArea` (seeded 100, 1 to 8000) and `CustomTableMaxFieldLengthForNumber` (seeded `10,2`). Blank means no check; a saved value is a ceiling. Existing fields are not re-checked.
6. Three more settings pre-fill the Add Field form: `CustomTableDefaultFieldLengthForText` (50), `...ForTextArea` (100), `...ForNumber` (`10,0`).
7. `WebhookSubscriptionUrl` (Event Subscription URLs) is what tells the Webstore to drop its caches. It is not the Custom API event webhook (`Dev Center > Webhook Settings`).
8. `SkipXssValidation` is shown as "Enable XSS Validation" and a stored `true` means validation is ON (product source). The KB says the opposite. Test before relying on it, and expect a recycle to be needed for a change.
9. Scheduler groups (cart purge, audit purge, quote expiration, voucher reminder, stock notice, stuck process, export purge) re-register their job on Save. Frequency accepts `Recurring` only.
10. The Global Settings API can read every setting (including secrets). Treat the routes as privileged.

## Where each topic lives

| Topic | File |
|---|---|
| Where a value is stored, caches, restart or publish rules, API routes | `reference/01-how-settings-apply.md` |
| Tabs, General, technical group, sessions, 2FA, CSP, XSS, IDOR, maintenance, SEO validation, checkout session, scheduler groups, integrations | `reference/02-tabs-and-general-settings.md` |
| Custom Table Settings, Product Information Overrides, product feed, event subscription, publish and index, import and export | `reference/03-customization-settings.md` |

## Settings that also exist at store level

| Global setting | Store level override or counterpart | Winner |
|---|---|---|
| Enable Maintenance for All Stores | Webstore Under Maintenance (Additional Store Attributes) | The global flag when it is Yes |
| Enable Two-Factor Authentication (Admin Console) | Store 2FA settings for shoppers (separate group) | They govern different users |
| Global content security policy | Store Content Security Policy | Combined (appended), limit 7,000 characters together |
| Enable Product Information Overrides | Store switch of the same name | Both must be on |
| Enable Previous Purchases Sync | Enable Previous Purchases on Webstore (store) | Both apply to different parts |

## Nelli-Dev decision guide

| Request | Verdict and steps |
|---|---|
| Turn on product overrides for one store only | Supported. Global switch On (Global Product Settings), store switch On for that store only, publish the products, make sure the Webstore customization reads the override fields. |
| Limit custom table field length | Supported. Save the three Custom Table max settings with explicit numbers. Say that existing fields stay as they are. |
| Why does my new setting not show on the storefront | Walk the chain: saved at the right level, publish done if it is an index setting, `WebhookSubscriptionUrl` and secret configured, Webstore portal cache (15 minutes) and page cache lifetimes, Webstore code actually reads the value. |
| Does this need a restart | Global Setting: no, except the XSS flag (recycle). Deployment setting (appsettings, environment variable): yes, restart of that service. Never recommend a restart for a Global Setting without first checking the broker. |
| Add a new Global Setting for my customization | Needs a platform change. Customizable alternatives: a custom table, a Custom API SDK appsettings value, a store attribute. |
| Change CSP, XSS, IDOR, 2FA or session values | Supported by configuration in the Admin Console. Not by code. Flag the security impact in the security report. |
| Read a setting from code | Supported: `GET /v2/global-settings/code/{groupCode}/{attributeCode}` from the SDK through the gateway. Never log the response for secret groups. |

## Verified against

Product source and seed values (2026-10-15), module guides for Custom Tables, PIM Publish and Stores, and the KB articles under Managing Global Settings (https://support.znode.com/support/solutions/folders/43000598150). KB versus product conflicts are listed in the files above; the product wins.

## Related

`config-store` · `sdk-extension-settings` · `sdk-custom-tables` · `commerce-catalog` · `sdk-events-and-webhooks` · `api-catalog`
