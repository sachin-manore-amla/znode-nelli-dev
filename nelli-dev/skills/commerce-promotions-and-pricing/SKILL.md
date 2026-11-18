---
name: commerce-promotions-and-pricing
description: Everything about changing what a shopper pays through price lists, promotions, coupons, vouchers and custom promotion types. Covers price list associations and precedence, sale/retail/tier prices and dates, promotion types and scoping by store and profile, coupon modes, stacking and global promotion settings, the discount distribution rules, vouchers, and the Promotion Extension SDK (CartPromotionTypeBase, PromotionExtension, Calculate, deployment, Admin registration) with a tested worked example. Load it for any discount, price, coupon, voucher or "custom discount rule" requirement, and to decide whether configuration is enough.
user-invocable: false
---

# Promotions and pricing

## Vocabulary
| Term | Meaning |
|---|---|
| Price list | Named set of SKU prices (retail, sale, tier) in one currency, associated with stores, profiles, accounts, users |
| Promotion | A discount rule of a promotion type, scoped by store and profile, with optional coupon |
| Coupon | A code that activates a promotion (shared code or unique generated codes) |
| Voucher | Prepaid balance paid like a payment method, not a discount (`reference/vouchers.md`) |
| Promotion extension | Your own promotion type written in C# (`reference/promotion-extension-sdk.md`) |

## Ten facts that matter
1. Price comes from price lists; discounts come from promotions. Change prices with price lists, not promotions, when you can. (KB 80)
2. Price list resolution order: user lists, then the user's account, then the user's profiles, then the store; lowest precedence number first at each level; list dates and price-record dates are two separate gates. (verified in product source 2026-09-23)
3. A child account does **not** inherit its parent's price lists. (verified)
4. Within a SKU: tier price (quantity) beats sale price beats retail price.
5. Promotions apply automatically in Display Order (lowest first); coupons follow in the order entered; the CSR discount is last. Handling charges are never discounted. (KB 80)
6. Each promotion is scoped to one store or all stores and to one, several or all profiles. There is no account or account-group scope. (KB 80, SDK members checked)
7. Global settings decide stacking (Dev Center > Global Settings > Promotions and Coupons), and apply when an order is created, not when it is managed afterwards.
8. A custom promotion type is a class deriving `CartPromotionTypeBase` marked `[PromotionExtension]`; `CreatePromoDiscount` takes an **absolute amount**, not a percentage. (verified)
9. After deploying an extension you must **Sync** (Admin > Extension Observability) and register the class name (case-sensitive) in Dev Center > Promotion Settings. (KB 80)
10. The shopper is exposed to an extension only as ids (user, profile, store, order), so "by account group" cannot be coded directly. (verified, `GAPS`)

## Reference files
- `reference/price-lists.md` – price lists, associations, precedence, dates, tiers, import, API.
- `reference/promotions-and-coupons.md` – types, scoping, coupon modes, stacking, BOGO, settings.
- `reference/discount-calculation.md` – order of application, MAD, distribution, CSR discount, tax interplay.
- `reference/vouchers.md` – vouchers versus coupons.
- `reference/promotion-extension-sdk.md` – the code route, contract, deployment, Admin registration, limits.
- `reference/worked-example-percent-off-min-items.md` – a tested custom promotion.

## Nelli-Dev decision guide
| Requirement | Verdict | Route |
|---|---|---|
| Discount by account group | Customizable via configuration | Account price list (account-specific pricing) or a profile (put the accounts' users in a profile) with a profile-scoped promotion. A code route is not available for account lookups; if the discount is a percentage across the catalog and price lists cannot express it, ask Znode |
| 10% off for wholesale customers | Supported | Percent Off Order or Product promotion scoped to the Wholesale profile |
| Contract prices for a distributor | Supported | Price list associated to the account, precedence lower than the store list |
| Sale price for two weeks | Supported | Sale price with price-list or record dates |
| Quantity break pricing | Supported | Tier prices |
| Coupon codes for 5000 recipients | Supported | Unique coupon codes (1 to 99,999 per generation) |
| Free shipping above a threshold | Supported | Percent Off Shipping (100%) with Minimum Order Amount, or Amount Off Shipping. See `sdk-provider-plugins` for rate-level options |
| Buy 2 get 1 | Supported | BOGO promotion |
| Discount when cart has 3 or more items (percentage of subtotal) | Supported or Customizable | Percent Off Order with Minimum Quantity first (check the built-in field); otherwise promotion extension (worked example) |
| Discount that depends on an ERP, loyalty tier, or custom attribute | Customizable | Promotion extension, plus lookups only through ids you can resolve; confirm the data is reachable |
| Change a unit price at checkout from an ERP | Not by override; Customizable via price list import/API sync | Import prices (see `config-import-export`) or a price-list integration |
| Adjust final total after calculation | Customizable | `sdk-method-overrides` |
| Gift balance | Supported | Vouchers |
| Apply promotions when managing an existing order | Needs platform change / limitation | Promotion/coupon changes on Manage Order are restricted in 10.10 |

Related: `sdk-method-overrides`, `commerce-orders-and-checkout-customization`, `config-import-export`, `sdk-custom-api`.
