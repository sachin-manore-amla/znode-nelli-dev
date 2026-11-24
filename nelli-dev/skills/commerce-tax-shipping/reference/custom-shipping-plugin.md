# Custom shipping plugin (customer view)
What this answers: what a custom shipping plugin must register, configure and return.
Source: KB Integrating Custom Shipping Plugins (read 2026-11-23). The article points to a separate "Shipping Plugin Customization Developers Guide" for endpoint paths, request schemas, authentication and deployment: **not read**. The code contract from the SDK template is in `sdk-provider-plugins`. Confidence 80.

## Architecture
A plugin is an independent service running shipping logic outside the Znode platform. It defines one or more **Shipping Services** (examples: LTL Freight, Local Truck Delivery, Will Call Pickup), can return several services in one response, and can be versioned independently.

## Service registration in Admin
| Field | Rule |
|---|---|
| Shipping Service Code | unique, no spaces or special characters, equal to what the plugin expects (LTLFREIGHT, OURTRUCK, WILLCALL) |
| Display Name | shown in Admin |
| Display Order | order in Admin |
| IsCalculateIndividually | 1: Znode calls the Calculate operation once per service; 0: one Estimate call for all services |
Admins enable services per store, map them to shipping methods and show rates at checkout.

## Configuration
- Global (all stores and environments): API base URL, authentication details, Environment (Sandbox or Production), shared headers or tokens.
- Store level (configuration sets): API keys, account numbers, warehouse or location identifiers, store rules.
- The plugin's `Spec.yaml` defines the schema and the Admin UI: only fields defined there appear in Admin. Include required fields, global versus store designation, groupings, data types, validation rules.

## Response contract
Estimate (each item in `ShippingEstimateRate[]`): `ShippingCode` required; `ShippingRate` required and greater than 0; `ResponseMessage` required, not null.
Calculate: `ShippingCost` required and greater than 0; `IsValidShippingSetting` required and true; `ResponseMessage` required.
Zero-cost rates are filtered out today (an enhancement for free shipping was in progress per the article).

## Errors
Return structured business messages ("Carrier unavailable", "Account not eligible") rather than generic 500s; they reach downstream systems and the UI.

## Pre-development checklist
Service codes, display names and order; IsCalculateIndividually values; global and store fields; validated `Spec.yaml`; sample Estimate and Calculate responses; error formats; business rules.

## Not documented here
Endpoint paths and payload schemas, authentication mechanics, deployment steps, how your package reaches Available Plugins (ask Znode).
