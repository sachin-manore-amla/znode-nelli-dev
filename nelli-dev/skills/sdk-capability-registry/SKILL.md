---
name: sdk-capability-registry
description: How Nelli-Dev decides whether a requirement is Supported, Customizable or Needs a platform change - the Capability Registry of Znode extension points, its schema, the verdict rules and how to look entries up and keep them verified. Use in the Architecture phase of every request, and before recommending any extension point.
user-invocable: false
---

# Capability Registry and verdicts

The registry is a set of JSON files (`registry/*.json`, one per extension point). It records, for each extension point, what it is for, the contract, the evidence in the SDK or Webstore source, the limits, and what is **not yet verified**. Nelli-Dev never recommends an extension point that is not in the registry or that it could not verify at its source.

```powershell
python ${CLAUDE_PLUGIN_ROOT}/scripts/scripts\nd_registry.py list
python ${CLAUDE_PLUGIN_ROOT}/scripts/scripts\nd_registry.py find "<requirement words>"
python ${CLAUDE_PLUGIN_ROOT}/scripts/scripts\nd_registry.py show <id>
python ${CLAUDE_PLUGIN_ROOT}/scripts/scripts\nd_registry.py check --sdk <sdk clone> --webstore <webstore clone>   # CI-style check; exit 1 on a bad entry
```

## The verdict (every request gets exactly one, with its evidence)

| Verdict | Test | Action |
|---|---|---|
| **Supported** | A built-in feature or configuration already does it (Admin setting, promotion type, price list, coupon, custom table, notification template). Evidence: a KB article or API operation | Explain how to configure it. No code. |
| **Customizable** | A registry entry with `class: customizable` fits, and its contract is verified for what the requirement needs | Proceed through the workflow. |
| **Restricted** | The only way is a `class: restricted` pattern (for example direct data access) | Ask the developer; allow only for customer-owned data. |
| **Needs platform change** | No supported feature and no verified extension point reaches the required behaviour, or an entry's `platform_change_if` matches | Stop before design. Write a Platform Change Request. Offer a workaround only if its limits are stated. |

Order of checks: Supported first (do not write code for something configuration can do), then Customizable, then Restricted, then Platform change. When two verdicts compete, choose the more conservative and say why.

## Rules

1. **No match is not "supported".** If `find` returns nothing, the requirement is UNKNOWN: search the KB and API documentation; if nothing documents it, classify it as Needs platform change or ask the developer.
2. **Partial means partial.** An entry with `verification.status: partial` lists what is unverified. If the requirement depends on any of those items, the verdict is "Customizable, pending verification": say which fact is missing, how to verify it (read a source file, ask Znode), and do not start implementation until it is settled or the developer accepts the risk.
3. **Webstore source changes are always labelled** "customization of source, not a supported extension point" and carry the upgrade-merge risk in the proposal.
4. **Where the logic lives matters.** A rule that must be identical on listing, cart and checkout belongs in the API/extension layer, not in UI components.
5. **Versions.** State which Znode version the verdict applies to. The registry carries `znode_versions` and the commit each entry was verified against.
6. **Never edit the registry during a customer request.** Report a gap; the registry owner fixes it.

## Entry schema (JSON)

`id`, `title`, `class` (supported | customizable | restricted | platform-change), `extension_type`, `znode_versions`, `summary`, `when_to_use[]`, `not_for[]`, `contract{}`, `evidence[{repo: sdk|webstore, path, note}]`, `docs[{title,url}]`, `apis[]`, `limitations[]`, `known_issues[]`, `platform_change_if[]`, `verification{status: verified|partial|unverified, sdk_commit, webstore_commit, date, unverified[]}`.

`nd_registry.py check` enforces: required keys, valid class and status, evidence paths exist, `verified` has evidence, `partial` lists its gaps, doc URLs are on allowed hosts.

## Adding or updating an entry (registry owner)

1. Read the source file that proves the contract; cite it in `evidence` with a note.
2. Put anything you did not read in `verification.unverified`; do not mark `verified` on the strength of a doc alone.
3. Run `nd_registry.py check`; record the commits and date.
4. Re-verify entries on each SDK, Webstore or Znode release.

## Related

`sdk-custom-api` · `sdk-conventions` · `sdk-method-overrides` · `sdk-events-and-webhooks` · `webstore-customization` · `api-catalog`
