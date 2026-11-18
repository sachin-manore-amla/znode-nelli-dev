# Export
Answers: which exports exist in Admin and through the API, how they run, and what cannot be exported.
Confidence: product source and API specification (90), KB (70).

## Admin
| Export | Where |
|---|---|
| Products | PIM > Products > Tools > **Export To CSV** or **Export To Excel** (toast "Export has been initiated. Please wait, this may take a few minutes."). Respects the catalog filter and language of the list |
| Promotions and Coupons | Marketing > Promotions (export popup, Promotion Type filter, 10.12.1.0) and the Exports screen |
| Vouchers | OMS > Vouchers (CSV or Excel, 10.12.1.0) |
| Form submissions | OMS > Form Submission > Tools |
| Failed import rows | Imports > log > CSV, Excel or PDF |
| Custom table data | Custom Tables screens (see `sdk-custom-tables`) |
| Grid exports | List screens with the generic export popup: CSV or Excel, with or without additional attributes, selected rows or the current filter |
Central list: **System Settings > Exports**: export ID, type, file type, status, start and end; download a completed export as a ZIP; delete completed export logs. Files are chunked and expire (a cleanup job removes expired files). The KB lists fewer exports than the product offers: the product wins.
Guidance: 5,000 records per file, 50 MB, 3 concurrent export jobs.

## API
| Operation | Purpose |
|---|---|
| `GET /v2/export/{exportHeadName}/{fileType}` | Start an export. Supported `exportHeadName`: `PromotionsAndCoupons`, `Vouchers`. `fileType`: `csv` or `excel`. Optional `filter`, include additional attributes. 202 Accepted, 409 conflict |
| `POST /v2/export/{exportType}/{fileType}` | Older form; supports `PromotionAndCoupon` only |
| Export log list, delete export log, expired file cleanup, export file path | Legacy v1 routes |
Filter fields: PromotionsAndCoupons: PromoCode, Name, Discount, StartDate, EndDate (DiscountType for a specific type); Vouchers: StoreName, CardNumber, Name, CustomerName, AccountCode, AccountName. Exports are asynchronous: poll the export list, download from Exports.

## What is not available
No API to export products, categories, prices, inventory, customers or orders as a file. Use list APIs with `pageIndex`, `pageSize`, `filter`, `sort` (`api-consumption`), or a Data Exchange with an API source. Reports and BI exports are separate (Reports API in `api-catalog`).
