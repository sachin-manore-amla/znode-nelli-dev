# Settings, flags, import and export, security and limits
Settings and flags tied to UDFs, system-defined fields, import and export support, XSS and permission notes, and limits.
Use it when a requirement touches a built-in switch or bulk data.

## System-defined fields (do not repurpose)

The Store, User, Account and Global Setting entities already contain UDFs that carry product settings (examples: store login requirements, maintenance mode, 2FA, CSP, reCAPTCHA, address validation, budget, voucher reminder days, the Global Settings values). They are marked system-defined.
- Do not delete, retype or reuse them for customer data. Delete is refused for system-defined items.
- A change to some of them raises extra cache refreshes (2FA, content security policy, XSS and IDOR switches, checkout session, address validation) in the product.
- For the list of settings and the Global Settings screen see `config-global-settings` and `config-store`.

## Flags and settings that involve UDFs

| Name | Where | Level | Effect |
|---|---|---|---|
| Required, Is Localizable, Unique Value, Allow Multiple Files, WYSIWYG | Attribute screen | Per field | See attribute-types-and-rules.md |
| Family per entity | Product data (not editable in Admin) | Entity type | One family for most entities, one per container for Content Containers, none for forms |
| `Enable XSS Validation` (global setting, stored as an inverted skip flag in the product) | Global Settings | Global | Applies to product attribute values and selected user and address fields. Not applied to UDF values (see below) |
| Media settings | `DAM > Media Settings` | Global | Decides whether File and Image fields use the internal media library or an external source, and the allowed extensions and size for `POST /v2/files-upload` |
| Events feature flag | See `sdk-events-and-webhooks` | Global | Needed for the `UserDefinedField` event |
| Admin permission | Role menu rights on `User-defined Fields` (Attributes, Attribute Groups, Attribute Families, Entity Attributes) | Role | Without write on Attributes the `Additional Attributes` link or save buttons are missing |

## Security: XSS validation

- The 10.13.1.0 release note (Aug 14, 2026) adds configurable XSS validation for product attributes. WYSIWYG-enabled Text and Text Area attributes are excluded. KB, 80.
- In the product source this check is written for product attributes only. The UDF value save and the v2 value write do not run it (verified by reading the save paths, 90). Do not assume UDF values are sanitised.
- The Admin writes values back into its pages HTML-encoded (verified, 90). The Webstore React code escapes text by default.
- Rules for a customization: validate and encode UDF values in your own endpoint, never place a UDF value in `dangerouslySetInnerHTML` or an email template without encoding, and treat a Text Area with WYSIWYG as HTML you must sanitise.
- Message used by the product for rejected product-attribute values (not UDFs): `The attribute '<code>' contains potentially unsafe content.`

## Import and export

| Feature | UDF support | Source |
|---|---|---|
| Export of Promotions and Vouchers | The export pop-up offers `Without Additional Attributes` or `With Additional Attributes` ("Exports the standard columns, including User-defined Fields, in a format compatible with the default import template."). Only these two exports (and the user voucher list) include UDF columns | Admin and API source (90) |
| Voucher import | UDF columns are read; a `<code>_Source` column carries the file or image source | Product source (85) |
| B2B customer import | A column named exactly like a User UDF code sets that user value. Option fields take the option code | Product source (85) |
| Other imports and exports (products, price, inventory, brands and so on) | Not found to carry UDFs. Brand import sets only the five Custom1 to Custom5 boxes | Product source, module guide (85) |
| Bulk import events | Bulk import raises no domain events (skill `sdk-events-and-webhooks`) | |

Release note 10.13.0.0 (Jul 24, 2026): promotion and voucher exports no longer carry unassociated or unconfigured UDF columns (KB, 80).

## Limits

| Item | Limit |
|---|---|
| Attribute code | Admin 100 characters, API 300 |
| Group code, family code | Admin 100, API 200 |
| Labels and descriptions | 300 characters |
| Option code | 100 characters |
| Display order | 1 to 999 |
| Value size | No fixed limit for the stored text. Use `Max Characters` on the field |
| Locale | Label per language; value per language when localizable |
| Count of fields, groups, families | No limit found in the source |
| Performance | Each record screen loads every group of its family. Keep groups small on high-traffic entities (Store, User) because the store portal call returns all Store values |

## Version notes (release notes, KB 80)

| Version and date | Change |
|---|---|
| 10.6.0.0, Dec 28, 2025 | Form attributes show in the order of the attribute group display order, and an order change updates every form that uses the group. Fix: global attributes missing on the category page after product publish. Fix: store code returned null by the update global attribute API. Shipping plugin estimate model carries the attributes of the shipping settings group |
| 10.13.0.0, Jul 24, 2026 | Promotion UDF groups and attributes by promotion type with an ALL option (listed as an upcoming enhancement). Export fix for promotions and vouchers |
| 10.13.1.0, Aug 14, 2026 | Improved API support for family and group associations. XSS validation for product attributes. Invalid attribute codes rejected in attribute default value imports |
| 10.14.0.5, Sep 29, 2026 | The release notes page was not readable for this build; no UDF change confirmed (GAPS) |
