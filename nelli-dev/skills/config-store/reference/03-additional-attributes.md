# Additional Attributes tab (store level feature settings)

What this answers: every group on `Manage Store > Additional Attributes`, its settings, defaults, apply rule, and the store level switches that customizations depend on (product information overrides, maintenance, two factor, content security policy, address validation).
Sources: KB article "Configuring Additional Store Attributes" (read in full, 80), product source and seed values (90, 2026-10-15).

The groups are data driven. They are the attribute groups defined for the entity "Store". A deployment can show fewer or more groups. If a setting below is absent from your screen, say it was not found rather than assuming a version.

## 1. Settings by group

| Group | Setting (label) | Type, default | Effect | Apply |
|---|---|---|---|---|
| Cloudflare Settings | Enable Cloudflare; Cloudflare Zone ID | Yes/No; text from Cloudflare | Edge caching for the store domain. Publishing the store, CMS content or store settings clears the Cloudflare cache; Global Settings can also clear it manually (KB) | Save |
| Webstore Authorization | Login To See Pricing and Inventory; Login Required | Enabled or Disabled | Hide price and stock from guests (B2B theme only); require login for every page | Publish Store Settings (KB) |
| Redirections | SEO URL redirect details | entries | Redirect to a page | not stated |
| Enable Budget Management | approval requirement; per order limit; annual limit; annual limit start month | toggles | Budget rules for customers with limits | not stated |
| Two Factor Authentication Settings | `Enable2FAForStore` and four value settings (code timeout, session timeout, failed attempts, lockout) | `false` | Overrides the global admin 2FA for shoppers of this store | Save (dedicated cache cleared) |
| Security | Content Security Policy (key `ContentSecurityPolicy`) | text, no default | Added to the global policy; needs a directive such as `default-src`, `script-src` or `connect-src` before a URL; combined policy at most 7,000 characters | Save |
| ReCaptcha | Invisible ReCaptcha for Login and Registration; for Forms; at Checkout for Guest Users; at Checkout for Logged-in Users | No (each) | Shows the challenge on those pages | not stated |
| Warehouse Settings | Display Stock Levels From Default And All Warehouses | Enabled or Disabled | Default warehouse plus all warehouse total on list and detail pages. Needs a warehouse with quantity and out of stock purchasing off | Publish the store; catalog publish not required (KB) |
| Address Settings | Shipping address suggestion at checkout | Enabled or Disabled | Suggestions when the shopper changes address | not stated |
| Quote Settings | Quote Expire In (Days); Enable Quote Requests From Web Store | number; Yes/No | Quote validity and request ability | not stated |
| Return Setting | Enable Return Requests From Web Store | Yes/No | Shoppers can create returns | not stated |
| TradeCentric | TradeCentric access | No | Store reachable through TradeCentric PunchOut | not stated |
| Voucher Settings | Voucher Expiration Reminder Email (In Days) | number | Days before expiry for the reminder | not stated |
| Shipping Setting | Show Estimate Shipping Cost Section; Show Shipping Constraints Section | Disabled; Yes | Cart estimate; constraints on checkout pages | not stated |
| Billing Setting | Billing Address visibility on checkout | Yes | Show billing address | not stated |
| Product Settings | Enable Product Information Overrides (key `EnableProductInformationOverrides`) | Yes/No, no default (off), per locale | Store switch of product overrides, see section 2 | Save |
| Product Settings | Label | text | Message shown under the SKU on the Webstore | not stated |
| Maintenance Mode | Webstore Under Maintenance (key `WebstoreUnderMaintenance`) | `false` | Store goes offline; shoppers see the Maintenance page and status 503 | Save; effective at once (KB), store data cache up to 15 minutes |
| Address Validation Settings | Enable Address Validation; Validate Addresses in Address Book Page; Allow User to Override Address; Configuration Set | Yes/No each; dropdown | Validation through the chosen shipping configuration set flagged for address validation. One set per store. USPS is the only supported provider. The two child switches matter only when the first is Yes | Save; a store cache event is sent for these three keys |
| Previous Purchases | Enable Previous Purchases on Webstore (`EnablePreviousPurchasesWebstore`) | store flag; copied by Copy Store | Show previous purchases | Save |
| Account inheritance | `EnableMultiAccountSupport` | Yes/No | Multi account support | Save |

## 2. Product Information Overrides at store level

| Item | Detail |
|---|---|
| Label and key | `Enable Product Information Overrides`, key `EnableProductInformationOverrides` |
| Location | `Stores > Stores > Manage > Additional Attributes > Product Settings` |
| Level | Per store and per locale; not required |
| Default | No saved value, treated as off |
| Read by | Search routes of the API, through a per store cache that is cleared when this attribute is saved |
| Needs | The Global Settings switch `EnableProductInfoOverrides` must also be on (see `config-global-settings`) |
| Does not control | The Product Overrides button on the product page (global switch only), the override index build at publish (global switch only), the override create, update and delete routes |
| Customization note | The help text says shoppers see override data "provided the required customizations are applied at the Storefront level". The stock Webstore does not read override fields for display unless customized |

## 3. Behaviour to know

- Where the KB states "requires publishing Store Settings" (Webstore Authorization, Warehouse), publish the store from `Stores > Stores > Publish`. For other groups the KB says nothing; use the table in `04-what-requires-publishing.md`.
- The Maintenance flag is saved on this tab, not on General. Global `Enable Maintenance for All Stores` wins.
- Copy Store copies only `EnablePreviousPurchasesWebstore` among the attribute values. Maintenance, overrides, 2FA, CSP and address validation start empty on a copy.
- Attribute values saved here raise a "User Defined Field, Updated" event for the store that a Custom API consumer can receive (verified in the product source).

## 4. Nelli-Dev decision guide for this file

| Request | Answer |
|---|---|
| Turn product overrides on for one store | Supported: store switch On on that store, global switch On, publish the products, and the Webstore must read the fields (source customization) |
| Add a store level flag for my customization | Customizable: a Custom API SDK setting, or a custom table keyed by store code. A new Additional Attributes setting is a platform change |
| Allow a payment or analytics script on one store | Supported: store Content Security Policy, within 7,000 characters with the global one |
| Take one store offline | Supported: Webstore Under Maintenance; confirm the global switch is No |
