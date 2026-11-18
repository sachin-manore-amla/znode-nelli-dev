# Method override hook catalogue (10.x)
What this answers: which methods can be overridden, where each fires, what you receive and which response fields Znode reads back.
Source: product source (95), release notes 10.1.1, 10.2.1, 10.10 (80). The Add form in Admin lists the same hooks.

## The six hooks
| Module (type) | Method name | Fires | Reads back |
|---|---|---|---|
| Calculate Cart (`CalculateCart`) | `CommerceCalculateCompleted` | End of the storefront cart/order calculation, after all standard steps | Overridden totals and per-item shipping/discount, only if `SkipExecution=true` |
| CP Calculate Cart (`CPCalculateCart`) | `CPCommerceCalculateCompleted` | End of Commerce Portal order calculation (order place and recalculation) | Overridden totals, only if `SkipExecution=true` |
| Calculate Cart (`CalculateCart`) | `InitiateTaxCalculationCompleted` | Just before tax is calculated (cart, order submit, cancel) | `CustomerCode`, `UserId`; `SkipExecution=true` skips the tax step |
| Quote (`Quote`) | `BindEmailTemplateDetailsStarted` | While the order/quote receipt text is built | The returned receipt text; `SkipExecution=true` returns your text as the whole receipt |
| Quote (`Quote`) | `SetTotalSectionInEmailTemplateCompleted` | After the receipt total section (table) is built | The returned table; `SkipExecution=true` uses it as final |
| Email Notification (`EmailNotification`) | `SendEmailCPAdministratorCompleted` | Commerce Portal order notification email to administrators | Returned text replaces the body; `SkipExecution=true` suppresses the send |

Note: the Quote-module receipt methods also build **order** receipts and the matching email templates, so overriding one affects quote and order receipts together (KB 80).
Admin shows a description for each method. The `CommerceCalculateCompleted` description says it applies to storefront cart, checkout, receipt and order detail totals and is **not** used for admin screens or other storefront screens.

## CommerceCalculateCompleted
Request fields (read-only context, sent in `EventPayload`):
`PortalId, LocaleId, ProfileId, UserId, ExternalId, ShippingId, GiftCardNumber, CurrencyCode, CurrencySuffix, Discount, GiftCardAmount, OrderLevelDiscount, OrderLevelShipping, OrderLevelTaxes, ShippingCost, ShippingHandlingCharges, SubTotal, Total, CustomShippingCost, CustomTaxCost, CSRDiscountAmount, Items[]`.
Each item: `CartItemId, ProductId, SKU, Quantity, AddOnQuantity, UnitPrice, CustomUnitPrice, ShippingCost, CustomShippingCost, ProductDiscountAmount, TaxCost, PromotionalPrice, DiscountAmount, PerQuantity* amounts, add-on/bundle/configurable SKU lists`.

Response (`ResponsePayload`, JSON string):
| Field | Applied to |
|---|---|
| `OverriddenSubTotal` | cart subtotal |
| `OverriddenShippingCost` | shipping cost |
| `OverriddenShippingHandlingCharges` | handling charges |
| `OverriddenDiscount` | discount |
| `OverriddenTotal` | total |
| `OverriddenItems[]` with `CartItemId` plus `ShippingCost`, `CustomShippingCost`, `DiscountAmount` | the matching line only |
Only fields that are non-null are applied. Nothing else is read back: **tax, unit price, quantity and SKU cannot be changed here** (the earlier note listing `SalesTax`, `UnitPrice` and similar as overridable was wrong; those are in the request only). The sample JSON shown in Admin includes `OverriddenTaxCost`; the storefront calculation does not apply it (verified in source, so do not rely on it).

## CPCommerceCalculateCompleted
Request: `SubTotal, Total, TaxCost, ShippingCost, Discount, HandlingFee, VoucherAmount, CSRDiscountAmount, ShippingDiscount, OrderLevelDiscount, OrderLevelShipping, OrderLevelTaxes, UserId, ShippingId, IsTaxExempt, CurrencySuffix, ImportDuty, Items[]` (each: `OrderProductId, SKU, ProductId, UnitPrice, ShippingCost, TaxCost, DiscountAmount`).
Response applied (non-null only, with `SkipExecution=true`): `OverriddenSubTotal, OverriddenTotal, OverriddenTaxCost, OverriddenShippingCost, OverriddenDiscount, OverriddenHandlingFee`. Line items are not read back. The overridden values are saved with the order.

## InitiateTaxCalculationCompleted
Request and response model: `UserId` (int, nullable) and `CustomerCode` (string). If you return a non-empty `CustomerCode` it is used as the tax customer code (it wins over `UserId`); a returned `UserId` replaces the user for tax-exempt lookups. Use it to send your ERP customer number to Avalara. It fires on cart calculation, order submit tax and order cancel tax paths.

## Receipt and email hooks
`BindEmailTemplateDetailsStarted`: `ExtendedRequestPayload` carries `{"MessageText": "<current html>"}`. Return the new html as `ResponsePayload` (a JSON string). `SetTotalSectionInEmailTemplateCompleted`: `EventPayload` is the total table as JSON rows `[ {Title, Amount}, ... ]`; return the changed table in `EventPayload` and `ResponsePayload`. `SendEmailCPAdministratorCompleted`: `ExtendedRequestPayload` carries `MessageText`; the sample in the SDK replaces a `#SampleEmail#` token.

## Not overridable (examples)
Unit prices, promotions result, inventory, payment capture, order status change, login, product publish. Use price lists, promotion extensions, events or a Custom API instead.
