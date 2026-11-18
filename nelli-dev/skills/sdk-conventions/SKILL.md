---
name: sdk-conventions
description: How to write code in the Custom API SDK the way its own samples do - controller, service and dependency-registration patterns, logging, error handling, calling Znode clients, plus the SDK template's known weak spots that must not be copied. Use whenever generating or reviewing C# in the Custom API SDK.
user-invocable: false
---

# Custom API SDK conventions

Verified against `znode10-customapi-sdk` `master` @ `7e30a61` (2026-09-03). File paths are relative to that repo.

## Layout

`Engine.Custom.Api` (host: `Program.cs`, Ocelot, JWT) · `Custom.Api.Core` (controllers, services, `App_Start/CustomDependencyRegistration.cs`) · `Custom.Admin.Core` · `Custom.Libraries.Data` / `.DataAccessCore` / `.DataAccessHelper` · `.DataExchange` · `.ERPConnector` · `.Event` · `.Utility` · `Plugins/{Payment,Shipping,Tax}` · `Extensions/Znode.Libraries.Promotions.Custom`.

## Pattern for a new endpoint

1. **Model** the request and response in the project that owns it (do not return Znode client models unchanged if you only need a few fields).
2. **Service**: an interface and implementation in `Custom.Api.Core/Services`; inject `IZnodeLogging` and the Znode clients you need.
3. **Controller** in `Custom.Api.Core/Controllers`: `[Route("[controller]")] [ApiController]`, inject the service interface only.
4. **Register** the service and every Znode client in `CustomDependencyRegistration.RegisterCustomDI` (`AddScoped<IOrderClient, OrderClient>()`, and so on). A client that is not registered fails at runtime.
5. **Route exposure**: if the endpoint must go through the gateway, add it to `Engine.Custom.Api/Ocelot/CustomOcelot.json`.

Sample to copy the shape from: `Custom.Api.Core/Controllers/CustomSampleEntityController.cs` and `Services/CustomSampleEntityService.cs`.

## Controller conventions seen in the samples

- Return `NoContent()` for an empty result, `Ok(model)` otherwise, `StatusCode(500)` on caught exceptions.
- Catch `ZnodeException` and `Exception` separately; log with `_znodeLogging.LogMessage(ex.Message, "CustomAPILoggingComponent", TraceLevel.Error)`.
- Helpers from `Znode.Libraries.ECommerce.Utilities`: `HelperUtility.IsNull(...)` / `IsNotNull(...)` exist; there is no `IsNullOrEmpty` helper in that class, so use the standard .NET checks for strings and collections.
- Do not log secrets, tokens, card data or full request bodies. Log ids and counts.

## Calling Znode

Use the typed clients (`Znode.Engine.Api.Client`, `Znode.Engine.CommercePortal.Client`, `Znode.Engine.CustomTable.Client`, `Znode.Engine.CommerceConnector.Client`), not hand-built HTTP. The host configuration holds the Znode API root URI and the payment URL (`ZnodeApiRootUri` and `PaymentApplicationUrl`, named in the SDK README) and the gateway and domain credentials (`ZnodeApiGateway`, `ZnodeApiDomainName`, `ZnodeApiDomainKey`: names taken from the SDK skill, ⚠ not yet confirmed in `appsettings.json` because the agent does not read its values). Never print or commit those values; read them from environment variables or a vault.

## Known weak spots in the template: do not copy them

Found by `nd_security_scan.py` and `nd_perf_scan.py` on 2026-10-09 (leads confirmed by reading the lines):

| Where | Problem | Do instead |
|---|---|---|
| `Custom.Api.Core/CustomBaseClient/CustomBaseClient.cs` (lines ~178, 229, 264, 317) | `new HttpClient()` per call | `IHttpClientFactory` or a typed client |
| same file (~182, 270) | `.Result` on `SendAsync`: blocks a thread | `await` the call |
| `Engine.Custom.Api/Program.cs:30` | `AllowAnyOrigin()` CORS policy | Restrict to the storefront origin(s) before production |
| `Custom.Libraries.DataAccessHelper` | Direct entity/stored-procedure access | Only for customer-owned tables (registry: `direct-data-access`) |

Report these to the developer when the customization touches the same files; do not silently rewrite template code that is not part of the request.

## Testing

The SDK has **no test project**. For new logic, add an xUnit project (for example `Custom.Api.Core.Tests`) referencing the service interfaces, and mock the Znode clients. See `quality-testing`.

## Related

`sdk-custom-api` (extension points) · `quality-logging` · `api-auth-and-headers` · `quality-security-checks` · `quality-performance-checks`
