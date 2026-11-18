# Shipping: methods, rules and writing a carrier plugin
What this answers: shipping method configuration, the four custom rate rules, display logic, and the contract a custom shipping plugin implements.
Sources: KB Managing Shipping Methods, Associating Shipping Rules, Integrating Custom Shipping Plugins (read, 80); SDK shipping template, abstract plugin models, shipping manager (95).

## Shipping methods (Admin)
System Settings > Shipping > Add New. Fields: Shipping Method (provider), Shipping Name (internal, unique), Display Name, Delivery Time Frame, Internal Code (Custom only), Shipping Service Code (carrier types), Handling Charge (Amount, Percentage of Order Subtotal, Percentage of Shipping Rate; not taxed), Tracking URL, Enable, Display Order, Additional Attributes. Destination restrictions: Destination Country, State, Shipping Destination Postal Code (no separate zone object). Product shipping settings choose the cost rule (Products > Edit > Shipping Settings).
Delete is blocked when the method is used in a store or an order. A built-in **Free Shipping** method serves downloadable and free-shipping products and cannot be deleted while used.

## Custom rate rules (Custom type only, Associated Rules > Add New, one of each type per method)
| Rule | Fields | Cost |
|---|---|---|
| Fixed Rate Per Item | Base Cost | Base Cost |
| Flat Rate Per Item | Base Cost, Per Unit Cost | Base + Per Unit x Quantity |
| Quantity-Based Rate | Base, Per Unit, Lower/Upper Limit (line quantity) | Base + Per Unit x Quantity inside limits, else the rule gives 0 |
| Weight-Based Rate | Base, Per Unit, Lower/Upper Limit (line total weight) | Base + Per Unit x Quantity x Weight inside limits, else 0 |
Shipping Rate = Handling + rule cost + Additional Shipping Cost per Item (API only). Limits apply to the order **line**, not the whole order.

## Checkout display
Profile methods are intersected with store methods; no overlap shows the store methods; profile methods with no store methods show nothing. See `commerce-orders-and-checkout-customization`.
For carrier types (UPS, FedEx, USPS) a rate must be above 0 to be listed. FedEx: up to 150 lb parcel, 150 to 2,500 lb Freight (LTL), above 2,500 lb not supported. UPS decides residential versus commercial and may return commercial rates.

## Contract for a custom carrier plugin
Base class the shipping plugin base controller (`ShippingPluginController` with the Znode prefix) (package `Znode10.Libraries.Abstract.Plugin.Shipping`), two abstract actions:
| Route (POST) | Request | Response |
|---|---|---|
| `/v1/<plugin name>/calculate` | `ShippingCalculateRequest`: `PluginGlobalConfigurations`, `PluginConfigurationSet`, `PluginCalculateShippingCart` (shipping bag with `ShippingCode`, `HandlingCharge`, `SubTotal`, `HandlingBasedOn`, `CalculateShippingPerLineItem`; cart items with SKU, quantity, weight, dimensions, free-shipping flag; origin, destination, billing addresses; currency) | `ShippingCalculateResponse`: `IsSuccess`, `ErrorDetail`, `PluginCalculateShippingCart` (`ShippingCost` > 0, `OrderLevelShipping`, `ShippingHandlingCharge`, `IsValidShippingSetting` true, `ResponseMessage`, `ApproximateArrival`, per-item costs) |
| `/v1/<plugin name>/estimates` | `ShippingGetEstimateRateRequest` (same configuration objects, estimate cart) | `ShippingGetEstimateRateResponse.ShippingEstimateRate[]` each with `ShippingCode` (required), `ShippingRate` (> 0), `EstimateDate`, `ResponseMessage` (not null) |
Address validation (optional): `{plugin URL}/{plugin name}/v1/address/validate`.
Extra: `Custom1` to `Custom5` strings pass through from the API request.
Service codes: unique, no spaces or special characters (examples `LTLFREIGHT`, `WILLCALL`). `IsCalculateIndividually` 1 means one calculate call per service, 0 means one estimates call for all.
Errors: return structured business messages (for example "Carrier unavailable") in `ErrorDetail`, not a bare HTTP 500 (KB 80). The manager treats a thrown or failed call as "no rate".
Template layout: Api (controller, routes, startup), Services (your logic: `Calculate`, `GetEstimateRate`; both first copy the configuration set into the plugin helper), Library (provider models), Api.Setting. The template controller catches exceptions into `ErrorDetail` with status 500. Template route segment is `ShippingTemplate`; **rename it to your Spec name**.

## Steps
1. Gather: service codes, display names and order, `IsCalculateIndividually`, global and store fields, sample responses, error format.
2. Write and validate Spec.yml. 3. Copy the template, implement both actions. 4. Unit-test with sample requests. 5. Host (private network). 6. Obtain registration (Znode). 7. Install, configure sets, activate, create the shipping method of the new type and its service codes, associate to the store. 8. Test estimates and checkout.
$0 rates (free shipping) are currently filtered out; model free shipping with promotions or Custom methods instead.
