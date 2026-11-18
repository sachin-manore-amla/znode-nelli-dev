# Customization decisions for user-defined fields
Worked requirement examples with a verdict (Supported, Customizable, Restricted, Needs platform change) and the steps.
Use it in the Architecture phase, together with `sdk-capability-registry`.

Verdict meanings: Supported = configuration only. Customizable = needs SDK or Webstore code. Restricted = only possible by a method the customer must approve. Needs platform change = request to Znode.

| Requirement | Verdict | How |
|---|---|---|
| PO approval code on the account | Supported | Account UDF, `Text`, `Required` as needed, `Alphanumeric` rule. Add to a group, family and `Entity Attributes`, then edit on `Customers > Accounts > Manage Account > Additional Attributes`. Read through the account response as `Attributes`. To use it in approval logic or checkout, code is needed (Customizable). The product does not read it |
| Delivery instruction per user | Supported to store, Customizable to show | User UDF `Text Area` with `Max Characters`. Admin edits it on the user's `Additional Attributes`. Showing or editing it in the Webstore account area or checkout needs Webstore source work (labelled source customization). Write it from your code with `PUT /v2/global-entity-attributes` |
| Extra attribute on the store shown in the footer | Customizable | Store UDF `Text`, one value per store. The Webstore receives it in the portal data. Render it in a footer component reading it by `AttributeCode`. Publish the store and clear the cache, then test. Do not edit the product's own system fields |
| Extra fields on a custom form | Supported | Form Builder entity: create the fields (Text, Text Area, Simple Select, Yes/No, Date and others), group them, attach groups or fields to the form (`CMS > Manage Forms > Edit`). The form widget renders them. Add a required Email Address field if the acknowledgement email is used. Needs no publish for form changes, publish the page that holds the widget |
| A field on a promotion | Supported (storage) | Promotion UDF. Edit on the promotion `Additional Attributes`. Promotion list export can include it. Using it to change discount results is Customizable and goes through the promotion extensibility route (skill `sdk-method-overrides` and the Promotion Extensibility Developer Guide). Check the 10.13.0.0 type-specific groups on your version |
| Extra data on a voucher | Supported | Voucher UDF, edit on the voucher screen, export and import support the columns |
| Extra data on an order, quote or return | Supported to store | UDF sections exist on the manage screens. Copy behaviour between quote and order is not verified. Test it |
| A custom content block with typed fields | Supported | Content Container with its own family and groups. Theme code decides display. KB: a developer updates the theme to show it |
| Something per product (colour, material, spec) | Use PIM | Product attributes, skill `commerce-product-attributes`. UDFs do not exist for products |
| One free note on one product | Use PIM | Product custom field |
| Structured reference data, lists of rows, lookups | Use Custom Table | Skill `sdk-custom-tables`. A UDF holds one value per record |
| A field the customer wants searched or filtered on the storefront | Use PIM attributes, or needs platform change | UDFs are not indexed for search |
| Per-store value for a B Store | Supported | B Store entity UDF, saved against the B Store (refreshes the portal cache) |
| A new entity type (for example UDFs on shipping rules or on carts) | Needs platform change | Entity types are created by Znode. Raise a Platform Change Request |
| Edit a field's type or entity after creation | Needs platform change or rebuild | Create a new field, migrate values with the API, delete the old field |
| Make the product behave differently because of a UDF value | Customizable | SDK endpoint, event consumer (`UserDefinedField` Updated from Admin saves) or method override. Never change core services |
| Sanitise or validate UDF values server-side | Customizable | The API does not check Required, pattern or length on write. Validate in your own endpoint before calling `PUT /v2/global-entity-attributes` |
| Clear a UDF value by API | Restricted until verified | The v2 write rejects blank values. Use the Admin, or confirm a supported way with Znode |
| Direct database writes to UDF values | Restricted | Allowed only for customer-owned data and with the developer's approval. Cache and events would be bypassed |

## Decision steps

1. Is the data about one of the supported entity types? If not (product, category, media, cart): use PIM or a Custom Table.
2. Is it one value per record, not rows? If rows: Custom Table.
3. Does the Admin user type it, or does your code write it? Both work.
4. Does a shopper need to see or enter it? Only Forms render dynamically. Everything else needs Webstore source work.
5. Does product behaviour need to change? Then it is Customizable at best. Name the extension point.
6. State the publish and cache steps in the proposal.
