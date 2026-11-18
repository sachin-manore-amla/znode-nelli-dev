# Attribute types, options and validation rules
Every attribute type a UDF can have, the options each type offers, the flags common to all, and the rules and messages on create.
Use it to choose a type and to explain why a field behaves as it does.

## Common settings (Admin: `Dev Center > User-defined Fields > Attributes > Add`)

| Admin label | API field | Meaning | Rule |
|---|---|---|---|
| Entity Type | `EntityName` | The entity the field belongs to | Required. Choose from the list. Read-only after the first save. Spaces matter in the API: use the name as the list shows it, for example `Price List` |
| Attribute Type | `AttributeTypeName` | The data type | Read-only after the first save |
| Code | `AttributeCode` | Unique key used by the API | Required. Unique across all entity types (case-insensitive). Read-only after the first save. Admin: letters and digits only, must start with a letter, at most 100 characters. API v2: at most 300 characters and no pattern check, so keep to the Admin rule |
| Required | `IsRequired` | The value must be filled when saving the record in Admin | Default is true (Yes) in both the API and the Admin form. Set it to No for optional data. Not shown for the Link type |
| Is Localizable | `IsLocalizable` | One value per language | Default in the API: true |
| Validation rules | `ValidationRule[]` | Per type, see below | Rule names must exist for the type |
| Default Value | `AttributeDefaultValue` | Value pre-filled for Number, Date and Yes/No types | Max 12 characters for Number in the form. For select types, defaults are separate rows (see below) |
| Help Description | `HelpDescription` | Text shown as help on the entity screen | Free text. Admin help text: "Add a help description for the attribute. It will help clarify the attribute." |
| Display Order | `DisplayOrder` | Position of the field inside its group | Whole number 1 to 999. API default 999 |
| Locale labels | `Locales[]` (separate call) | The label shown for each language (`AttributeName`, `Description`) | At least one label is needed. Label max 300 characters |

Evidence: Admin views and view models, API request models (verified, 90).

## Types available

The Admin list of types is the PIM list without `Link`. That gives ten types for UDFs:
`Text`, `Text Area`, `Number`, `Date`, `Yes/No`, `Simple Select`, `Multi Select`, `Label`, `File`, `Image`.

The API does not filter the type name. It accepts the name of any attribute type that exists, including `Link`, `Video` and `Audio`. Treat those three as unsupported for UDFs (the Admin never offers them and their behaviour on entity screens is not verified).

| Type | Stores | Options in Admin | Value rules applied by the Admin screen |
|---|---|---|---|
| Text | One line | `Validation Rule` (list: `Alphanumeric`, `Url`, `Email`, or custom `Regular Expression`), `Max Characters`, `Unique Value` (Yes/No) | Pattern, maximum length. `Unique Value` runs a duplicate check before save (see known-behaviours.md) |
| Text Area | Multi-line text | `Max Characters`, WYSIWYG toggle | Maximum length. With WYSIWYG on, the value is HTML |
| Number | A number | `Allow Negative`, `Allow Decimals`, `Min Number`, `Max Number`, `Default Value` | Range and sign checks |
| Date | A date | `Min Date`, `Max Date`, `Default Value` | `Minimum date can not be greater than Maximum date.` when the two conflict |
| Yes/No | Boolean | `Default Value` (Yes or No) | None |
| Simple Select | One option | A list of options (default values), see below | Value must be one of the option codes |
| Multi Select | Several options, stored as a comma-separated list of option codes | Same as Simple Select | Every value must be an option code |
| Label | Nothing entered. Shows its default text | Default text | Read-only on the entity screen. Use it to show fixed instructions inside a tab |
| File | One or more files (media library) | `Extensions` (multi-select), `Max File Size`, `Allow Multiple Files` | File type and size |
| Image | One or more images | `Extensions` (`.jpg .png .gif .jpeg .ico .svg`), `Max File Size`, `Allow Multiple Files` | Image type and size |

