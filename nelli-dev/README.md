# Nelli-Dev: the Znode customization engineer

Nelli-Dev helps customer and partner developers build customizations on Znode using only what customers receive: the Custom API SDK, the Webstore source, their hosted development environment, the Knowledge Base and the API reference. It turns a requirement into a validated, secure implementation, recommends APIs and builds working curls, and reviews customization code. It never changes the Znode platform services and never asks for database access.

It is a Claude Code plugin. Start with `/nelli-dev:setup`.

## Commands

| Command | What it does |
|---|---|
| `/nelli-dev:setup` | First-time setup (gateway URL, project folders, credential) and later changes |
| `/nelli-dev:status` | What is configured and what is in progress (no secrets) |
| `/nelli-dev:deliver <requirement or FSD>` | Verdict, plan, your approval, build, test, security and performance checks, handover |
| `/nelli-dev:advise <requirement>` | Verdict (Supported / Customizable / Restricted / Needs platform change) and approach, no code |
| `/nelli-dev:ask <question>` | Evidence-backed answer |
| `/nelli-dev:recommend-api <goal>` | Which APIs to use, in which order, with parameters and authentication |
| `/nelli-dev:curl <operation or scenario>` | Ready-to-run curl commands against your gateway |
| `/nelli-dev:review <path, branch or diff>` | Review of your customization code (read-only) |
| `/nelli-dev:docs <request id>` | Technical document and deployment guide for a finished request |

The knowledge skills (`sdk-*`, `webstore-*`, `config-*`, `commerce-*`, `api-*`, `quality-*`, `meta-*`) are loaded by the agents as needed and do not appear in the slash menu.

## Contents

| Folder | What |
|---|---|
| `agents/` | `nelli-dev` (lead) and six specialists: `api-curl-builder`, `sdk-builder`, `webstore-builder`, `test-author`, `code-reviewer`, `doc-writer` |
| `skills/` | 9 commands and 50 knowledge skills; `README.md` is the index and the source precedence |
| `hooks/` | The guard hook (`hooks.json`) |
| `registry/` | The Capability Registry (JSON): the source of each verdict |
| `scripts/` | Tools: guard, configuration, credential, spec query, scanners, progress, verification |
| `knowledge/` | The curated product-knowledge pack and API specs shipped with the plugin |
| `evals/` | Regression questions |
| `tests/` | Script tests |

## Setup in short

1. Add the plugin to Claude Code (plugin folder or marketplace; see the release notes for your distribution).
2. Run `/nelli-dev:setup`. It records your gateway URL (a development or test environment, never production) and your project folders in one central file (`%USERPROFILE%\.nelli-dev\config.json`, no secrets), then asks you to run one command in your own terminal to save your credential in the Windows Credential Manager (hidden input). The credential never goes through the chat, files or logs.
3. Put exported API specs in `<workspace>\nd-knowledge\specs\` (for example `commerce.json`, `core-v2.json`).

Other systems without the Windows credential store: record an environment variable name with `nd_setup_token.py --use-env-var`.

## How the guardrails are enforced

Two layers: the agents' instructions, and a PreToolUse hook (`scripts/nd_guard.py`, wired in `hooks/hooks.json`) that refuses what an agent must not do. The hook applies to Nelli-Dev's own agents only (`agent_type` `nelli-dev:*`); your other work in the same session is not restricted. Every command except `setup` and `status` runs inside a Nelli-Dev agent, so the hook always applies to it.

- file access only inside the workspace, the project folders you recorded and the plugin folder (read-only); `.env*`, keys and certificates are never read or written; `appsettings*.json` asks first
- before an approved plan exists, only `nd-work\` and `nd-knowledge\` can be written
- approval is bound to the plan files (`nd_approve.py`): change the plan and the approval is void
- HTTP tools may call your recorded gateway and the public Znode documentation sites only; non-GET calls ask first
- the central configuration and the credential store are reachable only through the `nd_*` scripts; no command prints the token
- shell: no `git push`, hard resets, recursive deletes, env-file reads, environment dumps or writes outside the workspace; asks before package installs and deploy commands

At the start of every run the agent proves the hook is active by reading a deliberately forbidden probe path and checking that the refusal comes from the guard. If it does not, the agent stops.

## Support and feedback

Report problems and knowledge errors through the Znode support site: https://support.znode.com

<support contact to be confirmed by Znode>

First run `/nelli-dev:status` to check your configuration (gateway, credential state, project folders). Then include in your report:

- the plugin version (from `.claude-plugin/plugin.json`)
- the command you used (for example `/nelli-dev:advise`) and what you asked
- the confidence line from the answer
- what you expected and what you got, and for a knowledge error the Knowledge Base page or API reference that shows the correct behaviour

Do not include secrets (tokens, passwords, keys, connection strings) or customer data (names, addresses, order or account details). Remove them from any text, log or screenshot first.

## License

See `LICENSE`. See `KNOWN-LIMITS.md` for what the plugin does not cover and `RELEASE-NOTES.md` for what changed.

## Maintenance

- `python scripts/nd_verify.py`: layout, commands, agents, hook, guard self-test and registry check must all pass.
- `python scripts/nd_registry.py check --sdk <sdk clone> --webstore <webstore clone>`: re-verify entries on each SDK, Webstore or Znode release.
- `python scripts/nd_scan_customer_safety.py agents skills registry --allow-file knowledge/scan-allow.txt`: 0 leads before any release; a person reviews adapted skills.
- `python tests/test_phase2.py`: configuration, credential store and token-leak tests.
