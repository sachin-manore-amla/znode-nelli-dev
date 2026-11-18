# Admin Customization API operations
Answers: which API operations create, read, change, enable, disable and delete custom pages and sections, and what they require.
Tags: [S] product source and public spec, [I] inference.

These operations belong to the **legacy Core API v1** family (`api-catalog` rule: no new work on v1 unless nothing else exists). No v2 or Commerce equivalent was found. Prefer the Admin screens; script these only to record or recreate pages, with the developer's approval. Auth: gateway token as for other v1 calls (`api-auth-and-headers`).

| Method and route | Purpose | Key fields |
|---|---|---|
| `GET /AdminCustomization/Pages` | List pages and sections | filter, sort, `pageIndex`, `pageSize` |
| `GET /AdminCustomization/Pages/{code}` | One page or section | response includes `SelectedRoles` |
| `POST /AdminCustomization/Pages` | Create | body below |
| `PUT /AdminCustomization/Pages` | Update (by `Code`) | same body |
| `DELETE /AdminCustomization/Pages/{code}` | Delete one | |
| `POST /AdminCustomization/Pages/Delete` | Delete many | JSON array of codes |
| `PUT /AdminCustomization/Pages/{code}/Enable` and `/Disable` | One | |
| `PUT /AdminCustomization/Pages/Enable` and `/Disable` | Many | JSON array of codes |

Request body (create and update): `Code`, `Name`, `ContentArea` (`CustomPages` for a page, `CustomSections` for a section), `EntityType`, `ContentType` (`URL` or `RawHTML`), `ContentDetails`, `SelectedRoles` (list of `{Code, Name}` with the role id as Code), `IsEnabled`, `SequenceNumber`, optional `AdminPageURL`. [S]

Rules enforced by the API (not by the field attributes of the Admin screen):
- `Code` required; duplicate code is refused (`<code> already exists.`).
- `ContentDetails` must be **Base64**; otherwise `The content details are not encoded in Base64 format.` [S]
- The API does not repeat the Admin's 25-character, letter-start and sequence-range checks [I: not seen in the service]; keep to the screen rules.
- Roles you list receive Write, Edit and Delete access on the page's menu entry. [S]
- Success for bulk operations is a true/false response; failure has the messages in `pages-and-sections.md` (API wording: `The page/section(s) has been enabled successfully!`, `The page/section(s) has been disabled successfully!`, `The Pages/Section(s) have been deleted successfully!`). [S]

Role ids come from the role operations (`config-roles-permissions`).
