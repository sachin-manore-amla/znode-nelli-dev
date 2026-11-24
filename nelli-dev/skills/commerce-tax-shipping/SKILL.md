---
name: commerce-tax-shipping
description: Znode tax and shipping configuration and customization - tax classes, tax rules (Sales, VAT, GST, PST, HST, precedence, destination), tax plugins (AvaTax configuration sets, import duties, custom tax plugin), shipping methods, shipping types (FedEx, UPS, USPS, Custom), the four custom rate rule formulas, handling charge, store and profile association, carrier account setup, USPS address validation, the custom shipping plugin response contract, and troubleshooting methods that do not appear. Load it for any tax calculation, tax exemption, shipping rate, free shipping, carrier, pickup, delivery-zone or missing-shipping-method requirement, and to choose between configuration, a plugin and a method override.
user-invocable: false
---

# Tax and shipping

Sources: Znode Knowledge Base articles Managing Taxes, Adding a Tax Rule, Associate Products to Tax Class, Managing Tax Processing Plugins, Configure the AvaTax Tax Plugin, Managing Shipping Methods, Associating Shipping Rules with a Shipping Method, Troubleshooting Shipping Methods, Managing Shipping Processing Plugins, Configuring a FedEx Account for Znode Access, Configuring a UPS Account for Znode Access, USPS Address Validation in Znode, Integrating Custom Shipping Plugins, Managing Returns, Configuring Promotion And Coupon Settings (read 2026-11-23). The plugin code contract is in `sdk-provider-plugins`. No exported API spec for tax or shipping was available. Confidence 85 for Admin behaviour; "not documented" is stated where the KB is silent.

## How the pieces fit
Checkout asks a **tax processor** and a **shipping processor**. Each is a **plugin** installed under System Settings > Plugins, configured through **configuration sets** (global values plus per-store sets), and associated with stores. Native options need no code: the built-in **Sales Tax** rule engine, and **Custom** shipping methods with rate rules. External providers (AvaTax, FedEx, UPS, USPS address validation, or your own plugin) use the plugin route.

## Fourteen facts that matter
1. Tax: **System Settings > Taxes** holds **tax classes**; each class has rules (**Manage Taxes** tab) and associated products (**Associated Products** tab). (KB 85)
2. A rule has Tax Type, **Include Shipping in taxes**, **Precedence** (processing order), Destination Country, Destination State, optional Zip Code, and value fields for Sales, VAT, GST, PST, HST. Only "Sales tax" is offered by default in the type list. Uniqueness and tie behaviour of Precedence are not documented. (KB 80)
3. Taxes on a placed order recalculate in real time from the tax settings saved on the order when discounts, vouchers, shipping type, zip or shipping amount change. (KB 85: Managing Returns)
4. **Calculate Tax On The Discounted Price** (Global Settings > Promotions and Coupon Settings) taxes the post-discount amount. (KB 85)
5. External tax plugins: System Settings > Plugins > Available Plugins (filter Plugin Type = Tax): **Avatax** and **Custom Developed Tax Plugin**. Activate on the Plugin Information tab; configure under Installed Plugins. (KB 85)
6. AvaTax **Global Configuration**: Avalara App Name, Exemption Number, "Allow Submissions Of The Tax Requests?". **Configuration Set**: Configuration Code, Name, AvaTax URL (sandbox or live), Company Code, Account Number, Avalara License, Freight Identifier, Prices Are Inclusive of Taxes. Import duties are calculated from the product HS Code and destination (Canada documented); default duty rates live only in Avalara. (KB 85)
7. Shipping methods: **System Settings > Shipping**; a method must be **associated with the store** (Stores > Manage Store > Shipping Methods) to appear at checkout. (KB 85)
8. Shipping types: **FedEx**, **UPS** (carrier rates, optional handling charge), **Custom** (rates from Associated Rules), **USPS** (weight limit 70 lb). (KB 85)
9. Checkout shows methods common to the user's profile(s) and the store; if no overlap, store methods; if the profile has methods but the store has none, **no methods**. (KB 85)
10. Rate = handling charge + associated rule cost + additional shipping cost per item (the last only through the API). Handling charge is flat, percent of subtotal, or percent of shipping rate, and is not taxed. (KB 85)
11. Custom rule outside its limits does **not apply**: cost 0. One rule of each type per method. (KB 85)
12. Znode **filters out $0 shipping rates** today; free shipping through a plugin rate of 0 does not work. (KB 85: Integrating Custom Shipping Plugins)
13. FedEx and UPS test/production is switched by a Webstore-side setting (`IsFedExRestGatewayTestMode`, `IsUPSRestGatewayTest`) plus store credentials: environment configuration, owned by whoever hosts the application. (KB 85)
14. USPS address validation is off by default, U.S. addresses only, one configuration set per store, and checkout continues if USPS is unavailable. (KB 85)

