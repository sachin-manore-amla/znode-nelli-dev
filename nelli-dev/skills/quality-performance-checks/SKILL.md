---
name: quality-performance-checks
description: The performance validation Nelli-Dev runs on every customization - static scan for N+1 calls, blocking async, sequential fetches and heavy imports, the per-action API-call budget, caching guidance for the SDK and Webstore, and how to run and report a measured load test. Use in the Performance phase and when designing anything that sits in a shopper's request path.
user-invocable: false
---

# Performance checks

Evidence over opinion. A change is never "fast" because it compiles: report what was measured and what was only estimated.

## 1. Static scan (leads)

```powershell
python ${CLAUDE_PLUGIN_ROOT}/scripts/scripts\nd_perf_scan.py --repo <repo> --git-diff <base ref>
```

Flags: remote or DB call inside a loop (N+1), `.Result` / `.Wait()` on async work, `new HttpClient()` per call, `ToList()` before filtering, sequential independent fetches, client-side fetch in effects, `no-store`/`force-dynamic`, whole-library imports. It cannot measure latency. Confirm each lead by reading it and, for suspected hot paths, by a trace or test.

## 2. Call budget per user action

For each changed user action (page view, add to cart, checkout step, endpoint call) list every outbound call it makes and compare to the baseline before the change:

| Action | Calls before | Calls after | Sequential? | Cacheable? | Notes |
|---|---|---|---|---|---|

Rules of thumb that the review applies:
- A custom endpoint should make the fewest Znode API calls that answer the request; fetch lists once and join in memory instead of calling per item.
- Independent calls run in parallel (`Task.WhenAll`, `Promise.all`).
- A rule that runs on listing, cart and checkout (for example a discount) is evaluated where Znode already computes the price, not by an extra call per product.
- Anything in the shopper's request path (real-time ERP touchpoint, method override) has a timeout and a failure behaviour that does not break the page.

## 3. Caching

- **Webstore:** use the Next.js data cache / revalidation already used by the surrounding routes; do not add `no-store` unless the data must be per-request. Do not cache personalized data in a shared cache.
- **SDK:** the host has a configurable cache (`Caching.CacheType`: InMemory or Redis). Cache reference data with a bounded lifetime; never cache per-user data under a shared key.
- State the invalidation rule for every cache you add (what changes it, how long it can be stale).

## 4. Measured test (when authorized)

Run only where the developer has authorized load against the environment, and never against production.

1. Baseline: measure the unchanged action (p50/p95 latency, error rate, calls per action).
2. Same scenario with the change, same data and concurrency.
3. Report the numbers, the tool and settings, the environment, and the date. Write "not measured" when you did not run it.
4. A regression above the agreed budget (default: p95 +20% or any new error rate) is a finding.

Suitable tools: k6 or a small `curl.exe` loop for an endpoint; Lighthouse or Next.js build output (`npx nx build webstore`) for bundle and page cost. Record the commands in `performance-report.md`.

## 5. Report

Findings table (lead, confirmed?, impact, fix), the call-budget table, the measurements or "not measured", and a one-line verdict: "no blocking performance findings from these checks" or the list of blockers.

## Related

`quality-security-checks` · `sdk-conventions` · `quality-testing`
