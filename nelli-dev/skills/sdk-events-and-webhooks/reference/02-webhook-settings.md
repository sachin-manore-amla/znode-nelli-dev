# Webhook settings, delivery and security
Answers: the Admin screen fields, the API, delivery behaviour, and how to secure an endpoint.
Confidence: product source (90), Admin resource strings (90), KB (75).

## Admin
Dev Center > **Webhook Settings** > page "Manage Webhook Settings". Grid: Event Module, Event Name, Webhook URL (shown truncated after 100 characters; hover shows all), Is webhook enabled, Authorization, Action (edit, delete, enable or disable toggle). **Add New** opens "Add Webhook Event".
| Field | Help text on screen / rule |
|---|---|
| Event Module | Select the module where the event originates |
| Event Name | Created, Updated, Deleted and the module-specific names. Locked after creation |
| Is Active | "Toggle to enable or disable sending this event to the configured webhook URL." |
| Webhook Url | Full URL for HTTP POST. Several URLs comma separated. Up to 1000 characters (API) |
| Authorization | "Enter credentials or a token required to authorize webhook requests. This will be included in the Authorization header exactly as provided (e.g., Bearer token or API key)." Optional |
| Verify | Checks reachability and format; an error covers unreachable URL, bad format or authorization required (then fill Authorization and verify again) |
Duplicate module + name: an error says the URL is already configured for that combination. Editing: only Is Active, Webhook Url and Authorization. Delete and enable or disable ask for confirmation ("Are you sure you want to Enable this WebHook URL?").

## API (core v2)
`GET /v2/events` (module names), `GET /v2/events-list`, `GET /v2/events/{eventModule}` (names), `GET /v2/events/{eventName}/{eventModule}`, `POST /v2/events` (body `EventName`, `EventModule`, `WebHookURL`, `IsWebHook`, `Authorization`), `PUT /v2/events/{eventName}/{eventModule}`, `DELETE /v2/events/{eventName}/{eventModule}`, `PUT /v2/events/{eventName}/{eventModule}/{isWebHook}` (enable or disable the webhook).

## Delivery rules (observed in product source)
- Events are published to the message broker; a platform consumer looks up the webhook record from a cached list and posts to each valid URL in parallel.
- A URL must parse as absolute http or https; invalid ones are skipped and logged.
- Per request timeout: `WebhookRequestTimeoutInSeconds`, default 5. After that the call is cancelled.
- Result not awaited by Znode; non-2xx or exceptions are written to the log. **No retry, no dead letter, no ordering guarantee.**
- If the feature flag is off, or the event or webhook is disabled, nothing is sent.
- The enabled-event list is cached: a change in Admin applies after the cache refreshes (the Admin save invalidates it; allow a short delay).
- Events that fire inside a transaction are raised after the action succeeded.

## Hosting the receiver
Receiver requirements: `POST`, accepts the JSON body, answers 2xx quickly. In the Custom API SDK the sample route is `flash-event-subscriber` (HTTP POST to the SDK host; 400 when module or payload is empty). Deploy with the Znode CLI (`sdk-extension-framework`), verify at the host's Swagger page, then put the URL in Webhook Settings. For direct cluster access the KB shows the cluster-local root URL plus the route; ask your DevOps contact for the host name.
CORS: add the Admin URL to `ZnodeAdminURLCorsPolicy` (appsettings, `appsettings` section) for Admin-initiated calls such as Verify. Server-to-server delivery is not subject to CORS.

## Security
| Check | Why |
|---|---|
| Set an Authorization value and compare it in the receiver (constant-time) | Anyone who knows the URL could post fake events |
| Use HTTPS only | Token travels in a header |
| Treat the body as untrusted input: validate module, name, ids; do not trust `UserId` | |
| Idempotency: key on `EventId` | The same event may be delivered more than once by your own broker |
| Return 2xx fast, process asynchronously | 5 second timeout, no retry |
| Do not log full payloads with personal data | Logs are shared |
| Do not put the secret in the URL | URLs appear in logs and Admin grids |
Znode does not sign the body. The KB tells whitelisting of a `znode-multifront/1.0` user agent for another broadcast: it is not documented for webhooks.

## Testing
Local: expose the Custom API with a tunnel (the KB uses a Cloudflare tunnel), register the tunnel URL plus route as the webhook URL with Authorization, trigger the action in Admin, watch the log. Broker consumer: see reference 03.
