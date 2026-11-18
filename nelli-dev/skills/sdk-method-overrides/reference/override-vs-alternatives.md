# Method override versus the alternatives
What this answers: which extension to pick for a commerce change, and the limits and surprises of overrides.

## Choosing
| Need | Best choice | Why |
|---|---|---|
| Different price per customer/account/profile | Price list (Supported) | Resolved by the engine, cached, visible in Admin |
| New discount rule | Promotion extension, or a built-in promotion type | Runs in promotion order, audit trail and MAD caps apply |
| Final adjustment of shipping/discount/total after everything | Method override | Only hook that runs last |
| Different rate source for shipping/tax | Provider plugin | Contract designed for it; per-store configuration |
| Notify another system after an order | Event/webhook | Asynchronous, no shopper impact |
| New field or rule in checkout UI | Webstore source customization | Labelled as source change |
| New endpoint your storefront calls | Custom API endpoint | No hook needed |

## Limits
- Six hooks; fixed fields read back; storefront calculation hook does not change tax or unit price.
- Synchronous: your latency is the shopper's latency. 5 s client timeout (platform setting).
- No retry. A failed call silently falls back to the default result, so a broken receiver means wrong-but-working totals rather than errors; monitor your receiver.
- Global to the environment, one hook per method, comma-separated chaining only.
- No request validation by Znode: it does not check that your totals add up (release note, KB 80). Order records store what you return.
- Commerce Portal and storefront use different hooks; an order edited in Commerce Portal is not seen by the storefront hook.
- Admin screens (create/manage order in Admin) are not covered by the storefront calculate hook.

## Behaviour to know
- Returning `SkipExecution=false` with new `ResponsePayload` totals changes nothing for calculate hooks.
- Because the hook runs after promotions, discounts you add by override do not appear in promotion reports.
- A non-2xx reply whose body parses is still used (see `request-and-callback.md`).
- A receipt override affects quote and order receipts and emails together.
- Hook registrations are environment data: re-create them per environment.

## Verdicts
| Verdict | Case |
|---|---|
| Supported | Any case a price list, promotion type, shipping rule, tax rule or email template edit covers |
| Customizable | The six hooks with the fields in `hook-catalogue.md` |
| Needs platform change | Any other method (for example intercept order placement, change unit price, change inventory) |
