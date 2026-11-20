# Nelli-Dev skills index

Knowledge for the Nelli-Dev agent. Skills are plain markdown (`<skill>/SKILL.md`). The agent preloads a small starter set and reads the rest in full before relying on them. A skill is never cited unread.

**Provenance.** Skills marked *adapted* were copied from the Znode in-house knowledge base and scrubbed of internal-only content (database objects, platform source repositories, internal hosts and process). Skills marked *new* were written for this agent from the Custom API SDK and Webstore source. Adapted skills have **not** all been re-verified against the customer-facing KB: treat them at "skill only" confidence (50-70%) until a person has verified them, and say so.

## Core (preloaded)

| Skill | Scope | Origin |
|---|---|---|
| `sdk-capability-registry` | Verdict rules and the registry of extension points | new |
| `sdk-custom-api` | The SDK project layout and the five extension points | adapted, SDK-verified |
| `sdk-conventions` | Code patterns, registration, logging, template weak spots | new, SDK-verified |
| `api-catalog` | The API families, v1 legacy rule, finding operations | new |
| `api-auth-and-headers` | Authentication modes and Znode-* context headers | adapted |
| `quality-security-checks` | Security phase | new |
| `quality-performance-checks` | Performance phase | new |
| `meta-document-templates` | The document set and templates | new |
| `meta-knowledge-sources` | Verified KB and API-reference URLs, the key articles, how to read and cite them | new, verified live |
| `meta-customization-landscape` | Every customization option and which fits which requirement | new |

## On demand

| Area | Skills |
|---|---|
| Start here | `meta-customization-landscape` (the ladder of options and which skill fits which requirement) |
| Data model | `commerce-product-attributes` · `config-global-attributes` (user-defined fields) · `sdk-custom-tables` · `commerce-product-overrides` |
| Extension points | `sdk-method-overrides` · `sdk-events-and-webhooks` · `sdk-provider-plugins` · `sdk-extension-framework` |
| Integration | `sdk-data-exchange` · `config-import-export` · `api-consumption` · `webstore-headless-api` |
| Webstore | `webstore-customization` · `webstore-page-builder-and-themes` · `webstore-cms` · `commerce-search-seo` |
| Admin and portals | `config-admin-customization` · `config-roles-permissions` · `config-commerce-portal` · `config-bstore` · `config-stores-tenancy` |
| Configuration | `config-global-settings` · `config-store` · `sdk-extension-settings` · `config-notifications` |
| Commerce behaviour | `commerce-promotions-and-pricing` · `commerce-tax-shipping` · `commerce-checkout-payments` · `commerce-orders-and-checkout-customization` · `commerce-orders` · `commerce-returns` · `commerce-inventory` · `commerce-b2b-accounts` · `commerce-catalog` |
| Quality | `quality-testing` · `quality-logging` |

Retired and replaced: old pricing-promotions skill and old vouchers skill (now `commerce-promotions-and-pricing`), old plugins skill (now `sdk-provider-plugins`), old webstore-source skill (now `webstore-customization`).
## Answer source order

1. Product knowledge (the customer-safe pack, `nd_pack_search.py`) with the skills and the registry: form the solution and answer here first.
2. API reference (exported specs, apidocs.znode.com): find and confirm every API named.
3. Knowledge Base (support.znode.com): confirm, correct or extend.

## Source precedence (highest first)

1. The customer's code and the exported API specs (actual behaviour)
2. The customer's requirement and FSD (intent)
3. The Znode Knowledge Base (support.znode.com) and the API reference (apidocs.znode.com)
4. These skills
5. General knowledge of .NET or Next.js (never for Znode-specific facts)

When sources disagree, follow this order, record the conflict, and raise it in the proposal if it changes the scope.

## Scripts (in the package `scripts\` folder)

| Script | Does |
|---|---|
| `nd_projects.py` | Detect, record and list the folders where the SDK and Webstore are cloned (the agent asks, never assumes) |
| `nd_env.py` | Record and check the developer's gateway URL (the agent asks, never guesses; only that host may be called) |
| `nd_config.py` | The central configuration (one user-level file, no secrets): status, what is missing |
| `nd_cred.py` | Credential state and removal (no command prints a token; only scripts use it) |
| `nd_setup_token.py` | The developer enters the credential in their own terminal (hidden input, credential store) |
| `nd_migrate.py` | Carry old Z-Custom environments, projects and request folders into Nelli-Dev (dry run first) |
| `nd_close_check.py` | End-of-run gate: progress file closed, required documents present with a Checked line, approval still matches the plan |
| `nd_registry.py` | List, search, show and check the Capability Registry |
| `nd_query_spec.py` | Query exported API specs; build a curl for an operation |
| `nd_guard.py` | Hook: workspace, approval-gate and secret rules, enforced outside the model |
| `nd_approve.py` | Record and verify the developer's approval, bound to the plan files |
| `nd_progress.py` / `nd_track.py` | Per-request progress file; tracked runs with a heartbeat |
| `nd_security_scan.py` / `nd_perf_scan.py` | Security and performance leads |
| `nd_scan_customer_safety.py` | Internal references and secrets in anything to be handed over |
| `nd_version_stamp.py` | What a document was built from |
| `nd_find_earlier.py` / `nd_list_tools.py` | Earlier output on a topic; the tools available now |
