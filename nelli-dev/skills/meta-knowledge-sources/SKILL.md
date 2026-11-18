---
name: meta-knowledge-sources
description: Where Nelli-Dev finds authoritative Znode information - the Knowledge Base (support.znode.com) and the API reference (apidocs.znode.com) - with the verified URLs, the Developer Documentation articles that matter for customization, how to read each source reliably, and the rules for citing them. Use at the start of Discovery and whenever a fact must be confirmed from documentation.
user-invocable: false
---

# Knowledge sources

Verified by reading the live sites on 2026-10-09. Re-check a URL before relying on it; sites change.

## 1. Knowledge Base: https://support.znode.com/support/solutions

- **Host rule:** use `https://support.znode.com/...`. Article pages show relative links; the same paths on `www.znode.com` returned **404**, so never rebuild a link on another host.
- **Public:** the article text of the pages read was visible without signing in (only a Sign In link in the header).
- **15 V10 categories**, among them: Znode Storefront & Features, **Developer Documentation**, Stores & Warehouses, Accounts & Users, Order Management, Product Information, Digital Asset Management, Marketing & Site Search, Reports, System Settings, Commerce Portal, Content Management, Security, Other Information, Znode Releases. Category id of Developer Documentation - V10: `43000373995`.

### Developer Documentation: the articles that matter for customization
(path prefix `/support/solutions/articles/`; folder paths are `/support/solutions/folders/<id>`)

| Folder | Article | Path |
|---|---|---|
| **API Development** (`43000594918`) | Znode API Documentation - V10 | `43000730673-znode-api-documentation-v10` |
| | API - Setup Guide, Installation & Configuration | `43000761221-api-setup-guide-installation-configuration-` |
| | **API Customization Guide** | `43000761402-api-customization-guide` |
| | Headless API Consumption | `43000761405-headless-api-consumption` |
| | **Znode Customization - How to use Znode Events** | `43000765833-znode-customization-how-to-use-znode-events` |
| | Integrating Custom Shipping Plugins | `43000784363-integrating-custom-shipping-plugins` |
| | **Promotion Extensibility Developer Guide** | `43000790288-promotion-extensibility-developer-guide` |
| | API Troubleshooting · React App & API - Troubleshooting guidelines | `43000761230-api-troubleshooting` · `43000761220-react-app-api-troubleshooting-guidelines` |
| **Storefront Development** (`43000594943`) | **Webstore Customization Guide** | `43000761087-webstore-customization-guide` |
| | Webstore Development & Page Builder Setup Guide | `43000760892-webstore-development-page-builder-setup-guide` |
| | Webstore Troubleshooting Guide | `43000761228-webstore-troubleshooting-guide` |
| | Secure Cache Revalidation Configuration | `43000789713-secure-cache-revalidation-configuration` |
| | Cloudflare Cache Rules & Purge Configuration | `43000794650-cloudflare-cache-rules-purge-configuration` |
| | Configuration of New Locale in webstore · Implementing the Znode ReCaptcha feature on any additional pages · Configure a Hero Image for Brand Pages · Znode Device & Browser Support | `43000793836-...` · `43000786828-...` · `43000793135-...` · `43000757141-...` |
| **Admin Customization** (`43000598555`) | **Admin Customization** · Admin Setup, Installation & Configuration · Admin Troubleshooting Guide | `43000761412-admin-customization` · `43000761482-admin-setup-installation-configuration` · `43000761488-admin-troubleshooting-guide` |

Read in full so far (2026-10-09): Promotion Extensibility Developer Guide, API Customization Guide, How to use Znode Events. **The others are listed but not read**: read the relevant article in full before relying on it.

### What those three articles established (read through a fetch summary: confidence 70-85%, not code-verified)

