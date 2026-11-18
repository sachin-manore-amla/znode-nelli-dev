# Building and testing a method override receiver
What this answers: how to implement the endpoint with the Custom API SDK, validate the secret, a worked calculation example, and how to test.

## SDK pieces
The Custom API SDK ships the Event library with:
- `OverrideEventSubscriberController`: `POST ~/callback-event-subscriber`, CORS policy `ZnodeAdminURLCorsPolicy`. It returns 400 when the body is empty or `EventType`/`EventPayload` are missing and 422 when the service returns null.
- `IOverrideEventSubscriberService` / `OverrideEventSubscriberService`: a **sample** `switch` on `EventType` then `EventName` handling the four original methods (`SetTotalSectionInEmailTemplateCompleted`, `BindEmailTemplateDetailsStarted`, `SendEmailCPAdministratorCompleted`, `InitiateTaxCalculationCompleted`), each with a mock-up.
- Model `OverrideZnodeActionEvent` with `ResponsePayload`, `ExtendedRequestPayload`, `WebHookURL`, `SecretKey`, `SkipExecution` plus the base event fields.
The sample **does not check the Authorization header**, and the sample catches exceptions and still returns the input (a no-op). Add a case for `CalculateCart` / `CommerceCalculateCompleted`; the SDK has none.

## Secret validation (add this)
```csharp
[HttpPost("~/callback-event-subscriber")]
public async Task<IActionResult> Subscribe([FromBody] OverrideZnodeActionEvent evt)
{
    string expected = _config["MethodOverride:Secret"];          // from secure configuration
    string received = Request.Headers["Authorization"].ToString();
    if (string.IsNullOrEmpty(expected) ||
        !CryptographicOperations.FixedTimeEquals(
            Encoding.UTF8.GetBytes(received), Encoding.UTF8.GetBytes(expected)))
        return Unauthorized();
    ...
}
```
Use the same value in the Admin Authorization field. Never log the header or `SecretKey`. Znode treats a 401 as a failure and continues with its default result, so a wrong secret fails safe.

## Worked example: handling surcharge on the storefront
Requirement: add 5.00 to shipping for store 12 when the subtotal is under 100.
```csharp
case "CalculateCart" when evt.EventName == "CommerceCalculateCompleted":
    var req = JsonConvert.DeserializeObject<CalcRequest>(evt.EventPayload);
    if (req.PortalId == 12 && req.SubTotal < 100m)
    {
        var resp = new CalcResponse { OverriddenShippingCost = req.ShippingCost + 5m,
                                       OverriddenTotal = req.Total + 5m };
        evt.ResponsePayload = JsonConvert.SerializeObject(resp);
        evt.SkipExecution = true;           // without this nothing is applied
    }
    else { evt.SkipExecution = false; }
    break;
```
Rules for your code: define `CalcRequest`/`CalcResponse` classes from the sample JSON shown in Admin; keep `EventPayload` as received; set both Overridden fields you change (shipping and total) because Znode does not recompute the total from your shipping; tax is not recomputed; return in well under 5 seconds; never throw.

## Testing
1. Unit tests (xUnit, see `quality-testing`): feed envelopes built from the Admin sample JSON; assert `SkipExecution` and each Overridden field; test null/garbage payloads return a no-op.
2. Secret tests: wrong, missing, empty header returns 401.
3. Verify in Admin on a development environment.
4. Functional: add items, change address, apply coupon on the storefront, confirm the cart, checkout and receipt show the same totals (a hook that only runs on some screens shows mismatches), then place an order and read it back through the API.
5. Failure drills: stop the receiver, make it slow (6 s), return 500; the cart must still calculate with default values.
6. Log the `TraceId` from the envelope on both sides.

## Performance and security checklist
No database or remote call per request unless cached; stateless; one pass; log summary only; no personal data in logs; secrets in configuration, not source; HTTPS only; limit the endpoint to Znode's address range where you can. See `quality-performance-checks`, `quality-security-checks`.
