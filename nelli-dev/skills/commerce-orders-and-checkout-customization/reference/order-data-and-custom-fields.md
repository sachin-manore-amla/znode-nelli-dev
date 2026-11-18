# Custom data on orders
What this answers: where extra information can live on an order and what the product supports.
Evidence level: partly verified; see the unknowns.

## Built-in carriers of extra data
| Field | Limit | Where set |
|---|---|---|
| Job/Project Name | 100 chars | checkout Additional Information; editable in Admin order |
| Additional Information | 500 chars | checkout; stored as instructions on the order |
| In Hands Date | date | Admin order / quote |
| External ID | text | order, user, account; written by API/ERP; read-only in Admin order |
| Purchase Order Number | text | PO payment |
| Custom1 to Custom5 | strings | pass through the shipping and tax plugin requests; not stored as order fields |
| Order notes and history | free text | notes by admins and buyers; audit log |
| Commerce Portal order attributes | name/value | order attribute collection stored with the order; created by the Commerce API (exposure in Admin not confirmed) |

## User-defined fields (global attributes)
Dev Center > User-defined Fields defines fields per entity type; values appear on entity screens. Documented customer entities: store, account, user, content container, form. The platform also contains entity definitions for Order, Quote, Return, Line Item, Voucher and others, with storage prepared, but **whether Admin lets you add fields to the Order entity, and whether the Commerce API returns them, was not confirmed** (`GAPS`). Do not promise it. A global setting "Save Order Attribute" exists for saving product attributes onto order lines.

## Patterns
| Need | Pattern |
|---|---|
| Free-text instruction | Additional Information |
| Structured extra order data | Custom table (see `sdk-custom-tables`) keyed by order number, written by a Custom API called from your storefront code or from an Order Created event |
| ERP reference | External ID |
| Show extra data on emails | edit the email template with tokens that exist; extra tokens need a receipt method override |
| Show on receipt | `BindEmailTemplateDetailsStarted` override or template edit |

## Verdicts
Adding a persisted field to the order record: Needs platform change unless the Order user-defined field entity is confirmed; the custom-table pattern is Customizable and upgrade-safe.
