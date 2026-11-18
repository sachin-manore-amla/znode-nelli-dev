#!/usr/bin/env python3
"""Security leads for a customization (C# SDK code and TypeScript Webstore code), plus optional dependency audits.

Usage
  python nd_security_scan.py --paths Custom.Api.Core src [--git-diff origin/main --repo .] [--audits] [--json]

  --git-diff REF   scan only files changed against REF in --repo (the normal use: scan the customization)
  --audits         also run `dotnet list package --vulnerable --include-transitive` and `npm audit --json`
                   (these contact the package feeds; the guard asks first)

Exit 1 on any Critical or High lead. Hits are LEADS: confirm each at its file:line. The
ownership/authorization check is a heuristic and MUST be followed by a manual read of each listed action.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nd_scan_common import Rule, git_changed, read, report, run_rules, walk  # noqa: E402

I = re.I
CS = (".cs",)
TS = (".ts", ".tsx", ".js", ".jsx", ".mjs")
RULES = [
    Rule("SEC-SQLI-1", "Critical", re.compile(r"(?:FromSqlRaw|ExecuteSqlRaw|SqlQueryRaw)\s*\(\s*\$\""), "SQL built with string interpolation (use parameters / FromSqlInterpolated)", CS),
    Rule("SEC-SQLI-2", "Critical", re.compile(r"new\s+SqlCommand\s*\(\s*(?:\$\"|\"[^\"]*\"\s*\+)"), "SQL command built by concatenation", CS),
    Rule("SEC-AUTH-ANON", "High", re.compile(r"\[AllowAnonymous\]"), "anonymous endpoint: confirm it must be public and returns no customer data", CS),
    Rule("SEC-CRYPTO", "High", re.compile(r"\b(?:MD5|SHA1|DES|RC2|TripleDES)\b(?:\.Create|CryptoServiceProvider)"), "weak cryptography", CS),
    Rule("SEC-TLS", "Critical", re.compile(r"ServerCertificateCustomValidationCallback\s*=.*true|DangerousAcceptAnyServerCertificateValidator"), "TLS validation disabled", CS),
    Rule("SEC-CORS", "High", re.compile(r"AllowAnyOrigin\s*\(\)"), "CORS open to any origin", CS),
    Rule("SEC-DEVEX", "Medium", re.compile(r"UseDeveloperExceptionPage"), "developer exception page: must not run in production", CS),
    Rule("SEC-DESER", "High", re.compile(r"BinaryFormatter|TypeNameHandling\.(?:All|Auto|Objects|Arrays)"), "unsafe deserialization", CS),
    Rule("SEC-PROC", "High", re.compile(r"Process\.Start\s*\("), "starts a process: check for input reaching the command", CS),
    Rule("SEC-LOGSECRET", "High", re.compile(r"Log\w*\([^)]*(?:password|token|secret|apikey|authorization|cardnumber)", I), "possible secret in a log call", CS + TS),
    Rule("SEC-HARDCODED", "Critical", re.compile(r"(?:password|secret|apikey|api_key|token|clientsecret)\w*\s*=\s*\"[^\"\s]{8,}\"", I), "hardcoded secret", CS, True),
    Rule("SEC-XSS-1", "High", re.compile(r"dangerouslySetInnerHTML"), "raw HTML: sanitize the value or avoid", TS),
    Rule("SEC-XSS-2", "High", re.compile(r"\.innerHTML\s*=|document\.write\s*\("), "DOM injection point", TS),
    Rule("SEC-EVAL", "Critical", re.compile(r"\beval\s*\(|new\s+Function\s*\("), "dynamic code execution", TS),
    Rule("SEC-TLS-JS", "Critical", re.compile(r"rejectUnauthorized\s*:\s*false|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]?0"), "TLS validation disabled", TS),
    Rule("SEC-TOKEN-STORE", "High", re.compile(r"(?:localStorage|sessionStorage)\.setItem\([^)]*(?:token|jwt|auth|password)", I), "token kept in browser storage", TS),
    Rule("SEC-PUBLIC-ENV", "Critical", re.compile(r"NEXT_PUBLIC_\w*(?:SECRET|PASSWORD|PRIVATE|TOKEN|API_?KEY)\w*", I), "secret exposed to the browser through NEXT_PUBLIC_", TS),
    Rule("SEC-EXEC", "High", re.compile(r"child_process|\bexec(?:Sync)?\s*\("), "shell execution", TS),
    Rule("SEC-HTTP", "Low", re.compile(r"[\"']http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)"), "plain-HTTP URL", CS + TS),
    Rule("SEC-REDIRECT", "Medium", re.compile(r"redirect\(\s*(?:req|request|searchParams|params)", I), "redirect target from the request: check for open redirect", TS),
]
ID_PARAM = re.compile(r"\b(?:int|long|string|Guid)\??\s+(\w*(?:[Ii]d|Code|Number))\b")
ACTION = re.compile(r"\[Http(?:Get|Post|Put|Delete|Patch)")
OWNERSHIP = re.compile(r"UserId|AccountId|PortalId|GetUserContext|ClaimsPrincipal|User\.Identity|HttpContext\.User|Authorize\(|IsOwner|Ownership|CheckAccess|ValidateOwner", I)


def ownership_leads(files):
    out = []
    for f in files:
        if f.suffix.lower() != ".cs" or "Controller" not in f.name:
            continue
        lines = read(f) or []
        has_check = bool(OWNERSHIP.search("\n".join(lines)))
        for n, line in enumerate(lines, 1):
            if ACTION.search(line):
                ids = ID_PARAM.findall(" ".join(lines[n:n + 6]))
                if ids and not has_check:
                    out.append({"rule": "SEC-OWNER", "sev": "High", "file": str(f), "line": n, "text": line.strip()[:140],
                                "msg": f"action takes caller-supplied id(s) {sorted(set(ids))} but the file shows no ownership/authorization check: read it and confirm the caller may access that record"})
    return out


def audits(paths):
    out = []
    for p in paths:
        root = Path(p)
        if not root.is_dir():
            continue
        for sln in list(root.glob("*.sln"))[:1]:
            r = subprocess.run(["dotnet", "list", str(sln), "package", "--vulnerable", "--include-transitive"], capture_output=True, text=True)
            for line in r.stdout.splitlines():
                if re.search(r"^\s*>\s+\S+.*(Critical|High|Moderate|Low)", line):
                    sev = "Critical" if "Critical" in line else "High" if "High" in line else "Medium"
                    out.append({"rule": "SEC-DEP-NUGET", "sev": sev, "file": str(sln), "line": 0, "msg": "vulnerable NuGet package", "text": line.strip()[:140]})
        if (root / "package.json").exists():
            r = subprocess.run("npm audit --json", cwd=root, capture_output=True, text=True, shell=True)
            try:
                v = json.loads(r.stdout).get("metadata", {}).get("vulnerabilities", {})
                for s, key in (("Critical", "critical"), ("High", "high")):
                    if v.get(key):
                        out.append({"rule": "SEC-DEP-NPM", "sev": s, "file": str(root / "package.json"), "line": 0, "text": "", "msg": f"{v[key]} {key} npm vulnerabilities (run npm audit for the list)"})
            except ValueError:
                out.append({"rule": "SEC-DEP-NPM", "sev": "Info", "file": str(root), "line": 0, "text": "", "msg": "npm audit gave no JSON (offline or no lockfile): NOT checked"})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--paths", nargs="*", default=[])
    ap.add_argument("--git-diff")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--audits", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    paths = a.paths + (git_changed(a.repo, a.git_diff) if a.git_diff else [])
    if not paths:
        ap.error("give --paths or --git-diff")
    files, skipped = walk(paths, CS + TS)
    hits, unreadable = run_rules(files, RULES)
    hits += ownership_leads(files)
    if a.audits:
        hits += audits(a.paths or [a.repo])
    return report("Security scan", hits, unreadable, skipped, len(files),
                  "pattern-based leads, not a full static analyzer. It cannot see data flow, so run Semgrep or CodeQL where available and read every SEC-OWNER action by hand. NOT scanned: runtime configuration, infrastructure, third-party package source.", a.json)


if __name__ == "__main__":
    sys.exit(main())
