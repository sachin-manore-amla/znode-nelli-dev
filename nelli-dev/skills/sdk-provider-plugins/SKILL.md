---
name: sdk-provider-plugins
description: Payment, shipping, tax and address-validation provider plugins in Znode 10 - the manager services that call plugins, the built-in providers, how a plugin is installed, configured and activated in Admin (System Settings > Plugins, configuration sets, global versus store scope, Spec.yml fields), how to write your own from the Custom API SDK templates (the controller contract each template implements, request and response models, hosting, security of provider credentials), the built-in custom shipping rate rules, tax classes and rules, and payment flows at a high level. Load it for any requirement about a new carrier, custom shipping rates, free shipping, a tax provider or tax rule, a payment gateway or payment method, or address validation.
user-invocable: false
---

# Provider plugins (payment, shipping, tax, address validation)

## Model in one picture
```
Znode API --> Shipping Manager / Tax Manager / Payment Manager --> plugin service (HTTP) --> provider API
```
A **plugin** is a package (Spec.yml plus a service) installed in System Settings > Plugins. A **configuration set** is a named group of values (credentials, URLs, options) for one plugin; a plugin can have several, each attached to stores. Plugin types: `Tax`, `Shipping`, `Payment` (external gateway), `PaymentInternal` (Znode's own methods: Charge on Delivery, Purchase Order, Invoice Me).

## Ten facts that matter
1. Built-in: shipping FedEx, UPS, USPS, Custom (rules, in-process); tax native Sales Tax, AvaTax, Vertex; payment Spreedly gateway (credit card, ACH) plus Charge on Delivery, Purchase Order, Invoice Me; address validation USPS. (KB 80, module guide 85)
2. Install flow: System Settings > Plugins > Available Plugins > install > Installed Plugins > open > Activate > Save; then add a configuration set; then attach to the store. Znode downloads the package, reads its spec file and registers it. (95)
3. How **your own** plugin package gets into Available Plugins is not in the customer sources: ask Znode (`GAPS`).
4. Only fields declared in Spec.yml appear in Admin. Field `varyBy` is `global` (plugin-wide) or `store` (per configuration set). (KB 80, spec files 95)
5. The shipping manager calls `<plugin URL>/v1/<plugin name>/calculate` and `/estimates` (POST, JSON, no authentication header, no retry, errors swallowed). The tax plugin template exposes `calculate`, `cancelorder`, `submit`, `presubmitorderprocess`, `returnorderlineitem`. (95)
6. A failing or silent plugin means **no rate or no tax**, not an error: the option simply does not appear. (95)
7. Shipping responses must carry a positive `ShippingRate` (estimates) or `ShippingCost` (calculate) and a non-null `ResponseMessage`; `IsValidShippingSetting` must be true. $0 methods are filtered out. (KB 80, source 95)
8. The manager sends the configuration set values (including secrets) in the request body to the plugin: host plugins on a private network and never log request bodies. (95)
9. Custom shipping rules are four formulas, one of each type per method, in System Settings > Shipping. (KB 80)
10. Tax is chosen per **tax rule** (Tax Type) of a tax class that is associated with the store; the store's tax configuration set supplies credentials. (95, KB 80)

## Reference files
- `reference/architecture-and-admin.md` – managers, install, configuration sets, scopes, store association.
- `reference/spec-yml.md` – the spec file schema and field types.
- `reference/shipping-plugin.md` – contract, models, rules for a custom carrier, shipping methods and rule types.
- `reference/tax-plugin.md` – contract, tax classes and rules, store tax settings.
- `reference/payment-plugin.md` – payment flow, gateway plugin contract, UI bundle, security.
- `reference/hosting-and-security.md` – deployment, secrets, testing, failure behaviour.

## Nelli-Dev decision guide
| Requirement | Verdict | Route |
|---|---|---|
| Flat or weight/quantity based shipping | Supported | Custom shipping type with associated rules |
| Free shipping above a threshold | Supported | 100% Percent Off Shipping promotion with Minimum Order Amount, or a Custom method with a rule; do not return a $0 plugin rate |
| Free shipping for some products | Supported | Product free-shipping setting uses the built-in Free Shipping method |
| Different shipping methods per customer group | Supported | Profile-specific methods (intersection with store methods) |
| New carrier (regional courier, LTL, pickup) | Customizable | Shipping plugin from the template, Spec.yml, hosted service |
| Add handling fee | Supported | Handling Charge on the method (amount, percent of subtotal, percent of rate) |
| Adjust final shipping amount | Customizable | `sdk-method-overrides` |
| Tax by country/state/zip | Supported | Tax class and tax rules |
| Tax by external provider (not AvaTax/Vertex) | Customizable | Tax plugin from the template |
| Send customer code to AvaTax | Customizable | `InitiateTaxCalculationCompleted` override |
| Tax exempt customers | Supported | Profile tax-exempt flag, CSR tax exempt |
| New payment gateway | Not self-service for gateway plugins through Spreedly: request through Znode; a fully custom payment plugin is Customizable only with Znode involvement | `reference/payment-plugin.md` |
| New payment method type (invoice-like) | Supported if Purchase Order, Invoice Me or COD fits | Configuration sets |
| Address validation by another vendor | Customizable | Address validation endpoint `{plugin}/v1/address/validate`; confirm with Znode |
| Intercept payment capture | Needs platform change | No hook |

Related: `commerce-promotions-and-pricing`, `sdk-method-overrides`, `commerce-orders-and-checkout-customization`, `sdk-custom-api`, `quality-security-checks`.
