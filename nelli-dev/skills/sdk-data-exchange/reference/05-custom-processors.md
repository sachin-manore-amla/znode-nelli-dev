# Custom processors for Data Exchanges
Answers: how to write, deploy and register a processor, which of the two models to use, and how an exchange reaches it.
Confidence: Custom API SDK source (90), KB developer guide read through a summary (75).

## Two models
| | IBaseProcessor (multi-step) | Legacy ProcessData class (two-step) |
|---|---|---|
| Interface | `IBaseProcessor` in `Znode.Libraries.CommerceConnector.SDK` | none; a class with `ProcessData()` |
| Hooks | `BeforeStepAsync`, `AfterStepAsync` per step | one `ProcessData` for the whole exchange |
| Data access | `executionOutputs` list of `TransmissionStepExecutionOutput` | `PostInputHandlerAsync` returns data parsed by the exchange mapping; `PostOutputHandlerAsync` sends to the destination |
| Constructor | `(IServiceProvider)` | `(IHandlerClient, IZnodeLogging, IServiceProvider, int logId)` |
| Use for new work | Yes | Only to maintain existing |
| Execution History / dashboard | Not shown for processor exchanges | Not shown |

## IBaseProcessor
```csharp
public class MyProcessor : IBaseProcessor
{
    public MyProcessor(IServiceProvider sp) { _log = sp.GetService<IZnodeLogging>(); }
    public async Task BeforeStepAsync(List<TransmissionStepModel> context,
        TransmissionStepModel step, List<TransmissionStepExecutionOutput> executionOutputs) { }
    public async Task AfterStepAsync(List<TransmissionStepModel> context,
        TransmissionStepModel step, List<TransmissionStepExecutionOutput> executionOutputs)
    {
        if (step.StepCode == "step1")
            executionOutputs.Add(new TransmissionStepExecutionOutput {
                StepCode = step.StepCode, OutputData = "...", DataFormat = "JSON" });
    }
}
```
Rules from the guide: return completed tasks, handle nulls, wrap logic in try and catch and log with `IZnodeLogging` (`LogMessage(message, source, TraceLevel)`), target a step with `step.StepCode`, keep processors lightweight and **stateless** (no statics), resolve services from the injected `IServiceProvider`. Lifecycle per step: BeforeStep, the step runs, AfterStep. `DataFormat` examples: `Text`, `JSON`. Behaviour when a processor throws, and order with several processors, are not stated.
Prefer built-in functions and mapping over a processor.

## Project and deployment
1. Class library in the Custom API SDK solution (sample: `Custom.Libraries.DataExchange`), referencing the Commerce Connector SDK package and the observability package.
2. `extension.manifest.json` next to the assembly (see `sdk-extension-framework`): `supportedContracts` is `["IBaseProcessor"]`.
3. `znode connect <token>`, then `znode deploy extension "<path to .csproj>"` or `znode deploy extension "<parent folder>"` (the CLI builds each project and uploads the assemblies).
4. Register: in the exchange, tick **Custom Processing Required** and set **Processor File Name** (legacy model: the class name). For `IBaseProcessor` the guide says to enter a descriptive **Processor Name** and a **Class Name** that exactly matches the deployed class, in Commerce Connector configuration. Where that screen is and how a processor is attached to a step is not stated (GAPS).
Not available for processors: Extension Observability, Sync, execution log viewer, health dashboard. Debug with `IZnodeLogging` platform logs, local debugging and the transmission results.

## How the legacy model is invoked
The Commerce Connector calls a route on the customer's Custom API (`custom-data-exchange/execute-data-exchange` with the exchange id and the log id). The SDK service reads the processor name from the exchange, finds the class by name in the `Libraries.DataExchange` assembly by reflection and runs `ProcessData()`. A class not found logs "Processor file not found". The gateway forwards `dataexchanges/custom-data-exchange/...` to the Custom API. The SDK also exposes `custom-data-exchange/get-processor-code` which returns the source of the named processor (used by the "download processor file code" feature, 10.6.0.0).
Both `ErpExchangeCode` (unique) and `ErpExchangeName` (may repeat) are accepted in the handler request; the code is the one to use.

## Mapping types a processor can complement
Direct, fixed, default, formula, conditional, lookup, transformation, object, collection (reference 02). Use a processor only for logic outside these.

## Security
Never hard-code credentials in a processor; use Credential Vault variables for exchange steps. Do not log payloads that hold personal data. Processors run inside the Custom API with the same reach as other SDK code: no direct database access is allowed by the platform guidance.
