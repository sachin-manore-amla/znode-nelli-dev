# Payment: methods, flow and the gateway plugin contract
What this answers: payment methods you can configure, the high-level flow, what a payment plugin implements, and what customers can and cannot add.
Sources: KB Managing Payment Process Plugins, Payment Plugin FAQ, Troubleshooting Payment Methods (read, 80); SDK payment template (95).

## Configure (no code)
Install the plugin (type PaymentInternal for Charge on Delivery, Purchase Order, Invoice Me; Payment for Spreedly), add a **configuration set** (each set equals one payment method offered), attach it at Stores > Manage > Webstore Payment Methods, or Offline Payment Methods for invoice payments. Spreedly sets hold the gateway choice and credentials (for example two sets for credit card and ACH through one gateway). Approval and open-account flags per method are described in `commerce-orders-and-checkout-customization`.
Troubleshoot "method missing": plugin installed and activated, configuration set active and "Display Setting" on, credentials, store association, profile intersection.

## Flow (high level)
Checkout collects card data in the gateway's iFrame/hosted form (Spreedly), receiving a token; the storefront places the order; Znode calls the Payment Manager to authorize (or purchase), capture later from the Admin order (Capture Payment), refund or void on cancellation or edit. A declined payment returns an error and no order is written. Cancel behaviour with Spreedly: void if authorized, refund if captured. Znode never stores card numbers; tokens identify cards.
Native Spreedly operations: Purchase, Authorize, Capture, Refund, Void.

## Adding a gateway
Customers do not manage Spreedly. A new gateway/method is requested through Znode support with: gateway and methods, existing relationship, connection URLs and credential field names (not values), expected flow (verify/authorize/capture). Znode may decline anything that cannot be done PCI-compliantly. Timeline is not stated.

## Custom payment plugin (template)
Base class the payment plugin base controller (`PaymentPluginController` with the Znode prefix) (package `Znode10.Libraries.Abstract.Plugin.Payment`); abstract actions: `GetGatewayToken`, `Authorize`, `Capture`, `Refund`, `Void`, `GetTransactionDetails`, `CreateCustomer`, `Verify`. A UI controller (the payment UI base controller action `RenderUI`) serves the gateway UI.
Template routes (all under `v1/template/`): `cc/{pluginIdentifier}/token/{environmentKey}`, `.../authorize`, `.../capture`, `.../refund`, `.../void`, `.../purchase`, `.../verify`, `.../customer`, `.../store`, `.../payment-method-details/...`, `.../redact/...`, `.../retain-payment-method/...`; `ach/...` (bank-account, refund, void); `apm/...` (purchase, transaction-details); `googlepay/...`; `gateway` (POST/PUT, redact); `environment-details/{environmentKey}`. Rename the prefix for your gateway.
A separate **React payment UI** template (UMD bundle) is embedded in the storefront: it receives a payment request object and callbacks, tokenizes with the gateway SDK and returns the token. Its guide lists the order of steps; the most common failure is a missing field in the request interface (blank screen).
Status: the payment manager's calling convention for custom plugins and plugin registration are not fully documented to customers. Treat a custom payment plugin as a Znode-assisted project.

## Security
Never log card data, tokens or secrets; keep gateway credentials only in the configuration set; PCI scope stays with the gateway form; verify transactions in the gateway system when debugging (customers cannot see Spreedly).
