# Import and export: where sources disagree
Answers: KB claims that the product contradicts, and open inconsistencies in the KB itself.

| Topic | KB says | Product shows | Follow |
|---|---|---|---|
| Upload formats | CSV or Excel | Admin accepts `.csv` only (browser and server check) | Product |
| Admin path | "Imports" and "Import & Export" both used | System Settings > Imports and Exports | Product |
| Exports available | Form submissions, failed import log, promotions and coupons | Also products (PIM list), vouchers (10.12.1.0), custom tables, grids | Product |
| Export API | one type | `PromotionsAndCoupons` and `Vouchers` | Product |
| Logs and partial failure | "not stated" | Row-level log, status Completed With Errors | Product |
| Scheduling | "not stated" | No scheduling in Imports | Data Exchange |
| Async | "several minutes" | Background task in the API; v2.1 returns 202 | Product |
| `ProductType` | required column and reserved word | Required column works | Use the column |
| Catalog Category Association Add on existing | "ignored" in one line, "creates or updates" in another | Not verified | Test |
| Promotional message length | 300 and 150 | Not verified | Use 150 to be safe |
| Product Association upsert key | not stated | Not verified | Test with a duplicate row |
| Auto publish | Auto Publish flag temporarily disabled (10.7.0.0) | Import API does not set it | Publish manually |
Release notes to check when behaviour surprises: 10.5.0.0, 10.7.0.0, 10.10.1.0, 10.12.0.0, 10.13.1.0, 10.14.0.0, 10.14.0.6.
