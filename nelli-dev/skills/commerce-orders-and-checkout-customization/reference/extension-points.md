# Extension points for commerce behaviour
What this answers: every customer-available way to change cart, checkout and order behaviour, with its reach and limits.

| Extension point | Reaches | Cannot do |
|---|---|---|
| Configuration (price lists, promotions, shipping rules, tax rules, profiles, approvals, templates, statuses) | most business rules | rules outside the built-in settings |
| Method override (`sdk-method-overrides`) | storefront totals after calculation, Commerce Portal totals, tax customer identity, receipt text, admin email | unit price, quantity, placement veto, other methods |
| Promotion extension (`commerce-promotions-and-pricing`) | a custom discount type | account-based conditions, tax, ordering |
| Provider plugins (`sdk-provider-plugins`) | shipping rates, tax, payment gateway, address validation | orchestration |
| Events and webhooks (`sdk-events-and-webhooks`) | notifications after order, user, store, product, address changes | changing results |
| Custom API SDK endpoints, ERP touchpoints, data exchange (`sdk-custom-api`) | your own data and integrations | altering Znode internals |
| Commerce API and Core API v2 (`api-catalog`) | creating and updating carts, orders, statuses, price lists, promotions, vouchers | hooks |
| Webstore source (`webstore-customization`) | checkout UI, BFF place-order route, validation before placing | server rules for other channels (Admin, Commerce Portal) |
| Custom tables | extra structured data | link enforced by Znode |
Rules of thumb: a rule that must hold in every channel (storefront, Admin, Commerce Portal, API) belongs in configuration, a promotion or a plugin; a rule only the storefront needs can live in the Webstore source but is labelled a source customization with upgrade-merge cost. Checkout veto options: approval routing, budget limits, inventory and min/max quantity, payment failure, store manual approval, or a Webstore source check. The promotion `PreSubmitOrderProcess` returning false is evaluated on the Engine order path; whether the storefront place-order path calls it was not seen, so do not rely on it.
