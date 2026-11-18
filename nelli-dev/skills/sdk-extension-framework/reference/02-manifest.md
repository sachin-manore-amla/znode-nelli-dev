# extension.manifest.json
Answers: the manifest fields, what the platform validates, and what `supportedContracts` does.
Source: sample manifests in the Custom API SDK (90) and the extension loader in the product source (90).

## Sample (Commerce Connector processor)
```json
{
  "name": "Custom.Libraries.DataExchange",
  "version": "1.0.0",
  "minPlatformVersion": "10.0.0",
  "maxPlatformVersion": "10.99.99",
  "supportedContracts": ["IBaseProcessor"],
  "description": "Custom processor for Commerce Connector Multi Step execution steps.",
  "vendor": "Znode"
}
```
The promotion sample uses `"supportedContracts": ["CartPromotionTypeBase"]`. Place the file next to the extension assembly and copy it to the output (`CopyToOutputDirectory`).

## Fields
| Field | Required | Meaning |
|---|---|---|
| `name` | Yes | Extension name shown in Admin. Upload also accepts `ExtensionName` |
| `version` | Yes | Semantic version (`1.2.0`); must parse as a version. Each version is stored separately and cannot be uploaded twice |
| `minPlatformVersion` | No, default `0.0.0` | Lowest Znode version (inclusive). Upload form calls it `MinimumPlatformVersion` |
| `maxPlatformVersion` | No, default `99.99.99` | Highest version (inclusive) |
| `supportedContracts` | No | Names of the contract types the extension implements, **for display in Admin and optional pre-load compatibility checks**. It is a label, not a registration: the loader finds your classes by their attribute or interface, not from this list |
| `description` | No | Shown in the Admin dashboard |
| `vendor` | No | Author |

## Validation rules (product source)
- No manifest file: validation is skipped and the extension still loads (older extensions).
- Malformed JSON: load rejected: `Cannot parse 'extension.manifest.json': ...`.
- Missing `name`: rejected: `'extension.manifest.json' is missing required field 'name'.` Missing `version`: same message with `'version'`.
- Running platform outside the range: rejected: `Extension '<name>' v<version> requires platform [<min> - <max>], but the running platform is v<platform>. Load rejected.`
- Versioned upload through Admin additionally requires the manifest, a parseable version, at least one `.dll`, and no duplicate version: `Version <v> already exists. Upload rejected.`; `Invalid version format '<v>'. Use semantic versioning (e.g. 1.2.0).`; `Package contains no DLL files.`; `extension.manifest.json not found in package root.`
- If the assembly loads no swappable types: `Extension loaded no swappable types - check DLL and ExtensionOverrideAttribute.` The platform then restores the previous active version automatically.

## Practical rules
Keep `maxPlatformVersion` open within the major version (`10.99.99`) unless you test per release. Bump `version` on every deploy; an unchanged version is refused by the versioned upload. Do not put secrets in the manifest.
