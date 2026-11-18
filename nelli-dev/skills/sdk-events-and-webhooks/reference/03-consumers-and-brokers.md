# Event consumers and message brokers in the Custom API SDK
Answers: how to consume events in code, the configuration names, retry settings and how to test locally.
Confidence: SDK source (90), KB (75).

## Two consumption modes
| Mode | Runs where | Needs |
|---|---|---|
| Event consumer (broker) | Custom API deployed inside the Znode cluster (default hosting); the platform team configures the broker connection | Consumer class registered at startup |
| Webhook consumer (HTTP) | Anywhere reachable | Webhook Settings record |
The KB: the consumer receives **all enabled events**; a webhook receives only the module and name you registered.

## SDK files (project `Custom.Libraries.Event`)
- `Consumers/ZnodeEventConsumers/ZnodeEventConsumer.cs`: `public class ZnodeEventConsumer : EventConsumer<ZnodeEvent>` with `public override Task Consume(ConsumeContext<ZnodeEvent> context)`. Read `context.Message.EventModule`, `EventName`, `EventPayload`. Return `context.ConsumeCompleted`.
- `MessageBroker/MessageBrokerStartup.cs`: `RegisterMessageBroker()` reads the `EventBus` section, adds MassTransit with RabbitMQ when a RabbitMQ connection string exists and registers the consumer. The queue name uses a shared instance id so all pods compete for each message (each event handled by one pod). The queue is temporary: it is removed when the endpoint stops.
- `Controllers/ZnodeEventSubscriberController.cs`: route `flash-event-subscriber`, `POST`, CORS policy `ZnodeAdminURLCorsPolicy`; delegates to `EventSubscriberService.SubscribeZnodeEvent` which has a switch by module and name for your logic (sample cases User Created and Updated).
- `Controllers/OverrideEventSubscriberController.cs`: route `callback-event-subscriber` for method-override callbacks (`OverrideZnodeActionEvent`: ResponsePayload, ExtendedRequestPayload, WebHookURL, SecretKey, SkipExecution); see `sdk-method-overrides`.
- Add your logic **inside the existing consume action**, switching on module and name. No new consumer type is needed.
Pattern rules: no blocking calls in `Consume`; catch and log (`IZnodeLogging`); keep handlers idempotent (key `EventId`); call Znode through the SDK clients or the gateway, not the database.

## Configuration names (appsettings, section `EventBus`)
`MessageBrokerService` (RabbitMQ or Azure Service Bus), `ServiceBusConnectionString`, `RabbitMQConnectionString`, `RabbitMQManagementUrl`, `RabbitMQUserName`, `RabbitMQPassword`, `QueueName`, `RetryCount`, `RetryInterval`, `EventRetry`. The sample values are `RetryCount` 2, `RetryInterval` 200 (milliseconds is the usual MassTransit meaning, not documented), `EventRetry` true. Their exact behaviour is not documented. Never copy broker credentials from samples; the platform team supplies them. Other names: `ZnodeAdminURLCorsPolicy`, `ZnodeCorsAllowedURLS` (appsettings section) for origins.
The core API and the Custom API must point at the same broker. A bad broker connection makes cached data stale and consumers silent (KB API troubleshooting).

## Local testing of a consumer
1. Install RabbitMQ locally; set `MessageBrokerService` to RabbitMQ, the connection string to the local AMQP port 5672 and the management URL to port 15672 (default test login guest, local only).
2. Run the Custom API; the queue `ZnodeEvent-customapi` appears (use the one without `_error` or `_skipped` suffix).
3. In the management UI, Queues, open the queue, Publish message, set `messageType` to the event type urn (`urn:message:Znode.Libraries.Abstract.Event:ZnodeEvent`), paste the event JSON, publish; the `Consume` breakpoint hits.

## Delivery semantics
At-least-once is MassTransit's default per consumer, but there is no dead-letter handling documented for Znode events; the Data Exchange article states event queues may be temporary and events can be lost on restart. Design for loss: reconcile periodically.

## Version notes
10.3.1.0 extensions can be managed without service interruption; 10.5.0.0 publish webhooks; 10.10.1.0 UpdateUserPortals webhook fix.
