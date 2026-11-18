# Caching, CORS, security and documentation gaps for headless clients

What this answers: how to cache API data safely, what the KB says (and does not say) about CORS and rate limits, security rules for a custom front end, how to test and debug, and what is undocumented.
Confidence: KB "Headless API Consumption" and troubleshooting article (80); Webstore source for the caching pattern (90). Anything marked "not documented" needs an answer from Znode.

## Caching

| Data | Safe to cache | How the Webstore does it |
|---|---|---|
| Store settings, menu, CMS content, banners | yes, per store, locale and publish state | Next data cache with tags plus an in-memory store cache; evicted on publish events |
| Product and category data | yes, shared across anonymous visitors | tagged cache when enabled; price and inventory refreshed live on pages |
| Prices | per user, account and profile; do not share between shoppers | live fetch for visible SKUs |
| Cart, checkout, account | never shared | no caching; per-user requests |

Rules: the cache key must include store code, locale, publish state, and profile or account when the data is personal. Refresh caches on publish: the Webstore receives a publish event call from the API; a separate front end needs its own invalidation path (poll with a short TTL, or ask whether your instance can send its events to a webhook of yours, `sdk-events-and-webhooks`). KB: "Implement rate-limit handling and caching strategies".

## CORS

Not documented in the KB articles read, nor in the public specs. The Webstore avoids the question by calling the gateway from its server. Treat browser-direct calls as unsupported until Znode confirms the gateway's allowed origins for your tenant.

## Rate limits

The KB says to learn the limits ("Rate Limits") and handle 429, but gives no numbers. Not documented.

## Security rules for a custom front end

1. Credentials (domain key, API key, client secrets) only on the server; the Webstore keeps them out of the browser bundle.
2. Take the user and account from your own authenticated session; never from a request body or query string.
3. Validate every input in your BFF and rely on the API for ownership checks; test with another shopper's ids (`quality-security-checks`).
4. Do not log tokens or card data; payment data goes to the provider's script and returns a token (`commerce-checkout-payments`).
5. Set a content security policy for payment and analytics scripts; the Webstore reads CSP from Admin store and global settings.
6. Add reCAPTCHA on login, registration, contact and checkout; the API-side flags exist as store settings and the Webstore validates tokens on the server.
7. Use HTTPS only; store tokens in secure, http-only cookies, not local storage, when the front end is a browser app.

## Test and debug (KB)

Use Postman or Insomnia to isolate the request from your code; browser Network tab for CORS, 401 and 500; log status, payload and endpoint without sensitive data; unit tests mock responses; integration tests run against a test environment. Production issues: Admin > Dev Center > Application Logs with categories Event, Database, Integration and types Error, Info, Warning, Debug; filter by application. Common causes by status: wrong environment URL, missing or wrong store header, expired token, wrong HTTP method.

## Gaps to raise with Znode

| Gap | Why it matters |
|---|---|
| Token endpoint for customer-facing JWT (`POST /token` in the KB, not in the specs) | cannot build login without it |
| Which routes the Webstore uses that are absent from the public specs (product list, product by SKU, category by key) | the public list route is by category code only |
| How `Z-Request-Context` is produced for third-party clients | required by the API for user-scoped calls from the Webstore |
| CORS policy and allowed origins | browser-direct clients |
| Rate-limit values | capacity planning |
| Webhook or event path to invalidate a custom front end cache | stale data |
| Whether Page Builder JSON can be fetched and rendered outside the Webstore stack | reuse of CMS pages |
