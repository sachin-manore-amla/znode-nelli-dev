---
name: commerce-inventory
description: Znode inventory tracking per SKU per warehouse - multi-warehouse display and deduction order, inventory record fields, the three out-of-stock options, backorder behaviour and low-stock alerts. Use when stock levels look wrong, when configuring warehouses, or when working on add-to-cart stock validation.
user-invocable: false
---

# Znode Inventory & Warehouses

## Tracking model

Inventory is tracked **per SKU per Warehouse**. Two admin views:
- `OMS > Inventory` — global, across all warehouses
- `PIM > Products > [Product] > Inventory` tab — per product, across all warehouses

## Multiple warehouses

Each store has one **Default Warehouse** plus any number of **Associated Warehouses** (fallback when the primary is out of stock).

| Rule | Detail |
|---|---|
| Quantity shown on the storefront | Sum of QoH across default + all associated warehouses |
| Deduction order on order placement | Default warehouse first; remainder from associated warehouses in association order |
| Backorder overflow | If backorder is enabled and all warehouses reach 0, the **default warehouse QoH goes negative** |

Warehouses also serve as the **shipping origin** address for carrier rate calculation.

## Inventory record fields

| Field | Description |
|---|---|
| SKU | Read-only after creation |
| Warehouse | Owning warehouse |
| Quantity On Hand | Current available stock |
| Re-Order Level | Threshold that triggers a low-stock admin notification when QoH ≤ this value |
| Backorder Quantity | **Not wired to backorder logic at all** |
| Backorder Expected Date | **Not wired to backorder logic at all** |

> The KB is explicit: these two fields "are **not bound to the Backorder functionality**" and exist so project teams can **customise** backorder behaviour on top of them. Nothing in the standard Znode platform reads them — do not assume they gate purchasing. The actual backorder switch is the per-product Out-of-Stock option below.

Admins may update Quantity On Hand, Re-Order Level and Warehouse, and may delete an inventory record, but **cannot change the SKU**.

## Out-of-stock options (per product)

`PIM > Products > [Product] > Product Settings > Out-of-Stock Options`

| Option | Storefront behaviour |
|---|---|
| Don't track inventory | Always purchasable |
| Disable purchasing for OOS products | Add-to-cart blocked at QoH = 0 |
| Allow back-ordering | Purchase allowed at QoH = 0; QoH goes negative |

Per-store messages: `In Stock Message`, `Out of Stock Message`, `Back Order Message` (`Stores > Manage > General`).

## Deduction on order placement


## Low-stock alerts

When `Quantity On Hand <= Re-Order Level` admins receive an automated notification (`LowInventoryOrderNotificationTemplate`). Configured per SKU per warehouse at `OMS > Inventory`. Back-in-stock buyer notifications use `SendWaitingListNoticeInventory` and require *Enable Inventory Stock Notification* in Additional Store Attributes.

## Import

`System Settings > Imports > Inventory` — CSV/Excel, key columns `SKU`, `Quantity`, `WarehouseCode`; matches on SKU + Warehouse. Imports can add or update only, never delete.

## Key tables


## KB source

- [Managing Inventory](https://support.znode.com/support/solutions/folders/43000598174)
- [Managing Warehouses](https://support.znode.com/support/solutions/folders/43000598172)

## Related
`commerce-catalog` · `commerce-orders` · `config-import-export`
