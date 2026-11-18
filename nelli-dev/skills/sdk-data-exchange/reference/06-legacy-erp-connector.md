# Legacy ERP connector, touch points and scheduler
Answers: what the legacy connector is, how touch points are scheduled and called, the SDK pattern, and why not to start new work on it.
Confidence: product source (90), KB summaries (75).

## Status
The Znode 9 style module. The KB says it "will not be enhanced and will be deprecated"; no date. **Data Exchanges are recommended for new work.** Maintenance fixes still ship (Trigger button restored, Create Order touch point for voucher orders, 10.14.0.6).

## Admin
| Screen | Path |
|---|---|
| Connector list | Dev Center > Commerce Connector > Legacy ERP Connector (fields: Package Name, ERP Name, Description, Status, Notification Email Address; Add New, Edit, Delete, enable or disable) |
| Per-connector menu | Dev Center > "<ERP Connector Name> Configuration" appears after you enable one: tabs **Log**, **Touch Point List**, **Settings** |
| Touch point actions | Run (play, "Create Scheduler" in older text), Edit (schedule), Enable or Disable, History |
Rule: **only one connector is active**; enabling one disables the previous. Touch points appear only after a connector is active. Znode 10 ships only the sample `MockERPConnector`. Real-time pricing and inventory callbacks require all legacy connectors disabled.

## Scheduler fields (Edit > Scheduler)
Touch Point Name (generated), Scheduler Type (default Scheduled), Scheduler Name (unique, set once), then **One Time** (Start Date, Time, Enabled) or **Recurring** (Cron Expression, Enabled; a commonly used list is on screen). The schedule runs as a background job; disabling removes the job.

## Settings tab
Credentials for the ERP, fields defined by the connector's own configuration resource (sample fields: Azure Blob URL, ERP Connector Folder, Blob Connection String). Values are stored in Znode and read by code through the ERP connector client.

## How it works
Znode (scheduler or an action such as order creation) posts to the Custom API, which finds the active connector class and invokes the touch point method by name. Touch points in the SDK sample (`[ConnectorTouchPoint]`; `Type = "RealTime"` for event-style): scheduled `InventoryRefresh`; real-time `GetProductInventory`, `GetInventoryList`, `GetRealTimePricing`, `CreateOrder`, `UpdateOrder`, and Create or Update for Product, Category, ProductInventory, ProductPrice, Account, Address, User. The connector class implements `IHasConnectorIntegration` and is registered in the SDK dependency registration; DevOps sets the Custom API, API and API v2 root URIs.
Import pattern in the sample (`RefreshInventory`): read a CSV from Blob, look up the import type and template, then call the import client `ImportData` with the template mappings and the touch point name. A scheduled call has no logged-in user; the platform then uses the first admin user as the import owner (product source).

## API (Core v1 legacy, ERP Touch Point family)
ERPConfigurator (List, Create, Update, Delete, Enable or Disable, GetActiveERPClassName), ERPConnector (GetERPConnectorControls, CreateERPControlData), ERPTaskScheduler (List, Create, Delete, TriggerSchedulerTask, Enable or Disable), TouchPointConfiguration (List, TriggerTaskScheduler, GetSchedulerLogList, SendSchedulerActivityLog). All are legacy v1 routes; confirm each on the API reference before use.

## Verdicts
| Requirement | Verdict |
|---|---|
| Scheduled import via a touch point on an existing legacy setup | Customizable, not recommended: migrate to a Data Exchange |
| Order to ERP via CreateOrder touch point on an existing setup | Customizable on legacy; for new work use an Order Created event exchange |
| New project | Do not choose legacy |
