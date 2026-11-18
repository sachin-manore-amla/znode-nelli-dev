# Data Exchange: steps, authentication, Znode Import, mapping, Credential Vault
Answers: what each step type needs, which auth types exist, which import types the destination accepts, the mapping functions and the vault syntax.
Confidence: KB read through summaries (70-80). Function list from the Data Exchange User Guide.

## Step model
A multi-step exchange has unlimited sequential steps (10.10.1.0). Each step has an optional **Step name** and a mandatory unique **Step code** (for example `Step1`). Each step has its own mapper. Later steps read earlier output with the step prefix: `Step1.Account.Name`. Step 0 is the trigger payload (event or callback request body). A **global mapper** produces the final output; its prefix must be the next step number after the last step. **Add Step** and **Delete Step** exist (delete added in 10.12.1.0).

## Transmission modes
| Mode | Fields |
|---|---|
| API | HTTP Action (GET, POST, PUT, DELETE, PATCH), Endpoint, Authentication Type, Source Format (CSV, JSON, XML), Query Parameter (key and value), Header Parameter (key and value) |
| SFTP | Server Address, Folder Path, File Name, Port, Username, Password, Format (CSV, JSON, XML). Test Connectivity |
| BLOB | Bucket Name, Access Key, Secret Key, Configuration URL, BLOB File Name, BLOB Folder Path, Format. Test Connectivity |
| Znode Import | Gateway URL, API Key (prefilled from the environment), Locale ID (admin locales), Import Type, and per type: Family List, Store, Catalog, Discount Type, Templates |

### API step options
- **Use Separate Requests for Each Record** (10.12.0.0): one request per record instead of a bulk payload; hidden for GET.
- **Reiterate**: pagination loop with **Page Index** and **Page Size** until all records are read. Pagination parameters can use macros (`{{Step1.PageNumber}}`).
- **Max Concurrent Pages**: pages in parallel. Blank is sequential. When the remote API rate-limits, the connector lowers concurrency and retries. Maximum value and default are not stated.
- **Request Body**: JSON; stored as Step 0 for event and callback exchanges.

## Authentication types (API steps)
| Type | Fields |
|---|---|
| Basic | API Username, API Password (sent Base64 in the Authorization header); API Key optional alternative |
| OAuth 2.0 | Grant Type (client_credentials, password), Access Token URL, Client ID, Client Secret, Scope |
| Bearer | Same fields as OAuth 2.0; Username and Password only for the password grant. Access token from step 1 can be a header value in later steps (fixed 10.13.1.0) |
| Custom | Custom Authentication Header (non-standard prefix); username, password and key fields hidden; API mode only; source and destination independent; values kept when you switch type and back |

## Znode Import destination
Import types listed in the KB: Product, Pricing, Inventory, Category, ZipCode, ProductAttribute, CategoryAssociation, Customer, CustomerAddress, ProductAssociation, SEODetails, Highlight, AddonAssociation, AttributeDefaultValue, Voucher, Account, Synonyms, CatalogCategoryAssociation, Brands, Promotion, Sales Rep. Columns and rules per type are in `config-import-export/reference/01-entities.md`. The destination mapping is generated for the type; you still map each source column. Import Logs are generated only for exchanges that use Znode Import.

## Mapping
Mapping types the engine supports: Direct, Fixed or Static value, Default value, Formula, Conditional, Lookup, Transformation, Processor-based, Object, Collection. YAML mappings remain for backward compatibility (two-step: Input/Edit YAML dialog with **Update Mapping**, **Download** sample, **Upload** file).

Macro forms: `{{$Step1.data[].orderNumber}}` and `{{Step1.OrderId}}` both appear in the KB; the release notes for 10.13.1.0 say placeholder behaviour and KB were aligned. Nested target keys use dots (`order.customer.email`).

Functions (case-insensitive): Upper, Lower, Trim, Concat, Replace, Substring, Left, Right, Length, DateTime.Today, DateTime.Now, DateTime.UtcNow, FormatDate(date, format), Math.Round, Math.Max, Math.Min, Math.Abs, Math.Ceiling, Math.Floor, Coalesce, IsNull, Guid, Guid.NewGuid. Notes: Coalesce treats empty string as non-null; Substring and Length throw on bad input; Left and Right return the whole string when the count is larger; Math.Round rounds away from zero. Example: `{{ FormatDate($Step1.data[].orderDate, "yyyy-MM-dd") }}`.
Callback global mapper must output **Sales Price, Retail Price, SKU, Line-Item ID** (architecture article).

## Credential Vault
Path: Commerce Connector > Credential Vault. Columns: Key, Value (masked for secrets), Secret, Description, Last Modified, Actions (edit, delete). Two search boxes (Key, Description). **Add Variable** fields: Key (required, unique), **Mark As Secret (Value Will Be Hidden)**, Value, Description.
Use: `{{Var.API_BaseUrl}}/v1/orders` in endpoint URLs, headers, request body, mapping templates; also usable for SFTP and Blob credentials and numeric page size (User Guide). The User Guide writes secrets as `{{Secret.KEY}}` and says secrets are stored encrypted; the Vault article writes `{{Var.Name}}` for secrets too. Test on the environment which form your version resolves (GAPS).
Behaviour to know: deleting a variable that an exchange uses makes runs fail (no warning documented). Works only with multi-step exchanges. Max count, value size and roles are not stated.
