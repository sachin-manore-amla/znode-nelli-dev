# How discounts are calculated and distributed
What this answers: order of application, maximum applicable discount (MAD), distribution to lines, interplay with shipping, tax and vouchers.
Source: KB Discount Distribution Workflow (read, 80); product source for the calculate sequence (95).

## Categories
| Category | Applied over |
|---|---|
| Line item | line total (unit price x quantity): product, brand, category, catalog, X if Y |
| Order | subtotal: Amount/Percent Off Order, CSR discount |
| Shipping | total shipping (sum of line shipping); handling is never discounted |

## Order of application
1. Price promotions on displayed price.
2. Automatic promotions by Display Order, lowest first.
3. Coupons in the order the shopper entered them.
4. CSR discount last (editable during or after order creation).
Engine sequence in the cart calculation: shipping, then promotions/coupons, then tax, then vouchers, then any method override (`sdk-method-overrides`).

## MAD
Before a discount applies, Znode stores a ceiling per line, for the subtotal and for shipping. Start value = the original amount. Applying a discount draws it down; a discount larger than the remaining MAD is capped. Order or CSR discount: multiplier = discount / subtotal MAD, each line gets multiplier x its MAD. Shipping works the same on shipping MAD. Changing shipping type, destination zip or a line shipping amount removes shipping discounts and resets shipping MAD.
Worked example (KB): products 50 and 89, subtotal 139; `150 off order` is capped at 139; the later 10% category promotion finds MAD 0 and gives nothing.

## Totals
Order Total = Subtotal + Shipping + Handling + Import + Tax - Discount - CSR Discount - Shipping Discount (+ Return Charges on an order with returns). Amount To Be Paid = Order Total - Voucher Amount. Rounding of distributed amounts is not documented.

## For customizations
- A promotion extension result goes through the same distribution (order level is distributed to lines by the engine; shipping level is capped by remaining shipping).
- A `CommerceCalculateCompleted` override rewrites totals after this; the distribution is not redone.
- Tax: with "Calculate Tax On Discounted Price" on, tax uses discounted amounts.
- Anything you add by override does not appear as a discount record.
