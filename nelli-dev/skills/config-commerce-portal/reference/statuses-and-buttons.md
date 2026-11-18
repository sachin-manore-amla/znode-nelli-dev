# Order statuses and quick status buttons
Answers: every status field and behaviour flag, the validations of Require Completeness, buttons, delete rules and store defaults.
Tags: [S] source, [KB] KB read in full, [M] module guide.

## Where
**Commerce Settings > Manage Order Statuses** (System Settings). Grid: Status Code, Status Name, Display Order, Show Customer, Editable, Send Email, Require Completeness, Working/Not Shipped, System Defined; names shown in their colours. [KB]

## Fields
| Label | Rule |
|---|---|
| Status Code | required, unique, letters and digits, max 50 (`Status Code field is required`, `Status Code cannot exceed 50 characters`, `Only alphanumeric characters are allowed.`) [S] |
| Status Name | required, max 50 (`Status Name field is required`) |
| Display Order | required, 1 to 99999 |
| Background Color / Text | required (`Background color field is required`, `Text color field is required`); preview "Will Display As" |
[S]

## Behaviour flags (Yes/No)
| Flag | Effect |
|---|---|
| Allow Editing | No makes orders view-only in Commerce Portal |
| Send Email | Yes sends order emails only if templates exist; receipts go at the first status with Require Completeness Yes; Canceled Order Receipt on the system "Canceled" |
| Require Completeness | Yes validates before the change: user info, open flags, no products, NA/NA variants, missing price, product status, inventory and back-order, min/max quantity, removed catalog/category, open line flags, ship-to, shipping method, bill-to, PO number, expired or empty vouchers and coupons, CSR discount above subtotal |
| Working/Not Shipped | feeds Smart View sections |
| Trigger Finalized Date | sets the finalized timestamp |
| Set Order Lines | also moves line items |
| Show to the Customer, Timeline Only if Active | not used in this release |
[KB]
Guidance: INPROGRESS for carts/checkout should have Require Completeness False and Allow Editing True; webstore default statuses should have it True. [KB]

## Order Class section and buttons
**Add Order Class** associates classes (`Order Class(es) associated successfully.`); Delete removes the link only. **Quick Status Buttons**: Button Text (max 100), Status (excludes itself), Display Order (1 to 99999, lowest left), **Required Permission** (any Commerce Portal permission). Message `Default order status button can not be deleted.` [S][KB]

## Delete
System-defined statuses and statuses used in a class cannot be deleted; a status that is a store's Commerce Portal default is protected. [KB][M]

## Store defaults
**Stores > Manage > Commerce Portal Settings**: **Order Status** (Orders class) and **Quote Status** (Quotes class), heading **Commerce Portal Default Settings**. Messages `Record updated successfully.` / `Failed to update record.` Applies to new orders only; takes effect at once, no publish. Keep them different from the webstore defaults. [M]

## In Commerce Portal
Status list needs **Set Any Order Status**; cancel needs **Cancel Orders**; line status needs **Change Order Line Status**. [KB]
API (Internal): `GET/POST/PUT /Statuses`, `/StatusButtons`; public: `GET /{classType}/class-status-list`. [S]
