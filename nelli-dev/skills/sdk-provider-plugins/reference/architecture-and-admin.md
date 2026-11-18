# Plugin architecture and Admin management
What this answers: how managers and plugins interact, and every Admin step to install, configure, activate and attach a plugin.
Sources: KB Managing Plugins, Managing Payment Process Plugins, Managing Shipping Processing Plugins, Managing Tax Processing Plugins (read, 80); product source (95).

## Managers
| Manager | Called for | Calls the plugin |
|---|---|---|
| Shipping Manager | shipping estimates, calculate, address validation | shipping type other than Custom/Free Shipping; Custom and Free Shipping are priced in-process |
| Tax Manager | calculate, commit (submit), cancel, return line item, pre-submit | the tax rule's plugin; native Sales Tax in-process |
| Payment Manager | authorize, capture, purchase, refund, void, verify, tokens, customers | the gateway plugin |
Shipping calls run **in parallel per shipping type**, bounded by a platform setting for maximum parallel tasks. Estimates (batch, `IsCalculateIndividually` = 0) return many service rates in one call; calculate (one call per service, = 1) is used for checkout totals and for Custom/Free Shipping types.

## Admin
**System Settings > Plugins**:
- **Available Plugins**: filter by Plugin Type (Tax, Shipping, Payment, PaymentInternal); install. A plugin already installed does not show.
- **Installed Plugins**: columns Plugin Name, Version, Details, Author Name, Pre Release, Activate. Open by name or the gear icon. Tabs: **Plugin Information** (Activate checkbox, Save), **Global Configuration** (shipping/tax: provider-level settings for all sets), **Configuration Sets** (Edit, Delete trash icon).
- Activate: check Activate and Save. Deactivate: uncheck and Save. A plugin must be installed, configured and activated.
Common configuration-set fields: Configuration Code (unique), Name (shipping/tax) or Display Name (payment), payment also Display Order, Display Setting (show in webstore checkout), Gateway Type. Read-only values cannot be edited. Plugin-specific fields come from the spec.
Scopes: `Global`, `Store`, `Profile` exist in the platform; spec fields use `global` and `store`.

## Attaching to stores
| Plugin type | Where |
|---|---|
| Storefront payment | Stores > Manage > Webstore Payment Methods (associate sets; display name and order editable); Offline Payment Methods for invoice payments; profile-specific methods on the profile |
| Shipping | Define methods at System Settings > Shipping, associate at Stores > Manage > Shipping Methods; carrier credentials as configuration sets on the store's shipping settings/origin |
| Tax | Tax classes associated at the store tax settings with a default tax class; store tax configuration set (AvaTax/Vertex) |
| Address validation | One configuration set per store (store additional attributes, USPS) |
A method or set must be associated to the store or it never appears. Profile methods intersect with store methods (see `commerce-orders-and-checkout-customization`).

## Behaviour to know
- The shipping estimates API needs a valid Znode user id header; a missing or invalid one can return 404.
- Editing a plugin's active flag matters for Tax and Shipping; for Payment the Activate save has no effect on other state.
- A plugin installed from the registry keeps Name and Version; the Available list hides name+version already installed.
- Deleting a shipping method used in a store or used in an order is blocked.
- Vertex now requires a Trusted Id (10.10 breaking change, masked field on the configuration set); CyberSource fraud phase 2 needs a new configuration set (10.10).
