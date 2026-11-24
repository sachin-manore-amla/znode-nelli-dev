# Nelli-Dev privacy notice

**DRAFT - legal and privacy review required. Not for release until approved.**

Notice version: 1 (draft)

## 1. Who is responsible (roles)
- Responsible party: `<legal entity name to be confirmed by Znode>`
- The developer using Nelli-Dev: the person whose machine holds the local data.
- Privacy contact: `<privacy contact to be confirmed by Znode>`; general support: https://support.znode.com

## 2. What data and why (purposes)
| Data | Purpose |
|---|---|
| Local session ledger (event times, command, skill and tool names, counts) | Show the developer their session progress and tool use. Stays on the developer's machine. |
| Consent level and notice version | Respect the developer's choice. Stays on the developer's machine. |
| Usage report file (counts only), only if the developer chooses `usage` and sends it | Understand which Nelli-Dev features are used, to improve the product. |
| Feedback note (sanitized), only if the developer writes, confirms and sends it | Fix problems and improve answers. |

Nelli-Dev does not collect prompts, code, file contents, paths, command arguments, responses or secrets.

## 3. Legal basis
`<legal basis per purpose to be confirmed: for example consent for usage and feedback files; basis for the local-only ledger to be confirmed>`

## 4. Recipients and transfers
By default none. Files the developer sends reach Znode support: `<recipients, processors and transfer mechanisms to be confirmed>`.

## 5. Retention
Local files: until the developer clears or deletes them. Files received by Znode: `<retention period to be confirmed>`.

## 6. Your rights
Access, correction, deletion, restriction, objection and withdrawal of consent, as applicable under `<applicable law to be confirmed>`. Locally you can see, export, delete and withdraw yourself (see DATA-INVENTORY.md). For data held by Znode, contact `<privacy contact to be confirmed by Znode>`.

## 7. Security
The ledger is built from a fixed list of non-sensitive fields; the configuration file holds no secrets; feedback is redacted before it is written.

## 8. Changes
A new notice version asks for consent again at the next `/nelli-dev:setup`.
