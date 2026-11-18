---
name: commerce-b2b-accounts
description: Znode B2B - the account hierarchy, storefront roles, user profiles and the payment/shipping intersection matrix, budgets, approval routing (Approval Type vs Approval Level, the subtotal-based threshold and the multi-level routing rule), pending orders, Open Account Billing and sales reps. Use when configuring B2B accounts, debugging why an order went to approval, or when payment methods differ per shopper.
user-invocable: false
---

# Znode B2B Accounts, Profiles & Approvals

```
ZnodePortal (store)
  └── ZnodeAccount (company)
        └── ZnodeUser
              └── ZnodeProfile (permissions, pricing tier)
```

## Accounts

Exactly **two tiers** — Parent → Child. No deeper nesting.

Fields: Account Name · Account Code · External ID (ERP) · Store · Sales Rep · Catalog override · Billing/Shipping address book · VAT / Business ID (for AvaTax).

An account controls: catalog override, multiple price lists with precedence, user profiles, a shared address book and approval routing.

> **There is no price-list inheritance from a parent account.** Verified in code 2026-09-23: price resolution never traverses upward, and no inheritance flag exists. A child account with no price lists of its own falls through to Profile, then Store — never to its parent. Evidence and the full algorithm are in `commerce-promotions-and-pricing`.
>
> What a parent account *does* get is **downward visibility** — `Fn_GetRecurciveAccounts` returns an account and its descendants, which is how parent-account admins see child-account orders.

**Storefront roles** (none has Admin Application access):

| Role | Order visibility | Addresses | User mgmt | Sees child accounts |
|---|---|---|---|---|
| Administrator | All account + child orders | Add/edit | Yes | Yes |
| Manager | Own account orders | Modify shipping at checkout | No | No |
| User | Own orders | Default account address only | No | No |

Users with the Admin role **cannot** be associated with a B2B account.

## User profiles

A **User Profile** is a named configuration controlling the shopping experience for a segment. Built-in: **Anonymous** (guests) and **Registered** (authenticated without a custom profile).

Controls: Catalog (one per profile) · Shipping methods · Payment methods · CMS Content Pages · Tax-Exempt flag · Price List.

### Payment/shipping intersection matrix

| Case | Store methods | Profile methods | Shown at checkout |
|---|---|---|---|
| 1 | A, B, C, D | none | A, B, C, D |
| 2 | A, B, C, D | C, D | C, D |
| 3 | A, B, C, D | E, F (no overlap) | A, B, C, D (store fallback) |
| 4 | A, B, C, D | Profile X: A,P,Q + Profile Y: C,D,G,H | A, C, D (union of intersections) |
| 5 | none | A, B | nothing displayed |

**Conflict resolution:** catalog and CMS visibility go to the profile with greatest admin-configured precedence; shipping/payment take the union of intersections. There is no fixed system-level rank.

> **Account** decides *what* they buy (catalog, pricing, addresses, approvals). **Profile** decides *how* they buy (payment and shipping methods).

## Budgets

`Customers > Users > Manage > Additional Attributes > Budgets`: **Per Order Limit** and **Annual Order Limit**.

- **Exceeding either limit blocks order placement entirely** — it does not route to approval.
- **Blank or `0` means no restriction.**
- The annual limit's start month is set on the store; **blank defaults to January**.

Approval Type (Does Not Require / Sometimes Requires / Always Requires) is **not** here — it lives under `Customers > Users > Manage > Approval Management`.

## Approval configuration — two orthogonal settings

Store side: `Stores > Stores > Select store > Manage store > Approval Management`.

> ⚠️ The KB is inconsistent about the location. Two articles (*Enabling Approval Management for a Store*, *Managing Pending Orders*) say a dedicated **`Approval Management`** tab; the older *User Guide for Approval Routing* says `Manage > Additional Attributes`. **Prefer the Approval Management tab** — it is the majority and the more recent wording.

**1. Approval Type** — who the threshold applies to:

| Type | Behaviour |
|---|---|
| **Store** | Any payment method; approval required when the order is above the store limit |
| **Payment** | Only orders using payment methods associated with approval management require it |
| **User** | Any payment method; approval required when the amount meets or exceeds the minimum in the **user-level approver brackets** |

**2. Approval Level** — how far it escalates:

| Level | Behaviour |
|---|---|
| **Single** | Triggered at or above *Set approval for Orders above ($)*; store-level approvers approve or reject |
| **Multi** | Triggered at the same threshold, then routed — see the routing rule below |

These are **independent selections**, not one list of five options.

### Multi-level routing rule

```
Order submitted at/above the threshold
  └─ Is the customer's Approval Type "Always Required Approval"?
       └─ Compare order amount against the MINIMUM "From Amount"
          of the user-level approval brackets
            ├─ amount >= that minimum  -> route to USER-level approvers
            └─ amount <  that minimum  -> route to STORE-level approvers
```

### The threshold is evaluated on Order Subtotal