Option lists seen in the product (verified in the product source):
- Text `Validation Rule`: `Alphanumeric`, `Url`, `Email`. The custom case uses the `Regular Expression` rule.
- File `Extensions` list: `.pdf .doc .docx .ppt .xls .xlsx .csv .txt .zip .ttf` plus video and audio extensions merged in for the File type (`.mp4 .webm .ogv .mp3 .wav .wma .3ga .aif .mid .flac .aac`). The existing `commerce-product-attributes` note says video is not allowed for PIM File attributes. The product code merges the video and audio extensions into the File list for UDFs and PIM alike, so the two disagree. The product source wins; confirm on the environment before promising video upload (GAPS item).
- API names of the rules (used in `ValidationRule[]`): `InputValidationName` is the rule family, for example `ValidationRule`, `RegularExpression`, `MaxCharacters`, `UniqueValue`, `MinDate`, `MaxDate`, `MaxFileSize`, `Extensions`, `IsAllowMultiUpload`, `AllowNegative`, `AllowDecimals`, `MinNumber`, `MaxNumber`, `WYSIWYGEnabledProperty`. `InputValidationRuleName` is the chosen rule inside the family (for example `Email`). `Name` carries the typed value (for example the regex or the number). Read the allowed set for a type with `GET /v2/input-validations/{typeName}/{attributeCode}` (source only, not in the local spec copy).

## Select types: options (default values)

- Create the attribute first, then add its options. The Admin blocks adding options before the attribute is saved: `Please save attribute before Saving its default values.`
- A new Simple Select or Multi Select attribute is created inactive. It becomes active when its first option is saved.
- Each option row has: `Code` (the stored value), `Display Order`, `Is Default`, a label per language, and, for swatches, the swatch content.
- Option `Code`: letters and digits only (`Only alphanumeric characters are allowed.`), at most 100 characters in the API, not blank (`Default value code cannot be blank`), unique inside the attribute (`Code value already exists.`).
- At least one label is needed (`Please enter at least one default value.`). A comma is not allowed in a label (`Comma (,) is not allowed.`, 100 characters at most per label field in the form).
- Display Order of an option: `Display order must be from 1-999`.
- Swatches (radio next to the grid): `Swatch Image`, `Swatch Text` or `Text`. A swatch image is a media file. A swatch text is a colour or text. Missing swatch: `Swatch is required.` The API fields are `IsSwatch` and `SwatchText`.
- Deleting an option that records already use is refused: `Failed to delete default attribute values because is is associated.` System-defined options cannot be deleted: `Failed to delete default Attribute values as they are system defined.`

## Errors on create and delete (exact text)

| When | Text | API status |
|---|---|---|
| Code already used (Admin) | `This code already exists` / on the field: `Attribute Code Already exist.` | form message |
| Code already used (API v2) | `Attribute already exists.` | 409 |
| Entity name not found | `The provided EntityName is invalid.` | 404 (v2), `Invalid Global Entity` in Admin |
| Attribute type name not found | `The provided AttributeTypeName is invalid.` | 404 |
| Validation rule name or rule value not found | `The provided InputValidationName is invalid.` / `The provided InputValidationRuleName is invalid.` | 404 |
| Missing code (Admin form) | `Please enter an Attribute Code.` | form |
| Code pattern (Admin form) | `Only alphanumeric characters are allowed and the code must start with a letter.` | form |
| Code too long (Admin form) | `Attribute Code can not exceed 100 characters.` | form |
| Display order out of range | `Display order should be between 1 and 999` | form; API: `Display order should be between 1 and 999.` |
| Delete: field in a group, used, or system-defined | `Failed to delete some Global Attribute as they may be system defined or associated.` (Admin shows `Failed to delete attributes because they are associated.`) | 404 or failure |
| Delete by code, code unknown | `The provided AttributeCode <code> is invalid.` | 404 |

## What you cannot change after creation

Entity type, attribute type and code are fixed. To change one, create a new field, move the data yourself, and delete the old field. Required, Localizable, labels, help, display order and validation rules can be edited in Admin. There is no v2 operation to edit the field definition (see api-and-values.md).
