#!/usr/bin/env python3
"""Scan files for internal-only content (hosts, paths, repo names, Jira keys, secrets) before they go to a customer or into the knowledge pack.

Usage
  python nd_scan_customer_safety.py <folder-or-file> [more paths] [--json] [--allow-file allow.txt]

Exit 1 when any Critical or High lead is found. Secret values are never printed (redacted).
Every hit is a LEAD: open it, decide, then fix it or add a reviewed line to the allow file
('<rule-id> <path-substring>' per line).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nd_scan_common import Rule, report, run_rules, walk  # noqa: E402

I = re.I
RULES = [
    Rule("CS-SECRET-KEY", "Critical", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----"), "private key", redact=True),
    Rule("CS-SECRET-CONN", "Critical", re.compile(r"(?:Password|Pwd)\s*=\s*[^;\"'\s]{3,}", I), "connection string password", redact=True),
    Rule("CS-SECRET-ASSIGN", "High", re.compile(r"(?:secret|password|passwd|apikey|api_key|accesskey|access_key|token|clientsecret)\w*\s*[:=]\s*[\"'][^\"'\s]{8,}[\"']", I), "possible hardcoded secret", redact=True),
    Rule("CS-SECRET-BEARER", "Critical", re.compile(r"Bearer\s+eyJ[\w-]{10,}\.[\w-]{10,}"), "JWT bearer token", redact=True),
    Rule("CS-SECRET-AZURE", "Critical", re.compile(r"(?:AccountKey|SharedAccessKey|SharedAccessSignature)=[^;\s\"']{10,}", I), "Azure key", redact=True),
    Rule("CS-PATH-LOCAL", "Medium", re.compile(r"(?:[A-Za-z]:\\Users\\|/home/\w+/|C:/Users/)", I), "local machine path"),
]

try:  # internal-name rules exist only in the owner's working copy; they are not shipped
    from nd_scan_internal_rules import INTERNAL_RULES  # noqa: E402
    RULES = RULES + INTERNAL_RULES
except ImportError:
    pass
ENV_NAME = re.compile(r"(^|[\\/])\.env(\.[\w.-]+)?$", I)
ENV_SECRET_LINE = re.compile(r"^\s*[A-Z][A-Z0-9_]*(?:SECRET|TOKEN|KEY|PASSWORD|PWD)[A-Z0-9_]*\s*=\s*\S{6,}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--allow-file")
    a = ap.parse_args()
    files, skipped = walk(a.paths)
    hits, unreadable = run_rules(files, RULES)
    for f in files:  # env files: count secret-looking lines without ever printing a value
        if ENV_NAME.search(str(f)):
            try:
                n = sum(1 for line in f.read_text(encoding="utf-8-sig", errors="replace").splitlines() if ENV_SECRET_LINE.match(line))
            except OSError:
                n = 0
            hits.append({"rule": "CS-ENVFILE", "sev": "High", "file": str(f), "line": 1, "text": "(values not printed)",
                         "msg": f"environment file in the shipped tree ({n} secret-looking line(s)): review by hand, then replace with a .env.example of names only"})
    if a.allow_file:
        allow = []
        for line in Path(a.allow_file).read_text(encoding="utf-8").splitlines():
            parts = line.split(None, 1)
            if len(parts) == 2 and not line.startswith("#"):
                allow.append(parts)
        hits = [h for h in hits if not any(h["rule"] == r and s.strip() in h["file"] for r, s in allow)]
    return report("Customer-safety scan", hits, unreadable, skipped, len(files),
                  "pattern-based. It can miss secrets in encoded or unusual forms and flags harmless text. Open every lead; a clean run is not proof of safety, so a person signs off before release.", a.json)


if __name__ == "__main__":
    sys.exit(main())
