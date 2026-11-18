# PIM Bulk Update from CSV
Answers: how to update many existing products by file, the file rules, what is rejected and the messages.
Source: PIM module guide, verified on a development environment on 2026-10-08 (85-90).

## Where and who
PIM > Products > **Tools > Bulk Update**. Needs the Admin role or any role with Read Only access on PIM or Products. Not available in Commerce Portal, B Store, webstore or the v2 API. No product selection is needed; only the SKUs in the file change.

## Steps
Tools > Bulk Update > (optional) **Download Sample File** (`ProductUpdate.csv` with `SKU,ProductName,IsActive`) > **Select A .Csv File** (Browse uploads at once) > **Import**. Success bar: "Update process has been initiated. Click to view log details" (link opens System Settings > Imports). Follow the run on the Imports list (Import Type and Template Name `ProductUpdate`).

## File rules
| Rule | Behaviour |
|---|---|
| Extension | `.csv` only ("Please select file with .csv extension only"; "File not present.") |
| Header row | Required; comma delimiter only; UTF-8 with or without BOM |
| Required column | `SKU` (any position, any case). Missing: "Mandatory column must be included in the import/update file." run Failed (the screen still says initiated) |
| Other headers | Product attribute codes. An unknown header rejects the **whole** file: "Input cannot be updated because of its unavailability in database." Duplicate header rejects the file |
| Category code columns | Ignored |
| SEO, price, inventory, category, catalog columns | Not attributes: the whole file is rejected |
| `ProductType` | Must equal the product's type |
| Unknown SKU | Row rejected: "Input must be available as a SKU saved against any existing product."; no product is created |
| Same SKU twice | Both rejected: "Duplicate records must be excluded from the import/update file." |
| Empty cell | Does not clear a value. Yes/No attributes become No |
| Select values | Option codes, multi select comma separated without spaces |
| Language | Default language only |
| Empty file | "CSV does not contain any data." |
| Required attribute empty | "Input is required." |
| Text too long | "Input must not exceed the maximum character limit of 300" (Product Name) |
Same checks as Edit Product apply for required, maximum characters (Text), unique within the file, number, date, options, image name, IsActive. Skipped: regular expressions, uniqueness against saved products, Text Area length, media type and size.
Media: file names already in the Media Manager; a single image is replaced, gallery images are added.
Every product touched moves to **Draft**: publish afterwards.

## Limits
Admin upload up to 10 GB; rows copied in batches of 1000; database time-out 20 minutes on the reference system; gateway answers about 90 seconds (the update continues, you may see "service unavailable"); on some database editions rows are processed in a database job after the answer.

## API route (legacy v1)
`POST /Products/ImportProductUpdateData`: body `FileName`, `ImportType` = `ProductUpdate`, `ImportData` (bytes, compressed flag `IsCompressed`), `TemplateName`, `LocaleId`. The call answers success even when rows fail: always read the import log. The `IsAutoPublish` field has no effect. No v2 equivalent exists.
Alternatives: single-product update by SKU and attribute code (any language), the generic import with a template and language, Data Exchange product update.
