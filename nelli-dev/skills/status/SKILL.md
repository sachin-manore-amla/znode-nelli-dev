---
name: status
description: Show the Nelli-Dev configuration and open work - gateway, authentication state, project folders and request folders, with no secrets. Use when the developer runs /nelli-dev:status or asks what is configured or in progress.
---

# Nelli-Dev status

Run, then summarize in a short table (no secrets, no token values). Scripts are in `${CLAUDE_PLUGIN_ROOT}/scripts` (path already filled in).

1. `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_config.py status` - environments, credential state (stored, env var set, or NOT set), project folders, what is still missing.
2. `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_env.py check` - only if an environment is recorded: reachability.
3. The open requests: list the folders under `<workspace>\nd-work\` and, for each, the last lines of its progress file (`python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_progress.py --help` shows the exact usage).
4. **Session block.** `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_ledger.py show` and `python ${CLAUDE_PLUGIN_ROOT}/scripts/nd_consent.py status`. Print a compact "Session" block: commands run, skills and tools used with counts, knowledge queries, tokens and cost (say "not available" when the ledger says so; never estimate), the open requests from step 3, the consent level, and the one-line statement of what is collected that the ledger prints. Mention `nd_ledger.py export` and `nd_ledger.py clear` once.

If anything is missing, say what and offer `/nelli-dev:setup`. If an old `zc-work` folder exists, mention `nd_migrate.py` once.
