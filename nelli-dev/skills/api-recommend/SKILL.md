---
name: api-recommend
description: How Nelli-Dev recommends which Znode APIs to use for a customization requirement - the ordered routes, why each, full parameters, headers and authentication, and which API to use for which purpose, preferring supported SDK and extension points and flagging legacy v1. Use when the developer asks which API to call or how to achieve something through APIs.
user-invocable: false
---

# Recommend the APIs for a requirement

Input: a requirement or goal in plain words. Output: the ordered set of APIs that implement it, written so it can be handed to the developer's team as it stands. This step calls nothing; the curl workflow (`api-curl-workflow`) proves what is recommended.

## Method
1. **Understand the goal.** Break it into the data and actions involved (read a catalog, create a cart, place an order, store custom data). Use the registry (`nd_registry.py find "<words>"`) and `meta-customization-landscape` to see whether this is plain API use, or needs a supported extension (a custom endpoint in the Custom API SDK, an event, a method override, a custom table). A need that only a platform change could meet is reported as such (verdict: needs a platform change), never worked around.
2. **Find candidates in the API reference.** `nd_query_spec.py paths all --grep "<words>"`, then `nd_query_spec.py op <spec> "<route>"` for each candidate. Prefer the current families (Commerce, Core v2, Dynamic Data Table, Payment v1, Reports, ERP Touch Point). The legacy v1 is named only when nothing current covers the need, and flagged.
3. **When several APIs overlap, choose.** Say "use X when ..., use Y when ..." with the deciding fact (store scope, published or draft data, B2B or B2C, paging, who may call it). Never return an undifferentiated list.
4. **Order them.** Dependencies first (an id from one call feeds the next), then the action. Note paging, filters, published-versus-draft data and required headers (`api-auth-and-headers`).
5. **Give the full parameter details for each route:** method and route, version, purpose, every request parameter and every response field that matters (name, type, required, allowed values, one-line meaning), the authentication and headers the caller sends, the status codes and error shapes the spec declares. Read them from the spec, not from memory.
6. **Customization lens.** Say where the requirement is better met by a supported SDK extension than by calling platform APIs from the Webstore (security, ownership checks, call budget), and which side performs authentication.

## Output rules
- Nothing internal: no database, tables, columns, stored procedures, connection strings, internal hosts or repositories, no how Znode stores or computes a value. Only what a caller needs.
- Every claim about a route is from the spec you read this run (cite the spec key and route). Mark anything not in the spec as unverified.
- Offer working curls for the chosen routes (`/nelli-dev:curl`) once the gateway and credential are set up.
- End with the confidence and what was not checked.
