# API operations and how field values appear on entity payloads
Core v2 operations to define fields, groups, families and to read and write values, plus where values show up on user, account, store, promotion, container and form responses.
Use the Core v2 operations. The older Multifront (v1) routes exist for the same features and are legacy (skill `api-catalog`).

Auth: the usual gateway token (skill `api-auth-and-headers`). The product checks no role or store for these calls beyond the token (module guide, brand entity, 85), so protect them in your own extension. Marks: SPEC = in the local public spec copy, SRC = verified in the product source but missing from the local spec copy (check apidocs before quoting it to a customer).

## Fields (attributes)

| Method and route | Purpose | Mark |
|---|---|---|
| `GET /v2/global-attributes` | List fields. Filter keys `localeId`, `AttributeCode`, `AttributeLabel`, `AttributeType`. Sort `AttributeCode`, `AttributeName` and others. Response `Attributes[]` with `AttributeCode`, `AttributeName`, `AttributeTypeName`, `EntityName`, `IsRequired`, `IsLocalizable` | SPEC |
| `GET /v2/global-attributes/{attributeCode}` | One field | SPEC |
| `POST /v2/global-attributes` | Create. Body `AttributeModel` (`AttributeCode`, `EntityName`, `AttributeTypeName`, `IsRequired`, `IsLocalizable`, `IsActive`, `HelpDescription`, `DisplayOrder`, `AttributeDefaultValue`) and `ValidationRule[]` (`InputValidationName`, `InputValidationRuleName`, `Name`). 409 if the code exists | SPEC |
| `POST /v2/global-attributes-locale`, `PUT /v2/global-attributes-locale` | Labels. Body `AttributeCode`, `Locales[]` (`LocaleCode`, `AttributeName`, `Description`). POST gives 409 `The provided attribute locale is already present.` | SPEC |
| `POST /v2/global-attributes-default-value`, `PUT /v2/global-attributes-default-value` | Options for select types. Body `AttributeCode`, `AttributeDefaultValueCode`, `ValueLocales[]`, `DisplayOrder`, `IsDefault`, `SwatchText`, `IsSwatch`. POST gives 409 `The provided attribute default value details already exists.` | SPEC |
| `DELETE /v2/global-attributes-bulk/{attributeCodes}` | Delete by comma-separated codes | SPEC |
| `DELETE /v2/default-values/{defaultvalueId}` | Delete one option | SRC |
| `GET /v2/attribute-locale/{globalAttributeId}` | Labels of a field | SRC |
| `GET /v2/input-validations/{typeName}/{attributeCode}` | Rules allowed for a type, with the field's current values | SRC |

There is no v2 call to edit an existing field definition, to list options, or to check whether a code exists (SRC check: none found). Use the Admin for edits. The v1 `PUT /GlobalAttribute/Update`, `GET /GlobalAttribute/IsAttributeCodeExist/{attributeCode}`, `GET /GlobalAttribute/GetDefaultValues/{globalAttributeId}` and `POST /GlobalAttribute/IsAttributeValueUnique` exist in the spec (legacy).

## Groups

| Method and route | Purpose | Mark |
|---|---|---|
| `GET /v2/global-attribute-groups` | List | SPEC |
| `GET /v2/global-attribute-groups/{groupCode}`, `GET /v2/global-attribute-groups-locale/{groupCode}` | One group and its names | SRC |
| `POST /v2/global-attribute-groups`, `PUT /v2/global-attribute-groups` | Create or update. Body `GroupCode`, `EntityName`, `AttributeGroupLocales[]` | SRC |
| `DELETE /v2/global-attribute-groups-bulk/{groupCodes}` | Delete | SPEC |
| `POST /v2/global-attribute-groups/{attributeCode}/assign-groups/{groupCode}` | Put a field in a group | SPEC |
| `POST /v2/global-attribute-groups/{groupCode}/unassign-groups/{globalAttributeCodes}` | Remove fields | SRC |
| `GET /v2/global-attribute-groups/{groupCode}/assigned-attributes` and `/unassigned-attributes` | Members and candidates | SRC |
| `PUT /v2/global-attribute-groups/update-attributes-display-order` | Body `AttributeCode`, `DisplayOrder` 1 to 999 | SPEC |

## Families

| Method and route | Purpose | Mark |
|---|---|---|
| `GET /v2/global-attribute-families` | List | SRC |
| `GET /v2/global-attribute-families/{familyCode}` | One family | SPEC |
| `POST /v2/create-attribute-families` | Body `FamilyCode`, `AttributeFamilyName`, `GlobalEntityName`, `AttributeFamilyLocales[]` | SPEC |
| `PUT /v2/update-attribute-families`, `DELETE /v2/delete-attribute-families/{familyCode}` | Update, delete | SRC |
| `GET /v2/assigned-attribute-groups/{familyCode}` | Groups of the family | SPEC |
| `POST /v2/global-attribute-family/{familyCode}/assign-groups/{attributeGroupCodes}`, `PUT .../unassign-groups/{groupCode}` | Assign, unassign | SRC |
| `PUT /v2/global-attribute-group/{groupCode}/display-order` | Group order in a family | SPEC |

