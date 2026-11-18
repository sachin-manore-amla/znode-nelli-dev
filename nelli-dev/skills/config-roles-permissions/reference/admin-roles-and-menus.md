# Admin roles, menu access and the Menu List
Answers: how to create a role, set menu access, what the fields and messages are, and what the Menu List is.
Tags: [S] source, [KB] KB read in full, [I] inference.

## Roles: Dev Center > Roles & Access Rights
Add New, Edit (open a row), Delete (icon, confirm). Title: `Add Role & Right` / `Edit Role & Right - <name>`. [S][KB]

| Label | Rule |
|---|---|
| **Name** | Required (`Name is required.`), max 100; read-only for system roles. Duplicate: `Role name already exists. Please enter a different name.` [S] |
| **Role Type** | Required (`Role Type is required.`): Admin, Commerce Portal, B2B, Customer [S] |
| **Is Active** | Checkbox; locked while the role is assigned to users or system-defined [S] |

Delete: `Role deleted successfully.` or `Failed to delete role.` [S]. Create/Update success: `Record created successfully.` / `Record updated successfully.` [S]

## Admin Permissions tab
Grid columns: **Menu Name**, **Parent Menu Name**, **Full Access**, **No Access**, **Delete Access** (column heads for Full/No act as select-all). [S]
- Full Access grants write and edit; Delete Access adds delete. No Access hides the menu item. [S][KB]
- Saving a role clears the saving admin's cached menu list; other signed-in users see the change after signing in again [I].
- A role chosen on a custom page gets write, edit and delete on that page's menu entry (`config-admin-customization`). [S]

## Commerce Portal Permissions tab
Columns **Object**, **Permission Name**, **Is Allowed**. Full list and meaning in `config-commerce-portal/reference/cp-permissions.md`. [S][KB]

## Menu List: Dev Center > Menu List
Fields: **Menu Name** (required, max 25), **Parent Menu List** or Is Parent Menu, **Area Name** (max 20), **Controller Name** and **Action Name** (required, max 200), **Sequence Number**, **CSS Class Name**, **Is Active**. Manage Menu sets per-action permission codes. Messages: `Menu <name> inserted successfully.`, `Menu <name> updated successfully.`, `Menu deleted successfully.`, `Cannot delete this menu as it is associated with child menus.` [S]
Each item names a controller and action that already exist in the Admin; a new item does not create a screen [I]. Use custom pages for new screens. Menu operations also exist in the v1 API (`/Menu/List`, `/Menu/Create`, `/Menu/Update`, `/Menu/Delete`, `/Menu/GetMenuActionsPermissionList/{menuId}`, `/Menu/UpdateActionPermissions`). [S]

## Role API (Core v1, legacy)
`POST /Role/Create`, `GET /Role/GetRoleList`, `GET /Role/GetRole/{roleId}`, `PUT /Role/Update/{roleId}`, `POST /Role/Delete`, `GET /Role/GetPermissionList`, `POST /Role/GetPermissionListByUserName`, `GET /Role/GetRolesMenusPermissionsWithRoleMenus`. [S]

## Behaviours to know
- The Admin role is not checked against menu permissions: it sees everything. [S][M]
- A user holding only a Commerce Portal role cannot sign in to the Admin (access denied). [M]
- Release 10.5.1 (Dec 10, 2025) fixed a portal role deletion issue; 10.7.0.0 (Jan 30, 2026) fixed portal roles being removed after B2B assignment. [KB summary]
