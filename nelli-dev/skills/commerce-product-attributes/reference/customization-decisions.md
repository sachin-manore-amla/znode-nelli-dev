# Customization decisions for product data

What this answers: for a requirement about extra product data, which mechanism to use (attribute, custom field, override, Custom Table, custom endpoint) and the verdict.

## Choosing the mechanism

| Question | If yes |
|---|---|
| Is it a product-level fact shared by many products (colour, material, spec)? | Product attribute in a group and family. Supported. |
| Does shoppers' filtering, comparing or searching use it? | Attribute with `Is used for facets` / `Is Comparable` / `Is used in Search`. Supported. |
| Is it a variant axis (size, colour)? | Simple Select attribute with `Is Configurable`, configurable product. Supported. |
| Is it a one-off note on one or two products? | Product custom field. Supported, with the storefront caveat. |
| Is it product name, short or long description or SKU that differs per store, account or locale? | Product Information Overrides (`commerce-product-overrides`). |
| Is it a value per customer, per order or per customer and product? | Custom Table plus custom endpoint. Customizable. |
| Is it reference data of your own (size charts, warranty tables, supplier info) looked up by SKU? | Custom Table keyed by SKU plus custom endpoint, or an attribute if it is a single value. |
| Does it change price, stock or tax? | Price lists, inventory, tax classes, or the method-override hook; not attributes. |

## Requirement examples and verdicts

| Requirement | Verdict | Reason and answer |
|---|---|---|
| Add a new product field shown on the PDP (for example "Warranty") | Supported for data, Customizable for display | Create an attribute (Text or Text Area), add it to a group in the product family, fill values, publish. The PDP renders only three fixed attributes as tabs plus theme templates, so showing it as a tab or panel needs a Webstore change (source customization). A product custom field shows under `Additional Information` but can be missing after publish on the released code. |
| Search or filter by a custom attribute | Supported | Use Simple or Multi Select, set `Is used for facets` and `Is used in Search`, add to the search profile, run a full catalog publish. Verify facets after the first publish. |
| Free-text attribute searchable | Supported with limits | `Is used in Search` on a Text attribute plus search profile; free text is a poor facet. |
| Different product name per store | Supported | Product Information Overrides; the stock Webstore does not show them (source customization). |
| Store a value per customer per product | Customizable | A Custom Table keyed by customer and SKU; a custom endpoint enforcing ownership. Not an attribute (attributes hold one value per product, not per customer). |
| Per-account product notes | Customizable | Custom Table keyed by account and SKU. |
| Add a new attribute type (colour picker, rich JSON) | Needs platform change | The eleven types are fixed. Model the value as Text or Text Area, or a Custom Table. |
| Add a new validation rule type | Needs platform change | Rule sets come from the platform. Use a regular expression on Text, or validate in a custom endpoint. |
| Change what the product form shows per user role | Needs platform change | Families are global and not role-aware. Create more families and assign by product. |
| Enforce an attribute value rule on import | Customizable | A custom import template with the family; validate before import; the API is not strict. |
| Add attributes to products automatically from an ERP | Customizable | ERP touchpoint or a script using product import (`config-import-export`) or the v1 APIs; imports fire no events. |
| Attribute values per store | Restricted | Attributes are global per product. Use separate catalogs or overrides for text, or a Custom Table. |
| Change an attribute's type after it has data | Needs platform change | Type is locked; create a new attribute and migrate values by import. |
| Remove an attribute used by variants | Restricted | The stored configurable choice remains and still feeds publishing; remove variant associations first and confirm in a test environment. |
| Show attributes grouped on the PDP as the Admin groups them | Customizable (source) | Groups are not in the published product; the Webstore would need the group mapping from a custom source (for example a Custom Table of attribute-to-section). |
| Publish attribute changes without a full publish | Needs platform change | Attribute definition edits need a full catalog publish (inference); schedule it. |

## Where to put the extra code

- Display logic on the PDP: Webstore component, labelled "customization of source, not a supported extension point".
- Validation on write: custom endpoint in front of the API (the v1 attribute APIs check no role and skip screen rules).
- Data that is not a product attribute: Custom Table (`sdk-custom-tables`) with the Dynamic Data Table API; define unique fields and lengths there.
- Do not recommend direct database access, and do not edit attribute data in the database.