**`Set approval for Orders above ($)` is measured against the Order Subtotal — never the Order Total.** Taxes, shipping, discounts, handling fees and every other order-level adjustment are excluded. This applies to both Single-Level and Multi-Level workflows.

## Order approval workflow

Setup requires: Approval Management enabled on the store · `Is Approval Required = True` on the relevant payment methods (`Stores > Payment Method`) · the shopper's Approval Type and approvers set at `Customers > Users > Manage > Approval Management`.

> The KB's workflow section describes the trigger as a payment method with `Is Approval Required = True` **or** an order falling in a configured budget approval range — i.e. looser than requiring both. Treat the exact trigger condition as worth confirming in code.

| Step | Actor | Action |
|---|---|---|
| 1 | Shopper | Places order → status **Pending Order** |
| 2 | System | Emails shopper + Level 1 approver |
| 3 | Level 1 approver | `My Account > Pending Orders` → Approve / Reject |
| 4 | System | Approved → next level; Rejected → notify shopper, order stays rejected |
| 5 | Highest approver | Final approval converts the Pending Order to a confirmed order + confirmation email |

Rules, managed at `Customers > Users > Manage > Approval Management` (`ZnodeApproverLevel`):

- Up to **5 levels** per user, each with a **FROM / TO** amount bracket.
- For an unbounded top bracket, leave **TO blank and tick `Is No Limit`**.
- Multiple approvers may share a level, but **one approver cannot hold two levels** for the same user.
- **When editing an approver, only the name can be changed** — every other detail is fixed once saved.
- Approvers are matched by typing an email; the system autocompletes.
- **Storefront-placed orders only** — admin-placed orders bypass routing entirely.

### Emails

| Event | Goes to |
|---|---|
| Order submitted | Level 1 approver (and the customer) |
| Approved at a level | The next approval level |
| Rejected at any level | The customer |

Final approval by the highest level converts the Pending Order into a real order and sends the confirmation email. Buyers see the trail via **See Approver History**.

Approval routing applies to deferred payment methods: Purchase Order, Invoice Me, Charge On Delivery.

## Pending Orders

Distinct from a "Pending" payment status and from **Pending Payments**. Created when Approval Routing is configured for **Store**, **Payment** or **User** and a qualifying order is submitted from the storefront.

> **After configuring Approval Routing you must Save *and Publish* the store settings** — otherwise the routing does not take effect. This is the most likely cause of "approval is configured but orders still place normally".

**At checkout** the **Place Order** button is replaced by **Submit for Approval**. The confirmation receipt then carries an **Approval Order Number** rendered as a clickable link straight to the approval order; the Pending Orders list links the same way. Default status is **Pending Approval**.

Buyers see order information, current approval status, **approval history and any comments** entered during approval. Admin grid (`OMS > Pending Orders`) shows Pending Order ID, Customer Name, Account Name, Store Name, Status, Amount and Created Date, with **View Order** and **Convert to Order** actions and configurable columns. Buyers view them at `My Account > Pending Order History` with **See Approver History**; they **cannot edit** quantities or delete line items while pending. Admin manages at `OMS > Pending Orders` — change approval status, add notes, or force **Convert Order**. Payment is not captured during the pending state, and there is no documented automatic expiry.

## Open Account Billing (OAB)

A user-level **Billing Account Number** (`Customers > Users > Manage > Additional Attributes > Open Account Billing Details`) that lets deferred-payment orders proceed without admin intervention. Applies to PO, Invoice Me and COD — never to credit card / PayPal / Amazon Pay.

```
Order with PO / Invoice Me / COD
  ├─ user HAS a Billing Account Number -> order proceeds normally
  └─ user has NONE -> queued as "Pending Payment" (OMS > Pending Payments)
        -> admin assigns a number and Accepts -> becomes a Pending Order
```

Notification template: `BillingAccountNumberAdded`.

## Sales representatives

A user with the system **Sales Rep** admin role sees a Sales Portal view in the Admin Console, scoped to their assigned accounts/users (Quotes, Orders, Returns, Sales Metrics). Configured at `Customers > Sales Reps` (Store Name, External ID) and associated from an account or user's General Settings. One user maps to only one Sales Rep. Sales Reps **cannot** create orders on behalf of customers — that requires full-admin **Impersonation** (`Customers > User List > Impersonation`), which also unlocks CSR Discount and Tax Exempt toggles.

## KB source

- [Accounts & Users](https://support.znode.com/support/solutions/43000374857)
- [Managing & Configuring Accounts (13)](https://support.znode.com/support/solutions/folders/43000598118)
- [Managing & Configuring Users (14)](https://support.znode.com/support/solutions/folders/43000598119)
- [Managing User Profiles](https://support.znode.com/support/solutions/folders/43000598124)
- [Enabling Approval Management (8)](https://support.znode.com/support/solutions/folders/43000598167)

> Approval routing verified against 4 articles. The account hierarchy, storefront roles and user-profile half is UNVERIFIED - the entire Accounts & Users category is unread.

## Related
`commerce-checkout-payments` · `commerce-promotions-and-pricing` · `config-stores-tenancy`
