# Worked example: 10% off the order subtotal when the cart has 3 or more items
What this answers: a complete custom promotion with its tests, as built and unit-tested in an earlier demonstration request; what is proven and what is not.

## Requirement
A new promotion type selectable in Admin: when total quantity is 3 or more, discount 10% of the order subtotal; fewer than 3 items gets nothing. Ambiguities settled by assumption (confirm with the customer): "items" is total quantity (as `GetCartQuantity()` counts it), subtotal is the cart subtotal before discount, tax and shipping, 10 and 3 are fixed, 2 decimals rounded away from zero.
Check first: the built-in Percent Off Order with **Minimum Quantity** may already do this (verdict would be Supported). Write code only if the customer needs behaviour the built-in cannot give.

## Code (pattern)
```csharp
[PromotionExtension(typeof(CartPromotionTypeBase))]
public sealed class PercentOffOrderMinItemsPromotion : CartPromotionTypeBase
{
    private const decimal DiscountPercent = 10m, MinimumItemCount = 3m;
    public PercentOffOrderMinItemsPromotion()
    { Name = "10% Off Order (3+ Items)"; Description = "10% off the order subtotal when the cart has 3 or more items.";
      ClassName = "PercentOffOrderMinItemsPromotion"; }

    public override PromotionCalculateResult Calculate(int? couponIndex, IReadOnlyList<IPromotionInfo> allPromotions)
    {
        var result = new PromotionCalculateResult();
        try
        {
            if (GetCartQuantity() < MinimumItemCount) return result;
            decimal subtotal = Context.Cart.SubTotal;
            if (subtotal <= 0) return result;
            decimal discount = Math.Round(subtotal * DiscountPercent / 100m, 2, MidpointRounding.AwayFromZero);
            if (discount > subtotal) discount = subtotal;
            if (discount <= 0) return result;
            result.OrderLevelDiscount = CreatePromoDiscount(discount, DiscountLevelCode.OrderLevel);
            result.IsApplied = true;
            return result;
        }
        catch (Exception) { return new PromotionCalculateResult(); }   // never break cart calculation
    }
}
```
The demonstration also resolved `IExtensionLogger` inside `Calculate`, logged counts and amounts only (no identifiers), and guarded the log call itself.

## Tests (xUnit, 24 passed, 0 failed)
Cases: three units qualify (15.00 on 150.00); three lines of one; two units do not; boundary 2 then 3; decimal quantity boundary 2.99/3.00/3.01; two lines of 1.5; empty cart; one unit; rounding (99.99 gives 10.00, 33.35 gives 3.34, 0.05 gives 0.01); zero and negative subtotal (negative logs a warning); tiny subtotal rounds to zero and is not applied; discount never exceeds subtotal; cart getter throws gives empty result and one error log; null provider and provider without logger still apply; metadata (attribute, base class, class name); group-product quantity counts toward 3; log content has counts and amounts only.
Tests used fakes for the context, cart and service provider built from the SDK interfaces (see `quality-testing`).

## Deployment steps used
Build Release; `znode deploy extension <csproj>`; Sync; register Class Name `PercentOffOrderMinItemsPromotion`; create the promotion (store, profile, dates, Display Order, Active); rollback by deactivating the promotion or redeploying the previous version.

## Not proven (run on a development environment)
That `Context.Cart.SubTotal` equals the displayed subtotal; stacking with other promotions and coupons and with "allow together"; how the discount line shows in cart, checkout and order; currency with other than 2 decimals; behaviour after a promotion is deactivated.
