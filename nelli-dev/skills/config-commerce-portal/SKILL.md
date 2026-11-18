---
name: config-commerce-portal
description: What can be configured and customized in the Znode Commerce Portal (the staff order desk) - order classes and number formats, class change buttons, order statuses and quick status buttons, order flags, order types, user groups, owner/followers/delegates, Smart View and saved views, dashboard, store defaults, the Commerce Portal permissions, and the classType-based Commerce API surface - plus what needs the Custom API SDK and the verdicts. Load it for any request about sales-rep or CSR order handling, extra order fields, order workflow, or integrating with Commerce Portal orders.
user-invocable: false
---

# Commerce Portal configuration

Tags: **[S]** source/spec (90+), **[KB]** KB read in full (80), **[M]** catalogue map, **[I]** inference.

## What it is
A separate staff application for creating and managing orders, quotes and carts. Almost everything is configured in the **Admin Console** (System Settings > Commerce Settings per the product; the KB also says "Commerce Portal Settings under Dev Center"). Two terms: **Order class** (system-defined record kind: orders, quotes, carts...) versus **Order type** (business-defined label that brings default flags and groups). [KB][M]

## The 10 facts that matter
1. Classes are Znode-defined; you can edit number settings and class change buttons, not create or delete classes. KB: in 9.9 only Orders is supported for configuration. [KB]
2. Order number = **Number Format** with `<MM>`, `<DD>`, `<YY>`, `<YYYY>`, `<Number>`; format max 35 characters, must be unique across classes. [KB][S]
3. Statuses carry behaviour flags (Allow Editing, Send Email, Require Completeness, Working/Not Shipped, Trigger Finalized Date, Set Order Lines). `Require Completeness` runs validations before the change. [KB]
4. Flags are checklists; open flags block statuses that require completeness. Only members of a flag's override user groups can override it. [KB]
5. Quick status buttons need a **Required Permission**; class change buttons move an order to another class and status. [KB]
6. Sign-in needs **Access Order Management**; there are more than 20 permissions (`reference/cp-permissions.md`). [KB]
7. Each store has default Commerce Portal order and quote statuses (**Stores > Manage > Commerce Portal Settings**). [M]
8. Commerce Portal data is read and written through the Commerce API using `{classType}` routes. [S]
9. There is **no supported way to add fields to the Commerce Portal screens**. Custom data on lines is possible through line custom data and attribute operations (`reference/cp-api-surface.md`). [S][I]
10. Admin-config operations in the API are marked Internal; integrators use the order operations only. [S]

## Nelli-Dev decision guide
| Request | Verdict | How |
|---|---|---|
| Let a sales rep see extra order fields | Needs platform change for new on-screen fields; Supported if the fields are existing ones (roles/views) | Saved views choose columns; custom fields: line custom data via API only. `reference/cp-api-surface.md` |
| New order workflow step/status | Supported | Create status, flags, quick buttons. `reference/statuses-and-buttons.md` |
| Order number like `AMLA-<MM>-<DD>-<Number>` | Supported | Order Classes number format |
| Require a credit check before completion | Supported | Flag without override, status with Require Completeness |
| Assign by team | Supported | User groups, order types. `reference/flags-types-teams.md` |
| Push orders to ERP when status changes | Customizable | Events/webhooks, `sdk-events-and-webhooks` |
| Show ERP data inside Commerce Portal | Needs platform change | Offer a Custom API plus an Admin custom page (`config-admin-customization`) for staff who use the Admin |
| Read a user's orders from a custom service | Customizable | `reference/cp-api-surface.md` |
| Change totals or validation rules | Customizable | `sdk-method-overrides` |

## References
`reference/order-classes-and-buttons.md` · `reference/statuses-and-buttons.md` · `reference/flags-types-teams.md` · `reference/cp-permissions.md` · `reference/views-dashboard-delegates.md` · `reference/cp-api-surface.md`

## Related
`config-roles-permissions` · `commerce-orders` · `sdk-custom-api` · `commerce-b2b-accounts` · `commerce-returns`
