# Limits, security, behaviours to know, KB versus product
Answers: what is enforced and what is only advised, why a page may be blank or blocked, and where the KB and the product disagree.
Tags: [S] product source, [KB] KB read in full, [I] inference.

## Enforced limits
| Item | Limit | Source |
|---|---|---|
| Code | max 25, starts with a letter, letters and digits, unique ignoring case | [S] |
| Name | max 25, letters, digits, spaces | [S] |
| Content Type | `URL` or `RawHTML` (shown as `RawHTML Or iFrame`), max 20 characters | [S] |
| Sequence Number | 1 to 100 | [S] |
| Content Details | required, no size limit set in the Admin model | [S] |
| Roles | at least one; only Admin-type roles are offered | [S] |
| Pages in the left menu | the sidebar lists the first nine pages, then **Show More** | [S, I on exact count] |
| Entities | the 20 in `entities-and-macros.md` | [S][KB] |

Behaviour to know: the length messages shown for Name and Code may quote 100 or 200 characters even though 25 is enforced. Trust 25. [S]

## What the KB says is limited
- Validation of HTML and URL content is limited. [KB]
- Pages and sections cannot be converted. [KB]
- Some entities may not exist in all releases. [KB]
- Changes take effect immediately after saving. [KB] (see timing in `pages-and-sections.md`)

## Security model (read before recommending a page)
1. **Trusted code.** Raw HTML is inserted into the Admin page without sanitising. Anyone who can edit Admin Customizations can run script in the admin of every user who opens the page. Limit the **Admin Customizations / Manage Pages** permission to a small role. [S]
2. **Credentials sent to the URL.** For content type `URL`, Admin calls the address from its server with a Basic header built from its API domain name and key. A URL on a host you do not control would receive those credentials. Use only your own Custom API host. [S]
3. **Your host must check that header.** The SDK attribute does. A page without it can be opened by anyone who knows the address. [S]
4. **Macros are identifiers, not authorisation.** Re-check in your Custom API that the signed-in admin may see the record; do not trust a macro value from a browser. [I]
5. **Content Security Policy.** The Admin sets its own policy. The product default allows frames only from a short list, restricts form posts to the Admin's own origin (`form-action 'self'`) and limits script sources. A form that posts to your Custom API host or a frame on another host is blocked until the policy is widened in the Admin's CSP global setting (**Dev Center > Global Settings**, attribute `AdminContentSecurityPolicy`). The release 10.10.1.0 (May 12, 2026) note says the default Storefront policy no longer allows inline scripts; it does not say whether Admin pages are affected, so test inline scripts and `onclick` handlers on your environment. [S][KB]
6. **CORS.** Your host must list the Admin origin in `ZnodeAdminURLCorsPolicy`. [KB][S]

## Why a page is blank, missing or denied
| Symptom | Likely cause | Check |
|---|---|---|
| Page not in the menu | Disabled; user's role not selected; not yet signed in again; more than nine pages (see Show More) | Role list, status, sign in again |
| `Access Denied. Please contact a Site Administrator.` | The user's role is not on the item, or no Manage Pages access | Edit the item's roles |
| Content area empty | Empty RawHTML; URL returned an empty body | Open the URL through the Admin |
| `Error loading content: ...` | The Admin server could not reach the URL or got a non-success code | Reachability from the Admin network, 401 from `ValidateAuthHeader` (key mismatch), TLS |
| Form post does nothing or fails in the browser console | CORS or CSP `form-action` | Origins list, Admin CSP |
| Section missing on an entity | Wrong Entity Type; entity not supported | `entities-and-macros.md` |
| Macros appear as literal `#Name#` | Case or spelling differs, or macro not offered for that entity | Compare with **Available Macros** |
| Edited content still old | The page model is kept in the admin session [I from source reading] | Sign out and in |

## KB versus product
| Topic | KB | Product | Wins |
|---|---|---|---|
| How URL content is shown | "iframe", multi-page navigation inside the iframe | Fetched by the Admin server and inserted into the page; RawHTML may contain an iframe tag | Product |
| Common macros | four listed | five (also `#username#`) | Product |
| Menu path | "Admin Customization > Manage" and "Dev Center > Admin Customizations" | **Dev Center > Admin Customizations** is the menu entry | Product |
| Immediate effect | immediate after save | menu lists are cached per signed-in session | Product (I) |
| Supported entities | 20 listed | same 20 | agree |

Release note: 10.0.1.0 (May 12, 2025) added the WYSIWYG editor for Content Details when the content type is RawHTML or iFrame. [KB]

## Environment promotion
Not stated in the KB. No export or import was found in the Admin. Treat pages as per-environment configuration, keep a record of every page (code, name, type, address, roles, sequence) in your repository and recreate it in each environment. [I]
