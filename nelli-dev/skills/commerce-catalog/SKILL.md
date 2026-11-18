---
name: commerce-catalog
description: Znode PIM structure - the four product types and their price/inventory precedence rules, add-on products, the Product-Category-Catalog-Store association path, catalog publish options, index settings and Product Information Overrides. Use when a product does not appear on a storefront or when working on catalog, category or product-type behaviour.
user-invocable: false
---

# Znode Catalog & PIM

## Four core product types

The type is set at creation and **cannot be changed**.

Admin filter tokens: `SimpleProduct`, `ConfigurableProduct`, `BundleProduct`, `GroupedProduct` — **no spaces**, and **not case-sensitive**. A space in the Product Type filter on the product list silently returns nothing.

Simple products are the building block for Grouped, Bundle, Configurable **and Add-On** products. Child products **inherit the parent's common behaviour** when ordered through the parent.

| Type | Structure | Whose settings win |
|---|---|---|
| **Simple** | One SKU, no parent/child. The atomic unit | its own |
| **Configurable** | Parent + N variants; buyer picks exactly one | **child variant's** price, inventory and settings |
| **Bundle** | Parent + N children bought as a package | **parent's** settings — except child inventory / out-of-stock, where the parent's are used too |
| **Group** | Parent + N children; buyer picks which and how many | **child's** settings |

**Configurable rules:** at least one attribute must have `Is Configurable`; each child needs a unique value for every configurable attribute; a Default Variant can be designated (otherwise random); `Display Variants On Grid` allows bulk ordering of multiple variants from the PDP.

**Bundle:** admin sets Quantities Per Bundle and Display Order.

## Add-On products

Not a product type — a feature on any product surfacing optional/required extras on the PDP. Controls: checkbox group (many), dropdown (one), radio (one). Marked Required or Optional. Added to the cart alongside the parent; total reflects the combined price.

## Association path

Products are **never associated directly to a catalog** — only through categories:

```
Product -> Category -> Catalog -> Store
```

1. `PIM > Categories > Edit > Associated Products`
2. `PIM > Catalogs > Edit Catalog > Associate Categories`
3. Arrange the category in the catalog tree (drag/drop or right-click Move)
4. `PIM > Catalogs > Publish`

If a category sits in two catalogs, its products appear in both automatically.

## Store ↔ catalog

| Relationship | Rule |
|---|---|
| Store → Catalog | 1-to-1 (required; set in `Stores & Reps > Store > Manage > General > Catalog`) |
| Catalog → Store | 1-to-many |

Overrides beyond the store default: **Account** (overrides for all users under a B2B account) and **User Profile** (segment-specific visibility). A published catalog can be associated with any store, account or profile; a non-published catalog can only be associated with user profiles.

Categories are created globally at `PIM > Categories` (catalog-agnostic), then associated and arranged per catalog. No documented depth limit.

## Publish options

| Option | Behaviour |
|---|---|
| Publish to Preview & Production | Live on the storefront |
| Publish to Preview Only | Preview Elasticsearch index only |
| Publish Draft Products Only (default on) | Only `status = draft` products; uncheck to republish everything |

A Store Publish has a "Catalog" checkbox that triggers catalog publishing as part of the store publish.

**Index Settings** (`PIM > Catalogs > Edit > Index Settings`): *Display Pricing and SEO Details from Index* designates one store as the pricing/SEO authority so sort and SEO stay consistent across multi-store deployments sharing a catalog.

**Versioning:** none. Copy a catalog (`Copy`) as an informal snapshot — tick **Copy All Data** to bring the **category associations** across.

> **Copy does not carry Schedulers or Index Settings** — both must be reconfigured on the copy.

**Catalog scheduler:** catalogs have their own scheduler for updating the catalog and its associated products. Publish history shows only the main catalog publish time.

**Deleting a catalog** requires it not be a store's primary catalog. Verify at `Admin > Store Settings > General > Catalog`, select an alternative, then **publish the store settings and the alternative catalog** before deleting.

