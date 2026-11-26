---
name: setup
description: First-time setup and later changes to the Nelli-Dev configuration - gateway URL of the developer's development environment, authentication scheme, the folders of the customization code (Custom API SDK, Webstore) and the credential. Use when the developer runs /nelli-dev:setup, when a command finds the configuration incomplete, or when they say the gateway, token or project folder changed.
argument-hint: "[what to change, optional]"
---

# Nelli-Dev setup

Goal: the central configuration is complete once, and every agent reuses it. The gateway URL and the credential are environment variables the developer sets in their own terminal. They never pass through chat, and no script is run to collect or store them.

Scripts are in `${CLAUDE_PLUGIN_ROOT}/scripts` (path already filled in). Run them with `python`.

## Steps

1. **See what exists.** `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_config.py status --json`. If an old Z-Custom `zc-work` folder exists in the workspace, run `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_migrate.py` (dry run), show the developer what it would carry over, and run it with `--apply` only if they agree (the guard asks them to confirm). Say in one line what is already configured and what is missing. Never re-ask for something that is recorded unless the developer says it changed.
2. **Ask only for what is missing, in one round (2 to 4 options each, recommended first):**
   - Authentication scheme: "Basic (Znode API key)", "Bearer token", "Not sure: decide per API from the spec (Recommended)".
   - Project folders: run `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_projects.py detect`; offer each candidate (best first), "I will type the path", "this part is not needed".
   - Confirm the gateway is a **development or test environment, not production**, and a name for it (default `dev`). Do not ask for the URL or the credential in chat and do not run a script to collect them: step 3 has the developer set them as environment variables.
3. **Gateway URL and credential: the developer sets them in their own terminal, you do not.** Show these commands in a code block (PowerShell), with placeholders, and wait. You never run them, never type the values, and never ask for them in chat:
   ```
   # persistent for your user account (open a NEW terminal and restart Claude Code afterwards)
   [Environment]::SetEnvironmentVariable("NELLIDEV_GATEWAY_URL", "https://<your-dev-gateway>", "User")
   [Environment]::SetEnvironmentVariable("ZNODE_API_BASIC", "<your credential>", "User")     # Basic scheme
   [Environment]::SetEnvironmentVariable("ZNODE_API_TOKEN", "<your token>", "User")          # Bearer scheme (use one of the two)
   ```
   Session only, nothing saved: in a terminal, set `$env:NELLIDEV_GATEWAY_URL = "..."` and `$env:ZNODE_API_BASIC = "..."`, then start `claude` from that same terminal. Paste the credential without the words "Basic" or "Bearer". A variable set in another window is not visible to a running Claude Code: the developer restarts it, then says "done". On Linux or macOS the equivalent is `export NAME="value"` in the shell that starts Claude Code. If a secret appears in chat anyway, do not use or repeat it; tell them to rotate it and set the new one with the command.
4. **Record** (the developer confirms each on screen). These commands read the variable inside the script and print no value:
   - `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_env.py from-env --name <name> --non-production --auth-scheme <auto|basic|bearer>` (reads `NELLIDEV_GATEWAY_URL`; add `--var <NAME>` if they used another variable name). If it says the variable is not set, repeat step 3 and the restart; do not accept the URL in chat.
   - `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_env.py credvar --name <name> --var <NAME>` only when the credential variable has a name other than `ZNODE_API_BASIC` / `ZNODE_API_TOKEN` (the default names need no record).
   - `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_projects.py add --name sdk|webstore --path "<folder>"`
5. **Verify.** `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_config.py status` (credential: set or not, never a value) and `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_env.py check` (reachability). Report honestly: reachable or not, credential set or not.
6. **Consent (data sharing), one question.** Run `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_consent.py status`. Explain in two sentences: Nelli-Dev keeps a local session ledger (names and counts only, never prompts, code or secrets; see `privacy/DATA-INVENTORY.md`) and sends nothing anywhere. Ask which level, recommended first: "off: nothing leaves this machine (Recommended)", "usage: I may share anonymous usage counts as a file I send myself", "usage+feedback: usage counts and feedback notes". Record it with `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_consent.py set --level <off|usage|usage+feedback>`. Skip the question if a level is already recorded and the developer did not ask to change it. They can withdraw any time with `nd_consent.py withdraw`.
7. **Summarize without secrets:** environment name and URL, scheme, project folders, credential state, and what the developer can do next (`/nelli-dev:status`, `/nelli-dev:deliver`, `/nelli-dev:ask`).

## Rules
- Setup is done once; later runs read the configuration. Changing the gateway host or a project folder asks the developer to confirm.
- Never read `.env` files, the credential store or the configuration file directly: use the scripts.
- Nothing about tokens appears in logs, progress files, documents or replies.
