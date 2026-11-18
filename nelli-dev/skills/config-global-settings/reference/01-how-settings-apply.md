# How Global Settings are stored, read and applied

What this answers: where a Global Setting lives, who reads it, how long a saved change takes to reach the API, Admin and Webstore, and which settings need more than a Save.
Read this before telling anyone to restart, publish or clear a cache.

## 1. Three kinds of "setting" (do not mix them)

| Kind | Where you change it | Who can change it | Applies after |
|---|---|---|---|
| Global Setting (an attribute on a tab of System Settings > Global Settings) | Admin Console | Admin users with Global Settings access | Save (see section 3) |
| Store setting (a flag on Manage Store, General tab or Additional Store Attributes) | Admin Console, per store | Admin users with access to the store | Save, plus the store caches (section 4); some need a store publish |
| Deployment setting (a key in an appsettings file or an environment variable of a service) | Deployment files of the service | Whoever deploys the service (for the Custom API SDK: you; for Znode services: Znode) | Restart of that service |

A customer developer normally controls the first two in the Admin Console and the third only for the Custom API SDK host and the Webstore source.

## 2. Resolving the value of a Global Setting

Verified in the product source (2026-10-15).

1. The Admin saves the tab values. The API stores them per setting key (the "attribute code", for example `EnableProductInfoOverrides`).
2. A reader asks for a key. The API returns the saved value, else the default value defined with the setting, else the code fallback written in the reader.
3. The reader code fallback is what you get when the setting has no value and no default. The tables in this skill call this the "code fallback".
4. Key matching is case-insensitive.

Two consequences:

- A setting that has never been saved is not an error. The product silently uses the default.
- Changing a default in the Admin form does not change what other callers see until the value is saved.

## 3. Apply rules (what a Save does)

Verified in the product source (2026-10-15): a successful save of a Global Setting tab

| Step | Effect |
|---|---|
| Clears the shared Global Settings cache of the API | The next read goes to storage. |
| Sends a cache-invalidation message through the message broker | Every API instance and the Admin drop their copy. This is why no restart is needed. |
| Clears a dedicated cache entry for these keys | IDOR validation, XSS validation flag, global Content Security Policy, timer-based checkout expiration, zero sales price for custom pricing, admin and store two-factor settings |
| Re-registers the scheduled job for scheduler settings | The enable switches and cron expressions of: cart purge, voucher reminder email, stock notification, exported file purge, terminate stuck process, audit log purge, previous purchases sync (and the other scheduler groups handled in the same routine) |
| Raises a "User Defined Field, Updated" event for the entity | A Custom API consumer can see that a Global Setting tab was saved. |

What this means in practice:

| Question | Answer |
|---|---|
| Does a Global Setting need an API or Admin restart? | No, in the normal case. The broker message is what updates every instance. If the broker is down or unreachable, instances keep the old value until the cache lifetime ends. |
| How long can an old value live if the message is lost? | The API cache lifetime (a deployment value, 20 minutes in the shipped configuration) and the Admin global settings cache duration (20 minutes in the shipped configuration). |
| Which Global Settings need a publish? | Settings that change what is written to the search index or the published copy: `EnableProductInfoOverrides` (override data is only indexed when a product or catalog is published), cart validation and index related settings. See `03-customization-settings.md`. |
| Which need a process recycle? | `SkipXssValidation` (shown as Enable XSS Validation): the validator keeps the value it read first in process memory, and the source says a recycle is needed to pick up a change. Treat any change to it as needing a recycle of the API (ask Znode for hosted environments). |
| Does the KB agree? | The KB "What Requires Publishing" article lists Global Settings as live immediately without publishing. That matches the save behaviour above, with the exceptions in this table. |

## 4. Reads you may see out of date

| Reader | Keeps a copy for | How a change reaches it |
|---|---|---|
| API (Global Settings cache) | Cache lifetime of the deployment (20 min shipped) | Save message (section 3) |
| Admin Console | 20 minutes (shipped) | Save message |
| Webstore store data (portal data) | 15 minutes by default (`PORTAL_CACHE_TTL_MS`) | The API posts a cache event to the Webstore only when an Event Subscription URL is configured (see `sdk-extension-settings`) |
| Search index and published copy | Until the next publish | Publish |

## 5. API exposure

| Operation | Purpose | Source |
|---|---|---|
| `GET /v2/global-settings` | List the global settings registry | Public specification (Customer API) |
| `GET /v2/global-settings/{globalSettingId}` | One entry by id | Public specification |
| `GET /v2/global-settings/name/{featureName}` | One entry by feature name | Public specification |
| `PUT /v2/global-settings/name/{featureName}` | Update one entry | Public specification |
| `POST /v2/global-settings` | Create an entry | Public specification |
| `GET /v2/global-settings/by-familycode/{familyCode}` | Setting groups of a family | Public specification |
| `GET /v2/global-settings/code/{groupCode}` | Setting attributes of a group (for example a tab) | Public specification |
| `GET /v2/global-settings/code/{groupCode}/{attributeCode}` | One setting attribute | Public specification |
| `GET /GeneralSetting/List`, `PUT /GeneralSetting/Update`, `GET/PUT /GeneralSetting/GetConfigurationSettings`, `UpdateConfigurationSettings` | Legacy v1 general settings (Multifront API) | Public specification |

Behaviour to know:

- The v2 routes read and write two stores of settings: the feature registry (`name/{featureName}`) and the tab attributes (`code/{groupCode}`). Which store a particular setting lives in is not shown on the Admin screen. Use `GET /v2/global-settings/code/{groupCode}/{attributeCode}` first, and fall back to `name/{featureName}` if it returns nothing.
- Do not use the v1 `GeneralSetting` routes for new work (legacy v1 rule in `api-catalog`).
- A write through the API goes through the same save logic as the Admin only where the Admin uses the same operation. Prefer the Admin screen for changes, and the API for reading.
- Secrets (license keys, client secrets, API keys) can be read back by anyone who can call these routes. Treat the route as privileged and never log the response.

Where the Knowledge Base differs: the KB general settings article lists eight General tab settings only and gives no defaults. The product has many more, listed in this skill. The product wins.
