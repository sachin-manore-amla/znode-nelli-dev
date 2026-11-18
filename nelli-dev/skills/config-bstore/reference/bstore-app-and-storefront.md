# B Store app and storefront behaviour
Answers: what owners and managers can do in the B Store app, what shoppers see on a B Store, and the limits.
Tags: [KB] KB read in full, [M] catalogue/module guide, [I] inference.

## Getting in
Storefront **My Account > Manage Stores** (also header menu) appears when **Is Owner** or **Is Manager** is Yes; it opens the B Store app in a new tab through an access link. With no stores: `Currently, you do not have any B Stores assigned`. Users with neither flag can submit **Requesting B Store Access**: First/Last Name, Email, Company, Address, City, State, Postal Code, Phone, Terms and captcha; **Register** sends it to the admin (only when the parent has Request B Store Page on). Expired link shows a session-expired page. [KB][M]

## Pages
Sidebar: Dashboard, Store Settings, Design, Products, Users, Orders, Quotes (managers see no Quotes). [M]
- **B Stores Dashboard:** card per store (name, link, dates, approval, active toggle), **Manage Store**, **Duplicate Store** (owners; new name and subdomain; copies settings, catalog, design, not users or orders; starts inactive), **Add New Store** (owners). [KB][M]
- **Add New Store wizard:** Tell Us About Your Store (Store Name, Description, Subdomain, Customer Can Self-Register, Require Login, Show Pricing) > Branding (logo, favicon, colours) > Products (Do You Want to Specify Products?) > Completion. Limits of the KB article are not stated; the app checks subdomain availability live. [KB][M]
- **Store Settings:** Approved (read-only), Active, Open/Close Date, Subdomain (read-only), Catalog, products switch, Price List (read-only), Customer Support Email/Phone, self-register, Required Login, Show Pricing. [KB][M]
- **Design:** Store Title, Description, Logo (.jpg .jpeg .png .svg .webp .gif), Favicon (.ico .webp), Primary Color, Heading Text Color, Secondary Color, Light Text Color, custom CSS editor; unsaved-changes warning. [KB][M]
- **Content:** Store-Wide Header Message, Checkout Message, Home Page Banner Title and Sub Title, Store-Wide Promotion Message (home page). Length limits not stated. [KB]
- **Products:** category tree, checkboxes, include whole category, 25/50/100 per page; read-only when specifying products is off. [KB][M]
- **Users:** list (User Name, Full Name, Email, Role, Status), add (role User or Manager; Owner cannot be picked), edit, lock/unlock, reset password email, CSV/Excel upload (columns User Name, Email Address, First Name, Last Name, Role Name, Is Active; template download; statuses Started, Completed Successfully, Completed with Errors, Failed). Duplicate user name in a store is refused. [KB][M]
- **Orders/Quotes:** sample data only in the current app. [M]

## Shopper side
Per KB, a B Store needs Approved, Active and the date window. Cart hides Place Order and checkout is blocked when the store does not allow orders or is not approved; quote requests follow the store's setting; guests cannot request quotes; quick order and order templates are not available. Inactive store shows an inactive page. Two-factor settings apply to B Stores (`Managing Two Factor Authentication`). [M][KB]

## Extension layer
The B Store app has a per-customer extension layer (override pages, components, services, add routes) and can use GraphQL or REST. Whether the app source is supplied to customers is not verified here. [M][I]

## KB versus product
KB "B Store Orders" describes a working order list; the module guide finds sample data only. KB leaves several limits "not stated" (name, subdomain, file sizes): use the Admin rules in `admin-configuration.md`. Product wins.
