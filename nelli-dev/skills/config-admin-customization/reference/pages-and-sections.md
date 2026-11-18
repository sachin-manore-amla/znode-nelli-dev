# Custom pages and sections: screens, fields, messages
Answers: where to create, edit, enable, disable and delete a custom page or section, the exact labels and rules, and who sees the result.
Tags: [S] product source, [KB] KB article read in full, [I] inference.

## Where
**Dev Center > Admin Customizations** (KB: "Admin Customization > Manage"). The list shows all pages and sections. Columns include the content area (`Custom Page` or the entity name), name, code, sequence (blank for sections) and a content link. [S][KB]

Permissions needed: the Admin Customizations screens and Manage Pages access in the signed-in admin's role (KB). Roles without access get **Access Denied. Please contact a Site Administrator.** [KB]

## Create
1. Click **Add New**, then **New Page** or **New Section** (KB). The create screen is titled **Add Custom Page**; the Edit screen is titled `Edit - <name>`. [S]
2. Fill the fields below, then **Save** or **Save & Close**.
3. Success message: `Record created successfully.`

| Label | Rule | Notes |
|---|---|---|
| **Content Area** | `Page` or `Section` switch | Locked after creation [S] |
| **Code** | Required, starts with a letter, letters and digits only, max 25, unique | Message: `Only alphanumeric characters are allowed and the code must start with a letter.` Duplicate: `<code> already exists.` Not editable later [S][KB] |
| **Name** | Required, letters, digits and spaces, max 25 | Message: `Only alphanumeric characters are allowed, please remove all special characters.` Shown as the menu text or the section tab text [S] |
| **Entity Type** | Required for a section | Dropdown of the 20 entities. Help text: the section appears inside the chosen entity, for example under **PIM > Pricing Engine > Edit Pricing** [S] |
| **Available Macros** | Read-only hint under Entity Type | Updates when the entity changes [S] |
| **Content Type** | `URL` or `RawHTML Or iFrame` | Required [S] |
| **Content Details** | Required | The address (URL) or the HTML. A WYSIWYG editor appears for RawHTML/iframe since release 10.0.1.0 (May 12, 2025) [KB] |
| **Select Roles** | At least one role, or tick **All Roles** | No role: `No roles have been selected. Please choose at least one role and try again.` [S] |
| **Sequence Number** | 1 to 100, default 99, pages only | Message: `Sequence Number should be between 1 to 100.` [S] |
| **Enable Page** | Checkbox, on by default | [S][KB] |

The Admin Base64-encodes Content Details before it calls the API; the API refuses content that is not Base64 (`The content details are not encoded in Base64 format.`). This matters only if you call the API yourself (`admin-api.md`). [S]

Saving gives the chosen roles Write, Edit and Delete access on the new menu entry. [S]

## Edit
Open the row. Content Area and Code are disabled. Everything else can change. Success: `Record updated successfully.` Failure: `Failed to update record.` Roles can be changed; at least one is required. [S]

## Enable, disable, delete
| Action | Where | Message |
|---|---|---|
| Enable / disable one | Row action | `Record(s) enabled successfully.` / `Record(s) disabled successfully.` |
| Enable / disable several | **Tools** menu on selected rows | same |
| Delete one or several | Row delete or **Tools** | `Record(s) deleted successfully.` |
| Delete fails | | `Unable to delete the provided list of page/section(s).` |
| Enable/disable fails | | `Unable to enable the page/section(s) for the provided code.` / `Unable to disable the page/section(s) for the provided code.` |
| Nothing matches | | `The page or section associated with the provided code cannot be found or accessed.` |
| Empty list | | `No records found.`; long lists use **Show More** |

[S][KB]. Filters work on grid columns such as status. [KB]

## How a page or section is shown
- **Page:** listed in the left menu under **Custom Pages** in sequence order; equal sequence numbers sort by creation order (KB). The page opens with its name as heading and a Cancel button only (Save buttons are hidden). Multi-page navigation inside the content works as long as it stays in the same frame (KB). [S][KB]
- **Section:** added as a link or tab in the entity's side panel. Clicking it loads your content into the screen area without a full page reload. [S]
- **Content Type URL:** the Admin server calls the URL and shows the response body as HTML. If the call fails, the page shows `Error loading content: <reason>`. [S]
- **Content Type RawHTML Or iFrame:** the pasted HTML is shown as it is. Empty HTML shows nothing. [S][KB]
- Macros in Content Details are replaced for both content types. [S]

## Who sees it
| User | Result |
|---|---|
| Admin role (system administrator) | Sees all enabled pages and sections [KB][S] |
| Other admin user | Sees only items whose roles include one of the user's roles [S] |
| Item disabled | Not listed |
| User lacks the role and opens the address directly | `Access Denied. Please contact a Site Administrator.` is shown in place of the content [S] |
| Commerce Portal user, shopper, B2B account user | No effect. This feature only touches the Admin Console [S] |

## Timing
KB: changes take effect immediately after saving. Source: the editing admin's own menu list is refreshed on save; other signed-in admins keep a menu list in their session, so a new page or role change may appear for them after they sign in again [I from source reading; not checked on a running environment]. If a page you edited still shows old content for you, sign out and in [I, see `security-and-limits.md`].
