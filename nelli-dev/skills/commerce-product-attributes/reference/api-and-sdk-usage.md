# APIs, storefront data and customization access

What this answers: which operations create, read and change attributes, groups, families and values, which are legacy v1 and which are v2, the shapes the storefront reads, and how a customization (Custom API SDK, Webstore) uses them.

## Rule for this area

Attribute, group and family management exists only in the legacy Core API v1 (documented separately as the v1 reference). Core API v2 offers read operations for published products and one read for attribute groups. Per `api-catalog`, a design that needs v1 writes must say "legacy v1, no preferred alternative found" and let the developer decide. Admin changes through the Admin console are always supported.

## Operations

Verified in the exported public specifications (checked 2026-10-15).

| Need | Operation | Family |
|---|---|---|
| List attributes (with expand for locales, types, groups, defaults, families) | `GET /PIMAttribute/List` | v1 legacy |
| Get one attribute | `GET /PIMAttribute/Get/{id}` | v1 legacy |
| Create attribute | `POST /PIMAttribute/Create` (body: `AttributeModel`, `FrontProperties`, `ValidationRule[]`) then `POST /PIMAttribute/SaveLocales` | v1 legacy |
| Update attribute | `PUT /PIMAttribute/Update` | v1 legacy |
| Delete attributes | `POST /PIMAttribute/Delete` | v1 legacy |
| Attribute types | `GET /PIMAttribute/AttributeTypes/{isCategory}` | v1 legacy |
| Validation options for a type | `GET /PIMAttribute/InputValidations/{typeId}/{attributeId}` | v1 legacy |
| Front-end properties (comparable, search, facets) | `GET /PIMAttribute/FrontEndProperties/{pimAttributeId}` | v1 legacy |
| Options (default values) | `POST /PIMAttribute/SaveDefaultValues`, `GET /PIMAttribute/GetDefaultValues/{pimAttributeId}`, `DELETE /PIMAttribute/DeleteDefaultValues/{defaultvalueId}`, `GET /PIMAttribute/GetAttributeDefaultValueList` | v1 legacy |
| Code and uniqueness checks | `GET /PIMAttribute/IsAttributeCodeExist/{attributeCode}/{isCategory}`, `POST /PIMAttribute/IsAttributeValueUnique` | v1 legacy |
| Validation by attribute codes | `POST /PIMAttribute/GetAttributeValidationByCodes` | v1 legacy |
| Groups | `/PIMAttributeGroup/*`: List (marked deprecated), Get, Create, Update, Delete, AssociateAttributes, RemoveAssociatedAttributes, UpdateAttributeDisplayOrder, SaveAttributeGroupLocales, AssignedAttributes, UnAssignedAttributes | v1 legacy |
| Read groups with their family ids | `GET /v2/pim-attribute-groups` (filters `GroupCode`, `localeCode`, `LocaleId`; added in release 10.13.0.1) | Core v2 |
| Families | `/PIMAttributeFamily/*`: List, Create, Delete, AssociateAttributeGroup, UnAssociateAttributeGroup, AssignAttributes, UnAssignAttributes, UpdateAttributeGroupDisplayOrder, SaveLocales and the Assigned/UnAssigned lists | v1 legacy |
| Custom fields | `/Products/AddCustomField`, `GetCustomFieldList`, `GetCustomField/{id}`, `UpdateCustomField`, `DeleteCustomField` | v1 legacy |
| Published product with attributes | `GET /v2/published-products/{publishProductId}` | Core v2 |
| Published attributes of a SKU, with configurable definitions | `GET /v2/published-products/{sku}/attribute` | Core v2 |
| Configurable options | `GET /v2.2/published-products/{parentProductSKU}/configurable-products` | Core v2 |
| Compare | `GET /v2/published-products/{productSKUs}/compare-products` | Core v2 |

Not for PIM: the v2 `global-attribute*` routes and the v1 `/AttributeFamily`, `/AttributeGroup`, `/Attributes` routes belong to global (user-defined) attributes and media attributes. The v2 `attribute-families` calls are for global families, not PIM families. There are no PIM family create/update routes in v2.

Release 10.14.0.4 made PIM list and get API responses include full attribute configuration details. Release 10.8.0.0 let the Commerce API return specific custom product attributes and preserved special characters in attribute data across APIs.

Create order of work through the API: create the attribute, save locales, save default values (for select types), create or find the group, associate attributes, create or find the family, associate the group, then create products with that family. If locales are not saved the attribute may not show correctly in the Admin. (API reference text)

API behaviour to know: the v1 attribute, group and family routes check no role, only the API credentials; the API does not apply some Admin screen rules (code format and lock, uniqueness on update, built-in and hidden flags, display order range). Validate on your side. Saves are not transactional: a create can leave a partial result (for example a group with no name whose code is taken).

## Published attribute shape (read side)

`GET /v2/published-products/{publishProductId}` and `{sku}/attribute` return `Attributes[]` with:

`AttributeCode`, `AttributeName`, `AttributeValues` (string; select options come as codes or values), `AttributeTypeName`, `IsComparable`, `IsHtmlTags`, `IsFacets`, `IsUseInSearch`, `IsConfigurable`, `IsPersonalizable`, `IsCustomField`, `IsSwatch`, `DisplayOrder`, `SelectValues[]`, `ConfigurableAttribute[]`.

The published product has no family or group information. To read an attribute value in the storefront, find it by `AttributeCode` in `Attributes`. Casing: the API returns PascalCase; the Webstore client converts to camelCase.

## How a customization reads or writes attributes

| Goal | Approach |
|---|---|
| Show a new attribute on the PDP | Create the attribute in Admin, add it to a group in the product's family, fill and publish. In the Webstore it arrives in `Attributes`; add rendering in a component or theme (source customization). Product page tabs are built from three fixed attributes, so a new tab needs a Webstore change. |
| Filter or search by it | Set `Is used for facets` and/or `Is used in Search`, add it to a search profile, full catalog publish. No code if it is a Simple or Multi Select attribute (Supported). |
| Read it in a custom endpoint | Call `GET /v2/published-products/{sku}/attribute` or the published product route through the gateway with the portal and locale headers (`api-auth-and-headers`). Do not read the PIM draft. |
| Write values from an ERP or script | Product import (async CSV or Excel, key `SKU`, see import-export-and-limits.md), or the product operations in the API reference (verify the operation before use). Imports raise no platform events. |
| React to a change | No attribute-specific event or webhook is documented; check `sdk-events-and-webhooks`. Not verified (see gaps). |

The Custom API SDK ships no sample or client wrapper for attributes, families, custom fields or overrides (searched 2026-10-15). A custom endpoint calls the Znode APIs through the gateway like any other client; keep the call count low (batch SKUs, cache published attribute reads per store and locale).

Direct database access is not a supported way to read or write attribute data.
