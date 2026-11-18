# Order flags, order types, user groups, owners and followers
Answers: how checklists, order types and team visibility are configured and behave.
Tags: [S] source, [KB] KB read in full, [M] catalogue.

## Order flags (Manage Order Flags)
Grid: Flag Code, Name Unchecked, Name Checked, Can Override, Name Overridden, Display Order.
| Field | Rule |
|---|---|
| Flag Code | required, unique, letters and digits, max 50 (`Flag Code is required.`) |
| Name Unchecked / Name Checked | required, max 50 (`Flag Name (Unchecked) is required.`) |
| Can Override | No makes the flag mandatory |
| Name Overridden | required when Can Override is Yes, max 50 |
| Display Order | required, 1 to 9999 (`Display Order should be between 1 and 9999.`) |
[S][KB]
After saving, **Associate User Groups**: only members can override; with none, overriding is not possible. Delete fails for flags in use (`Failed to delete the flag(s) as it may be associated with an Order Class.`). [KB][S]
On an order: open (unchecked), completed (checked), overridden; override icon only on flags that can be overridden and only for group members. Open flags block statuses that require completeness. Product (line) flags exist on Edit Product. [KB][M]

## Order types
Grid Type Code, Type Name. Type Code required, unique, letters and digits, max 300; Type Name max 100. **Default Flags** and **Default User Groups** appear after saving (`Associate Order Flag`, `Associate User Group`; `Order flag(s) associated successfully`, `User Group(s) associated successfully`). Choosing or changing the type on an order adds the missing default flags and groups. Deleting a type used by orders blanks it on them without a log. [S][KB]

## User groups
Created under Accounts & Users > User Groups (`config-roles-permissions`). They drive: who sees an order (My Team's), who can be assigned, who overrides flags, who a view is shared with. [KB][M]

## Owner, followers, delegates
Assign to Me, Assign To, Unassign Orders, Follow/Unfollow. Rules and the permissions needed are in `cp-permissions.md`. Delegates: **My Profile > View Delegates**, **Add a Delegate** (needs Can Delegate); candidates are admin users with a Commerce Portal role that has Can Be Assigned to Orders. [KB]
