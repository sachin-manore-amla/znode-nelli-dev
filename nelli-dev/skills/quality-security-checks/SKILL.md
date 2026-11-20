---
name: quality-security-checks
description: The security assessment Nelli-Dev runs on every customization - the scanner, the Znode-specific authentication, authorization and ownership checks, input validation, data protection and secret handling, severity rules and what must be fixed before handover. Use in the Security phase and when reviewing any custom endpoint or Webstore change.
user-invocable: false
---

# Security checks

Run on the customization's changed files, after tests pass and before handover. Output goes to `security-report.md` (template in `meta-document-templates`).

## 1. Scanner (leads, not facts)

```powershell
python ${CLAUDE_PLUGIN_ROOT}/scripts/scripts\nd_security_scan.py --repo <repo> --git-diff <base ref> [--audits]
python ${CLAUDE_PLUGIN_ROOT}/scripts/scripts\nd_scan_customer_safety.py <changed paths>       # secrets and internal references in what you are about to hand over
```

`--audits` runs `dotnet list package --vulnerable --include-transitive` and `npm audit` (needs network; the guard asks first). The scanner is pattern-based: open every lead at its `file:line`, decide, and record **confirmed**, **false positive (why)** or **accepted by developer**. Where the customer has Semgrep or CodeQL, run it too and attach the output. Never report "no vulnerabilities": report what was checked and what was not.

## 2. Znode-specific checks (read the code; the scanner only flags candidates)

| Area | Check | Fail when |
|---|---|---|
| Authentication | Custom endpoints sit behind the SDK's JWT registration (`RegisterJwtAuthentication`); gateway routes do not bypass it | An endpoint is reachable without a token that does not need to be public |
| Authorization | The caller's role may do this action | Any state-changing action has no role/permission check |
| **Ownership** (most common defect) | Every id the caller supplies (user, account, order, cart, address, quote) is checked to belong to the caller, their account or their store | A caller can read or change another shopper's, account's or store's record by changing an id (`SEC-OWNER` leads) |
| Tenant scope | Portal/store context comes from the validated request context, not from a client-supplied value; see `config-stores-tenancy`, `api-auth-and-headers` | A client-supplied portal code or id selects the data without validation |
| Input validation | Models are validated (ranges, lengths, allowed values); search/filter text is never concatenated into SQL | String-built SQL, unvalidated file names/paths, unbounded page sizes |
| Output encoding (Webstore) | No raw HTML from API data; no `dangerouslySetInnerHTML` with unsanitized input | Stored or reflected XSS path |
| Data protection | No secrets, tokens, card data or personal data in logs, URLs, client storage or `NEXT_PUBLIC_` variables | Any of those appear |
| Secrets | Credentials come from environment variables or a vault; none are in source, `.env` files in the repo, or generated files | A secret is committed or printed |
| Transport | HTTPS only; certificate validation never disabled | `rejectUnauthorized: false`, validation callbacks returning true |
| CORS | Restricted to the storefront origin(s) in production | `AllowAnyOrigin()` left in a deployable configuration |
| Webhooks and overrides | Incoming calls validate the shared secret (`SecretKey`) and reject mismatches; handlers are idempotent | Unvalidated callback endpoint |
| Dependencies | No Critical or High known vulnerabilities in packages the change adds | Audit reports Critical/High |
| Direct data access | Only customer-owned tables (registry `direct-data-access`) | Platform tables read or written directly |

## 3. Severity and gate

| Severity | Examples | Gate |
|---|---|---|
| Critical | Injection, authentication bypass, ownership bypass, exposed secret, disabled TLS validation | Must be fixed; no handover |
| High | Missing authorization on a state-changing action, open CORS in a deployable config, vulnerable High dependency | Fix, or the developer accepts in writing in `security-report.md` |
| Medium | Missing input bounds, verbose error detail | Fix or list as a recommendation |
| Low / Info | Hygiene | List |

## 4. What this check cannot show

Runtime configuration, infrastructure, network exposure, third-party package source, and the Znode platform itself. Say so in the report. A change is never called "secure": it is "no Critical or High findings from these checks".

## Related

`api-auth-and-headers` · `quality-logging` · `sdk-conventions` · `quality-performance-checks`
