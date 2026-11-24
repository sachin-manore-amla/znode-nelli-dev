---
name: api-catalog
description: The Znode API families available to customers (Core v2, Commerce, Dynamic Data Table, Payment v1, Reports, ERP Touch Point, and the legacy Core v1), which API to choose for which data, the rule against legacy v1, and how to find and verify an operation with nd_query_spec.py. Use whenever a recommendation names an API or endpoint.
user-invocable: false
---

# Znode API catalog (customer view)

Source: the Znode 10 API Reference, https://apidocs.znode.com/ (a Stoplight site; read it in a browser-capable tool or from exported spec files, not with a plain page fetch). Overview read 2026-10-09.

| API family | Use it for | Spec key |
|---|---|---|
| **Core API (v2)** | The preferred general platform API: catalog, accounts, stores and the rest of the core platform | `core-v2` |
| **Commerce API** | Orders, quotes, carts, save-for-later, saved carts, order templates, approval routings, returns | `commerce` |
| **Dynamic Data Table API** | Custom tables: create and manage custom data structures | `custom-table` |
| **Payment API (v1)** | Transactions, payment methods, payment processing through plugins | `payment` |
| **Reports API** | Sales, customer and product reports | `reports` |
| **ERP Touch Point API** | Synchronizing data between Znode and an ERP | `erp` |
| **Core API (v1) - legacy** | Existing legacy implementations only. Documented separately | `core-v1-legacy` |

## Rules

1. **Never recommend Core API v1 for new work.** If a requirement appears to need a v1 operation, check whether a v2 or Commerce operation covers it; if none does, say so, mark the dependency as "legacy v1, no preferred alternative found" and let the developer decide.
2. **For orders, quotes, carts, saved carts, order templates, approval routings and returns, prefer the Commerce API** over Core API operations.
3. **Every API named in a proposal is verified.** Find the operation in a spec file with the tool below; an operation you could not find is written as "NOT VERIFIED" and is not used in code.
4. **Authentication and headers** differ by API family: see `api-auth-and-headers`.

## Finding and checking an operation

Place exported spec files at `<workspace>\nd-knowledge\specs\<key>.json` (for example `commerce.json`).

```powershell
python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_query_spec.py specs
python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_query_spec.py paths all --grep "<keyword or route>"
python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_query_spec.py op commerce "/v1/carts/{cartId}"
python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_query_spec.py curl commerce "/v1/carts/{cartId}" --base <gateway url> --set cartId=<id>
```

With a gateway recorded by `nd_env.py`, `--base` can be omitted. Run these from PowerShell (a Unix-style shell rewrites arguments that start with `/`). `curl` builds the Authorization header from the `ZNODE_API_BASIC` / `ZNODE_API_TOKEN` environment variables at run time and never prints a secret. Commands marked `[WRITE]`, `[MONEY]` or `[CARD]` are handed to the developer, never run by the agent.

## Gaps (to fill)

- The spec files themselves are not in the knowledge pack yet; until exported, operations can only be confirmed by reading the API reference site page by page.
- Which family a given Core v2 operation belongs to is not yet mapped here.
