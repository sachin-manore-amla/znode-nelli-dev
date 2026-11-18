# B Stores in the Admin Console
Answers: how an admin enables B Stores, creates and manages one, and the exact labels, rules and messages.
Tags: [S] source, [KB] KB read in full, [M] catalogue/module guide.

## Parent store: Stores > Manage > B Store Settings
| Label | Help text / effect |
|---|---|
| **Enable B Stores** | `If set to Yes, then B Store against the parent store can be created else do not.` |
| **Request B Store Page** | `If set to yes then allow request from the webstore for B Store owner or manager else do not.` (registration page on the storefront) |
| **Is Auto Approved** | approves new B Stores without an admin |
| **B Store Domain** | must start with `.` or `-`, for example `.mysite.com` |
| Theme and CSS | base look for B Stores |
Error `B Store domain already exists.` when a domain repeats. [S][M]

## Stores > B Stores (list) and Add/Manage
Titles **Add B Store** / **Manage B Store**. Tabs: **General Info**, **Contact Info**, **Design**, **Content**, **Products**, **Users**, **Sales Reps**, **Additional Attributes**, **Analytics**, **Robots.txt**. Design and Products open the B Store app embedded. [S]

| Label | Rule |
|---|---|
| Store name (parent) | required; read-only after creation |
| **B Store Name** | required, max 100, letters, digits and `- _ . & ( ) / \ ' " @ # + : ; ! ? % * space`; messages `B Store Name is required.`, `B Store Name cannot exceed 100 characters.`, `B Store Name contains invalid characters.` |
| **B Store Code** | required, letters and digits, max 100, unique: `B Store Code is required.`, `B Store Code already exists.` |
| External ID | max 50 |
| **Approved** | Yes: owners can manage the store; No: only admins via the Admin. Default No |
| **Active** | Yes: shoppers and managers can browse and shop |
| **Open Date**, **Close Date** | optional |
| **Catalog Name** | required |
| **Do you want to specify products?** | Yes makes picking categories/products mandatory (**Customize catalog**) |
| **Price List** | required |
| Access method | login required / self-register options |
| **Subdomain** | required (`Subdomain is required.`), must not start with `.` or `-`, letters and digits; unique |
Customer service email (required, max 50) and phone (required, max 30) are set in Contact Info. [S]

## Other actions
Copy B Store (**Copy B Store**, new name and subdomain; `Copy`/`Failed to copy` messages), Delete, **Publish** (confirmation `Please select publish options & click "Proceed" to publish the B Store.`; publishes all locales), Associate Catalogs, Associate price lists (**Available B Store Catalogs/Price Lists**), associate users (`User Associated to B Store successfully.`), sales reps, bulk reset password, create customer, B Store Access tab on a user (`Associate B Stores`). [S]
Error `Unable to launch B Store application.` when the embedded app fails. [S]

## Who can do what
Admin: everything above. Owner: create, duplicate, all pages. Manager: settings, design, products, users, orders; no create, no duplicate, no quotes page. [M][KB]
