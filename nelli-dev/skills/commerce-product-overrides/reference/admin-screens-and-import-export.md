# Admin screens, CSV import and export

What this answers: where to manage override records in the Admin, what each screen offers, the exact CSV template and the messages shown on import and export.
The Admin uses the generic Custom Table data screens, so behaviour matches other custom tables.

## Screens

| Screen | Path | What it does |
|---|---|---|
| Product Information Overrides list | `PIM > Product Information Overrides` | Lists the system table (one row, "Product Information Overrides"). Filter operators: Contains, Is, Begins With, Ends With. |
| Record grid | Edit icon of that row | Lists override records. Columns menu, sort, page size (10, 20, 50, 100), `Tools > Delete`, row delete icon, `ADD A RECORD`, `Import`, `Export`, `Manage Fields`. |
| Add / Edit record form | `ADD A RECORD` or a row's edit icon | One text box per field, in display order, with the label and character limit. No drop-downs. |
| Manage Fields | Table page, `MANAGE FIELDS` | Grid of Field Type, Field Code, Field Name, Is Unique, Field Length, Display Order. Field code and length are read-only. |
| Product Overrides window | `PIM > Products >` open a product > `Product Overrides` button | Read-only list of the product's overrides, title `{SKU} - Product Information Overrides`. No add, edit, delete, import or export. Shows `No records found.` when empty. Button is shown only when the global flag is on. |

(Module guide, verified on a development environment 2026-10-13 for the grid, form, Manage Fields and delete popups; the product window could not be seen because the global flag was off there, so its contents are from product source, 85.)

Behaviour to know:

- The grid search is a plain text filter. On one build, a search containing an apostrophe left the grid's saved view showing `No records found.` with the toolbar gone, even after a reload; records still opened by id. Avoid apostrophes in filters. (module guide, observed 2026-10-09)
- On that same environment, adding or editing a record from the Admin failed with `Failed to create.` / `Failed to update record.` while delete worked. This was recorded as a product defect on that build only. Check add and edit on your own environment before planning a manual data entry process, and use import or the API if it fails. (module guide, observed; gap)
- Admin saves also move the product (and its parent products) to Draft; API saves through `v2/productoverrides` do not. A full catalog publish is still required in both cases. (module guide, from source, 85)

## Import

1. On the record grid click `Import`. If the table is empty a Note popup first says: `A unique column cannot be added or changed once a row is added to the system. Do you still want to continue?` and `OK` continues.
2. In the `IMPORT TABLE DATA` panel use `Download Sample File` to get `ImportCustomTableTemplate.csv`.
3. The header row is:

```
Locale,SKU,StoreCode,AccountCode,AltSKU,AltProductName,AltShortDescription,AltLongDescription
```

4. Choose the file with `Browse` (`Select a .csv file`). A file without `.csv` shows `Please select file with .csv extension only`. No file shows `File not present.`
5. Click `Import`. You see `Import has been initiated. Click here or redirect to the Imports screen to view more details.` The import runs in the background. Results per row (imported or failed with reason) are on the Imports screen (`System Settings > Imports`). A failed run shows `Import process failed. Please review the logs for more details.` An empty file shows `CSV does not contain any data.`

Rules: there is no validation against products, stores, locales or accounts, and a duplicate row in the file creates a duplicate record. If your build shows a `CatalogCode` field, the template may carry it too: download the template from your own environment and use its header. (module guide, 85; KB says CSV layout is not stated)

## Export

1. Click `Export`. The message `Export has been initiated. Please wait, this may take a few minutes.` appears.
2. When accepted: `Export has been initiated. Click here or redirect to the Exports screen to view more details.` An empty table gives the error `No Data To Export the Custom Table.`
3. On the Exports screen the row reaches `Completed`; its download is a `.zip` holding `CustomTable1.csv` with all records and all columns.

The KB recommends import and export for large catalogs, enterprise rollouts and moving override data between environments.

## API route for the same data

The Admin uses the generic Custom Table data API with table key `ProductInformationOverrides` (list, create, update, delete, import, export, template). Customers can use the Custom Table API for reading and bulk work, and `v2/productoverrides` for create, update and delete. See override-apis.md and the custom table skill.