- **Promotion extensions:** inherit `CartPromotionTypeBase` (package `Znode10.Libraries.Promotions.SDK`), marked `[PromotionExtension(typeof(CartPromotionTypeBase))]`, logic in `Calculate()` returning `PromotionCalculateResult`. Deployed with `znode deploy extension`, then **Sync** in Admin > Extension Observability, then the promotion type is registered in Admin > Dev Center > Promotion Settings (the Class Name must match the code's `ClassName`, case-sensitive), then a promotion is created under Marketing > Promotions. Context read: `Context.PromotionBag` (admin settings, user-defined attributes, coupons, promotion name, promo code), cart items, subtotal, quantity, coupons, and the cart's `UserId`, `ProfileId`, `PortalId`, `OrderId`; DI services via `ServiceProvider`; SDK helpers for product, category, brand and catalog lookups. **The article does not state that account or account-group data is available, only numeric ids** (so an account-group discount depends on a lookup the article does not describe).
- **Custom API (API Customization Guide):** custom endpoints and logic can wrap Znode APIs (POST changes applied before the call, GET responses transformed after it). Deploy with `Znode deploy CustomAPISDK <Environment> [<SDK path>]`; endpoint pattern `https://<CustomAPISDKHostedURL>/<Controller>/<Action>`; host in the same VNET as the Znode API; routes in `CustomOcelot.json` use route keys with "customapi" and need higher priority than Znode routes; `ZnodeApiDomainName` in appsettings for domain authentication. **Limitations stated: no direct database or Entity Framework access; changes to Znode's own APIs go through a support ticket.** This conflicts with the SDK template, which contains direct-data-access code (`Custom.Libraries.DataAccessHelper`): treat direct data access as **not supported** and say so.
- **Events (How to use Znode Events):** enabled in the Znode database (default events are on); webhooks are managed in Dev Center > Manage Webhook Settings (module, event name, active, URL, optional authorization); message fields `EventDataCode, EventDataId, EventId, EventModule, EventName, EventPayload (JSON string), EventTimeStamp, EventVersion, UserId, Source, TraceId`; sample consumers in `Custom.Libraries.Event`, extended inside the existing `Consume` method; consumers registered in `MessageBrokerStartup.RegisterMessageBroker()`; webhook endpoints need the Admin URL in `ZnodeAdminURLCorsPolicy`. The full event list and per-event payloads are in an external spreadsheet that the article links and that was **not** readable.

## 2. API reference: https://apidocs.znode.com/

- A **Stoplight** documentation site (client-rendered). A plain fetch returns only the page title. **Read it in the browser pane**: `navigate` to the page, then `get_page_text` (text of the current page, about 2,500 characters is enough to confirm a page, use a larger limit for a full page) or `find`/`read_page` for the sidebar.
- Page URL pattern: `https://apidocs.znode.com/docs/<collection>/<node id>-<slug>`, for example `/docs/commerce-api/58ae0e7908f3d-1-introduction`. The overview page lists the families: Core API v2, Commerce API, Dynamic Data Table API, Payment API v1, Reports API, ERP Touch Point API, and the legacy Core API v1 (hosted separately). See `api-catalog` for the rules.
- The raw OpenAPI document is **not** exposed to the browser (the site's token request returned 400). **Scripted checks need exported spec files** in `nd-knowledge/specs/` (ask the Znode contact for them). Until then, confirm each operation by reading its page in the browser pane and mark it `VERIFIED (apidocs page)`, with the page URL.

## 3. How to read and cite

1. **Fetch, then read what matters in full.** WebFetch returns a short model summary of the page: ask for specific facts and "not stated" for gaps, and never copy a summary's names into code. For exact names, signatures and code samples, open the article in the browser pane (`get_page_text`) and read it.
2. **Cite** the full URL, the article title and the date read. Record each source in `discovery.md`.
3. **Confidence:** KB article read through a summary 70-80%; read in full in the browser pane 80-85%; the same fact confirmed in source code or a spec 90%+.
4. **Conflicts:** when the KB and the code disagree (for example direct data access), follow the precedence in `README.md` (code, then KB), record the conflict, cap confidence at 60% until the developer or Znode settles it, and tell the developer.
5. **Only these hosts:** `support.znode.com`, `apidocs.znode.com` (and the developer's recorded gateway for API calls). Do not use other sites for Znode-specific facts.
6. **Gaps:** if the documentation is silent, say "not documented", not "not supported", and offer to ask Znode support.

## 4. Not yet verified

- A working KB search URL (use the folder listings above).
- Whether every article in the other KB categories is public.
- The external events spreadsheet and the SDK Guideline Documents (Google Docs) named in the SDK README.
