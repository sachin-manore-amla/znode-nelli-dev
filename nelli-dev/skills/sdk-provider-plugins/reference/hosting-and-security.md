# Plugin hosting, security and testing
What this answers: where a plugin runs, how Znode reaches it, how to protect credentials and how to test and diagnose.
Sources: shipping manager source and SDK templates (95); KB Integrating Custom Shipping Plugins (hosting "not stated", 80).

## Hosting
A plugin is an independent ASP.NET Core 8 service (Docker files and compose in the templates), versioned separately from Znode. Znode stores its **base URL** with the installed plugin and posts to it. Host it where Znode can reach it and the internet cannot (cluster-internal or private network). Hosting platform and registration steps are not stated in the KB.

## Calling behaviour (verified for shipping)
| Aspect | Behaviour |
|---|---|
| Method and body | POST JSON with the configuration set and global configuration in the body |
| Authentication | none sent by the manager |
| Timeout | default web request timeout (about 100 s); no retry |
| Failure | exception or non-JSON reply yields no result for that shipping type; other types continue |
| Parallelism | one task per shipping type, limited by a platform setting |

## Security rules
1. Not publicly routable; restrict by network policy to Znode.
2. Because the manager sends no credentials, authenticate by network, not by header. Do not trust a header you cannot verify.
3. Bodies contain provider secrets: never log request bodies, never write them to disk or telemetry.
4. Keep provider credentials only in configuration sets; never hard-code or commit them. Rotate by editing the set.
5. Validate input (null cart, negative quantities); return `ErrorDetail`, never a stack trace.
6. Keep call time short: shipping runs at every cart change; cache carrier tokens, set short outbound timeouts (a few seconds) and fall back to an error response.
7. TLS to the provider; pin to the vendor's published hosts.
8. Add a health endpoint and monitor errors yourself: Znode hides plugin failures from the shopper.

## Testing
Unit test the service with sample requests copied from the template artifacts; contract test the JSON (field names, `ShippingRate` > 0, `ResponseMessage` not null); run the compose file locally; then install on a development environment, create a method, and test cart estimates with an address, a heavy cart, an excluded country, a provider outage (must hide the option, not break checkout), then place an order. Use `quality-testing` for evidence.

## Diagnosing "method missing"
Plugin active? Configuration set exists and attached to the store? Shipping method enabled, associated to the store and profile-compatible? Service code mapped? Plugin reachable and returning rate > 0? Header with a valid user id on the estimates call? Check the plugin's own logs first.
