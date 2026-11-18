# Nelli-Dev

Nelli-Dev is the Znode customization engineer for customer and partner developers, delivered as a Claude Code plugin. Give it a customization requirement. It works out whether Znode already does it, finds the right APIs and extension points, waits for your approval, then builds, tests and reviews the result in your own Custom API SDK and Webstore source.

## Install

In Claude Code:

```
/plugin marketplace add sachin-manore-amla/znode-nelli-dev
/plugin install nelli-dev@znode-nelli-dev
```

Restart Claude Code, then type `/nelli-dev:` to see the commands.

## First-time setup

Run `/nelli-dev:setup`. It records your development or test gateway URL and your SDK and Webstore folders in `%USERPROFILE%\.nelli-dev\config.json` (no secrets). It then gives you one command to run in your own terminal to save your credential in the Windows Credential Manager with hidden input. Never paste a credential into the chat.

## Commands

| Command | Purpose |
|---|---|
| `/nelli-dev:setup` | First-time setup and later changes |
| `/nelli-dev:status` | What is configured and in progress |
| `/nelli-dev:deliver` | Verdict, plan, your approval, build, tests, checks, handover |
| `/nelli-dev:advise` | Verdict and recommended approach, no code |
| `/nelli-dev:ask` | A sourced, read-only answer |
| `/nelli-dev:recommend-api` | Which APIs to use, in which order |
| `/nelli-dev:curl` | Ready-to-run curl commands against your gateway |
| `/nelli-dev:review` | Security, performance and standards review of your customization code |
| `/nelli-dev:docs` | Technical document and deployment guide for a finished request |

## Safety

A guard hook limits what Nelli-Dev's agents can do: your code is not touched before you approve a plan, secrets are never read or printed, and only your recorded gateway is called. Calls that change data need your approval.

Version 0.1.0 is a first release. Verify customizations in your own development environment before release.
