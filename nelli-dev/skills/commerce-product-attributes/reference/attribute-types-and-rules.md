# Attribute types, flags, validation and rules

What this answers: every product attribute type with its options, every flag with its exact Admin label and when it is shown, the validation messages, option values, and what can or cannot change once an attribute is in use.

## Where

`PIM > Product Attributes > Attributes`, then the add/edit page. Category attributes use `PIM > Category Attributes > Attributes` and the same page. The `Locale/Values` tab holds names per language and option values.

## Types

Eleven types, chosen on the page with `Attribute Type` (locked after the first save). (KB read in full, 80; product source, 90)

| Type | For | Type-specific settings | Notes |
|---|---|---|---|
| Text | one line of text | `Validation Rule`, `Regular Expression`, `Max Characters`; `Unique Value`; can be `Is Personalizable` | Validation Rule choices: Select (none), URL, Alphanumeric, Email. Picking one fills the regular expression, which you may overwrite. |
| Text Area | multi-line or rich text | `Max Characters`, `WYSIWYG Enabled` | When WYSIWYG is on the Max Characters box is hidden and cleared. |
| Number | numeric | `Allow Negatives`, `Allow Decimals`, `Min Number`, `Max Number` | Min and Max must respect the switches; Max must be greater than Min. Default value is validated. |
| Date | calendar date | `Min Date`, `Max Date` | Picked from a calendar, shown as year-month-day. |
| Yes/No | true / false | none | Default value is a Yes or No switch. |
| Simple Select | one option from a list | options on the `Locale/Values` tab; may be `Is Configurable` and `Is used for facets` | Options can have swatch image, swatch text or text. |
| Multi Select | several options | options; may be `Is used for facets` | Options can have swatches. Lazy loading of localized values. |
| Label | read-only caption/value for display and filtering; multiple values | options | No `Required` row. |
| File | document upload | `Allowed Extensions`, `Max File Size(MB)`, `Allow Multiple Files` | Extensions available: .Bin .Csv .Doc .Docx .Dwg .File .Gz .Pdf .Ppt .Rfa .Tar .Ttf .Txt .Xls .Xlsx .Zip. Video formats such as .mp4 are not in the list. |
| Image | image upload | `Allowed Extensions`, `Max File Size(MB)`, `Allow Multiple Files` | No `Required` row. |
| Link | associates other products with this product (related-product style) | none | Hides almost every other option; cannot be put in a group; hidden from required, configurable, personalizable, localizable, comparable, search and group settings. |

The per-type validation controls come from the platform's shared input-validation list for each type (the same list the media attribute screens use). The rows above for Number, Date, Text, Text Area, File and Image were verified for media attributes on a development environment (2026-10-07) and read in the product's Admin source for products; `Unique Value` is visible on product Text attributes but was a hidden setting for media. (module guide, 85; product source, 85)

## Behaviour flags (exact Admin labels)

| Label | Shown for | Effect |
|---|---|---|
| `Required` | every type except Label, Link and Image | The product edit page refuses to save until filled. Locked on for `Is Active`, `SKU`, `Product Name` and `Shipping Cost`. Adding a required attribute to a family makes imports fail for rows without it. |
| `Is Configurable` | Simple Select only | Lets the attribute define configurable-product variants. Hidden when `Is Personalizable` is on. |
| `Is Personalizable` | Text only | Value is entered by the shopper on the product page (personalization). Cannot belong to a group; managed on the product's Personalization tab. Switches off search and HTML options. |
| `Is localizable` | all but Link | The value can differ by language. |
| `Is Show On Grid` | all but Link | Adds the attribute as a column on the PIM product list. |
| `Attribute Group` | all but Link and personalizable | The group the attribute is put in on creation. |
| `Is Comparable` | all but Link | Adds the attribute to the compare options in the Webstore. Help text: `Select 'Yes' to add this attribute to the list of compare options in the webstore product comparison.` |
| `Is used in Search` | all but Link, personalizable | Adds the attribute to the search options. Also needs the attribute in a search profile and that profile published. See publish-and-search-effects.md. |
| `Is used for facets` | Simple Select, Multi Select | Adds the attribute to the facet (filter) options in the Webstore. |
| `Default Value` | Text, Label, Number, Date, Yes/No, Simple/Multi Select | Value used when a product has none. Select options have an `IsDefault` row switch. |
| `Help Description` | all but Link | Text shown to Admin users when entering the product. |
| `Display Order` | all | Whole number, required; 1 to 999 in the Admin. The order belongs to the attribute, not to the group: changing it changes it in every group and family. Equal numbers allowed. |
| `Unique Value` | Text | Value must be unique across products. `Copy Product` blanks unique values. |
| Swatch: `Swatch Image`, `Swatch Text`, `Text` | option values of Simple Select, Multi Select, Label, Text | Priority on display: Swatch Image, then Swatch Text, then Text. |
| `Allow Multiple Files?` | File, Image | `Select 'Yes' to associate multiple files while creating products. (Ex. Gallery Images)` |

An attribute flagged "HTML tags" is carried in the published attribute as `IsHtmlTags`; no Admin label for it was found on the attribute page of this build (see gaps).

## Option (default value) rules

- Open the attribute, tab `Locale/Values`, click `Add New Value`. Enter a code (letters and digits only, unique in the attribute), a display value per language (at least one), optionally swatch image/text and `Default Value`, then click the row's own Save icon, then Save the attribute. Rows not saved with the row icon are not stored.
- Messages: `Please save attribute before Saving its default values.` (attribute not yet saved); `Please enter at least one default value.`; `Default value code cannot be blank`; `Only alphanumeric characters are allowed.`; and from the API `Attribute code with same value is already exists`. (product source, 90)
- Option names must not contain a comma and at most 100 characters per language (the same locale checks as groups). (product source, 85)
- Delete of a system-defined option is refused: `Failed to delete default attribute values as they are system defined.`

## Messages on the attribute page

| Message | When |
|---|---|
| `Please enter an Attribute Code.` | Code empty |
| `Only alphanumeric characters are allowed and the code must start with a letter.` | Code format |
| `Attribute Code can not exceed 100 characters.` | Over 100 |
| `Please enter the Display Order.` / `Only positive integers are allowed.` | Display Order empty or not a positive whole number |
| `Attribute already exists.` | API create with a code already used (same kind) |
| `Failed to delete some PIM attributes because they are either system defined or are associated.` | API delete of system or associated attributes |
| `Failed to delete some attribute because it is either system defined or is associated.` | Admin delete result |
| `System-defined attribute '{code}' is always required.` | API update trying to make a system attribute optional |

## What cannot change or be removed

| Action | Allowed? | Detail |
|---|---|---|
| Change Code or Attribute Type after the first save | No | Fields are disabled on edit. |
| Make `Is Active`, `SKU`, `Product Name`, `Shipping Cost` not required | No | Locked. |
| Delete a system-defined attribute | No | System attributes also cannot be removed from a group or family (`Cannot delete system defined attributes.`). |
| Delete an attribute assigned to products | No | KB statement; the delete procedure refuses "associated" attributes (what counts as associated is not fully documented, see gaps). |
| Delete a custom attribute that is only in a group or family | Not verified | Removal from a group or family is allowed (see below); whether the attribute delete is refused while it is still in a group is not documented. |
| Remove an attribute from a group or family with product values | Yes | Values are kept, hidden on the product form, and still published. |
| Change the type of an attribute used by variants | No | Type is locked. |

Attribute definition changes do not need a store restart. They reach the storefront only after publish (publish-and-search-effects.md).
