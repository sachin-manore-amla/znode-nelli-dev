#!/usr/bin/env python3
"""Customization-practice leads: deviations from the recommended way to write Custom API SDK and Webstore code.

Usage
  python nd_practice_scan.py --paths <folder or file> ... [--kind sdk|webstore|auto] [--json]

SDK (C#): a service that is never registered, controllers without [ApiController] or a route, catch blocks that neither log nor
rethrow, exception details returned to the caller, hand-built HTTP to the Znode API root.
Webstore (TypeScript): API route handlers with no session or token check, browser code ('use client') calling the gateway
directly, edits to shared packages. Secrets, XSS and injection are in nd_security_scan.py; speed is in nd_perf_scan.py.
These are LEADS. The reviewer confirms each at its file:line. Exit 1 on any High lead.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nd_scan_common import Rule, read, report, run_rules, walk  # noqa: E402

CS = (".cs",)
TS = (".ts", ".tsx", ".js", ".jsx", ".mjs")
RULES = [
    Rule("PRAC-SDK-EXC-LEAK", "High", re.compile(r"StatusCode\s*\(\s*500\s*,\s*(?:ex|e|exception)\b|Ok\s*\(\s*(?:ex|exception)\b|return\s+(?:BadRequest|Problem)\s*\(\s*(?:ex|e)\.(?:Message|StackTrace|ToString)", re.I),
         "exception details are returned to the caller: return a generic error and log the detail", CS),
    Rule("PRAC-SDK-ZNODE-HTTP", "Medium", re.compile(r"ZnodeApiRootUri[^;]*(?:HttpClient|GetAsync|PostAsync|SendAsync)|(?:HttpClient|GetAsync|PostAsync|SendAsync)[^;]*ZnodeApiRootUri"),
         "hand-built HTTP to the Znode API root: use the typed Znode clients so versioning, headers and errors stay consistent", CS),
    Rule("PRAC-SDK-THROW-EX", "Low", re.compile(r"\bthrow\s+(?:ex|e|exception)\s*;"), "`throw ex;` resets the stack trace: use `throw;`", CS),
]
CATCH = re.compile(r"\bcatch\s*(?:\([^)]*\))?\s*\{?")
LOGS = re.compile(r"Log(?:Message|Information|Error|Warning)|_logger|throw\b|logger\.", re.I)
ROUTE_FILE = re.compile(r"[\\/]app[\\/]api[\\/].*route\.(?:ts|js)$|[\\/]pages[\\/]api[\\/]", re.I)
AUTH_WORDS = re.compile(r"getServerSession|getToken\s*\(|auth\s*\(\s*\)|withAuth|requireAuth|verifyToken|session\b|authorization|isAuthenticated", re.I)
PUBLIC_OK = re.compile(r"\bpublic\b|\bhealth\b|\bwebhook\b|\brevalidate\b", re.I)
GATEWAY = re.compile(r"fetch\s*\(\s*[`'\"]?(?:https?://|\$\{?\s*(?:process\.env\.)?(?:NEXT_PUBLIC_)?\w*(?:API|GATEWAY)\w*)", re.I)


def catch_leads(files):
    out = []
    for f in files:
        if f.suffix.lower() != ".cs":
            continue
        lines = read(f) or []
        for n, line in enumerate(lines, 1):
            if CATCH.search(line) and "catch" in line:
                window = " ".join(lines[n - 1:n + 7])
                if not LOGS.search(window):
                    out.append({"rule": "PRAC-SDK-CATCH-NOLOG", "sev": "Medium", "file": str(f), "line": n, "text": line.strip()[:140],
                                "msg": "catch block neither logs nor rethrows: the failure disappears"})
    return out


def controller_leads(files):
    out = []
    for f in files:
        if f.suffix.lower() != ".cs" or not re.search(r"Controller\.cs$", f.name):
            continue
        text = "\n".join(read(f) or [])
        if re.search(r"class\s+\w+Controller\b", text) and not re.search(r"\[ApiController\]", text):
            out.append({"rule": "PRAC-SDK-CTRL-ATTR", "sev": "Medium", "file": str(f), "line": 1, "text": f.name,
                        "msg": "controller without [ApiController]: no automatic model validation or problem responses"})
        if re.search(r"class\s+\w+Controller\b", text) and not re.search(r"\[Route\(|\[Http(?:Get|Post|Put|Delete|Patch)\(\"", text):
            out.append({"rule": "PRAC-SDK-CTRL-ROUTE", "sev": "Medium", "file": str(f), "line": 1, "text": f.name,
                        "msg": "controller without a route attribute: the endpoint may not be reachable or may collide"})
    return out


def registration_leads(files, root: Path):
    """Services with an interface that are not mentioned in the dependency registration."""
    reg = [f for f in root.rglob("CustomDependencyRegistration*.cs") if "bin" not in f.parts and "obj" not in f.parts]
    if not reg:
        return []
    reg_text = "\n".join("\n".join(read(f) or []) for f in reg)
    out = []
    for f in files:
        if f.suffix.lower() != ".cs" or not re.search(r"Service\.cs$", f.name):
            continue
        for n, line in enumerate(read(f) or [], 1):
            m = re.search(r"class\s+(\w+Service)\s*:\s*(I\w+Service)\b", line)
            if m and m.group(1) not in reg_text and m.group(2) not in reg_text:
                out.append({"rule": "PRAC-SDK-UNREGISTERED", "sev": "High", "file": str(f), "line": n, "text": line.strip()[:140],
                            "msg": f"{m.group(1)} is not registered in the dependency registration: it fails at run time when injected"})
    return out


def route_leads(files):
    out = []
    for f in files:
        if f.suffix.lower() not in TS or not ROUTE_FILE.search(str(f)):
            continue
        text = "\n".join(read(f) or [])
        if PUBLIC_OK.search(str(f)):
            continue
        if re.search(r"export\s+(?:async\s+)?function\s+(?:GET|POST|PUT|PATCH|DELETE)|export\s+default", text) and not AUTH_WORDS.search(text):
            out.append({"rule": "PRAC-WEB-ROUTE-NOAUTH", "sev": "High", "file": str(f), "line": 1, "text": f.name,
                        "msg": "API route handler with no session or token check: confirm it is meant to be public, otherwise anyone can call it"})
    return out


def client_gateway_leads(files):
    out = []
    for f in files:
        if f.suffix.lower() not in TS:
            continue
        lines = read(f) or []
        if not any(re.match(r"\s*['\"]use client['\"]", l) for l in lines[:5]):
            continue
        for n, line in enumerate(lines, 1):
            if GATEWAY.search(line):
                out.append({"rule": "PRAC-WEB-CLIENT-GATEWAY", "sev": "High", "file": str(f), "line": n, "text": line.strip()[:140],
                            "msg": "browser code calls the API directly: credentials or tokens would reach the browser. Call a server route (BFF) instead"})
    return out


def shared_pkg_leads(paths):
    out = []
    for p in map(Path, paths):
        for f in ([p] if p.is_file() else []):
            if "packages" in f.parts and "node_modules" not in f.parts:
                out.append({"rule": "PRAC-WEB-SHARED-PKG", "sev": "Info", "file": str(f), "line": 0, "text": f.name,
                            "msg": "change inside a shared package folder: it is shared Webstore source, so every upgrade must re-apply it. Label it a source customization"})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--paths", nargs="+", required=True)
    ap.add_argument("--root", help="project root (for the registration check); default: the first path")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    files, skipped = walk(a.paths, CS + TS)
    rules = RULES
    hits, unreadable = run_rules(files, rules)
    root = Path(a.root or a.paths[0])
    root = root if root.is_dir() else root.parent
    hits += catch_leads(files) + controller_leads(files) + registration_leads(files, root) + route_leads(files) + client_gateway_leads(files)
    hits += shared_pkg_leads([str(f) for f in files])
    return report("Practice scan", hits, unreadable, skipped, len(files),
                  "pattern-based leads about customization practice; confirm each by reading the code. NOT checked: behaviour at run time, whether a public route is intended.", a.json)


if __name__ == "__main__":
    sys.exit(main())
