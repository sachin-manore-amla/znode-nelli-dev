# Groups, families and how an entity picks them
How attribute groups and families are created and linked, how a record ends up with a set of groups, the screens and API calls, and the rules and messages.
Read it before you build a new field set for an entity type.

## Menu paths (Admin)

| Screen | Path | Notes |
|---|---|---|
| Attributes (the fields) | `Dev Center > User-defined Fields > Attributes` | List with an entity filter (`Select Entity`) and an `Add` button |
| Attribute Groups | `Dev Center > User-defined Fields > Attribute Groups` | KB: Admin > Dev Center > User-Defined Fields > Attribute Groups |
| Attribute Families | `Dev Center > User-defined Fields > Attribute Families` | Menu item exists in the product. Whether it is visible depends on the menu rights of the role |
| Entity Attributes | `Dev Center > User-defined Fields > Entity Attributes` | Page title `Manage - Entity Attributes`, field `Entity Name` |

The permission for these screens is held on the `User-defined Fields` menu. Only the Admin role has it out of the box (module guide, 85).

## Attribute group

| Admin label | API field | Rule |
|---|---|---|
| Entity Type | `EntityName` | Required. The group can only hold attributes of this entity type (API: `The entity of the attribute does not match the entity of the group.`, HTTP 400) |
| Group Code | `GroupCode` | Required, unique, letters and digits, must start with a letter. Admin max 100 characters, API max 200. Cannot be changed after creation |
| Group name per language | `AttributeGroupLocales[]` (`LocaleCode`, `AttributeGroupName`, `Description`) | Name is required (max 300). Only groups that have a name in the default language show in some lists |

Steps (Admin): `Attribute Groups > Add`, choose Entity Type, enter Group Code and the name, Save. Then open the group and:
1. `Associate` unassigned attributes of that entity type to the group.
2. Edit the display order of each attribute inside the group (1 to 999).
3. Remove an attribute from the group.
Delete: the delete icon on the grid row and confirm.

Rules and messages:

| Case | Text |
|---|---|
| Group code exists | `Global Attribute Group already exists.` |
| Delete a group that is system-defined or still in use | `Failed to delete some groups as they may be system defined or because they are associated.` |
| Remove attribute from group fails | `Failed to delete an Attribute Group Mapper.` |
| Group code missing (Admin form) | `Attribute group code is required.` |
| Code too long (Admin form) | `Group Code can not exceed 100 characters.` |

Rule seen in the v2 API (source): an attribute can belong to one group only. A second assignment answers `The provided attribute code is already associted with a group.` (409, the word is spelled as in the product).

## Attribute family

| Admin label | API field | Rule |
|---|---|---|
| Entity Type | `GlobalEntityName` | Required |
| Family Code | `FamilyCode` | Required, unique, letters and digits, starts with a letter. Admin max 100, API max 200. Cannot change |
| Family name per language | `AttributeFamilyName`, `AttributeFamilyLocales[]` | Name required, max 300 |

Steps: `Attribute Families > Add`, then on the family assign groups (`Assign`), set each group's display order (whole number, `Only positive integers are allowed.`), unassign groups.

| Case | Text |
|---|---|
| Family code exists | Admin: `Global Attribute Group already exists.` (the Admin reuses the group text). API v2: `Global attribute family already exists.` |
| Delete a family that still has groups | `Failed to delete, please unassigned attribute groups from family.` |
| Family code unknown | `Invalid Family Code` |
| Group not in the family (display order call) | `The group '<group>' is not associated with the family '<family>'.` |

## How a record gets its groups (what the product does)

There are two links, and both exist in the product:
1. Entity to groups: the `Entity Attributes` screen (`Entity Name` drop-down, assign or unassign groups, edit group display order in the pop-up `Attribute Group - Edit Display order`). Messages: `Assigned successfully.`, `Unassigned successfully.`, `Please select at least one record.`. API: list assigned and unassigned groups of an entity, associate, unassociate.
2. Family to groups, and entity (or record) to family.

How the entity picks its family depends on the entity type:

| Entity type | Family used | Source |
|---|---|---|
| Store, User, Account, Brand, Promotion, Voucher, Order and every other entity except the two below | One family per entity type, created with the product (for the Global Setting entity the family is `GlobalSetting`). All records of the type use it | Product source (90): these entities are marked "family unique" |
| Content Containers | The family you choose per container. The create call requires `FamilyCode`. The family decides the field set of that container's variants | Product source and API reference (90) |
| Form Builder | No family. Groups or single attributes are attached directly to the form | Product source (90) |

For a record screen the Admin reads the groups of the record's family (ordered by the group's display order in the family) and shows one tab or section per group, with fields ordered by the attribute display order.

Verified behaviour to remember:
- Unassigning a group from a family or an entity is checked by the product against saved values of that group's fields, and the unassign can be refused (the error text is `Failed to unassociate group from entity.`). The exact condition was read from a code comment only (inference, below 50 confidence): expect the refusal when records already hold values for the group's fields.
- For the Promotion entity, groups can be tied to a promotion type. A promotion record shows the groups with no type plus the groups of its own type (source). The 10.13.0.0 release notes describe an `ALL` option that makes attributes and groups available to every promotion type and say the Admin loads global and type-specific groups by the chosen discount type (KB, 80). Treat the promotion-type grouping as new behaviour and test it on your version.

Not verified (see GAPS): whether assigning a group on `Entity Attributes` alone is enough for it to show on a record screen, or whether the entity's family must also contain it. Do both steps for a new group unless the environment shows otherwise.

## Recommended order to add a field set

1. Attributes: create the field(s), then their locale labels and, for selects, their options.
2. Attribute Groups: create the group for the same entity type, associate the fields.
3. Attribute Families: add the group to the entity's family (for a container, create or edit the family).
4. Entity Attributes: assign the group to the entity type.
5. Open a record of the entity: the group appears as a tab or section.

## API calls (Core v2, summary; full list in api-and-values.md)

Groups: `GET /v2/global-attribute-groups`, `GET /v2/global-attribute-groups/{groupCode}`, `POST /v2/global-attribute-groups`, `PUT /v2/global-attribute-groups`, `DELETE /v2/global-attribute-groups-bulk/{groupCodes}`, associate and remove attributes, update display order.
Families: `GET /v2/global-attribute-families`, `GET /v2/global-attribute-families/{familyCode}`, `POST /v2/create-attribute-families`, `PUT /v2/update-attribute-families`, `DELETE /v2/delete-attribute-families/{familyCode}`, assign and unassign groups, update group display order.
Entity link: `GET /v2/global-entities`, `GET /v2/global-entity-attributes/{entityCode}/assigned-groups`, `.../unassigned-groups`, `POST .../associate-groups/{groupCodes}`, `PUT .../unassociate-groups/{groupCode}`.
