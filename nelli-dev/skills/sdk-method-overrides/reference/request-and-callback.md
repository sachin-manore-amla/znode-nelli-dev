# Method override request and callback
What this answers: the exact envelope Znode sends and expects, every field, secret handling, timeout, failure behaviour and ordering.
Source: product source and the SDK `Custom.Libraries.Event` project (95).

## Envelope (same shape both ways)
Znode POSTs `application/json` to each URL. Fields:
| Field | Direction | Meaning |
|---|---|---|
| `EventId`, `EventVersion`, `TraceId` | in | Identifiers; log the trace id |
| `EventType` (obsolete) / `EventModule` | in | Module code, for example `CalculateCart`, `Quote`. The SDK sample validates `EventType` is present: send back unchanged |
| `EventName` | in | Method name, for example `CommerceCalculateCompleted` |
| `EventDataId`, `EventDataCode` | in | Record key. Calculate hook: order number and class code; receipt hooks: quote id and number; tax: cart number |
| `EventPayload` | in and out | JSON **string** of the request model. Return the (possibly changed) model here |
| `ExtendedRequestPayload` | in | Extra named values as a JSON string, for example `{"MessageText":"..."}` |
| `ResponsePayload` | out | JSON string of the response model (the thing Znode applies) |
| `WebHookURL` | in | The URL(s) Znode is calling (informational) |
| `SecretKey` | in (body) | The configured Authorization value. Do not log it |
| `SkipExecution` | out | `true` = use my response instead of the default; `false` = continue with default (request changes in `EventPayload` still flow on) |
| `UserId` | in | Logged-in user id that raised the call (may be empty/0 for scheduled work) |
| `EventTimeStamp`, `Source` | in | Time (UTC) and optional origin |

`EventPayload` and `ResponsePayload` are strings holding JSON (double-encoded). Deserialize twice.

## What Znode does with the reply
1. Reads `EventPayload` back into the request model (updated request).
2. Reads `ResponsePayload` into the response model.
3. If `SkipExecution=true` and the response model exists: the caller uses the response (full override).
4. Else the caller continues its default logic with the updated request.
For the calculate hooks only step 3 changes totals.

## Security
- Header `Authorization: <value typed in Admin>` is sent exactly as entered (`Bearer ...`, an API key, anything). If the field is empty a placeholder Basic value is sent, so an unconfigured hook is never anonymous but is also not secret.
- Znode does not sign the body. Validate the header with a constant-time comparison against a secret held in your configuration, and accept only HTTPS.
- Treat the body as untrusted input (validate JSON and numbers); the call comes from Znode but the secret is the only proof.
- The URL is validated only as an absolute http/https URL (Admin additionally enforces a host with a dot). Plain http is accepted: do not use it outside a private network.

## Timeout and failures (caller side)
| Situation | Result |
|---|---|
| No webhook registered, or inactive | Hook skipped silently; default logic |
| Request timeout (default 5 seconds, platform setting) | Error logged; default logic; no shopper error |
| Non-2xx reply | Error logged, **but the body is still parsed**; a JSON body with `SkipExecution=true` would still be applied. Return 2xx with a safe body or an empty no-op |
| Unparseable or empty body | Treated as no response; default logic |
| Your exception | Same as above: default logic |
| Calls slower than 2 s | Logged as a warning on the Znode side |
The call is blocking: a slow endpoint slows the shopper's cart and checkout directly. Cache, avoid chained remote calls, and return quickly.

## Ordering with other logic
- `CommerceCalculateCompleted` runs **last**, after shipping, promotions and coupons, tax, vouchers. Your values overwrite the result; nothing recalculates afterwards.
- `InitiateTaxCalculationCompleted` runs **before** the tax manager call.
- Receipt hooks run while the receipt text is assembled; later token replacement (store name, order number) still runs on text you return for the non-skip case.
- Registered URLs separated by commas run in the order written; each next call receives the previous `EventPayload`; the final reply is the one applied.

## Limits and behaviour to know
- One webhook per method (a second create returns "Webhook is already configured for the MethodName").
- Hooks are global to the environment, not per store.
- Changes made in Admin (create, edit, enable, disable, delete) clear Znode's hook cache, so take effect on the next call.
- The release notes recommend the latest Storefront for the 10.10 calculation override; older storefronts may support it only partly.
