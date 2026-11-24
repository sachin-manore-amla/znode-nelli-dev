# Nelli-Dev data inventory

Plain-language list of what Nelli-Dev records on your computer, and what it never does.

## Short version
- Nelli-Dev keeps a small **local ledger** of what you ran. It stays on your machine.
- **Nothing is sent anywhere by default.** Nelli-Dev has no sending function at all. "Sharing" means a file that you read and send yourself.
- You can see, export, delete and withdraw at any time.

## What the ledger holds
One line per event, in `%USERPROFILE%\.nelli-dev\ledger\<date>.jsonl`:
- the time, and a short code that groups the lines of one session (a one-way hash, not the session id itself)
- the kind of event: session start, a Nelli-Dev command, a tool or skill use, session end
- the **name** of the command, skill or tool (for example `nelli-dev:ask`, `Read`, `Bash`)
- whether the call was a knowledge lookup (a count)

## What it never holds
Your prompts, your code or file contents, file or folder paths, command arguments, API responses, URLs, host names, tokens, passwords, keys or any other secret. The lines are built from a fixed list of fields, so these cannot get in by accident.

Token counts and cost are **not recorded**: Claude Code does not give them to plug-in hooks, and Nelli-Dev does not estimate them.

## Where else Nelli-Dev writes
| Item | Location | Created when |
|---|---|---|
| Configuration, including your consent level (no secrets) | `%USERPROFILE%\.nelli-dev\config.json` | setup |
| Ledger summary export | `%USERPROFILE%\.nelli-dev\ledger-export\` | you run `nd_ledger.py export` |
| Usage report (counts only) | `%USERPROFILE%\.nelli-dev\reports\` | you run `nd_consent.py report`, level usage or higher |
| Feedback notes (sanitized) | `%USERPROFILE%\.nelli-dev\feedback\` | you confirm a preview in `/nelli-dev:feedback` |

## See, export, delete
- See: `/nelli-dev:status` (Session block) or `python scripts/nd_ledger.py show` (`--all` for every day).
- Export a readable counts-only summary: `python scripts/nd_ledger.py export`.
- Delete the ledger: `python scripts/nd_ledger.py clear`. Deleting the `.nelli-dev` folder removes everything listed above.
- Switch the ledger off: set the environment variable `NELLIDEV_LEDGER=off`.

## Retention
Local only. Kept until you run `clear`, delete the folder, or uninstall Nelli-Dev and remove `%USERPROFILE%\.nelli-dev`. Nelli-Dev does not delete it on its own schedule.

## Who receives data, and when
**Nobody, by default.** The consent levels are:
- `off` (default): nothing leaves your machine; only the local ledger exists.
- `usage`: you may share anonymous usage counts. Nelli-Dev writes a report file and shows its path; you decide whether to send it.
- `usage+feedback`: the same, plus feedback notes you wrote and confirmed.

Files you choose to share go to Znode through https://support.znode.com (or `<support contact to be confirmed by Znode>`).

## Withdraw
`python scripts/nd_consent.py withdraw` sets the level to `off`. Existing local files stay until you `clear` them.

## Update check
At session start Nelli-Dev compares its installed version with the version in the plug-in marketplace copy already on your computer. It reads one local file, makes **no network call**, sends no identifier, and installs nothing. If a newer version exists it prints one line with the update commands.
