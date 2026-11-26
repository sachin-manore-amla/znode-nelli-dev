# Nelli-Dev security

## Report a vulnerability

Report a security problem in Nelli-Dev through **https://support.znode.com** (open a support request and mark it "Security"), or write to `<security contact to be confirmed by Znode>`.
Please include: the Nelli-Dev version (`.claude-plugin/plugin.json`), what you did, what you expected, what happened, and the smallest example that shows it. Do not include real credentials, tokens or customer data; replace them with placeholders. Please do not publish details until Znode has had a chance to respond.

## What Nelli-Dev never does

- **No secrets in chat.** It never asks for, accepts, prints or stores a token, password or key in the conversation. You set your gateway URL and credential as environment variables in your own terminal (the plugin shows the command and never runs it); the credential is read only inside the plugin's scripts. If you ever paste a secret into the chat, rotate it.
- **No writes without approval.** Before you approve a plan it writes only to its own working folders (`nd-work` and `nd-knowledge` in your workspace). After approval it writes only inside the scope you approved. Changes to the approval, the allowed gateway host or the project folders always ask you first.
- **GET-only discovery.** To learn what your environment returns it makes read-only calls (GET and HEAD) to the gateway you recorded, within a call budget, with responses redacted. A call that changes data runs only after you approved that exact call. Payment and card calls are never run for you.
- **Nothing leaves your machine without you.** No commit, push, deploy, package install or call to another host happens unless you pick it.
- **No changes to the Znode platform.** It works on your Custom API SDK and your Webstore source only.
- **No reading of other folders.** Only your workspace and the project folders you recorded.

## What protects you (and what does not)

A guard (a Claude Code hook) checks every file and shell action the agent makes and refuses writes outside your workspace, secret files, the credential store, calls to unrecorded hosts, and destructive commands. It is a safety net that reads the visible command text; it is not a sandbox. It cannot see what a script you or the agent run does inside.

Check that the plugin files are intact: `python <plugin folder>/scripts/nd_integrity.py verify` compares them with the release manifest (changed, missing or extra files are listed). If it reports a difference, reinstall the plugin from the official source. A secret check for anything you hand over: `python <plugin folder>/scripts/nd_secret_scan.py <file or folder>`.

## Safe-use guidance

1. Point Nelli-Dev only at a **development or test** gateway, never production.
2. Use a credential with the **least access** that works, and rotate it if it was ever shown.
3. Work on a **branch**; review every changed file yourself; run the build and tests in your own environment before merging. Nelli-Dev output is generated: it carries a stamp saying human review and testing are required before production use.
4. Treat advice as advice. Check what it cites (knowledge article, API operation, file and line). Items marked "needs confirmation" are not facts.
5. Be careful with what you let it read: files in your workspace with secret-like content (not named like `.env` or `appsettings`) can be read. Keep secrets in a vault or environment variables.
6. Content it reads (knowledge pages, API responses, comments in code) is treated as data. If it tells you that some content asked it to do something, do not approve that action unless you want it.
7. Read each approval prompt. The plugin asks before anything that widens its reach (approval, allowed host, project folders, non-GET calls, installs, deploys).
8. Delete `nd-work` folders you no longer need; they hold redacted responses and your request documents.
9. Keep the plugin updated; each update lists its changes in the release notes.

This document is not a legal notice. Terms of use and liability are in the licence delivered with the plugin.