## Nelli-Dev decision guide
| Requirement | Verdict | Route |
|---|---|---|
| Sales tax by country, state, zip | Supported | Tax class and rules; precedence for overlaps |
| Tax-exempt customers | Supported | Profile or order Tax Exemption (Managing Returns lists it as a locked order field); AvaTax Exemption Number for provider |
| Tax by AvaTax | Supported | Configure AvaTax; per-store configuration sets |
| Another tax provider (for example Vertex or your own) | Customizable | Tax plugin built from the SDK template (`sdk-provider-plugins`); the KB lists only AvaTax and a custom plugin as native |
| Change tax customer code sent to the provider | Customizable | Method override hook for the tax step (`sdk-method-overrides`) |
| Flat shipping by weight bracket | Supported | Custom method, Weight-Based Rate rule |
| Free shipping above a threshold | Supported | Percent Off Shipping promotion 100% with a minimum order amount (`commerce-promotions-and-pricing`); not a $0 plugin rate |
| Shipping only to some states | Supported | Method Destination Country, State, Postal Code |
| Different methods for B2B profiles | Supported | Assign methods to the user profile (Accounts & Users > User Profiles) |
| Pickup or local delivery with fixed price | Supported | Custom method with Fixed Rate Per Item |
| New carrier or LTL service | Customizable | Custom shipping plugin: service codes, `Spec` configuration, estimate and calculate responses (`reference/custom-shipping-plugin.md`) |
| Add a handling surcharge after calculation | Customizable | Handling Charge field first; otherwise method override on the calculate step |
| Hide a method by cart contents | Customizable | Product shipping setting plus method rules; custom logic in a plugin; unverified beyond that |
| Calculate shipping per item with different origins | Needs confirmation | Warehouse address is the origin; per-item origin routing is not documented |
| Shipping rate API without a user id | Not supported | The shipping-estimates call needs a valid user id header or may return 404 (KB 80) |

## Pitfalls
- Method defined but not associated with the store, or the profile intersection removes it (`reference/shipping.md`, troubleshooting).
- Custom method with no associated rules is incomplete.
- Quantity/Weight limits are evaluated on the order line, not the whole order.
- Expecting $0 rates from plugins.
- Missing or invalid carrier credentials, sandbox/live mismatch, wrong shipping origin or warehouse address.
- UPS commercial address override changes rates.
- Tax class missing on a product: no rule matches; check Associated Products.
- Handling charges are not part of the tax base and (per Managing Returns) the article is inconsistent about whether returns refund them.

## Reference files
- `reference/tax.md` – tax classes, rules, plugins, AvaTax, exemption, customization.
- `reference/shipping.md` – methods, rule formulas, restrictions, carrier setup, address validation, troubleshooting.
- `reference/custom-shipping-plugin.md` – service registration, configuration, response contract, errors.

Related: `sdk-provider-plugins`, `sdk-method-overrides`, `commerce-checkout-payments`, `commerce-inventory`, `commerce-promotions-and-pricing`, `config-store`.
