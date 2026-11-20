---
name: meta-customization-landscape
description: The map of every way a customer or partner can customize Znode V10 and which option fits which requirement - configuration in Admin, data model (PIM attributes, user-defined fields, custom tables, overrides), Page Builder and theme, Webstore source, Custom API SDK endpoints, events and webhooks, method overrides, provider plugins, Data Exchange and import, Admin and Commerce Portal customization, and when a Znode platform change is needed. Use first for any customization question or requirement, to choose the option and the skill to read next.
user-invocable: false
---

# Znode customization landscape

Start here. Pick the lightest option that meets the requirement, in the order of the ladder below. Then read the named skill in full before answering. If nothing on the ladder fits, the verdict is **Needs platform change**, never an invented API.

## The ladder (lightest first)

| # | Option | Choose it when | Verdict it usually gives | Read |
|---|---|---|---|---|
| 1 | Admin configuration and settings | A setting, toggle, template or rule already does it | Supported | `config-global-settings`, `config-store`, `sdk-extension-settings`, `config-notifications`, `config-roles-permissions`, `config-commerce-portal`, `config-bstore` |
| 2 | Business configuration | Price lists, promotions, coupons, vouchers, tax, shipping, inventory, B2B accounts and approvals | Supported | `commerce-promotions-and-pricing`, `commerce-tax-shipping`, `commerce-inventory`, `commerce-b2b-accounts`, `commerce-orders-and-checkout-customization` |
| 3 | Data model | An extra field or table of data | Supported to store, Customizable to show or act on | see "Which data option" below |
| 4 | Content and layout | Pages, banners, containers, forms, theme, and footer or header content editors can change in Page Builder (check this before a source change) | Supported by Page Builder and theme, Customizable beyond them | `webstore-cms`, `webstore-page-builder-and-themes`, `webstore-customization` |
| 5 | Import and Data Exchange | Move data in bulk or on a schedule or event | Supported | `config-import-export`, `sdk-data-exchange` |
| 6 | Events and webhooks | React after something changed | Customizable | `sdk-events-and-webhooks` |
| 7 | Method override | Change a total or short-circuit a platform method synchronously | Customizable (only listed hooks) | `sdk-method-overrides` |
| 8 | Custom API SDK | New endpoint, service, promotion type, processor, Ocelot route, ERP touchpoint | Customizable | `sdk-custom-api`, `sdk-conventions`, `api-catalog`, `api-auth-and-headers` |
| 9 | Provider plugin | A payment, shipping, tax or address provider not shipped | Customizable | `sdk-provider-plugins` |
| 10 | Webstore source change | UI or storefront behaviour the widgets and theme cannot do | Customizable, labelled a source customization | `webstore-customization`, `webstore-headless-api` |
| 11 | Admin customization | A custom Admin page or section | Customizable, with the cautions in the skill | `config-admin-customization` |
| 12 | Platform change request | Platform behaviour, a new entity, hook, event, field type or schema, a new system table (`sdk-custom-tables`: the system-defined flag cannot be set through any endpoint), a column on a built-in Admin grid | Needs platform change | `sdk-capability-registry` |

Rules: never skip a lighter rung without saying why it does not fit. Prefer configuration over code, events over method overrides when the outcome need not change, and the registry (`nd_registry.py find`) before any claim.

## Which data option (the commonest confusion)

| The extra data is... | Use | Not |
|---|---|---|
| One value or set of values on a **product or category** | PIM attribute or product custom field (`commerce-product-attributes`) | user-defined field |
| One value on a **store, account, user, order, promotion, voucher, form** and other entities | User-defined field (`config-global-attributes`) | PIM attribute |
| A **list, mapping, lookup or flag set** | Custom table (`sdk-custom-tables`) | attributes |
| Different product **text or SKU per store, locale or account** | Product Information Overrides (`commerce-product-overrides`) | duplicate products |
| Different **price** per account, profile or store | Price list (`commerce-promotions-and-pricing`) | overrides |
| Large, fast-changing or relational data, or a large payload per record (megabytes of JSON per user) | Not a designed use of any Znode field or table: your own store behind a Custom API endpoint, with your own ownership checks. Verdict Restricted | custom tables, user-defined fields |
| Searchable or facetable custom field | PIM attribute in a published search profile | user-defined field |

All of these store the data. **Showing it on the storefront or acting on it needs a Webstore source change or SDK code** unless the skill says a built-in feature reads it.

## Which integration option

| Requirement | Use |
|---|---|
| Scheduled pull from an ERP API, SFTP or Blob | Data Exchange (`sdk-data-exchange`) |
| Push to an ERP when an order or account changes (after the fact) | Event-triggered Data Exchange or an event consumer (`sdk-events-and-webhooks`) |
| The ERP call must succeed before checkout completes | Method override or custom endpoint (`sdk-method-overrides`, `sdk-custom-api`) |
| One-off or periodic bulk load from a file | Import (`config-import-export`) |
| Real-time stock or price on the product page | Callback Data Exchange with its limits, or a custom endpoint with caching |
| An outside app reads or writes Znode | Call the APIs through the gateway (`api-consumption`, `api-catalog`) |
| Legacy ERP connector | Do not recommend for new work; use Data Exchange |

## How to answer a customization question

1. State the requirement in one line and the user it serves.
2. Walk the ladder; name the first rung that works and the rungs you rejected, with one reason each.
3. Check the registry (`nd_registry.py find "<words>"`) and read the named skill in full.
4. Confirm facts that decide the verdict in the Knowledge Base or API reference (`meta-knowledge-sources`); where they differ from the product, say which one you followed.
5. Give the verdict (Supported, Customizable, Restricted, Needs platform change) with confidence, what is unverified, and the next step. Code changes wait for the developer's approval.

## Always true

- Nothing changes the Znode platform services, the database or other tenants.
- Settings and flags vary by release: say which version a claim was observed on.
- Data written to Draft (import, Data Exchange, attributes, overrides) reaches shoppers only after publish.
- Custom API endpoints need their own authorization; the platform APIs do not enforce ownership for you.
