---
name: sdk-custom-api
description: The znode10-customapi-sdk extension template - its project layout, the five extension points (custom endpoints, event consumers, ERP connector touchpoints, data exchange processors, Ocelot routes), key appsettings values and deployment. Use when building any customisation on top of Znode instead of modifying platform code.
user-invocable: false
---

# Znode Custom API SDK

An **ASP.NET Core microservice template** that acts as a customisable overlay on the Znode API. Integrators add controllers, event consumers, ERP connectors and data-exchange processors here — **never modify the Znode platform**.

It sits downstream of the core API and calls it through the `Znode.Engine.Api.Client` NuGet packages.

## Project structure

| Project | Role |
|---|---|
| `Engine.Custom.Api` | Host — DI, middleware, Ocelot, JWT auth, Swagger, Dockerfile |
| `Custom.Api.Core` | Custom REST controllers and services |
| `Custom.Admin.Core` | Admin-side customisation endpoints |
| `Custom.Libraries.Data` | Custom EF data models and DbContext |
| `Custom.Libraries.DataAccessHelper` | `ZnodeDomainService` — direct DB access |
| `Custom.Libraries.DataExchange` | Import/export processors |
| `Custom.Libraries.ERPConnector` | ERP touchpoints |
| `Custom.Libraries.Event` | MassTransit consumer for `ZnodeEvent` messages |
| `Plugins/` | Shipping and tax plugin templates |

## Extension points

**1. Custom endpoints** — add controllers under `Custom.Api.Core/Controllers/`; register clients in `CustomDependencyRegistration`.

**2. Event / webhook consumers** — MassTransit over RabbitMQ or Azure Service Bus:

```csharp
public class ZnodeEventConsumer : EventConsumer<ZnodeEvent>
{
    public override Task Consume(ConsumeContext<ZnodeEvent> context)
    {
        // context.Message: EventModule, EventName, EventPayload
        return context.ConsumeCompleted;
    }
}
```

**3. ERP connector touchpoints** — implement `IHasConnectorIntegration` and mark methods:

```csharp
[ConnectorTouchPoint]
public bool InventoryRefresh() { ... }                       // scheduled batch

[ConnectorTouchPoint(Type = "RealTime")]
public List<InventoryERPResponseModel> GetProductInventory(InventoryERPRequestModel model) { ... }
```

**4. Data exchange processors** — pre-built: `MockProcessor`, `ProductFeed`, `StaticInputWithOutputProcessor`, `ZnodeProductCategoryAssociation`.

**5. Ocelot route customisation** — `Engine.Custom.Api/Ocelot/CustomOcelot.json`.

This is also where **Znode Method Override** webhook controllers live — see `sdk-method-overrides`.

## Key `appsettings.json` values

| Key | Purpose |
|---|---|
| `ZnodeApiGateway` | Core API gateway URL |
| `ZnodeApiDomainName` / `ZnodeApiDomainKey` | Domain (Basic) auth for core API calls |
| `EventBus.MessageBrokerService` | `RabbitMQ` or `AzureServiceBus` |
| `Caching.CacheType` | `InMemory` or `Redis` |
| `ConnectionStrings.ZnodeMongoDBForLog` | MongoDB for logs |
| `RetryCount` / `RetryInterval` / `EventRetry` | Event consumer retry policy |

## Deployment

```bash
dotnet nuget add source "https://nuget.znode.com/nuget"
# via Znode CLI:
Znode deploy CustomAPISDK <Environment>
# or:
docker-compose up      # Dockerfile lives in Engine.Custom.Api/
```

## KB source

- [Developer Documentation](https://support.znode.com/support/solutions/43000373995)

> Never KB-checked.

## Related
`sdk-method-overrides` · `sdk-events-and-webhooks`
