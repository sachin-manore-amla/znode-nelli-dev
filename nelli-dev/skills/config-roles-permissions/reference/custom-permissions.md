# Custom permissions
Answers: how to define a custom permission, allow it per role, read it from custom code, and what the rules and messages are.
Tags: [S] source and public spec, [I] inference.

## What it is
A permission you name (Object + Permission Name + Permission Code + application type) and allow or deny per role. Znode stores it and returns it through the API. No Znode screen, API or webstore code reviewed checks it, so enforcement is your code's job. [S]

## Admin steps
**Dev Center > Roles & Access Rights**, open a role, tab **Custom Permissions**. Pick an **Application Type** filter, click **Add Permission** (dialog **Add Custom Permission**), fill fields, **Add**, then tick the permission for the role and save the role. [S]

| Label | Rule |
|---|---|
| **Object** | Required, max 50, `^[a-z0-9 _&-]+$` (lower case). Called the menu name in the API |
| **Permission Name** | same rule |
| **Permission Code** | Required, max 50, lower-case letters, digits, `_`, `-` between words, no spaces |
| **Application Type** | Admin, Commerce Portal, Webstore, Others (`Custom_Admin`, `Custom_Commerce_Portal`, `Custom_Webstore`, `Custom_Others` in the API; `Custom_All` only as a filter) |

Messages: `Input is required.`; `The input field value cannot exceed 50 characters.`; `Only lower case letters are allowed. No special characters are allowed except -, _ and &`; `Only lowercase letters, - and _ are allowed in between two words. No spaces allowed.`; `Custom Permission Created Successfully.`; `Custom Permission Access Updated Successfully.`; `Custom Permission Deleted Successfully.`; `Failed to retrieve permissions data`; `Failed to Update Custom Permission Access.` [S]
API wording: `The value of the object is required.`, `The value of the permission code is required.`, `Unable to delete custom permission's access.` [S]
Delete asks you to type `Delete`; it removes the permission **for every role**, not only the open one. [S]

## API (Core v2)
| Method and route | Purpose |
|---|---|
| `GET /v2/custom-permissions?applicationType=&roleName=` | List |
| `POST /v2/custom-permissions` | Create (`Object`, `PermissionCode`, `PermissionName`, `ApplicationType`, `IsAllowed`, `RoleName`) |
| `DELETE /v2/custom-permissions?applicationType=&...` | Delete (application type, object, code, name) |
| `GET /v2/custom-permissions/{applicationType}/check-if-exists` | Duplicate check |
| `PUT /v2/custom-permissions/{roleName}` | Set allowed flags for a role |
| `GET /v2/custom-permissions/roles/{usernames}` | Permissions per user's role (`PermissionsByRole[]` with `UserName`, `RoleName`, `CustomPermissionsList[]` of `Object`, `PermissionCode`, `PermissionName`, `ApplicationType`, `IsAllowed`) |

## Using it in custom code
1. Define permission `export-orders` under Custom_Admin and allow it for role X.
2. In the Custom API endpoint, call `GET /v2/custom-permissions/roles/{username}` and require `IsAllowed` for the code. Cache briefly (`quality-performance-checks`).
3. Deny by default when the call fails. [I]

Verdict: Customizable. If a requirement says Znode itself must block a built-in action, that is a platform change.
