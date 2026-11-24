# Tax
What this answers: tax classes, rules, plugins, AvaTax setup and what is customizable.
Sources: KB Managing Taxes, Adding a Tax Rule, Associate Products to Tax Class, Managing Tax Processing Plugins, Configure the AvaTax Tax Plugin, Configuring Promotion And Coupon Settings, Managing Returns (read 2026-11-23). Confidence 85.

## Tax classes (System Settings > Taxes)
- A tax class groups products that share tax rules; many products per class.
- Fields: **Tax Class Name** (internal), **Display Order**, **Activate** box.
- Actions: Add New (Save then shows **Manage Taxes** and **Associated Products** tabs), Edit (pencil), Delete (trash). The article names only the Action column of the grid and gives no confirmation texts.
- Store association of tax: Stores > (store) > Configuring Taxes For a Store (article listed, **not read**: unverified).

## Tax rules (Taxes > Edit > Add Rule)
| Label | Notes |
|---|---|
| Tax Type | list shows "Sales tax" by default |
| Include Shipping in taxes | checkbox |
| Precedence | number; processing order; tie behaviour not documented |
| Destination Country / State | drop-downs; which are mandatory is not documented |
| Zip Code | optional |
| Sales Tax, VAT Tax, GST Tax, PST Tax, HST Tax | value fields; mapping to types not documented |
Validation rules and messages: not documented.

## Associate products
Taxes > Edit (pencil) > **Associated Products** > Associate Products > select > Save. The article's last step contradicts its confirmation: verify the grid after saving.

## Native vs plugin
| Mode | Notes |
|---|---|
| Native Sales Tax rule engine | different rates per country; rules by product type and category through classes |
| AvaTax | real-time provider; import duties for international orders |
| Custom Developed Tax Plugin | your own service (`sdk-provider-plugins`) |

## Plugins (System Settings > Plugins)
Available Plugins (Plugin Type = Tax) to install; Installed Plugins to configure. Each plugin: tabs **Plugin Information**, **Global Configuration**, **Configuration Sets**. Grid columns: Plugin Name, Version, Details, Author Name, Pre Release, Activate. Configuration set needs a unique **Configuration Code** and a **Name**; several sets can serve different stores (example: two AvaTax sets for two webstores). Deleting a set: trash icon on the Configuration Sets tab. How a set is bound to a store is not described in the plugin article (store tax settings article not read).

## AvaTax (Installed Plugins > AvaTax)
- Global Configuration: Avalara App Name, Exemption Number, "Allow Submissions Of The Tax Requests?".
- Configuration Set: Configuration Code, Name, AvaTax URL (`https://sandbox-rest.avatax.com/api/v2` or `https://rest.avatax.com/api/v2`), Company Code, Account Number, Avalara License, Freight Identifier (item number for shipping cost), Prices Are Inclusive of Taxes (Yes = prices already include taxes, duties, VAT, shipping).
- Activate on Plugin Information before use.
- Import duties: calculated at checkout from HS Code and destination; Canada documented; duty settings are managed in Avalara; Znode shows duties with taxes and shipping.
- Not documented in the KB: commit, cancel and return behaviour at Avalara, store-level setup steps, errors.

## Tax in orders and returns
- Order tax recalculates in real time when discounts, vouchers, shipping type, zip or shipping amount change. Custom tax service rates are saved on the order.
- Tax on a return is calculated on the line total plus line shipping. Order-level settings **Calculate Tax On The Discounted Price** and **Include Shipping In Taxes** are frozen at placement (`commerce-returns`).

## Customization
Configuration first (rules, classes, exemption). A different provider needs a tax plugin; tax result tweaks use the tax method-override hook (`sdk-method-overrides`); tax rates stored per order cannot be edited by a customization.
