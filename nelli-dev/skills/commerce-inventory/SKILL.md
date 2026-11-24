---
name: commerce-inventory
description: Znode inventory and warehouses - inventory records per SKU per warehouse (Quantity On Hand, Reorder Level, the unconnected backorder fields), creating and editing inventory in OMS, in the product and by import, warehouses and the shipping-origin role, the store default and associated warehouses with display and deduction order, out-of-stock and backorder options and storefront messages, low-inventory and back-in-stock emails, near-real-time versus cached stock display, and the customization verdict per need (ERP stock sync, reservations, per-customer stock). Load it for any stock level, warehouse, backorder, availability message or inventory integration requirement, and when stock looks wrong on the storefront.
user-invocable: false
---

# Inventory and warehouses

Sources: Znode Knowledge Base articles Configuring Inventory, Managing Inventory (OMS), Managing Inventory (store, Stores & Warehouses), Managing Inventory for a Product, Configuring a Warehouse, Managing Warehouses, Understanding Default Email Templates, Storefront Performance and Caching Guidance, Managing Returns (read 2026-11-23). No exported API spec for inventory was available: API statements are unverified. Confidence 85 for Admin behaviour.

## Model in one paragraph
Stock is tracked **per SKU per warehouse**. A warehouse has a code, a name and an address that serves as the **shipping origin**. A store has one required **default warehouse** and optional **associated warehouses** that supplement it. Inventory can be created in OMS, from a product, or by import; all views stay synchronized, and storefront orders update the levels automatically. (KB 85)

## Twelve facts that matter
1. Admin views: **OMS > Inventory** (all), **PIM > Products > product > Inventory** tab; both show the same records. (KB 85)
2. Record fields: **SKU** (cannot change after creation), **Warehouse**, **Quantity On Hand**, **Reorder Level**, **Backorder Quantity**, **Backorder Expected Date**. Create: Add New, enter SKU (or Browse), warehouse, quantities, Save. (KB 85)
3. **Backorder Quantity and Backorder Expected Date are not bound to the backorder function**: they exist for custom business processes. Do not expect them to gate purchases. (KB 85)
4. **Reorder Level** is the monitoring threshold; low-inventory notifications can be generated when quantity reaches it. (KB 80)
5. Out-of-stock behaviour is set by two rules: **Disable Purchase for Out-of-Stock Products** and **Allow Back-Ordering of Products**; storefront labels are In Stock, Out of Stock, Back Ordered / Available for Backorder; messages **In-Stock Message**, **Out-of-Stock Message**, **Backorder Message** are set in inventory settings. A "do not track inventory" option exists per earlier notes: unverified in these articles. (KB 80)
6. Storefront stock quantity is the **sum** of the default and associated warehouses. (KB 85)
7. An order draws stock from the **default warehouse first**, then associated warehouses. Example: 1 in the default and 5 in an associated one lets a shopper order 1 to 6. (KB 85)
8. With back-ordering on, stock is drawn from the default, then the associated warehouse; after both reach 0 the **default warehouse goes negative**. (KB 85)
9. The **product detail page** updates in near real time; the **listing page** may show cached inventory: check in another browser or a private window. (KB 80)
10. Store association: Stores and Reps > Stores > Manage > Inventory tab: add a default warehouse; associate others by selecting from the "Unassociated Warehouse" table and moving it with the right arrow, then Save. The warehouse needs products linked already. (KB 85)
11. An SKU can have alternate warehouses; if the primary is out of stock the alternates supply it; an SKU may also be left without any warehouse. (KB 80)
12. Bulk: System Setup (Settings) > Import > type **Inventory**, template download, upload; creates records for the listed SKUs and warehouses. Import matches and column details: `config-import-export` (earlier notes: key columns SKU, Quantity, WarehouseCode; add or update only: unverified here). (KB 80)

## Grid and actions (OMS > Inventory)
Default columns SKU, Product Name, Warehouse Code, Warehouse, Quantity On Hand, Action; more via **Columns**. Edit (Quantity On Hand, Reorder Level, Warehouse, Backorder fields) and Delete (confirm). Filters and bulk actions are not described.
Warehouses (OMS > Warehouses): Add New (Code unique, Name internal, Address details used as shipping origin), after Save an **Associated SKUs** tab shows linked SKUs; Edit; Delete (no restrictions documented beyond a confirmation).

## Emails
| Template | Purpose |
|---|---|
| Low Inventory Order Notification (administrator) | an order caused low or negative inventory; macros `#StoreName#`, `#OrderId#`, `#OrderDate#`, `#SKU#`, `#Quantity#`, `#StoreLogo#` |
| Send Waiting List Notice In Inventory (customer) | a previously unavailable item is back in stock; macros `#StoreName#`, `#ProductName#`, `#SKU#`, `#EmailAddress#`, `#Image#`, `#ProductLink#`, `#Url#` |
Enable templates per store (`config-notifications`). The store attribute that enables back-in-stock notification is named only in earlier notes (unverified).

## Nelli-Dev decision guide
| Requirement | Verdict | Route |
|---|---|---|
| Show stock per warehouse to shoppers | Customizable | Admin shows per warehouse; storefront sums them; a custom component needs an inventory read operation (unverified, find in the API reference) |
| Nightly ERP stock sync | Supported | Inventory import, or an integration calling the inventory create/update operation (`config-import-export`, `sdk-data-exchange`); then expect PLP caching delay |
| Real-time ERP check at add to cart | Customizable, risky | Custom endpoint in your own service called by your Webstore component; keep it off the checkout critical path; fail open or closed deliberately (`quality-performance-checks`) |
| Reserve stock for a pending order or quote | Not documented | Inventory updates on order placement; no reservation concept in the articles; ask Znode |
| Backorder with an expected date shown to shoppers | Customizable | Backorder Expected Date is stored but not used: display it yourself from the record; unverified read route |
| Different stock for B2B accounts | Needs platform change / Customizable | Stock is per warehouse and store; use separate stores with different default warehouses or a custom check |
| Stop selling at zero | Supported | Disable Purchase for Out-of-Stock Products |
| Sell past zero | Supported | Allow Back-Ordering of Products |
| Low stock alert to a buyer ("only 3 left") | Customizable | Read quantity on the server in a component; do not cache per-user |
| Pickup warehouse chosen at checkout | Customizable | Store locations and warehouse origin; per-order warehouse choice is not documented |
| Return restocks inventory | Not documented | The returns articles say nothing about restocking: confirm before promising |

## Pitfalls
- Expecting backorder quantity or date to change purchasing.
- Changing a SKU on an inventory record (cannot): delete and recreate.
- Associated warehouse without inventory for the SKU.
- Negative default warehouse after backorders: reconcile with import.
- Judging stock from the listing page right after a change (cache).
- Warehouse address wrong: it is the shipping origin for rates (`commerce-tax-shipping`).

## Reference files
- `reference/inventory-and-warehouses.md` – forms, field rules, store association, deduction examples, import, messages.

Related: `commerce-catalog`, `commerce-orders`, `commerce-returns`, `commerce-tax-shipping`, `config-caching`, `config-notifications`, `config-import-export`.
