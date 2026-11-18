# Data Exchange: event and callback triggers, real-time rules
Answers: how an exchange starts from a Znode event or a storefront request, which events exist, what is required first, and the performance rules.
Confidence: KB (70-80), event module list checked in product source (90).

## Trigger types (Trigger Execution (HTTP) on)
| Type | Direction | Use |
|---|---|---|
| Znode Event (push) | Znode raises an event, the exchange starts | Order Created to ERP, Account Updated to ERP |
| Znode Callback (pull) | Storefront asks, connector calls the external API, answer returns | Get Real Time Price, Get Real Time Inventory (PDP) |
| API-based | An external caller invokes the exchange | When no Znode event exists |

Exchanges with this switch on cannot be scheduled. Existing scheduled exchanges keep working.

## Event trigger setup
1. Create the exchange, switch **Trigger Execution (HTTP)** on, pick **Znode Events**.
2. Choose the event module and event name (same list as Dev Center > Webhook Settings).
3. **Return Payload Response**: checked, the event payload is stored as Step 0 as received; unchecked, the connector fetches the entity (for Order Created, the order details) and stores that as Step 0. **Input Parameters** shows the payload. Release 10.10.1.0 states the payload holds only the data code, module and name, so a fetch step may be needed. Behaviour differs by version: look at Input Parameters on your environment.
4. Add steps and map: left side destination fields, right side `StepN.` sources, for example `Step2.SalesOrderName` from `Step0.Payload.EventDataCode`.

Event modules and names offered (KB, same names seeded in the product): Account (Created, Updated, Deleted), User (Created, Updated, Deleted, EnableDisabledUsers, UpdateUserPortals, AssociateUserAccount, UnAssociateUserAccount), Product (Created, Updated, Deleted, Published), Category (Created, Updated, Deleted, Published), Catalog (Created, Updated, Deleted, Published), Portal (Created, Updated, Deleted, Published), Price (Created, Updated, Deleted), Inventory (Created, Updated, Deleted), Address (Created, Updated, Deleted), UserUpdatedFields (Updated), ContentPage (Published), CustomTabledData (Created, Updated, Deleted), ConfigurationSet (Updated, Deleted). The Order module (Created, Updated) exists in the product and in Webhook Settings but is missing from the KB list of the exchange screen; check the dropdown. Full detail: `sdk-events-and-webhooks/reference/01-events.md`.

## Callback setup
Prerequisites (all three):
1. Global Settings flag **Enable CC API** is Yes.
2. All legacy ERP connectors are **Disabled**.
3. The callback exchange is **Enabled**.
Steps: enable Znode Callback trigger, select the action (Get Real Time Price or Get Real Time Inventory), add steps that call the ERP, set the global mapper (Sales Price, Retail Price, SKU, Line-Item ID). Disabling the callback exchange returns the storefront to stored Znode price and inventory.

## Real-time rules (architecture article)
- Real-time runs **synchronously and inline**: the caller waits. No queue buffering, no built-in rate limiting.
- Targets: response under 2 seconds, payload under 1 MB (maximum recommended 10 MB), fewer than 20 concurrent requests, ERP latency under 500 ms.
- Recommended: single order, single SKU inventory, order acknowledgment. Not recommended: full catalog sync, bulk inventory, full price sync.
- Use short cache expiry (2 to 5 minutes) for inventory lookups.
- Events in temporary queues can be lost on a restart and there is no dead-letter queue: do not treat an event exchange as guaranteed delivery. For must-not-lose flows, add a reconciliation exchange (scheduled order export) or compare counts.

## What an event exchange cannot do
It runs after the Znode action committed. It cannot veto or change the Znode action. For a pre-commit decision use `sdk-method-overrides`.