Categories can also be created directly from the Catalog landing page via **Add New Category**.

## Product Information Overrides (v10.6.2.0+)

Same SKU, different content per **Store + Account + Locale** — no duplicate product records.

- Overridable: Alternate SKU, Alternate Product Name, Alternate Short/Long Description. **Not** pricing, SEO, inventory or images.
- Context key: `SKU + Locale Code + Store Code + Account Code (optional)`. Duplicates cause API errors.
- Requires **both** `Global Settings > Global Product Settings > Enable Product Information Overrides` and the per-store flag. Either off ⇒ all overrides ignored.
- Dedicated index `override_<catalog_index_name>`; any change needs a **full catalog publish** (not draft-only). Products are not auto-marked Draft.
- ~100,000 record performance ceiling. Variants not in a category are excluded from API results.
- APIs: `GET /v2/productoverrides/{sku}`, `GET /v2/productoverrides/multiple-products/{skus}`. Fallback: override → PIM locale → default locale.

## Product types in the code

The Admin filter tokens have no spaces (`BundleProduct`), but the C# constants hold display values with spaces: `public const string BundleProduct = "Bundle Product";`. The same constants are defined in more than one class, Eg `ZnodeCommercePortalConstant` (Commerce Portal) and `CommercePortalContractConstant`. Code compares `.ProductType` or `.ParentProductType` with them, and procedures compare the column with literals such as `ProductType = 'Bundle Product'`.

## Script: `product_type_branches.py`

Finds every place a feature's code branches on the product type: Simple, Configurable, Bundle, Grouped, and add-ons through `IsAddOn`.

```powershell
python product_type_branches.py --route POST "/returns/{classNumber}/validate"   # the chain and its procedures
python product_type_branches.py CommerceCollectionsService
python product_type_branches.py OrderService --branches-only
python product_type_branches.py OrderService --pattern "IsTaxExempt" --label tax-exempt   # any other category
```

- **Branch kinds:** each hit is labelled from the whole statement around it. The kinds are if, else if, while, switch, switch case, the condition of a ternary, a LINQ filter, SQL CASE, SQL filter and SQL IF.
- **Mentions:** a hit that isn't a branch, such as an assignment or an argument, is listed as a mention, so nothing is dropped.
- **The matrix:** the output ends with each value and the branches that test it.
- **IsConfigurable:** a bare `IsConfigurable` is flagged, because it can be the attribute flag.

Confirmed on 2026-10-01:
- `CommerceCollectionsService.cs`: an `if` at 1550, and multi-line ternaries at 1584 and 1636.
- `OrderService.cs`: a multi-line LINQ filter at 3921–3923, and an `if` at 3940.

Pattern-based (see the skills README); confirm each branch at its `file:line`.

## KB source

- [Product Information (PIM)](https://support.znode.com/support/solutions/43000374859)
- [Configuring a Product (12 articles)](https://support.znode.com/support/solutions/folders/43000598183)
- [Managing Catalogs](https://support.znode.com/support/solutions/folders/43000598187)

> Only 2 of ~31 PIM articles read. This is the least-verified functional skill - check the KB before relying on detail here.

## Related
`commerce-product-attributes` · `commerce-search-seo`

## Making variants selectable on the product page (configurable products)

The product attribute `DisplayVariantsOnGrid` (Admin label `Display Variants On Grid`, configurable products only) decides the layout:

- **Off (false):** the product page shows the variant pickers (one choice per configurable attribute) and the shopper picks a combination, then adds one product to the cart. This is the setting for "variants as selectable options".
- **On (true):** the page fetches the child products as a grid for bulk ordering of several variants at once.

Evidence: Webstore source (`packages/agents/src/product/product.ts` fetches configurable children only when the flag is true; `packages/bstore/.../ProductBasicInfo.tsx` shows the selectors when it is false; `packages/utils/src/component/cart.ts` branches on it). Admin path and exact label not yet read in the Admin: confirm there before quoting them. A different picker look (swatches, buttons) is a theme override of the product details component (see `webstore-customization`).
