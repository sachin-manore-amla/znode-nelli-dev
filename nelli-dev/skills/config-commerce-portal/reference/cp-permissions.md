# Commerce Portal permissions
Answers: the full list of Commerce Portal permissions, how they combine, and where they are set.
Tags: [KB] KB read in full, [S] source.

Set on a role of type Commerce Portal: **Dev Center > Roles & Access Rights > Commerce Portal Permissions** (columns Object, Permission Name, Is Allowed). Give the role to the user on **Users > Roles**. [KB][S]

| Object | Permission Name | Meaning |
|---|---|---|
| Security | Access Order Management | sign in to Commerce Portal |
| User Profile | Can Delegate | add delegates |
| Orders | Can Be Assigned to Orders | orders can be assigned to the user |
| Orders | Edit My Orders | edit owned orders |
| Orders | Edit My Team Orders | edit orders sharing a user group (needs See My User Groups Orders) |
| Orders | Edit All Order | edit all |
| Orders | Create Orders | create orders |
| Orders | Cancel Orders | cancel |
| Orders | Change Prices | edit line prices |
| Orders | See My User Groups Orders | view team orders |
| Orders | See Next Unassigned Order / See All Unassigned Orders | queue visibility |
| Orders | See All Orders | view all |
| Orders | Assign to Me / Assign to My Team / Assign to Anyone | assignment (targets need Can Be Assigned to Orders) |
| Orders | Unassign Orders | clear owner |
| Orders | Change Order Line Status | line status |
| Orders | Set Any Order Status | line and order status |
| Orders | Change CSR Discount | CSR discount |
| Orders | Share Views with Everyone / Share Views with User Groups | saved views |

Rules: the broader permission overrides the narrower (All beats My Team beats My). An order must also be in a status with Allow Editing. Screens without permission show a "No permission" page. Create Order needs Create Orders. Custom permissions for Application Type Commerce Portal can be added (`config-roles-permissions`) but Commerce Portal does not enforce them [S, I]. API: `GET /UserRolesAndPermissions/{userId}` and `/ItemLevelPermissions/{orderId}/{orderStateId}` (Internal). [S]
