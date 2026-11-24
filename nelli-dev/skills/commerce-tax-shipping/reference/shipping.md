# Shipping
What this answers: shipping methods, rate rules, restrictions, carrier setup, address validation and troubleshooting.
Sources: KB Managing Shipping Methods, Associating Shipping Rules with a Shipping Method, Troubleshooting Shipping Methods, Managing Shipping Processing Plugins, Configuring a FedEx Account for Znode Access, Configuring a UPS Account for Znode Access, USPS Address Validation in Znode, Managing Returns (read 2026-11-23). Confidence 85.

## Method form (System Settings > Shipping)
Prerequisite: install the shipping plugins under System Settings > Plugins > Installed Plugins.
| Field | Notes |
|---|---|
| Shipping Method | carrier or provider; list depends on installed plugins |
| Shipping Name | internal unique name |
| Display Name | customer-facing; include a delivery time |
| Delivery Time Frame | shown at checkout |
| Internal Code | unique; Custom methods only |
| Shipping Service Code | carrier service; non-Custom methods |
| Handling Charge | flat, percent of order subtotal, or percent of shipping rate; not taxed |
| Destination Country, State, Shipping Destination Postal Code | region restrictions |
| Tracking URL | parcel tracking link |
| Enable | method appears at checkout |
| Display Order | lower first |
Tabs: Manage Shipping (General Settings, Shipping Display Settings), Associated Rules (Custom only), Additional Attributes. Delete: blocked if used in a webstore configuration or an order.

## Types and limits
- FedEx and UPS: carrier API rates plus optional handling. FedEx parcel up to 150 lb, FedEx Freight 150 to 2,500 lb, above 2,500 lb not supported. UPS: if UPS classifies an address as commercial it overrides the residential flag and returns commercial rates. USPS: not for packages over 70 lb (31.75 kg).
- Custom: rates from associated rules.

## Custom rate rules (System Settings > Shipping > Edit Custom > Associated Rules > Add New)
| Rule type | Formula | Limits |
|---|---|---|
| Fixed Rate Per Item | Base Cost | none |
| Flat Rate Per Item | Base Cost + (Per Unit Cost x Quantity Ordered) | none |
| Quantity-Based Rate | within limits: Base Cost + (Per Unit Cost x Quantity Ordered); outside: rule does not apply, cost 0 | Lower and Upper Limit on order line quantity |
| Weight-Based Rate | within limits: Base Cost + (Per Unit Cost x Quantity Ordered x Weight Per Product); outside: cost 0 | Lower and Upper Limit on order line total weight |
Fields: Base Cost, Per Unit Cost, Lower Limit, Upper Limit ("Limits For Tiered Pricing"). One rule of each type per method. A custom method is not complete until rules are associated. Not documented: whether limits are inclusive, whether Lower must be below Upper, error messages, worked numeric examples.
Shipping rate = handling charge + rule cost + additional shipping cost per item (API only).

## Association
- Store: Stores > Manage Store > Shipping Methods. Only associated methods are used.
- Product: Products > Edit > Product Info > Shipping Settings; the **Shipping Cost** setting selects which custom rule applies.
- Profile: assign methods to a profile in Accounts & Users > User Profiles > Manage User Profile; checkout intersects profile and store methods (no overlap: store methods; profile has methods but store has none: none shown).
- Shipping origin per store: Stores & Reps > Stores > Shipping Origin (carrier accounts live here).

## Carrier setup (Znode side)
FedEx (Shipping Origin > Fedex section): Shipping Account Number (non-LTL), LTL Account Number, Account API Key, Account Secret Key, Use FedEx Discount Rate, Declare Package Value. Two account numbers per store, both linked to the same key pair. Environment: `FedExSandboxURL`, `FedExProductionURL`, `IsFedExRestGatewayTestMode` (true = test); regenerate the secret only in production and update Znode afterwards or estimates fail.
UPS (Shipping Origin > UPS section): UPS Client ID, Client Secret, Account Number; LTL account number, client ID, client secret (blank if unused); Shipment Drop-Off Type; Packaging Type. Environment: `UPSRestGatewayBaseURL`, `UPSRestProductionBaseURL`, `IsUPSRestGatewayTest`; same credentials for test and production.
These environment settings are application configuration, not Admin fields.

## USPS address validation
Plugin installed and active; configuration set with Configuration Code, Display Name, Client ID, Client Secret, optional Shipping Calculation Method (default Total Cart Weight, alternative Per-Item Shipping); **Is address validation configuration set** (default NO; YES makes it selectable). Store: Store Settings > Address Validation Settings: Enable Address Validation, Configuration Set, optionally Validate Addresses in Address Book Page and Allow User to Override Address. Runs on shipping/billing entry, add and edit at checkout; U.S. only; existing addresses untouched; one set per store; if USPS is unavailable checkout continues silently.

## Plugins page behaviour
Open a plugin via Plugin Name or the gear icon; tabs Plugin Information, Global Configuration, Configuration Sets. A plugin must be configured before it can process. The shipping-estimates API needs a valid user id in the request header; missing or invalid may give 404.

## Troubleshooting: methods not appearing
1. Shipping origin or warehouse details wrong (Stores > Manage Store > Shipping Settings).
2. Carrier credentials missing or invalid (same screen).
3. Method not associated with the store (Stores > Manage Store > Shipping Methods).
4. Plugin configuration (account, token, URL) wrong; several sets can exist for live and sandbox.
5. Sandbox vs live mismatch.
6. Profile-based: store level broken first; method not assigned to the profile.
7. Custom method without associated rules; product Shipping Cost setting not pointing at an existing rule.
8. Rate of 0 from a plugin (filtered out).
