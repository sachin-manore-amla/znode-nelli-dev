# Spec.yml
What this answers: the spec file that defines a plugin and its Admin configuration form.
Source: SDK template spec files and platform spec reader (95); KB (80, which states field names are "not stated").

## Header
`specFileVersion` (1.0.0), `name`, `type` (`Shipping`, `Tax`, `Payment`, `PaymentInternal`), `version`, `license`, `preRelease` (true shows Pre Release), `author`, `description`; optional `isActive`, `isApproved`, `tablePermission`, `pluginAttributes`, `options`. A signing key line exists in the shipped templates: keep it out of source control copies you share; its use is not documented.
`name` matters at runtime: the shipping manager uses it as the route segment (`/v1/<name>/calculate`; the FedEx spec name is `Fedex` and its routes are `/v1/fedex/...`). The tax template spec header says `type: "Shipping"`: change it to `Tax` in your copy.

## Fields
```yaml
configurationRootFieldKeys: ["Root", "GlobalConfiguration"]
allFields:
  - key: "UniqueName"        # unique within the plugin
    label: "Configuration Code"
    type: "text"             # seen: text, number, checkbox, dropdown
    defaultValue: ""
    isRequired: true
    varyBy: store            # store = per configuration set; global = plugin-wide
    helpText: "Configuration set code."
    value: ""
    options:                 # dropdown only
    - { key: "TotalCartWeight", value: "TotalCartWeight", displayName: "Total Cart Weight" }
templateCategories:
  - key: "Root"
    code: "Root"
    displayName: "Root"
    type: "Root"             # Root = configuration set form, GlobalConfiguration = Global tab
    childrenFields: ["UniqueName", "DisplayName", "DisplayOrder"]
```
Model fields also supported by the platform: `code`, `style`, `behavior`, `isHidden`; categories support `sectionField`, `childrenCategories`, `childrenCategorySelectionField`/`Behavior` (grouped sections).
Standard shipping set fields: Configuration Code, Display Name, Display Order. Shipping global field example: "Enable Promotions And Coupons For This Shipping Method" (checkbox, default true): lets promotions discount that method's price.

## Rules
- Only fields in the spec are shown in Admin; validate completeness before coding.
- Keys must match the names your service reads from the configuration set.
- Secrets are ordinary text fields: no masking type was found in the templates (Vertex gained a masked field in 10.10; the syntax is not in the sources). Treat all spec values as secrets in transit (`hosting-and-security.md`).
- Sample JSON versions of the same form ship beside the spec (`SamplePluginTemplate.json`, `SampleGlobalConfiguration.json`).
