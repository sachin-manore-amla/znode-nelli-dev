---
name: commerce-tax-shipping
description: Znode tax and shipping configuration - the Tax Manager and Shipping Manager orchestration services, supported engines and carriers, AvaTax setup fields, tax classes, shipping zones and the four custom shipping rate rule formulas. Use when configuring or debugging tax calculation or shipping rates at checkout.
user-invocable: false
---

# Znode Tax & Shipping

Both follow the same mirror architecture: **Core API → Manager service → Plugin → Provider**. See `sdk-provider-plugins`.

## Tax

### Supported systems

| Mode | Description |
|---|---|
| Native Sales Tax | Built-in rule engine — Sales Tax, VAT, GST, PST, HST per Country / State / ZipCode |
| AvaTax (Avalara) | External plugin, real-time REST; supports international import duties |
| Vertex | Partner plugin (`znode10-plugin-tax-vertex`) |
| Custom | Microservice implementing `IZnodeTaxPlugin` |

### Tax Manager

```
Znode Commerce API  --HTTP POST-->  Tax Manager (TaxGatewayController)
  POST /taxmanager/v1/tax-gateway/calculate                -> CalculateRates()
  POST /taxmanager/v1/tax-gateway/cancelorder              -> Cancelorder()
  POST /taxmanager/v1/tax-gateway/returnorderlineitem
  POST /taxmanager/v1/tax-gateway/presubmitorderprocess
  POST /taxmanager/v1/tax-gateway/submit                   -> commit the tax document
```

`TaxGatewayService` inspects `TaxBag.TaxType`: `"SalesTax"` delegates to in-process `IZnodeTaxSalesTax`; anything else is an HTTP call to the external plugin via `IPluginAPIClient`.

Models: `TaxManagerCalculateRequest/Response`, `TaxManagerCancelOrderRequest/Response`, `TaxManagerReturnOrderLineItemRequest/Response`, `TaxManagerPreSubmitOrderProcessRequest/Response`, `TaxManagerCommitTaxRequest/Response`.

### AvaTax configuration

`System Settings > Plugins > Installed Plugins > AvaTax`

**Global:** `Avalara App Name` · `Exemption Number` · `Allow Submissions Of Tax Requests`

**Per-store configuration set:** `AvaTax URL` (sandbox `https://sandbox-rest.avatax.com/api/v2`, production `https://rest.avatax.com/api/v2`) · `Company Code` · `Account Number` · `Avalara License` · `Freight Identifier` (item code for shipping cost) · `Prices Are Inclusive of Taxes`.

On order placement AvaTax **commits** the transaction; `CancelOrder` fires on cancellation.

### Tax classes

1. Create a Tax Class at `System Settings > Taxes > Add New`
2. Add Tax Rules per Country/State/ZipCode — rates for Sales/VAT/GST/PST/HST and whether shipping is taxable
3. Associate products at `System Settings > Taxes > Edit > Associated Products`

Tax classes, tax rules (by type) and their SKU and store associations are managed in Admin; the data is exposed through the tax APIs.

Checkout flow: assemble cart → resolve Tax Class per product → invoke the store's active plugin via Tax Manager → native rules match destination + class by precedence, or AvaTax returns line-level tax including import duties → display alongside shipping. A profile flagged **Tax Exempt** is charged no tax.

## Shipping

### Carriers

| Carrier | Type | Notes |
|---|---|---|
| FedEx | Real-time REST | Non-LTL (Ground, Overnight, 2Day) + LTL Freight; separate API keys per service class |
| UPS | Real-time REST (OAuth2) | Non-LTL + TForce Freight LTL; same credentials for test/prod, only the URL switches |
| USPS | Plugin | Listed in Available Plugins |
| Custom | Rules-based | No external API; rates from configured rules |

### Shipping Manager

```
POST /shippingmanager/v1/shipping-gateway/estimates  -> GetShippingEstimates()
POST /shippingmanager/v1/shipping-gateway/calculate  -> CalculateRates()
```

Groups the incoming `ShippingBagList` by `ShippingType`, then dispatches **parallel tasks** bounded by a `MaximumAllowedParallelTask` semaphore to each plugin URL. **Rates of $0 are currently filtered out.**

Models: `ShippingManagerEstimatesRequest` → `ShippingManagerEstimateRatesResponse`; `ShippingManagerCalculateRequest` → `ShippingManagerCalculateResponse`.

### Zones

There is no dedicated Shipping Zone entity. Restrictions are set on the **shipping method**: `Destination Country`, `State`, `Shipping Destination Postal Code`.

### Custom rate rules (one of each type per method)

| Rule | Formula | Applies |
|---|---|---|
| Weight-Based Rate | `BaseCost + (PerUnitCost x Qty x WeightPerProduct)` | when the **order line total weight** ∈ [Lower, Upper] |
| Quantity-Based Rate | `BaseCost + (PerUnitCost x Qty)` | when the **order line quantity** ∈ [Lower, Upper] |
| Flat Rate Per Item | `BaseCost + (PerUnitCost x Qty)` | always, regardless of qty or weight |
| Fixed Rate Per Item | `BaseCost` | always, regardless of qty or weight |

> **Outside the limits the rule does not apply at all — Shipping Rule Cost = 0**, it does not fall back to Base Cost. Limits are evaluated against the **order line** total, not the whole order.

Rules attach only to a **Custom** shipping type, at `System Settings > Shipping > Edit > Associated Rules`. Each rule type may be associated **once per shipping method**.

`Shipping Rate = Handling Charge + Rule Cost + Additional Shipping Cost Per Item` (the last is API-configurable only, not exposed in Admin).

### Setup and association

FedEx/UPS: create a project at the developer portal → set base URLs and the test/prod toggle in `web.config` (`FedExSandboxURL`, `IsUPSRestGatewayTest`, …) → enter credentials per store at `Stores & Reps > Stores > Shipping Origin`.

Methods are defined globally at `System Settings > Shipping` and must be explicitly associated per store at `Stores > Manage > Shipping Methods` — only associated methods appear at checkout, and the profile intersection rule then applies.

Shipping methods, shipping types, rate rules and their rule types, service codes, and store and SKU associations are managed in Admin.

## KB source

- [Managing Taxes](https://support.znode.com/support/solutions/folders/43000598155)
- [Managing Shipping (7)](https://support.znode.com/support/solutions/folders/43000598154)

## Related
`sdk-provider-plugins` · `commerce-checkout-payments` · `commerce-inventory`
