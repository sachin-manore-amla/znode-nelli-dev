# Tax: configuration and writing a tax plugin
What this answers: native tax setup, tax classes and rules, store tax settings, and the contract of a custom tax plugin.
Sources: KB Managing Taxes, Adding a Tax Rule, Managing Tax Processing Plugins (read, 80); SDK tax template, abstract plugin models, calculate-cart source (95).

## Native tax setup (Admin)
1. System Settings > Taxes > Add New: Tax Class Name, Display Order, Activate. Saving adds tabs **Manage Taxes** (rules) and **Associated Products**.
2. Add Rule: Tax Type (default only "Sales tax"; installed tax plugins also appear), Include Shipping in taxes, Precedence, Destination Country, Destination State, Zip Code (optional), Sales Tax, VAT Tax, GST Tax, PST Tax, HST Tax.
3. Associate products to the tax class.
4. Stores > Manage > Tax Settings: associate tax classes, set the default tax class, associate the tax configuration set (AvaTax, Vertex), test the AvaTax connection.
Tax is computed with the rule whose plugin is selected in the rule's Tax Type; precedence orders rules. Profile "Tax Exempt" and CSR tax exempt give 0 tax. Setting "Calculate Tax On Discounted Price" is global (`commerce-promotions-and-pricing`). Quote and order paths use the same plugins; zero-rate tax types are ignored in the bifurcation (10.10).

## AvaTax
Global: Avalara App Name, Exemption Number, Allow Submissions Of Tax Requests. Set (per store): AvaTax URL, Company Code, Account Number, Avalara License, Freight Identifier, Prices Are Inclusive of Taxes. Order placement commits the document; cancel and return call the matching plugin actions. The tax customer code can be set by method override (`InitiateTaxCalculationCompleted`).

## Contract for a custom tax plugin
Base class the tax plugin base controller (`TaxPluginController` with the Znode prefix) (package `Znode10.Libraries.Abstract.Plugin.Tax`), five abstract actions, POST JSON:
| Route in the template | Action | Request | Response |
|---|---|---|---|
| `v1/TaxTemplate/calculate` | `Calculate` | `CalculateTaxRequest`: `PluginGlobalConfigurations`, `PluginConfigurationSet`, `PluginTaxCart` (cart items with SKU, quantity, amount, discount, tax code, tax class; origin, destination, billing address; shipping cost and discount; handling; currency; `IsPricesInclusiveOfTaxes`, `IsCalculateTaxAfterDiscount`, `TaxExempt`, order number and state, `CustomTaxCost`) | `CalculateTaxResponse`: `TaxCost`, `SalesTax`, `TaxRate`, `TaxOnShipping`, `ImportDuty`, per-item taxes (`CartItems`), `TaxSummaryList`, `TaxMessageList`, `IsSuccess`, `ErrorDetail` |
| `.../submit` | `CommitTax` | order identifiers and cart | `CommitTaxResponse` |
| `.../presubmitorderprocess` | `PreSubmitOrderProcess` | cart | validity result |
| `.../cancelorder` | `CancelOrder` | order and user | `CancelOrderResponse` |
| `.../returnorderlineitem` | `ReturnOrderLineItem` | returned items | `ReturnOrderLineItemResponse` |
Each request carries the configuration set, so credentials arrive per call. Keep the route prefix consistent with your Spec name (confirm with Znode how the tax manager forms the URL; the shipping manager uses `/v1/<name>/`).
Failure behaviour: a failed tax call logs and yields no tax or blocks submit depending on the path; test both quote and order. Not verified: the tax manager's timeout and retry.

## Guidance
Use the native rules first. Use a plugin only when rates must come from a provider. Return line-level taxes that add up to `TaxCost`; return a clear `ErrorDetail` for unserviceable addresses. For tax customer identity use the override hook rather than a second plugin.
