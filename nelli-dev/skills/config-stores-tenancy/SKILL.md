---
name: config-stores-tenancy
description: The Znode Portal (store) tenancy model - what a portal owns, the two-domain preview/production pattern, and B Stores as self-service B2B sub-stores. Use when data comes back empty for a store, when scoping a query or feature per store, or when a ticket mentions B Stores or store setup.
user-invocable: false
---

# Znode Multi-tenancy: Portal / Store Model

**Portal** is the technical term for what users call a **store**. Every piece of data is scoped to a portal.

```
ZnodePortal (store)
  ├── Domain(s)     URLs that resolve to this store
  ├── Catalog       one PIM catalog, published into Elasticsearch
  ├── Locale(s)     language settings (currency is separate, store-level)
  ├── Theme         storefront visual theme
  ├── B2B Accounts  companies associated with this store
  │     └── Users
  └── B Stores      self-service sub-stores created by B2B users
```

Scoping is header-driven — see `api-auth-and-headers` for `Znode-PortalCode`, `Znode-LocaleCode`, `Znode-CatalogCode`.

## Cardinality rules

| Relationship | Rule |
|---|---|
| Store → Catalog | 1-to-1 — a store has exactly one catalog |
| Catalog → Store | 1-to-many — one catalog can be shared across stores |
| Store → Locale | 1-to-many, one marked default |
| Store → Currency | exactly one active currency (no conversion engine) |

## Two-domain production pattern

A store may have two domains pointing at the same portal — one preview, one production. `Znode-PublishState` (`Preview` / `Production`) selects which Elasticsearch index is queried. Sending the wrong value returns stale or unreleased data.

> Preview state is **deprecated in 10x**. Do not depend on it in new work.

## Common empty-response cause

A portal must have a **domain, a catalog and a locale** assigned before it returns data. Missing any of these produces **empty responses, not errors**.

## B Stores (B2B self-service sub-stores)

Created by a B2B user with the Owner role from the storefront (`My Account > Manage Stores`) — no admin involvement.

| Dimension | Regular Store | B Store |
|---|---|---|
| Created by | Znode admins (Admin Portal) | B2B users with Owner role (storefront) |
| Approval | Direct | Must be admin-approved before the URL works |
| Catalog | Admin-configured | Inherits an existing catalog; owner may restrict to a product subset |
| Price list | Admin-configured | Owner picks from existing price lists |
| Theme | Full Site Theme | Logo, favicon and brand colour overrides only |
| Domain | Set by admin | Custom subdomain entered by the owner |

**Roles:** `Is Owner` (create/edit/configure, sees "Add New Store") and `Is Manager` (manage settings and content, cannot create new B Stores).

**Creation wizard:** store details (name, description, subdomain) → access flags (self-register, require login, show pricing) → branding (logo, favicon, theme colours) → optional product subset → create.

**Management sections:** Dashboard, Content, Design, Products, Orders, Users, Settings, Starter Theme. Owners can also duplicate a B Store (starts Inactive).

Admin-side enablement lives at `Stores > Manage > [Store] > B Store Settings`. Orders placed through a B Store appear in the parent OMS with the B Store identifier; data is stored in `ZnodeBStore*` tables.

## KB source

- [Stores & Warehouses](https://support.znode.com/support/solutions/43000374856)
- [Managing Stores](https://support.znode.com/support/solutions/folders/43000598171)
- [Managing B Stores (12)](https://support.znode.com/support/solutions/folders/43000598169)

## Related
`api-auth-and-headers` · `commerce-b2b-accounts` · `commerce-catalog`
