# Design recipes and anti-patterns

What this answers: how to design a custom table well, five recipes, how to promote tables between environments, and what to avoid.

## Design checklist

1. Can an attribute or user-defined field do this instead? A field on an existing product, account, user or store belongs there, not in a table.
2. Choose the **Table Key** as a permanent name (letters and digits, no spaces).
3. Give the table **one unique field** (your own business key) before any data goes in. It is the only way to get upsert imports and `/unique/{value}` lookups, and it cannot be added once rows exist.
4. Keep columns to 10 to 15; keep rows well under the advisory 50,000.
5. Use `Numeric` with scale 0 for whole numbers (the integer type cannot be created); use `Text` for codes; store dates as `datetime` but send ISO dates and expect `1900-01-01` for empty values from the API.
6. Set the three Global Settings to sensible ceilings (blank means no ceiling).
7. Decide who may call the API and put your own authorization in front of anything a shopper can reach.

## Recipes

### 1. ERP id cross-reference
Table `ErpCustomerMap`: `ErpCustomerId` (Text 50, unique), `AccountCode` (Text 100), `PriceTier` (Text 20). Load by import or a scheduled data exchange. Your integration looks up with `/unique/{ErpCustomerId}`.

### 2. Lookup list used by custom code
Table `Regions`: `RegionCode` (unique), `RegionName`, `SalesTeam`. Custom endpoint reads `/records`, caches for a bounded time, returns only needed fields.

### 3. Feature flag or eligibility list
Table `FeatureAccess`: `FeatureCode`, `AccountCode`, `IsEnabled` (Boolean). Only one unique field is allowed, so use a composite value such as `FeatureCode|AccountCode` as the unique `AccessKey`. Reads must be fast and cached; changes appear after the cache lifetime.

### 4. Configuration with thresholds
Table `ShippingThresholds`: `ThresholdCode` (unique), `MinOrderValue` (Numeric 12,2), `Active` (Boolean). Read by a custom endpoint or a method-override receiver. Small tables only.

### 5. UI-level note for a record
Table `AccountNotes`: `AccountCode` (unique), `HandlingNote` (TextArea 500). Shown on an Admin custom page or a custom Webstore component through your endpoint.

## Environments: tables do not promote themselves

The documentation does not describe exporting or promoting a table definition between environments. Treat table, field and settings creation as **code**: a script that is safe to re-run, using the API in this order: `GET /v1/custom-tables/{key}` (create if 404), `GET /v1/custom-table-fields/{key}` (create missing fields only, as an array), then load data. Never rename or drop in a re-run script. Keep the script in source control and run it per environment. Remember the Global Settings can differ per environment (field length ceilings).

## Testing

Create test tables with an unmistakable prefix, never touch production, assert on exact messages, clean up what you create, and do not run data-changing tests on a shared environment without agreement. Check each behaviour that matters on the customer's Znode version (see `known-behaviours.md`).

## Anti-patterns

| Anti-pattern | Why |
|---|---|
| Using a table as the store for orders, payments or high-frequency writes | not what it is for; no joins, no transactions across tables |
| Storing the system `Id` in another system | it is not stable across re-imports |
| Scripting `POST .../import` from the published contract | the implementation ignores it |
| Importing the same file twice into a table with no unique field | duplicates every row |
| Calling `/records` per page view | returns every row unpaged |
| Reading or writing the table's database directly | unsupported; bypasses validation and events |
| Changing a system table's fields or key | breaks the feature that owns it |
| Leaving the length settings blank to "disable" tables | blank removes the ceiling |
| Exposing the table API to the browser | no per-user authorization on it |
