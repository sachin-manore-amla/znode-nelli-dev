# User roles, user groups and per-store access
Answers: how roles, user groups and store access are assigned to admin users, and the rules.
Tags: [S] source, [KB] KB read in full, [M] module catalogue/guide, [I] inference.

## Admin users: Dev Center > Admin Users
Fields: Username, Email Address, First Name, Last Name, Phone Number, **Role Name** (decides modules), **Stores** (stores the admin manages). A super admin can reset the password with **Tools**. Add, edit, delete, lock/unlock, reset password, convert a shopper to admin exist. [KB][M]
Default admin password must be changed on first sign-in. [M]

## User roles: Users > Manage > Roles tab
**Associate Role**; grid **Role**, **Role Type**, **Action** (Delete removes). One Znode role per user, many Commerce Portal roles. Roles can also be associated per store through the v1 operations `Customer/AssociateRolesByPortalId/...` and `UnAssociateRolesByPortalId/...`. [KB][S]
An account cannot be associated with a user whose role type is only Admin or Commerce Portal. [KB]

## User groups (Commerce Portal teams)
**Accounts & Users > User Groups**: **User Group Code** (unique, required, letters and digits, max 100), **User Group Name** (required, max 100). Messages: `User group code is required`, `User group name is required`, `User Group(s) associated successfully.`, `No records found`. A user's **User Groups** tab: Associate User Groups, Priority edit, Delete. Deleting a group linked to orders or flags is allowed and not logged. [S][KB]

## Store access
- Admin: the **Stores** field limits which stores the admin can open. No assignments or All Stores means no limit; the store **list** shows nothing for a user with no assignments (module finding). A store assignment clears that user's cached store list at once; other changes can take up to 20 minutes. Refused reads return `User does not have the requested Portal Access.` [M]
- Shopper store access: **Users > Stores** tab; API `GET /v2/users-portals/{userId}`, `POST /v2/users/update-portals-configuration`, v1 `GET /User/GetPortalIds/{aspNetUserId}`, `POST /User/SavePortalsIds`. [S]
- Release 10.10.1.0 (May 12, 2026) fixed an Admin "All Store Access" removal and duplicate role assignments. [KB summary]

## Verdicts
Per-store admins, team visibility and role bundles are Supported. A role that restricts by product category or field is a platform change.
