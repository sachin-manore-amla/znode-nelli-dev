---
name: config-roles-permissions
description: How access is configured and customized in Znode - Admin roles and menu access (Dev Center > Roles & Access Rights, Full/No/Delete access, Commerce Portal permissions), custom permissions (Object, Permission Name, Permission Code, application type), user roles and user groups, per-store admin access, B2B account roles and account permissions, and API authentication (gateway JWT tokens vs Basic domain credentials). Load it for any request about who may see or do what, limiting a role to menus, a new permission for custom code, or how an integration authenticates.
user-invocable: false
---

# Roles, permissions and API authentication

Tags: **[S]** product source/spec (90+), **[KB]** KB read in full (80), **[M]** module catalogue (map only), **[I]** inference.

## Vocabulary people confuse
| Term | Meaning |
|---|---|
| **Role** | Named bundle of access. Role Type: Admin, Commerce Portal, B2B or Customer. |
| **Access right** | Per Admin menu item: Full Access, No Access, plus a Delete Access box. |
| **Commerce Portal permission** | Named switch (Object + Permission Name) on a Commerce Portal-type role. |
| **Custom permission** | Permission you define; Znode stores and returns it but enforces nothing itself. |
| **Account permission** | B2B purchasing level on an account (not a role). |
| **User group** | Team of admin users for Commerce Portal visibility (`config-commerce-portal`). |

## The 10 facts that matter
1. Roles and access: **Dev Center > Roles & Access Rights**. Three tabs: **Admin Permissions**, **Commerce Portal Permissions**, **Custom Permissions**. [S]
2. A user has **one** Znode role and **any number** of Commerce Portal roles (Users > Roles tab). [KB][M]
3. The Admin role is a system role; its name is read-only. Users in it see every menu and custom page. [S]
4. Admin access per menu is Full Access or No Access, plus Delete Access. The Read Only column exists but is hidden. [S]
5. Signing in to Commerce Portal needs **Security > Access Order Management**. [KB]
6. Custom permissions are data for your code: no screen, API or webstore code reviewed enforces them. [S]
7. Custom permission API is Core v2: `/v2/custom-permissions`. [S]
8. Admin roles can have access limited to chosen stores through the admin user's **Stores** field. [KB][M]
9. API tokens come from the gateway: application token from client name and key, user token adds user name and password; access token 30 minutes, refresh token 30 days by default. [S][KB]
10. Shoppers and B2B account users never reach the Admin Console, whatever their account role. [KB]

## Nelli-Dev decision guide
| Request | Verdict | How |
|---|---|---|
| Limit a role to certain menus | Supported | Create a role, tick Full Access only on those menus. `reference/admin-roles-and-menus.md` |
| Let a sales rep see extra order fields in Commerce Portal | Needs platform change for new on-screen fields; existing order fields as saved-view columns and the permissions are Supported (same answer as `config-commerce-portal`) | `config-commerce-portal` |
| New permission for my custom page/API | Customizable | Custom permission, check it from your Custom API via `GET /v2/custom-permissions/roles/{usernames}`. `reference/custom-permissions.md` |
| Hide a button in a built-in screen | Needs platform change | No hook |
| Separate admins per store | Supported | Admin user Stores field; `reference/user-roles-groups-store-access.md` |
| Different purchasing levels per B2B user | Supported | Account Permissions; `reference/account-permissions-b2b.md` |
| Server-to-server integration login | Supported | `reference/api-authentication.md` |
| Add a new Admin menu item pointing at my screen | Customizable via `config-admin-customization` (Menu List only edits built-in controller/action entries [I]) |

## References
`reference/admin-roles-and-menus.md` · `reference/custom-permissions.md` · `reference/user-roles-groups-store-access.md` · `reference/account-permissions-b2b.md` · `reference/api-authentication.md`

## Related
`config-admin-customization` · `config-commerce-portal` · `commerce-b2b-accounts` · `api-auth-and-headers` · `quality-security-checks`
