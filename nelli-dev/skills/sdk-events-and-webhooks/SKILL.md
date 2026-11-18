---
name: sdk-events-and-webhooks
description: Znode events and webhooks - which modules and event names exist, the message and POST body fields, how to enable events, Manage Webhook Settings (fields, authorization, verify), the delivery rules (fire and forget, 5 second timeout, no retry), event consumers in the Custom API SDK over RabbitMQ or Azure Service Bus, broker configuration names, CORS, local testing, security, and the choice between an event, a Data Exchange trigger and a method override. Use when an external system must be told that something happened in Znode, or when a webhook does not fire.
user-invocable: false
---

# Events and webhooks

## What it is
An **event** is a message Znode raises after a record changes (module + name, for example `Order` + `Created`). A **webhook** is an HTTP POST of that message to a URL you register. An **event consumer** is customer code in the Custom API that listens on the message broker. Terms people confuse: *event* (after the fact, cannot change the action) versus *method override* (a synchronous hook that can change or stop the action, `sdk-method-overrides`); *event module* (Order, User) versus *event name* (Created, Updated); *flash event* (this feature) versus cache-invalidation events (internal).

## Use / do not use
| Need | Verdict |
|---|---|
| Tell an external system an order, user, product, price or inventory record changed | Supported: webhook |
| Run your own code on every event with high volume | Customizable: event consumer on the broker (Custom API runs inside the Znode cluster) |
| Start a Data Exchange when something happens | Supported: event trigger (`sdk-data-exchange`) |
| Change an order total or block checkout | Not an event. Use a method override |
| Guaranteed delivery with retries | Not provided for webhooks (one attempt). Design reconciliation |
| Events for bulk imports | Not raised |

## The facts that matter most
1. Admin path: **Dev Center > Webhook Settings** (page title "Manage Webhook Settings"). One record per unique Event Module + Event Name.
2. Delivery: **one HTTP POST per URL**, JSON body, run in the background. Timeout is **5 seconds** by default (platform setting `WebhookRequestTimeoutInSeconds`). **No retry.** A non-success answer or timeout is only logged.
3. The `Authorization` value you enter is sent **exactly as typed** in the `Authorization` header (for example `Bearer abc` or a key). Nothing else signs the request.
4. The body field `EventPayload` is a **JSON string** (double encoded): deserialize it.
5. The message fields: `EventDataCode`, `EventDataId`, `EventId`, `EventModule`, `EventName`, `EventPayload`, `EventTimeStamp`, `EventVersion`, `UserId`, `Source`, `TraceId`. `EventType` is obsolete.
6. The feature is controlled by a global feature flag and a per-event enabled state. Default events are enabled; a webhook needs its record **Is Active**.
7. Webhook URLs: comma separated for several; must be absolute http or https; internal cluster URLs are allowed.
8. Bulk import does **not** raise events.
9. Order events are raised by the Commerce Portal (Commerce API) order flow, other modules by the core API.
10. Consumers: the SDK sample `ZnodeEventConsumer` (broker) and `flash-event-subscriber` (HTTP endpoint). Webhook endpoints hosted in the Custom API need the Admin URL in `ZnodeAdminURLCorsPolicy` (KB; a server-to-server POST does not use CORS).

## Decision guide for Nelli-Dev
| Requirement | Verdict and approach |
|---|---|
| Call our system when an order is placed | **Supported.** Webhook on Order + Created pointing to your endpoint; Authorization header set; the endpoint validates it, answers 200 within 5 seconds and queues its own work. Reconcile with a scheduled Data Exchange order export for lost calls |
| Trigger something when inventory is low | **Not a built-in event.** Inventory events (Created, Updated, Deleted) carry the record; your consumer compares quantity to the re-order level. Low-stock email alerts are a separate feature (`commerce-inventory`) |
| Enrich a record when a user is created | **Supported** (User Created webhook), but the record is already saved: call the Znode API to update it afterwards |
| Run code when a product is published | Product, Category, Catalog, Portal, ContentPage + Published events |
| Block an order if the ERP is down | **Not supported by events.** Method override or custom endpoint |
| React to a bulk import finishing | **Not supported** (no event). Poll the import log |
| Send events to Azure Service Bus consumers | Customizable: broker type is configuration (reference 03) |
| Same event to many systems | Supported: several URLs on one record, or one broker consumer that fans out |

## Reference files
- `reference/01-events.md` modules, names, versions, the POST body and payload notes
- `reference/02-webhook-settings.md` Admin screen fields, verify, API, delivery, security, CORS
- `reference/03-consumers-and-brokers.md` SDK consumer, broker settings names, retries, local testing
- `reference/04-event-vs-override.md` choosing between event, trigger and method override

Related: `sdk-method-overrides`, `sdk-data-exchange`, `sdk-custom-api`, `quality-security-checks`.
