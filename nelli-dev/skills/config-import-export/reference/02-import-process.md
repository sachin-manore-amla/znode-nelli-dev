# Import process: Admin steps, templates, statuses, API, limits
Answers: how an import runs, how to follow and debug it, how to start one from code, SKU rules and limits.
Confidence: product source and API specification (90), Admin source (90), KB (70-75).

## Admin steps
1. System Settings > Imports > **Add New**.
2. Choose **Locale ID**, **Import Type**, and the context control that appears for the type (Family List, Select Store, Select Catalog, Select Country, Select Discount Type; pricing uses the price list code in the file).
3. **Select Template** (a default template exists per type) or **Create a new Template**.
4. **Download Template** to get the header row; fill it.
5. Browse a file (`.csv` only: "Only select file with a .csv extension."). The CSV headers appear and map to **Attribute Codes**; use **Update Mapping** to save changes, **Reset Template** to restore.
6. **Import**. Follow the row in the Imports list: ID, Import Type, Template, Status, Start and End Date, counts.
7. Verify the data in the owning screen, then publish where the data feeds the storefront.
Re-create templates after you add or change family attributes.

## Custom templates
Path: Imports > Add New > Select Template stays on Please Select > **Create a new Template** > enter **Template Name** > Save > Download Template (CSV with the family's attributes) > Browse your CSV > move headers with the `>>` button into **Attribute Codes** (instruction on screen: "Move CSV Headers to Attribute Codes to map with Database Columns for creating an Import Template. Attribute Codes should match Database Columns sequentially."). **Manage Templates** (Imports list) lists and deletes custom templates. Limits on name length and number of attributes are not stated; the API limits the template name to 300 characters.

## Statuses and logs
`Started` in progress; `Completed Successfully` no failed record; `Completed With Errors` some failed and some succeeded; `Failed` all failed. Click the status for **Import Log Status**; log details give Row Number, CSV Column Name, CSV Column Data, Error Description; download CSV, Excel or PDF (Export > Export Failed Import Details). Delete log rows from the list. Imports started from PIM Bulk Update appear in the same list.

## Async and concurrency
The API reads the file into a temporary table and then continues processing on a background task inside the API process; the HTTP call returns early. A restart of the API during a run can interrupt it. Only one import or export runs at a time per the platform check; the Admin shows an error if another is running. The v2.1 API additionally refuses while a catalog publish or export is running (409).

## Import API
| Operation | Purpose |
|---|---|
| `POST /v2.1/imports/process-log/{importType}/{templateName}?localeCode=&touchPointName=` | Start an import asynchronously. Returns 202 and `ImportProcessLogId` |
| `GET /v2/imports/process-log-details/{importProcessLogId}` | Status and paged error details |
| `GET /v2/imports/import-families/{importType}` | Families with configured templates |
Headers on the start call: `Authorization` (Bearer or Basic) and `Znode-UserId` (integer, greater than 0, audit owner). Body JSON: `importData` (the CSV compressed then Base64 encoded, or binary) and `properties` (type specific, below). Template name must exist and match the import type. Errors: 400 invalid template or type or locale or missing user, 401, 403, 404, 409 publish or export running, 500.
Required `properties` per type: Product `FamilyCode`; Pricing `PriceListCode` (not needed with the default `PriceTemplate`); Category `FamilyCode`; ZipCode `CountryName`; Customer, SeoDetails, Account `StoreCode`; CatalogCategoryAssociation `CatalogCode`; Promotions `DiscountName`; the rest none. Import types accepted: Product, Pricing, Inventory, Category, ZipCode, ProductAttribute, CategoryAssociation, Customer, CustomerAddress, ProductAssociation, SeoDetails, Highlight, AddonAssociation, AttributeDefaultValue, Voucher, Account, Synonyms, CatalogCategoryAssociation, Brands, Promotions, SalesRep, BStoreCustomer.
Older v1 import operations exist (GetImportTypeList, GetAllTemplates, GetTemplateData, ImportData, GetImportLogs, GetLogStatus, Delete, CheckImportStatus, UpdateMappings, DeleteImportTemplate). They are legacy; the SDK import client wraps them. Prefer v2.1 for new work.
The import request model carries `IsAutoPublish`; the v2.1 start call does not set it, so assume **no auto publish** and publish yourself (verify on the environment).

## SKU rules
The Product SKU field does not support special characters. Enter an alphanumeric SKU and put the original value (with special characters) in `ProductCode`. Storefront search still finds the original because Product Code is searchable by default (Marketing > Site Search settings). Allowed set, maximum length, case and API behaviour are not stated in the KB. Bulk Update matches SKUs case-insensitively and does not apply the SKU character rules.

## Limits
No documented row or file size limit for the Imports screen. Guidance: files under 50 MB, product batches 1,000 to 10,000 rows, price and inventory 2,500 to 10,000, categories 500 to 1,000, promotions 500. Import processing time "may take several minutes".

## Version notes
10.5.0.0 product import rebuilt, multi-tier price import fixed; 10.10.1.0 import logs API matches Admin logs, missing price list code logged; 10.12.0.0 customer import flag 11; 10.13.1.0 customer and sales rep username rules, voucher and product association fixes; 10.14.0.0 username script blocking; 10.14.0.6 new templates import fix, SEO details import fix.