The route that returns the family's locale details is registered with the path `/v2/global-attribute-family/{familyCode}/assigned-groups` in the source, the same name as the assigned-groups idea. Test before relying on it.

## Entities and values

| Method and route | Purpose | Mark |
|---|---|---|
| `GET /v2/global-entities` | Entity types on this environment | SRC |
| `GET /v2/global-entity-attributes/{entityCode}/assigned-groups`, `.../unassigned-groups`, `POST .../associate-groups/{groupCodes}`, `PUT .../unassociate-groups/{groupCode}` | Entity to group link | SRC |
| `GET /v2/global-entity-attributes/code/{entityCode}/{entityType}` | All values of one record, grouped. Query `localeCode`, `groupCode`. Response `EntityDetails.Groups[].Attributes[]` and `EntityDetails.Attributes[]` with `AttributeCode`, `AttributeTypeName`, `IsRequired`, `IsLocalizable`, `AttributeName`, `ControlName`, `ValidationName`, `ValidationValue`, `SelectValues`. 204 when nothing is set up | SPEC |
| `GET /v2/global-entity-attributes/{recordId}/{entityType}/{attributeCode}` | One value. Response `AttributeValue`, `RecordId`. `recordId` must be a number: store = portal id, user = user id, account = account id, content container = container variant id | SPEC |
| `GET /v2/global-entity-attributes-bulk/{recordIds}/{entityType}/{attributeCode}` | The same value for many records | SRC |
| `GET /v2/global-entity-attributes/{familyCode}/{entityType}` | The field definitions of a family (container default variant) | SPEC |
| `PUT /v2/global-entity-attributes` | Write values. Body `GlobalAttributeDetails[]` of `AttributeCode`, `AttributeValue`, `LocaleCode`, `EntityType`, `EntityCode`. Response echoes the list with `IsSuccess` | SPEC |

Rules of the write call (verified in source, 90):
- Send values for one entity type per request. The record check uses the first field's entity type.
- The `Znode-PortalCode` header is read and passed on. Set it.
- Checked: field code exists, entity record exists, Date value parses as a date, Number value is numeric, select values equal existing option codes (Multi Select: each item). Blank values are rejected as invalid, so this call cannot clear a value.
- Not checked: Required, `Max Characters`, `Regular Expression`, Min and Max, `Unique Value`, file extension. Enforce them in your own code.
- Error text: `Invalid data: Following are the attribute codes which do not exist in the system: <codes>. Following are the entity codes which do not exist in the system: <codes>. Following are the codes with invalid values: <codes>.` Unknown entity type: `Invalid or unsupported entity type(s) found - EntityType: <x>, AttributeCode: <y>. Please provide valid entity types.` Save failure: `Failed to save Entity Attribute.` Status 500 on save failure, 404 on the other cases.
- File and Image fields: upload with `POST /v2/files-upload`, then write the returned `MediaId` as `AttributeValue`. The upload is validated against the DAM media settings.
- Date values: send a date string the server can parse.
- This v2 save raises no domain event (module guide, brand entity, 85).

## How values appear on entity responses

| Response | Where the values are | Mark |
|---|---|---|
| `GET /v2/portals/{storeCode}` and `GET /v2.1/portals/{storeCode}/application/{type}` | `GlobalAttributes.Attributes[]`. Only fields with a value (the Store response drops blanks). B Store settings carry `BStoreGlobalAttributes` | SPEC |
| `GET /v2/users/{userId}/{storeCode}`, `GET /v2/users/{username}` and related user calls | `AdditionalAttributes[]` | SPEC |
| `GET /v2/accounts/{accountCode}` | `Attributes[]` | SPEC |
| `GET /v2/promotion-details/{entityType}/{entityCode}` | `Promotions.PromotionList[].Attributes` | SPEC |
| `GET /v2/content-containers/{containerKey}/details` | `Attributes` | SPEC |
| `GET /v2/form-builders/{formCode}`, `GET /v2.1/forms/attribute-group/{widgetKey}` | `FormBuilderAttributeGroup.Groups[].Attributes` | SPEC |

The create and update bodies of users, accounts, stores and promotions do not take UDF values in the spec. Write them with `PUT /v2/global-entity-attributes` as a second call. `POST /v2/content-containers` requires `FamilyCode`.

## From the Custom API SDK

The SDK uses the Core v2 client package. Its interface for this area is `IGlobalAttributeEntitiesClient` with `PutGlobalEntityAttributes(GlobalAttributeRequestModel)`, `GetCodeByEntityCode(entityCode, entityType, localeCode, groupCode)`, `GetGlobalEntityAttributesByRecordId(...)` and bulk and family variants. Follow the SDK sample patterns (skill `sdk-conventions`).

## Events

A value save through the Admin, and an update of a field definition, dispatch a domain event with module `UserDefinedField` and name `Updated`. The payload carries the record id, the entity type, the family code and the changed attributes as JSON. The v2 write does not. The skill `sdk-events-and-webhooks` does not list this module; it needs the events feature flag. Whether the Admin webhook screen offers `UserDefinedField` is not verified (GAPS).
