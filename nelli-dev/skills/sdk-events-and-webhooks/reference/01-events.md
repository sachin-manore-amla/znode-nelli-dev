# Events: modules, names, message
Answers: which events exist, when they were added, what the message and webhook body contain.
Confidence: seeded event list and dispatch calls read in product source (90); KB article read through a summary (75).

## Modules and names
| Module | Names | Added |
|---|---|---|
| Account | Created, Updated, Deleted | Created and Updated in 10.0, Deleted 10.10 |
| User | Created, Updated, Deleted, EnableDisableUser, UpdateUserPortals, AssociateUserAccount, UnAssociateUserAccount | Created and Updated 10.0; EnableDisableUser and UpdateUserPortals 10.7; Deleted, AssociateUserAccount, UnAssociateUserAccount 10.10 |
| Order | Created, Updated | 10.0 |
| Product | Created, Updated, Deleted, Published | 10.0 |
| Category | Created, Updated, Deleted, Published | Deleted 10.10 |
| Catalog | Created, Updated, Deleted, Published | 10.0 |
| Portal (store) | Created, Updated, Deleted, Published | 10.0 |
| Price | Created, Updated, Deleted | Deleted 10.10 |
| Inventory | Created, Updated, Deleted | Deleted 10.10 |
| Address | Created, Updated, Deleted | 10.0 |
| UserDefinedField | Updated | 10.0 |
| ContentPage | Published | 10.0 |
| CustomTableData | Created, Updated, Deleted | 10.10 |
| ConfigurationSet (plugin configuration) | Updated, Deleted | 10.10 |
"Added" is the platform script in which the event was seeded. The Data Exchange trigger list in the KB names the same modules and calls the user-defined field event `UserUpdatedFields`. The dropdowns in Webhook Settings are the authority for your version. The KB says the platform lists only Order, User, Portal, Product and Address in older text: that is out of date.
Names in the older SDK sample use the pattern Module+Action (`OrderCreated`): in the live message `EventModule` and `EventName` are separate (`Order`, `Created`). The KB describes these fields inconsistently.
Where raised (observed in code): Account, Address, User, Product, Category, Catalog, Portal, Price, Inventory, ContentPage, UDF, ConfigurationSet and CustomTableData by the core, customer and custom table services; **Order Created and Updated by the Commerce Portal order service** (order creation, copy, conversion of a quote, status updates). Order Updated carries the status code.
Release notes: 10.5.0.0 added publish webhooks (Product, Category, Catalog, Content Page, Store); 10.10.1.0 fixed UpdateUserPortals on login.

## Message and webhook body
POST, `Content-Type: application/json`, UTF-8, body = the serialized event:
```json
{
  "EventDataCode": "MaxwellHardware",
  "EventDataId": "2",
  "EventId": "<guid>",
  "EventModule": "Account",
  "EventName": "Created",
  "EventVersion": "1.0",
  "EventPayload": "{ \"ParentAccountId\":\"\", \"PortalId\":\"9\" }",
  "EventTimeStamp": "2026-05-27T12:00:00Z",
  "Source": null,
  "TraceId": "<guid>",
  "UserId": ""
}
```
| Field | Meaning |
|---|---|
| EventDataCode | Business code of the record (store code, SKU, order or cart number, username) |
| EventDataId | Numeric id of the record (or a comma list for bulk actions) |
| EventId | Unique id of this event |
| EventModule / EventName | Module and action |
| EventPayload | JSON string of extra values: the shape differs per module (the KB links a spreadsheet of per-event payloads that could not be read). Parse defensively |
| EventTimeStamp | UTC |
| EventVersion | Currently `1.0` |
| UserId | Id of the user who caused it; empty or default for scheduled actions |
| Source, TraceId | Optional origin and trace id |
Sample payloads for each event are stored with the event record and visible through `GET /v2/events/{eventName}/{eventModule}` (core v2).
Other header sent: only `Authorization` when you configured one (the `User-Agent` marker `znode-multifront/1.0` belongs to a different, internal broadcast). Do not rely on a header to identify Znode: validate the Authorization secret you set.
