# Known behaviours and Knowledge Base differences

What this answers: behaviours that surprise people (stated neutrally with the source), version notes, and where the Knowledge Base differs from the product. The product, as observed, wins.

## Behaviours to know

| Behaviour | Detail | Source |
|---|---|---|
| Removing is not blocked by use | Removing an attribute from a group or family, or a group from a family, never checks product values. The field disappears from the product form on next open; values stay in the data and are still published. | module guide, 85 |
| Deleting a group in use is allowed | The group disappears from every family; attributes and values stay. No undo. | module guide, 85 |
| Family cannot be deleted while used | One saved value (any state) under the family blocks the delete. | module guide, 85 |
| Display order is per attribute | Changing it in one group changes every group and family. | module guide, 85 |
| Label locale rows are replaced on save | Saving group or family locale names replaces all of them; names for languages no longer active are lost. A group or family with no default-language name vanishes from lists. | module guide, 85 |
| Add Attributes on a family | The control is empty; add attributes through groups. | module guide, 85 |
| Option rows need their own save | On the attribute `Locale/Values` tab, unsaved rows are not stored when the page is saved. | KB, 80 |
| Duplicate-code check on group form | The live check answers not-found on the build checked; the duplicate shows after Save. | module guide, 85 |
| API skips screen rules | Code format and lock, display order range, built-in and hidden flags and others are enforced only by the Admin screens. | module guide, 85 |
| Saves not transactional | Group and family saves in the API can leave partial results. | module guide, 85 |
| Custom fields and the PDP | Custom fields can fail to reach the product page after publish on the released code checked; only the default language Value shows. | module guide, 85 |
| Custom fields accept HTML | Stored as typed and shown as HTML. | module guide, 85 |
| Custom field code can break publish | A code of 101 to 299 characters is accepted by the Admin and breaks the publish of its batch. | module guide, from source, 85 |
| Link type is special | No group, no flags; it associates products. | product source, 90 |
| Personalizable attributes | Cannot be in a group; managed on the Personalization tab. A removed personalizable attribute with a value still returns with the product. | KB, product source |
| Facets without a search profile mapping | With no mapping and two or more attributes in the default index setting, no search or facet copies were made on the build checked. | module guide, 85 |
| File extension set | Fixed list; no video formats. | KB, product source |

## Version notes (release notes read)

| Version | Date | Change |
|---|---|---|
| 10.5.0.0 | | Custom field code may not equal any attribute code (module guide; release note not re-read) |
| 10.8.0.0 | 4 Mar 2026 | Duplicate PIM attribute rows in Admin views removed; Commerce APIs can return specific custom product attributes; special characters in attribute data preserved across APIs; configurable variants on grid sort by attributes |
| 10.13.0.1 | 29 Jul 2026 | New `GET /v2/pim-attribute-groups` read, with family ids per group |
| 10.14.0.4 | 23 Sep 2026 | Fixed "The results could not be loaded." error on Select and Multi Select attributes after a product family change; PIM list and get responses include full attribute configuration |
| 10.6.2.0 | 23 Jan 2026 | Release notes carry no attribute, family, group or facet items (overrides introduced) |

## Knowledge Base versus product

| Topic | KB says | Product | Wins |
|---|---|---|---|
| Family after first save | "Cannot be changed" (Configuring General Product Information) | Can be changed for simple, grouped, bundle on Edit Product; locked for configurable and Copy | Product |
| Product type after first save | Locked | Locked | Same |
| Group code after save | Cannot be edited | Locked on screen; API can change it | Product |
| Attributes assigned to products cannot be deleted | Yes | Delete refuses system or "associated" attributes; exact definition of associated not documented | Treat as KB until verified |
| "Is Shown on Grid" | Two labels in one article | Admin label is `Is Show On Grid` | Product |
| "Is Used In Search" | Capitalised so | Admin label is `Is used in Search` | Product |
| Custom field on the product page | Appears in Additional Information after publish | Can be missing on the released code | Product |
| Custom field code rule | Unique, not an attribute code | Also checked against category attributes; API does not enforce format | Product |
| `Is Configurable`, `Use For Facets`, import/export of attributes | Not stated in the attribute article | Admin shows `Is Configurable` (Simple Select only) and `Is used for facets` (select types) | Product |
| Required lock | Is Active, SKU, Product Name, Shipping Cost | Same for the Admin; API refuses optional on system attributes | Same |

KB articles read: Managing Product Attributes (43000756863), Managing Product Attribute Groups (43000756866), Managing Product Attribute Families (43000756867), Product Attributes, Groups, and Families Overview (43000756862), Configuring General Product Information (43000757014), Adding a Custom Field to a Product (43000757004), What Requires Publishing (43000757211), Managing PIM Index (43000757077), Defining the Product Data Model - Best Practice (43000757186), Dynamic Schema - Product Attributes, Groups, and Families (43000757204), all at https://support.znode.com/support/solutions/articles/<id>.
