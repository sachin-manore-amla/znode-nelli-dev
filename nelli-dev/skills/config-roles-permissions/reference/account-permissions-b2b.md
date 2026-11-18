# B2B account roles and account permissions
Answers: the three storefront account roles and how account permissions are defined and given to users.
Tags: [S] source, [KB] KB read in full.

## Account roles (storefront only)
| Role | Users | Orders | Child accounts | Shipping address at checkout |
|---|---|---|---|---|
| Administrator | manages all | all, incl. child accounts | yes | can change |
| Manager | none | own account's | no | can change |
| User | none | own | no | default address only |
None of them can open the Admin Console. [KB] See `commerce-b2b-accounts`.

## Account permissions: Customers > Accounts > Manage > Permissions
Create: **Permission Name** (required, `Permission Name is required.`, max 300: `Permission Name should not exceed 300 characters.`) and **Permission Access** (required, `Permission Access is required.`; list limited to B2B access levels). Edit, delete, unique-name check per account. Created message `Record added successfully` style; failure `Failed to create.` [S]
A user is given one account permission (purchasing level) in the user's account tab. What each level changes at checkout is not stated in the KB article read; levels connect to approval routing (`commerce-b2b-accounts`). [KB]
API: v1 `GET /AccessPermission/AccountPermissionList`, `GET /AccessPermission/AccessPermissionList`, `GET /AccessPermission/GetAccountPermission`, `POST .../CreateAccountPermission`, `PUT .../UpdateAccountPermission`, `POST .../DeleteAccountPermission`; v2 `POST /v2/account-permission-setting`, `PUT /v2/accounts/{accountId}/permissions`, `GET`/`POST /v2/accounts/{userName}/user-permissions`. [S]
Verdict: configuration is Supported; new permission levels with new built-in behaviour are a platform change.
