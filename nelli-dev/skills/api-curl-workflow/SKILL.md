---
name: api-curl-workflow
description: How Nelli-Dev turns an API operation or scenario into a working curl against the developer's recorded gateway without a database - find the operation in the spec, discover each required value from earlier responses, read-only GET calls and spec examples, prove the GETs live, hand over writes unrun. Use for any curl, working request or "how do I call this" task.
user-invocable: false
---

# From operation to working curl (no database)

Scripts are in `${CLAUDE_PLUGIN_ROOT}/scripts`. Run them with `python` (PowerShell; a Unix-style shell rewrites arguments that start with `/`).

## Inputs
- the scenario or route (`POST /v1/carts`, "add a product to the cart", a route from an API recommendation)
- the environment: the recorded gateway (`nd_config.py status`); never a host the developer did not record, never a default
- audience: the developer (default) or a client; client-facing output follows `api-recommend` (no internal names)

## Steps
1. **Configuration.** `nd_config.py status --json`. If the gateway or credential is missing, stop and offer `/nelli-dev:setup`. Never ask for a token in chat.
2. **Find the operation.** `nd_query_spec.py paths <spec> --grep "<words>"`, then `nd_query_spec.py op <spec> "<route>"`. Prefer the current API family (Commerce, Core v2, Dynamic Data Table, Payment v1, Reports, ERP Touch Point); the legacy v1 only when nothing else covers it, and say so (`api-catalog`).
3. **Discover the values.** `nd_discover.py resolve --spec <spec> --op "<METHOD /route>" --key <request id>`. It resolves each required input from, in order: what the developer gave, earlier saved responses, a read-only GET on the gateway that returns the field (page size at most 5), the spec example. It states for each value where it came from and whether it is proven live. Read the table honestly:
   - "proven live": real data from the developer's environment
   - "earlier response": real data from a previous call
   - "spec example, NOT proven": say so in the output; never present it as verified
   - unresolved: ask the developer, in one round, with 2 to 4 options (a value they type, or the call that would return it)
4. **Build the curl.** Run the `curl` command line that `nd_discover.py` prints (`nd_query_spec.py curl ...`), with `--base` from the recorded gateway when it is not picked up. It marks `[WRITE]`, `[MONEY]` and `[CARD]` operations.
5. **Prove the GETs.** For a GET, run it: `nd_call.py GET <route> --query k=v --key <request id> --save`. Report the status and the key fields of the response (the output is already redacted). A GET is proven only when it returned success; a 401 or 403 is a finding (`api-auth-and-headers`), not a curl to hand over as working.
6. **Writes are handed over, not run.** `[WRITE]` commands go in the answer with the exact body and a note that they change data. Run one only when the developer approved that exact call in this conversation, using `nd_call.py <METHOD> ... --allow-write` (the guard asks again). `[MONEY]` and `[CARD]` calls are never run here.
7. **Dependencies.** For a scenario, return the hops in order (hop, METHOD route, why, values it needs, where each came from) and one command per hop, so the output of one call feeds the next.

## Hard limits
- No database, no credential reads, no host except the recorded gateway. At most 25 calls per request key; the scripts enforce it.
- The curl you show uses the placeholder `$env:ZNODE_API_BASIC` or `$env:ZNODE_API_TOKEN` for the credential; never a real value. Scripts add the real one inside the process.
- Everything shown or saved is redacted; do not paste raw response data that contains personal data.
- End the answer with: what was proven live, what is spec-only, what is unresolved, and the confidence.
