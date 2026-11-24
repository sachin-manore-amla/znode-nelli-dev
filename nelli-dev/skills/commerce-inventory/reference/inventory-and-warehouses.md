# Inventory and warehouses: details
What this answers: the screens, fields and rules behind inventory, warehouses and their store association.
Sources: KB Configuring Inventory, Managing Inventory (OMS and Stores & Warehouses versions), Managing Inventory for a Product, Configuring a Warehouse, Managing Warehouses (read 2026-11-23). Confidence 85 unless marked.

## Create inventory
| Where | Steps |
|---|---|
| OMS > Inventory | Add New > enter SKU and pick it (or Browse) > Warehouse > Quantity On Hand, Reorder Level, optional Backorder Quantity and Backorder Expected Date > Save |
| PIM > Products > product > Inventory | Warehouse inventory section, backorder settings; **Save** in the section saves inventory; **Save & Close** in the page header does not save inventory changes |
| Import | System Setup > Import > Add New > type Inventory > template > upload |
Records appear in all views.

## Field meaning
- Warehouse: where stock is held and available for fulfilment.
- Quantity On Hand: available stock.
- Reorder Level: minimum threshold for monitoring (the only low-inventory reference in the configuring article).
- Backorder Quantity / Expected Date: for custom processes, not native backorder.

## Out-of-stock behaviour and messages
Rules: **Disable Purchase for Out-of-Stock Products**, **Allow Back-Ordering of Products** (set per product on the Inventory tab or product settings; exact placement per earlier notes: PIM > Products > product > Product Settings > Out-of-Stock Options, unverified here). Storefront status: In Stock, Out of Stock, Back Ordered or Available for Backorder. Messages: In-Stock Message, Out-of-Stock Message, Backorder Message (store inventory settings). The PDP updates in real time after a purchase or manual change; the PLP may lag from caching.
Returns freeze the **Out Of Stock Options value** at order placement (`commerce-returns`).

## Store warehouses (Stores and Reps > Stores > Manage > Inventory)
- Default warehouse: required.
- Associated warehouses: optional supplements.
- Associate: pick from "Unassociated Warehouse" (must already have products linked), right arrow, Save; confirmation "The warehouse is now associated with the store."
- Storefront stock = default + associated. Deduction = default first, then associated in order. Back-ordering takes the default negative after all reach 0.

## Warehouse record
OMS > Warehouses: Add New (Code unique, Name, address details; address is used as shipping origin) > Save > **Associated SKUs** tab. Edit icon; Delete icon (page reloads with confirmation). Inventory is associated to a warehouse when first created; alternates can be linked per SKU; a SKU may have no warehouse.
Returns: Shipping To address of a return is the store's default warehouse address.

## Grid
OMS > Inventory: SKU, Product Name, Warehouse Code, Warehouse, Quantity On Hand, Action; Columns adds more. Edit and Delete only. Filters, bulk actions: not described.

## API and events
Not confirmed (no spec). Inventory create, read, update and delete operations are expected in the API reference; locate with `nd_query_spec.py` and mark unverified until read. No inventory event is documented (`sdk-events-and-webhooks`).

## Not documented
Import column rules (use the template), reservation, restock on return, warehouse deletion restrictions, low-inventory threshold semantics (below or equal), the per-store attribute for back-in-stock notices.
