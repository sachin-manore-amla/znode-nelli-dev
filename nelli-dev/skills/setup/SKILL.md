---
name: setup
description: First-time setup and later changes to the Nelli-Dev configuration - gateway URL of the developer's development environment, authentication scheme, the folders of the customization code (Custom API SDK, Webstore) and the credential. Use when the developer runs /nelli-dev:setup, when a command finds the configuration incomplete, or when they say the gateway, token or project folder changed.
argument-hint: "[what to change, optional]"
---

# Nelli-Dev setup

Goal: the central configuration is complete once, and every agent reuses it. The credential never passes through chat.

Scripts are in `${CLAUDE_PLUGIN_ROOT}/scripts` (path already filled in). Run them with `python`.

## Steps

1. **See what exists.** `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_config.py status --json`. If an old Z-Custom `zc-work` folder exists in the workspace, run `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_migrate.py` (dry run), show the developer what it would carry over, and run it with `--apply` only if they agree (the guard asks them to confirm). Say in one line what is already configured and what is missing. Never re-ask for something that is recorded unless the developer says it changed.
2. **Ask only for what is missing, in one round (2 to 4 options each, recommended first):**
   - Gateway URL of the hosted development environment. Options: "I will type the URL" (not a secret), "no environment available: stay code-only". A name for it (default `dev`). Confirm it is a **development or test environment, not production**.
   - Authentication scheme: "Basic (Znode API key)", "Bearer token", "Not sure: decide per API from the spec (Recommended)".
   - Project folders: run `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_projects.py detect`; offer each candidate (best first), "I will type the path", "this part is not needed".
3. **Record** (the developer confirms each on screen):
   - `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_env.py add --name <name> --gateway-url "<url>" --non-production --auth-scheme <auto|basic|bearer>`
   - `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_projects.py add --name sdk|webstore --path "<folder>"`
4. **Credential: the developer does this, not you.** Give exactly this, in a code block, and wait:
   ```
   python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_setup_token.py --env <name>
   ```
   Tell them to run it in their own terminal, paste the credential when asked (the input is hidden), then come back and say "done". On a system without the Windows credential store, or if they prefer, `--use-env-var <NAME>` records an environment variable they set themselves. **Never ask them to paste the credential here.** If one appears in chat anyway, do not use or repeat it; tell them to rotate it and enter the new one with the script.
5. **Verify.** `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_config.py status` (credential: stored or set, never a value) and `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_env.py check` (reachability). Report honestly: reachable or not, credential stored or not.
6. **Consent (data sharing), one question.** Run `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_consent.py status`. Explain in two sentences: Nelli-Dev keeps a local session ledger (names and counts only, never prompts, code or secrets; see `privacy/DATA-INVENTORY.md`) and sends nothing anywhere. Ask which level, recommended first: "off: nothing leaves this machine (Recommended)", "usage: I may share anonymous usage counts as a file I send myself", "usage+feedback: usage counts and feedback notes". Record it with `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_consent.py set --level <off|usage|usage+feedback>`. Skip the question if a level is already recorded and the developer did not ask to change it. They can withdraw any time with `nd_consent.py withdraw`.
7. **Summarize without secrets:** environment name and URL, scheme, project folders, credential state, and what the developer can do next (`/nelli-dev:status`, `/nelli-dev:deliver`, `/nelli-dev:ask`).

## Rules
- Setup is done once; later runs read the configuration. Changing the gateway host or a project folder asks the developer to confirm.
- Never read `.env` files, the credential store or the configuration file directly: use the scripts.
- Nothing about tokens appears in logs, progress files, documents or replies.
