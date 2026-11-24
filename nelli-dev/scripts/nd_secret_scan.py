#!/usr/bin/env python3
"""Find secrets and identifying values in text before it is handed over. Standard library only, no network.

Looks for: private keys, JWTs, Basic and Bearer strings, well-known API key shapes, key = value assignments
(password, secret, token, api key ...), connection strings and URLs with credentials, e-mail addresses,
host names and private IP addresses. A finding never prints the value: only the rule, the line and a masked hint.

Usage
  python nd_secret_scan.py <file-or-folder> [...]       scan files (folders: every text file below, binary files skipped)
  python nd_secret_scan.py -                            scan standard input
  python nd_secret_scan.py <path> --allow <text> ...    ignore a finding whose matched value contains <text> (repeatable)
  python nd_secret_scan.py <path> --allow-file <file>   one allowed text per line (# comments)
  python nd_secret_scan.py <path> --json                machine-readable output
  python nd_secret_scan.py <path> --min-severity high   only secret-like findings (default: medium = also e-mails and hosts)

Exit code: 0 nothing found, 1 at least one finding, 2 usage error. Placeholders are not findings: $ZNODE_API_TOKEN,
${TOKEN}, <token>, {{token}}, %TOKEN%, a variable name in capitals, example.com / example.org / .invalid / localhost,
and the public Znode documentation hosts. The scan is pattern-based: it gives leads, not proof that a text is clean.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKIP_PARTS = {".git", "node_modules", "__pycache__", "bin", "obj"}
TEXT_EXT = {".md", ".txt", ".json", ".yml", ".yaml", ".xml", ".config", ".cs", ".ts", ".tsx", ".js", ".jsx", ".py", ".ps1", ".sh", ".html",
            ".csv", ".sql", ".http", ".env", ".ini", ".toml", ".cfg", ".properties", ".sln", ".csproj"}
MAX_BYTES = 5_000_000
OK_HOSTS = ("support.znode.com", "www.znode.com", "apidocs.znode.com", "znode.com", "localhost", "github.com", "nuget.org", "npmjs.com",
            "microsoft.com", "learn.microsoft.com", "json-schema.org", "w3.org", "schemas.xmlsoap.org", "keepachangelog.com")
OK_MAIL_DOMAINS = ("example.com", "example.org", "example.net", "example.invalid", "znode.com")

PLACEHOLDER = re.compile(r"^(?:\$\{?[A-Za-z_][\w:]*\}?|%\w+%|<[^>]*>|\{\{[^}]*\}\}|\[[A-Za-z_ -]*\]|[A-Z][A-Z0-9]*_[A-Z0-9_]+|x{4,}|\*{3,}|\.{3,}|redacted|changeme|your[-_ ]?\w*|"
                         r"\$env:\w+|<?[A-Za-z_ -]*(?:here|placeholder)>?)$", re.I)

# (rule id, severity, regex, group holding the value or 0)
RULES = [
    ("private-key", "high", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED |PGP )?PRIVATE KEY(?: BLOCK)?-----"), 0),
    ("jwt", "high", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{4,}"), 0),
    ("bearer-string", "high", re.compile(r"\bBearer\s+([A-Za-z0-9._~+/=-]{16,})"), 1),
    ("basic-string", "high", re.compile(r"\bBasic\s+([A-Za-z0-9+/]{12,}={0,2})(?![A-Za-z0-9+/])"), 1),
    ("aws-key", "high", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"), 0),
    ("github-token", "high", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"), 0),
    ("api-key-shape", "high", re.compile(r"\b(?:sk-[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{30,}|glpat-[A-Za-z0-9_-]{16,})"), 0),
    ("azure-key", "high", re.compile(r"(?:AccountKey|SharedAccessKey|SharedAccessSignature|sig)=([A-Za-z0-9+/%]{20,}={0,2})", re.I), 1),
    ("connection-string", "high", re.compile(r"(?:\b(?:Server|Data Source|Host|Endpoint|AccountName)\s*=[^;\r\n]+;[^\r\n]*?\b(?:Password|Pwd|AccountKey|User Id|Uid)\s*=\s*([^;\s\"']+))", re.I), 1),
    ("password-in-connection", "high", re.compile(r"\b(?:Password|Pwd)\s*=\s*([^;\s\"'<>]{3,})", re.I), 1),
    ("url-credentials", "high", re.compile(r"\b[a-z][a-z0-9+.-]{2,}://[^\s/:@\"']+:([^\s/@\"']{3,})@"), 1),
    ("secret-assignment", "high", re.compile(r"""(?ix)\b(?:api[_-]?key|apikey|secret|client[_-]?secret|access[_-]?key|auth[_-]?token|token|passwd|password|pwd|private[_-]?key|credential)s?
                                                   ["']?\s*[:=]\s*["']?([^\s"'<>,;)}\]`]{8,})"""), 1),
    ("email", "medium", re.compile(r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,})\b"), 0),
    ("private-ip", "medium", re.compile(r"\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b"), 0),
    ("host-name", "medium", re.compile(r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+(?:com|net|org|io|dev|cloud|local|internal|corp|lan|intra|co|us|uk|eu|in|biz|info)\b"), 0),
]


def mask(v: str) -> str:
    return (v[:2] + "***" + f"({len(v)} chars)") if len(v) > 6 else "***"


def is_placeholder(value: str) -> bool:
    v = value.strip().strip("\"'")
    return bool(PLACEHOLDER.match(v)) or v.lower().startswith(("http://", "https://")) and "@" not in v


def host_ok(host: str) -> bool:
    h = host.lower().rstrip(".")
    return (h.endswith((".invalid", ".example", ".test", ".localhost")) or h in OK_HOSTS or any(h.endswith("." + d) for d in OK_HOSTS)
            or h.split(".")[0] == "example" or h.endswith(("example.com", "example.org", "example.net")))


def looks_like_code_identifier(token: str) -> bool:
    # file names and dotted member access (Newtonsoft.Json, appsettings.dev, README.md) are not hosts
    return bool(re.search(r"\.(?:json|md|py|cs|ts|js|txt|html|csv|xml|yml|yaml|sql|ps1|sh|config|dll|exe)$", token, re.I))


def scan_text(text: str, name: str, allow: list, min_sev: str = "medium") -> list:
    findings = []
    for ln, line in enumerate(text.splitlines(), 1):
        if len(line) > 4000:
            line = line[:4000]
        seen = set()
        for rule, sev, rx, grp in RULES:
            if min_sev == "high" and sev != "high":
                continue
            for m in rx.finditer(line):
                value = m.group(grp) if grp else m.group(0)
                if rule == "email":
                    domain = m.group(1).lower()
                    if domain.endswith(OK_MAIL_DOMAINS) or domain.endswith((".invalid", ".example", ".test")) or looks_like_code_identifier(domain):
                        continue
                    value = m.group(0)
                if rule == "private-ip" and value.startswith("10.") and re.search(r"version|release|came in|since|Znode\s*10|v?10\.\d+\.\d+\.\d+\s*(?:and|or|to|,)", line, re.I):
                    continue            # a Znode 10.x.y.z version number, not an address
                if rule == "host-name":
                    if host_ok(value) or looks_like_code_identifier(value) or "@" in line[max(0, m.start() - 1):m.start()]:
                        continue
                if rule in ("secret-assignment", "bearer-string", "basic-string", "password-in-connection", "connection-string", "url-credentials", "azure-key") \
                        and is_placeholder(value):
                    continue
                if rule == "secret-assignment" and (value.startswith(("(", "[", "new ", "string.", "Environment.", "process.env", "os.environ", "config", "Configuration"))
                                                    or re.match(r"^[A-Za-z_][\w.]*\(", value) or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", value) and not re.search(r"\d", value)):
                    continue            # code that reads a value, not a literal secret
                if any(a and a.lower() in value.lower() for a in allow):
                    continue
                key = (rule, m.start())
                if key in seen:
                    continue
                seen.add(key)
                findings.append({"file": name, "line": ln, "rule": rule, "severity": sev, "hint": mask(value)})
    # a host or e-mail inside a line that already has a high finding is reported once per rule: fine
    return findings


def iter_files(paths: list):
    for p in paths:
        path = Path(p)
        if path.is_dir():
            for f in sorted(path.rglob("*")):
                if f.is_file() and not (SKIP_PARTS & set(f.relative_to(path).parts)) and (f.suffix.lower() in TEXT_EXT or f.name.lower().startswith(".env")):
                    yield f
        elif path.is_file():
            yield path
        else:
            print(f"not found: {p}", file=sys.stderr)


def read_text(f: Path):
    try:
        if f.stat().st_size > MAX_BYTES:
            return None
        data = f.read_bytes()
    except OSError:
        return None
    if b"\x00" in data[:4096]:
        return None
    return data.decode("utf-8", errors="replace")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help="files or folders, or - for standard input")
    ap.add_argument("--allow", action="append", default=[], help="ignore findings whose value contains this text")
    ap.add_argument("--allow-file")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--min-severity", choices=["medium", "high"], default="medium")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    allow = list(a.allow)
    if a.allow_file:
        try:
            allow += [l.strip() for l in Path(a.allow_file).read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
        except OSError as e:
            print(f"cannot read the allow file: {e}", file=sys.stderr)
            return 2
    findings, scanned, unreadable = [], 0, []
    if a.paths == ["-"]:
        findings += scan_text(sys.stdin.read(), "<stdin>", allow, a.min_severity)
        scanned = 1
    else:
        for f in iter_files(a.paths):
            text = read_text(f)
            if text is None:
                unreadable.append(str(f))
                continue
            scanned += 1
            findings += scan_text(text, str(f), allow, a.min_severity)
    if a.json:
        print(json.dumps({"scanned": scanned, "skipped": unreadable, "findings": findings}, indent=1))
    else:
        for x in findings:
            print(f"[{x['severity'].upper()}] {x['rule']}  {x['file']}:{x['line']}  value {x['hint']}")
        print(f"# Secret scan: {scanned} file(s), {len(findings)} finding(s)" + (f", {len(unreadable)} skipped (binary or too large)" if unreadable else ""))
        if findings:
            print("Remove or replace each value with a placeholder (for example $ZNODE_API_TOKEN) and scan again. Values are never printed.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
