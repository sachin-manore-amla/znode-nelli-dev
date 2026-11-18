# Attribute groups and attribute families

What this answers: how to create and manage groups and families, how attributes reach a product through them, display order, and exactly what can and cannot be changed, removed or deleted once they are in use.

## Where

| Object | Product path | Category path |
|---|---|---|
| Attribute Groups | `PIM > Product Attributes > Attribute Groups` | `PIM > Category Attributes > Attribute Groups` |
| Attribute Families | `PIM > Product Attributes > Attribute Families` | `PIM > Category Attributes > Attribute Families` |

Each page shows only its own kind. The product and category menus are separate permissions. Groups and families are global: no store, catalog, account or profile limits them. The API does not check roles, only the API credentials. (module guide, dev environment 2026-10-11/12, 85)

## Attribute groups

Create: `Add New`, enter `Group Code` (required; letters and digits, starting with a letter, up to 100 characters, unique per kind with letter case ignored), then add names on the `Locale` tab. The code is locked after save. A group needs a name in the default language to show in lists and pickers; if every name is empty the first active language gets the code as its name. Names: at most 100 characters, no comma.

Add attributes: save the group first, then on its attribute list click `ADD ATTRIBUTE`, tick attributes, `ADD`. Nothing ticked shows `Please select at least one record.`

| Rule | Detail |
|---|---|
| Attributes offered | only attributes of the same kind that are in no group, not system-defined, not personalizable, not Link type, and with a default-language name |
| One attribute, two groups | not possible from the screens |
| System-defined groups (green tick, for example Product Info, Product Settings, Shipping Settings, General Info, Descriptions) | can be renamed and take custom attributes; cannot be deleted or removed from a family |
| Hidden groups | Personalization, Custom Fields, Add-Ons, Associated Products are never shown in lists or pickers and still belong to families |
| Display Order column on the attribute list | the attribute's own order (1 to 999), shared by every group that attribute appears in |
| Remove an attribute from a group | allowed for custom attributes, one at a time, even when products hold values (values are kept). System attributes (for example SKU, Product Name) are refused: `Cannot delete system defined attributes.` |
| Delete a group | from the list only (row bin or `Tools > Delete`); there is no Delete on the edit page. Custom groups are deleted even when a family uses them: the group disappears from every family, its attributes and product values stay, and there is no undo. System-defined groups are refused. |
| Mixed delete | custom groups are deleted, the system one stays, message `Failed to delete some group because it is either system defined or is associated.` |

Reaching families: adding an attribute to a group copies it at once into every family that holds the group. A group in a family shows as a section (tab) on the product page of that family. A required attribute added to a group blocks saving of products of every family holding it until filled. (module guide, 85)

Messages: `Attribute Group Code is required.`; `Only alphanumeric characters are allowed and the code must start with a letter.`; `Group Code can not exceed 100 characters.`; `Attribute group already exists.` (shown after Save); `Locale can not be longer than 100 Characters.`

Behaviour to know: the live duplicate-code check on the form does not work on the build checked (it answers not-found), so the duplicate only shows after Save. The code of a group should never be changed through the API: features that look a group up by code (Shipping Settings, product settings, personalization, custom fields, add-ons, general info, descriptions) break.

## Attribute families

Create: `Add New`. A family must be **based on an existing family** (the field has no empty option). The base family's groups and attributes are copied, not linked. `Family Code`: starts with a letter, letters and digits, up to 100 in the Admin (API accepts up to 200); unique per kind (case and trailing spaces ignored); a product family and a category family may share a code. Message after save when duplicate: `PIM Attribute Family already exists.`

| Rule | Detail |
|---|---|
| Change code, kind or flags after create | Not possible. There is no family update route. Only labels and group/attribute content change. |
| Default families | `Default` (product) and `DefaultCategory` (category) are system-defined and default. There is no screen or API call to make another family the default. Both can be edited (labels, groups) but not deleted. |
| Labels (`Locale` tab) | One per active language. Saving replaces all labels, including those of inactive languages. A family with no label in the default language disappears from lists and drop-downs. Labels never reach the storefront. |
| Add groups | `Add Attribute Groups` offers custom, visible groups of the same kind not yet in the family and holding at least one attribute. The API adds anything, including duplicates. |
| Group display order | Pencil icon on the family page. 1 to 999 in the screen; sets tab order on the family page, product and category pages and the product import template. It is not used in publish or on the storefront. |
| Add attributes straight to a family | The `Add Attributes` control on the family page is empty for every role; the picker can only be reached by typed address or the API. Prefer adding attributes to groups. |
| Remove a group from a family | Delete right needed; system groups refused (`Cannot delete the Attribute Group because it is either system defined or associated.`). Nothing is written to products: the group disappears from the form, saved values are kept and still published. |
| Remove an attribute from a family | Write right; system attributes refused (`Cannot delete system defined attributes.`); values kept and still published. |
| Delete a family | Refused when any product or category still has a saved value under it: `Failed to delete the family as it may be system defined, set as the default family, or it may be in use.` Nothing is moved to Default. Unused families are deleted with their labels and assignments. |
| Family and product type | Not linked. Any family can be used with any product type. A configurable product needs a family with at least one `Is Configurable` attribute. |
| Change a product's family | Allowed on Edit Product for simple, grouped and bundle products (the KB says it is locked); locked for configurable products and on Copy Product. Save marks the product Draft. Values of fields the new family lacks are kept. |
| Import | There is no family import. Imports use an existing family chosen once per import (no family column in the file). |

Why a family shows fewer groups than it has: "not editable" groups (Personalization, Custom Fields, Add-Ons, Associated Products) are hidden on the family page but still belong to it and become product tabs.

Storefront reach: no storefront screen shows a family, group, group order or default mark. The published product carries no family or group. The family affects shoppers only through which attributes get published, and product page tabs come from fixed attributes and each attribute's own flags. (module guide, 85)

## Required order of work

1. Create the attribute (type and flags).
2. Create the group (if new) and add the attribute to it.
3. Create or open a family, add the group.
4. Create or edit products using that family; fill the values.
5. Publish (publish-and-search-effects.md).

An attribute not in a group of the product's family never appears on that product's form. (KB, 80)

## Knowledge Base versus product

| Topic | KB | Product | Wins |
|---|---|---|---|
| Family after first save | Cannot be changed | Can be changed for simple, grouped, bundle products | Product |
| Delete a group in use | Not stated | Allowed; group leaves families, values kept | Product |
| Delete a family | Deleting removes it | Refused if any product or category value exists under it | Product |
| Group code after save | Cannot be edited | Locked on screen; the API can change it | Product (do not do it) |

KB articles: https://support.znode.com/support/solutions/articles/43000756866-managing-product-attribute-groups, https://support.znode.com/support/solutions/articles/43000756867-managing-product-attribute-families, https://support.znode.com/support/solutions/articles/43000756862-product-attributes-groups-and-families-overview
