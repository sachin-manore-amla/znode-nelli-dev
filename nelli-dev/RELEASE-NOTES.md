# Nelli-Dev release notes

## 0.4.1

Corrections only.

### Changed in 0.4.1
- **The integrity check no longer fails on line endings.** The release manifest now hashes text with Windows line endings read as LF, so an install that converted line endings still verifies. Any other change to a file is still reported.
- The manifest was rebuilt from the current files, so skill wording edited after 0.4.0 is covered.

## 0.4.0

Setup no longer runs a script to ask for or store your gateway URL or credential.

### Changed in 0.4.0
- **You set the gateway URL and the credential yourself.** `/nelli-dev:setup` shows two PowerShell commands that set `NELLIDEV_GATEWAY_URL` and `ZNODE_API_BASIC` (or `ZNODE_API_TOKEN`) as environment variables in your own terminal. Restart Claude Code afterwards so it can see them. Nelli-Dev never runs these commands, never asks for the values in chat, and the guard refuses it setting or printing them.
- **Recording.** `nd_env.py from-env` reads the URL variable and records the gateway (still confirmed on screen, development or test only). `nd_env.py credvar` records the name of a differently named credential variable. The configuration file holds names only, never values.
- **Existing setups keep working.** A credential saved by an earlier version in the Windows Credential Manager is still read; `nd_setup_token.py` is kept as a legacy tool and setup no longer uses it.
- Known limit: a variable set in another window is not visible to a running Claude Code, so a restart is needed.

## 0.3.0

Nelli-Dev is now safer, shows what it is doing, and keeps your data on your machine.

### Added in 0.3.0
- **Znode-only code review.** `/nelli-dev:review` reviews Znode customizations only (SDK extension points, Webstore customizations, Znode API usage, and their security and performance). General style or language review is politely declined.
- **Session visibility.** `/nelli-dev:status` now shows what the session used: commands, skills and tools, with counts. It stores names and counts only, never your prompts, code or secrets, and token or cost figures are shown only where Claude Code provides them.
- **Consent, off by default.** `/nelli-dev:setup` asks what, if anything, may be shared. Nothing leaves your machine unless you opt in, and even then Nelli-Dev only writes a file for you to send.
- **Feedback.** `/nelli-dev:feedback` builds a redacted preview and saves it locally only after you confirm.
- **Update notice.** At session start Nelli-Dev tells you when a newer version is in your local marketplace copy. It makes no network call and installs nothing.
- **Cost control.** Heavy commands show an estimate first and ask for a go-ahead above a cap.
- **Stronger guard and checks.** Writes outside your workspace are blocked or need approval, generated documents are scanned for secrets, and the plugin files are checked against the release manifest at start.
- **Liability stamp.** Every answer and handover document states the plugin version, knowledge date, confidence and that human review and testing are required before production use.
- **Privacy and security pages.** See `privacy/DATA-INVENTORY.md` and `SECURITY.md`.

## 0.2.0

Nelli-Dev now knows more about customizing the Znode platform, and has new areas of knowledge.

### Added in 0.2.0
- New skills: publish pipeline, vouchers, caching, brands and reviews.
- Deeper skills for tax and shipping, returns, search and SEO, inventory and notifications.
- A Support and feedback section in the README, a license notice (`LICENSE`) and a list of known limits (`KNOWN-LIMITS.md`).

### What Nelli-Dev covers
Customization knowledge across the Custom API SDK, the Webstore, Admin and Commerce Portal configuration, plus API recommendations and ready-to-run curls against your own development gateway.

### Updating
Run `claude plugin marketplace update znode-nelli-dev`, then `claude plugin update nelli-dev@znode-nelli-dev`, and restart Claude Code. Your saved configuration and credential are kept. Start with `/nelli-dev:status` to check them.

### Reporting problems
See Support and feedback in `README.md`.

## 0.1.0
First release: setup, advise, ask, recommend-api, curl, review, docs and deliver commands.
